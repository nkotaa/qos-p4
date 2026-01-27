INGRESS_METER_TABLE_BFRUNTIME = "Ingress.flow_meters_ingress.execute_ig_meter"
EGRESS_METER_TABLE_BFRUNTIME = "Egress.flow_meters_egress.execute_eg_meter"

class BFRuntimeIntServ:

    def __init__(self, switch_connection):
        self.switch_connection = switch_connection

    def set_guaranteed(self, flow_selector, bandwidth_kbps):
        ingress_match_list = [{
            "hdr.vlan.vid": flow_selector.source_vlanid,
            "meta.pipe_id": pipe_id,
            "ig_tm_md.ucast_egress_port": flow_selector.egress_port,
            } for pipe_id in range(2)]
        ingress_action = ('Ingress.flow_meters_ingress.invoke_flow_meter', {
            "$METER_SPEC_CIR_KBPS": 0,
            "$METER_SPEC_PIR_KBPS": 25000000,
            "$METER_SPEC_CBS_KBITS": 100000,
            "$METER_SPEC_PBS_KBITS": 1000000,
            })
        egress_match = {
            "hdr.vlan.vid": flow_selector.source_vlanid,
            "eg_intr_md.egress_port": flow_selector.egress_port,
            }
        egress_action = ('Egress.flow_meters_egress.invoke_flow_meter', {
            "$METER_SPEC_CIR_KBPS": bandwidth_kbps,
            "$METER_SPEC_PIR_KBPS": 25000000,
            "$METER_SPEC_CBS_KBITS": 100000,
            "$METER_SPEC_PBS_KBITS": 1000000,
            })
        self.switch_connection.insert_table_entry(
            INGRESS_METER_TABLE_BFRUNTIME, ingress_match_list,
            [ingress_action, ingress_action])
        self.switch_connection.insert_table_entry(
            EGRESS_METER_TABLE_BFRUNTIME, [egress_match], [egress_action])

    def set_best_effort(self, flow_selector):
        ingress_match_list = [{
            "hdr.vlan.vid": flow_selector.source_vlanid,
            "meta.pipe_id": pipe_id,
            "ig_tm_md.ucast_egress_port": flow_selector.egress_port,
            } for pipe_id in range(2)]
        egress_match = {
            "hdr.vlan.vid": flow_selector.source_vlanid,
            "eg_intr_md.egress_port": flow_selector.egress_port,
            }
        self.switch_connection.remove_table_entry(
            INGRESS_METER_TABLE_BFRUNTIME, ingress_match_list)
        self.switch_connection.remove_table_entry(
            EGRESS_METER_TABLE_BFRUNTIME, [egress_match])
