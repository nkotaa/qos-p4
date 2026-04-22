#ifndef __FORWARD__
#define __FORWARD__

const MulticastGroupId_t BROADCAST_ID = 0xffff;
const ReplicationId_t BROADCAST_REPLICATION_ID = 0xffff;
const int MAC_ADDRESS_TABLE_SIZE = 65536;

control forward_frame(
        in ingress_intrinsic_metadata_t ig_intr_md,
        in ingress_intrinsic_metadata_for_deparser_t ig_dprsr_md,
        inout ingress_intrinsic_metadata_for_tm_t ig_tm_md,
        in ingress_headers_t hdr,
        out bit<3> drop_ctl,
        out DigestType_t digest_type)
{
    action flood() {
        ig_tm_md.mcast_grp_a = BROADCAST_ID;
        ig_tm_md.rid = BROADCAST_REPLICATION_ID;
    }

    action set_dest_port(PortId_t egress_port) {
        ig_tm_md.ucast_egress_port = egress_port;
    }

    table dest_mac {
        key = {
            hdr.ethernet.dst_addr: exact;
        }
        actions = {
            flood;
            set_dest_port;
        }
        const default_action = flood();
        size = MAC_ADDRESS_TABLE_SIZE;
    }

    apply {
        if (ig_dprsr_md.drop_ctl[0:0] == 1
                || ig_tm_md.mcast_grp_a != 0
                || ig_tm_md.mcast_grp_b != 0)
        {
            return;
        }
        dest_mac.apply();

    }
}

#endif /* __FORWARD__ */
