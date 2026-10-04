# Minecraft simulator review — bounded audit and working revision

## 0. Result

The purchased source contains a substantial, thoughtfully decomposed Monte Carlo model. We built and repaired its native C engine, corrected replay interpretation, added reproducibility and ensemble tools, and independently tested the changes. We also built an exact competing-hazard research kernel. **Neither the repaired engine nor the new kernel is a vanilla Minecraft proof or an optimality certificate.** The next step is validation of the intended experiment and its indispensable mechanics.

## 1. Scope

Review target: RedLogic’s [Running Minecraft Until It Beats Itself](https://youtu.be/9t2fV52jMA8), the supplied Prototypers archive, and Source Architects archive. This review directly inspected the purchased implementation and replay evidence. It did not obtain a complete video transcript or execute Minecraft 1.21.4. Source Architects is a source package with technical documentation; we did not identify a separate formal research paper in the inspected material.

## 2. Evidence and provenance

The core is `Native/src/mcmacro.c`, approximately 12,090 lines in the untouched package. Its Java integration depends on an external matching MCP-Reborn workspace, absent here; available Java is 17, while that integration needs a newer matching toolchain. The supplied seed manifest identifies Minecraft 1.21.4. The two original archives remain untouched. SHA-256 hashes are in the private `PROVENANCE.json`; source changes are supplied as a patch.

Original source line numbers in `TRIAGE.md` and `MODEL_REVIEW.md` refer to the untouched C file. Static inspection, native execution, synthetic analytic tests, and target-game verification are different evidence classes throughout this report.

## 3. What the author appears to optimize

The documentation describes an abstract, fast, event-driven thought experiment conditioned on a rare suitable world. It develops a complete proposed causal chain and produces illustrative histories. Some settings and scripts select the most successful history from many trials. That serves mechanism exploration and explanation; the selected winner is not a typical waiting-time estimate.

Ignored player loading, spawn caps and despawn are declared simplifications. The package also describes constrained End reconstructions and between-event visualization. These are scope choices to evaluate, not evidence of deception.

## 4. The supplied winning replay

`replay_updated.jsonl` contains 3,668 records, 38 damage milestones and 206 nominal damage points against 200 health, with terminal health clamped to zero. All 38 damage milestone clocks incorrectly read 13,172,536.7133 model years. Their matching damage/health resource records span 226,073,682.138671 to 1,975,124,500.924769 model years. Pairing is exact in emission order, damage and remaining health. The latter records and terminal event are internally consistent about damage chronology.

There are 187 counter frames whose health exceeds a preceding matching damage outcome. The last sampled resource counter can describe 200 health after damage has occurred. The ledger is selected evidence, not a complete block/entity inventory. Its 65 adjacent clock reversals cannot all be called errors: resource histories can legitimately be emitted retrospectively.

## 5. Execution and reproduction

GCC C11 initially rejected a call to `macro_choose_edge` preceding its declaration. A declaration-only baseline allowed comparison. Baseline and logging-corrected unassisted runs with the supplied world/event seeds, manifest and 45-second wall cap both stopped before opening the route. Independently, all 758 comparable recorded trajectory rows matched exactly. Their final simulated clocks differ with throughput; wall-time censoring is not deterministic stopping.

A later **80% RNG-help run** matched the supplied replay’s first 19 major events exactly and its first 978 comparable resource/golem events exactly. It reached all ten crystals destroyed and the first four-point dragon hit at 226,073,682.138671 model years. At a 60-second cap it stopped at 262,219,866.103013 model years, health 196. This is strong evidence identifying a configuration matching the historical prefix. It is not yet a full historical replay reproduction, and does not prove the exact archival command or source revision. Do not characterize that supplied trace as an unassisted estimate.

## 6. Confirmed implementation defects

The triage document provides reproduction details and bounded fixes:

- Missing forward declaration prevents this native build.
- Full-chain milestone calls use an outdated global clock instead of the phase clock.
- Resource-only counters assert zero route/crystal progress and full dragon health despite having no authority over those fields.
- A global counter cap can suppress death/terminal evidence.
- JavaScript numeric parsing rounds 64-bit seeds, and a zero-health fallback can revive the displayed health.
- The viewer silently accepts malformed lines if a manifest exists.
- Batch outcome inference treats exit zero as dragon death.
- Scalar batch ranking loses lower-priority distinctions to floating-point precision and, where elapsed time distinguishes runs, favors greater time.
- The compressed geometric-count formula is approximate even at p=0.24 and p=1. At p=0.24 its mean is 4.686647493 rather than 4.166666667, about 12.48% too high. This is a count/clutter issue; it does not establish that completion times are 12.48% too high.
- The final explanatory note hard-codes TNT despite creeper damage in the fixture.

## 7. Structural modeling questions

Some hostile/golem encounters are fixed Bernoulli decisions per outer loop, while selected resource work advances time. Consequently encounter opportunities per simulated year depend on workload. Replacing those with arbitrary new rates would not repair the scientific model. A common clock needs calibrated hazards or appropriate non-exponential first-passage kernels.

Successful pickup time and failed-attempt count are independently sampled. Exponential thinning gives a valid time marginal under the assumed Poisson process, but independent counters are not a joint microscopic history. RNG-help changes encounter, placement, survival, direction and sometimes stage behavior without likelihood weights; it is a different assisted model. Structure existence, optional room inventory, far-world density, spatial aggregation, crystal routes and End damage all need matching-version empirical checks. See `MODEL_REVIEW.md`.

## 8. Several optima

| Goal | Appropriate objective | Required evidence |
| --- | --- | --- |
| Feasibility | Does any legal positive-probability path exist in the specified setup? | Engine fixtures and dependency-consistent state |
| Waiting time | Conditional distribution or chosen quantile of completion time | Calibrated clocks and all histories |
| Success probability | Completion probability by a physical horizon | Unassisted samples or valid weighted rare-event estimation |
| Favorable-world search | Minimize a declared time functional over permitted seeds | Exact seed constraints, search budget and conditioning |
| Computational efficiency | Minimize cost at fixed error or uncertainty | Reference comparison and convergence |
| Explanation | Understandable, truthful causal history | Provenance and clearly labeled reconstructions |

A fastest sampled history, minimum expected time, minimum median time and most probable route are different optimizations. Number theory and combinatorics may improve seed search or constrain reachability; they do not infer encounter rates from nothing.

## 9. Delivered implementation

The private revision includes corrected C source, a Linux executable, a patch, corrected viewer, exact integer parsing, strict imports, replay audit and explicit timestamp derivative, portable ensemble runner, deterministic outer-loop budgets, retained terminal/censor records, units and assistance metadata, enforced End accounting failures, exact geometric counts, and lexicographic batch ranking. The ranking policy now prefers faster completed histories; incomplete runs are ordered by explicit progress fields, then time. No extra random draws were introduced for the geometric repair.

The independently written `event_kernel.py` offers a common tick clock, competing hazards, horizon stopping and optional target/proposal importance weights. Its synthetic rates are **not Minecraft rates**. It is a component for the next validated model, not a replacement full-game simulator.

## 10. Validation

Seven native harness checks passed, including clock/RNG preservation, partial frames, terminal frames, outcome classification, exponential/geometric sanity checks and ranking. AddressSanitizer and UndefinedBehaviorSanitizer passed the harness and an actual 1,000-step run; LeakSanitizer was unavailable in this environment. Two unassisted 1,000-step runs produced identical JSONL bytes and truthful stronghold-stage censor summaries.

Nine Python replay/runner checks, five CTMC analytic checks and eight viewer checks passed. The CTMC tests use 30,000 synthetic histories, including weighted rare-event and survival likelihoods. The 80% assisted run has no inconsistencies under the available replay checks and reports zero End entity-accounting deltas. These checks establish the tested software properties, not full inventory conservation or vanilla physics.

## 11. Negative results and unperformed work

No unassisted dragon completion was observed in this audit. No complete historical replay reproduction was completed. No matching Minecraft engine oracle was built or executed. Scanner candidate correctness, Java exporter correctness, every optional structure piece, full block conservation, resolution convergence and calibrated End hazards remain unverified. The existing native batch orchestration is Windows-specific; only the comparator was unit-tested here, not Windows multi-process execution. The corrected browser logic was tested in Node; its visual UI was not exercised in a browser.

## 12. Uncertainty and interpretation limits

The selected historical replay and different test fixtures are not interchangeable independent trials. Assistance settings, source revision and search conditioning must accompany conclusions. A wall-time timeout depends on the trajectory’s work and may be informative censoring; do not automatically fit an ordinary survival curve or call completed-only statistics population estimates. The runner’s completion fraction refers to its compute budget and conditional model, not vanilla completion probability.

One model year is 365 Minecraft days: 8,760,000 ticks, or 438,000 nominal real seconds at 20 ticks/s. Thus the 1.975-billion-model-year duration is approximately 27.4 million civil years at uninterrupted nominal tick rate, not 1.975 billion civil years. Neither figure is a validated vanilla prediction.

## 13. Next steps and communication

The user requested transition to Dot. `HANDOFF.md` gives the exact continuation order: finish assisted prefix reproduction, recover configuration provenance, define the experiment, validate indispensable mechanics, then calibrate a reduced model and choose an estimator/search objective. A potential speed improvement is reducing repeated pool scans to active graph nodes, with unused-pool invariants and byte-identical trajectory checks before adoption. No measured speedup is claimed.

The user will handle any creator contact later through Patreon. Drafts are private and unsent. Lead with small reproducible defects, offer calibration questions separately, and respect the creator’s declared goals and considerable work. The public repository contains original research notes and newly written tools; purchased source, derivatives, original replay data and third-party snapshots are excluded.

## 14. References

- [Original video](https://youtu.be/9t2fV52jMA8).
- Purchased Prototypers: `Docs/PROJECT_README.md`, `Docs/DEVLOG_NOTES.md`, replay and seed manifest.
- Purchased Source Architects: README, native C source and Java integration. Personal-use terms preserved in the private package.
- Gillespie, D. T. (1977), [Exact stochastic simulation of coupled chemical reactions](https://doi.org/10.1021/j100540a008). Background for a stated stochastic event model; not a Minecraft validation.
- [Unbiased Simulation of Rare Events in Continuous Time](https://doi.org/10.1007/s11009-021-09886-2). Background on rare-event acceleration with statistical correction.
- Primary game-code witnesses previously inspected were an older-version snapshot, not target-version 1.21.4 certification; their full copyrighted source is excluded from deliverables.
