# IKE Source Intelligence V1 - M4 Phase Judgment

Date: 2026-04-13
Phase: `M4 Same-Repo Release Duplicate Compression In LATEST/FRONTIER`
Status: `approved_for_bounded_start`

## Purpose

Open one bounded post-`M3` slice that is distinct from generic-domain
compression.

## Why M4 Starts Now

`M3` already handled one same-source generic-domain duplication family.

The next useful narrow edge is different:

- a repository candidate
- and a release candidate
- for the same repo
- inside a timely discovery context

## M4 Objective

Compress one same-repo overlap pattern:

1. keep `release`
2. suppress `repository`
3. only when the focus is `LATEST` or `FRONTIER`, where release signal can
   legitimately outrank the baseline repository duplicate

## Explicit Non-Goals

- no repository suppression in `METHOD`
- no release ranking redesign
- no lifecycle automation
- no source-plan schema changes

## Exit Condition

`M4` is complete when the project has:

1. one bounded helper-level overlap-compression rule
2. one focused route proof on `/sources/discover`
3. one explicit truth boundary that this is a timely-focus heuristic, not a
   general repository-vs-release policy
