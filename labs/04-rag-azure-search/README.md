# Lab 04 — Retrieval-Augmented Generation with Azure AI Search

## Objective

Ground a chat model on **your own data** using the **Retrieval-Augmented
Generation (RAG)** pattern. You will chunk and embed local documents, store the
vectors in an **Azure AI Search** index, and then build a query pipeline that
retrieves the most relevant passages and "stuffs" them into a chat prompt so the
model answers from your data instead of hallucinating.

This is the same building block behind Foundry's **"Add your data"** feature —
here you build it explicitly so you understand each moving part.

## Prerequisites

- Completed **Lab 02** (working chat calls) and, ideally, **Lab 03**.
- An **Azure AI Search** service (Basic tier or higher). Create one in the
  [Azure portal](https://portal.azure.com) → *Create a resource* → *Azure AI
  Search*. Copy its **URL** and an **admin key** (Settings → Keys).
- An **embedding model** deployed in your Foundry project
  (`text-embedding-3-large` recommended — it produces 3072-dimensional vectors).
- `.env` filled in with the `AZURE_SEARCH_*`, `AZURE_AI_PROJECT_ENDPOINT`,
  `EMBEDDING_MODEL_DEPLOYMENT`, and `CHAT_MODEL_DEPLOYMENT` values.

## Estimated time

**60 minutes**

## Key concepts

| Concept                | Description                                                                                      |
| ---------------------- | ------------------------------------------------------------------------------------------------ |
| **Chunking**           | Splitting long documents into smaller passages so retrieval is precise and fits the context window. |
| **Embeddings**         | Vector representations of text; semantically similar text has nearby vectors.                     |
| **Vector index**       | An Azure AI Search index with a vector field + HNSW profile for fast nearest-neighbour search.    |
| **Retrieval**          | Embedding the query and finding the top-k nearest chunks.                                         |
| **Grounding / stuffing** | Injecting retrieved passages into the prompt so the model answers from them and can cite sources. |

---

## Steps

### 1. Provision Azure AI Search

If you don't already have a search service:

```bash
az search service create \
  --name "<your-search-service>" \
  --resource-group "<your-rg>" \
  --sku basic \
  --location eastus2
```

Then grab the endpoint and an admin key:

```bash
az search admin-key show --service-name "<your-search-service>" --resource-group "<your-rg>"
```

### 2. Configure your environment

Add these to your `.env` (values from step 1 and your Foundry project):

```dotenv
AZURE_SEARCH_ENDPOINT="https://<your-search-service>.search.windows.net"
AZURE_SEARCH_API_KEY="<admin-key>"
AZURE_SEARCH_INDEX_NAME="workshop-rag-index"
EMBEDDING_MODEL_DEPLOYMENT="text-embedding-3-large"
CHAT_MODEL_DEPLOYMENT="gpt-4o"
```

### 3. Review the sample data

Open [`data/contoso-foundry-faq.md`](./data/contoso-foundry-faq.md). It contains
**fictional** facts (pricing tiers, SLAs, regions) that a base model cannot know
— so a correct answer *proves* retrieval worked. Drop your own `.md`/`.txt`
files into `data/` to ground on different content.

### 4. Ingest: chunk, embed, and upload

```bash
python labs/04-rag-azure-search/ingest_documents.py
```

This script:

1. Reads every `.md`/`.txt` file in `data/`.
2. Splits each into ~800-character overlapping chunks.
3. Embeds all chunks in one batch with your embedding deployment
   (`azure-ai-inference` `EmbeddingsClient`).
4. Creates/updates the Azure AI Search index with a **vector field**
   (`azure-search-documents`).
5. Uploads the chunks + vectors.

### 5. Query with retrieval + grounding

```bash
python labs/04-rag-azure-search/rag_query.py "What is the Enterprise SLA?"
```

The script embeds your question, runs a **vector search** for the top-3 chunks,
builds a numbered context block, and asks GPT-4o to answer **only** from that
context and cite the passages it used.

### 6. Prove that grounding matters

Ask something only answerable from the doc, e.g.:

```bash
python labs/04-rag-azure-search/rag_query.py "Which region supports GPU fine-tuning?"
```

The correct answer (`contoso-west-2`) can only come from retrieval — a base
model would guess. Then ask something *not* in the doc and confirm the model
says it doesn't know.

---

## Expected output

```
> Question: What is the Enterprise SLA?

Retrieved context:
  [1] contoso-foundry-faq.md: ## Service level agreement (SLA)  The Enterprise tier guarantees 99.95%...
  [2] contoso-foundry-faq.md: ## Pricing tiers  Contoso offers three pricing tiers:  - **Starter**...
  [3] contoso-foundry-faq.md: ## Data residency and retention  Customer data is stored only in the...

=== Grounded answer ===
The Enterprise tier guarantees 99.95% monthly uptime. If uptime falls below
99.95% but stays at or above 99.0%, you receive a 10% service credit; below
99.0% the credit is 25%. [1]
```

---

## Troubleshooting

| Problem                                                   | Fix                                                                                            |
| --------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| `No results retrieved`                                    | Run `ingest_documents.py` first; confirm the index name matches in `.env`.                      |
| Vector dimension mismatch on upload                       | The index dim must equal the embedding dim. `text-embedding-3-large` = 3072; `-3-small` = 1536. Update `EMBEDDING_DIMENSIONS` in `ingest_documents.py`. |
| `403`/`401` from Azure AI Search                          | Use an **admin** key for ingestion; check `AZURE_SEARCH_ENDPOINT` has no trailing slash.        |
| `VectorizedQuery` import error                            | `pip install -U azure-search-documents>=11.5.1`.                                                |
| Embedding call fails with auth error                      | Ensure `az login` succeeded and your account has the `Azure AI Developer` role on the project.  |
| Answers ignore the context                                | Lower `temperature`, and keep the "answer ONLY from context" instruction in the system prompt.  |

---

## Challenge / Extension

1. **Hybrid search:** Combine vector search with keyword (BM25) search by passing
   `search_text=question` alongside the `vector_queries`, then add a
   **semantic ranker** (`query_type="semantic"`) for reranking.
2. **Integrated vectorization:** Configure the index with a
   *vectorizer* + *skillset* so Azure AI Search embeds text for you at index and
   query time (no client-side embedding calls).
3. **Citations UI:** Return and display the `source` + chunk id for each cited
   passage so users can click through to the original document.
4. **Use "Add your data" directly:** Recreate this in the Foundry portal's chat
   playground by attaching your Azure AI Search index as a data source, and
   compare the answers.
5. **Evaluate it:** Feed the RAG outputs into Lab 03's `GroundednessEvaluator`
   and `RetrievalEvaluator` to measure grounding quality objectively.
