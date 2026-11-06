# Packer
HashiCorp Packer builds identical machine images (VM templates, cloud images, container images) from one HCL template. Typical homelab use is building a Proxmox VM template from an ISO and then cloning it with [[terraform]] or [[proxmox-qm-pct]]. Provisioning inside the image is often done with [[ansible]].

Documentation: [Packer docs](https://developer.hashicorp.com/packer/docs), [Proxmox plugin](https://developer.hashicorp.com/packer/integrations/hashicorp/proxmox)

## Workflow
COMMAND | DESCRIPTION
---|---
`packer init .` | Download the plugins declared in `required_plugins`
`packer fmt .` | Format templates (`-check` for CI)
`packer validate .` | Check syntax and configuration
`packer validate -var-file=prod.pkrvars.hcl .` | Validate with a variable file
`packer build .` | Build all sources in the directory
`packer build -only='ubuntu.proxmox-iso.noble' .` | Build one named source
`packer build -except='*.docker.*' .` | Skip matching builds
`packer build -var 'node=pve1' .` | Set a variable on the command line
`packer build -var-file=prod.pkrvars.hcl .` | Load variables from a file
`packer build -on-error=ask .` | On failure keep the VM and ask what to do (`cleanup`, `abort`, `run-cleanup-provisioner`)
`packer build -debug .` | Step through each stage with confirmation
`PACKER_LOG=1 packer build .` | Verbose logging (`PACKER_LOG_PATH=packer.log` writes to a file)
`packer console .` | Interactive HCL expression evaluator
`packer inspect .` | List variables, sources and builds in a template
`packer plugins installed` | Show installed plugins
`packer plugins install github.com/hashicorp/proxmox` | Install a plugin without a template
`packer version` | Show version

Install: [[homebrew]] (`brew install hashicorp/tap/packer`), [[winget]] (`winget install Hashicorp.Packer`), or the HashiCorp apt repository.

## File Layout
Packer reads every `*.pkr.hcl` and `*.pkrvars.hcl` file in the directory given to it (use `.`, not a single file, so the whole template loads).

```
ubuntu-template/
  versions.pkr.hcl        # required_plugins
  variables.pkr.hcl       # variable blocks
  ubuntu.pkr.hcl          # source and build blocks
  secrets.auto.pkrvars.hcl  # not committed
  http/
    user-data             # cloud-init autoinstall files
    meta-data
```
Files named `*.auto.pkrvars.hcl` load automatically.

## Template: Proxmox ISO to Template
`versions.pkr.hcl`:
```hcl
packer {
  required_plugins {
    proxmox = {
      version = ">= 1.2.0"
      source  = "github.com/hashicorp/proxmox"
    }
  }
}
```

`variables.pkr.hcl`:
```hcl
variable "proxmox_url" {
  type = string
}

variable "proxmox_token_id" {
  type = string
}

variable "proxmox_token_secret" {
  type      = string
  sensitive = true
}

variable "node" {
  type    = string
  default = "pve"
}

variable "ssh_password" {
  type      = string
  sensitive = true
}
```

`ubuntu.pkr.hcl`:
```hcl
source "proxmox-iso" "noble" {
  proxmox_url              = var.proxmox_url            # https://<PVE-HOST>:8006/api2/json
  username                 = var.proxmox_token_id       # user@realm!tokenname
  token                    = var.proxmox_token_secret
  insecure_skip_tls_verify = true                       # only for self-signed lab certs
  node                     = var.node

  vm_id                = 9000
  vm_name              = "ubuntu-2404-template"
  template_description = "Built by Packer"
  tags                 = "template;ubuntu"

  boot_iso {
    type         = "scsi"
    iso_file     = "local:iso/ubuntu-24.04-live-server-amd64.iso"
    unmount      = true
  }

  cores           = 2
  memory          = 2048
  cpu_type        = "host"
  os              = "l26"
  qemu_agent      = true
  scsi_controller = "virtio-scsi-single"

  disks {
    disk_size    = "20G"
    storage_pool = "local-lvm"
    type         = "scsi"
    discard      = true
    io_thread    = true
  }

  network_adapters {
    model    = "virtio"
    bridge   = "vmbr0"
    firewall = false
  }

  cloud_init              = true
  cloud_init_storage_pool = "local-lvm"

  http_directory = "http"
  boot_wait      = "5s"
  boot_command = [
    "c<wait>",
    "linux /casper/vmlinuz autoinstall ds=nocloud-net\\;s=http://{{ .HTTPIP }}:{{ .HTTPPort }}/ ---<enter><wait>",
    "initrd /casper/initrd<enter><wait>",
    "boot<enter>"
  ]

  ssh_username = "ubuntu"
  ssh_password = var.ssh_password
  ssh_timeout  = "30m"
}

build {
  name    = "ubuntu"
  sources = ["source.proxmox-iso.noble"]

  provisioner "shell" {
    inline = [
      "sudo cloud-init clean --logs",
      "sudo apt-get -y autoremove --purge",
      "sudo apt-get -y clean",
      "sudo truncate -s 0 /etc/machine-id",
    ]
  }

  post-processor "manifest" {
    output = "manifest.json"
  }
}
```
Older plugin releases use `iso_file` and `iso_storage_pool` directly on the source instead of a `boot_iso` block; match the syntax to your plugin version. The `boot_command` is distro specific and must be adapted to your installer.

Other Proxmox builder: `proxmox-clone` builds from an existing template (`clone_vm = "<TEMPLATE>"`), which is much faster for layering changes on a base image.

## Variables
WAY | EXAMPLE
---|---
Default in the template | `variable "node" { default = "pve" }`
Command line | `packer build -var 'node=pve2' .`
Variable file | `packer build -var-file=lab.pkrvars.hcl .` with `node = "pve2"` inside
Auto-loaded file | `*.auto.pkrvars.hcl` in the template directory
Environment | `export PKR_VAR_proxmox_token_secret='<TOKEN>'`
Local value | `locals { image_name = "ubuntu-${formatdate("YYYYMMDD", timestamp())}" }`

Mark secrets `sensitive = true` so they are masked in output, and supply them from environment variables or a file excluded by `.gitignore`. Never commit tokens or passwords. Read from [[bitwarden]] at run time if you keep secrets there.

## Provisioners
PROVISIONER | USE
---|---
`shell` | Run inline commands or scripts (`script = "scripts/base.sh"`)
`file` | Copy a file or directory into the image
`ansible` | Run a playbook over SSH (needs Ansible on the build host; see [[ansible-playbook]])
`ansible-local` | Run Ansible inside the machine
`powershell` | Windows images
`windows-restart` | Reboot a Windows guest and wait

```hcl
provisioner "ansible" {
  playbook_file   = "ansible/base.yml"
  extra_arguments = ["--extra-vars", "env=lab"]
}
```
The `ansible` provisioner needs its own plugin entry: `github.com/hashicorp/ansible` in `required_plugins`.

## Post-Processors
POST-PROCESSOR | USE
---|---
`manifest` | Write a JSON list of artifacts (IDs, names) for later pipeline steps
`shell-local` | Run a command on the build host, for example to tag or notify
`checksum` | Write checksums of the artifact
`compress` | Compress file artifacts
`docker-tag`, `docker-push` | Tag and push Docker images (see [[docker]])
`vagrant` | Build a Vagrant box ([[vagrant]])

Chain steps with `post-processors { ... }` (plural) to feed one output into the next.

## Other Builders
BUILDER | PLUGIN SOURCE
---|---
`docker` | `github.com/hashicorp/docker`
`vsphere-iso` | `github.com/hashicorp/vsphere`
`amazon-ebs` | `github.com/hashicorp/amazon`
`qemu` | `github.com/hashicorp/qemu`
`virtualbox-iso` | `github.com/hashicorp/virtualbox`
`azure-arm` | `github.com/hashicorp/azure`

## Tips
- Set the Proxmox API user to an API token with only the roles it needs (VM allocate, datastore allocate, audit) rather than `root@pam`; see [[proxmox-access-api]].
- The VM must reach the build host's HTTP server (`{{ .HTTPIP }}`): check firewall rules on the build machine ([[proxmox-firewall]], [[ufw]]).
- Enable `qemu_agent = true` and install `qemu-guest-agent` in the image so Packer can read the IP.
- If a build hangs at boot, run `packer build -debug .` or watch the VM console in the Proxmox UI.
- Clean `machine-id`, SSH host keys and cloud-init state before templating so clones get unique identities.

## Not Verified
Commands and the template were written from the official documentation and not executed. Proxmox plugin argument names change between versions: check the plugin docs for the version you install.
