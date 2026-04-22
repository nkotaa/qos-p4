#ifndef __IXP_TYPES__
#define __IXP_TYPES__

#ifndef FLOW_COUNT_INDEX_WIDTH
#define FLOW_COUNT_INDEX_WIDTH 8
#endif
#define FLOW_COUNT 1<<FLOW_COUNT_INDEX_WIDTH

#ifndef IXP_INGRESS_RESULT_FIELDS
#define IXP_INGRESS_RESULT_FIELDS \
    flow_count_idx_t flow_id
#endif

#ifndef IXP_EGRESS_RESULT_FIELDS
#define IXP_EGRESS_RESULT_FIELDS \
    bool is_sampled
#endif

type bit<FLOW_COUNT_INDEX_WIDTH> flow_count_idx_t;

struct ixp_ingress_results_t {
    IXP_INGRESS_RESULT_FIELDS;
}

struct ixp_egress_results_t {
    IXP_EGRESS_RESULT_FIELDS;
}

#endif /* __IXP_TYPES__ */
