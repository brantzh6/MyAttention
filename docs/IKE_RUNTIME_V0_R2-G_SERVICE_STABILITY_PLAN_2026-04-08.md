# IKE Runtime v0 R2-G Service Stability Plan

## Goal

Harden the runtime operating surface enough that live proof and delegated closure become more repeatable.

## Work Buckets

### 1. API runtime process discipline
- identify one truthful API launch path
- eliminate multi-process ambiguity from validation runs
- make live proof criteria explicit

### 2. Delegated closure reliability
- preserve controller truthfulness around incomplete delegated artifacts
- reduce cases where a lane does useful work but fails durable finalization

### 3. Comparison baseline formalization
- use the current `Claude` coding evidence as baseline
- schedule a same-packet dual-lane comparison later
- do not overstate existing comparison evidence

## Success Criteria

- runtime live proof can be repeated without process ambiguity
- delegated lanes produce fewer incomplete-final-artifact outcomes
- controller recovery decreases for narrow packets
