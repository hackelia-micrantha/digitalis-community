# QART-01: Repository and Product Boundaries

**Status:** Recommended and recorded by ADRs 0001, 0002, and 0006  
**Scope:** `digitalis`, `digitalis-community`, and `cloudflare-play-integrity`

## Questions

1. Which repository is authoritative for implementation?
2. Is `ryjen/cloudflare-play-integrity` a separate product, reusable component, historical prototype, or predecessor Digitalis service?
3. Which repository owns the public website and public artifacts?
4. How should source be published without creating divergent copies?
5. Should Digitalis maintain both Express and Cloudflare verification implementations?
6. Should the Cloudflare Worker remain the primary hosted product runtime?

## Security invariant

There must be exactly one authoritative implementation of each security-critical verifier and protocol rule. Public publication must not create a second editable implementation source. The Themis-to-Digitalis transition must not create parallel supported services.

## Existing evidence

- `digitalis` contains the RFC suite, backend prototype, schema, SDK placeholders, and a copied site.
- `digitalis-community` contains the same public site source plus a public security contact.
- `cloudflare-play-integrity`, internally Themis, contains an earlier functional Google OAuth and token-decode path running as a Cloudflare Worker.
- The current Digitalis Google provider is newer but less strict than Themis.
- The user intends Themis to be reworked and rebranded into Digitalis while retaining Cloudflare Workers as the preferred hosted runtime.
- The private and public sites are exact copies, and schema source is duplicated between documentation and runtime paths.

## Alternatives

### A. Keep all three repositories and products independent

Each repository and verifier evolves on its own.

**Advantages**

- no migration work;
- small repositories remain simple;
- Themis can continue to deploy independently.

**Risks**

- duplicate security fixes;
- protocol and policy drift;
- unclear product identity;
- competing Themis and Digitalis services;
- public site drift;
- difficult provenance and conformance.

### B. Replace Themis with a generic Digitalis backend

Build Digitalis around the Express service and treat the Worker as disposable prior art.

**Advantages**

- familiar centralized service architecture;
- one private repository can contain all implementation.

**Risks**

- discards the strongest working provider and deployment lineage;
- loses the intended Themis-to-Digitalis product continuity;
- entrenches an unsafe and highly coupled Express prototype;
- delays a real hosted verification path.

### C. Rebuild and rebrand Themis as the Digitalis Cloudflare service

`hackelia-micrantha/digitalis` is authoritative for architecture, protocol, policy, SDKs, conformance, and the supported service implementation. The Themis code and deployment lineage are corrected and evolved into the first-party Digitalis Cloudflare Worker. Public content is published one-way into `digitalis-community`.

The repository transition may be a history-preserving rename/move or a migration into `digitalis` with the old repository retained as a redirect and provenance record.

**Advantages**

- one verifier and one supported service;
- preserves product and Git provenance;
- keeps Cloudflare Workers as the primary hosted runtime;
- clear private/public boundary;
- supports runtime-neutral testing and later portability without weakening the Worker-first product;
- prevents public/private source drift.

**Risks**

- requires redesign, rebrand, and attribution work;
- repository transition mechanics must be selected;
- publication automation must be maintained;
- runtime-neutral package boundaries must be designed inside a Worker-first service.

## Recommendation

Select alternative C.

### Repository and product ownership

`hackelia-micrantha/digitalis` owns:

- the Digitalis product identity;
- protocol and schemas;
- provider and policy packages;
- the first-party Cloudflare Worker service;
- control-plane interfaces and records;
- SDKs and reference applications;
- conformance and release assurance;
- private architecture and implementation documentation.

`hackelia-micrantha/digitalis-community` owns:

- public website;
- public disclosure and security-contact material;
- public generated documentation and release metadata;
- future community artifacts explicitly selected for publication.

`ryjen/cloudflare-play-integrity` / Themis is:

- the predecessor Digitalis service and implementation lineage;
- a source of Worker deployment knowledge, code, and provenance;
- transitioned through a history-preserving rename/move or a documented migration;
- not maintained as a separate competing verifier after the Digitalis cutover;
- archived only when an active replacement location and redirect preserve discoverability and history.

### Runtime ownership

- Cloudflare Workers is the primary first-party hosted verification runtime for Digitalis v1.
- Provider, policy, protocol, and canonical serialization remain runtime-neutral packages.
- Runtime neutrality supports testing and later adapters; it does not demote the Worker to a disposable example.
- Express must not retain a second independent Google provider or policy implementation.

### Source publication

- remove the private copied site or treat it as a generated staging artifact;
- publish through a one-way workflow with explicit source commit metadata;
- generate schema documentation from authoritative migrations or protocol schemas;
- prohibit hand-maintained duplicate security contracts.

## Tradeoffs

- A Worker-first product creates some Cloudflare dependency, but it preserves the existing deployment direction and accelerates a credible real-provider path.
- Runtime-neutral core packages add internal structure, but they prevent security logic from being trapped in HTTP handlers and permit later supported runtimes.
- A history-preserving repository rename is operationally simple but may conflict with the existing Digitalis repository; a migration provides cleaner consolidation but requires stronger provenance documentation.
- The old Themis repository may eventually be archived, but the Themis product lineage is not discarded—it becomes Digitalis.

## Decisions

- **QART-0001:** `digitalis` is the authoritative engineering and product repository.
- **QART-0002:** `digitalis-community` is the public publication boundary and does not independently maintain copied implementation source.
- **QART-0003:** Themis is the predecessor Digitalis Cloudflare service and will be rebuilt and rebranded, not treated merely as disposable historical code.
- **QART-0004:** Google verification is implemented once as a shared provider package consumed by the first-party Digitalis Worker and any future supported runtime.
- **QART-0005:** Public publication is one-way, reproducible, and records source provenance.

## Validation

- repository and product ownership are documented;
- the supported service is branded Digitalis and deployed on Cloudflare Workers;
- copied site source is removed from the private repository or generated automatically;
- schema duplication is replaced by migrations and generated documentation;
- only one package contains Google verdict interpretation;
- only one first-party hosted verification service is supported;
- Themis-to-Digitalis source, release, and repository provenance are preserved;
- any archived predecessor repository points clearly to the active Digitalis service.
