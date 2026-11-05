---
title: Product
summary: The artifact contract, the variable model, and the errors a model author can provoke.
---

# Product

What a consumer may rely on: the FMI artifact shape, the variables it carries,
and the refusals that keep an invalid model from becoming a file.

## Contents

<!-- pb:index:start -->
<!-- GENERATED FILE — do not edit. Regenerate with pb-registers. -->
- **CP-001** [FMI 2.0 CoSimulation artifact contract](artifact-contract.md) — A generated FMU is a deterministic zip with a validated modelDescription at the root and an executable binary named by modelIdentifier.
- **CP-002** [Variable model](variable-model.md) — Parameters come from the parameter dialect, lists expand into scalars, port fields are dotted names, and value references restart at zero per component.
- **CP-003** [Errors and refusals](errors-and-refusals.md) — Ambiguous roots, flat parameters, non-fixed lists, flattened connectors, naive clocks, and platform or identifier mismatches are refused with an actionable message.
<!-- pb:index:end -->
