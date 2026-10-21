{ pkgs }:
let
  manifest = builtins.fromJSON (builtins.readFile ../web/garden-assets.json);
  assets = map (asset: {
    inherit (asset) path;
    file = pkgs.fetchurl { inherit (asset) url hash; };
  }) manifest.assets;
in
pkgs.runCommand "rdf-garden-${manifest.version}-assets" { } (
  pkgs.lib.concatMapStringsSep "\n" (asset: ''
    mkdir -p "$out/$(dirname '${asset.path}')"
    cp ${asset.file} "$out/${asset.path}"
  '') assets
)
