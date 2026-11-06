# Go and Rust Toolchains
Everyday commands for building, testing and installing programs with the Go toolchain and with Rust's `rustup` and `cargo`. Both compile to single static-ish binaries, which makes them popular for homelab CLIs (several tools in [Modern CLI Tools](modern-cli-tools.md) install with `cargo install` or `go install`).

Documentation: [Go docs](https://go.dev/doc/), [Go command](https://pkg.go.dev/cmd/go), [Rust book](https://doc.rust-lang.org/book/), [Cargo book](https://doc.rust-lang.org/cargo/)

## Go: Install and Environment
COMMAND | DESCRIPTION
---|---
`go version` | Show the Go version
`go env` | Show all Go environment settings
`go env GOPATH GOROOT GOOS GOARCH` | Show specific settings
`go env -w GOFLAGS=-mod=readonly` | Persist a setting
`go install golang.org/dl/go1.23.0@latest && go1.23.0 download` | Install an extra Go version side by side
`export PATH="$PATH:$(go env GOPATH)/bin"` | Put `go install` binaries on `PATH`

Download from [go.dev/dl](https://go.dev/dl/) or use `brew install go` ([Homebrew](../macos/homebrew.md)) or `winget install GoLang.Go` ([winget](../windows/winget.md)). The apt package is often old. Since Go 1.21 the `go` line in `go.mod` can trigger an automatic toolchain download (`GOTOOLCHAIN`).

## Go: Modules
COMMAND | DESCRIPTION
---|---
`go mod init github.com/<USER>/<REPO>` | Start a module (creates `go.mod`)
`go get <MODULE>@latest` | Add or upgrade a dependency
`go get <MODULE>@v1.2.3` | Pin a version
`go get -u ./...` | Update all dependencies of the module
`go mod tidy` | Add missing and remove unused requirements
`go mod download` | Fetch dependencies into the module cache
`go mod vendor` | Copy dependencies into `vendor/`
`go mod why <MODULE>` | Why is it needed
`go mod graph` | Dependency graph
`go list -m all` | All modules in the build
`go list -m -u all` | Show available updates
`go clean -modcache` | Empty the module cache

Commit both `go.mod` and `go.sum`.

## Go: Build, Run, Test
COMMAND | DESCRIPTION
---|---
`go run .` | Compile and run the package in the current directory
`go build ./...` | Compile everything (discards results for several packages)
`go build -o bin/app ./cmd/app` | Build one binary to a path
`go build -ldflags "-s -w" -o app .` | Smaller binary (strip symbols and debug info)
`go build -ldflags "-X main.version=1.2.3" .` | Set a string variable at link time
`go build -trimpath` | Remove local file paths from the binary
`go test ./...` | Run all tests
`go test -v -run TestName ./pkg` | One test, verbose
`go test -race ./...` | Race detector
`go test -cover ./...` | Coverage summary
`go test -coverprofile=c.out ./... && go tool cover -html=c.out` | HTML coverage report
`go test -bench=. -benchmem ./...` | Benchmarks
`go test -count=1 ./...` | Skip the test result cache
`go vet ./...` | Static checks
`gofmt -l -w .` / `go fmt ./...` | Format code
`go doc <PACKAGE>.<SYMBOL>` | Show documentation
`go tool pprof <FILE>` | Profile analysis

## Go: Install and Cross-Compile
COMMAND | DESCRIPTION
---|---
`go install <MODULE>/cmd/<TOOL>@latest` | Install a tool into `$(go env GOPATH)/bin`
`go install ./cmd/app` | Install from the local module
`GOOS=linux GOARCH=amd64 go build -o app-linux-amd64 .` | Cross-compile for Linux x86-64
`GOOS=linux GOARCH=arm64 go build -o app-linux-arm64 .` | Linux ARM64 (Raspberry Pi 4/5, Ampere)
`GOOS=windows GOARCH=amd64 go build -o app.exe .` | Windows
`GOOS=darwin GOARCH=arm64 go build -o app-darwin .` | Apple Silicon
`CGO_ENABLED=0 go build -o app .` | Fully static binary (no C library), ideal for scratch containers
`go tool dist list` | All supported OS/architecture pairs

PowerShell sets variables differently:
```powershell
$env:GOOS = "linux"; $env:GOARCH = "amd64"; go build -o app .
Remove-Item Env:GOOS, Env:GOARCH
```
A minimal container build pairs well with a multi-stage [Dockerfile](../docker/docker-file.md).

## Rust: rustup
COMMAND | DESCRIPTION
---|---
`curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs \| sh` | Install rustup (review the script first)
`winget install Rustlang.Rustup` | Windows ([winget](../windows/winget.md))
`rustup update` | Update all toolchains
`rustup show` | Active toolchain and targets
`rustup toolchain install stable` | Install a channel (`beta`, `nightly`, or `1.80.0`)
`rustup default stable` | Set the default toolchain
`rustup override set nightly` | Use a toolchain only in the current directory
`rustup component add clippy rustfmt` | Add the linter and formatter
`rustup component add rust-src rust-analyzer` | Sources and language server for editors ([VSCode (Visual Studio Code)](vscode.md))
`rustup target list --installed` | Installed compile targets
`rustup target add <TARGET>` | Add a cross-compile target
`rustup self uninstall` | Remove rustup and Rust
`rustc --version` / `cargo --version` | Check versions

Pin a project toolchain with a `rust-toolchain.toml` file:
```toml
[toolchain]
channel = "stable"
components = ["clippy", "rustfmt"]
targets = ["x86_64-unknown-linux-musl"]
```

## Rust: Cargo
COMMAND | DESCRIPTION
---|---
`cargo new <NAME>` | New binary project (`--lib` for a library)
`cargo init` | Initialise the current directory
`cargo add <CRATE>` | Add a dependency (`--features <F>`, `--dev`)
`cargo remove <CRATE>` | Remove a dependency
`cargo build` | Debug build into `target/debug`
`cargo build --release` | Optimised build into `target/release`
`cargo run -- <ARGS>` | Build and run, passing arguments to the program
`cargo check` | Type-check without producing binaries (fast)
`cargo test` | Run tests (`cargo test <NAME> -- --nocapture` for output)
`cargo clippy -- -D warnings` | Lint and fail on warnings
`cargo fmt` / `cargo fmt --check` | Format / check formatting
`cargo doc --open` | Build and open documentation
`cargo update` | Update `Cargo.lock` within semver ranges
`cargo tree` | Dependency tree (`-i <CRATE>` for reverse)
`cargo outdated` | Outdated crates (needs `cargo install cargo-outdated`)
`cargo audit` | Known vulnerabilities (needs `cargo install cargo-audit`)
`cargo clean` | Delete `target/`
`cargo bench` | Run benchmarks
`cargo publish` | Publish to crates.io

## Rust: Install Tools
COMMAND | DESCRIPTION
---|---
`cargo install <CRATE>` | Build and install a binary crate into `~/.cargo/bin`
`cargo install --locked <CRATE>` | Use the crate's own lockfile (more reproducible)
`cargo install --path .` | Install the local project
`cargo install --git <URL>` | Install from a Git repository
`cargo install --list` | Installed crates
`cargo uninstall <CRATE>` | Remove
`cargo binstall <CRATE>` | Download a prebuilt binary instead of compiling (needs `cargo-binstall`)

Add `~/.cargo/bin` to `PATH` (rustup does this via `~/.cargo/env`). Examples: `cargo install --locked ripgrep fd-find bat eza zoxide git-delta`.

## Rust: Release Profile
```toml
# Cargo.toml
[profile.release]
opt-level = 3
lto = true          # slower build, smaller and faster binary
codegen-units = 1
strip = true        # strip symbols
panic = "abort"
```

## Rust: Cross-Compile
COMMAND | DESCRIPTION
---|---
`rustup target add x86_64-unknown-linux-musl` | Static Linux target
`cargo build --release --target x86_64-unknown-linux-musl` | Build for it (output in `target/<TARGET>/release`)
`rustup target add aarch64-unknown-linux-gnu` | ARM64 Linux (needs `gcc-aarch64-linux-gnu` and a linker setting)
`rustup target add x86_64-pc-windows-gnu` | Windows from Linux (needs `mingw-w64`)
`cargo install cross` | `cross build --target <TARGET>` uses Docker containers with the right toolchain ([Docker](../docker/docker.md))
`cargo zigbuild --target <TARGET>` | Use Zig as the linker (needs `cargo-zigbuild`)

Set a linker for a target in `.cargo/config.toml`:
```toml
[target.aarch64-unknown-linux-gnu]
linker = "aarch64-linux-gnu-gcc"
```
Pure-Rust projects cross-compile easily; crates that need C libraries (OpenSSL) are the usual problem. Prefer `rustls` features, or use `cross`.

## Go vs Rust Quick Map
TASK | GO | RUST
---|---|---
New project | `go mod init` | `cargo new`
Add dependency | `go get <MOD>` | `cargo add <CRATE>`
Build / run | `go build` / `go run .` | `cargo build` / `cargo run`
Test | `go test ./...` | `cargo test`
Format / lint | `go fmt` / `go vet` | `cargo fmt` / `cargo clippy`
Install a tool | `go install <MOD>@latest` | `cargo install <CRATE>`
Dependency file | `go.mod`, `go.sum` | `Cargo.toml`, `Cargo.lock`

## Not Verified
Commands were written from the official documentation and not executed. Crate names and cross-compile linker packages depend on the target distro.
