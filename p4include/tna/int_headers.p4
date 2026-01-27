#ifndef __INT_COMMON__
#define __INT_COMMON__

#ifndef FLOW_COUNT_INDEX_WIDTH
#define FLOW_COUNT_INDEX_WIDTH 8
#define FLOW_COUNT 1<<FLOW_COUNT_INDEX_WIDTH
#endif /* __FLOW_COUNT_INDEX_WIDTH__ */

typedef bit<FLOW_COUNT_INDEX_WIDTH> flow_count_idx_t;
typedef bit<8> mirror_header_type_t;

const MirrorType_t EGR_PORT_MIRROR = 1;

const mirror_header_type_t HEADER_TYPE_EGR_MIRROR = 0xD;
const DigestType_t TELEM_REPORT_DIGEST_TYPE = 1;

struct telem_md_ingr_t {
    flow_count_idx_t flow_id;
    PortId_t ingress_port;
    bit<48> ingress_mac_tstamp;
    bit<48> ingress_global_tstamp;
    bit<32> rx_count;
}

#ifndef TELEMETRY_FIELDS
#define TELEMETRY_FIELDS \
    @flexible PortId_t ingress_port; \
    @flexible bit<48> ingress_mac_tstamp; \
    @flexible bit<48> ingress_global_tstamp
#endif /* __TELEMETRY_FIELDS__ */

struct telem_digest_t {
    TELEMETRY_FIELDS;
}

header egr_port_mirror_h {
    mirror_header_type_t header_type;
    TELEMETRY_FIELDS;
}

#endif /* __INT_COMMON__ */
