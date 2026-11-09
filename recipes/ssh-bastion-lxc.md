# SSH Bastion Host in an LXC
Run one small, hardened host as the only SSH entry point to your lab, so servers do not each face your network or VPN. This recipe builds it in a minimal Proxmox LXC, restricts what it can do, and connects to targets through it with `ProxyJump`.

Documentation: [ssh_config](https://man.openbsd.org/ssh_config) · [sshd_config](https://man.openbsd.org/sshd_config) · [Proxmox pct](https://pve.proxmox.com/pve-docs/pct.1.html)

> **Verification:** the OpenSSH options below were checked against the OpenBSD manual pages. The `pct create` line was composed from the option list, with no worked example, and the firewall and logging advice is general practice. Nothing here was run end to end *(unverified)*.

## Goal
You reach every internal host with `ssh <TARGET>`, through one bastion. The bastion allows only key logins (with optional second factor), forwards only to approved hosts, keeps no agent keys and logs every session.

## Prerequisites
- A Proxmox host with a container template downloaded, see [Proxmox VE Overview and Install](../proxmox/proxmox-overview.md).
- A way to reach the bastion from outside, such as [WireGuard](wireguard-remote-access.md), so SSH is not exposed to the internet directly.
- Console access to the container in case you lock yourself out.

## Steps
1. **Create a minimal unprivileged container.**

   ```bash
   pct create <VMID> <STORAGE>:vztmpl/<TEMPLATE> --hostname bastion --unprivileged 1 \
     --net0 name=eth0,bridge=vmbr0,ip=dhcp,firewall=1
   ```

   `--unprivileged` defaults to 1 on create. Do not enable nesting (`--features nesting=1`), and give it little CPU and memory. Put it on its own management VLAN if you have one ([VLANs](../homelab/vlans.md)).

2. **Harden sshd.** Follow [SSH Hardening](../security/ssh-hardening.md), then add to `/etc/ssh/sshd_config`:

   ```text
   PasswordAuthentication no
   AllowAgentForwarding no
   AllowTcpForwarding yes
   PermitOpen 192.0.2.10:22 192.0.2.11:22
   PermitTTY no
   ClientAliveInterval 60
   LogLevel VERBOSE
   ```

   - `PermitOpen` limits forwarding to the listed `host:port` pairs, so the bastion cannot be used to reach anything else. Use `any` or `none` for the extremes.
   - `PermitTTY no` blocks an interactive shell on the bastion itself. Jump connections still work, because they only forward a TCP connection.
   - `LogLevel VERBOSE` (default `INFO`) records key fingerprints and forwarding.
   - Disabling agent forwarding adds little on its own if people can run a shell, so combine it with `PermitTTY no` or `ForceCommand`.

3. **Restrict each key.** In `~/.ssh/authorized_keys` on the bastion:

   ```text
   restrict,port-forwarding,permitopen="192.0.2.10:22" ssh-ed25519 AAAA... user@laptop
   ```

   `restrict` turns off port, agent and X11 forwarding and the PTY, and `port-forwarding` turns forwarding back on for that key. `permitopen` limits it to a target. Options such as `command="..."` and `no-agent-forwarding` also exist.

4. **Optional: require a second factor.** `AuthenticationMethods publickey,keyboard-interactive` demands both, and each method must also be enabled on its own. The keyboard-interactive side needs a PAM module for your second factor, which is not covered here.

5. **Optional: use SSH certificates.** Short-lived certificates replace key distribution:

   ```bash
   ssh-keygen -s <CA_KEY> -I <KEY_ID> -n <USER> -V +52w1d <USER_KEY>.pub
   ```

   Set `TrustedUserCAKeys /etc/ssh/ca.pub` on the bastion. A certificate with no principals is rejected. The `-V` value above is the documented format, so a short validity such as `+1h` follows the same pattern but was not shown verbatim.

6. **Connect through it.** On your client in `~/.ssh/config`:

   ```text
   Host bastion
       HostName bastion.example.com
       User <USER>

   Host 192.0.2.10 192.0.2.11
       ProxyJump bastion
   ```

   `ssh -J bastion <USER>@192.0.2.10` does the same on one line. Jump hosts do not inherit the destination's settings, so keep options in `~/.ssh/config`. `ProxyCommand` is the older form, and `ssh -W host:port` forwards standard input and output.

7. **Close the internal hosts.** On each target, allow SSH only from the bastion's address using [UFW](../linux/ufw.md) or the VLAN firewall rules.

8. **Add brute-force protection.** Install [fail2ban](../security/fail2ban.md) or [CrowdSec](../security/crowdsec.md) on the bastion.

9. **Keep records.** Ship the bastion's auth log to your logging stack ([Graylog](../apps/graylog.md), [Elastic Stack](../apps/elastic-stack.md) or [Loki and Alloy](../apps/loki-alloy.md)). A bastion that nobody reads logs from is only a delay.

## Verify
- `ssh -J bastion <TARGET>` works, and `ssh <TARGET>` directly from your client does not.
- An attempt to forward to a host that is not in `PermitOpen` is refused.
- A password login to the bastion is refused.
- The login appears in the bastion's log with the key fingerprint.

## Roll Back
Keep the Proxmox console open while you edit `sshd_config`, run `sshd -t` before `systemctl reload ssh`, and take a container snapshot first. Remove `ProxyJump` from your client config to go back to direct access.

## Alternatives
Tailscale SSH, Teleport and HashiCorp Boundary exist for the same job. They were not researched here.

## Not Verified
The `pct create` line, the firewall and logging advice, and the PAM setup for a second factor.

## See Also
- [SSH Hardening](../security/ssh-hardening.md)
- [Fail2ban](../security/fail2ban.md)
- [WireGuard Remote Access](wireguard-remote-access.md)
- [New Server Checklist](new-server-checklist.md)
