import json

from fastapi import FastAPI
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from pipeliness import research_pipeline, research_pipeline_stream

app = FastAPI(title="ARIA Research Agent")

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def home():
    return FileResponse("static/index.html")


@app.get("/health")
def health():
    return {"status": "ARIA running"}


@app.post("/research")
def research(data: dict):
    """Blocking endpoint — runs the full pipeline and returns everything at once."""
    topic = data.get("topic")

    result = research_pipeline(topic)

    return {
        "search_results": result["search_results"],
        "scraped_content": result["scraped_content"],
        "report": result["report"],
        "feedback": result["feedback"],
    }


@app.get("/research/stream")
def research_stream(topic: str):
    """
    Server-Sent Events endpoint — streams one JSON event per pipeline
    step so the UI can show live progress instead of waiting on one
    long request.
    """

    def event_generator():
        for event in research_pipeline_stream(topic):
            yield f"data: {json.dumps(event)}\n\n"
        yield "event: end\ndata: {}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # disable proxy buffering so events flush immediately
        },
    )
