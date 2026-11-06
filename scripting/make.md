# Make
`make` runs recipes from a `Makefile` and rebuilds only what is out of date. Outside of compiling C it is a handy task runner for homelab and repo chores (`make up`, `make lint`, `make deploy`). Scripts that a Makefile calls are covered in [Bash](bash.md); linting in [ShellCheck and shfmt](shellcheck-shfmt.md).

Documentation: [GNU Make Manual](https://www.gnu.org/software/make/manual/make.html)

## Command Line
COMMAND | DESCRIPTION
---|---
`make` | Build the first (default) target
`make <TARGET>` | Build a specific target
`make -n` | Dry run: print recipes without running them
`make -j<N>` / `make -j$(nproc)` | Run N jobs in parallel
`make -k` | Keep going after errors
`make -B` | Rebuild everything regardless of timestamps
`make -C <DIR>` | Run in another directory
`make -f <FILE>` | Use a different makefile
`make VAR=value` | Override a variable
`make -s` | Silent, do not echo recipes
`make -p -q` | Print the rules and variables make knows
`make --warn-undefined-variables` | Catch typos in variable names

## Makefile Syntax
```make
# target: prerequisites
#<TAB>recipe
build/app: src/main.c src/util.c
	$(CC) -o $@ $^

.PHONY: all clean
all: build/app

clean:
	rm -rf build
```
Recipe lines **must start with a TAB**, not spaces. The error `*** missing separator` almost always means spaces were used (or a line is not a rule or assignment). Set `.RECIPEPREFIX = >` to use another character, or configure your editor to keep tabs in `Makefile`.

## Variables
SYNTAX | DESCRIPTION
---|---
`NAME = value` | Recursive: expanded each time it is used
`NAME := value` | Simple: expanded once, at assignment (use this by default)
`NAME ?= value` | Set only if not already set (environment or command line wins)
`NAME += more` | Append
`NAME != cmd` | Assign the output of a shell command
`$(NAME)` or `${NAME}` | Expand
`$(shell cmd)` | Run a shell command and use its output
`export NAME` | Pass to recipes' environment
`$$VAR` | A literal `$` so the shell sees `$VAR`
`override NAME = value` | Beat a command-line override

### Automatic Variables
VARIABLE | MEANING
---|---
`$@` | Target name
`$<` | First prerequisite
`$^` | All prerequisites (deduplicated)
`$+` | All prerequisites (with duplicates)
`$?` | Prerequisites newer than the target
`$*` | The stem matched by `%` in a pattern rule
`$(@D)`, `$(@F)` | Directory and file part of the target

## Phony Targets
Targets that are actions, not files. Without `.PHONY`, a file named `clean` would make `make clean` do nothing.
```make
.PHONY: up down logs test lint
up:
	docker compose up -d
down:
	docker compose down
logs:
	docker compose logs -f --tail=100
```

## Pattern Rules and Functions
```make
# Build every .o from its .c
%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

SRC := $(wildcard src/*.c)
OBJ := $(SRC:.c=.o)
OBJ2 := $(patsubst src/%.c,build/%.o,$(SRC))
```
FUNCTION | DESCRIPTION
---|---
`$(wildcard *.c)` | Expand a glob
`$(patsubst %.c,%.o,$(SRC))` | Pattern substitution
`$(SRC:.c=.o)` | Shorthand substitution
`$(subst a,b,text)` | Plain replace
`$(foreach f,$(LIST),cmd $(f))` | Loop
`$(filter %.c,$(FILES))`, `$(filter-out ...)` | Keep / drop matching words
`$(addprefix pre-,$(LIST))`, `$(addsuffix .o,$(LIST))` | Add prefix / suffix
`$(dir ...)`, `$(notdir ...)`, `$(basename ...)` | Path pieces
`$(if cond,then,else)` | Conditional
`$(call fn,arg)` | Call a user-defined `define`
`$(error message)`, `$(warning message)` | Stop or warn at parse time

## Conditionals and Includes
```make
ifeq ($(ENV),prod)
  COMPOSE_FILES := -f compose.yml -f compose.prod.yml
else
  COMPOSE_FILES := -f compose.yml
endif

ifndef VERSION
  $(error VERSION is required, run: make release VERSION=1.2.3)
endif

-include .env          # leading - ignores a missing file
include config.mk
```

## Recipes
```make
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := help
.DELETE_ON_ERROR:

deploy:
	@echo "Deploying to $(HOST)"        # @ hides the command line
	-rm -f stale.lock                   # - ignores a failure
	cd app && ./build.sh                # each line is a separate shell!
	cd app; \
	  ./build.sh && ./test.sh           # one shell via backslash continuation

.ONESHELL:                              # run the whole recipe in one shell
```
Each recipe line runs in its own shell, so `cd` and variable assignments do not carry to the next line. Use `&&`, `;` with a backslash, or `.ONESHELL`. Make does not use `bash` by default; set `SHELL := bash` before using Bash features.

## Self-Documenting Help Target
Put a `##` comment after each target and generate the help from them:
```make
.DEFAULT_GOAL := help
.PHONY: help up down lint

help: ## Show this help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

up: ## Start the stack
	docker compose up -d

down: ## Stop the stack
	docker compose down

lint: ## Run all linters
	pre-commit run --all-files
```
`make` then prints a coloured, aligned list of targets. The `awk` program is explained in [AWK](../linux/awk.md); note the doubled `$$` so make passes `$1` and `$2` through to awk.

## Example: Project Task Runner
```make
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := help

COMPOSE ?= docker compose
SERVICE ?=

.PHONY: help up down restart logs ps pull update lint fmt

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "} {printf "%-12s %s\n", $$1, $$2}'

up: ## Start services
	$(COMPOSE) up -d $(SERVICE)

down: ## Stop services
	$(COMPOSE) down

restart: ## Restart (make restart SERVICE=web)
	$(COMPOSE) restart $(SERVICE)

logs: ## Follow logs
	$(COMPOSE) logs -f --tail=100 $(SERVICE)

update: pull up ## Pull images and recreate

pull:
	$(COMPOSE) pull

lint: ## shellcheck and shfmt
	git ls-files -z '*.sh' | xargs -0 -r shellcheck -x
	git ls-files -z '*.sh' | xargs -0 -r shfmt -d

fmt: ## Format shell scripts
	git ls-files -z '*.sh' | xargs -0 -r shfmt -w
```

## Pitfalls
PROBLEM | CAUSE AND FIX
---|---
`*** missing separator` | Recipe indented with spaces; use a TAB
`make: 'x' is up to date.` | A file called `x` exists; mark the target `.PHONY`
`$VAR` empty in recipe | make expanded it; write `$$VAR` for a shell variable
`cd` has no effect on the next line | Separate shells; chain with `&&` or use `.ONESHELL`
Recipe runs even when it should not | Prerequisite is a phony target or a file that always changes
Editing `.env` does nothing | Make variables are read at start; `export` and `-include` the file
Spaces in filenames break rules | Make splits on whitespace; avoid spaces in paths
`make -j` output interleaves | Add `--output-sync=target` (GNU Make 4+)
`$(shell ...)` runs on every parse | Cache it with `:=`
