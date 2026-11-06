# Vagrant Cheat-Sheet
Vagrant builds and manages reproducible development VMs from a `Vagrantfile`.

## General Management
COMMAND | DESCRIPTION
---|---
`vagrant status` | Outputs status of the vagrant machine
`vagrant global-status` | Outputs status of all vagrant machines
`vagrant global-status --prune` | Same as above, but prunes invalid entries
`vagrant version` | Installed version
`vagrant validate` | Validate the Vagrantfile
`vagrant plugin list` | Installed plugins

## Managing VMs
COMMAND | DESCRIPTION
---|---
`vagrant init <BOX>` | Create a Vagrantfile for a box, e.g. `ubuntu/jammy64`. Without a box you must specify one in the Vagrantfile before `vagrant up`
`vagrant up` | Starts vagrant environment (also provisions only on the FIRST vagrant up)
`vagrant halt` | Stops the vagrant machine
`vagrant reload` | Restart and re-read the Vagrantfile
`vagrant suspend` | Suspends a virtual machine (remembers state)
`vagrant resume` | Resume a suspended machine (vagrant up works just fine for this as well)
`vagrant ssh` | Connects to machine via SSH
`vagrant ssh <BOXNAME>` | If you give your box a name in your Vagrantfile, you can ssh into it with boxname
`vagrant ssh-config` | SSH settings, useful for `~/.ssh/config` ([OpenSSH Cheat-Sheet](openssh.md))
`vagrant destroy` | Stops and deletes all traces of the vagrant machine
`vagrant destroy -f` | Same as above, without confirmation

## Provisioning VMs
COMMAND | DESCRIPTION
---|---
`vagrant provision` | Forces reprovisioning of the vagrant machine
`vagrant provision --debug` | Use the debug flag to increase the verbosity of the output
`vagrant up --provision \| tee provision.log` | Runs `vagrant up`, forces provisioning and logs all output to a file
`vagrant up --provision-with <NAME>` | Run one named provisioner

## Manage Boxes
COMMAND | DESCRIPTION
---|---
`vagrant box list` | See a list of all installed boxes on your computer
`vagrant box add <BOXNAME> <BOXURL>` | Download a box image to your computer
`vagrant box outdated` | Check for updates
`vagrant box update` | Update the box for the current environment
`vagrant box prune` | Remove old box versions
`vagrant box remove <BOXNAME>` | Deletes a box from the machine
`vagrant package` | Packages a running VirtualBox env in a reusable box

## Snapshots
COMMAND | DESCRIPTION
---|---
`vagrant snapshot save <NAME>` | Save state
`vagrant snapshot list` | List snapshots
`vagrant snapshot restore <NAME>` | Restore
`vagrant snapshot delete <NAME>` | Delete

## Example Vagrantfile
```ruby
Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/jammy64"
  config.vm.hostname = "dev"
  config.vm.network "private_network", ip: "192.168.56.10"
  config.vm.network "forwarded_port", guest: 80, host: 8080
  config.vm.synced_folder ".", "/vagrant"
  config.vm.provider "virtualbox" do |vb|
    vb.memory = 2048
    vb.cpus = 2
  end
  config.vm.provision "shell", inline: "apt-get update && apt-get install -y nginx"
  # or: config.vm.provision "ansible", playbook: "site.yml"  (see the Ansible Playbooks sheet)
end
```

## Vagrant with WSL2

Vagrant is able to run inside your Windows Subsystem for Linux environment ([WSL Cheat-Sheet](wsl.md)). A tutorial on how to install
and use it with your Windows installed Virtualbox can be found [here](https://thedatabaseme.de/2022/02/20/vagrant-up-running-vagrant-under-wsl2/).
