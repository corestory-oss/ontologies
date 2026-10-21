# Contributing to SAO

Follow the shared [repository contribution guide](../../CONTRIBUTING.md). Run commands from the repository root.

Edit vocabulary under `ontologies/sao/vocabulary/`, constraints under `ontologies/sao/shapes/`, and reviewed inverse axioms under `ontologies/sao/axioms/`. Update manifests when adding files. Rebuild and commit the `dist/sao.*ttl` distributions with source edits.

The [inverse audit](inverse-relationships.md) and [3.0.0 migration notes](migration-3.0.md) explain relationship compatibility. Do not reinterpret class-local inverses as global OWL axioms without reviewing all uses. Add valid and invalid examples for changed constraints.

The historical LinkML baseline and its check commands are documented under [legacy/sao/](../../legacy/sao/README.md). It is not the source for current Turtle authoring.

Use **bold** for class names in prose and `monospace` for exact property names, enum values and dotted paths. Keep synthetic examples and preserved Apache attribution.
