# Buildah
Buildah builds OCI and Docker images without a daemon, and without root when run rootless. Use it for Containerfile builds in CI where Docker is unavailable, or to build an image step by step from a shell script without a Dockerfile.

Documentation: [Buildah docs](https://github.com/containers/buildah/tree/main/docs) · `man buildah`
Project: [containers/buildah](https://buildah.io/)

> **Verification:** options checked against the Ubuntu 24.04 `buildah` man pages with a script that flags any option missing from the pages. Nothing was run. `buildah-build(1)` documents the command as `buildah bud` in that release; `buildah build` is listed in the same page set.

Related sheets: [Podman](podman.md), [Docker Buildx](buildx.md), [OCI Images](oci-images.md) (short Buildah section and `skopeo`), [Dockerfile](docker-file.md), [Docker Registry](docker-registry.md), [GitLab CI/CD](../cicd/gitlab-ci.md).

## Build From a Containerfile
COMMAND | DESCRIPTION
---|---
`buildah build -t <IMAGE>:<TAG> .` | Build from `Containerfile` or `Dockerfile` (`buildah bud` is the older name)
`buildah build -f <FILE> -t <IMAGE>:<TAG> <CONTEXT>` | Pick the file and context
`buildah build --build-arg <NAME>=<VALUE> .` | Pass a build argument
`buildah build --layers .` | Cache intermediate layers (off by default in this release)
`buildah build --platform linux/amd64,linux/arm64 --manifest <NAME> .` | Multi-platform build into a manifest list
`buildah build --all-platforms --manifest <NAME> .` | Every platform the base image supports
`buildah build --format docker .` | Docker image format instead of OCI (`oci` is the default)
`buildah build --secret id=<ID>,src=<FILE> .` | Expose a build secret (see the man page for the full syntax)
`buildah build --cache-from <REPO> --cache-to <REPO> .` | Use a registry as layer cache
`buildah build --iidfile <FILE> .` | Write the image ID to a file
`buildah build --isolation chroot .` | Pick the isolation mode (useful inside containers)

## Build Without a Dockerfile
A working container is a mutable image under construction. Script it with ordinary shell.

```bash
ctr=$(buildah from docker.io/library/alpine:3.20)
buildah run "$ctr" -- apk add --no-cache curl
buildah copy "$ctr" ./app /usr/local/bin/app
buildah config --entrypoint '["/usr/local/bin/app"]' --port 8080 --label org.opencontainers.image.source=https://example.com/repo "$ctr"
buildah commit "$ctr" registry.example.com/team/app:1.0
buildah rm "$ctr"
```

COMMAND | DESCRIPTION
---|---
`buildah from <IMAGE>` | Create a working container and print its name
`buildah from --name <NAME> <IMAGE>` | Choose the name
`buildah from scratch` | Start from an empty image
`buildah run <CTR> -- <COMMAND>` | Run a command inside (`--user`, `--env`, `--volume`, `--network` also apply)
`buildah copy <CTR> <SRC> <DEST>` | Copy files in
`buildah add <CTR> <SRC> <DEST>` | Like `copy`, plus URL and archive handling
`buildah config --env <NAME>=<VALUE> <CTR>` | Set an environment variable in the image config
`buildah config --cmd '<COMMAND>' --workingdir <DIR> --user <USER> <CTR>` | Set command, working directory and user
`buildah config --label <KEY>=<VALUE> --annotation <KEY>=<VALUE> <CTR>` | Labels and annotations
`buildah commit <CTR> <IMAGE>:<TAG>` | Turn the container into an image
`buildah commit --squash <CTR> <IMAGE>:<TAG>` | Squash layers on commit
`buildah commit --rm <CTR> <IMAGE>:<TAG>` | Remove the working container afterwards
`buildah mount <CTR>` | Mount its filesystem and print the path (needs `buildah unshare` when rootless)
`buildah umount <CTR>` | Unmount it
`buildah unshare` | Shell in the user namespace, so rootless mounts work

## Images and Containers
COMMAND | DESCRIPTION
---|---
`buildah images` | List local images (`--json`, `--digests`, `-a`)
`buildah containers` | List working containers (`-a` includes ones from other tools)
`buildah inspect <NAME>` | Show config (`--type container\|image\|manifest`, `--format '<TEMPLATE>'`)
`buildah tag <IMAGE> <NEW_NAME>` | Add a name
`buildah rename <OLD> <NEW>` | Rename a working container
`buildah rm <CTR>` / `buildah rm --all` | Remove working containers
`buildah rmi <IMAGE>` | Remove an image (`--all`, `--force`, `--prune`)
`buildah prune` | Remove intermediate images and build cache (`-a` for more)
`buildah info` | Show host, storage and runtime details
`buildah version` | Show the version

## Pull, Push and Log In
COMMAND | DESCRIPTION
---|---
`buildah pull <IMAGE>` | Pull an image
`buildah login <REGISTRY>` / `buildah logout <REGISTRY>` | Store or remove credentials (`--authfile <FILE>`)
`buildah push <IMAGE> docker://<REGISTRY>/<REPO>:<TAG>` | Push to a registry
`buildah push <IMAGE> oci:<DIR>:<TAG>` | Write an OCI layout directory
`buildah push <IMAGE> dir:<DIR>` | Write a plain directory
`buildah push <IMAGE> docker-daemon:<NAME>:<TAG>` | Load into a local Docker daemon
`buildah push --digestfile <FILE> <IMAGE> docker://<REGISTRY>/<REPO>:<TAG>` | Save the pushed digest
`buildah push --sign-by <FINGERPRINT> ...` | Sign with a GPG key
`buildah push --tls-verify=false ...` | Allow an untrusted or plain-HTTP registry (testing only)

## Manifest Lists
COMMAND | DESCRIPTION
---|---
`buildah manifest create <LIST>` | Create an empty list
`buildah manifest add <LIST> <IMAGE>` | Add an image
`buildah manifest annotate --arch <ARCH> --os <OS> <LIST> <IMAGE>` | Set platform info on an entry
`buildah manifest inspect <LIST>` | Show it
`buildah manifest push --all <LIST> docker://<REGISTRY>/<REPO>:<TAG>` | Push the list and every image in it
`buildah manifest rm <LIST>` / `buildah manifest remove <LIST> <DIGEST>` | Delete a list, or remove one entry
`buildah manifest exists <LIST>` | Exit status says whether it exists

## Rootless Setup and CI
COMMAND | DESCRIPTION
---|---
`grep "$USER" /etc/subuid /etc/subgid` | Rootless builds need subordinate UID and GID ranges for the user
`buildah --storage-driver vfs build -t <IMAGE> .` | Storage driver for CI containers without overlay support
`buildah --root <DIR> --runroot <DIR> ...` | Keep image storage in a specific location

In a CI job, use a Buildah image your team trusts and pin its tag (the upstream project publishes `quay.io/buildah/stable`; unverified here). See [GitLab CI/CD](../cicd/gitlab-ci.md) for a Docker-less build job.

## Troubleshooting
SYMPTOM | FIX
---|---
Rootless `mount` fails | Run it inside `buildah unshare`
Permission or namespace errors when Buildah runs inside a container | Try `--isolation chroot`, or give the CI job the permissions Buildah needs (unverified: depends on the runtime)
Overlay mount errors in nested containers | Try `--storage-driver vfs` (slower, larger)
Push refused with an authentication error | `buildah login <REGISTRY>` or pass `--creds <USER>:<PASSWORD>` / `--authfile`
Image works in Docker but not in Podman or Kubernetes | Check `--format` and the registry's media-type support

## See Also
- [Podman](podman.md)
- [Docker Buildx](buildx.md)
- [OCI Images](oci-images.md)
- [Dockerfile](docker-file.md)
