#ifndef __RX_TX_COUNTERS__
#define __RX_TX_COUNTERS__

control rx_counters_ingress(
        in ingress_intrinsic_metadata_t ig_intr_md,
        in ingress_intrinsic_metadata_for_tm_t ig_tm_md)
{
    DirectCounter<bit<64>>(CounterType_t.PACKETS_AND_BYTES) rx_counters;

    action counts() {
        rx_counters.count();
    }

    table count_rx {
        key = {
            ig_intr_md.ingress_port: exact;
            ig_tm_md.ucast_egress_port: exact;
        }
        actions = {
            counts;
        }
        size = 128;
        counters = rx_counters;
    }

    apply {
        count_rx.apply();
    }
}

control tx_counters_egress(
        in egress_metadata_t meta,
        in egress_intrinsic_metadata_t eg_intr_md)
{
    DirectCounter<bit<64>>(CounterType_t.PACKETS_AND_BYTES) tx_counters;

    action counts() {
        tx_counters.count();
    }

    table count_tx {
        key = {
            meta.ingress_port: exact;
            eg_intr_md.egress_port: exact;
        }
        actions = {
            counts;
        }
        size = 128;
        counters = tx_counters;
    }

    apply {
        count_tx.apply();
    }
}

#endif /* __RX_TX_COUNTERS__ */
