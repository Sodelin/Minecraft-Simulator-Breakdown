# Handoff for Dot / next research agent

## Start here

Continue the user's Minecraft simulator audit. The user admires RedLogic's mathematical explanations, bought Prototypers and Source Architects, wants a fair source audit and a better simulator, and requested this handoff before more experiments. Preserve the work below. **Do not restart the research, publicly publish purchased source, contact the creator, or call the current model optimal/vanilla-verified.** The user will handle Patreon contact after the work is ready.

Public research home: https://github.com/Sodelin/Minecraft-Simulator-Breakdown . The related Research Commons exists at https://github.com/Sodelin/Research-Commons ; it has not been changed in this task. The current chat's assistant had no direct Dot communication API. This document and the saved private package are the interface.

## What exists

Private download: `minecraft-simulator-audit-private.zip` includes the working C source/binary, viewer, patch, original terms, seed manifest, original rich replay, corrected-timestamp derivative, tests, evidence, triage and private message drafts. Public repository includes only original research notes and independently written tools. The native C derivative and modified viewer are intentionally private.

Workspace if still available: `/workspace/scratch/80ab83997ccd/minecraft-audit/`.

- `source-original/Source Architects/Native/src/mcmacro.c`: untouched source.
- `original/Prototypers/`: extracted relevant docs/viewer/data/executables.
- `baseline/mcmacro.c`: only a missing forward declaration was added; compiled baseline and logs.
- `release/`: final private deliverable source, tools, report and verification.
- `evidence/`: older game-code witnesses, excluded from deliverable; do not redistribute.
- User uploads: `upload/01-Prototypers.zip`, `upload/01-Source-Architects.zip`.

Archive SHA-256s: Prototypers `5d0c118668636c0d3016770e022522d723aa5a9a92dfdc61b87cbeeb0133a7aa`; Source Architects `a29ce5c1baa605719ae4da19943b1bd8c1731ef49f15d7dd85b439caf80b3587`. See `PROVENANCE.json` for source hashes.

## Confirmed findings

Read `AUDIT_REPORT.md` sections 6–12, `TRIAGE.md`, `MODEL_REVIEW.md` and machine evidence. Core issues repaired: build declaration, stale milestone clocks, partial counter resets, terminal cap, exact seed metadata, completion classification, numeric/time batch ranking, inaccurate geometric sampling, misleading terminal mechanism text. Viewer repairs: exact large integers, strict imports, preservation of zero health, interpretation of partial/outcome records and evidence warnings.

Bigger unresolved issue: regional/hostile encounters occur per loop iteration rather than physical elapsed time. Pickup count and time are independently sampled. These need a calibrated shared-clock model, not an arbitrary probability tweak. Model assumptions about loading/spawning, resources, spatial compression and End hazards are disclosed or unvalidated; distinguish both from coding errors.

## The most valuable reproduction result

World seed unsigned `17911097197626437575` (signed `-535646876083114041`); event RNG `7897602236245615709`; target manifest Minecraft 1.21.4.

Unassisted baseline/logging-corrected 45-second runs stopped at route 0. All 758 comparable recorded trajectory events matched exactly; their final clocks differ due wall-time throughput. The final distribution fix was applied after this comparison.

With **`--rng-help 80`**, a later corrected run matched all first 19 major events and the first 978 comparable resource/golem records from the supplied winning replay **exactly**. At 60 seconds it had all ten crystals destroyed, one four-point dragon hit, health196, and time262219866.103013 model years. Firsthit226073682.138671 matches supplied exactly. This identifies a configuration matching a large historical prefix, but **full completion remains unreplicated**. Do not make an exact archival-command/source-version claim from a prefix alone.

Original replay:38damage hits,206damage, final1975124500.924769 model years. All damage milestones incorrectly share13.172536m; matching resources give true times226.073682m–1975.124501m. Resource/counter ledger is sampled. One model year = 8,760,000 ticks, about5.069civil days at 20 TPS; finalduration≈27.4million civil years, under modelassumptions.

## Verification already completed

- Seven native helper tests pass under ASAN+UBSAN; actual deterministic1000-step run also passes without diagnostics. LSAN unavailable due environment, not a claimed memory pass.
- Two unassisted1000-step JSONLs are byte-identical, SHA `eacc5cb15362a34b3321048e03d60eeadca45bfe514f5d62ed0e6638b4bba9bf`.
- Nine Python replay/runner tests, five CTMC tests (30000 synthetic histories), eight viewer checks pass.
- `results/assisted80-audit.json` has no available-check findings, health196 and all three End entity-accounting deltas0.
- Two-run runner smoke test retains both censored runs. Do not use it as a statistically informative completion estimate.

## Reproduce commands

From unpacked private package root:

```sh
gcc -O2 -std=c11 src/mcmacro.c -lm -o bin/mcmacro
python3 -m unittest discover -s tests -p 'test_*.py' -v
node tests/viewer.test.js
gcc -O1 -g -fsanitize=address,undefined -fno-omit-frame-pointer tests/core_harness.c -lm -o tests/core_harness
ASAN_OPTIONS=detect_leaks=0 ./tests/core_harness
./bin/mcmacro --seed 17911097197626437575 --rng-seed 7897602236245615709 --seed-manifest inputs/seed_manifest.jsonl --rng-help 80 --runtime-seconds 60 --no-schems --quiet --replay results/continuation.tsv --replay-jsonl results/continuation.jsonl
python3 audit_replay.py results/continuation.jsonl
```

Replay is an observation ledger, **not a resumable engine checkpoint**. A longer run starts from the same seeds; there is no engine resume facility. `--audit-max-steps 1000` provides deterministic outer-loop stopping. Default omitted runtime means uncapped; explicit `--runtime-seconds 0` is rejected by current CLI. Native multi-run wrappers are Windows-specific; `ensemble.py` is portable and retains all runs. The bundled binary is Linux, not Windows.

## Next actions in order

1. Finish the historical assisted reproduction if useful, retaining all flags/source/input hashes. Compare typed events and matching damage/health sequence, not only final time. Explain assistance clearly.
2. Improve speed without changing trajectories: `macro_loose_tnt_total` scans36872entries repeatedly though suppliedmanifest has 1617 local nodes+8 far. Candidate graph-aware sums can use active nodes only **after verifying unused pools are always zero**. Benchmark-O3 orvectorization separately. No optimization was implemented or measured before handoff.
3. Define the contract: literalzero players ever present vs no inputs after setup, target version, chunk activity, spawning/modifications, initial dragon/fight state, world border, finite blocks and permitted conditions. Audit Java integration/build mappings before claiming game truth. Original sourceREADME requires matching external MCP; Java 17 here is insufficient.
4. Implement target-version fixtures for pickup/placement, actual carved pumpkin plus two snow blocks, portal traversal, dragon initialization, crystal projectiles, retaliation/explosion and damage. Record failures and setup; schematics alone are not execution proofs.
5. Calibrate and validate spatial/first-passage reductions against held-out traces. Then use `event_kernel.py` only for appropriate Markov constant-hazard transitions, or extend semi-Markov/event queue behavior. No Minecraft rates are supplied by this kernel.
6. Choose objectives: feasibility, probability by physical horizon, time quantiles, favorable seed search, error per compute budget, visual explanation. Prefer an explicit Pareto comparison to “optimal simulator.”
7. For rare events, retain likelihood weights/support/lineages. RNG-help alone is not an unbiased estimator. Wall timeout may be informative censoring; completed-only means/medians are not unconditional estimates.
8. Prepare concise triaged findings for optional creator feedback. Drafts are private, unsent; user will send via Patreon when ready.

## Stop / honesty conditions

No engine oracle executed, no unassisted completion, no full historical completion, no exhaustive audit, noWindows build verification, noUI browser visual verification, no formal paper located. The corrected native model is usable and better instrumented; remaining assumptions are material. Do not turn the synthetic kernel benchmarks into claims about Minecraft.
