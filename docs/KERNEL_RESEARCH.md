# A reusable event scheduler for the next model

`event_kernel.py` is an exact competing-hazard scheduler **for the CTMC supplied by its caller**. It is a research component alongside the repaired original simulator. It does not supply Minecraft physics, replace the original model, or certify its assumptions. The synthetic benchmark rates below are arbitrary analytic test rates and must never be presented as Minecraft encounter rates.

For transitions with constant hazards `a_i(state)` per tick, the kernel samples an exponential waiting time with total rate `A = sum(a_i)` and selects event `i` with probability `a_i/A`. Every transition advances one common clock. The initial state, RNG seed, event count, terminal status, physical tick, and optional event trace are returned. A physical horizon truncates the final waiting interval. Event-budget exhaustion raises an error, so it cannot masquerade as physical-horizon censoring. The RNG stream continues across calls; instantiate a fresh kernel with the same seed to reproduce a history.

```python
from event_kernel import EventKernel, Transition

def synthetic_rates(state):
    if state != 'start':
        return []
    return [Transition('A', 1.0, 'A'), Transition('B', 3.0, 'B')]

result = EventKernel(2026).run('start', synthetic_rates, horizon_ticks=100,
                             record_trace=True)
```

This synthetic process has mean absorption time `1/(1+3) = 0.25 ticks` and absorption probability `P(A)=1/(1+3)=0.25`. Run `python3 event_kernel.py` for the seeded 12,000-history comparison. The unit tests also check a rare event with target hazard 0.01 and proposal hazard 1, over a one-tick horizon; the exact target probability is `1-exp(-0.01)`. They verify the weighted estimate and total expected weight, including survival weights.

## Optional importance sampling

Pass a `proposal(state)` callback with the same transition names and destinations but altered hazards `b_i`. Every positive target transition must have positive proposal hazard; missing support and changed destinations are rejected. A proposal-only transition receives zero target path weight, so it cannot contribute an impossible target success. Its presence does not make such a transition physical.

The kernel accumulates the continuous-time path likelihood ratio:

`log w = sum_events log(a_i / b_i) - integral (A - B) dt`.

It includes the censored interval's survival contribution. Use the ordinary estimate `mean(weight * outcome)`, with independently sampled proposal histories and valid uncertainty estimates. Dividing only by the total weight produces a different, generally biased finite-sample estimator. Work in log space for extreme weights; the convenience `weight` property can overflow for very large positive log weights. Initial-state or seed-selection proposal weights, ensemble bookkeeping, effective sample size, and confidence intervals are the caller's responsibility. The tests establish the numerical method on synthetic analytic cases, not accuracy of game estimates.

## Wiring validated game mechanisms

1. Define a setup contract: target version, actual loaded chunks, spawning changes, initial dragon/fight state, border geometry, seed conditioning, finite resource inventory, and permitted actions.
2. Execute reproducible target-version fixtures, retaining failures, to estimate encounter and transfer distributions and verify legal transitions. Exported schematics alone are insufficient.
3. Construct a sufficient state: resource ownership, entity locations/health, excavation geometry, dimension progress, and time-dependent environmental variables. Test conservation invariants after every event.
4. Supply only calibrated hazards that are constant between state changes. Include pickups, golem movement/death, encounters, and useful or destructive events in the same clock rather than performing Bernoulli checks per software iteration.
5. Validate held-out first-passage curves, joint outcomes, and spatial-resolution convergence. A simple node-level Markov model need not preserve boundary-entry position or wandering history. If hazards vary with time or waiting distributions are non-exponential, augment state or implement integrated-hazard/semi-Markov scheduling; this kernel does not handle those cases automatically.
6. Keep every seed/history result, config and manifest hash, assistance/proposal setting, target/proposal weight, and terminal reason. Distinguish true extinction, a physical horizon, a computational timeout, and an event-budget exception. A wall timeout may produce informative censoring and is not automatically suitable for a standard survival estimator.
7. Benchmark accuracy per computational budget before calling any method better. Conditional-world completion probabilities, seed-search efficiency, minimum observed time, expected time, and mechanism feasibility are separate objectives.

Run validation from the release directory:

```sh
python3 -m unittest discover -s tests -p test_event_kernel.py -v
python3 event_kernel.py
```

State snapshots must be immutable if traces are requested. Transition names must be unique within a state; destination objects must support meaningful equality checks. Hazards must be finite and nonnegative. Exactness here refers to the supplied CTMC distribution up to floating-point arithmetic, not bit-for-bit engine replay or a proof about Minecraft.
