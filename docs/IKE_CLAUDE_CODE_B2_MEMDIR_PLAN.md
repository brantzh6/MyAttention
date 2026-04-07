# IKE Claude Code B2 Memdir Plan

## Purpose

`B2` focuses only on the `memdir` subsystem inside `Claude Code`.

This is the highest-value next packet because it most directly touches the IKE
gap:

- `memory capture and procedural improvement are still weak`

## Main Question

For IKE, what is actually reusable from `Claude Code`'s memory system?

The goal is not to copy memdir wholesale.
The goal is to identify:

- which memory patterns are useful
- which memory taxonomy parts should change
- where memory extraction should connect into IKE

## What To Study

Primary files:

- `D:\claude-code\src\memdir\memdir.ts`
- `D:\claude-code\src\memdir\memoryTypes.ts`
- `D:\claude-code\src\memdir\findRelevantMemories.ts`
- `D:\claude-code\src\services\extractMemories\extractMemories.ts`

Secondary orientation:

- `D:\code\MyAttention\.qoder\repowiki\en\content\Project Overview.md`
- `D:\code\MyAttention\.qoder\repowiki\en\content\Architecture and Design\Architecture and Design.md`

## Required Outputs

The packet should answer:

1. what the memory taxonomy is
2. what the entrypoint/index pattern is
3. how memory extraction is triggered
4. which parts map to IKE
5. which parts should not be copied directly
6. one bounded prototype candidate for IKE

## Constraints

- no implementation yet
- no full code audit
- no product-wide architecture discussion
- no assuming that every memory pattern is good for IKE

## Success Condition

`B2` succeeds if it produces:

- one credible reusable memory pattern
- one explicit rejection or caution
- one bounded prototype recommendation for IKE memory/procedural capture
