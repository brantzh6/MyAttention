# IKE DeerFlow 2.0 Research Note

Date: 2026-04-09
Status: accept_with_changes

## Scope

This note records a narrow research pass on DeerFlow 2.0 as a reference
project for:

- multi-agent orchestration
- long-horizon task execution
- sandboxed execution
- memory layering
- runtime/controller boundaries

## Source Discipline

Primary source used:

- official/community-facing DeerFlow 2.0 documentation site:
  - [https://deerflow.one/](https://deerflow.one/)

Secondary supporting sources:

- GitHub reference surfaced through public summaries
- third-party architectural writeups used only as secondary interpretation,
  not as the source of truth

## What DeerFlow 2.0 Clearly Emphasizes

### 1. Long-horizon tasks are first-class

DeerFlow 2.0 explicitly frames itself around long-running tasks:

- plan
- research
- revise
- deliver

This is important because it is not optimized for one-shot chat completion.
It is optimized for sustained task progression over minutes to hours.

Implication for IKE:

- our runtime direction is correct
- task/state continuity must remain first-class
- the system cannot just be a better prompt wrapper

### 2. Lead-agent + dynamic sub-agent orchestration

DeerFlow describes:

- a lead agent / coordinator
- dynamic sub-agent spawning
- separate contexts for different lines of work
- sequential and parallel task advancement

Implication for IKE:

- this strongly supports our controller/delegate structure
- it also reinforces that subagent context separation matters
- the key question is not whether to use subagents, but how to constrain them

### 3. Docker-native sandbox execution

DeerFlow explicitly treats sandbox execution as a core layer:

- Docker-based sandbox
- filesystem + command execution
- AIO Sandbox with Browser, Shell, File, MCP, VSCode Server

Implication for IKE:

- this is stronger than our current state
- we now have isolated workspaces and external run roots
- but DeerFlow shows the next step:
  - execution isolation as an enforced runtime property
  - not just a directory/layout convention

### 4. Long-term and short-term memory are explicit

DeerFlow 2.0 explicitly says:

- long-term memory
- short-term memory
- context continuity
- user preference / task-state retention

Implication for IKE:

- our current runtime truth + memory packet direction is consistent
- but our retrieval/memory layering is still earlier-stage than DeerFlow's
- we still need to mature:
  - typed memory
  - task-state continuity
  - controlled recall

### 5. Skills/tools/MCP are extension surfaces, not the whole system

DeerFlow explicitly treats:

- skills
- tools
- MCP
- knowledge integrations

as extension surfaces around the core orchestrator.

Implication for IKE:

- correct architectural order is:
  - runtime/task/controller core first
  - tools/skills/connectors second

## What DeerFlow 2.0 Seems Stronger At Than Current IKE

1. Enforced sandbox execution
2. Long-horizon orchestration as an explicit product-level design
3. More explicit separation between orchestrator and execution environment
4. More productized multi-agent shape

## What IKE Is Already Stronger At

1. Runtime truth discipline
- task/decision/memory/work-context truth boundaries are more explicitly
  articulated in our current docs than in DeerFlow's public-facing material

2. Controller acceptance discipline
- we are unusually strict about:
  - durable results
  - mixed evidence
  - fallback vs delegated truth
  - memory trust boundaries

3. Explicit concern for false durability / false memory / false closure
- this remains one of our strongest architectural instincts

## Most Useful Takeaways For IKE

### A. Sandbox must become an execution primitive

Not just:

- isolated directories
- separate workspaces

But:

- task/run-bound execution environment
- explicit lifecycle
- explicit capability boundaries

### B. Long-horizon orchestration should stay central

DeerFlow strengthens the argument that runtime should model:

- plan progression
- phase progression
- parallel sub-work
- staged deliverables

### C. Environment lifecycle should be separated from task truth

The strongest shared lesson across DeerFlow, CREAO, and Anthropic-style agent
harness thinking is:

- execution environment is not the same thing as runtime truth
- but it must be modeled explicitly

### D. Skills/MCP should remain secondary to harness correctness

DeerFlow supports many integrations, but its stronger lesson for us is not
“add more connectors.”

It is:

- get orchestration and sandboxing right first

## Current Controller Judgment

DeerFlow 2.0 is worth studying further, but not as a full architecture to copy.

The highest-value borrow points are:

1. enforced sandbox execution
2. orchestrator + dynamic sub-agent shape
3. long-horizon task framing
4. explicit memory layering

The wrong takeaway would be:

- to expand tool/plugin surfaces before the execution/runtime core is hardened

## Recommended Follow-up

1. Add DeerFlow to the long-horizon reference set for agent harness design.
2. Use it specifically when refining:
   - sandbox identity
   - execution environment lifecycle
   - long-horizon controller/subagent orchestration
3. Do not let DeerFlow study widen current runtime scope prematurely.

## Sources

- DeerFlow 2.0 docs:
  - [https://deerflow.one/](https://deerflow.one/)
- Supporting secondary interpretation:
  - [https://www.termdock.com/en/blog/deer-flow-bytedance-superagent](https://www.termdock.com/en/blog/deer-flow-bytedance-superagent)
  - [https://www.aibase.com/news/26583](https://www.aibase.com/news/26583)
