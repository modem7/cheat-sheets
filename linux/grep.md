# Grep
Grep is a command-line utility for searching plain-text data for lines matching a regular expression. Its name comes from the ed command `g/re/p` (globally search for a regular expression and print). It is available on **[Linux](linux)** and all Unix-like systems. See also **[Sed](sed)** and **[Awk](awk)**.

## Common Options
OPTION | DESCRIPTION
---|---
`-i` | Ignore case
`-v` | Invert match (lines that do NOT match)
`-r` / `-R` | Recurse into directories (`-R` follows symlinks)
`-n` | Show line numbers
`-c` | Count matching lines
`-l` / `-L` | List files with / without matches
`-w` | Match whole words only
`-x` | Match whole lines only
`-o` | Print only the matched part
`-h` | Hide file names
`-A <N>` / `-B <N>` / `-C <N>` | Show N lines after / before / around a match
`-E` | Extended regex (same as `egrep`)
`-F` | Fixed strings, no regex (fastest)
`-P` | Perl-compatible regex (lookaheads, `\d`, `\K`)
`-q` | Quiet, only set the exit code
`-m <N>` | Stop after N matches
`--include=<GLOB>` / `--exclude=<GLOB>` | Filter files by name
`--exclude-dir=<DIR>` | Skip a directory
`--color=auto` | Highlight matches

## Examples
COMMAND | DESCRIPTION
---|---
`grep -rn "TODO" .` | Find TODOs with file and line number
`grep -rIl "password" /etc 2>/dev/null` | List text files mentioning a word, skip binaries
`grep -v '^\s*#' file.conf \| grep -v '^\s*$'` | Show config without comments and blank lines
`grep -E "error\|warn" app.log` | Match either word
`grep -ow "[0-9]\{1,3\}\(\.[0-9]\{1,3\}\)\{3\}" file` | Extract IPv4-looking strings
`grep -Po '(?<=version=)\S+' file` | Print text after a prefix (lookbehind)
`grep -rn --include="*.py" "import os" .` | Search only Python files
`grep -C 3 "Exception" app.log` | Match with 3 lines of context
`grep -c "" file` | Count lines in a file
`grep -f patterns.txt file` | Use patterns from a file
`ps aux \| grep [n]ginx` | Search processes without matching grep itself
`docker logs <CONTAINER> 2>&1 \| grep -i error` | Filter container logs (stderr must be merged)

## Regex Quick Reference
PATTERN | MEANING
---|---
`.` | Any single character
`^` / `$` | Start / end of line
`*` `+` `?` | 0 or more / 1 or more / 0 or 1 (`+` and `?` need `-E`)
`{n,m}` | Between n and m repeats (`-E`)
`[abc]` / `[^abc]` | Character in / not in the set
`[[:digit:]]` `[[:space:]]` `[[:alpha:]]` | POSIX classes
`(a\|b)` | Alternation (`-E`)
`\b` | Word boundary
