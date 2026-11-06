# Node.js and npm
Node.js runs JavaScript outside the browser; `npm` is its bundled package manager and `pnpm` is a faster, disk-efficient alternative. Manage Node versions with `nvm` or `fnm` rather than a system package so each project can pin its own.

Documentation: [npm docs](https://docs.npmjs.com/cli/commands), [pnpm docs](https://pnpm.io/cli/add), [fnm](https://github.com/Schniz/fnm), [nvm](https://github.com/nvm-sh/nvm)

## Version Managers
COMMAND | DESCRIPTION
---|---
`curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh \| bash` | Install nvm (check the latest tag; review the script first)
`nvm install --lts` | Install the latest LTS release
`nvm install 22` | Install a major version
`nvm use 22` | Use a version in this shell
`nvm alias default 22` | Default for new shells
`nvm ls` / `nvm ls-remote --lts` | Installed / available versions
`nvm use` | Use the version from `.nvmrc` in the current directory
`curl -fsSL https://fnm.vercel.app/install \| bash` | Install fnm (fast, Rust based; also `brew install fnm`, `winget install Schniz.fnm`)
`eval "$(fnm env --use-on-cd)"` | Enable fnm in bash/zsh with automatic version switching (put in the shell profile)
`fnm install --lts` / `fnm use 22` / `fnm default 22` | Install, use and set default
`fnm list` / `fnm list-remote` | Installed / available versions
`node -v` / `npm -v` | Check versions

Pin a project version by putting `22` (or `lts/*`) in `.nvmrc`; fnm reads `.nvmrc` and `.node-version`. The `engines` field in `package.json` documents the supported range. `corepack enable` activates `pnpm` and `yarn` at the version a project declares in `packageManager` (Corepack ships with most Node releases; newer ones may need `npm install -g corepack` first).

## npm Commands
COMMAND | DESCRIPTION
---|---
`npm init -y` | Create a `package.json`
`npm install` / `npm i` | Install everything from `package.json` and the lockfile
`npm ci` | Clean install strictly from `package-lock.json` (CI, fails on mismatch)
`npm install <PKG>` | Add a dependency
`npm install -D <PKG>` | Add a dev dependency
`npm install <PKG>@<VERSION>` | Specific version or tag (`@latest`, `@next`)
`npm install -g <PKG>` | Global install (avoid; prefer `npx` or a version manager)
`npm uninstall <PKG>` | Remove a dependency
`npm update` | Update within the semver ranges
`npm outdated` | Show packages with newer versions
`npm ls` / `npm ls --depth=0` | Dependency tree / top level only
`npm ls <PKG>` | Why is this package installed
`npm view <PKG> versions` | Published versions
`npm run <SCRIPT>` | Run a `scripts` entry (`npm test`, `npm start` omit `run`)
`npm run <SCRIPT> -- --flag` | Pass arguments through to the script
`npm exec <CMD>` / `npx <CMD>` | Run a local or remote package binary
`npm config get registry` | Show the registry in use
`npm cache verify` | Check the cache (`npm cache clean --force` clears it)
`npm pack --dry-run` | See what would be published
`npm publish --access public` | Publish a package (`npm login` first)
`npm link` | Symlink a local package for development
`npm prefix -g` | Global install location

## pnpm Commands
COMMAND | DESCRIPTION
---|---
`pnpm install` | Install dependencies (`--frozen-lockfile` for CI)
`pnpm add <PKG>` / `pnpm add -D <PKG>` | Add a dependency / dev dependency
`pnpm remove <PKG>` | Remove a dependency
`pnpm update` / `pnpm update --latest` | Update within ranges / to latest
`pnpm outdated` | Outdated packages
`pnpm run <SCRIPT>` / `pnpm <SCRIPT>` | Run a script
`pnpm dlx <PKG>` | Run a package once, like `npx`
`pnpm why <PKG>` | Why is this installed
`pnpm store prune` | Remove unreferenced packages from the global store
`pnpm -r <CMD>` | Run in every workspace package
`pnpm --filter <NAME> <CMD>` | Run in one workspace package

pnpm uses a shared content-addressable store and hard links, which saves disk space and keeps `node_modules` strict about undeclared dependencies.

## npx
COMMAND | DESCRIPTION
---|---
`npx <PKG>` | Run a package binary, downloading it if needed
`npx <PKG>@<VERSION>` | Run a specific version
`npx --no-install <CMD>` | Only use a locally installed binary
`npx -y create-vite@latest my-app` | Scaffold a project without the confirmation prompt
`npx http-server -p 8080` | Throwaway static server
`npx serve .` | Another static server

Only run packages you trust: `npx` executes code straight from the registry.

## package.json
```json
{
  "name": "my-app",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "engines": { "node": ">=22" },
  "packageManager": "pnpm@9.15.0",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "test": "vitest run",
    "lint": "eslint .",
    "prebuild": "npm run lint",
    "postinstall": "echo done"
  },
  "dependencies": {},
  "devDependencies": {}
}
```
FIELD | MEANING
---|---
`scripts` | Named commands; `pre<NAME>` and `post<NAME>` run automatically around `<NAME>`
`dependencies` | Needed at runtime
`devDependencies` | Build and test tooling only
`type: "module"` | Treat `.js` as ES modules
`engines` | Declares supported Node versions (enforced only with `engine-strict`)
`bin` | Executables a package installs
`workspaces` | Monorepo package globs (npm and yarn; pnpm uses `pnpm-workspace.yaml`)
`overrides` | Force a version of a transitive dependency (npm; pnpm uses `pnpm.overrides`)

Version ranges: `^1.2.3` allows `1.x.x` (below 2.0.0), `~1.2.3` allows `1.2.x`, `1.2.3` is exact.

## Lockfiles
MANAGER | LOCKFILE | CI INSTALL
---|---|---
npm | `package-lock.json` | `npm ci`
pnpm | `pnpm-lock.yaml` | `pnpm install --frozen-lockfile`
yarn | `yarn.lock` | `yarn install --immutable` (Yarn 2+)

Commit the lockfile for applications and use one package manager per project. Delete `node_modules` and run the CI install command to reproduce a clean build.

## Audit and Security
COMMAND | DESCRIPTION
---|---
`npm audit` | Report known vulnerabilities in dependencies
`npm audit --omit=dev` | Ignore dev dependencies
`npm audit fix` | Apply compatible fixes (`--force` allows breaking upgrades; review first)
`npm audit signatures` | Verify registry signatures and provenance
`pnpm audit` | Same check with pnpm
`npm ci --ignore-scripts` | Install without running lifecycle scripts from dependencies
`npm config set ignore-scripts true` | Disable install scripts by default

## Troubleshooting
SYMPTOM | FIX
---|---
`EACCES` on global install | Use nvm/fnm (user-owned Node) instead of `sudo npm -g`
`ERESOLVE` peer dependency conflict | Check `npm ls`; last resort `--legacy-peer-deps`
Stale or odd install | `rm -rf node_modules` then `npm ci`
Wrong Node version | `node -v`, then `nvm use` / `fnm use`; check `.nvmrc`
Behind a proxy or private registry | `npm config set registry <URL>` or a project `.npmrc`
Port already in use | `ss -ltnp \| grep <PORT>` ([Linux Basics](../linux/linuxbasics.md))

Never commit an `.npmrc` that holds an auth token; use environment variables (`//registry.npmjs.org/:_authToken=${NPM_TOKEN}`).

## Not Verified
Commands were written from the official documentation and not executed. The nvm install script version shown may be out of date.
