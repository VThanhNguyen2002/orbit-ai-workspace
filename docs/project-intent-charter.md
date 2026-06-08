# Project Intent Charter / IDSD Alignment

## 1. Primary Intent

*   **Synapse is a personal, non-commercial, architecture-focused portfolio project.**
*   It exists to demonstrate contract-first backend/API design, testing, CI quality gates, security posture, fake-provider AI boundary, and mobile TypeScript view-state architecture.
*   It is not currently a production SaaS, commercial product, or fully rendered mobile app.

---

## 2. Success Criteria

The project is successful if:
*   A reviewer can understand the architecture from README/docs.
*   The local demo script runs and proves the API flow.
*   CI/test/security gates are green.
*   CV/portfolio wording can honestly describe the project without overclaiming.
*   Deferred gates are clearly documented.

---

## 3. Non-Goals

The following are explicitly out of scope:
*   Production AI
*   Live OpenAI integration
*   OpenAI SDK installation
*   Rendered React Native / Expo app
*   Supabase/RLS runtime
*   Production persistence
*   Offline-first sync completion
*   Commercial users/revenue
*   Feature growth without portfolio/demo value

---

## 4. IDSD Layering Rules

*   **Intent Layer**: Stable mission and success criteria.
*   **Spec Layer**: Docs/plans/specs that must stay aligned with intent.
*   **Execution Layer**: Agent tasks, slices, checklists, commits, tests.

### Layering Constraints:
*   Spec can change if context changes.
*   Execution can change if implementation facts change.
*   **Intent must not be silently overridden by a spec or agent task.**
*   If a spec conflicts with intent, stop and ask for review.
*   If a slice passes tests but does not improve intent, defer it.

---

## 5. Build / Stop Rules

Before any future slice, the agent must answer:
1. Which intent does this serve?
2. What portfolio/demo value increases?
3. Is this needed, or merely possible?
4. Does it open blocked gates?
5. If we do not do it, does the project become weaker?

### Task Classification:
*   **A: Intent-critical** → Allowed
*   **B: Demo-value** → Allowed
*   **C: Risk-reduction** → Allowed
*   **D: Nice-to-have** → Defer
*   **E: Spec-churn** → Stop

---

## 6. Current Freeze State

*   Feature work is paused.
*   Search/filter is deferred.
*   Repository is ready for portfolio/release review.
*   New product slices require an explicit new product goal.

---

## 7. Agent Rules

### For Antigravity (AG):
*   Docs/planning/review only unless explicitly authorized.
*   Must not expand scope.
*   Must not invent implementation work.

### For Codex:
*   Coding/testing/refactor only after a reviewed implementation prompt.
*   Must stop if package/lockfile/env/SQL/Supabase/OpenAI/Expo gates are needed.
*   Must not auto-proceed to the next slice.

### For ChatGPT:
*   Remains review gate.
*   Must challenge whether a slice is worth doing.
*   Must prevent overbuilding.

---

## 8. Overclaim Guardrails

Do not claim:
*   No production AI
*   No live OpenAI
*   No rendered mobile app
*   No deployed app
*   No Supabase/RLS runtime
*   No persistent summary history
*   No completed offline sync
*   No users/revenue

---

## 9. Future Reopen Criteria

Feature work may resume only when:
*   User states a concrete product goal.
*   Expected value is higher than churn.
*   Blocked gates remain untouched or are explicitly approved.
*   Verification plan is clear.
*   Scope is small and reversible.
