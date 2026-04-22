#ifndef __PARSERS__
#define __PARSERS__

parser IngressParser(
        packet_in pkt,
        out ingress_headers_t hdr,
        out ingress_metadata_t meta,
        out ingress_intrinsic_metadata_t ig_intr_md)
{
    state start {
        pkt.extract(ig_intr_md);
        pkt.advance(PORT_METADATA_SIZE);

        transition select(ig_intr_md.ingress_port) {
            68 &&& DEVPORT_PORT_MASK: parse_recirc;
            default: parse_ethernet;
        }
    }

    state parse_recirc {
        transition select (pkt.lookahead<header_type_t>()) {
            HEADER_TYPE_INT_REPORT: parse_telem_report;
            default: reject;
        }
    }

    state parse_telem_report {
        pkt.extract(meta.telem_report);
        transition accept;
    }

    state parse_ethernet {
        pkt.extract(hdr.ethernet);
        transition select(hdr.ethernet.ether_type) {
            0x8100: parse_vlan;
            default: accept;
        }
    }

    state parse_vlan {
        pkt.extract(hdr.vlan);
        transition accept;
    }
}

parser EgressParser(
        packet_in pkt,
        out egress_headers_t hdr,
        out egress_metadata_t meta,
        out egress_intrinsic_metadata_t eg_intr_md)
{
    bridge_h bridge;

    state start {
        pkt.extract(eg_intr_md);

        transition select (pkt.lookahead<header_type_t>()) {
            HEADER_TYPE_EGR_MIRROR: parse_egr_mirror;
            HEADER_TYPE_BRIDGE: parse_bridge;
            default: reject;
        }
    }

    state parse_egr_mirror {
        pkt.extract(meta.egr_port_mirror);
        transition parse_ethernet;
    }

    state parse_bridge {
        pkt.extract(bridge);
        meta.flow_id = bridge.flow_id;
        meta.ingress_port = bridge.ingress_port;
        meta.ingress_mac_tstamp = bridge.ingress_mac_tstamp;
        meta.ingress_global_tstamp = bridge.ingress_global_tstamp;
        transition parse_ethernet;
    }

    state parse_ethernet {
        pkt.extract(hdr.ethernet);
        transition select(hdr.ethernet.ether_type) {
            0x8100: parse_vlan;
            default: accept;
        }
    }

    state parse_vlan {
        pkt.extract(hdr.vlan);
        transition accept;
    }
}

#endif /* __PARSERS__ */
