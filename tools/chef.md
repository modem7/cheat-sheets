# Chef
Chef is a configuration management tool: you describe the desired state of a machine in Ruby based recipes, group them in cookbooks, and `chef-client` converges the node towards that state. Chef Workstation bundles the tools you use on your own machine (`chef`, `knife`, `kitchen`, `cookstyle`, `inspec`). Nothing here was run: the commands, resources and file layouts come from the Chef documentation and are unverified, so confirm with `--help` or `knife --help` on your installed version before relying on a flag. Compare with [Ansible](ansible.md), [Puppet](puppet.md) and [Salt](salt.md).

Documentation: [Chef docs](https://docs.chef.io/)
Project: [chef/chef](https://github.com/chef/chef)

---
## Cookbook Layout
PATH | PURPOSE
---|---
`metadata.rb` | Name, version, dependencies (`depends 'other'`), supported platforms
`recipes/default.rb` | The default recipe (a list of resources)
`attributes/default.rb` | Default attribute values
`templates/` | ERB templates for the `template` resource
`files/` | Static files for `cookbook_file`
`resources/` | Custom resources
`libraries/` | Ruby helpers
`kitchen.yml` | Test Kitchen configuration
`test/` | InSpec profiles and other tests

## chef CLI (Workstation)
COMMAND | DESCRIPTION
---|---
`chef generate cookbook NAME` | Create a cookbook skeleton
`chef generate recipe NAME RECIPE` | Add a recipe (run inside the cookbook directory or give a path)
`chef generate attribute` / `template` / `file` / `resource` | Add other cookbook parts (each takes a name)
`chef generate repo NAME` | Create a Chef repository
`chef exec COMMAND` | Run a command using Workstation's Ruby and gems
`chef shell-init bash` | Print the shell setup that puts Workstation's tools first on the path
`chef gem install NAME` | Install a gem into Workstation's Ruby
`chef env` | Show the Workstation environment
`chef install` / `chef update` | Resolve and update a Policyfile lock
`chef push POLICY_GROUP` | Push a policy to a policy group on the server
`chef --version` | Show the version

## knife
`knife` talks to a Chef Infra Server using `config.rb` (usually in `.chef/` or `~/.chef/`) and your API key.

COMMAND | DESCRIPTION
---|---
`knife ssl check` | Check the server certificate is trusted
`knife ssl fetch` | Download the server certificate into the trusted certificate store
`knife node list` / `node show NAME` | List nodes, show one
`knife node edit NAME` | Edit a node's JSON in your editor
`knife node delete NAME` | Delete a node object (destructive)
`knife node run_list add NAME 'recipe[COOKBOOK]'` | Add to a node's run list
`knife node run_list remove NAME 'recipe[COOKBOOK]'` | Remove from a run list
`knife node run_list set NAME 'role[web],recipe[ntp]'` | Replace the run list
`knife role list` / `role show NAME` / `role from file FILE.json` | Roles
`knife environment list` / `environment from file FILE.json` | Environments
`knife data bag create NAME` | Create a data bag
`knife data bag from file NAME ITEM.json` | Upload an item (`--secret-file FILE` encrypts it)
`knife data bag show NAME ITEM` | Show an item
`knife cookbook upload NAME` | Upload a cookbook from the cookbook path (`-a` uploads all)
`knife cookbook list` / `cookbook show NAME` | List or show cookbooks on the server
`knife cookbook delete NAME VERSION` | Delete a cookbook version from the server (destructive)
`knife search node 'platform:ubuntu'` | Search node data (also `knife search role ...`; add `-a ATTRIBUTE` to print one attribute)
`knife status` | When each node last checked in
`knife client list` | API clients (`client delete NAME` is destructive)
`knife ssh 'role:web' 'sudo chef-client'` | Run a command on nodes found by search
`knife bootstrap HOST -N NODE_NAME -x USER --sudo -r 'recipe[COOKBOOK]'` | Install the client on a machine and run it (`-x` SSH user, `-i KEY`, `-E ENVIRONMENT`, `--policy-name`, `--policy-group`)
`knife exec SCRIPT.rb` | Run a Ruby script against the server API
`knife config list` | Show the configuration knife is using

## chef-client
COMMAND | DESCRIPTION
---|---
`chef-client` | Converge this node against the server
`chef-client -z` | Local mode: run with an in-memory Chef server using local files
`chef-client -z -o 'recipe[COOKBOOK]'` | Local mode with an override run list
`chef-client -o 'recipe[COOKBOOK]'` | Override the run list for one run
`chef-client -j attributes.json` | Supply JSON attributes (can set a `run_list`)
`chef-client -W` | Why-run: report what would change without changing it
`chef-client -l debug` | Log level
`chef-client -L FILE` | Log to a file
`chef-client -i 1800 -s 300` | Run as a loop every interval seconds, with splay
`chef-client -E ENVIRONMENT` | Set the environment
`chef-client -c FILE` | Use a specific `client.rb`
`chef-client --chef-license accept` | Accept the licence non-interactively
`chef-apply FILE.rb` | Run a single recipe file without a cookbook

`chef-solo` is deprecated in favour of local mode (`chef-client -z`): treat it as legacy.

## Recipe Resources
```ruby
package 'nginx' do
  action :install
end

template '/etc/nginx/nginx.conf' do
  source 'nginx.conf.erb'
  owner 'root'
  group 'root'
  mode '0644'
  variables(workers: node['nginx']['workers'])
  notifies :reload, 'service[nginx]', :delayed
end

service 'nginx' do
  action [:enable, :start]
end

directory '/var/www/app' do
  owner 'www-data'
  recursive true
end

execute 'build-index' do
  command '/usr/local/bin/build-index'
  creates '/var/lib/app/index.db'
end
```

RESOURCE | PURPOSE
---|---
`package` | Install, upgrade or remove a package
`service` | `:enable`, `:disable`, `:start`, `:stop`, `:restart`, `:reload`
`template` / `cookbook_file` / `file` | Write config from ERB, from a cookbook file, or inline content
`directory` / `link` | Directories and symlinks
`execute` / `script` | Run commands; make them idempotent with `creates`, `only_if` or `not_if`
`user` / `group` | Accounts
`cron` / `systemd_unit` | Scheduled jobs and unit files
`remote_file` / `git` | Download a file, check out a repository
`apt_package` / `dnf_package` | Platform specific packages

Common meta properties: `action`, `only_if`, `not_if`, `notifies :action, 'resource[name]', :immediately|:delayed`, `subscribes`. A resource runs in the order written; notifications are queued and, with `:delayed`, run once at the end of the run.

## Attributes
```ruby
# attributes/default.rb
default['nginx']['workers'] = 2
```

`node['nginx']['workers']` reads the merged value. Precedence, lowest to highest: `default`, `force_default`, `normal`, `override`, `force_override`, `automatic`. Role, environment and policy levels are also layered into `default` and `override` (see the docs for the full table). Prefer `default` in cookbooks and override in roles or environments.

## Data Bags
COMMAND | DESCRIPTION
---|---
`knife data bag create users` | Create a bag
`knife data bag from file users alice.json` | Add an item
`knife data bag from file secrets db.json --secret-file FILE` | Add an encrypted item
`data_bag_item('users', 'alice')` | Read an item in a recipe
`search(:users, 'groups:sudo')` | Search a bag in a recipe

## Test Kitchen
Test Kitchen builds a throwaway instance, converges your cookbook on it and runs tests.

COMMAND | DESCRIPTION
---|---
`kitchen list` | Instances and their state
`kitchen create` / `converge` / `verify` | Make the instance, apply the cookbook, run the tests
`kitchen test` | Full cycle: create, converge, verify, destroy
`kitchen login INSTANCE` | Shell into an instance
`kitchen destroy` | Remove instances
`kitchen diagnose` | Show the resolved configuration
`kitchen converge -c 2` | Run instances concurrently

```yaml
# kitchen.yml
driver:
  name: dokken

provisioner:
  name: dokken

verifier:
  name: inspec

platforms:
  - name: ubuntu-24.04
    driver:
      image: dokken/ubuntu-24.04

suites:
  - name: default
    run_list:
      - recipe[COOKBOOK::default]
    verifier:
      inspec_tests:
        - test/integration/default
```

The `dokken` driver (container based) needs the `kitchen-dokken` gem and Docker. Other drivers include `vagrant` (see [Vagrant](vagrant.md)).

COMMAND | DESCRIPTION
---|---
`cookstyle .` | Lint cookbook Ruby (`-a` auto-corrects safe offences)
`inspec init profile NAME` | Create a test profile
`inspec exec PROFILE` | Run a profile locally (`-t ssh://USER@HOST` for a remote host)
`inspec check PROFILE` | Check a profile is valid

## Troubleshooting
SYMPTOM | FIX
---|---
`SSL certificate verify failed` from knife | `knife ssl fetch` then `knife ssl check`
Resource runs every time | Not idempotent: add `creates`, `only_if` or `not_if` to `execute`
Template change does not restart the service | Add `notifies :restart, 'service[NAME]'` to the template
Attribute has the wrong value | Check precedence levels; `knife node show NAME -l` or `node.debug_value('KEY')` shows where it came from
Cookbook dependency missing | Add `depends` in `metadata.rb` and upload the dependency
Run is slow or unclear | `chef-client -l debug`, and `-W` to see what would change
Want to test without a server | `chef-client -z -o 'recipe[NAME]'` or `kitchen test`

## See Also
- [Ansible](ansible.md)
- [Puppet](puppet.md)
- [Salt](salt.md)
- [Vagrant](vagrant.md)
- [Terraform](terraform.md)
