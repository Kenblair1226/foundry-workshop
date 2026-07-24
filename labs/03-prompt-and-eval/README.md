# Lab 03 — Prompt Engineering & Evaluation

## Objective

Learn practical prompt-engineering techniques and then **measure** prompt
quality objectively using the **`azure-ai-evaluation`** SDK (the engine behind
Foundry's Evaluation feature and prompt flow). You'll compare a weak prompt
against an improved one and score the outputs with AI-assisted evaluators.

## Prerequisites

- Completed **Lab 02** (working chat calls).
- `gpt-4o` deployment and `.env` configured.

## Estimated time

**45 minutes**

## Key concepts

| Concept                     | Description                                                                                     |
| --------------------------- | ---------------------------------------------------------------------------------------------- |
| **System prompt**           | Sets role, tone, constraints, and output format. The highest-leverage lever you have.          |
| **Few-shot examples**       | Demonstrations in the prompt that steer format and behaviour.                                   |
| **Grounding**               | Providing context/data so the model doesn't hallucinate (previewing Lab 04's RAG).             |
| **Evaluators**              | Functions that score model output. *AI-assisted*: Groundedness, Relevance, Coherence, Fluency. *NLP*: F1, BLEU, ROUGE. *Safety*: Violence, Hate, Self-harm, Sexual. |
| **Evaluation run**          | Applying evaluators to a dataset of (query, response, context, ground-truth) rows.             |

---

## Steps

### 1. Understand the anatomy of a good prompt

Review the two prompt styles in [`prompts/`](./prompts):

- `weak_prompt.txt` — vague, no role, no format.
- `improved_prompt.txt` — role, constraints, output format, and a few-shot example.

### 2. Run the prompt comparison

```bash
python labs/03-prompt-and-eval/prompt_engineering.py
```

This sends the same user question through both prompts and prints both answers
side by side so you can eyeball the difference.

### 3. Run an automated evaluation

We provide a small dataset of Q&A rows (`data/eval_dataset.jsonl`) with a
`query`, a `context`, a model `response`, and a `ground_truth`.

```bash
python labs/03-prompt-and-eval/run_evaluation.py
```

This uses `azure-ai-evaluation` with AI-assisted evaluators
(**Relevance**, **Coherence**, **Groundedness**) that call your GPT-4o
deployment as the *judge* model.

### 4. Inspect the scores

The script prints per-row scores and aggregate averages. Higher is better
(evaluators are on a 1–5 Likert scale). Note which rows score poorly and why.

### 5. (Optional) View results in the portal

Pass your project endpoint so results are uploaded to **Evaluation** in the
Foundry portal, where you can visualize and compare runs. See the comments in
`run_evaluation.py`.

---

## Expected output

```
=== Prompt comparison ===
[weak]     Paris is the capital.
[improved] **Answer:** The capital of France is Paris.
           **Confidence:** High
           **Source:** General knowledge.

=== Evaluation (3 rows) ===
row 1  relevance=5  coherence=5  groundedness=5
row 2  relevance=4  coherence=5  groundedness=3
row 3  relevance=5  coherence=4  groundedness=5

Averages: relevance=4.67  coherence=4.67  groundedness=4.33
```

*(Judge-model scores vary slightly between runs — that's expected.)*

---

## Troubleshooting

| Problem                                                | Fix                                                                                     |
| ------------------------------------------------------ | --------------------------------------------------------------------------------------- |
| `azure-ai-evaluation` import error                     | `pip install -U azure-ai-evaluation`.                                                    |
| Evaluators fail with auth error                        | The judge model config needs a valid endpoint/deployment; check `.env`.                 |
| Scores are all `NaN`                                   | Usually a malformed dataset row — every row needs `query`, `response`, and `context`.   |
| Very slow                                              | Each evaluator makes a model call per row; keep datasets small in the workshop.         |
| Region/quota `429`                                     | Reduce dataset size or add a short `time.sleep` between rows.                            |

---

## Challenge / Extension

1. **Add a safety evaluator:** Wire in `ViolenceEvaluator` /
   `HateUnfairnessEvaluator` (these use Azure AI Content Safety via your project)
   and score a deliberately edgy prompt.
2. **Custom evaluator:** Write your own evaluator function (e.g. "does the answer
   contain a citation?") and include it in the run.
3. **Prompt flow:** Recreate this evaluation visually in the portal's
   **Prompt flow**, chaining an LLM node to evaluator nodes.
4. **Regression gate:** Fail a CI build if average groundedness drops below 4.0.
