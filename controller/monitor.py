INGRESS_COUNTER_TABLE_BFRUNTIME = "rx_counters_ingress.count_rx"
EGRESS_COUNTER_TABLE_BFRUNTIME = "tx_counters_egress.count_tx"
INGRESS_COUNT_ACTION = "rx_counters_ingress.counts"
EGRESS_COUNT_ACTION = "tx_counters_egress.counts"

class BFRuntimeMonitor:

    def __init__(self, switch_connection):
        self.switch_connection = switch_connection

    def start_rx_counter(self, flow_id, qid=(0,31)):
        ingress_match = self.switch_connection.make_match([
            ("flow_id", {"value": flow_id}),
            ("ig_tm_md.qid", {"low": qid[0], "high": qid[1]}),
            ])
        ingress_action = (INGRESS_COUNT_ACTION, {})
        self.switch_connection.set_table_entries(
            INGRESS_COUNTER_TABLE_BFRUNTIME, [ingress_match], [ingress_action])

    def start_tx_counter(self, flow_id, qid=(0,31), is_marked_drop=0):
        egress_match = self.switch_connection.make_match([
            ("flow_id", {"value": flow_id}),
            ("eg_intr_md.egress_qid", {"low": qid[0], "high": qid[1]}),
            ("is_marked_drop", {"value": is_marked_drop}),
            ])
        egress_action = (EGRESS_COUNT_ACTION, {})
        self.switch_connection.set_table_entries(
            EGRESS_COUNTER_TABLE_BFRUNTIME, [egress_match], [egress_action])

    def stop_rx_counter(self, flow_id, qid=(0,31)):
        ingress_match = self.switch_connection.make_match([
            ("flow_id", {"value": flow_id}),
            ("ig_tm_md.qid", {"low": qid[0], "high": qid[1]}),
            ])
        self.switch_connection.remove_table_entries(
            INGRESS_COUNTER_TABLE_BFRUNTIME, [ingress_match])

    def stop_tx_counter(self, flow_id, qid=(0,31), is_marked_drop=0):
        egress_match = self.switch_connection.make_match([
            ("flow_id", {"value": flow_id}),
            ("eg_intr_md.egress_qid", {"low": qid[0], "high": qid[1]}),
            ("is_marked_drop", {"value": is_marked_drop}),
            ])
        self.switch_connection.remove_table_entries(
            EGRESS_COUNTER_TABLE_BFRUNTIME, [egress_match])

    def read_rx_counter(self, flow_id, qid=(0,31)):
        ingress_match = self.switch_connection.make_match([
            ("flow_id", {"value": flow_id}),
            ("ig_tm_md.qid", {"low": qid[0], "high": qid[1]}),
            ])
        table_entry = self.switch_connection.read_table_entries(
            INGRESS_COUNTER_TABLE_BFRUNTIME, [ingress_match], from_hw=True)[0]
        rx_count = table_entry["$COUNTER_SPEC_BYTES"]
        return rx_count

    def read_tx_counter(self, flow_id, qid=(0,31), is_marked_drop=0):
        egress_match = self.switch_connection.make_match([
            ("flow_id", {"value": flow_id}),
            ("eg_intr_md.egress_qid", {"low": qid[0], "high": qid[1]}),
            ("is_marked_drop", {"value": is_marked_drop}),
            ])
        table_entry = self.switch_connection.read_table_entries(
            EGRESS_COUNTER_TABLE_BFRUNTIME, [egress_match], from_hw=True)[0]
        tx_count = table_entry["$COUNTER_SPEC_BYTES"]
        return tx_count
