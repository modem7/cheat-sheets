# Cloudflare Pages and Workers
Cloudflare Pages hosts static sites (with optional Functions) from a Git repo or a direct upload, and Workers runs JavaScript at the edge. Both use the `wrangler` CLI. Account setup, tokens, Tunnel and R2 are in [Cloudflare](cloudflare.md).

Documentation: [Pages](https://developers.cloudflare.com/pages/) · [Workers](https://developers.cloudflare.com/workers/) · [Wrangler commands](https://developers.cloudflare.com/workers/wrangler/commands/) · [Workers limits](https://developers.cloudflare.com/workers/platform/limits/)

> **Verification:** commands and config were read on developers.cloudflare.com (one page each) and not run here. Marked *(unverified)* where a page did not confirm it.

## Pages or Workers
Cloudflare's docs do not call Pages deprecated, but they steer new projects towards Workers, which has a broader feature set, and publish a migration guide. Workers static assets supports `_headers` and `_redirects` natively. A "Workers is recommended for all new projects" statement was only seen in secondary sources *(unverified)*.

## Pages: Wrangler
COMMAND | DESCRIPTION
---|---
`wrangler pages project create <NAME> --production-branch main` | Create a project
`wrangler pages project list` | List projects (`--json` available)
`wrangler pages deploy <DIR> --project-name <PROJECT> --branch <BRANCH>` | Direct upload deploy
`wrangler pages deployment list --project-name <PROJECT>` | List deployments (`--environment` to filter)
`wrangler pages deployment tail --project-name <PROJECT>` | Stream logs (production by default)
`wrangler pages secret put <KEY> --project-name <PROJECT>` | Set a secret
`wrangler pages dev <DIR>` | Run locally (`--port`, `--kv`, `--d1`, `--r2`, `--binding`)
`wrangler pages download config <PROJECT>` | Download a project's config

## Pages: Git Builds
FRAMEWORK | BUILD COMMAND | OUTPUT DIRECTORY
---|---|---
Vite, React, Vue | `npm run build` | `dist`
Astro | `npm run build` | `dist`
Hugo | `hugo` | `public`
No framework | leave blank or `exit 0` | the folder with your files

- Root directory defaults to the repo root. Set it for a monorepo.
- Set `NODE_VERSION` as an environment variable, or use `.nvmrc` or `.node-version`.
- System variables available in builds: `CF_PAGES`, `CF_PAGES_BRANCH`, `CF_PAGES_COMMIT_SHA`, `CF_PAGES_URL`.
- The production branch defaults to the first branch you push. Other branches build as previews, and include and exclude rules accept `*` (excludes are evaluated first).
- Older build images are being retired: v1 projects move to v3 on 2026-09-15 and v2 on 2027-02-23.
- Preview URL format: *(unverified)*.

## Pages: Custom Domains
- Add the domain in the dashboard **first**, or you get a 522.
- Apex domain: the zone must be on Cloudflare with its nameservers.
- Subdomain: CNAME to `<SITE>.pages.dev`.

## Pages: wrangler.jsonc
```jsonc
{
  "name": "my-site",
  "pages_build_output_dir": "./dist",
  "compatibility_date": "2026-01-01"
}
```

`main` does not apply. Only `env.production` and `env.preview` exist. Once the file is used, the dashboard settings become read-only.

## Pages: `_redirects` and `_headers`
Put both files in the build output directory.

```text
# _redirects: SOURCE DESTINATION [CODE]
/old-page  /new-page  301
/blog/*    /news/:splat  302
```

```text
# _headers: URL line, then indented headers
/*
  X-Frame-Options: DENY
  X-Content-Type-Options: nosniff
```

FILE | RULES
---|---
`_redirects` | Default code 302. Allowed 301, 302, 303, 307, 308, and 200 (proxy, same-site relative URLs only). 2,000 static plus 100 dynamic rules, 1,000 characters per line. One `*` splat per rule (`:splat`), placeholders `:name`. No query-string matching. Not applied to requests handled by Functions
`_headers` | 100 rules, 2,000 characters per line. Supports `*`, `:splat` and `:name`. `! Header-Name` removes a header. Not applied to Functions or `_worker.js` responses

## Pages: Functions
Files under `functions/` become routes.

PATH | ROUTE
---|---
`functions/fruits/apple.js` | `/fruits/apple`
`functions/fruits/[id].js` | One path segment
`functions/fruits/[[id]].js` | Any depth
`functions/_middleware.js` | Runs before routes (can export an array of handlers)

Export `onRequest`, or a method form: `onRequestGet`, `onRequestPost`, `onRequestPut`, `onRequestPatch`, `onRequestDelete`, `onRequestHead`, `onRequestOptions`.

`_routes.json` limits which paths invoke Functions:

```json
{
  "version": 1,
  "include": ["/api/*"],
  "exclude": ["/api/static/*"]
}
```

`exclude` wins. Limits: 100 rules combined, 100 characters per rule.

## Workers: Wrangler
COMMAND | DESCRIPTION
---|---
`wrangler dev` | Run locally (`--remote` runs on Cloudflare, `--test-scheduled` exposes the cron test route)
`wrangler deploy` | Deploy the Worker
`wrangler tail [WORKER]` | Stream logs (`--format`, `--status`, `--search`)
`wrangler versions upload` | Upload a version without deploying it (`--tag`, `--message`)
`wrangler versions deploy <ID>@10% <ID2>@90% -y` | Gradual rollout between versions
`wrangler rollback [VERSION_ID]` | Roll back to a previous version
`wrangler secret put <KEY>` | Set a secret (`list` and `delete` also exist)
`wrangler types` | Write `worker-configuration.d.ts` (`--check` verifies it)
`wrangler d1 create <NAME>` | Create a D1 database
`wrangler d1 execute <DB> --command "<SQL>" --remote` | Run SQL (`--file`, or `--local`)
`wrangler d1 migrations apply <DB>` | Apply migrations (`create` and `list` also exist)

## Workers: wrangler.jsonc
```jsonc
{
  "name": "my-worker",
  "main": "src/index.js",
  "compatibility_date": "2026-01-01",
  "assets": { "directory": "./public", "not_found_handling": "single-page-application" },
  "routes": [{ "pattern": "app.example.com", "custom_domain": true }],
  "vars": { "ENVIRONMENT": "production" },
  "kv_namespaces": [{ "binding": "CACHE", "id": "<KV_ID>" }],
  "r2_buckets": [{ "binding": "FILES", "bucket_name": "my-bucket" }],
  "d1_databases": [{ "binding": "DB", "database_name": "my-db", "database_id": "<D1_ID>" }],
  "triggers": { "crons": ["*/3 * * * *"] }
}
```

- `name` cannot contain underscores.
- `not_found_handling` takes `single-page-application`, `404-page` or `none`. `run_worker_first` sends requests to the Worker before assets.
- Routes can also be `{ "pattern": "...", "zone_name": "example.com" }`.

## Workers: Handlers
```js
export default {
  async fetch(request, env, ctx) {
    return new Response("ok");
  },
  async scheduled(controller, env, ctx) {
    // runs on each cron trigger
  },
};
```

The `fetch` form is the standard shape but its docs page was not fetched *(unverified)*. Test a cron locally with `wrangler dev --test-scheduled`, then:

```bash
curl "http://localhost:8787/cdn-cgi/local/scheduled?cron=*+*+*+*+*"
```

## Free Plan Limits
LIMIT | FREE PLAN
---|---
Requests | 100,000 per day, resetting at 00:00 UTC. Over the limit returns Error 1027
CPU time | 10 ms per HTTP request
Subrequests | 50 per invocation
Workers per account | 100
Memory | 128 MB

The paid plan allows 30 s CPU by default, up to 5 minutes. Check [Workers limits](https://developers.cloudflare.com/workers/platform/limits/) before relying on these numbers.

## See Also
- [Cloudflare](cloudflare.md)
- [Cloudflare Speed Test](cloudflare-speed-test.md)
- [Cloudflare Tunnel Recipe](../../recipes/expose-service-cloudflare-tunnel.md)
