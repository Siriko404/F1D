# §III.E Reverse-Causality Defense Restructure — Decision Tracker

**Started:** 2026-05-13
**Status:** ACTIVE — update as decisions evolve
**Anchor memory:** `~/.claude/projects/<id>/memory/feedback_endo_defense_final_hierarchy.md`

---

## Scope note

This tracker addresses the **reverse-causality (RC)** threat specifically. §III.E covers multiple endogeneity threats; the locked hierarchy below is RC-only. Other threats live in parallel:

| Threat | Primary defense | Status |
|---|---|---|
| Reverse causality | Tier hierarchy (D6 below) | **LOCKED this session** |
| OVB (industry×time, firm×year) | FE rotation today | SHIPPED commits C1-C6 (`e6a31fb`→`a32da03`); UncAnsMgr inferences survive |
| Measurement error (generated regressor UncResCEO from DWZ) | Not addressed | OPEN — Murphy-Topel / bootstrap deferred |
| Selection (F1D call panel restriction) | Hasan-population diagnostic on full Compustat | SHIPPED prose at `section_3_main.tex:78` |

---

## Locked decisions (this session)

### D1 — 12-cell ladder kept (2026-05-13)
- Both Cash_t and Cash_{t+1} retained as DV horizons.
- Reason: Cash_{t+1} is temporally inoculated from RC (future ↛ past); Cash_t spec retains contemporaneous evidence with mitigated-not-eliminated RC threat.
- Spec table verified: 12 cells = (industry, firm) × (Year, YearQuarter) × (Cash_t, Cash_{t+1}) with base/extended control toggle on first 4.
- Source memory: `feedback_endo_defense_focused_on_cash_t.md`.

### D2 — Modus tollens moderator argument FAILS (2026-05-13, advisor round 1)
- Sina's polished argument claimed: moderators (Unrated, HighCFvol) exogenous to BOTH cash and speech → interaction amplification = forward-arrow evidence.
- **Killed by**: Bates 2009 (`section_2_framework.tex:12`), ACW 2004 + Han-Qiu 2007 (`:14`) — all establish moderators *correlate with cash-policy structure* (unrated/HighCFvol firms hold larger + more variable cash).
- Implication: reverse arrow Cash → Speech ALSO predicts amplification at moderators (more cash → more cash-talk under reverse story).
- Both arrows make same prediction → interaction coefficient is NOT arrow-discriminating.
- **Polished prose drafted earlier this session is RETRACTED. Do not ship.**

### D3 — H1a + H1b moderators KEPT as framework hypothesis tests (2026-05-13)
- Per `section_2_framework.tex:30, 34`, H1a and H1b are stated hypotheses, not just defense props.
- They test precautionary stress amplification per ACW04 + HQ07 framework — a substantive theoretical claim independent of RC defense.
- Direction-consistent 8/8 pattern remains informative about precautionary mechanism even if not about arrow direction.
- **Action**: keep §III.C, §III.D content intact. Drop "modus tollens" framing from these sections.

### D4 — DiDs CANNOT discriminate forward vs reverse arrow (2026-05-13, Sina-derived mediation-DAG insight)
- Sina identified: even if all DiD premises sig (Shock → Cash, Shock → Speech, main panel Speech ↔ Cash), Shock → Speech could route via Cash (mediation through cash policy).
- Three DAGs all predict joint sig:
  - FORWARD: Shock → Speech → Cash
  - REVERSE: Shock → Cash → Speech
  - NEITHER: Shock → Speech, Shock → Cash (common cause; no direct speech-cash link)
- Joint sig is mechanism-existence evidence, NOT arrow-direction evidence.
- Strict discrimination would need: mediation analysis OR asymmetric shock OR IV. **IV out of scope per Sina.**

### D5 — Cash-arm vs Speech-arm DiD split (2026-05-13, advisor round 2)
- Cash-arm DiDs: Brexit (DiD_10K), Boasiako, Hasan-full-Compustat all sig. **Cash channel validated.**
- Speech-arm DiDs: 4/5 null + 1 positive-sign-not-significant (Chen Variant B β=+0.1380, p_one=0.229 — direction-consistent but statistically null). **Speech channel NOT validated.** Do not shade with "promising"; p_one=0.229 doesn't qualify.
- Speech-arm null is NOT a "thin caveat" — it's a finding that constrains interpretation.
  - Referee will ask: "If Brexit didn't move speech, what does speech capture?"
  - One natural answer: cash position (reverse arrow).
  - Speech-arm null = empirically-relevant in wrong direction, not neutral.
- **Action**: report cash-arm + speech-arm asymmetry explicitly in §III.E.4 prose.

### D6 — Final tier hierarchy LOCKED (2026-05-13, advisor round 2)

```
TIER 1  PRIMARY (ironclad):
        Cash_{t+1} temporal asymmetry. Future ↛ past.
        RC dead for lead spec by construction.

TIER 2  AUXILIARY (mechanism EXISTENCE only, not arrow direction):
        Cash-arm DiDs validate uncertainty → cash causal channel.
        Speech-arm DiDs mostly null → speech-side mechanism
        validation absent in F1D; reported honestly.

HONEST REPORTING (Cash_t spec):
        Cash_{t+1} regression: forward arrow identified by
        temporal asymmetry. Cash_t regression: forward arrow
        NOT strictly identified. Magnitude/sign consistency
        with Cash_{t+1} (β range +0.0016 to +0.0028 across 12
        cells, no horizon-discontinuity) supports inference
        that the same causal channel operates at both horizons,
        but supplementary not identifying. Strict identification
        = IV (out of scope).

NOT LOAD-BEARING (demoted):
        H1a/H1b moderators — cannot defend RC per Bates/ACW/HQ.
        Kept as framework hypothesis tests per §II.2.
```

### D7 — Three tests for future framings (advisor anti-oscillation directive)
1. Does it strictly identify arrow direction without IV? (No → not RC defense)
2. Does it require empirical premises F1D delivers? (Check before claiming)
3. Does cited literature support or contradict the exogeneity claim? (Bates/ACW/HQ test)
If any answer is no, hold the line. Do not re-litigate.

---

## Pending prose work (mapped to existing tasks)

- **Task #112** — §III.E.4 paragraphs (Brexit + Boasiako + Chen) framed per D5 + D6. Cash-arm validated, speech-arm null reported, mediation-DAG ambiguity acknowledged, IV out of scope explicit.
- **Task #114** — §III.E intro (`section_3_main.tex:57-63`) rebuilt around D6 tier hierarchy. Cash_{t+1} primary, moderator+DiD framings demoted.
- **Task #113** — Boasiako Knightian vs probabilistic risk framing (separate concern, not blocked by this restructure).
- **Task #111** — ACW04+HQ07+FW06 lit-review (no longer needed for moderator-exogeneity defense per D2; may still be useful for §II.2 hypothesis-justification prose).

---

## Open items (not yet decided)

- Spec C OVB rotation (today's work, commits e6a31fb → a32da03): how to integrate into the tier hierarchy. Currently shows moderator interactions go to 0/6 NS under stricter FE — corroborates D2 (moderator argument empirically weak).
- §III.E.4 prose: Brexit speech-arm "promising-NS" treatment (was it 1 or 0 promising cells?). Verify before drafting.
- ~~Mediation analysis option~~ — **CLOSED: NOT FEASIBLE.** Mediation analysis requires significant first stage (Shock → Speech), which F1D delivers in 0/5 DiDs strictly. Chen 1/5 positive-sign cell has p_one=0.229, well above any conventional threshold. Reopen only if speech-arm empirics change.

---

## Update log

| Date | Decision | Trigger |
|---|---|---|
| 2026-05-13 | D1-D7 above | Session work, 2 advisor rounds, Sina mediation-DAG insight |
| _next update_ | _add as decisions evolve_ |  |
