{ pkgs }:
let
  ps = pkgs.python313Packages;
  # Preserve the validator version used during the Turtle migration. The
  # remaining RDF libraries come from our pinned nixpkgs, within project bounds.
  lock = builtins.fromTOML (builtins.readFile ../uv.lock);
  validator = pkgs.lib.findFirst (
    p: p.name == "pyshacl"
  ) (throw "pyshacl is missing from uv.lock") lock.package;
  pyshacl = ps.buildPythonPackage {
    pname = "pyshacl";
    version = validator.version;
    pyproject = true;
    src = pkgs.fetchurl {
      url = validator.sdist.url;
      sha256 = pkgs.lib.removePrefix "sha256:" validator.sdist.hash;
    };
    build-system = [ ps.poetry-core ];
    dependencies = [
      ps.rdflib
      ps.owlrl
      ps.packaging
      ps.prettytable
      ps.html5lib
    ];
    pythonImportsCheck = [ "pyshacl" ];
  };
in
pkgs.python313.withPackages (p: [
  p.rdflib
  p.owlrl
  p.markdown
  pyshacl
])
