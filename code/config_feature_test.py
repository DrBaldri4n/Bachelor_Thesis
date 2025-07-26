# Pfade (Achtung: Auf dem Rechner muss der Pfad identisch sein!)  
DATA_PATH = "EVSE-B-HPC-Kernel-Events-Combined_real.csv"  
# FEATURES = ['L1-dcache-loads', 'L1-icache-loads', 'branch-load-misses', 'br_indirect_spec', 'br_pred', 'bus_access_wr', 'cache-misses', 'cpu-cycles', 'cpu-migrations', 'dp_spec', 'exc_taken', 'inst_spec', 'instructions', 'irq_irq_handler_entry', 'isb_spec', 'iTLB-load-misses', 'kmem_kfree', 'kmem_kmem_cache_alloc', 'l1d_cache', 'l1d_cache_wr', 'l1i_cache', 'l1i_tlb_refill', 'l2d_cache_rd', 'ldrex_spec', 'ldst_spec', 'mem_access', 'mem_access_wr', 'node-stores', 'pagemap_mm_lru_activate', 'pc_write_spec', 'qdisc_qdisc_dequeue', 'raw_syscalls_sys_enter', 'rc_st_spec', 'sched_sched_stat_runtime', 'sock_inet_sock_set_state', 'tcp_tcp_probe', 'ttbr_write_retired', 'unaligned_ldst_spec', 'vfp_spec']

FEATURES = [
    "syscalls_sys_exit_recvfrom",
    "bus_access_not_shared",
    "tcp_tcp_retransmit_skb",
    "jbd2_jbd2_checkpoint_stats",
    "l2d_cache_wb",
    "jbd2_jbd2_shrink_count",
    "qdisc_qdisc_dequeue",
    "syscalls_sys_enter_accept4",
    "syscalls_sys_enter_accept",
    "node-loads",
    "bus-cycles",
    "iTLB-load-misses",
    "dTLB-load-misses",
    "node-stores",
    "l1d_cache_wb_clean",
    "syscalls_sys_enter_fchmod",
    "dp_spec",
    "l2d_cache_refill_rd",
    "br_mis_pred",
    "mem_access"
]


LABEL = 'Label'  
SEQ_LENGTH = 10 
