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
      deploy = pkgs.writeShellApplication {
        name = "ontology-deploy";
        runtimeInputs = [
          pkgs.wrangler
          pkgs.coreutils
        ];
        text = ''
          if [ "$#" -gt 1 ]; then
            echo "Usage: nix run .#deploy [-- --login|--dry-run|--help]" >&2
            exit 2
          fi
          case "''${1:-}" in
            --help|-h)
              echo "nix run .#deploy                 Build and publish the production site"
              echo "nix run .#deploy -- --login       Sign in to Cloudflare without deploying"
              echo "nix run .#deploy -- --dry-run     Show the built artifact and target without uploading"
              exit 0
              ;;
            ""|--login|--dry-run) ;;
            *) echo "Unknown option: $1" >&2; exit 2 ;;
          esac

          export CLOUDFLARE_ACCOUNT_ID=bea09d9cf3f7aef8adff86cc8726b9ca
          export WRANGLER_SEND_METRICS=false
          if [ "''${1:-}" = --dry-run ]; then
            echo "Site: ${site}"
            echo "Cloudflare Pages: corestory-ontologies (production branch: main)"
            echo "URL: https://ontologies.corestory.ai"
            exit 0
          fi

          # Ignore checkout-local Wrangler configs, dotenv files and Git branch
          # inference. Upload only the checked Nix artifact to this fixed project.
          deploy_tmp=$(mktemp -d)
          trap 'rm -rf "$deploy_tmp"' EXIT
          cd "$deploy_tmp"
          if [ "''${1:-}" = --login ]; then
            wrangler login
          else
            echo "Publishing ${site} to corestory-ontologies (production)"
            wrangler pages deploy ${site} --project-name corestory-ontologies --branch main
          fi
        '';
      };
      rdfChecks =
        pkgs.runCommand "corestory-ontology-checks"
          {
            nativeBuildInputs = [ python ];
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
        inherit ontologies site deploy;
        default = site;
      };
      checks = {
        rdf = rdfChecks;
        inherit site;
      };
      apps.deploy = {
        type = "app";
        program = "${deploy}/bin/ontology-deploy";
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
