<!-- GENERATED FILE — do not edit. Regenerate with pb-registers. -->

# Decision Stream

Flat, dated history of every committed design choice. Current state lives
in the layer leaves named by each record's `state:` field.

Records live in the cold-storage archive; extract one with `pb archive read <ID>`.

## By Layer

### Product

- **AD-002** — inout and undirected ports become inputs · accepted · 2026-11-05 · `AD-002`
  FMI 2.0 has no bidirectional scalar, so inout and undirected ports are emitted as inputs and the Modelica connector keeps no direction qualifier.

### Architecture

- **AD-001** — The guid namespace string stays literally pyssp_sysml2 · accepted · 2026-11-05 · `AD-001`
  The FMI guid is uuid5(NAMESPACE_URL, "pyssp_sysml2/<composition>/<component>") even though the package is named pyfmi_sysml2.
