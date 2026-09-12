from agents import search_agent, reader_agent, writer_chain, critic_chain


def research_pipeline_stream(topic: str):
    """
    Runs the research pipeline step by step and yields progress events as
    each agent starts and finishes. This is what the API's SSE endpoint
    consumes to drive the live UI.

    Event shape:
        {"step": "search"|"reader"|"writer"|"critic"|"complete"|"error",
         "label": <human readable name>,
         "status": "running"|"done"|"error",
         "message": <optional status text>,
         "data": <optional payload>}
    """
    state = {}

    try:
        # ---- step 1: search agent -----------------------------------
        yield {
            "step": "search",
            "label": "Search Agent",
            "status": "running",
            "message": "Searching the web for recent, reliable sources...",
        }

        search_worker = search_agent()
        search_result = search_worker.invoke(
            {
                "messages": [
                    (
                        "user",
                        f"Find recent, reliable and detailed information about: {topic}",
                    )
                ]
            }
        )
        state["search_results"] = search_result["messages"][-1].content

        yield {
            "step": "search",
            "label": "Search Agent",
            "status": "done",
            "data": state["search_results"],
        }

        # ---- step 2: reader agent ------------------------------------
        yield {
            "step": "reader",
            "label": "Reader Agent",
            "status": "running",
            "message": "Scraping the most relevant source for deeper content...",
        }

        reader_worker = reader_agent()
        reader_result = reader_worker.invoke(
            {
                "messages": [
                    (
                        "user",
                        f"Based on the following search results about '{topic}', "
                        f"pick the most relevant URL and scrape it for deeper content.\n\n"
                        f"Search Results:\n{state['search_results'][:300]}",
                    )
                ]
            }
        )
        state["scraped_content"] = reader_result["messages"][-1].content

        yield {
            "step": "reader",
            "label": "Reader Agent",
            "status": "done",
            "data": state["scraped_content"],
        }

        # ---- step 3: writer chain --------------------------------------
        yield {
            "step": "writer",
            "label": "Writer",
            "status": "running",
            "message": "Drafting the research report...",
        }

        research_combined = (
            f"SEARCH RESULTS : \n {state['search_results']} \n\n"
            f"DETAILED SCRAPED CONTENT : \n {state['scraped_content']}"
        )
        raw_report = writer_chain.invoke(
            {"topic": topic, "research": research_combined}
        )
        if hasattr(raw_report, "content"):
            state["report"] = raw_report.content
        elif isinstance(raw_report, dict):
            state["report"] = (
                raw_report.get("text") or raw_report.get("output") or str(raw_report)
            )
        else:
            state["report"] = str(raw_report)

        yield {
            "step": "writer",
            "label": "Writer",
            "status": "done",
            "data": state["report"],
        }

        # ---- step 4: critic chain ---------------------------------------
        yield {
            "step": "critic",
            "label": "Critic",
            "status": "running",
            "message": "Reviewing the report and preparing feedback...",
        }

        raw_feedback = critic_chain.invoke({"report": state["report"]})
        # normalize: LangChain chains can return an AIMessage or a dict
        # depending on how the chain ends — json.dumps() needs a plain string.
        if hasattr(raw_feedback, "content"):
            state["feedback"] = raw_feedback.content
        elif isinstance(raw_feedback, dict):
            state["feedback"] = (
                raw_feedback.get("text")
                or raw_feedback.get("output")
                or str(raw_feedback)
            )
        else:
            state["feedback"] = str(raw_feedback)

        yield {
            "step": "critic",
            "label": "Critic",
            "status": "done",
            "data": state["feedback"],
        }

        # ---- done -----------------------------------------------------
        yield {"step": "complete", "status": "done", "data": state}

    except (
        Exception
    ) as exc:  # surfaces the failure to the UI instead of a dead connection
        yield {"step": "error", "status": "error", "message": str(exc)}


def research_pipeline(topic: str) -> dict:
    """Non-streaming version — kept for CLI use and the existing /research route."""
    state = {}
    for event in research_pipeline_stream(topic):
        if event["step"] == "complete":
            state = event["data"]
        elif event["step"] == "error":
            raise RuntimeError(event["message"])
    return state


if __name__ == "__main__":
    topic = input("\n Enter a research topic : ")
    result = research_pipeline(topic)
    print("\nFinal Report\n", result["report"])
    print("\nCritic Feedback\n", result["feedback"])
