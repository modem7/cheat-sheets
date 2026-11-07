# REST APIs
Calling and testing HTTP/JSON APIs from the command line with [curl](curl.md) and [jq](jq.md). Use it for homelab and service APIs (for example a UPS wrapper, [Proxmox](../proxmox/proxmox-access-api.md) or the [Claude API](../ai/claude-api.md)).

Documentation: [curl manual](https://curl.se/docs/manpage.html) · [MDN: HTTP methods](https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods)

> **Verification:** Flags checked against the curl man page from memory; not run here. `--json` needs curl 7.82 or later and `--fail-with-body` needs 7.76 or later.

See also: [curl](curl.md) · [jq](jq.md) · [HTTP Status Codes](../misc/http-status-codes.md) · [apcupsd](../homelab/apcupsd.md)

---
## Methods
METHOD | USE | SAFE | IDEMPOTENT
---|---|---|---
`GET` | Read a resource or list | Yes | Yes
`HEAD` | Headers only | Yes | Yes
`POST` | Create, or trigger an action | No | No
`PUT` | Replace a resource | No | Yes
`PATCH` | Partial update | No | Not guaranteed
`DELETE` | Remove a resource | No | Yes
`OPTIONS` | Ask what is allowed (CORS preflight) | Yes | Yes

---
## Requests with curl
COMMAND | DESCRIPTION
---|---
`curl -sS <URL>` | GET, quiet but show errors
`curl -i <URL>` | Include response headers
`curl -I <URL>` | HEAD request
`curl -X DELETE <URL>` | Set the method explicitly
`curl -H 'Accept: application/json' <URL>` | Add a header
`curl --json '{"name":"x"}' <URL>` | POST JSON and set `Content-Type` and `Accept` (7.82+)
`curl -X POST -H 'Content-Type: application/json' -d '{"name":"x"}' <URL>` | POST JSON on older curl
`curl -d @body.json -H 'Content-Type: application/json' <URL>` | Body from a file
`curl -X PUT -H 'Content-Type: application/json' -d @body.json <URL>` | Replace a resource
`curl -X PATCH -H 'Content-Type: application/json' -d '{"a":1}' <URL>` | Partial update
`curl -G --data-urlencode 'q=a b' <URL>` | Add a URL-encoded query string to a GET
`curl -F file=@PATH <URL>` | Multipart file upload
`curl -L <URL>` | Follow redirects
`curl -o out.json <URL>` | Save the body
`curl -K curl.conf` | Read options from a file (keeps secrets out of shell history)

---
## Authentication
STYLE | COMMAND
---|---
Bearer token | `curl -H "Authorization: Bearer $API_TOKEN" <URL>`
Bearer token (curl option) | `curl --oauth2-bearer "$API_TOKEN" <URL>`
Basic auth | `curl -u <USER> <URL>` (curl prompts for the password; or use `--netrc`)
API key in header | `curl -H "X-API-Key: $API_KEY" <URL>`
API key in query | `curl "<URL>?api_key=$API_KEY"` (leaks into logs; avoid)
Client certificate | `curl --cert client.pem --key client.key <URL>`
Custom CA | `curl --cacert ca.pem <URL>`
Skip TLS verification | `curl -k <URL>` (testing only; never in scripts)

Keep tokens in environment variables or a `-K` config file, not in the command line, and rotate any that reach shell history or logs.

---
## Reading Responses
COMMAND | DESCRIPTION
---|---
`curl -s <URL> \| jq .` | Pretty-print JSON
`curl -s <URL> \| jq -r '.items[].name'` | Extract fields as raw text
`curl -s <URL> \| jq 'map(select(.status=="ok"))'` | Filter an array
`curl -s -o /dev/null -w '%{http_code}\n' <URL>` | Print only the status code
`curl -s -o /dev/null -w '%{time_total}\n' <URL>` | Request time in seconds
`curl -fsS <URL>` | Exit non-zero on HTTP 4xx/5xx, still show errors
`curl --fail-with-body -sS <URL>` | Same, but print the error body (7.76+)
`curl -s -D - -o /dev/null <URL>` | Print headers only

---
## Reliability
OPTION | MEANING
---|---
`--connect-timeout 5` | Seconds allowed to connect
`-m 30` / `--max-time 30` | Total time limit
`--retry 3` | Retry transient failures
`--retry-delay 2` | Seconds between retries
`--retry-all-errors` | Retry on any error, not just transient ones (7.71+; only for idempotent calls)

Retry only idempotent requests (`GET`, `PUT`, `DELETE`). A retried `POST` can create duplicates unless the API supports an idempotency key.

---
## Pagination
PATTERN | EXAMPLE
---|---
Page and size | `?page=2&per_page=100`
Offset and limit | `?offset=200&limit=100`
Cursor | `?cursor=<NEXT_CURSOR>` taken from the previous response
`Link` header | `Link: <URL>; rel="next"`: follow `next` until absent

Loop on a cursor:
```bash
cursor=""
while :; do
  resp=$(curl -fsS -H "Authorization: Bearer $API_TOKEN" "https://api.example.com/items?cursor=$cursor")
  echo "$resp" | jq -c '.items[]'
  cursor=$(echo "$resp" | jq -r '.next_cursor // empty')
  [ -n "$cursor" ] || break
done
```

---
## Status Codes
RANGE | MEANING | ACT
---|---|---
`2xx` | Success (`200`, `201` created, `204` no content) | Use the result
`3xx` | Redirect | Add `-L`, check the new URL
`400` / `422` | Bad request or invalid body | Fix the payload
`401` | Not authenticated | Check the token or header
`403` | Authenticated but not allowed | Check scopes and permissions
`404` | Not found | Check the path and ID
`409` | Conflict | Re-read the resource, then retry
`429` | Rate limited | Honour `Retry-After`, back off
`5xx` | Server error | Retry with back-off if idempotent

Full list: [HTTP Status Codes](../misc/http-status-codes.md).

---
## Design Conventions
- Nouns in paths, plural collections: `/users`, `/users/42`.
- Method carries the verb; avoid `/getUser`.
- Version the API: `/v1/...` or an `Accept` header.
- Return the right status code and a JSON error body with a message.
- Support filtering, sorting and pagination on list endpoints.
- Use HTTPS and short-lived tokens.

---
## Troubleshooting
SYMPTOM | CHECK
---|---
`401 Unauthorized` | Header name and the `Bearer` prefix (with a space after it); token expired
`415 Unsupported Media Type` | Add `-H 'Content-Type: application/json'`
`400` on a valid-looking body | Shell quoting; send from a file with `-d @body.json`
Empty output, exit code 0 | `-s` hides errors; use `-sS`, and `-i` to see the status
`curl: (60)` certificate error | Wrong CA or self-signed cert: use `--cacert`, not `-k`
`curl: (7)` connection refused | Service down, wrong port or firewall
Response not JSON | Redirect to a login page: add `-i` and check `Location`
`jq: parse error` | Body is HTML or empty; inspect it before piping to `jq`
