INGRESS_COUNTER_TABLE_BFRUNTIME = "Ingress.rx_counters_ingress.count_rx"
EGRESS_COUNTER_TABLE_BFRUNTIME = "Egress.tx_counters_egress.count_tx"

class BFRuntimeMonitor:

    def __init__(self, switch_connection):
        self.switch_connection = switch_connection

    def start_counter(self, flow_selector):
        ingress_match = {
            "ig_intr_md.ingress_port": flow_selector.ingress_port,
            "ig_tm_md.ucast_egress_port": flow_selector.egress_port,
            }
        ingress_action = ('Ingress.rx_counters_ingress.counts', {})
        egress_match = {
            "meta.ingress_port": flow_selector.ingress_port,
            "eg_intr_md.egress_port": flow_selector.egress_port,
            }
        egress_action = ('Egress.tx_counters_egress.counts', {})
        self.switch_connection.insert_table_entry(
            INGRESS_COUNTER_TABLE_BFRUNTIME, [ingress_match], [ingress_action])
        self.switch_connection.insert_table_entry(
            EGRESS_COUNTER_TABLE_BFRUNTIME, [egress_match], [egress_action])

    def stop_counter(self, flow_selector):
        ingress_match = {
            "ig_intr_md.ingress_port": flow_selector.ingress_port,
            "ig_tm_md.ucast_egress_port": flow_selector.egress_port,
            }
        egress_match = {
            "meta.ingress_port": flow_selector.ingress_port,
            "eg_intr_md.egress_port": flow_selector.egress_port,
            }
        self.switch_connection.remove_table_entry(
            INGRESS_COUNTER_TABLE_BFRUNTIME, [ingress_match])
        self.switch_connection.remove_table_entry(
            EGRESS_COUNTER_TABLE_BFRUNTIME, [egress_match])
