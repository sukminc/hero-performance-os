# V2 Module Map

## Build here

New active implementation should be placed in:

- `core/`
- `operator_app/`
- `app/`
- `docs/v2/`

## Reference here

Use V1 folders as reference sources when selectively migrating logic:

- `operator/truth/`
- `operator/review/`
- `operator/drafting/`
- `runtime/`
- `qa/`

## Legacy / historical

The following areas should be treated as historical or pending archive candidates rather than active expansion targets:

- `ingestion/`
- `actions/`
- `context/`
- `demo/`
- `frontend/`
- older `tasks/`
- older `reports/`

## Selective migration rule

When logic is useful, migrate it by responsibility into V2 rather than copying folder structure forward unchanged.
