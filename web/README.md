# Static reference browser assets

The site uses The RDF Garden 2.0.56 browser distribution, as used by the Brick ontology explorer. `garden-assets.json` pins the four official upstream assets by URL and SHA-256. `nix/garden.nix` fetches them as declared fixed-content build inputs; no third-party binary assets are checked into this repository.

The site builder verifies those bytes before applying two explicit bootstrap adaptations:

1. Load ordinary JSON instead of manually gunzipping the dataset. This works with standard static-host/CDN compression without special server configuration.
2. Redirect the built-in error-reporting endpoint to a disabled local path. The site also disables event/feedback reporting and restricts browser connections to its own origin.

CSS, font and application modules are copied into the static output. Their original attribution remains available in Garden's About panel. Upstream assets retain their own terms; they are not covered by the repository's Apache license.

The RDF-to-Garden display projection is our adapter in `scripts/site_projection.py`. It is version-coupled to this pinned runtime. Update hashes, bootstrap checks and projection tests together when upgrading Garden. Do not replace a failed checksum merely to make a build pass without inspecting the new upstream content.
