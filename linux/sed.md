# SED Cheat-Sheet
**sed** ("stream editor") is a **[Linux](linux.md)** and Unix utility that parses and transforms text using a compact programming language. See also **[Grep](grep.md)** and **[Awk](awk.md)**.

> On macOS (BSD sed) use `sed -i ''` instead of `sed -i`.

## Substitution
COMMAND | DESCRIPTION
---|---
`sed 's/old/new/' file` | Replace first match on each line
`sed 's/old/new/g' file` | Replace all matches on each line
`sed -i 's/old/new/g' file` | Edit the file in place
`sed -i.bak 's/old/new/g' file` | Edit in place and keep a `.bak` backup
`sed 's/old/new/2' file` | Replace only the 2nd match on each line
`sed 's/old/new/gI' file` | Case-insensitive replace (GNU sed)
`sed 's\|/usr/local\|/opt\|g' file` | Use another delimiter when the pattern contains `/`
`sed -E 's/([a-z]+)@([a-z]+)/\2 at \1/' file` | Extended regex with capture groups
`sed 's/.*/\U&/' file` | Uppercase each line (GNU sed)
`sed 's/[ \t]*$//' file` | Strip trailing whitespace

## Print, Delete and Select Lines
COMMAND | DESCRIPTION
---|---
`sed -n '5p' file` | Print line 5
`sed -n '5,10p' file` | Print lines 5 to 10
`sed -n '/start/,/end/p' file` | Print between two patterns
`sed -n '$p' file` | Print the last line
`sed '5d' file` | Delete line 5
`sed '/^#/d' file` | Delete comment lines
`sed '/^$/d' file` | Delete empty lines
`sed '1d;$d' file` | Delete first and last lines
`sed -n '/error/{p;q}' file` | Print first match then quit

## Insert and Append
COMMAND | DESCRIPTION
---|---
`sed '3i\New line' file` | Insert before line 3
`sed '3a\New line' file` | Append after line 3
`sed '/pattern/a\New line' file` | Append after matching lines
`sed '1i\#!/bin/bash' file` | Add a line at the top
`sed '$a\New last line' file` | Add a line at the end
`sed 's/^/    /' file` | Indent every line by 4 spaces
`sed '/pattern/c\Replacement line' file` | Replace the whole matching line

## Multiple Commands
COMMAND | DESCRIPTION
---|---
`sed -e 's/a/b/' -e 's/c/d/' file` | Chain expressions
`sed 's/a/b/;s/c/d/' file` | Same, with `;`
`sed -f script.sed file` | Read commands from a file
`sed = file \| sed 'N;s/\n/\t/'` | Number lines
