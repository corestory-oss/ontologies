{
  perSystem =
    { pkgs, ... }:
    let
      python = import ./python.nix { inherit pkgs; };
      garden = import ./garden.nix { inherit pkgs; };
      src = pkgs.lib.fileset.toSource {
        root = ../.;
        fileset = pkgs.lib.fileset.unions [
          ../scripts
          ../tests
          ../ontologies
          ../examples
          ../dist
          ../docs
          ../web
          ../legacy
          ../README.md
          ../CONTRIBUTING.md
          ../CHANGELOG.md
          ../LICENSE
          ../NOTICE
        ];
      };
      ontologies = pkgs.stdenvNoCC.mkDerivation {
        pname = "corestory-ontologies";
        version = "0.1.0";
        inherit src;
        nativeBuildInputs = [ python ];
        dontConfigure = true;
        buildPhase = ''
          runHook preBuild
          python scripts/build_rdf.py
          runHook postBuild
        '';
        doCheck = true;
        checkPhase = ''
          python scripts/validate_rdf.py
          python scripts/validate_axioms.py
        '';
        installPhase = ''
          mkdir -p "$out"
          cp dist/*.ttl "$out/"
          cp ontologies/catalog.json "$out/catalog.json"
        '';
      };
      site = pkgs.stdenvNoCC.mkDerivation {
        pname = "corestory-ontology-site";
        version = "0.1.0";
        inherit src;
        nativeBuildInputs = [ python ];
        dontConfigure = true;
        buildPhase = ''
          python scripts/build_site.py --output site \
            --garden-assets ${garden} --distributions ${ontologies}
        '';
        doCheck = true;
        checkPhase = ''
          python scripts/check_site.py site
        '';
        installPhase = ''
          cp -R site "$out"
        '';
      };
      rdfChecks =
        pkgs.runCommand "corestory-ontology-checks"
          {
            nativeBuildInputs = [
              python
              pkgs.git
            ];
          }
          ''
            cp -R ${src} source
            chmod -R u+w source
            cd source
            export HOME="$TMPDIR"
            python scripts/build_rdf.py --check
            python scripts/validate_rdf.py
            python scripts/validate_rdf.py --ontology sao examples/sao/rdf/relationships-3.ttl
            python scripts/validate_axioms.py
            python -m unittest discover -s tests
            touch "$out"
          '';
    in
    {
      packages = {
        inherit ontologies site;
        default = site;
      };
      checks = {
        rdf = rdfChecks;
        inherit site;
      };
      apps.prepare-site = {
        type = "app";
        program = "${
          pkgs.writeShellApplication {
            name = "ontology-prepare-site";
            runtimeInputs = [ pkgs.git ];
            text = ''
              exec ${python}/bin/python ${../scripts/prepare_site.py} "$@"
            '';
          }
        }/bin/ontology-prepare-site";
      };
      apps.preview = {
        type = "app";
        program = "${pkgs.writeShellScript "ontology-preview" ''
          port="''${1:-4173}"
          if [ "$#" -gt 0 ]; then shift; fi
          echo "Ontology docs: http://127.0.0.1:$port/ (Ctrl-C to stop)"
          exec ${python}/bin/python ${src}/scripts/preview_site.py "$port" \
            --bind 127.0.0.1 --directory ${site} "$@"
        ''}";
      };
      devShells.default = pkgs.mkShell {
        packages = [
          python
          pkgs.nixfmt
        ];
        shellHook = ''
          echo "CoreStory Ontologies: nix build | nix flake check | nix run .#preview"
        '';
      };
      formatter = pkgs.writeShellApplication {
        name = "format-ontology-nix";
        runtimeInputs = [ pkgs.nixfmt ];
        text = ''
          if [ "$#" -eq 0 ]; then set -- flake.nix nix/*.nix; fi
          exec nixfmt "$@"
        '';
      };
    };
}
