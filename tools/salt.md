# Salt Cheat-Sheet
Salt (SaltStack) is a configuration management and remote execution tool. A master sends commands and states to minions, or `salt-call --local` and `salt-ssh` run without a master. Use it to keep machines in a declared state and to run one command across many hosts.

Documentation: [Salt docs](https://docs.saltproject.io/) · [Salt install guide](https://docs.saltproject.io/salt/install-guide/en/latest/)
Project: [Salt Project](https://saltproject.io/)

> **Verification:** options checked against the `--help` output of Salt 3008.5 (installed with `pip` in a throwaway Python 3.11 container; it needed a C compiler). `salt-call --local` was run for `test.ping`, `grains.*`, `pillar.items`, `state.apply` (with `test=True`), `state.single`, `state.sls`, `sys.*` and `--out=json`; the example states below were applied twice and the second run changed nothing. No master, minion connection, `salt-key` exchange or `salt-ssh` login was tested, so those rows are from `--help` only. Output details change between releases.

Related sheets: [Ansible](ansible.md), [Ansible-Playbook](ansible-playbook.md), [Puppet](puppet.md), [Terraform](terraform.md), [Vagrant](vagrant.md).

## Run Without a Master
`--local` makes `salt-call` read states from the local file roots and skip the master.

COMMAND | DESCRIPTION
---|---
`salt-call --local test.ping` | Check Salt works (prints `True`)
`salt-call --local state.apply <STATE>` | Apply a state file (`<STATE>.sls` under the file roots)
`salt-call --local state.apply <STATE> test=True` | Dry run
`salt-call --local state.highstate` | Apply everything `top.sls` assigns to this machine
`salt-call --local state.sls <STATE>` | Apply one state without `top.sls`
`salt-call --local state.single file.managed name=<PATH> contents=<TEXT>` | Run a single state function
`salt-call --local state.show_sls <STATE>` | Show the compiled state data
`salt-call --local state.show_top` | Show which states `top.sls` selects
`salt-call -c <DIR> --local ...` | Use a config directory containing `minion`
`salt-call --local <MODULE.FUNCTION> --out=json` | Machine-readable output (`--out` also takes `yaml`, `nested` and others)
`salt-call --local state.apply <STATE> --retcode-passthrough` | Non-zero exit if a state failed
`salt-call -l debug --local ...` | Debug logging (`-l`, `--log-level`)

Minimal minion config for local use, saved as `<DIR>/minion`:

```yaml
file_client: local
file_roots:
  base:
    - /srv/salt
pillar_roots:
  base:
    - /srv/pillar
```

## Remote Execution From the Master
Run on the master. The target comes first, then the function.

COMMAND | DESCRIPTION
---|---
`salt '*' test.ping` | Ping every accepted minion
`salt 'web*' cmd.run 'uptime'` | Run a shell command on matching minions (glob target)
`salt -L 'web1,web2' pkg.version nginx` | Target a list
`salt -G 'os:Debian' grains.get osrelease` | Target by grain
`salt -E 'web[0-9]+' test.ping` | Target by regular expression
`salt -C 'G@os:Debian and web*' test.ping` | Compound target
`salt -I 'role:db' test.ping` | Target by pillar value
`salt -N <NODEGROUP> test.ping` | Target a nodegroup from the master config
`salt '*' state.apply <STATE> test=True` | Dry-run a state everywhere
`salt '*' state.highstate` | Apply `top.sls` everywhere
`salt -b 10 '*' state.highstate` | Roll out in batches (`--batch`, `--batch-wait`)
`salt -t 60 '*' <FUNCTION>` | Wait up to 60 seconds for answers
`salt --summary '*' <FUNCTION>` | Show a result summary
`salt '*' <FUNCTION> --out=json` | JSON output
`salt '*' sys.doc <MODULE>` | Documentation for a module on the minions

Quote `*` so the shell does not expand it.

## Minion Keys
Minions send a public key to the master. Accept only the ones you recognise.

COMMAND | DESCRIPTION
---|---
`salt-key -L` | List accepted, pending and rejected keys (`--list-all`)
`salt-key -F <MINION_ID>` | Show a key's fingerprint (`-F`, `--finger`; check it matches the minion's own)
`salt-key -a <MINION_ID>` | Accept a key
`salt-key -A` | Accept all pending keys (only for trusted networks)
`salt-key -r <MINION_ID>` | Reject a key
`salt-key -d <MINION_ID>` | Delete a key
`salt-key -y ...` | Skip the confirmation prompt

## Introspection
COMMAND | DESCRIPTION
---|---
`salt-call --local grains.items` | All grains (facts) for this machine
`salt-call --local grains.get <GRAIN>` | One grain, such as `os` or `osrelease`
`salt-call --local grains.ls` | List grain names
`salt-call --local grains.setval <KEY> <VALUE>` | Set a custom grain (persisted in the minion's grains file)
`salt-call --local pillar.items` | All pillar data for this machine
`salt-call --local pillar.get <KEY> <DEFAULT>` | One pillar value
`salt-call --local sys.list_modules` / `sys.list_state_modules` | Available execution and state modules
`salt-call --local sys.doc <MODULE.FUNCTION>` | Documentation
`salt-call --local config.get <OPTION>` | Read a minion config option
`salt-call --local test.versions_report` | Salt and dependency versions
`salt-call --local cmd.run '<COMMAND>'` | Run a shell command
`salt-call --local pkg.version <PACKAGE>` | Installed package version

Salt 3008 printed pillar values as `**********` in `pillar.items` and `pillar.get` output in the test run. That is a display default; check the release notes for how to show them.

## States
A state file describes desired state. `top.sls` assigns state files to minions.

```yaml
# /srv/salt/top.sls
base:
  '*':
    - demo
```

```yaml
# /srv/salt/demo.sls
saltdemo_file:
  file.managed:
    - name: /tmp/saltdemo.txt
    - source: salt://motd.jinja
    - template: jinja
    - mode: '0644'

saltdemo_cmd:
  cmd.run:
    - name: echo changed
    - onchanges:
      - file: saltdemo_file
```

```jinja
{# /srv/salt/motd.jinja #}
Hello {{ grains['id'] }} ({{ pillar['app']['greeting'] }})
```

```yaml
# /srv/pillar/top.sls and /srv/pillar/app.sls
base:
  '*':
    - app
```

```yaml
app:
  greeting: hello-from-pillar
```

Common requisites: `require`, `watch`, `onchanges`, `onfail`, `unless`, `onlyif`, `creates` keep states ordered and idempotent.

STATE FUNCTION | MANAGES
---|---
`pkg.installed` | Packages (not run here)
`service.running` (`enable: true`) | Services (not run here)
`file.managed` | Files from `source` or `contents`, with templating
`file.directory` | Directories
`user.present` / `group.present` | Accounts
`cmd.run` | Commands; guard with `unless`, `creates` or `onchanges`

## Salt SSH
Agentless: runs over SSH using a roster file instead of a minion.

COMMAND | DESCRIPTION
---|---
`salt-ssh '*' test.ping` | Run a function on every roster host
`salt-ssh -i '*' test.ping` | Ignore host keys (`--ignore-host-keys`; weakens security)
`salt-ssh --roster-file <FILE> '*' state.apply <STATE>` | Use another roster file
`salt-ssh -r '*' '<COMMAND>'` | Run a raw shell command (`--raw`)
`salt-ssh --user <USER> --sudo '*' <FUNCTION>` | Set the login and use sudo

Roster file (`/etc/salt/roster`; format from the documentation, not tested):

```yaml
web1:
  host: 192.0.2.10
  user: deploy
  sudo: true
```

## Other Tools
COMMAND | DESCRIPTION
---|---
`salt-run manage.up` | Which minions are connected (unverified here: needs a master)
`salt-run jobs.list_jobs` | Recent jobs on the master (unverified here)
`salt-cp '*' <LOCAL_FILE> <REMOTE_PATH>` | Copy a file to minions
`salt-master` / `salt-minion` | Start the daemons (usually through systemd)

## Troubleshooting
SYMPTOM | FIX
---|---
Minion does not answer | Is its key accepted (`salt-key -L`)? Are the ports reachable? Run `salt-minion -l debug` on the minion
State changes every run | The state is not idempotent: add `unless`, `creates` or `onchanges`
`Rendering SLS failed` | Check YAML indentation and Jinja syntax; `state.show_sls` shows the compiled result
Pillar value not found | Check `pillar_roots`, the pillar `top.sls` target, and refresh with `saltutil.refresh_pillar`
`salt-call` does nothing useful without `--local` | It talks to a master unless `file_client: local` is set

## See Also
- [Ansible](ansible.md)
- [Puppet](puppet.md)
- [Terraform](terraform.md)
