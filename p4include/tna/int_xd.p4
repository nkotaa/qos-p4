#ifndef __INT_XD__
#define __INT_XD__

control int_source_ingress(
        in ingress_intrinsic_metadata_t ig_intr_md,
        in ingress_intrinsic_metadata_from_parser_t ig_prsr_md,
        in ingress_intrinsic_metadata_for_tm_t ig_tm_md,
        inout telem_md_ingr_t telem_md_ingr)
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
    flow_count_idx_t flow_id = telem_md_ingr.flow_id;

    action stage_metadata(inout telem_md_ingr_t staged_metadata) {
        bit<32> rx_count = increment_counter.execute(flow_id);
        staged_metadata.ingress_port = ig_intr_md.ingress_port;
        staged_metadata.ingress_mac_tstamp = ig_intr_md.ingress_mac_tstamp;
        staged_metadata.ingress_global_tstamp = ig_prsr_md.global_tstamp;
        staged_metadata.rx_count = rx_count;
    }

    table int_source {
        key = {
            flow_id: exact;
        }
        actions = {
            stage_metadata(telem_md_ingr);
            NoAction;
        }
        default_action = NoAction;
    }

    apply {
        int_source.apply();
    }
}

control int_event_egress(
        in egress_intrinsic_metadata_t eg_intr_md,
        inout egress_intrinsic_metadata_for_deparser_t eg_dprsr_md,
        out MirrorId_t mirror_session,
        in telem_md_ingr_t telem_md_ingr,
        out egr_port_mirror_h egr_port_mirror)
{
    Register<bit<32>, flow_count_idx_t>(FLOW_COUNT, 0) sflow_counts;
    RegisterParam<bit<32>>(1000) sflow_freq;
    RegisterAction<bit<32>, flow_count_idx_t, bool>(
        reg=sflow_counts) do_sflow = {
        void apply(inout bit<32> reg_value, out bool is_sflow) {
            if (reg_value < sflow_freq.read()) {
                reg_value = reg_value + 1;
                is_sflow = false;
            } else {
                reg_value = 1;
                is_sflow = true;
            }
        }
    };
    bool is_sflow = false;
    action trigger_sflow_count() {
        is_sflow = do_sflow.execute(telem_md_ingr.flow_id);
    }
    action mirror(out egr_port_mirror_h egr_port_mirror_header,
            MirrorId_t int_mirror_session) {
        eg_dprsr_md.mirror_type = EGR_PORT_MIRROR;
        mirror_session = int_mirror_session;
        egr_port_mirror_header = {
            HEADER_TYPE_EGR_MIRROR,
            telem_md_ingr.ingress_port,
            telem_md_ingr.ingress_global_tstamp,
            telem_md_ingr.rx_count,
            eg_intr_md.egress_port,
            eg_intr_md.enq_qdepth,
            eg_intr_md.enq_congest_stat,
            eg_intr_md.deq_qdepth,
            eg_intr_md.deq_congest_stat,
            eg_intr_md.app_pool_congest_stat,
            eg_intr_md.deq_timedelta,
        };
    }

    table sample_flow_count {
        key = {
            telem_md_ingr.flow_id: exact;
        }
        actions = {
            trigger_sflow_count;
            NoAction;
        }
        default_action = NoAction();
        size = FLOW_COUNT;
    }

    table int_event_trigger {
        key = {
            is_sflow: exact;
        }
        actions = {
            mirror(egr_port_mirror);
            NoAction;
        }
        default_action = NoAction();
        size = FLOW_COUNT;
    }

    apply {
        sample_flow_count.apply();
        int_event_trigger.apply();
    }
}

#endif /* __INT_XD__ */
