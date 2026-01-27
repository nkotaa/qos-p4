from dataclasses import dataclass

# From rfc1633: "flow" abstraction as a distinguishable stream of related
# datagrams that results from a single user activity and requires the same QoS.
@dataclass
class DataFlow:
    ingress_port: int = None
    source_vlanid: int = None
    egress_port: int = None
    dest_vlanid: int = None
