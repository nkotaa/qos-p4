#ifndef __INT_DIGEST__
#define __INT_DIGEST__

control stage_int_digest_exit(
        in int_report_h telem_report,
        out DigestType_t digest_type,
        out bit<3> drop_ctl,
        out bit<1> bypass_egress)
{
    apply {
        if (!telem_report.isValid()) {
            return;
        }
        digest_type = TELEM_REPORT_DIGEST_TYPE;
        drop_ctl = 1;
        bypass_egress = 1w1;
        exit;
    }
}

control int_digest_report(
        in ingress_intrinsic_metadata_for_deparser_t ig_dprsr_md,
        in int_report_h telem_report)
{
    Digest <telem_digest_t>(TELEM_REPORT_DIGEST_TYPE) telem_digest;
    apply {
        if (ig_dprsr_md.digest_type == TELEM_REPORT_DIGEST_TYPE) {
            telem_digest.pack(
                {
                    telem_report.ingress_port,
                    telem_report.ingress_global_tstamp,
                    telem_report.rx_count,
                    telem_report.egress_port,
                    telem_report.enq_qdepth,
                    telem_report.enq_congest_stat,
                    telem_report.deq_qdepth,
                    telem_report.deq_congest_stat,
                    telem_report.app_pool_congest_stat,
                    telem_report.deq_timedelta,
                }
            );
        }
    }
}

#endif /* __INT_DIGEST__ */
