---
title: Verification
summary: The six test levels, the cross-artifact gate, the compiler and Modelica oracles, and the fixture and golden policy.
---

# Verification

How the artifacts are proven: the test ladder, the consistency gate, the
external oracles, and the rules a fixture follows.

## Contents

<!-- pb:index:start -->
<!-- GENERATED FILE — do not edit. Regenerate with pb-registers. -->
- **TEST-001** [Test strategy](test-strategy.md) — Six pytest markers, five levels plus a slow qualifier; each owns a distinct fault class, and component goldens are the default gate.
- **TEST-002** [Cross-artifact consistency gate](cross-artifact-gate.md) — check_artifacts() reads modelDescription, the C header, and the packed FMU with independent parsers and proves they describe one component; mutation tests prove it fails when one is broken.
- **TEST-003** [Oracles, fixtures, and goldens](oracles-and-fixtures.md) — gcc and g++ syntax-check the headers, omc checkModel proves the Modelica package, and four shared fixtures carry case records and byte-compared goldens.
<!-- pb:index:end -->
