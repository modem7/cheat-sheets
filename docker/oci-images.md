# OCI Images
The Open Container Initiative (OCI) specs define the image format, runtime and registry API that Docker, Podman and Kubernetes all share. Use this sheet to inspect, copy, build multi-architecture and pin images with `skopeo`, `buildah`, `crane`, `oras` and `buildx`.

Documentation: [OCI image-spec](https://github.com/opencontainers/image-spec) · [skopeo](https://github.com/containers/skopeo/tree/main/docs) · [buildah](https://github.com/containers/buildah/tree/main/docs) · [buildx reference](https://github.com/docker/buildx/tree/master/docs/reference) · [crane](https://github.com/google/go-containerregistry/blob/main/cmd/crane/doc/crane.md) · [ORAS](https://oras.land/)

> **Verification:** layout, media types and annotation keys were checked against the image-spec repository; skopeo, buildah and buildx commands against their upstream man pages and reference docs (November 2026). Nothing was run. Items marked *(unverified)* were not confirmed. Registry and `skopeo` basics are in [Docker Registry](docker-registry.md); this sheet does not repeat them.

## The Three Specs
SPEC | WHAT IT DEFINES
---|---
Image spec | Image manifest, config and layer format
Runtime spec | How a runtime (`runc`, `crun`) runs a container bundle
Distribution spec | The registry push and pull HTTP API

## Image Layout
An OCI image on disk (for `skopeo copy ... oci:DIR:TAG`) is a directory:

PATH | PURPOSE
---|---
`oci-layout` | Contains `{"imageLayoutVersion": "1.0.0"}`
`index.json` | Entry point listing manifests
`blobs/sha256/<DIGEST>` | Manifests, configs and layers by digest

## Media Types
MEDIA TYPE | MEANING
---|---
`application/vnd.oci.image.manifest.v1+json` | Image manifest (one platform)
`application/vnd.oci.image.index.v1+json` | Image index (multi-architecture list of manifests)
`application/vnd.oci.image.config.v1+json` | Image config

## Standard Annotations
Set these as labels in the Dockerfile (`LABEL`) or build annotations. All keys start with `org.opencontainers.image.`.

KEY SUFFIX | MEANING
---|---
`created` | Build timestamp (RFC 3339)
`authors` | Contact details of the authors
`url` / `documentation` / `source` | Project, docs and source repository URLs
`version` / `revision` | Version and source control revision
`vendor` / `licenses` | Distributor and SPDX licence expression
`title` / `description` | Human-readable name and summary
`ref.name` | Reference name, for example a tag
`base.name` / `base.digest` | Base image reference and digest

```dockerfile
LABEL org.opencontainers.image.source="https://github.com/EXAMPLE/REPO" \
      org.opencontainers.image.licenses="MIT" \
      org.opencontainers.image.version="1.0.0"
```

See [Dockerfile](docker-file.md).

## skopeo
Works without a daemon and does not need the image pulled.

COMMAND | DESCRIPTION
---|---
`skopeo inspect docker://<IMAGE>` | Show metadata
`skopeo inspect --raw docker://<IMAGE>` | Show the raw manifest or index
`skopeo inspect --config docker://<IMAGE>` | Show the image config
`skopeo list-tags docker://<REPOSITORY>` | List tags
`skopeo copy docker://<SOURCE> docker://<DESTINATION>` | Copy between registries
`skopeo copy --all docker://<SOURCE> docker://<DESTINATION>` | Copy every architecture, not just the host's
`skopeo copy docker://<IMAGE> oci:<DIR>:<TAG>` | Save as an OCI layout directory
`skopeo copy docker://<IMAGE> dir:<PATH>` | Save as a plain directory
`skopeo sync --src docker --dest dir <SOURCE> <DESTINATION>` | Sync repositories (see the man page for the transports)
`skopeo delete docker://<IMAGE>` | Delete from a registry (destructive)
`skopeo login <REGISTRY>` | Authenticate

## buildah
Full reference: [Buildah](buildah.md).
Builds images without a daemon or a Dockerfile.

COMMAND | DESCRIPTION
---|---
`buildah build -t <TAG> .` | Build from a Containerfile or Dockerfile (`buildah bud` is the same command)
`buildah from <IMAGE>` | Start a working container, prints its name
`buildah run <CONTAINER> -- <COMMAND>` | Run a command in it
`buildah copy <CONTAINER> <SRC> <DEST>` | Copy files in
`buildah config --entrypoint '["<CMD>"]' <CONTAINER>` | Set image config (entrypoint form *unverified*)
`buildah commit <CONTAINER> <IMAGE>` | Create an image
`buildah images` / `buildah rm <CONTAINER>` | List images, remove a working container

## crane
COMMAND | DESCRIPTION
---|---
`crane manifest <IMAGE>` | Print the manifest
`crane digest <IMAGE>` | Print the digest
`crane ls <REPOSITORY>` | List tags
`crane copy <SOURCE> <DESTINATION>` | Copy an image
`crane export <IMAGE> <FILE>.tar` | Export the filesystem as a tarball
`crane config <IMAGE>` | Print the config
`crane catalog <REGISTRY>` | List repositories

## ORAS
ORAS pushes any file as an OCI artefact.

COMMAND | DESCRIPTION
---|---
`oras push <REF> <FILE>[:<TYPE>]` | Push files as an artefact
`oras pull <REF>` | Pull an artefact
`oras manifest fetch <REF>` | Print a manifest
`oras copy <SOURCE> <DESTINATION>` | Copy between registries *(unverified)*

## Multi-Architecture Builds
COMMAND | DESCRIPTION
---|---
`docker buildx build --platform linux/amd64,linux/arm64 -t <IMAGE> --push .` | Build for several platforms and push as one index
`docker buildx build -o type=oci,dest=<FILE>.tar .` | Export an OCI archive instead of loading
`docker buildx build --provenance=true --sbom=true --push -t <IMAGE> .` | Attach provenance and SBOM attestations (see [Container Scanning](../security/container-scanning.md))
`docker buildx imagetools inspect <IMAGE>` | Show an index and its platforms
`podman manifest create <LIST>` | Create a manifest list *(unverified)*
`podman manifest push --all <LIST> <DESTINATION>` | Push a list with all its images
`podman save --format oci-archive -o <FILE>.tar <IMAGE>` | Save as an OCI archive (`docker save` writes Docker's own format)

Building for a foreign architecture needs QEMU emulation or a native builder *(general practice, unverified)*.

## Pin and Verify
COMMAND | DESCRIPTION
---|---
`docker image ls --digests` | Show digests of local images
`skopeo inspect docker://<IMAGE> --format '{{.Digest}}'` | Fetch a digest (the `--format` flag is *unverified*)
`crane digest <IMAGE>` | Fetch a digest
`<IMAGE>@sha256:<DIGEST>` | Reference an image by digest in a Compose file or manifest
`cosign sign <IMAGE>` / `cosign verify <IMAGE>` | Sign and verify images (verify needs identity flags, see the cosign docs)

A tag can move; a digest cannot. Pin by digest for reproducible deployments and let Renovate update it. `crun --version` reports the runtime version; `docker info` shows configured runtimes *(output unverified)*. Inspecting layers with `dive` and generating SBOMs with `syft` are *not verified* here.

## See Also
- [Docker](docker.md)
- [Docker Registry](docker-registry.md)
- [Dockerfile](docker-file.md)
- [Podman](podman.md)
- [Docker Buildx](buildx.md)
- [Buildah](buildah.md)
- [Container Scanning](../security/container-scanning.md)
