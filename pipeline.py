from agents import (
    build_reader_agent,
    build_search_agents,
    writer_chain,
    critic_chain
)


def run_research_pipeline(topic: str) -> dict:

    state = {}

    # STEP 1 — SEARCH AGENT
    print("\n" + "=" * 50)
    print("Search agent working...")
    print("=" * 50)

    search_agent = build_search_agents()

    search_result = search_agent.invoke({
        "messages": [
            ("user",
             f"Find recent, reliable and detailed information about: {topic}")
        ]
    })

    state["search_results"] = search_result['messages'][-1].content

    print("\nSearch Results:\n")
    print(state['search_results'])

    # STEP 2 — READER AGENT
    print("\n" + "=" * 50)
    print("Reader agent working...")
    print("=" * 50)

    reader_agent = build_reader_agent()

    reader_result = reader_agent.invoke({
        "messages": [
            ("user",
             f"Based on the following search results about '{topic}', "
             f"pick the most relevant URL and scrape it for deeper content.\n\n"
             f"Search Results:\n{state['search_results'][:800]}")
        ]
    })

    state['scraped_content'] = reader_result['messages'][-1].content

    print("\nScraped Content:\n")
    print(state['scraped_content'])

    # STEP 3 — WRITER CHAIN
    print("\n" + "=" * 50)
    print("Writer agent drafting report...")
    print("=" * 50)

    research_combined = (
        f"SEARCH RESULTS:\n{state['search_results']}\n\n"
        f"SCRAPED CONTENT:\n{state['scraped_content']}"
    )

    state["report"] = writer_chain.invoke({
        "topic": topic,
        "research": research_combined
    })

    print("\nFinal Report:\n")
    print(state['report'])

    # STEP 4 — CRITIC CHAIN
    print("\n" + "=" * 50)
    print("Critic agent reviewing report...")
    print("=" * 50)

    state["feedback"] = critic_chain.invoke({
        "report": state['report']
    })

    print("\nCritic Feedback:\n")
    print(state['feedback'])

    return state


if __name__ == "__main__":
    topic = input("\nEnter a research topic: ")
    run_research_pipeline(topic)