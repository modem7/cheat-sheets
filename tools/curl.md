# curl
`curl` transfers data over HTTP(S), FTP and many other protocols. For TLS debugging also see [OpenSSL](openssl.md).

Documentation: [curl Docs](https://curl.se/docs/)

## Common Options
OPTION | DESCRIPTION
---|---
`-s` | Silent (no progress bar)
`-S` | Show errors even when silent (use as `-sS`)
`-f` | Fail on HTTP errors (exit non-zero for 4xx/5xx)
`-L` | Follow redirects
`-o <FILE>` / `-O` | Save to a file / save using the remote name
`-I` | Headers only (HEAD request)
`-i` | Include response headers in output
`-v` | Verbose, shows the request and TLS handshake
`-k` | Skip certificate verification (testing only)
`-H "Name: value"` | Add a header
`-X <METHOD>` | Set the HTTP method
`-d <DATA>` | Send a POST body
`-u <USER>:<PASS>` | Basic auth
`-A "<UA>"` | User agent
`-m <SEC>` | Max total time
`--connect-timeout <SEC>` | Connection timeout
`--retry <N>` | Retry on transient errors
`-C -` | Resume a download
`-w "<FORMAT>"` | Print info after the transfer
`--resolve <HOST>:<PORT>:<IP>` | Override DNS for one request
`-x <PROXY>` | Use a proxy

Reliable script default: `curl -fsSL <URL>`

## Requests
COMMAND | DESCRIPTION
---|---
`curl -fsSL <URL> -o <FILE>` | Download a file
`curl -I <URL>` | Show response headers
`curl -X POST -H "Content-Type: application/json" -d '{"a":1}' <URL>` | POST JSON
`curl --json '{"a":1}' <URL>` | POST JSON (curl 7.82+, sets headers)
`curl -d "a=1&b=2" <URL>` | POST form data
`curl -F "file=@photo.jpg" <URL>` | Upload a file (multipart)
`curl -T file.txt <URL>` | PUT a file
`curl -X DELETE <URL>` | DELETE
`curl -H "Authorization: Bearer <TOKEN>" <URL>` | Bearer token
`curl -u <USER>:<PASS> <URL>` | Basic auth
`curl --cookie-jar jar.txt <URL>` / `--cookie jar.txt` | Save / send cookies
`curl --data-urlencode "q=hello world" <URL>` | URL-encode data
`curl 'https://example.com/file[1-5].txt' -O` | Download a range

## Timing and Diagnostics
COMMAND | DESCRIPTION
---|---
`curl -o /dev/null -sS -w "%{http_code}\n" <URL>` | Print only the status code
`curl -o /dev/null -sS -w "dns:%{time_namelookup} connect:%{time_connect} tls:%{time_appconnect} ttfb:%{time_starttransfer} total:%{time_total}\n" <URL>` | Timing breakdown
`curl -sS -o /dev/null -w "%{redirect_url}\n" <URL>` | Where a redirect goes
`curl -v --http2 <URL>` / `--http1.1` / `--http3` | Force an HTTP version
`curl --tlsv1.2 --tls-max 1.2 <URL>` | Force TLS 1.2
`curl --resolve example.com:443:203.0.113.10 https://example.com` | Test a server before changing DNS
`curl --interface <IF> <URL>` | Use a specific network interface
`curl -4 <URL>` / `-6` | Force IPv4 / IPv6
`curl ifconfig.me` | Your public IP

## With jq
```bash
curl -fsS https://api.github.com/repos/<OWNER>/<REPO>/releases/latest | jq -r .tag_name
```
See [jq](jq.md).

## Config File
`~/.curlrc` applies defaults, for example:
```
--fail
--location
--silent
--show-error
```

## See Also
- [REST APIs](rest-api.md)
