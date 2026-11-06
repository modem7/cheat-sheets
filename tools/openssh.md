# OpenSSH Cheat-Sheet
OpenSSH provides encrypted remote login, file transfer and tunnelling.

## Connect and Keys
COMMAND | DESCRIPTION
---|---
`ssh <USER>@<HOST>` | Connect
`ssh -p <PORT> <USER>@<HOST>` | Non-standard port
`ssh -i ~/.ssh/<KEY> <USER>@<HOST>` | Use a specific key
`ssh <USER>@<HOST> '<CMD>'` | Run a command and return
`ssh-keygen -t ed25519 -C "<COMMENT>"` | Generate an Ed25519 key
`ssh-copy-id <USER>@<HOST>` | Install your public key on a server
`ssh-copy-id -i ~/.ssh/<KEY>.pub <USER>@<HOST>` | Install a specific key
`ssh-keygen -y -f ~/.ssh/<KEY>` | Derive the public key from a private key
`ssh-keygen -lf ~/.ssh/<KEY>.pub` | Show the fingerprint
`ssh-keygen -p -f ~/.ssh/<KEY>` | Change a key's passphrase
`eval "$(ssh-agent -s)" && ssh-add ~/.ssh/<KEY>` | Start the agent and load a key
`ssh-add -l` | List loaded keys

## Known Hosts

Remove Entry from the Known-Hosts File.
```bash
ssh-keygen -R hostname
```
`ssh-keyscan -t ed25519 <HOST> >> ~/.ssh/known_hosts` adds a host key without prompting.

## Using the SSH Config File
If you are regularly connecting to multiple remote systems over SSH, you can configure your remote servers with the `.ssh/config` file.

**Example:**
```ini
Host dev
    HostName dev.your-domain
    User xcad
    Port 7654
    IdentityFile ~/.ssh/targaryen.key

Host jump
    HostName bastion.example.com
    User admin

Host internal-*
    ProxyJump jump
    User admin

Host *
    ServerAliveInterval 60
    ServerAliveCountMax 3
    Compression yes
    AddKeysToAgent yes
```

Connect to a host (like *dev* , eg.) with `ssh dev`.

Keep `~/.ssh` at `700`, private keys and `config` at `600`.

## Tunnels and Jump Hosts
COMMAND | DESCRIPTION
---|---
`ssh -L 8080:localhost:80 <USER>@<HOST>` | Local forward: `localhost:8080` reaches port 80 on the remote side
`ssh -L 5432:db.internal:5432 <USER>@<BASTION>` | Reach a host behind the server
`ssh -R 9000:localhost:3000 <USER>@<HOST>` | Remote forward: expose your local port 3000 on the server
`ssh -D 1080 <USER>@<HOST>` | SOCKS proxy
`ssh -J <USER>@<BASTION> <USER>@<TARGET>` | Jump through a bastion
`ssh -N -f -L 8080:localhost:80 <USER>@<HOST>` | Background tunnel, no shell
`ssh -A <USER>@<HOST>` | Forward the agent (only to hosts you trust)

## File Transfer
COMMAND | DESCRIPTION
---|---
`scp <FILE> <USER>@<HOST>:<PATH>` | Copy to a remote host
`scp -r <USER>@<HOST>:<DIR> .` | Copy a directory from a remote host
`rsync -avzP -e ssh <SRC>/ <USER>@<HOST>:<DEST>/` | Efficient sync with resume
`sftp <USER>@<HOST>` | Interactive file transfer
`sshfs <USER>@<HOST>:<PATH> <MOUNTPOINT>` | Mount a remote directory

## Server Hardening (`/etc/ssh/sshd_config`)
```
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
AllowUsers <USER>
MaxAuthTries 3
X11Forwarding no
```
Check and reload: `sudo sshd -t && sudo systemctl reload ssh` (the unit is `sshd` on RHEL). Keep a second session open while testing.

## Troubleshooting
- `ssh -v <HOST>` (up to `-vvv`) shows the key and auth negotiation.
- `Permission denied (publickey)`: check key permissions and `~/.ssh/authorized_keys` ownership on the server.
- `WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED`: confirm the change is legitimate, then `ssh-keygen -R <HOST>`.
- Server side logs: `sudo journalctl -u ssh -f`.
