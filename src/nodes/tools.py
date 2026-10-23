"""Tools node: agent with access to web search for CNEB and MINEDU queries."""

from langchain_core.messages import BaseMessage, SystemMessage, ToolMessage
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch

from src.config import config
from src.state import AgentState


def tools_node(state: AgentState) -> dict[str, str]:
    """Answer the query using web search in an agentic loop.

    Binds web search (Tavily) to the LLM, then iteratively
    calls tools until the LLM produces a final text answer.

    Args:
        state: The current graph state containing the user query.

    Returns:
        A dictionary with the 'draft_response' key containing the final answer.
    """

    tools = [
        TavilySearch(
            max_results=config.tools.tavily_max_results, topic=config.tools.tavily_topic
        ),
    ]
    llm = ChatGroq(
        model=config.llm.model_name, temperature=config.llm.tools_temperature
    ).bind_tools(tools)

    messages: list[BaseMessage] = [
        SystemMessage(content=config.prompts.tools),
    ] + list(state["messages"])

    tool_map = {t.name: t for t in tools}

    while True:
        response = llm.invoke(messages)
        messages.append(response)

        if not response.tool_calls:
            break

        for tool_call in response.tool_calls:
            tool_result = tool_map[tool_call["name"]].invoke(tool_call["args"])
            messages.append(
                ToolMessage(content=str(tool_result), tool_call_id=tool_call["id"])
            )

    if not isinstance(response.content, str):
        return {"draft_response": "Error executing tools node."}

    return {"draft_response": response.content}