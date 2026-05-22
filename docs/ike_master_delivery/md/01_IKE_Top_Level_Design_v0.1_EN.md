# IKE Top-Level Design v0.1

## 1. Purpose

IKE is a self-evolving research intelligence system built around three interacting brains: Information, Knowledge, and Evolution. The purpose of this document is to define the system at the method level before locking in implementation choices.

## 2. Core Thesis

Information Brain senses high-value external signals. Knowledge Brain organizes them into structured understanding. Evolution Brain identifies promising directions for self-improvement, launches research and experiments, and validates what should be adopted.

## 3. Three-Brain Model

- Information Brain: external sensing, source evaluation, filtering, watchlists, observations.
- Knowledge Brain: entities, relations, claims, consensus vs controversy, field maps, timelines.
- Evolution Brain: concept detection, self-relevance assessment, research initiation, experimentation, adoption decisions.

## 4. Shared Layers

IKE requires a shared object layer, a shared memory layer, a thinking-model layer, and a governance layer. The brains should not become isolated vertical stacks.

## 5. Long-Term Direction

The long-term target is not a static knowledge system. It is a system that can improve how it studies the world, how it chooses methods, and how it validates its own upgrades.

## 6. Engineering Consequence

The system should start as a modular monolith with clean contracts. Premature service splitting should be avoided until the object model, workflows, and evaluation loops have stabilized.
