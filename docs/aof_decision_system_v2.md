# AOF Decision System V2

## Purpose

AOF v2 expands OPB from a simple short-stack jam/fold profile into a short-stack decision leak engine.

The product rule is:

- do not correct coolers,
- do not punish standard all-ins that lose,
- do correct repeated hand-selection, calloff, multiway, satellite, and premium-induce mistakes.

## Situation Taxonomy

The v2 detector currently classifies short-stack preflop spots into:

- `unopened_open_decision`
- `premium_induce_candidate`
- `facing_open_decision`
- `facing_open_reshove`
- `facing_jam_calloff`
- `multiway_after_open`
- `multiway_all_in_decision`
- `other_short_stack_decision`

This is intentionally broader than AOF v1, which only covered unopened Hero decisions.

## Decision Quality Buckets

Each spot receives one high-level quality bucket:

- `standard`
- `mistake_candidate`
- `non_mistake`
- `operator_defer`

`non_mistake` protects cooler / runout territory from fake correction.

`operator_defer` keeps PKO, satellite, multiway, and unclear contexts inspectable without over-grading them.

## Mistake Families

Current v2 mistake families include:

- `too_wide_open_jam_12_15bb`
- `premium_missed_induce`
- `too_tight_premium_fold`
- `too_wide_reshove`
- `bad_calloff_candidate`
- `satellite_survival_violation`
- `multiway_overcommit`
- `too_tight_monster_fold`

These are product families, not final solver verdicts.

They are meant to become repeatable correction targets after operator review and baseline approval.

## Current Corpus Read

Current local Hero corpus:

- short-stack decisions: `3721`
- mistake candidates: `75`
- mistake candidate rate: `2.0%`
- non-mistake / cooler-protected examples: `467`
- operator-defer spots: `1418`
- standard spots: `1761`

Top early families include:

- `multiway_overcommit`
- `bad_calloff_candidate`
- `satellite_survival_violation`
- `too_wide_open_jam_12_15bb`

## Caveats

This is not solver-grade EV truth.

Position extraction is still incomplete, and exact opener position / stack geometry is not fully modeled yet.

The next major upgrade should infer positions from GG seat/button metadata and introduce an operator-approved AOF baseline table.
