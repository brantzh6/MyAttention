# IKE Data Contracts and Core Schemas v0.1

## 1. Purpose

This document defines the first implementation-grade schema set for IKE.

## 2. Envelope

Every persisted object should include id, kind, version, status, timestamps, provenance, confidence, and references.

## 3. First-Class Objects

Priority first-class objects: Source, Observation, Entity, Relation, Claim, ThinkingModel, Paradigm, ResearchTask, Experiment, Decision, HarnessCase, EvaluationRecord.

## 4. Anti-Patterns

Avoid schema drift between modules, implicit enums, and payloads with no provenance or version fields.
