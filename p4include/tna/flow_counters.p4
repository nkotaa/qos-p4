#ifndef __FLOW_COUNTERS__
#define __FLOW_COUNTERS__

control rx_counters_ingress(
        in ingress_intrinsic_metadata_for_tm_t ig_tm_md,
        in flow_count_idx_t flow_id)
{
    DirectCounter<bit<64>>(CounterType_t.PACKETS_AND_BYTES) rx_counters;

    action counts() {
        rx_counters.count();
    }

    table count_rx {
        key = {
            flow_id: exact;
            ig_tm_md.qid: range;
        }
        actions = {
            counts;
        }
        size = 1<<(FLOW_COUNT_INDEX_WIDTH + QUEUE_ID_WIDTH);
        counters = rx_counters;
    }

    apply {
        count_rx.apply();
    }
}

control tx_counters_egress(
        in egress_intrinsic_metadata_t eg_intr_md,
        in egress_intrinsic_metadata_for_deparser_t eg_dprsr_md,
        in flow_count_idx_t flow_id)
{
    DirectCounter<bit<64>>(CounterType_t.PACKETS_AND_BYTES) tx_counters;

    action counts() {
        tx_counters.count();
    }

    table count_tx {
        key = {
            flow_id: exact;
            eg_intr_md.egress_qid: range;
            eg_dprsr_md.drop_ctl[0:0]: exact @name("is_marked_drop");
        }
        actions = {
            counts;
        }
        size = 1<<(FLOW_COUNT_INDEX_WIDTH + QUEUE_ID_WIDTH + 1);
        counters = tx_counters;
    }

    apply {
        count_tx.apply();
    }
}

#endif /* __FLOW_COUNTERS__ */
