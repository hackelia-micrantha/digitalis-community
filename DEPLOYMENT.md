# Public Site Deployment

The only deployable site root in this repository is `web/`. Publishing the repository root may expose governance files or produce an incorrect site layout.

## Cloudflare Pages with Git integration

Configure the Pages project in the Cloudflare dashboard with:

- production branch: `main`;
- build command: none;
- build output directory: `web`;
- root directory: repository root;
- preview deployments: enabled for reviewed branches as appropriate.

The dashboard setting is external state. `wrangler.jsonc` does not automatically update the build output directory for an existing Git-integrated Pages project.

## Wrangler or direct upload

`wrangler.jsonc` defines:

```json
{
  "name": "digitalis-community",
  "pages_build_output_dir": "./web"
}
```

A direct deployment should publish the same directory, for example:

```sh
npx wrangler pages deploy web --project-name=digitalis-community
```

Credentials and account identifiers must be stored in the deployment environment, not committed to this repository.

## Pre-deployment validation

Run:

```sh
python3 scripts/validate_site.py
```

The validator checks the publication root, required public files, local links and anchors, security metadata, headers, and progressive-enhancement invariants.

## Post-deployment verification

Verify both the `pages.dev` preview and the custom domain before considering a deployment complete:

1. `/` renders the Digitalis landing page.
2. `/whitepaper.html` renders correctly.
3. `/.well-known/security.txt` is available and matches its canonical URL.
4. HTML responses contain the CSP, HSTS, framing, content-type, referrer, and permissions headers from `web/_headers`.
5. HTML and security metadata revalidate rather than remaining stale.
6. CSS and JavaScript use the intended short cache policy.
7. The site remains readable with JavaScript disabled.
8. Internal links and fragment navigation work on desktop and mobile widths.

## Rollback

Cloudflare Pages retains prior deployments. If a production deployment fails verification, promote the last known-good deployment or roll back the production branch deployment before investigating further.

Do not weaken the security headers or publish the repository root as an emergency workaround.
