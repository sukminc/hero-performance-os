# AOF Implementation Profile V1

## Purpose

This surface compares Hero's real short-stack AOF behavior against a deterministic v1 baseline.

It answers:

- when does Hero actually enter jam / near-jam mode?
- which hand classes repeat?
- which tournament formats create exceptions?
- which 12-15bb jams look suspicious before deeper chart validation?

## Current Scope

Included:

- Hero effective stack `<= 15bb`
- `5+` active seats
- unopened Hero preflop decisions
- real hand classes from `Dealt to Hero`
- action families: `fold`, `open_raise_small`, `open_jam`, `open_almost_all_in`
- format profiles: `standard_mtt`, `pko`, `satellite`

Excluded:

- facing-open reshoves
- facing-jam calloffs
- exact PKO math
- exact ICM / satellite bubble math
- solver EV claims

## Current Read

The current corpus produces:

- AOF opportunities: `1691`
- average opportunity stack: `10.63bb`
- median opportunity stack: `11.28bb`
- average jam / near-jam stack: `9.45bb`
- median jam / near-jam stack: `10.08bb`

Hero's hypothesis that AOF mode appears around `12bb` is directionally supported.

## Important Caveat

Position extraction is still incomplete for many GG hands, so many early AOF pattern cards currently show `position: unknown`.

This means the current layer is useful for:

- stack-depth profiling
- hand-class repetition
- format split
- suspicious 12-15bb jam review queues

It is not yet sufficient for final position-aware chart grading.

## Next Upgrade

Improve position inference from seat/button metadata so the AOF chart deviation layer can separate:

- UTG / HJ / CO / BTN / SB / BB

before issuing stronger coaching claims.
