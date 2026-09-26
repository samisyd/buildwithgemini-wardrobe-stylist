# WardrobeAI: The Smart Style & Closet Assistant — Project Overview & Implementation Log

## Overview
**WardrobeAI** (The Smart Style & Closet Assistant) is an agentic AI assistant built with the Google Agent Development Kit (ADK) and Gemini on Google Cloud Vertex AI Agent Platform. It serves as an expert personal styling and wardrobe management companion, offering personalized outfit curation, catalog search, item inspection, apparel image generation, code sandbox analytics, and cross-session memory.

---

## 1. Project Architecture & Components

```
                ┌────────────────────────────────────────────────────────┐
                │                     WardrobeStylist                     │
                │             (Gemini 3.6 Flash / ADK Agent)             │
                └───────┬────────────┬─────────────┬─────────────┬───────┘
                        │            │             │             │
        ┌───────────────┴┐     ┌─────┴────────┐  ┌─┴─────────┐  ┌┴────────────────┐
        │ Firestore DB   │     │ Vertex AI    │  │ GCS       │  │ Agent Engine    │
        │ Catalog Search │     │ Image Model  │  │ Public    │  │ Code Sandbox &  │
        │ & Inventory    │     │ Flash Lite   │  │ Bucket    │  │ Memory Bank     │
        └────────────────┘     └──────────────┘  └───────────┘  └─────────────────┘
```

### Core Technologies
- **Model**: `gemini-3.6-flash`
- **Framework**: Google Agent Development Kit (`google-adk`)
- **Serving Interfaces**:
  - ADK Web Playground (`adk web`)
  - A2A (Agent-to-Agent) protocol endpoints (`/a2a/app`)
  - Reasoning Engine adapter (`/query`, `/stream_query`)
- **Hosting & Sandbox Platform**: Vertex AI Agent Engine (`projects/311001706350/locations/us-east1/reasoningEngines/1257689569571110912`)

---

## 2. Completed Capabilities & Implementations

### A. Firestore Wardrobe Catalog Tools (`app/firestore_tools.py`)
- Integrated with Google Cloud Firestore database in project `qwiklabs-gcp-04-7202d2aeaa87`.
- **Tools**:
  - `search_wardrobe_catalog`: Flexible search with query matching across item names, brands, fabrics, tags, and categories, plus filters for category, season, occasion, color, and max price.
  - `list_wardrobe_items`: Fetches wardrobe items with optional category filtering.
  - `get_wardrobe_item`: Inspects a specific apparel piece by item ID.
  - `add_wardrobe_item`: Persists newly acquired garments directly to Firestore.

### B. Public Cloud Storage & Image Generation (`app/image_tools.py`)
- Created a public Google Cloud Storage bucket: `gs://wardrobestylist-qwiklabs-gcp-04-7202d2aeaa87` in `us-central1` with `allUsers:objectViewer` permissions.
- **Tool**:
  - `generate_wardrobe_item_image`:
    - Calls `gemini-3.1-flash-lite-image` in `location="global"` to generate high-resolution fashion/outfit visuals.
    - Saves the image part in-memory as an ADK artifact using `tool_context.save_artifact(...)` so it appears in the playground's Artifacts panel.
    - Uploads the raw bytes to the public GCS bucket and returns a public HTTPS link (`https://storage.googleapis.com/...`).

### C. Agent Engine Sandbox Code Execution (`app/agent.py`)
- Created and running an isolated sandbox environment:
  `projects/311001706350/locations/us-east1/reasoningEngines/1257689569571110912/sandboxEnvironments/9150311688212316160`
- Wired `AgentEngineSandboxCodeExecutor` directly to `root_agent.code_executor`.
- Empowers the agent to execute real Python code to perform calculations, such as cost-per-wear formulas, wardrobe valuation, and outfit budget analytics.

### D. Long-Term Cross-Session Memory & Allergy Tracking
- Connected `VertexAiMemoryBankService` to the deployed Agent Engine (`1257689569571110912`).
- Configured dedicated memory extraction topics:
  - `ManagedTopicEnum.USER_PERSONAL_INFO`
  - `ManagedTopicEnum.USER_PREFERENCES`
  - `Custom topic: user_allergies`: Captures fabric/material sensitivities (wool, synthetics, latex, nickel, dyes) and medical allergies.
- Agent wiring:
  - `PreloadMemoryTool()` in `tools`: Recalls past facts and allergies at the start of each turn.
  - `after_agent_callback=generate_memories_callback`: Runs `add_session_to_memory()` to store conversation insights.
- Configured shared memory service in `app/app_utils/services.py` and `app/fast_api_app.py` for local serving and future redeployments.

### E. A2UI Rich Visual Rendering
- Adopted A2UI v0.8 specification using `A2uiSchemaManager` and `BasicCatalog`.
- Added `app/a2ui_utils.py` containing `a2ui_callback` to wrap model UI outputs into `<a2a_datapart_json>` parts recognized by `adk web`.
- Configured `root_agent.after_model_callback = a2ui_callback`.

---

## 3. Local Development & Serving
- Playground startup command with Memory Bank and Global Location:
  ```bash
  export GOOGLE_CLOUD_PROJECT="qwiklabs-gcp-04-7202d2aeaa87"
  export GOOGLE_CLOUD_LOCATION="global"
  uv run adk web . --port 8080 --reload_agents --memory_service_uri=agentengine://projects/311001706350/locations/us-east1/reasoningEngines/1257689569571110912
  ```
- Accessible locally on `http://127.0.0.1:8080/dev-ui/?app=app`.

---

## 4. Verification & Testing
- Verified live communication with Vertex AI in `global` region for `gemini-3.6-flash`.
- Successfully validated weather queries, allergic constraint filtering (wool-free styling recommendations), A2UI v0.8 card formatting, artifact persistence, and memory ingestion.
