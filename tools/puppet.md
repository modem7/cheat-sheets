# Puppet Cheat-Sheet
Puppet is a declarative configuration management tool: you describe the desired state of a machine in manifests and an agent makes the machine match. Use `puppet apply` for a single host or testing, and an agent talking to a Puppet server for a fleet.

Documentation: [Puppet docs](https://www.puppet.com/docs/puppet/latest/puppet_index.html) · `man puppet-apply`
Project: [Puppet](https://www.puppet.com/)

> **Verification:** options checked against the Puppet 8 man pages (Ubuntu 24.04 package, December 2023 pages). The manifest, EPP template and the `apply`, `resource`, `facts`, `config`, `lookup`, `parser` and `epp` commands were run in a throwaway container with `puppet apply`; no Puppet server, agent-to-server run, Hiera hierarchy or Forge module was tested.

Related sheets: [Ansible](ansible.md), [Ansible-Playbook](ansible-playbook.md), [Terraform](terraform.md), [Salt](salt.md), [Vagrant](vagrant.md).

## Run Puppet
COMMAND | DESCRIPTION
---|---
`puppet apply <MANIFEST>.pp` | Apply a manifest to this machine
`puppet apply --noop <MANIFEST>.pp` | Dry run: show what would change
`puppet apply -e 'notify { "hi": }'` | Apply a one-line manifest
`puppet apply --modulepath <DIR> <MANIFEST>.pp` | Use modules from a directory
`puppet apply --detailed-exitcodes <MANIFEST>.pp` | Exit codes: `0` no changes, `1` failed, `2` changes applied, `4` some resources failed, `6` changes and failures
`puppet apply --test <MANIFEST>.pp` | Verbose, detailed exit codes and diffs
`puppet apply --debug --trace <MANIFEST>.pp` | Debug output and stack traces
`puppet agent -t` | One verbose agent run against the server (`--test`)
`puppet agent -t --noop` | Dry run against the server
`puppet agent --onetime --no-daemonize` | One run, no background daemon
`puppet agent --disable "<REASON>"` / `puppet agent --enable` | Pause or resume agent runs on this node
`puppet agent --fingerprint` | Show the certificate fingerprint
`puppet agent --certname <NAME> --waitforcert 60` | Set the identity and wait for the cert to be signed
`puppet parser validate <FILE>.pp` | Check manifest syntax
`puppet epp validate <FILE>.epp` | Check an EPP template's syntax
`puppet --version` | Show the version

`--detailed-exitcodes` uses `2` for "changes applied", so a clean second run returning `0` is the idempotence check.

## Inspect and Change Resources
COMMAND | DESCRIPTION
---|---
`puppet resource <TYPE>` | List every resource of a type (for example `service`, `package`, `user`)
`puppet resource <TYPE> <NAME>` | Show one resource as Puppet code
`puppet resource <TYPE> <NAME> <ATTR>=<VALUE>` | Change a resource right now
`puppet resource --types` | List the available resource types
`puppet describe <TYPE>` | Documentation for a type (`--list` shows all types, `--short` a brief form)
`puppet facts` | Print this node's facts as JSON
`puppet config print <SETTING>` | Show a setting (`all` for everything)
`puppet config set <SETTING> <VALUE> --section main` | Write a setting to `puppet.conf`
`puppet lookup <KEY>` | Look a value up through Hiera
`puppet lookup <KEY> --explain` | Show how it was resolved
`puppet lookup <KEY> --node <NAME> --facts <FILE>` | Look up for another node, with overridden facts
`puppet lookup <KEY> --merge deep` | Merge strategies: `first`, `unique`, `hash`, `deep`
`puppet lookup <KEY> --default <VALUE>` | Fall back if nothing is found
`puppet filebucket` | Back up and restore file contents Puppet has changed

## Manifest Basics
Resources have a type, a title and attributes. `ensure`, `require`, `notify` and `subscribe` order and trigger them.

```puppet
class motd_demo (
  String  $message = 'Managed by Puppet',
  Boolean $enable  = true,
) {
  file { '/tmp/motd-demo':
    ensure  => file,
    mode    => '0644',
    content => epp('motd_demo/motd.epp', { 'message' => $message }),
  }

  exec { 'say-hello':
    command     => '/bin/echo changed',
    refreshonly => true,
    subscribe   => File['/tmp/motd-demo'],
  }
}

node default {
  class { 'motd_demo':
    message => "Hello from ${facts['networking']['hostname']}",
  }
}
```

The EPP template `modules/motd_demo/templates/motd.epp`:

```text
<%- | String $message | -%>
<%= $message %>
```

Run it with `puppet apply --modulepath modules site.pp`. A second run changes nothing and exits `0` with `--detailed-exitcodes`.

Common resource types:

TYPE | MANAGES
---|---
`package` | Software (`ensure => installed`, `latest`, `absent`)
`file` | Files, directories, links (`ensure`, `source`, `content`, `owner`, `group`, `mode`)
`service` | Services (`ensure => running`, `enable => true`)
`user` / `group` | Accounts
`exec` | Commands; add `creates`, `onlyif`, `unless` or `refreshonly` so they stay idempotent
`cron` | Cron jobs
`notify` | Messages in the run log

## Modules and Data
COMMAND | DESCRIPTION
---|---
`puppet module install <AUTHOR>-<MODULE>` | Install a module from the Forge (`--version`, `--target-dir`)
`puppet module list` | List installed modules (`--tree` for dependencies)
`puppet module upgrade <AUTHOR>-<MODULE>` | Upgrade
`puppet module uninstall <AUTHOR>-<MODULE>` | Remove
`puppet module changes <PATH>` | Show files changed since installation
`puppet generate types` | Generate resource type metadata for environments
`puppet catalog compile <CERTNAME>` | Compile a catalog (needs a server or the right terminus)

A module is a directory with `manifests/`, `templates/`, `files/`, `lib/` and `data/`; `manifests/init.pp` defines the class named after the module.

## Server and Certificates
COMMAND | DESCRIPTION
---|---
`puppetserver ca list` | Pending certificate requests (run on the server)
`puppetserver ca sign --certname <NAME>` | Sign a request
`puppetserver ca clean --certname <NAME>` | Revoke and remove a node's certificate
`puppet ssl bootstrap` | Bootstrap an agent's certificates (`puppet ssl --help` for other actions)
`puppet node clean <NAME>` | Remove a node's data from the server

The `puppetserver ca` commands were not checked against a server here.

## Troubleshooting
SYMPTOM | FIX
---|---
Agent run says the certificate is not signed | Sign it on the server, or check `--certname` and the server name
Run changes the same thing every time | The resource is not idempotent: add `creates` or `unless` to `exec`, or manage the attribute properly
`Could not find class` | Check `--modulepath` and that `manifests/init.pp` defines a class with the module's name
Dependency cycle error | Look for `require`/`before`/`notify`/`subscribe` that loop back on each other
Need to see what would change | `puppet agent -t --noop` or `puppet apply --noop`

## See Also
- [Ansible](ansible.md)
- [Terraform](terraform.md)
- [Vagrant](vagrant.md)
- [Salt](salt.md)
