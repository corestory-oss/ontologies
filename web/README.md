# Website sources and reference browser

`main` holds editable sources; the generated `site` branch is an output artifact.

- `pages/*.md`: website prose. `index.md` becomes `/index.html`; another page named `about.md` would become `/about/index.html`. `{{sao_version}}` and `{{specspec_version}}` come from the ontology catalog.
- `templates/page.html`: shared accessible page shell, navigation and footer. Python's string-template placeholders receive the title, relative root path and rendered body.
- `styles/site.css`: shared CoreStory styles for prose pages and guides.
- `assets/brand/`: official, unmodified SVG logo and symbol variants from the CoreStory media kit.
- `assets/fonts/`: Roboto, Roboto Condensed and Roboto Mono, served locally with their SIL Open Font License notices.
- `assets/provenance.json`: source references and SHA-256 hashes for the selected brand and font files. Fonts are fetched from a recorded immutable Google Fonts revision when added; normal builds use the checked-in bytes.

The homepage is website prose, not a copy of the contributor README. Ontology documentation remains in `docs/`; the builder renders it into branded HTML under `/guides/`. The combined ontology browser lives at `/reference/`. All pages share one static build. A small homepage script forwards old Garden term-fragment bookmarks to `/reference/`.

The logos remain CoreStory trademarks; the repository license does not grant trademark rights. The brand source is the [CoreStory media kit](https://app.notion.com/p/24fb12d93cb280f2a0dfc8aa8e14d18e). Body copy uses Roboto, headings use Roboto Condensed, and code uses Roboto Mono. Colors follow the kit: black, gold `#FFD83A`, forest `#425F57`, teal `#378794`, and cornflower `#71ABDD`. Text colors may be darkened for readable contrast on white.

Garden retains its own typography and UI. Its supported logo setting uses the official CoreStory wordmark as a mask that follows Garden's light/dark theme. Its links connect back to the homepage, guides and downloads. No private application CSS selectors are overridden.

# Pinned Garden assets

The site uses The RDF Garden 2.0.56 browser distribution, as used by the Brick ontology explorer. `garden-assets.json` pins the four official upstream assets by URL and SHA-256. `nix/garden.nix` fetches them as declared fixed-content build inputs; no third-party binary assets are checked into this repository.

The site builder verifies those bytes before applying two explicit bootstrap adaptations:

1. Load ordinary JSON instead of manually gunzipping the dataset. This works with standard static-host/CDN compression without special server configuration.
2. Redirect the built-in error-reporting endpoint to a disabled local path. The site also disables event/feedback reporting and restricts browser connections to its own origin.

CSS, font and application modules are copied into the static output. Their original attribution remains available in Garden's About panel. Upstream assets retain their own terms; they are not covered by the repository's Apache license.

The RDF-to-Garden display projection is our adapter in `scripts/site_projection.py`. It is version-coupled to this pinned runtime. Update hashes, bootstrap checks and projection tests together when upgrading Garden. Do not replace a failed checksum merely to make a build pass without inspecting the new upstream content.
