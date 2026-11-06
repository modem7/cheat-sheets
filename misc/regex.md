# Regex
Regular expressions describe text patterns. The core is shared everywhere, but the details (escaping, `\d`, lookaround, backreferences) differ by flavour, so check which engine you are actually talking to. Tools that use them: [Grep](../linux/grep.md), [SED Cheat-Sheet](../linux/sed.md), [AWK](../linux/awk.md), [jq](../tools/jq.md) and every programming language.

Documentation: [regular-expressions.info](https://www.regular-expressions.info/), [PCRE2 syntax](https://www.pcre.org/current/doc/html/pcre2syntax.html), [RE2 syntax](https://github.com/google/re2/wiki/Syntax), [Python `re`](https://docs.python.org/3/library/re.html), [MDN regular expressions](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Regular_expressions)

## Anchors and Boundaries
PATTERN | DESCRIPTION
---|---
`^` / `$` | Start / end of line (of the whole string unless a multiline flag is set)
`\A` / `\z` | Start / end of the whole string (PCRE, Python `\A`, RE2; not JS, not POSIX)
`\b` / `\B` | Word boundary / not a word boundary (GNU grep and sed also support these)
`\<` / `\>` | Start / end of a word (GNU grep, sed, awk; not PCRE)

## Character Classes
PATTERN | DESCRIPTION
---|---
`.` | Any character except newline (any character with the dotall flag)
`[abc]` / `[^abc]` | One of / none of
`[a-z0-9_-]` | Ranges; put `-` last or escape it
`\d` / `\D` | Digit / non-digit (not POSIX)
`\w` / `\W` | Word character `[A-Za-z0-9_]` / not
`\s` / `\S` | Whitespace / non-whitespace
`[[:alpha:]]` `[[:digit:]]` `[[:alnum:]]` | POSIX classes, valid inside a bracket expression in every flavour
`[[:space:]]` `[[:upper:]]` `[[:lower:]]` `[[:punct:]]` | More POSIX classes
`\p{L}` / `\p{Lu}` | Unicode letter / uppercase (PCRE, Python `regex` module, JS with `u`, RE2 `\pL`)
`\h` / `\R` | Horizontal whitespace / any newline sequence (PCRE only)

## Quantifiers
PATTERN | DESCRIPTION
---|---
`*` | Zero or more (greedy)
`+` | One or more (greedy)
`?` | Zero or one
`{n}` / `{n,}` / `{n,m}` | Exactly n / at least n / between n and m
`*?` `+?` `??` `{n,m}?` | Lazy: match as little as possible (PCRE, JS, Python, RE2; not POSIX)
`*+` `++` `?+` | Possessive: never give back (PCRE, Java, Python 3.11+; not JS, not RE2)
`(?>...)` | Atomic group, same idea (PCRE, Python 3.11+)

## Groups and Backreferences
PATTERN | DESCRIPTION
---|---
`(...)` | Capturing group, numbered from 1 by opening bracket
`(?:...)` | Non-capturing group
`(?<name>...)` | Named group (PCRE, JS, Go 1.22+, Rust; Python needs `(?P<name>...)`)
`(?P<name>...)` | Named group (Python, PCRE, Go/RE2)
`\1` | Backreference to group 1 (not in RE2/Go or Rust)
`\k<name>` / `(?P=name)` | Named backreference (PCRE, JS / Python)
`a\|b` | Alternation
`$1` / `\1` / `\g<1>` | Group in the replacement: JS, Rust, Go `${1}` / sed, PCRE tools / Python
`\K` | Reset match start, drop what came before (PCRE only; handy with `grep -oP`)

## Lookaround
Zero-width assertions, supported in PCRE, JS and Python. **Not** in POSIX, RE2, Go or Rust (use a second pass or a different approach).

PATTERN | DESCRIPTION
---|---
`foo(?=bar)` | Positive lookahead: `foo` followed by `bar`
`foo(?!bar)` | Negative lookahead
`(?<=\$)\d+` | Positive lookbehind: digits preceded by `$`
`(?<!\$)\d+` | Negative lookbehind
`^(?=.*\d)(?=.*[a-z]).{8,}$` | Several conditions at once (at least 8 chars, a digit and a lowercase letter)

Lookbehind length rules: Python needs fixed width, PCRE needs each alternative fixed width, JavaScript allows variable width.

## Flags
FLAG | DESCRIPTION
---|---
`i` | Case-insensitive
`m` | Multiline: `^` and `$` match at each line
`s` | Dotall: `.` also matches newline
`x` | Extended: ignore whitespace and allow `#` comments
`g` | Global (JS, and `sed s///g`): all matches, not just the first
`u` | Unicode mode (JS)
`(?i)` `(?s)` `(?m)` `(?x)` | Inline flags at the start of the pattern (PCRE, Python, Go/RE2, Rust; not JS)
`(?i:...)` | Flag scoped to a group (PCRE, Python, Go/RE2)
`re.I` `re.M` `re.S` `re.X` | Python flag constants, combine with `\|`

## Flavour Comparison
FLAVOUR | NOTES
---|---
POSIX BRE | `grep`, `sed` default. `\(` `\)` `\{` `\}` are the special forms; `+ ? \|` are literal unless GNU `\+ \? \|`
POSIX ERE | `grep -E`, `sed -E`, `awk`. `( ) { } + ? \|` are special unescaped. No `\d`, no lazy, no backrefs in strict POSIX (GNU adds `\1`)
PCRE / PCRE2 | `grep -P`, PHP, `rg -P`, nginx. Full feature set: lookaround, lazy, possessive, atomic, `\K`, recursion
JavaScript | Lookbehind (ES2018), named groups, `d` flag for indices, `\d` is ASCII only. No possessive, no atomic, no inline flags
Python `re` | `(?P<name>)`, `re.fullmatch`, fixed-width lookbehind, possessive and atomic since 3.11. Use the third-party `regex` module for more
RE2 / Go / Rust | Linear-time guarantee, so **no backreferences and no lookaround**. Lazy quantifiers and Unicode classes are fine. Go: `regexp`; `rg` uses the Rust engine

## grep, sed and awk
COMMAND | DESCRIPTION
---|---
`grep 'a\+b'` | BRE (GNU extension `\+`)
`grep -E 'a+b\|c'` | ERE, same as the obsolete `egrep`
`grep -P '\d+(?=px)'` | PCRE (GNU grep only; macOS grep has no `-P`)
`grep -oP 'id=\K\d+'` | Print only the part after `\K`
`grep -oE '[0-9]{1,3}(\.[0-9]{1,3}){3}'` | Extract IPv4-looking strings
`grep -Pzo '(?s)BEGIN.*?END'` | Multi-line match (`-z` treats the file as one line)
`grep -F 'a.b'` | Fixed string, no regex at all (fastest and safest for literals)
`sed -E 's/([a-z]+)-([0-9]+)/\2-\1/'` | ERE with backreferences in the replacement
`sed 's/\(a\)\(b\)/\2\1/'` | BRE: groups need backslashes
`awk '/^ERROR/ && $3 ~ /^[0-9]+$/'` | `~` matches, `!~` negates (POSIX ERE)
`awk 'match($0, /[0-9]+/) { print substr($0, RSTART, RLENGTH) }'` | Extract a match
`rg '\d+'` | ripgrep: Rust regex, no lookaround or backrefs
`rg -P '(?<=x)\d+'` | ripgrep with PCRE2 (`--pcre2`)
`rg -o -r '$1' 'id=(\d+)'` | Print only group 1

Notes:
- `sed` and `awk` have no lazy quantifiers or lookaround. Use `[^"]*` instead of `.*?` (for example `"[^"]*"`).
- GNU sed supports `\w`, `\s` and `\b` as extensions but has no `\d`. Prefer `[0-9]` and `[[:space:]]` in portable scripts.
- `awk` flavours differ: gawk has `\y` for word boundaries and `\s`; mawk (the Debian/Ubuntu default `awk`) is plainer.
- The shell quoting matters as much as the regex: always single-quote patterns.

## Common Patterns
These are practical filters, not validators.

WHAT | PATTERN (PCRE/JS style)
---|---
IPv4 | `\b(?:(?:25[0-5]\|2[0-4]\d\|1\d\d\|[1-9]?\d)\.){3}(?:25[0-5]\|2[0-4]\d\|1\d\d\|[1-9]?\d)\b`
IPv4 (loose) | `\b\d{1,3}(?:\.\d{1,3}){3}\b`
Port | `\b(?:[0-9]\|[1-9]\d{1,3}\|[1-5]\d{4}\|6[0-4]\d{3}\|65[0-4]\d{2}\|655[0-2]\d\|6553[0-5])\b`
MAC address | `\b(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b`
UUID | `\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b`
ISO date | `\b\d{4}-(?:0[1-9]\|1[0-2])-(?:0[1-9]\|[12]\d\|3[01])\b`
Time HH:MM:SS | `\b(?:[01]\d\|2[0-3]):[0-5]\d:[0-5]\d\b`
Semver (loose) | `\bv?\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?\b`
Semver (official) | `^(0\|[1-9]\d*)\.(0\|[1-9]\d*)\.(0\|[1-9]\d*)(?:-((?:0\|[1-9]\d*\|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0\|[1-9]\d*\|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$`
URL (http/https) | `https?://[^\s/$.?#][^\s]*`
Email (sanity check) | `[^@\s]+@[^@\s]+\.[^@\s]+`
Hex colour | `#(?:[0-9a-fA-F]{3}){1,2}\b`
Blank line | `^\s*$`
Trailing whitespace | `[ \t]+$`
Duplicate word | `\b(\w+)\s+\1\b`

Caveats:
- **Email**: the real grammar (RFC 5322) is not regular in any practical sense. Use the loose pattern to catch typos, then confirm by sending a message.
- **IPv4** with dots unescaped (`1.2.3.4`) also matches `1x2y3z4`; always escape `\.`. Regex cannot tell you that `10.0.0.256` is invalid unless you use the strict pattern above.
- **Dates**: the pattern accepts `2026-02-31`. Validate the calendar in code.
- **URLs**: strip trailing punctuation (`.`, `)`, `,`) in prose, or use a proper URL parser.
- **Never parse HTML or nested structures** (JSON, YAML) with a regex. Use [jq](../tools/jq.md) or a real parser.

## Performance and Safety
- Nested quantifiers such as `(a+)+$` can backtrack exponentially (ReDoS) in backtracking engines (PCRE, JS, Python). Prefer possessive or atomic groups, anchor patterns, or use a linear engine (RE2/Go/Rust) for untrusted input.
- Prefer specific classes (`[^"]*`) to `.*` plus lazy.
- Remember greedy `.*` is the usual cause of "matched too much".
- Escape user input before building a pattern: `re.escape()` (Python), `regexp.QuoteMeta` (Go), `grep -F` for plain strings.

## Testing
COMMAND | DESCRIPTION
---|---
[regex101.com](https://regex101.com/) | Pick the flavour (PCRE2, JS, Python, Go), explanation, match info and a debugger
[regexr.com](https://regexr.com/) | JavaScript flavour with a cheat sheet
[debuggex.com](https://www.debuggex.com/) | Railroad diagrams
`echo 'text' \| grep -P '<REGEX>'` | Quick PCRE test (`-o` for matches only)
`echo 'text' \| rg '<REGEX>'` | Rust engine
`python3 -c "import re,sys; print(re.findall(r'<REGEX>', sys.argv[1]))" 'text'` | Python test
`node -e "console.log('text'.match(/<REGEX>/g))"` | JavaScript test
`sed -nE 's/<REGEX>/[&]/p'` | Show where an ERE matches (`&` is the whole match)
