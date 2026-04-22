#ifndef __HEADERS__
#define __HEADERS__

#include "int_headers.p4"

typedef bit<48> MacAddr_t;
typedef bit<16> EtherType_t;

const header_type_t HEADER_TYPE_BRIDGE = 0xC;

header bridge_h {
    header_type_t header_type;
    @flexible flow_count_idx_t flow_id;
    @flexible PortId_t ingress_port;
    @flexible bit<48> ingress_mac_tstamp;
    @flexible bit<48> ingress_global_tstamp;
}

header ethernet_h {
    MacAddr_t dst_addr;
    MacAddr_t src_addr;
    EtherType_t ether_type;
}

header vlan_h {
    bit<4> pcp_dei;
    bit<12> vid;
    EtherType_t ether_type;
}

struct ingress_headers_t {
    bridge_h bridge;
    ethernet_h ethernet;
    vlan_h vlan;
}

struct ingress_metadata_t {
    int_report_h telem_report;
}

struct egress_headers_t {
    int_report_h int_report;
    ethernet_h ethernet;
    vlan_h vlan;
}

struct egress_metadata_t {
    flow_count_idx_t flow_id;
    PortId_t ingress_port;
    bit<48> ingress_mac_tstamp;
    bit<48> ingress_global_tstamp;
    bit<32> sflow_count;
    bit<32> tx_bytes_incr;
    MirrorId_t mirror_session;
    egr_port_mirror_h egr_port_mirror;
}

#endif /* __HEADERS__ */
