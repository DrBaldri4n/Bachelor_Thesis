# Pfade (Achtung: Auf dem Rechner muss der Pfad identisch sein!)  
DATA_PATH = "EVSE-B-HPC-Kernel-Events-Combined_real.csv"  
# FEATURES = ['L1-dcache-loads', 'L1-icache-loads', 'branch-load-misses', 'br_indirect_spec', 'br_pred', 'bus_access_wr', 'cache-misses', 'cpu-cycles', 'cpu-migrations', 'dp_spec', 'exc_taken', 'inst_spec', 'instructions', 'irq_irq_handler_entry', 'isb_spec', 'iTLB-load-misses', 'kmem_kfree', 'kmem_kmem_cache_alloc', 'l1d_cache', 'l1d_cache_wr', 'l1i_cache', 'l1i_tlb_refill', 'l2d_cache_rd', 'ldrex_spec', 'ldst_spec', 'mem_access', 'mem_access_wr', 'node-stores', 'pagemap_mm_lru_activate', 'pc_write_spec', 'qdisc_qdisc_dequeue', 'raw_syscalls_sys_enter', 'rc_st_spec', 'sched_sched_stat_runtime', 'sock_inet_sock_set_state', 'tcp_tcp_probe', 'ttbr_write_retired', 'unaligned_ldst_spec', 'vfp_spec']

FEATURES = [
    "node-stores",
    "cpu-cycles",
    "block_block_bio_queue",
    "jbd2_jbd2_commit_flushing",
    "syscalls_sys_exit_pipe2",
    "st_spec",
    "dTLB-load-misses",
    "sched_sched_waking",
    "bus_access",
    "br_immed_spec",
    "bus_access_periph",
    "l1d_cache_rd",
    "l1d_cache_wb",
    "node-loads",
    "l2d_cache_wb",
    "l1d_tlb_refill_rd",
    "context-switches",
    "rc_ld_spec",
    "exc_return",
    "br_mis_pred"
]

LABEL = 'Label'  
SEQ_LENGTH = 10 
