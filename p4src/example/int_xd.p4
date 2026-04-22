#ifndef __INT_XD__
#define __INT_XD__

control packet_sample_egress(
        in egress_intrinsic_metadata_t eg_intr_md,
        in egress_intrinsic_metadata_from_parser_t eg_prsr_md,
        in egress_intrinsic_metadata_for_deparser_t eg_dprsr_md,
        in egress_intrinsic_metadata_for_output_port_t eg_oport_md,
        in egress_headers_t hdr,
        in egress_metadata_t meta,
        out MirrorType_t mirror_type,
        inout ixp_egress_results_t ixp_eg_res)
{
    Register<bit<32>, flow_count_idx_t>(
            FLOW_COUNT, 0) sflow_counts;
    RegisterAction<bit<32>, flow_count_idx_t, bit<32>>(
        reg=sflow_counts) increment_counter = {
        void apply(inout bit<32> reg_value, out bit<32> rx_count) {
            reg_value = reg_value + 1;
            rx_count = reg_value;
        }
    };

    flow_count_idx_t flow_idx = 0;
    action trigger_sflow_count(flow_count_idx_t flow_id) {
        ixp_eg_res.sflow_count = increment_counter.execute(flow_id);
        flow_idx = flow_id;
    }

    table sample_flow_count {
        key = {
            hdr.ethernet.src_addr: exact;
        }
        actions = {
            trigger_sflow_count;
            NoAction;
        }
        default_action = NoAction();
        size = FLOW_COUNT;
    }

    Register<bit<32>, flow_count_idx_t>(
            FLOW_COUNT, 0) flow_tx_bytes;
    RegisterAction<bit<32>, flow_count_idx_t, bit<32>>(
        reg=flow_tx_bytes) increment_bytes = {
        void apply(inout bit<32> reg_value, out bit<32> tx_bytes) {
            if (eg_dprsr_md.drop_ctl[0:0] == 0) {
                reg_value = reg_value + (bit<32>)eg_intr_md.pkt_length;
            }
            tx_bytes = reg_value;
        }
    };
    RegisterAction<bit<32>, flow_count_idx_t, bit<32>>(
        reg=flow_tx_bytes) reset_bytes = {
        void apply(inout bit<32> reg_value, out bit<32> tx_bytes) {
            if (eg_dprsr_md.drop_ctl[0:0] == 0) {
                tx_bytes = reg_value + (bit<32>)eg_intr_md.pkt_length;
            } else {
                tx_bytes = reg_value;
            }
            reg_value = 0;
        }
    };
    action gather_flow_stats() {
        increment_bytes.execute(flow_idx);
    }
    action mirror_sample() {
        ixp_eg_res.tx_bytes_incr = reset_bytes.execute(flow_idx);
        ixp_eg_res.is_sampled = true;
        mirror_type = EGR_PORT_MIRROR;
    }
    action drop_sample() {
        ixp_eg_res.tx_bytes_incr = reset_bytes.execute(flow_idx);
        ixp_eg_res.is_sampled = true;
    }

    table sample_flow_event {
        key = {
            flow_idx: exact;
            ixp_eg_res.sflow_count: ternary;
            eg_dprsr_md.drop_ctl: ternary;
        }
        actions = {
            mirror_sample;
            drop_sample;
            NoAction;
        }
        default_action = NoAction();
    }

    apply {
        mirror_type = 0;
        ixp_eg_res.is_sampled = false;
        ixp_eg_res.sflow_count = 0;
        ixp_eg_res.tx_bytes_incr = 0;
        if (sample_flow_count.apply().miss) {
            return;
        }
        if (sample_flow_event.apply().miss) {
            gather_flow_stats();
        }
    }
}

control int_event_egress(
        in egress_intrinsic_metadata_t eg_intr_md,
        in egress_metadata_t meta,
        in MirrorType_t mirror_type,
        out MirrorId_t mirror_session,
        out egr_port_mirror_h egr_port_mirror)
{
    action mirror(MirrorId_t int_mirror_session) {
        mirror_session = int_mirror_session;
        egr_port_mirror = {
            HEADER_TYPE_EGR_MIRROR,
            meta.ingress_port,
            meta.ingress_global_tstamp,
            meta.sflow_count,
            eg_intr_md.egress_port,
            eg_intr_md.enq_qdepth,
            eg_intr_md.enq_congest_stat,
            eg_intr_md.deq_qdepth,
            eg_intr_md.deq_congest_stat,
            eg_intr_md.app_pool_congest_stat,
            eg_intr_md.deq_timedelta,
            meta.tx_bytes_incr,
        };
    }

    table sample_mirror {
        key = {
            mirror_type: exact;
        }
        actions = {
            mirror();
            NoAction;
        }
        default_action = NoAction();
    }

    egr_port_mirror_h egr_port_mirror_res;
    apply {
        mirror_session = 0;
        egr_port_mirror_res.setInvalid();
        egr_port_mirror = egr_port_mirror_res;
        sample_mirror.apply();
    }
}

control int_event_mirror(
        in egress_intrinsic_metadata_for_deparser_t eg_dprsr_md,
        in egress_intrinsic_metadata_t eg_intr_md,
        in MirrorId_t mirror_session,
        in egr_port_mirror_h egr_port_mirror)
{
    Mirror(EGR_PORT_MIRROR) int_mirror;
    apply {
        if (eg_dprsr_md.mirror_type == EGR_PORT_MIRROR) {
            int_mirror.emit<egr_port_mirror_h>(
                mirror_session, egr_port_mirror
            );
        }
    }
}

control stage_int_report_egress(
        in egr_port_mirror_h egr_port_mirror,
        inout egress_headers_t hdr)
{
    action encapsulate_int_report() {
        hdr.int_report.setValid();
        hdr.int_report.header_type = HEADER_TYPE_INT_REPORT;
        hdr.int_report.ingress_port = egr_port_mirror.ingress_port;
        hdr.int_report.ingress_global_tstamp =
            egr_port_mirror.ingress_global_tstamp;
        hdr.int_report.rx_count = egr_port_mirror.rx_count;
        hdr.int_report.egress_port = egr_port_mirror.egress_port;
        hdr.int_report.enq_qdepth = egr_port_mirror.enq_qdepth;
        hdr.int_report.enq_congest_stat = egr_port_mirror.enq_congest_stat;
        hdr.int_report.deq_qdepth = egr_port_mirror.deq_qdepth;
        hdr.int_report.deq_congest_stat = egr_port_mirror.deq_congest_stat;
        hdr.int_report.app_pool_congest_stat =
            egr_port_mirror.app_pool_congest_stat;
        hdr.int_report.deq_timedelta = egr_port_mirror.deq_timedelta;
        hdr.int_report.tx_bytes_incr = egr_port_mirror.tx_bytes_incr;
    }

    apply {
        if (!egr_port_mirror.isValid()) {
            return;
        }
        encapsulate_int_report();
    }
}

#endif /* __INT_XD__ */
