# Nix builds and static documentation

The public commands are Nix commands. Python remains the implementation language, but a normal build does not invoke uv, pip, or a local virtual environment.

## The everyday commands

```sh
nix build                     # Build static documentation; result/ points to it
nix run .#preview             # Build and serve it locally; Ctrl-C stops it
nix flake check               # Run RDF, composition, projection and site checks
nix build .#ontologies        # Build just the Turtle distributions
nix run .#deploy              # Build and publish the production documentation site
```

`nix build` puts the completed artifact in the Nix store and creates a `result` symlink in your checkout. `result/` contains an HTML shell, JavaScript, CSS, fonts, ontology JSON, HTML guides, source downloads and Turtle distributions. It is a directory of static files, not a running service.

`nix run .#preview` is a convenience application supplied by this repository. The `preview` name is our choice; `nix run` is the standard Nix mechanism for running such a named application. It starts an ordinary foreground HTTP server bound to `127.0.0.1:4173`. That server exists only for local preview and stays up until Ctrl-C or the terminal closes. The preview disables HTTP caching, including timestamp-based 304 responses: Nix normalizes file timestamps, which would otherwise let browsers reuse an older dataset. It does not watch files or rebuild automatically; restart the command after editing. To use another port, run `nix run .#preview -- 8080`.

`nix flake check` runs finite checks and exits. It does not start a long-lived server. CI invokes the same checks and builds the same site, then attaches the site directory as a downloadable artifact.

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
- `nix/default.nix` describes the products, checks, preview application and development shell. Each product is a recipe, called a derivation: inputs go in and a directory or executable comes out.
- `nix/python.nix` builds the Python environment from pinned Nix packages. The validator remains at the version recorded in `uv.lock`, preserving the earlier migration's pySHACL contract.
- `web/garden-assets.json` pins the browser runtime by URL and SHA-256. Nix checks the downloaded bytes rather than silently accepting a changed upstream asset.

Nix fetches declared dependencies, then runs ordinary builds in its build environment. Build scripts do not download packages or browser assets themselves. On subsequent runs, Nix can reuse outputs when the relevant inputs have not changed.

For Git-based flakes, new files must be added with `git add` before Nix sees them. Staging is sufficient; a commit is not required. A dirty-tree warning while developing is expected and does not mean the build failed. `result` and `.direnv/` are local outputs ignored by Git.

## Static hosting and Cloudflare

Deploy the **contents of `result/`**, preserving directory layout. Cloudflare Pages can host this as a plain static site; no application server, database, Worker, Python, uv or Nix is needed at runtime. A Cloudflare build can also be skipped when an already-built artifact or `site` branch supplies those files.

Garden renders term-reference pages in the visitor's browser using the bundled dataset. Existing Markdown guides are pre-rendered into HTML under `guides/`. The explorer uses fragment links such as `#spec:Requirement`, so those links do not need server-side routing. All browser assets and datasets are served from the same static site. Telemetry and feedback are disabled.

The dataset is plain JSON. Its URL includes a SHA-256 content hash so changed ontology data cannot reuse an older browser cache entry. Normal CDN gzip/Brotli transport compression is handled by the browser; the application does not rely on special `.gz` response headers or server decompression behavior. `_headers` supplies a small set of static Cloudflare Pages headers.

### Deploy from your workstation

```sh
nix run .#deploy -- --login     # One-time Cloudflare browser authorization
nix run .#deploy -- --dry-run   # Build and show the artifact and target, without uploading
nix run .#deploy               # Build, check and upload to production
```

Nix supplies a pinned Wrangler CLI and its runtime; no separate npm installation is needed. `deploy` is another repository-defined Nix application, like `preview`. It references the site derivation directly, so it builds the site even if `result` currently points at a Turtle-only build. A failing site build or its checks prevents upload. A successful upload replaces the production deployment, including when invoked from a local feature branch or dirty checkout: the Cloudflare target branch is explicitly `main`, independent of your Git branch.

The command fixes the account to CoreStory Corporate Account and the project to `corestory-ontologies`, serving `https://ontologies.corestory.ai`. It runs Wrangler from a temporary directory to avoid inheriting local Wrangler configuration, dotenv files or Git branch inference. It uploads only the static Nix output. It does not change DNS, Access policies, other projects or the production branch setting.

Wrangler stores browser-login credentials in its user configuration outside the checkout and Nix store. An existing `CLOUDFLARE_API_TOKEN` can be supplied through your environment instead (use Account / Cloudflare Pages / Edit permission for the CoreStory account); never put tokens in Nix files or commit them. Cloudflare API token permissions are account-scoped for Pages, so the wrapper fixes the project but a token is not inherently restricted to this one project. Deployment is a network action performed by the running app, after the reproducible build completes. `--dry-run` only builds and prints the destination; it does not invoke Wrangler or validate credentials.

CI still produces an artifact without deploying. No automatic writes to a `site` branch are configured.

## Reproducibility and scope

The builder reads the ontology catalog and authored Turtle. Garden JSON is a display projection; it does not replace SHACL validation or the source graphs. Cardinalities, allowed values and ranges appear in definitions; additional constraints and graph-rule descriptions appear in remarks. Source versions, hashes and display limitations are recorded in `snapshot.json`.

Output records no wall-clock time or absolute developer paths. Anonymous RDF nodes are canonicalized before distribution serialization. Tests check stable projection output, anonymous-node serialization, term coverage and local HTML links.

SAO's old LinkML checks remain a separate optional legacy job. Its commands are documented under `legacy/sao/`. The primary RDF and documentation workflow does not need that toolchain.

The Garden runtime is third-party software fetched from its official distribution, retaining its built-in attribution. The asset manifest records the source and exact bytes; those assets are not relicensed by this repository's Apache license. The local-preview bootstrap adaptations are documented in `web/README.md`.

## Evaluation-cache contention and binary caches

A dirty-tree warning is expected during development. If Nix/Lix reports that its SQLite evaluation cache is busy, retry with `nix build --option eval-cache false`. This bypasses the evaluation cache for that invocation; it does not disable binary substitutions or rebuild every dependency. Check the exit status and the `result/` symlink to confirm the build succeeded. No cache files need to be deleted.

A Cachix cache stores completed build outputs and can speed up reuse between CI and developers. It is separate from the local SQLite evaluation cache, so adding Cachix is not a fix for that lock message. This flake works without an ontology-specific Cachix cache. Cache configuration and CI credentials can be added once a cache is chosen; no private Plot cache configuration has been copied here.
