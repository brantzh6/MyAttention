# IKE Task, Experiment, and Decision Engine Spec v0.1

## 1. Core Execution Loop

Tasks are created from signals, gaps, exceptions, governance actions, or harness failures. Tasks may spawn experiments. Experiments generate evidence. Decisions adopt, reject, defer, or escalate.

## 2. State Machines

Task, Experiment, and Decision each require explicit state transitions and audit trails.

## 3. Human-in-the-Loop

High-impact decisions should require explicit review gates.

## 4. Integration

The engine binds together workflows, governance, harness, and adoption records.
