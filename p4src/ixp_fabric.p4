#include <core.p4>
#include <tna.p4>

#include "headers.p4"
#include "parsers.p4"
#include "forward.p4"
#include "flow_watchlist.p4"
#include "include/flow_counters.p4"
#include "include/flow_meters.p4"
#include "include/int_xd.p4"
#include "include/int_digest.p4"

control Ingress(
        inout ingress_headers_t hdr,
        inout ingress_metadata_t meta,
        in ingress_intrinsic_metadata_t ig_intr_md,
        in ingress_intrinsic_metadata_from_parser_t ig_prsr_md,
        inout ingress_intrinsic_metadata_for_deparser_t ig_dprsr_md,
        inout ingress_intrinsic_metadata_for_tm_t ig_tm_md)
{
    apply {
        hdr.bridge.setValid();
        hdr.bridge.header_type = HEADER_TYPE_BRIDGE;
        forward_frame.apply(ig_intr_md, ig_dprsr_md, ig_tm_md, hdr);
        flow_watchlist_ingress.apply(ig_intr_md, ig_tm_md, hdr.vlan.vid,
                hdr.bridge.flow_id);

        flow_count_idx_t flow_id = hdr.bridge.flow_id;
        stage_int_digest_exit.apply(meta.telem_report,
                ig_dprsr_md.digest_type, ig_dprsr_md.drop_ctl,
                ig_tm_md.bypass_egress);
        flow_meters_ingress.apply(ig_dprsr_md, flow_id, ig_tm_md.packet_color,
                ig_tm_md.qid);
        rx_counters_ingress.apply(ig_tm_md, flow_id);
        int_source_ingress.apply(ig_intr_md, ig_prsr_md, ig_tm_md,
                flow_id, hdr.bridge.telem_md_ingr);
    }
}

control IngressDeparser(
        packet_out pkt,
        inout ingress_headers_t hdr,
        in ingress_metadata_t meta,
        in ingress_intrinsic_metadata_for_deparser_t ig_dprsr_md)
{
    apply {
        int_digest_report.apply(ig_dprsr_md, meta.telem_report);

        pkt.emit(hdr);
    }
}

control Egress(
        inout egress_headers_t hdr,
        inout egress_metadata_t meta,
        in egress_intrinsic_metadata_t eg_intr_md,
        in egress_intrinsic_metadata_from_parser_t eg_prsr_md,
        inout egress_intrinsic_metadata_for_deparser_t eg_dprsr_md,
        inout egress_intrinsic_metadata_for_output_port_t eg_oport_md)
{
    apply {
        tx_counters_egress.apply(eg_intr_md, eg_dprsr_md,
                meta.flow_id);
        stage_int_report_egress.apply(meta.egr_port_mirror, hdr.int_report);
        int_event_egress.apply(eg_intr_md, meta.flow_id, meta.telem_md_ingr,
                eg_dprsr_md.mirror_type, meta.mirror_session,
                meta.egr_port_mirror);
    }
}

control EgressDeparser(
        packet_out pkt,
        inout egress_headers_t hdr,
        in egress_metadata_t meta,
        in egress_intrinsic_metadata_for_deparser_t eg_dprsr_md,
        in egress_intrinsic_metadata_t eg_intr_md)
{
    apply {
        int_event_mirror.apply(eg_dprsr_md, eg_intr_md,
                meta.mirror_session, meta.egr_port_mirror);
        pkt.emit(hdr);
    }
}

Pipeline(
        IngressParser(),
        Ingress(),
        IngressDeparser(),
        EgressParser(),
        Egress(),
        EgressDeparser()
) pipe;

Switch(pipe) main;
