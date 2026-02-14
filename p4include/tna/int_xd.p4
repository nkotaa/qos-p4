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

#endif /* __INT_XD__ */
