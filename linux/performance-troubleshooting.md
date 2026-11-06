# Linux Performance Troubleshooting
A short path from "the server is slow" to the resource that is the cause. Start with the USE method (utilisation, saturation, errors for each resource), then use the one-liners below to dig into CPU, memory, disk and network.

Documentation: [Brendan Gregg: Linux Performance](https://www.brendangregg.com/linuxperf.html) · [USE Method](https://www.brendangregg.com/usemethod.html) · `man sar`, `man vmstat`, `man ss`

> **Verification:** commands follow the man pages and common practice. No command was executed. Most need `sysstat` (`sudo apt install sysstat`), plus `htop`, `iotop`, `iftop` or `nethogs` where noted. `perf` and `strace` can slow the target; use them briefly on production.

See also: [Linux](linux.md) · [systemd](systemd.md) · [Storage and Filesystems](storage-and-filesystems.md) · [Docker Troubleshooting](../docker/docker-troubleshooting.md) · [IPTables](iptables.md) · [tmux](../tools/tmux.md)

---
## USE Method Checklist
For each resource ask: how busy is it (**U**), is work queueing (**S**), are there errors (**E**)?

RESOURCE | UTILISATION | SATURATION | ERRORS
---|---|---|---
CPU | `mpstat -P ALL 1` (`%usr+%sys`) | `vmstat 1` column `r` above core count, load average | `dmesg -T \| grep -i mce`
Memory | `free -h`, `vmstat 1` | Swapping: `si`/`so` columns, `sar -B`, PSI `/proc/pressure/memory` | `dmesg -T \| grep -i 'out of memory'`
Disk | `iostat -xz 1` (`%util`) | `aqu-sz`, `await` | `smartctl -a`, `dmesg \| grep -i 'I/O error'`
Network | `sar -n DEV 1` vs link speed | `ss -s`, `nstat`, drops in `ip -s link` | `ip -s link` errors, `ethtool -S <IF>`

---
## First 60 Seconds
```bash
uptime                       # load averages: 1, 5, 15 minutes
dmesg -T | tail -20          # kernel errors, OOM kills
vmstat 1 5                   # r, free, si/so, us/sy/id/wa
mpstat -P ALL 1 3            # per-CPU balance
pidstat 1 3                  # per-process CPU
iostat -xz 1 3               # disk latency and utilisation
free -h                      # memory and swap
sar -n DEV 1 3               # network throughput
sar -n TCP,ETCP 1 3          # TCP connections and retransmits
top                          # overview
```
Load average counts runnable **and** uninterruptible (usually I/O waiting) tasks. Compare to `nproc`. A high load with low CPU usually means I/O wait.

---
## CPU
COMMAND | DESCRIPTION
---|---
`top -o %CPU` | Sort by CPU (press `1` for per-core, `H` for threads)
`ps -eo pid,ppid,cmd,%cpu --sort=-%cpu \| head` | Top CPU processes
`mpstat -P ALL 1` | Per-core usage. One core pegged means single-threaded work
`pidstat -u 1` | Per-process CPU, each second
`pidstat -t -p <PID> 1` | Threads of one process
`vmstat 1` | `us` user, `sy` system, `wa` I/O wait, `st` stolen by hypervisor
`cat /proc/pressure/cpu` | Pressure stall information
`sudo perf top` | Live hottest functions
`sudo perf record -g -p <PID> -- sleep 30 && sudo perf report` | Profile a process
`lscpu \| grep -i mhz; cpupower frequency-info` | Frequency scaling

High `st` on a VM means a noisy neighbour or an over-committed host. High `sy` often means many syscalls, context switches or network interrupts.

---
## Memory
COMMAND | DESCRIPTION
---|---
`free -h` | Look at `available`, not `free`. Cached memory is reclaimable
`ps aux --sort=-%mem \| head` | Top memory processes
`smem -tk -s pss` | Proportional memory per process (needs `smem`)
`vmstat 1` | `si` / `so` above zero for a while = swapping
`swapon --show` | Swap devices and use
`cat /proc/meminfo` | Everything: `MemAvailable`, `Slab`, `Dirty`
`cat /proc/pressure/memory` | Memory pressure (`some`, `full`)
`sudo slabtop -o \| head` | Kernel cache usage
`sudo dmesg -T \| grep -i -e 'out of memory' -e 'killed process'` | OOM killer events
`journalctl -k \| grep -i oom` | Same from the journal
`cat /proc/<PID>/status \| grep -e VmRSS -e VmSwap` | One process's memory
`cat /proc/sys/vm/swappiness` | Swap tendency (default 60, lower on database hosts)

OOM in containers: the container's cgroup limit is hit, see [Docker Troubleshooting](../docker/docker-troubleshooting.md).

Drop caches only for testing, never as a fix: `echo 3 | sudo tee /proc/sys/vm/drop_caches`.

---
## Disk I/O
More detail in [Storage and Filesystems](storage-and-filesystems.md).

COMMAND | DESCRIPTION
---|---
`iostat -xz 1` | `r_await`/`w_await` (ms), `aqu-sz`, `%util`
`sudo iotop -oPa` | Which process is writing or reading
`pidstat -d 1` | Per-process kB read and written
`vmstat 1` | `bi`/`bo` blocks in and out, `wa`
`cat /proc/pressure/io` | I/O pressure
`df -h; df -i` | Space and inodes
`sudo lsof +L1` | Deleted files still using space
`sudo lsof -p <PID>` | Files a process holds
`sudo iostat -x 1 -p sda` | One disk with partitions
`findmnt -o TARGET,SOURCE,FSTYPE,OPTIONS` | Mount options (`noatime`, `discard`)
`sudo smartctl -H /dev/sda` | Disk health

---
## Network
COMMAND | DESCRIPTION
---|---
`ss -s` | Socket summary
`ss -tulpn` | Listening sockets and owners
`ss -tn state established '( dport = :443 )' \| wc -l` | Established connections to a port
`ss -ti dst <IP>` | TCP internals to one host (rtt, retransmits, cwnd)
`ip -s link show <IF>` | Packets, errors, drops, per interface
`sar -n DEV 1` | Throughput per interface
`sar -n TCP,ETCP 1` | TCP active/passive opens, retransmits
`nstat -az \| grep -i -e retrans -e drop` | Kernel counters
`sudo ethtool <IF>` / `sudo ethtool -S <IF>` | Link speed, duplex, NIC counters
`sudo iftop -i <IF>` | Live bandwidth per connection
`sudo nethogs <IF>` | Bandwidth per process
`sudo tcpdump -ni <IF> host <IP> and port <PORT>` | Capture
`mtr -rwc 50 <HOST>` | Path loss and latency
`ping -c 20 <HOST>` | Loss and jitter
`iperf3 -s` / `iperf3 -c <HOST>` | Throughput test between two hosts
`dig +stats <NAME>` | DNS response time
`cat /proc/sys/net/netfilter/nf_conntrack_count /proc/sys/net/netfilter/nf_conntrack_max` | Conntrack table fill (full table drops packets)

Many `TIME_WAIT` sockets are normal. Many `CLOSE_WAIT` sockets mean the application is not closing connections. See also [IPTables](iptables.md) and [nftables](nftables.md) for firewall counters.

---
## Processes and Tracing
COMMAND | DESCRIPTION
---|---
`sudo strace -f -tt -p <PID>` | Syscalls of a running process
`sudo strace -c -p <PID>` | Syscall summary (stop with Ctrl-C)
`sudo strace -e trace=network,file -f <CMD>` | Filtered trace
`sudo ltrace -p <PID>` | Library calls
`sudo lsof -p <PID>` | Open files and sockets
`ls /proc/<PID>/fd \| wc -l` | Open file descriptors
`cat /proc/<PID>/limits` | Resource limits
`sudo pstack <PID>` / `gdb -p <PID> -batch -ex "thread apply all bt"` | Thread stacks
`ps -eo stat,pid,cmd \| awk '$1 ~ /^D/'` | Processes stuck in uninterruptible sleep (usually I/O)
`ps -eo stat,ppid,pid,cmd \| awk '$1 ~ /^Z/'` | Zombies
`systemd-cgtop` | Per-service CPU, memory, I/O ([systemd](systemd.md))
`journalctl -p warning -b` | Warnings and errors since boot

---
## Quick Diagnosis
SYMPTOM | LOOK AT
---|---
High load, low CPU | I/O wait: `iostat -xz 1`, `D` state processes, NFS hangs ([NFS](nfs.md))
High `sy` CPU | Interrupts, syscalls: `perf top`, `pidstat -w 1` for context switches
Free memory low | Normal if `available` is fine. Swapping or OOM kills are the real signs
Swap growing | `smem`, `vmstat 1`, a leaking process, `swappiness`
Slow disk | `await` high: failing disk (SMART), RAID rebuild ([RAID with mdadm](raid-mdadm.md)), a noisy process
Random timeouts | Packet loss and retransmits (`nstat`, `ip -s link`), conntrack full, DNS slow
"No space left on device" | `df -h` and `df -i`, deleted-but-open files
Service slow after boot only | `systemd-analyze blame`, `critical-chain` ([systemd](systemd.md))

## Monitoring Tools
TOOL | USE
---|---
`htop`, `btop` | Interactive process view
`glances` | One-screen overview
`atop` | Records history, replay after an incident (`atop -r`)
`sar` (sysstat) | Historical CPU, memory, disk, network. Enable `sysstat.service`
`netdata`, `Prometheus node_exporter` | Dashboards and alerts
