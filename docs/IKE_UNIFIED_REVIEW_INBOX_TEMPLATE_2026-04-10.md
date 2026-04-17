# IKE Unified Review Inbox Template

This is the single writeback document for external reviews.

Use one file per review target, not one file per model.

You send the same review request to multiple models, then paste all returned
opinions into this one document under separate sections.

---

## External Review Request Prompt

Review this packet as a narrow IKE runtime/mainline review.

Focus on:

1. semantic honesty
2. durable truth alignment
3. hidden execution or failure-mode risk
4. whether the packet overclaims capability
5. whether tests are proving the right thing instead of a convenient proxy

Return your review in the following exact structure:

### Overall Judgment

- score:
- direction:
  - on_track
  - mixed
  - off_track
- recommendation:
  - accept
  - accept_with_changes
  - reject

### Findings

List findings first, ordered by severity.

For each finding, use:

- severity: `P0` / `P1` / `P2` / `P3`
- title:
- location:
- why it matters:
- suggested correction:

If there are no findings, explicitly write:

- no material findings

### Validation Gaps

- what you did not rerun
- what you inferred only from file reading
- what still needs direct proof

### What Looks Good

- point 1
- point 2
- point 3

### Semantics Check

- fake capability risk:
- fake durability risk:
- hidden state risk:
- trust-boundary wording risk:

### Short Conclusion

Write one short paragraph that can be pasted back to the controller directly.

---

## Review Target

- packet / doc:
- date:
- controller owner:
- notes:

## Source Links

- review pack:
- primary result docs:
- key code files:
- key test files:

---

## Model A Review

- model:
- date:

Paste full returned review below this line.



---

## Model B Review

- model:
- date:

Paste full returned review below this line.



---

## Model C Review

- model:
- date:

Paste full returned review below this line.



---

## Controller Synthesis

Use this section after all external reviews are pasted back.

### Shared Findings

- point 1:
- point 2:
- point 3:

### Disagreements

- disagreement 1:
- disagreement 2:

### Controller Decision

- recommendation:
  - accept
  - accept_with_changes
  - reject
- absorbed now:
- defer:
- next packet:

### Final Short Conclusion

One short controller paragraph for durable record.

---

## Suggested Usage Rule

For each new review packet, create one file named like:

- `review-for IKE_RUNTIME_V0_<PACKET>.md`

Then:

1. keep the prompt section at the top
2. paste the packet links once
3. collect all external model reviews in the same file
4. add controller synthesis at the end
