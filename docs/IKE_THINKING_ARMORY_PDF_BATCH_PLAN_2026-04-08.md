# IKE Thinking Armory PDF Batch Plan

## Problem

The first full-corpus local Claude review run over all 21 extracted texts is
still running without a durable final artifact.

This likely reflects bounded-run completion pressure rather than a lack of
useful corpus.

## Narrow Recovery Strategy

Keep the original full-corpus run as evidence, but split the study into:

1. `Batch A`
- `001.txt` through `010.txt`

2. `Batch B`
- `011.txt` through `021.txt`

3. `Synthesis`
- only after at least one batch returns a durable review result

## Controller Rule

- do not discard the original full-corpus run
- do not claim completion from a still-running batch
- prefer smaller durable review artifacts over one oversized hanging run
