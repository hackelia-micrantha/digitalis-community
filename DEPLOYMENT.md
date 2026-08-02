# Public Site Deployment

The only deployable site root in this repository is `web/`. Publishing the repository root may expose governance files or produce an incorrect site layout.

## Cloudflare Workers Git integration

The production deployment uses Cloudflare Workers static assets. The root `wrangler.jsonc` sets the asset directory to `./web`.

Keep `wrangler.jsonc` at the repository root. Deployment configuration must not be copied into `web/`, because every file under `web/` is part of the public asset boundary.

Configure the Git integration with:

- production branch: `main`;
- root directory: repository root;
- preview deployments enabled for reviewed branches;
- production custom domain: `digitalis.micrantha.com`.

Credentials and account identifiers must remain in Cloudflare or the deployment environment, not in this repository.

## Pre-deployment validation

Run:

```sh
python3 scripts/validate_publication.py
python3 scripts/validate_site.py
```

The validators check the publication root, provenance coverage, required public files, local links and anchors, security metadata, headers, and progressive-enhancement invariants.

## Post-deployment verification

Verify both a branch preview and the production custom domain before considering a deployment complete:

1. `/` renders the Digitalis landing page.
2. `/whitepaper.html` renders correctly.
3. `/.well-known/security.txt` is available and matches its canonical URL.
4. HTML responses contain the CSP, HSTS, framing, content-type, referrer, and permissions headers from `web/_headers`.
5. HTML and security metadata revalidate rather than remaining stale.
6. CSS and JavaScript use the intended short cache policy.
7. The site remains readable with JavaScript disabled.
8. Internal links and fragment navigation work on desktop and mobile widths.
9. An unknown route returns the branded `404.html` with HTTP 404.

Run `python3 scripts/smoke_production.py` or dispatch the Production smoke test workflow after production deployment.

## Rollback

Cloudflare retains prior Worker deployments. If production verification fails, roll back to the last known-good deployment in the Cloudflare dashboard or restore the last known-good commit on `main`.

Do not weaken security headers or publish the repository root as an emergency workaround.
