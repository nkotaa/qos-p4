#ifndef __FLOW_WATCHLIST__
#define __FLOW_WATCHLIST__

control flow_watchlist_ingress(
        in ingress_intrinsic_metadata_t ig_intr_md,
        in ingress_intrinsic_metadata_for_tm_t ig_tm_md,
        in ingress_headers_t hdr,
        out flow_count_idx_t flow_id_res)
{
    action set_flow_id(flow_count_idx_t flow_id) {
        flow_id_res = flow_id;
    }
    table flow_watchlist {
        key = {
            hdr.ethernet.src_addr: exact;
            hdr.ethernet.dst_addr: exact;
            hdr.vlan.vid: exact;
        }
        actions = {
            set_flow_id;
            NoAction;
        }
        default_action = NoAction();
        size = FLOW_COUNT;
    }
    apply {
        flow_watchlist.apply();
    }
}

#endif /* __FLOW_WATCHLIST__ */
