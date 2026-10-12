# llm-eval-dataset-lint

Lint a golden eval set before you trust a score computed on it. A JSONL file of
cases goes in; a list of findings comes out, and the CLI exits non-zero on errors
so it can gate CI.

## Case format

One JSON object per line:

```json
{"id": "q-001", "input": "What is the capital of France?", "expected": "Paris"}
```

`id`, `input` and `expected` are required non-empty strings.

## Checks

| Code | Severity | Meaning |
| --- | --- | --- |
| `bad-json` | error | line is not a JSON object |
| `missing-field` | error | required field absent, not a string, or blank |
| `duplicate-id` | error | two cases share an id |
| `duplicate-input` | warning | same input after case/whitespace normalisation |
| `conflicting-label` | error | duplicate input with different `expected` |
| `label-imbalance` | warning | one expected label covers more than 70% of cases |
| `tiny-set` | warning | fewer than 20 cases, so differences are mostly noise |

## Usage

```bash
python3 -m evallint fixtures/good.jsonl
python3 -m evallint fixtures/bad.jsonl   # exits 1
```

## Tests

```bash
python3 -m unittest -v
```
