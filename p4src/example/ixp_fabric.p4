#include <core.p4>
#include <tna.p4>

#include "configuration.p4"
#include "../ixp_core.p4"

#include "headers.p4"
#include "parsers.p4"
#include "forward.p4"
#include "flow_watchlist.p4"
#include "int_xd.p4"
#include "int_digest.p4"
#ifdef ENABLE_FLOW_COUNTERS
#include "../include/flow_counters.p4"
#endif
#ifdef ENABLE_FLOW_METERS
#include "../include/flow_meters.p4"
#endif

control empty_rate_limit_ingress(
        in ingress_intrinsic_metadata_t ig_intr_md,
        in ingress_intrinsic_metadata_from_parser_t ig_prsr_md,
        in ingress_intrinsic_metadata_for_deparser_t ig_dprsr_md,
        in ingress_intrinsic_metadata_for_tm_t ig_tm_md,
        in ingress_headers_t hdr,
        out bit<3> drop_ctl)
{
    apply { }
}

control empty_rate_limit_egress(
        in egress_intrinsic_metadata_t eg_intr_md,
        in egress_intrinsic_metadata_from_parser_t eg_prsr_md,
        in egress_intrinsic_metadata_for_deparser_t eg_dprsr_md,
        in egress_intrinsic_metadata_for_output_port_t eg_oport_md,
        in egress_headers_t hdr,
        out bit<3> drop_ctl)
{
    apply { }
}

control Ingress(
        inout ingress_headers_t hdr,
        inout ingress_metadata_t meta,
        in ingress_intrinsic_metadata_t ig_intr_md,
        in ingress_intrinsic_metadata_from_parser_t ig_prsr_md,
        inout ingress_intrinsic_metadata_for_deparser_t ig_dprsr_md,
        inout ingress_intrinsic_metadata_for_tm_t ig_tm_md)
{
    ixp_ingress_results_t ixp_ig_res;
    IXPIngressHead<ingress_headers_t, ingress_metadata_t>(
            empty_rate_limit_ingress(), flow_watchlist_ingress()) ixp_ingr_head;
    IXPIngressTail<ingress_headers_t, ingress_metadata_t>(
            forward_frame()) ixp_ingr_tail;

    apply {
        hdr.bridge.setValid();
        hdr.bridge.header_type = HEADER_TYPE_BRIDGE;
        ixp_ingr_head.apply(hdr, meta, ig_intr_md, ig_prsr_md, ig_dprsr_md,
                ig_tm_md, ixp_ig_res);

        stage_int_digest_exit.apply(meta.telem_report,
                ig_dprsr_md.digest_type, ig_dprsr_md.drop_ctl,
                ig_tm_md.bypass_egress);
        flow_count_idx_t flow_id = ixp_ig_res.flow_id;
#ifdef ENABLE_FLOW_METERS
        flow_meters_ingress.apply(ig_dprsr_md, flow_id, ig_tm_md.packet_color,
                ig_tm_md.qid);
#endif
#ifdef ENABLE_FLOW_COUNTERS
        rx_counters_ingress.apply(ig_tm_md, flow_id);
#endif

        ixp_ingr_tail.apply(hdr, meta, ig_intr_md, ig_prsr_md, ig_dprsr_md,
                ig_tm_md, ixp_ig_res);
        hdr.bridge.flow_id = flow_id;
        hdr.bridge.ingress_port = ig_intr_md.ingress_port;
        hdr.bridge.ingress_mac_tstamp = ig_intr_md.ingress_mac_tstamp;
        hdr.bridge.ingress_global_tstamp = ig_prsr_md.global_tstamp;
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
    bridge_h bridge;
    ixp_egress_results_t ixp_eg_res;
    IXPEgressHead<egress_headers_t, egress_metadata_t>(
            empty_rate_limit_egress()) ixp_egr_head;
    IXPEgressTail<egress_headers_t, egress_metadata_t>(
            packet_sample_egress()) ixp_egr_tail;

    apply {
        ixp_egr_head.apply(hdr, meta, eg_intr_md, eg_prsr_md, eg_dprsr_md,
                eg_oport_md, ixp_eg_res);

#ifdef ENABLE_FLOW_COUNTERS
        tx_counters_egress.apply(eg_intr_md, eg_dprsr_md,
                meta.flow_id, sizeInBytes(bridge));
#endif

        stage_int_report_egress.apply(meta.egr_port_mirror, hdr);
        ixp_egr_tail.apply(hdr, meta, eg_intr_md, eg_prsr_md, eg_dprsr_md,
                eg_oport_md, ixp_eg_res);
        meta.sflow_count = ixp_eg_res.sflow_count;
        meta.tx_bytes_incr = ixp_eg_res.tx_bytes_incr;
        int_event_egress.apply(eg_intr_md, meta, eg_dprsr_md.mirror_type,
                meta.mirror_session, meta.egr_port_mirror);
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
