# IKE Object Model and Shared Memory Layer Design v0.1

## 1. Object Layer

The shared object layer should contain Source, Observation, Entity, Relation, Claim, Event, Concept, ThinkingModel, Paradigm, ResearchTask, Experiment, Decision, HarnessCase, and GovernanceReview.

## 2. Shared Memory Layer

Suggested memory strata: observation memory, evidence memory, structured knowledge memory, working research memory, governance memory, and long-term adopted memory.

## 3. Read/Write Boundaries

Information writes observations and source evaluations. Knowledge writes entities, relations, and claims. Evolution writes tasks, experiments, and decisions. Governance writes selection and review records.

## 4. Lifecycle

Objects move from observation to structured interpretation, to tasks and experiments, to adoption or retirement. The lifecycle must remain inspectable.
