# Ansible Cheat-Sheet
Ansible is agentless automation over SSH ([OpenSSH Cheat-Sheet](openssh.md)). Playbooks have their own sheet: [Ansible-Playbook Cheat-Sheet](ansible-playbook.md).

Documentation: [Ansible Docs](https://docs.ansible.com/)

## Install Ansible on Ubuntu
Recommended: isolated with pipx (or [uv](https://docs.astral.sh/uv/) `uv tool install ansible`).
```bash
sudo apt install -y pipx
pipx ensurepath
pipx install --include-deps ansible
```
Alternative from the official PPA:
```bash
sudo apt install -y software-properties-common
sudo add-apt-repository --yes --update ppa:ansible/ansible
sudo apt install -y ansible
```
Verify:
```bash
ansible --version
```

## Inventory
`inventory.ini`
```ini
[web]
web1.example.com
web2.example.com ansible_user=deploy

[db]
db1.example.com ansible_port=2222

[prod:children]
web
db

[all:vars]
ansible_python_interpreter=/usr/bin/python3
```
`inventory.yml`
```yaml
all:
  children:
    web:
      hosts:
        web1.example.com:
        web2.example.com:
          ansible_user: deploy
```

## Ad-Hoc Commands
COMMAND | DESCRIPTION
---|---
`ansible all -i inventory.ini -m ping` | Test connectivity
`ansible web -i inventory.ini -a "uptime"` | Run a command
`ansible web -i inventory.ini -b -m apt -a "name=nginx state=present update_cache=yes"` | Install a package with sudo
`ansible web -i inventory.ini -b -m service -a "name=nginx state=restarted"` | Restart a service
`ansible web -i inventory.ini -m copy -a "src=./f dest=/tmp/f mode=0644"` | Copy a file
`ansible web -i inventory.ini -m setup -a "filter=ansible_distribution*"` | Gather facts
`ansible all -i inventory.ini --list-hosts` | List matched hosts
`ansible web -i inventory.ini -m shell -a "df -h \| grep /$"` | Shell features (pipes)
`ansible all -i inventory.ini -m reboot -b` | Reboot and wait

Common flags:

FLAG | DESCRIPTION
---|---
`-i <FILE>` | Inventory
`-b` | Become root (sudo)
`-K` | Ask for the sudo password
`-k` | Ask for the SSH password
`-u <USER>` | Remote user
`--private-key <FILE>` | SSH key
`-l <PATTERN>` | Limit to hosts
`-f <N>` | Parallel forks (default 5)
`-v` to `-vvvv` | Verbosity

## ansible-vault
COMMAND | DESCRIPTION
---|---
`ansible-vault create secrets.yml` | Create an encrypted file
`ansible-vault edit secrets.yml` | Edit
`ansible-vault view secrets.yml` | View
`ansible-vault encrypt file` / `decrypt file` | Encrypt or decrypt in place
`ansible-vault encrypt_string 'secret' --name 'db_password'` | Encrypt a single value
`ansible-playbook site.yml --ask-vault-pass` | Run with a vault password prompt
`ansible-playbook site.yml --vault-password-file ~/.vault_pass` | Run with a password file

## ansible-galaxy
COMMAND | DESCRIPTION
---|---
`ansible-galaxy collection install community.general` | Install a collection
`ansible-galaxy role install geerlingguy.docker` | Install a role
`ansible-galaxy install -r requirements.yml` | Install from a requirements file
`ansible-galaxy role init <NAME>` | Scaffold a role

## Other Tools
COMMAND | DESCRIPTION
---|---
`ansible-inventory -i inventory.ini --graph` | Show the inventory tree
`ansible-doc <MODULE>` | Module documentation
`ansible-doc -l \| grep <TERM>` | Search modules
`ansible-config dump --only-changed` | Show non-default config
`ansible-lint <PLAYBOOK>` | Lint a playbook

## ansible.cfg
```ini
[defaults]
inventory = ./inventory.ini
host_key_checking = False
forks = 20
interpreter_python = auto_silent

[privilege_escalation]
become = True
```
> `host_key_checking = False` is convenient for labs. Leave it on for production.

## See Also
- [Ansible-Playbook Cheat-Sheet](ansible-playbook.md)
- [Puppet Cheat-Sheet](puppet.md)
- [Salt Cheat-Sheet](salt.md)
- [Terraform](terraform.md)
