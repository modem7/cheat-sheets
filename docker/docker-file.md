# Dockerfile
A Dockerfile is a text file of instructions Docker reads to build an image. See also [[docker]], [[docker-compose]] and [[docker-networking]].

## Instructions
INSTRUCTION | DESCRIPTION
---|---
`FROM <IMAGE>:<TAG>` | Base image. Pin a tag or digest, avoid `latest`
`FROM <IMAGE> AS <NAME>` | Start a named build stage
`WORKDIR /app` | Set the working directory (created if missing)
`COPY <SRC> <DEST>` | Copy files from the build context
`COPY --from=<STAGE> <SRC> <DEST>` | Copy files from another stage
`COPY --chown=<USER>:<GROUP> <SRC> <DEST>` | Copy and set ownership
`ADD <URL-OR-TAR> <DEST>` | Like COPY, plus URLs and tar auto-extract. Prefer COPY
`RUN <CMD>` | Run a command at build time and commit the layer
`ENV KEY=value` | Environment variable, kept in the image
`ARG NAME=default` | Build-time variable (`--build-arg NAME=value`)
`EXPOSE 8080` | Document a listening port (does not publish it)
`USER <USER>` | Run later instructions and the container as this user
`VOLUME /data` | Declare a mount point
`HEALTHCHECK CMD <CMD>` | Command Docker runs to check container health
`ENTRYPOINT ["executable"]` | The fixed command of the container
`CMD ["arg1"]` | Default arguments, or default command if no ENTRYPOINT
`LABEL org.opencontainers.image.source="<URL>"` | Image metadata

## Example: Multi-Stage Build
```dockerfile
# syntax=docker/dockerfile:1
FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN --mount=type=cache,target=/root/.npm npm ci
COPY . .
RUN npm run build

FROM node:22-alpine
ENV NODE_ENV=production
WORKDIR /app
COPY --from=build /app/dist ./dist
COPY --from=build /app/package*.json ./
RUN npm ci --omit=dev && npm cache clean --force
USER node
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://localhost:3000/health || exit 1
CMD ["node", "dist/index.js"]
```

## Best Practices
- **Order layers by change frequency.** Copy dependency manifests and install first, copy source last, so the cache survives code changes.
- **Use multi-stage builds** to keep compilers and build tools out of the final image.
- **Combine related RUN steps** and clean up in the same layer: `apt-get update && apt-get install -y --no-install-recommends <PKG> && rm -rf /var/lib/apt/lists/*`.
- **Run as a non-root user** with `USER`.
- **Use exec form** (`CMD ["a","b"]`) so signals reach your process. Shell form wraps it in `sh -c`.
- **Add a `.dockerignore`** (`.git`, `node_modules`, `*.log`, `.env`) to shrink the build context and avoid leaking secrets.
- **Never bake secrets into layers.** Use `RUN --mount=type=secret,id=<NAME> ...` at build time.
- **Pin versions** of base images and packages for reproducible builds.

## ENTRYPOINT vs CMD
ENTRYPOINT | CMD | `docker run <IMAGE> x`
---|---|---
unset | `["a"]` | runs `x`
`["e"]` | unset | runs `e x`
`["e"]` | `["a"]` | runs `e x` (CMD replaced)

## Build Commands
COMMAND | DESCRIPTION
---|---
`docker build -t <NAME>:<TAG> .` | Build an image
`docker build -f <FILE> -t <NAME> .` | Use a different Dockerfile
`docker build --no-cache -t <NAME> .` | Ignore the layer cache
`docker build --target <STAGE> -t <NAME> .` | Build only up to a stage
`docker build --build-arg KEY=value -t <NAME> .` | Pass a build argument
`docker buildx build --platform linux/amd64,linux/arm64 -t <NAME> --push .` | Multi-arch build and push
`docker history <NAME>` | Show image layers and sizes
