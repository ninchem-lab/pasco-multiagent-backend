"""Router node: classifies the query and decides the route."""

import json
from typing import Literal

from langchain_core.messages import BaseMessage, SystemMessage
from langchain_groq import ChatGroq
from pydantic import BaseModel

from src.config import config
from src.state import AgentState


class RouterOutput(BaseModel):
    """Structured output for the router node."""

    route: Literal["general", "tools"]
    needs_editing: bool


def router_node(state: AgentState) -> dict[str, str | bool]:
    """Classify the user query and decide the routing path."""

    # Forzamos formato JSON puro para evitar errores de tool call en Groq
    llm = ChatGroq(
        model=config.llm.model_name,
        temperature=config.llm.router_temperature,
        model_kwargs={"response_format": {"type": "json_object"}}
    )

    system_prompt = (
        config.prompts.router + 
        "\n\nDebes responder UNICAMENTE con un objeto JSON valido con la siguiente estructura:"
        '\n{"route": "general", "needs_editing": false}'
    )

    messages: list[BaseMessage] = [
        SystemMessage(content=system_prompt)
    ] + state["messages"]

    try:
        response = llm.invoke(messages)
        content = response.content if isinstance(response.content, str) else ""
        data = json.loads(content)
        
        route = data.get("route", "general")
        needs_editing = data.get("needs_editing", False)
        
        return {"route": route, "needs_editing": needs_editing}
    except Exception:
        # En caso de fallo de lectura, redirige por defecto a general
        return {"route": "general", "needs_editing": False}
