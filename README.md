# A.R.I.A. — Autonomous Research Insight Agent

A multi-agent research pipeline with a live, high-tech dashboard. Give it a topic, and four agents work it in sequence — searching, reading, writing, and critiquing — while the UI streams their progress in real time.

## How it works

```
  1. Search Agent   →  finds recent, reliable sources on the topic
  2. Reader Agent   →  picks the best source and scrapes it for depth
  3. Writer         →  drafts a structured research report
  4. Critic         →  reviews the report and scores it out of 10
```

Each step streams to the browser as it completes via Server-Sent Events, so you watch the pipeline work instead of waiting on one long request.

## Project structure

```
.
├── app.py              # FastAPI app — serves the UI and the SSE stream
├── pipeliness.py        # The 4-step pipeline (streaming + blocking versions)
├── agents.py            # Agent / chain definitions (search, reader, writer, critic)
├── agentTools.py        # Tools used by the agents (search, scraping, etc.)
├── static/
│   └── index.html        # Dashboard UI — dark, high-tech, live progress
├── requirements.txt
├── Procfile              # Railway/Heroku start command
└── LICENSE
```

## Setup

1. Clone the repo and create a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/Scripts/activate      # Windows (Git Bash)
   # or: source .venv/bin/activate    # macOS/Linux
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Add a `.env` file in the project root with whatever API keys your agents in `agents.py` / `agentTools.py` require (e.g. your LLM provider key and search tool key). This file is git-ignored and never committed.

## Running locally

From the project root (the folder containing `app.py`):

```bash
uvicorn app:app --reload
```

Then open **http://127.0.0.1:8000** — that serves the dashboard and connects it to the pipeline.

> `static/index.html` must exist at that exact relative path for the UI to load. If you see `RuntimeError: Directory 'static' does not exist`, you're either missing the folder or running `uvicorn` from the wrong directory.

## API

| Endpoint           | Method | Description                                                              |
| ------------------ | ------ | ------------------------------------------------------------------------ |
| `/`                | GET    | Serves the dashboard UI                                                  |
| `/health`          | GET    | Simple health check                                                      |
| `/research`        | POST   | Runs the full pipeline, returns all results at once (`{"topic": "..."}`) |
| `/research/stream` | GET    | SSE stream of live pipeline progress (`?topic=...`)                      |

## Deploying to Railway

1. Push this repo to GitHub.
2. Create a new project in Railway and connect the repo.
3. Add your environment variables (the same ones from your local `.env`) under the project's Variables tab.
4. Railway detects the included `Procfile` and starts the app with:
   ```
   uvicorn app:app --host 0.0.0.0 --port $PORT
   ```
5. Once deployed, Railway gives you a public URL serving the dashboard.

## Tech stack

- **Backend:** FastAPI, Server-Sent Events for streaming
- **Agents/orchestration:** LangChain-style agents and chains (`agents.py`)
- **Frontend:** Vanilla HTML/CSS/JS — no build step, rendered Markdown via marked.js
- **Deployment:** Railway (Procfile-based)

## License

See [LICENSE](./LICENSE).

---

Built by **Bimlesh Kumar Sah**.
