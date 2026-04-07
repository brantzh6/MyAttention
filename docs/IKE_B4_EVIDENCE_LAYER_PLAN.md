# IKE B4 Evidence Layer Plan

## Purpose

`B4` is the next benchmark-method upgrade after:

- `B1`: signal + meaning + relevance hint
- `B2`: concept trigger + study packet
- `B3`: concept deepening + applicability review

The purpose of `B4` is to improve evidence quality so benchmark conclusions are
not overly shaped by generic search/discovery bias.

## Why B4 Exists

The current `harness` benchmark is directionally useful, but current entity and
concept conclusions are still too exposed to:

- generic search ranking bias
- weak authority discrimination
- weak separation of official vs community evidence
- weak separation of concept-defining vs merely adjacent entities

That means the system can already trigger bounded research, but it should not
yet automatically trigger method adoption.

## Core Principle

Evidence must be layered before it is ranked.

The benchmark method should explicitly distinguish:

- authoritative / official
- expert / maintainer
- implementation repository
- community discourse
- media context
- primary local artifact
- structured secondary interpretation

before:

- entity tier assignment
- gap mapping
- recommendation level
- study packet generation

## Evidence Layers

### 1. `authoritative_official`

Examples:

- official project documentation
- official repository docs
- official release notes
- organization-owned statements

Role:

- define concept scope
- anchor working definition
- reduce ambiguity

Priority:

- highest

### 2. `expert_maintainer`

Examples:

- maintainers
- primary authors
- core contributors
- recognized practitioners with direct technical ownership

Role:

- validate interpretation
- clarify boundary conditions
- surface current best practice

Priority:

- high

### 3. `implementation_repository`

Examples:

- repositories
- implementation guides
- release / commit / issue evidence
- directly inspectable technical patterns

Role:

- identify applicability
- support bounded study packets
- support prototype decisions

Priority:

- high

### 4. `community_discourse`

Examples:

- community discussions
- practitioner commentary
- adoption chatter
- disagreement and open questions

Role:

- detect traction
- surface competing interpretations
- expose unresolved ambiguity

Priority:

- medium

### 5. `media_context`

Examples:

- articles
- news coverage
- ecosystem trend framing

Role:

- background awareness only

Priority:

- low

### 6. `primary_local_artifact`

Examples:

- local source snapshot
- directly inspectable local codebase
- local docs shipped with the artifact

Role:

- provide direct technical evidence
- validate whether the concept is implemented in reality
- anchor applicability judgment

Priority:

- high

### 7. `structured_secondary_interpretation`

Examples:

- local repowiki
- structured machine-generated repository explanation
- subsystem map generated from repository contents

Role:

- accelerate navigation
- summarize large codebases
- support packet formation

Priority:

- medium

## Controller Rules

1. Media/context cannot define the concept by itself.
2. Community/discourse cannot outrank official or maintainer evidence by default.
3. Implementation-relevant entities require direct technical evidence.
4. Concept-defining entities should require official and/or maintainer evidence.
5. Structured secondary interpretation cannot overrule primary local artifacts.
6. If evidence quality is weak, recommendation level must remain conservative.

## First B4 Upgrade

The first bounded B4 upgrade should be:

- add explicit evidence-layer tagging to benchmark candidates/entities

This should happen before:

- stronger concept-defining selection
- stronger gap-to-mechanism mapping
- any move from `study` to `prototype`

## Immediate Question For `harness`

For the current `harness` benchmark, the next question is:

- are the current top entities ranked because they occupy stronger evidence
  layers, or mainly because they are nearby in generic discovery?

That should be answered explicitly in the next packet.
