"""General knowledge node: answers using LLM's built-in football knowledge."""

from langchain_core.messages import BaseMessage, SystemMessage
from langchain_groq import ChatGroq

from src.config import config
from src.state import AgentState


def general_node(state: AgentState) -> dict[str, str]:
    """Answer the query using general football knowledge.

    Invokes the LLM without tools, relying on its training data to answer questions
    about rules, history, tactics, players, teams, and competitions.

    Args:
        state: The current graph state containing the user query.

    Returns:
        A dictionary with the 'draft_response' key containing the LLM answer.
    """

    llm = ChatGroq(
        model=config.llm.model_name, temperature=config.llm.general_temperature
    )
    messages: list[BaseMessage] = [
        SystemMessage(content=config.prompts.general)
    ] + state["messages"]
    response = llm.invoke(messages)

    content = response.content
    if not isinstance(content, str):
        return {"draft_response": "Error executing the general node."}
    return {"draft_response": content}
