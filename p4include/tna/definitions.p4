#ifndef __DEFINES__
#define __DEFINES__

#define FLOW_COUNT_INDEX_WIDTH 8
#define FLOW_COUNT 1<<FLOW_COUNT_INDEX_WIDTH

typedef bit<FLOW_COUNT_INDEX_WIDTH> flow_count_idx_t;
typedef bit<8> header_type_t;

const MirrorType_t EGR_PORT_MIRROR = 1;

const header_type_t HEADER_TYPE_EGR_MIRROR = 0xD;
const header_type_t HEADER_TYPE_INT_REPORT = 0xE;

const DigestType_t TELEM_REPORT_DIGEST_TYPE = 1;

#endif /* __DEFINES__ */
