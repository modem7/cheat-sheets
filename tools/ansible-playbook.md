# Ansible-Playbook Cheat-Sheet
Playbooks describe the desired state of your hosts in YAML. Setup and ad-hoc commands: [Ansible Cheat-Sheet](ansible.md).

## Run
COMMAND | DESCRIPTION
---|---
`ansible-playbook -i inventory.ini site.yml` | Run a playbook
`ansible-playbook site.yml --check --diff` | Dry run and show file diffs
`ansible-playbook site.yml --syntax-check` | Syntax check only
`ansible-playbook site.yml --list-tasks` | List tasks
`ansible-playbook site.yml --list-hosts` | List targeted hosts
`ansible-playbook site.yml -l web1` | Limit to a host or group
`ansible-playbook site.yml --tags nginx` | Only tagged tasks
`ansible-playbook site.yml --skip-tags slow` | Skip tagged tasks
`ansible-playbook site.yml --start-at-task "Install nginx"` | Resume from a task
`ansible-playbook site.yml --step` | Confirm each task
`ansible-playbook site.yml -e "version=1.2.3"` | Extra variable
`ansible-playbook site.yml -e @vars.yml` | Variables from a file
`ansible-playbook site.yml -K` | Ask for the sudo password

## Example Playbook
```yaml
---
- name: Configure web servers
  hosts: web
  become: true
  vars:
    packages: [nginx, curl]

  tasks:
    - name: Install packages
      ansible.builtin.apt:
        name: "{{ packages }}"
        state: present
        update_cache: true
        cache_valid_time: 3600

    - name: Deploy nginx config
      ansible.builtin.template:
        src: nginx.conf.j2
        dest: /etc/nginx/nginx.conf
        owner: root
        group: root
        mode: "0644"
        validate: nginx -t -c %s
      notify: Reload nginx

    - name: Ensure nginx is running
      ansible.builtin.service:
        name: nginx
        state: started
        enabled: true

  handlers:
    - name: Reload nginx
      ansible.builtin.service:
        name: nginx
        state: reloaded
```

## Common Modules
MODULE | PURPOSE
---|---
`ansible.builtin.apt` / `dnf` / `package` | Packages
`ansible.builtin.copy` / `template` | Files and Jinja2 templates
`ansible.builtin.file` | Directories, links, permissions
`ansible.builtin.lineinfile` / `blockinfile` | Edit lines in files
`ansible.builtin.service` / `systemd` | Services
`ansible.builtin.user` / `group` | Accounts
`ansible.builtin.command` / `shell` | Commands (prefer real modules)
`ansible.builtin.get_url` / `unarchive` | Download and extract
`ansible.builtin.git` | Clone repositories
`ansible.builtin.cron` | Cron jobs
`ansible.builtin.reboot` | Reboot and wait
`community.docker.docker_container` | Containers
`ansible.posix.authorized_key` | SSH keys
`ansible.builtin.debug` | Print variables

## Control Flow
```yaml
- name: Only on Debian family
  ansible.builtin.apt:
    name: htop
  when: ansible_os_family == "Debian"

- name: Create users
  ansible.builtin.user:
    name: "{{ item }}"
  loop: [alice, bob]

- name: Run a command and keep the result
  ansible.builtin.command: cat /etc/hostname
  register: hostname_out
  changed_when: false

- name: Show it
  ansible.builtin.debug:
    msg: "{{ hostname_out.stdout }}"

- name: Retry until ready
  ansible.builtin.uri:
    url: http://localhost:8080/health
  register: r
  until: r.status == 200
  retries: 10
  delay: 3
```

## Roles
```
roles/
  nginx/
    tasks/main.yml
    handlers/main.yml
    templates/
    defaults/main.yml   # lowest-precedence variables
    vars/main.yml
```
```yaml
- hosts: web
  roles:
    - nginx
    - role: app
      vars:
        port: 8080
```

## Tips
- Use fully qualified module names (`ansible.builtin.copy`).
- Make tasks idempotent. Use `changed_when` and `creates:` on `command`.
- Test with `--check --diff` first, and lint with `ansible-lint`.
- Keep secrets in `ansible-vault`, never in plain vars.
- `serial: 1` in a play does rolling updates, `max_fail_percentage` limits blast radius.
