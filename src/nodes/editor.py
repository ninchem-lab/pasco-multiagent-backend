"""Editor node: rewrites the draft response for clarity and quality."""

from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq

from src.config import config
from src.state import AgentState


def editor_node(state: AgentState) -> dict[str, str]:
    """Polish the draft response into a well-written final answer.

    Takes the raw draft from the general or tools node and rewrites it with improved
    clarity, structure, and engagement.

    Args:
        state: The current graph state containing the draft response.

    Returns:
        A dictionary with the 'final_response' key containing the polished text.
    """

    llm = ChatGroq(
        model=config.llm.model_name, temperature=config.llm.editor_temperature
    )
    prompt = config.prompts.editor.format(draft=state["draft_response"])
    response = llm.invoke([HumanMessage(content=prompt)])

    content = response.content
    if not isinstance(content, str):
        return {"final_response": "Error executing the workflow."}
    return {"final_response": content}
