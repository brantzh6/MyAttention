# IKE System Modules and Service Boundaries v0.1

## 1. Recommended Shape

Start as a modular monolith. Use module boundaries and contracts first; delay service splitting.

## 2. Module Groups

Suggested groups: information runtime, knowledge runtime, evolution runtime, thinking-model and governance runtime, shared object/memory, harness runtime, and external API layer.

## 3. Boundary Rules

Shared schemas must live in a neutral package. No module should reach directly into another module's private persistence model.

## 4. Migration Path

When needed, split by proven runtime pressure or team autonomy needs, not by theoretical purity.
