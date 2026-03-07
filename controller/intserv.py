INGRESS_METER_TABLE_BFRUNTIME = "Ingress.flow_meters_ingress.execute_ig_meter"
BEST_EFFORT_BANDWIDTH_KBPS = 100000000
BEST_EFFORT_BURST_RATE_KBPS = 1000000

class BFRuntimeIntServ:

    def __init__(self, switch_connection):
        self.switch_connection = switch_connection

    def set_guaranteed(self, flow_id, bandwidth_kbps, burst_rate_kbps=10000):
        ingress_match = self.switch_connection.make_match([
            ("flow_id", {"value": flow_id}),
            ])
        ingress_action = ('Ingress.flow_meters_ingress.set_color', {
            "$METER_SPEC_CIR_KBPS": bandwidth_kbps,
            "$METER_SPEC_PIR_KBPS": BEST_EFFORT_BANDWIDTH_KBPS,
            "$METER_SPEC_CBS_KBITS": burst_rate_kbps,
            "$METER_SPEC_PBS_KBITS": BEST_EFFORT_BURST_RATE_KBPS,
            })
        self.switch_connection.insert_table_entry(
            INGRESS_METER_TABLE_BFRUNTIME, [ingress_match], [ingress_action])

    def set_best_effort(self, flow_id):
        ingress_match = self.switch_connection.make_match([
            ("flow_id", {"value": flow_id}),
            ])
        self.switch_connection.remove_table_entry(
            INGRESS_METER_TABLE_BFRUNTIME, [ingress_match])
