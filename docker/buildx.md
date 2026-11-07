# Docker Buildx
Buildx is the Docker CLI plugin that drives BuildKit: builders, multi-platform builds, cache export, attestations and `bake` (builds described in a file). `docker build` already uses it on current Docker; use this sheet for the parts beyond a single `docker buildx build`.

Documentation: [Buildx reference](https://docs.docker.com/reference/cli/docker/buildx/) · [Bake](https://docs.docker.com/build/bake/)
Project: [docker/buildx](https://github.com/docker/buildx)

> **Verification:** options checked against `docker buildx --help` output for Buildx v0.38.2 (run in the `docker:cli` image), and the Bake file below was parsed with `docker buildx bake --print`. No image was built or pushed. Flags can change between releases; run `docker buildx <COMMAND> --help` for yours.

Related sheets: [Docker](docker.md), [Dockerfile](docker-file.md), [OCI Images](oci-images.md), [Docker Registry](docker-registry.md), [CI Docker Builds](../cicd/ci-docker-builds.md), [Buildah](buildah.md).

## Build
COMMAND | DESCRIPTION
---|---
`docker buildx build -t <IMAGE>:<TAG> .` | Build with the current builder
`docker buildx build --load -t <IMAGE>:<TAG> .` | Load the result into the local image store (single platform)
`docker buildx build --push -t <REGISTRY>/<IMAGE>:<TAG> .` | Push straight to a registry
`docker buildx build --platform linux/amd64,linux/arm64 --push -t <REGISTRY>/<IMAGE>:<TAG> .` | Multi-platform image
`docker buildx build -f <DOCKERFILE> --target <STAGE> .` | Pick a file and a stage
`docker buildx build --build-arg <NAME>=<VALUE> .` | Pass a build argument
`docker buildx build --secret id=<ID>,src=<FILE> .` | Expose a secret to `RUN --mount=type=secret`
`docker buildx build --ssh default .` | Forward the SSH agent to `RUN --mount=type=ssh`
`docker buildx build --no-cache --pull .` | Ignore the cache and refresh base images
`docker buildx build -o type=local,dest=<DIR> .` | Export files instead of an image (`--output`)
`docker buildx build --progress plain .` | Plain log output (`auto`, `none`, `plain`, `rawjson`, `tty`)
`docker buildx build --iidfile <FILE> --metadata-file <FILE> .` | Write the image ID and build metadata for scripts
`docker buildx build --check .` | Lint the Dockerfile without building (same as `--call=check`)
`docker buildx build --call outline .` | Show the build's arguments and stages (`--call` takes `build`, `check`, `outline`, `targets`)

## Cache
COMMAND | DESCRIPTION
---|---
`--cache-to type=registry,ref=<REGISTRY>/<IMAGE>:buildcache,mode=max` | Export cache to a registry tag
`--cache-from type=registry,ref=<REGISTRY>/<IMAGE>:buildcache` | Import cache from it
`--cache-to type=local,dest=<DIR> --cache-from type=local,src=<DIR>` | Cache in a directory
`--cache-to type=gha --cache-from type=gha` | GitHub Actions cache backend (unverified here; see [CI Docker Builds](../cicd/ci-docker-builds.md))
`docker buildx du` | Show build cache disk usage (`--verbose`, `--filter`)
`docker buildx prune` | Remove build cache (`-a` all, `-f` no prompt, `--filter until=72h`)
`docker buildx prune --max-used-space <SIZE>` | Prune down to a size limit (also `--reserved-space`, `--min-free-space`)

The default `docker` driver cannot export cache or build multi-platform images; create a `docker-container` builder for those.

## Attestations
COMMAND | DESCRIPTION
---|---
`--provenance=mode=max` | Attach a provenance attestation (shorthand for `--attest type=provenance,...`)
`--sbom=true` | Attach an SBOM attestation (shorthand for `--attest type=sbom`)
`--attest type=sbom,generator=<IMAGE>` | Choose the SBOM generator image
`--annotation <KEY>=<VALUE>` | Add an OCI annotation to the image
`--policy <OPTIONS>` | Evaluate a build policy (format in `docker buildx build --help`; unverified here)

## Builders
COMMAND | DESCRIPTION
---|---
`docker buildx ls` | List builders and their nodes
`docker buildx create --name <NAME> --driver docker-container --use` | Create and select a builder
`docker buildx create --driver kubernetes --name <NAME>` | Builder that runs in a cluster (drivers: `docker-container`, `kubernetes`, `remote`, `cloud`)
`docker buildx create --append --name <NAME> --node <NODE> --platform linux/arm64 <CONTEXT>` | Add a node to a builder
`docker buildx create --driver-opt network=host --buildkitd-config <FILE>` | Driver option and BuildKit config file
`docker buildx inspect --bootstrap` | Start the builder and list its platforms
`docker buildx use <NAME>` | Make a builder the default
`docker buildx stop <NAME>` | Stop a builder
`docker buildx rm <NAME>` | Remove a builder (`--keep-state`, `--keep-daemon`, `--all-inactive`)
`docker buildx build --builder <NAME> .` | Use a builder for one command

## Bake
`docker-bake.hcl` (or JSON, or a Compose file) describes targets so one command builds them all.

```hcl
variable "TAG" {
  default = "latest"
}

group "default" {
  targets = ["app", "worker"]
}

target "app" {
  context    = "."
  dockerfile = "Dockerfile"
  tags       = ["registry.example.com/app:${TAG}"]
  platforms  = ["linux/amd64", "linux/arm64"]
}

target "worker" {
  inherits = ["app"]
  target   = "worker"
  tags     = ["registry.example.com/worker:${TAG}"]
}
```

COMMAND | DESCRIPTION
---|---
`docker buildx bake` | Build the `default` group
`docker buildx bake <TARGET>` | Build one target
`docker buildx bake --print` | Print the resolved config without building
`docker buildx bake --list=targets` / `--list=variables` | List targets or variables
`docker buildx bake --var TAG=1.2.3` | Set a variable
`docker buildx bake --set app.platform=linux/amd64` | Override a target value (`--set '*.output=type=docker'` for all)
`docker buildx bake -f <FILE>` | Use another file (repeatable)
`docker buildx bake --push` / `--load` | Push or load every target
`docker buildx bake --check` | Lint every target
`docker buildx bake -j <N>` | Limit parallel jobs

## Inspect Images in a Registry
COMMAND | DESCRIPTION
---|---
`docker buildx imagetools inspect <IMAGE>:<TAG>` | Show the manifest list and platforms (`--raw` for the JSON)
`docker buildx imagetools inspect <IMAGE>:<TAG> --format '{{ json .Provenance }}'` | Show attestations with a Go template
`docker buildx imagetools create -t <IMAGE>:<NEW_TAG> <IMAGE>:<TAG>` | Add a tag to an existing image without pulling
`docker buildx imagetools create -t <IMAGE>:<TAG> <IMAGE>@sha256:<A> <IMAGE>@sha256:<B>` | Merge per-architecture images into one manifest list
`docker buildx imagetools create --dry-run ...` | Show the result without pushing

## Build History
COMMAND | DESCRIPTION
---|---
`docker buildx history ls` | List recent builds
`docker buildx history logs <REF>` | Print a build's logs
`docker buildx history trace <REF>` | Show the OpenTelemetry trace
`docker buildx history rm <REF>` | Remove build records

## Troubleshooting
SYMPTOM | FIX
---|---
Error that multi-platform builds are not supported for the `docker` driver | Create a builder: `docker buildx create --use --driver docker-container`
`exec format error` when running the image | Wrong platform: add `--platform`, or check with `imagetools inspect`
Multi-platform result missing from `docker images` | `--load` only supports one platform; use `--push` or an OCI export (unverified: `-o type=oci,dest=<FILE>`)
Cache never hits in CI | Export with `--cache-to ...,mode=max` and import with `--cache-from` on every run
Cannot emulate Arm on an Intel host | Install QEMU handlers (unverified here: `docker run --privileged --rm tonistiigi/binfmt --install all`) or use native nodes

## See Also
- [Docker](docker.md)
- [Dockerfile](docker-file.md)
- [OCI Images](oci-images.md)
- [CI Docker Builds](../cicd/ci-docker-builds.md)
- [Buildah](buildah.md)
