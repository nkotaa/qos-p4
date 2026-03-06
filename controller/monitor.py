INGRESS_COUNTER_TABLE_BFRUNTIME = "Ingress.rx_counters_ingress.count_rx"
EGRESS_COUNTER_TABLE_BFRUNTIME = "Egress.tx_counters_egress.count_tx"

class BFRuntimeMonitor:

    def __init__(self, switch_connection):
        self.switch_connection = switch_connection

    def start_rx_counter(self, flow_id, qid=(0,31)):
        ingress_match = self.switch_connection.make_match([
            ("flow_id", {"value": flow_id}),
            ("ig_tm_md.qid", {"low": qid[0], "high": qid[1]}),
            ])
        ingress_action = ('Ingress.rx_counters_ingress.counts', {})
        self.switch_connection.insert_table_entry(
            INGRESS_COUNTER_TABLE_BFRUNTIME, [ingress_match], [ingress_action])

    def start_tx_counter(self, flow_id, qid=(0,31), is_marked_drop=0):
        egress_match = self.switch_connection.make_match([
            ("flow_id", {"value": flow_id}),
            ("eg_intr_md.egress_qid", {"low": qid[0], "high": qid[1]}),
            ("is_marked_drop", {"value": is_marked_drop}),
            ])
        egress_action = ('Egress.tx_counters_egress.counts', {})
        self.switch_connection.insert_table_entry(
            EGRESS_COUNTER_TABLE_BFRUNTIME, [egress_match], [egress_action])

    def stop_rx_counter(self, flow_id, qid=(0,31)):
        ingress_match = self.switch_connection.make_match([
            ("flow_id", {"value": flow_id}),
            ("ig_tm_md.qid", {"low": qid[0], "high": qid[1]}),
            ])
        self.switch_connection.remove_table_entry(
            INGRESS_COUNTER_TABLE_BFRUNTIME, [ingress_match])

    def stop_tx_counter(self, flow_id, qid=(0,31), is_marked_drop=0):
        egress_match = self.switch_connection.make_match([
            ("flow_id", {"value": flow_id}),
            ("eg_intr_md.egress_qid", {"low": qid[0], "high": qid[1]}),
            ("is_marked_drop", {"value": is_marked_drop}),
            ])
        self.switch_connection.remove_table_entry(
            EGRESS_COUNTER_TABLE_BFRUNTIME, [egress_match])

    def read_rx_counter(self, flow_id, qid=(0,31)):
        ingress_match = self.switch_connection.make_match([
            ("flow_id", {"value": flow_id}),
            ("ig_tm_md.qid", {"low": qid[0], "high": qid[1]}),
            ])
        table_entry = self.switch_connection.read_table_entry(
            INGRESS_COUNTER_TABLE_BFRUNTIME, [ingress_match], from_hw=True)[0]
        rx_count = table_entry["$COUNTER_SPEC_BYTES"]
        return rx_count
