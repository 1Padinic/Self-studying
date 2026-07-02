# Cheat-sheet: How to interrogate model predictions

## The 7 questions to always ask

1. **What kind of model is it?**
   Optimization (least-cost, assumes rational frictionless behavior → optimistic) vs. simulation (behavioral rules, historical calibration → conservative) vs. accounting/cost-curve (no feedbacks). The architecture *is* a hidden assumption.

2. **What's the counterfactual?**
   A policy's "impact" is always *scenario minus baseline*. Half the headline range usually lives in the baseline (fuel prices, GDP, technology costs), not in the policy itself.

3. **Which assumptions drive the result?**
   Find the 2–3 levers the outcome is most sensitive to (e.g., transmission build rate, ETS price, subsidy uptake). Ignore the other hundred inputs.

4. **What's exogenous vs. endogenous?**
   Things fed *into* the model (fuel prices, behavior, permitting speed) can't be "predicted" by it. Real-world frictions outside the model (siting, litigation, supply chains) almost always bias reality below the modeled outcome.

5. **Is it a forecast or a conditional scenario?**
   Nearly always the latter: "*if* these assumptions hold, *then* X." Never quote the point estimate without its conditions.

6. **Who made it and can you check it?**
   Academic / consultancy / government / advocacy — each has systematic tilt. Open-source and documented > proprietary black box.

7. **Do independent models agree?**
   Convergence across *different architectures* is strong evidence for the direction and rough magnitude. Divergence tells you where the real uncertainty is.

## Rules of thumb for reading the numbers

- **Trust deltas, not levels.** The difference between scenarios (with vs. without policy) is more robust than any absolute number — shared baseline errors cancel.
- **A range is information, not weakness.** A single point estimate from a complex system is a red flag; ask what was varied to get the band.
- **Check the base year and units.** (% vs. 2005 ≠ % vs. 1990; CO₂ ≠ all GHG; incl./excl. land sink.)
- **Discrete beats continuous in small systems.** In small countries/sectors a few lumpy decisions (one nuclear plant, one coal closure) dominate; sensitivity analysis matters more than model detail.
- **The actionable finding is usually the gap** — where all scenarios fail a target — not the headline success number.
- **Follow the incentives:** uncapped subsidies → outcome scales with uptake (behavioral uncertainty); caps/mandates → outcome scales with enforcement (political uncertainty).
