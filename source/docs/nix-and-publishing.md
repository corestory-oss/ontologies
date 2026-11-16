# Nix builds and static documentation

**Repository access required.** These maintainer commands require an authorized, complete checkout, including `flake.nix`, `flake.lock`, `nix/`, and website build assets. The browsable public source collection is a reference subset, not that checkout. To validate a downloaded example without repository access, use [Getting started](getting-started.md).

The repository build commands use Nix. Python remains the implementation language, but a normal build does not invoke uv, pip, or a local virtual environment.

## The everyday commands

```sh
nix build                     # Build static documentation; result/ points to it
nix run .#preview             # Build and serve it locally; Ctrl-C stops it
nix flake check               # Run RDF, composition, projection and site checks
nix build .#ontologies        # Build just the Turtle distributions
nix run .#prepare-site        # Populate local site from committed main; never push
```

`nix build` puts the completed artifact in the Nix store and creates a `result` symlink in your checkout. `result/` contains the prose homepage, the Garden browser in `reference/`, JavaScript, CSS, fonts, ontology JSON, HTML guides, source downloads and Turtle distributions. It is a directory of static files, not a running service.

`nix run .#preview` is a convenience application supplied by this repository. The `preview` name is our choice; `nix run` is the standard Nix mechanism for running such a named application. It starts an ordinary foreground HTTP server bound to `127.0.0.1:4173`. That server exists only for local preview and stays up until Ctrl-C or the terminal closes. The preview disables HTTP caching, including timestamp-based 304 responses: Nix normalizes file timestamps, which would otherwise let browsers reuse an older dataset. It does not watch files or rebuild automatically; restart the command after editing. To use another port, run `nix run .#preview -- 8080`.

`nix flake check` runs finite checks and exits. It does not start a long-lived server. CI invokes `nix flake check` directly. Its checks include the static site build and validation, so there is no separate CI build script or artifact-copy step. Publication stays local.

## direnv and the development shell

Like Plot, this repository has an `.envrc` containing `use flake`. If your existing direnv/nix-direnv setup is active, run this once in the checkout:

```sh
direnv allow
```

This explicitly trusts this directory's environment configuration. Afterward, entering the directory loads the pinned development tools; leaving restores your previous environment. It does not build or serve the documentation automatically.

Without direnv, run `nix develop`. This opens a shell with the same Python/RDF tooling and Nix formatter. Inside either environment, maintainers can run `python scripts/build_rdf.py` to refresh committed distributions, or use the validation scripts directly. Readers and routine contributors can stay with the public Nix commands above.

## What the Nix files mean

- `flake.nix` is the project's entry point. It declares public inputs and supported platforms.
- `flake.lock` pins those inputs to exact revisions and content hashes. We started from Plot's existing public nixpkgs and flake-parts revisions; this project does not import Plot or need its private cache.
- `nix/default.nix` describes the products, checks, preview/preparation applications and development shell. Each product is a recipe, called a derivation: inputs go in and a directory or executable comes out.
- `nix/python.nix` builds the Python environment from pinned Nix packages. The validator remains at the version recorded in `uv.lock`, preserving the earlier migration's pySHACL contract.
- `web/garden-assets.json` pins the browser runtime by URL and SHA-256. Nix checks the downloaded bytes rather than silently accepting a changed upstream asset.

Nix fetches declared dependencies, then runs ordinary builds in its build environment. Build scripts do not download packages or browser assets themselves. On subsequent runs, Nix can reuse outputs when the relevant inputs have not changed.

For Git-based flakes, new files must be added with `git add` before Nix sees them. Staging is sufficient; a commit is not required. A dirty-tree warning while developing is expected and does not mean the build failed. `result` and `.direnv/` are local outputs ignored by Git.

## Static hosting

Deploy the **contents of `result/`**, preserving directory layout. Cloudflare Pages can host this as a plain static site; no application server, database, Worker, Python, uv or Nix is needed at runtime. A Cloudflare build can also be skipped when an already-built artifact or `site` branch supplies those files.

The intended public identity is `https://ontologies.corestory.ai`. Canonical URLs and social metadata name that origin; they do not prove it is deployed. The site is a reference library with no analytics or lead collection. Hosting, DNS, TLS, security headers, and public social-preview validation require separate deployment verification.

Serve `healthz` as a static response and use `404.html` with HTTP 404 for unknown paths. Do not use a successful homepage fallback. `robots.txt` allows crawling; `sitemap.xml` lists canonical HTML pages except the error page. Normal pages use relative links for root or subpath hosting. For a subpath build, pass `--base-path /ontologies/` to `scripts/build_site.py` so deep error-page recovery links use the same prefix. The default is `/`.

Garden renders term-reference pages in the visitor's browser using the bundled dataset. Existing Markdown guides are pre-rendered into HTML under `guides/`. The explorer uses fragment links such as `#spec:Requirement`, so those links do not need server-side routing. All browser assets and datasets are served from the same static site. Telemetry and feedback are disabled.

The dataset is plain JSON. Its URL includes a SHA-256 content hash so changed ontology data cannot reuse an older browser cache entry. Normal CDN gzip/Brotli transport compression is handled by the browser; the application does not rely on special `.gz` response headers or server decompression behavior. `_headers` supplies a small set of static Cloudflare Pages headers.

### Main and site branches

`main` is the source branch: authored RDF, Markdown, website templates, styles, selected brand assets and build definitions. Website copy lives in `web/pages/`, separate from the ontology guides in `docs/`. Templates in `web/templates/` and styles in `web/styles/` control the prose pages. `web/assets/` holds the official CoreStory logo variants, locally served fonts, their licenses and provenance hashes. Builds never need access to Notion.

`site` is the publication branch. Its repository root is exactly the contents of the completed static build:

```text
index.html              # CoreStory Ontologies introduction
reference/              # Combined Garden browser and its dataset
sao/, specspec/         # HTML namespace entries with explicit RDF downloads
guides/                 # Rendered Markdown guides and examples
dist/                   # Turtle distributions
assets/                 # Brand assets, fonts, CSS and pinned Garden runtime
source/                 # Browsable public source, including LICENSE and NOTICE
search-index.json       # Local term and guide discovery
snapshot.json           # Ontology versions and input hashes
robots.txt, sitemap.xml # Public crawl policy and canonical page inventory
healthz, 404.html        # Static health response and noindex error body
_headers                # Static hosting headers
publication.json        # Exact source commit (added when preparing site)
```

The homepage versions come from the ontology catalog, rather than a second version declaration in the website copy. Ontology namespace IRIs remain `/sao/` and `/specspec/`; moving the browser to `/reference/` does not rename terms. Namespace entries are HTML, not RDF content-negotiation endpoints. Individual term paths are not generated; use Garden fragments or explicit Turtle downloads. Existing root-fragment Garden bookmarks redirect to the browser location.

The public source collection copies only the exact, reviewed paths in `web/public-source-manifest.json`; directory names do not grant publication permission. The build also publishes that inventory as `source-manifest.json`. New nested files require explicit review, and symlinks are refused. The confidential whitepaper and its equivalent Markdown source are withheld without modifying the repository originals. Other reviewed guides remain available. LICENSE and NOTICE are preserved byte-for-byte. The builder creates directory indexes rather than relying on server directory listing; the collection is not a complete build checkout.

The publication process is local: start from committed `main`, run `nix flake check` and `nix build`, populate a separate `site` checkout with the complete output (removing files left over from earlier builds), record the source commit, then commit and push `site` with ordinary fast-forward history. Never merge `site` into `main` or hand-edit generated HTML. The command performs the checks, build and local branch update; pushing remains an explicit separate step:

```sh
nix run .#prepare-site
# Review the new branch; your source checkout stays where it is.
git log -1 site
git show site:publication.json
git push origin site
```

Preparation requires a clean checkout, including untracked files, and uses **local `main`**, not an automatic fetch of `origin/main`. Update and push your source branch through your usual Git workflow before publishing. To prepare a candidate from the current committed feature branch instead, use `nix run .#prepare-site -- --source-ref HEAD`; its actual commit is recorded in `publication.json`. The source is passed to Nix by immutable Git revision. Tests and the site build must succeed before local `site` changes.

Preparation uses a temporary Git index and content directory. It creates an initial parentless `site` commit, then preserves ordinary history on subsequent updates. Old generated files disappear, identical output with the same source commit is a no-op, and concurrent branch changes cause a refusal instead of an overwrite. Your current branch, files and index stay untouched. It refuses to update `site` while that branch is checked out in any worktree, or to repurpose an existing source branch named `site`. Git author/committer identity must already be configured.

No Git network operations occur during preparation. If you already have a published branch on another machine, first fetch it and create local tracking history with `git branch --track site origin/site`. If a concurrent push makes your later `git push origin site` fail, do not force-push: preserve the remote history and prepare again from it. A successful branch push is what the future Git-connected host will use as its deployment trigger. Nix may fetch declared build dependencies; there are no Cloudflare credentials or API calls in preparation.

A Git-connected static host can watch `site` and serve its root without installing Nix or rebuilding the ontologies. No Cloudflare API credentials or GitHub Actions publishing job are needed for that arrangement. Existing Cloudflare project migration and domain configuration are outside this repository layout change.

## Reproducibility and scope

The builder reads the ontology catalog and authored Turtle. Garden JSON is a display projection; it does not replace SHACL validation or the source graphs. Cardinalities, allowed values and ranges appear in definitions; additional constraints and graph-rule descriptions appear in remarks. Source versions, hashes and display limitations are recorded in `snapshot.json`.

Output records no wall-clock time or absolute developer paths. Anonymous RDF nodes are canonicalized before distribution serialization. Tests check stable projection output, anonymous-node serialization, term coverage and local HTML links.

SAO's old LinkML baseline is archived and excluded from CI. Its manual comparison commands remain documented under `legacy/sao/`. The active RDF and documentation workflow does not need that toolchain.

The Garden runtime is third-party software fetched from its official distribution, retaining its built-in attribution. The asset manifest records the source and exact bytes; those assets are not relicensed by this repository's Apache license. The local-preview bootstrap adaptations are documented in `web/README.md`.

## Evaluation-cache contention and binary caches

A dirty-tree warning is expected during development. If Nix/Lix reports that its SQLite evaluation cache is busy, retry with `nix build --option eval-cache false`. This bypasses the evaluation cache for that invocation; it does not disable binary substitutions or rebuild every dependency. Check the exit status and the `result/` symlink to confirm the build succeeded. No cache files need to be deleted.

A Cachix cache stores completed build outputs and can speed up reuse between CI and developers. It is separate from the local SQLite evaluation cache, so adding Cachix is not a fix for that lock message. This flake works without an ontology-specific Cachix cache. Cache configuration and CI credentials can be added once a cache is chosen; no private Plot cache configuration has been copied here.
