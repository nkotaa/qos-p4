#ifndef __CONFIGURATION__
#define __CONFIGURATION__

#define IXP_EGRESS_RESULT_FIELDS \
    bool is_sampled; \
    bit<32> sflow_count; \
    bit<32> tx_bytes_incr

typedef bit<8> header_type_t;

const MirrorType_t EGR_PORT_MIRROR = 1;

const header_type_t HEADER_TYPE_EGR_MIRROR = 0xD;
const header_type_t HEADER_TYPE_INT_REPORT = 0xE;

const DigestType_t TELEM_REPORT_DIGEST_TYPE = 1;

#endif /* __CONFIGURATION__ */
