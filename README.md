# Minecraft Simulator Breakdown

A source audit and research workbench for RedLogic’s [Minecraft self-completion project](https://youtu.be/9t2fV52jMA8). We distinguish software defects, disclosed simplifications, unvalidated mechanics, and different optimization goals. This is an AI-assisted review; findings remain open to correction.

Start with [the report](docs/AUDIT_REPORT.md), [triage](docs/TRIAGE.md), and [continuation handoff](docs/HANDOFF.md). The historical assisted replay has been reproduced through a substantial prefix, not full completion. No target-version Minecraft oracle or unassisted completion was executed.

This repository contains original research notes, aggregate evidence and independently written tools. Purchased source, modified source/viewer, original replay assets and third-party snapshots remain outside this public repository. No creator contact has been made.

## Tools

- `audit_replay.py`: strict JSONL loading and cross-record evidence checks; optional explicit timestamp derivative. Requires a locally obtained compatible replay.
- `ensemble.py`: retains all histories, commands, hashes and censoring. Requires a locally supplied compatible native executable and manifest; those are not distributed here.
- `event_kernel.py`: exact competing-hazard scheduling and optional likelihood weights for a caller-specified CTMC, **not Minecraft physics**. Synthetic rates are analytic test rates.

Run the independent tests with `python3 -m unittest discover -s tests -p 'test_*.py' -v`. Read [kernel assumptions](docs/KERNEL_RESEARCH.md) before interpreting any benchmark. Native/viewer tests and private engine are supplied separately to the purchaser.

The proposed next stage is a setup contract and matching-version engine fixtures, followed by calibration, reduced-model validation and an explicit estimation/search objective. There is no claim of a universally optimal simulator.
