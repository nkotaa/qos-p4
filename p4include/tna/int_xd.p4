#ifndef __INT_XD__
#define __INT_XD__

#include "int_headers.p4"

control int_source_ingress(
        out telem_md_ingr_t telem_md_ingr,
        in ingress_metadata_t meta,
        in ingress_intrinsic_metadata_t ig_intr_md,
        in ingress_intrinsic_metadata_from_parser_t ig_prsr_md,
        in ingress_intrinsic_metadata_for_tm_t ig_tm_md)
{
    Register<bit<32>, flow_count_idx_t>(
            FLOW_COUNT, 0) rx_counters;
    RegisterAction<bit<32>, flow_count_idx_t, bit<32>>(
        reg=rx_counters) increment_counter = {
        void apply(inout bit<32> reg_value, out bit<32> rx_count) {
            reg_value = reg_value + 1;
            rx_count = reg_value;
        }
    };
    action trigger_counter(out bit<32> rx_count, flow_count_idx_t stats_idx) {
        rx_count = increment_counter.execute(stats_idx);
    }

    action collect_metadata(in flow_count_idx_t flow_id) {
        bit<32> rx_count;
        trigger_counter(rx_count, flow_id);
        telem_md_ingr = {
            flow_id,
            ig_intr_md.ingress_port,
            ig_intr_md.ingress_mac_tstamp,
            ig_prsr_md.global_tstamp,
            rx_count
        };
    }

    table int_source {
        key = {
            meta.flow_id: exact;
        }
        actions = {
            collect_metadata(meta.flow_id);
            NoAction;
        }
        default_action = NoAction;
    }

    apply {
        int_source.apply();
    }
}

control flow_watchlist_ingress(
        in ingress_headers_t hdr,
        inout ingress_metadata_t meta,
        in ingress_intrinsic_metadata_t ig_intr_md,
        in ingress_intrinsic_metadata_from_parser_t ig_prsr_md,
        in ingress_intrinsic_metadata_for_tm_t ig_tm_md)
{
    action set_flow_id(flow_count_idx_t flow_id) {
        meta.flow_id = flow_id;
    }
    table flow_watchlist {
        key = {
            ig_intr_md.ingress_port: exact;
            ig_tm_md.ucast_egress_port: exact;
            hdr.vlan.vid: exact;
        }
        actions = {
            set_flow_id;
            NoAction;
        }
        default_action = NoAction();
        size = FLOW_COUNT;
    }
    apply {
        flow_watchlist.apply();
    }
}

control int_recirc_ingress(
        in egr_port_mirror_h telem_report,
        inout ingress_intrinsic_metadata_for_deparser_t ig_dprsr_md)
{
    apply {
        if (!telem_report.isValid()) {
            return;
        }
        ig_dprsr_md.digest_type = TELEM_REPORT_DIGEST_TYPE;
        ig_dprsr_md.drop_ctl = 1;
    }
}

// event determination is preferred at egress because triggers might be desired
// based on information only available in eg_intr_md
// total number of mirror sessions = bit<10>
control int_event_egress(
        inout egress_metadata_t meta,
        in egress_intrinsic_metadata_t eg_intr_md,
        inout egress_intrinsic_metadata_for_deparser_t eg_dprsr_md)
{
    action mirror(out bool is_event, MirrorId_t mirror_session){
        meta.mirror_session = mirror_session;
        meta.mirror_type = HEADER_TYPE_EGR_MIRROR;
        is_event = true;
    }

    bool is_event = false;
    table int_event_trigger {
        key = {
            meta.telem_md_ingr.flow_id: exact;
            meta.telem_md_ingr.rx_count: ternary;
            (bit<16>)meta.telem_md_ingr.ingress_global_tstamp: range @name("timestamp");
        }
        actions = {
            mirror(is_event);
            NoAction;
        }
        default_action = NoAction();
        size = FLOW_COUNT;
    }

    apply {
        if (int_event_trigger.apply().hit) {
            eg_dprsr_md.mirror_type = EGR_PORT_MIRROR;
        }
    }
}

control int_event_report(
        in egr_port_mirror_h telem_report,
        in ingress_intrinsic_metadata_for_deparser_t ig_dprsr_md)
{
    Digest <telem_digest_t>() telem_digest;
    apply {
        if (ig_dprsr_md.digest_type == TELEM_REPORT_DIGEST_TYPE) {
            telem_digest.pack(
                {
                    telem_report.ingress_port,
                    telem_report.ingress_mac_tstamp,
                    telem_report.ingress_global_tstamp,
                }
            );
        }
    }
}

control int_event_mirror(
        in MirrorId_t mirror_session,
        in mirror_header_type_t mirror_type,
        in telem_md_ingr_t telem_md_ingr,
        in egress_intrinsic_metadata_for_deparser_t eg_dprsr_md,
        in egress_intrinsic_metadata_t eg_intr_md)
{
    Mirror() egr_port_mirror;
    apply {
        if (eg_dprsr_md.mirror_type == EGR_PORT_MIRROR) {
            egr_port_mirror.emit<egr_port_mirror_h>(
                mirror_session,
                {
                    mirror_type,
                    telem_md_ingr.ingress_port,
                    telem_md_ingr.ingress_mac_tstamp,
                    telem_md_ingr.ingress_global_tstamp,
                }
            );
        }
    }
}

#endif /* __INT_XD__ */
