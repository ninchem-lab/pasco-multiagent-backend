"""LangGraph graph definition for the multi-agent system."""

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from src.nodes.editor import editor_node
from src.nodes.general import general_node
from src.nodes.router import router_node
from src.nodes.tools import tools_node
from src.state import AgentState


def route_query(state: AgentState) -> str:
    """Determine which agent should handle the query.

    Args:
        state: The current graph state with the routing decision.

    Returns:
        The route name: 'general' or 'tools'.
    """

    return state["route"]


def should_edit(state: AgentState) -> str:
    """Determine whether the draft response needs editorial polishing.

    Args:
        state: The current graph state with the needs_editing flag.

    Returns:
        'editor' if polishing is needed, 'skip' otherwise.
    """

    if state["needs_editing"]:
        return "editor"
    return "skip"


def skip_editor(state: AgentState) -> dict[str, str]:
    """Pass the draft response directly as the final response.

    Args:
        state: The current graph state containing the draft response.

    Returns:
        A dictionary with the 'final_response' key set to the draft.
    """

    return {"final_response": state["draft_response"]}


def build_graph() -> CompiledStateGraph:
    """Build and compile the multi-agent LangGraph graph.

    Constructs the graph with the following flow:
        router -> general or tools -> editor (conditional) -> END

    Returns:
        The compiled LangGraph state graph ready for invocation.
    """

    graph = StateGraph(AgentState)

    graph.add_node("router", router_node)
    graph.add_node("general", general_node)
    graph.add_node("tools", tools_node)
    graph.add_node("editor", editor_node)
    graph.add_node("skip_editor", skip_editor)

    graph.set_entry_point("router")

    graph.add_conditional_edges(
        "router", route_query, {"general": "general", "tools": "tools"}
    )
    graph.add_conditional_edges(
        "general", should_edit, {"editor": "editor", "skip": "skip_editor"}
    )
    graph.add_conditional_edges(
        "tools", should_edit, {"editor": "editor", "skip": "skip_editor"}
    )

    graph.add_edge("editor", END)
    graph.add_edge("skip_editor", END)

    return graph.compile()

from langgraph.graph import StateGraph, END
from src.state import AgentState
from src.nodes.router import router_node
from src.nodes.general import general_node
from src.nodes.ml_evaluator import ml_evaluator_node
from src.nodes.stock_auth import stock_auth_node

def build_graph():
    workflow = StateGraph(AgentState)

    # 1. Registrar los nodos de los agentes
    workflow.add_node("router", router_node)
    workflow.add_node("general", general_node)
    workflow.add_node("ml_evaluator", ml_evaluator_node)
    workflow.add_node("stock_auth", stock_auth_node)

    # 2. Configurar el punto de entrada
    workflow.set_entry_point("router")

    # 3. Definir la lógica de enrutamiento
    def route_decision(state: AgentState):
        route = state.get("route", "general")
        if route == "ml_evaluator":
            return "ml_evaluator"
        elif route == "stock_auth":
            return "stock_auth"
        return "general"

    workflow.add_conditional_edges(
        "router",
        route_decision,
        {
            "general": "general",
            "ml_evaluator": "ml_evaluator",
            "stock_auth": "stock_auth"
        }
    )

    workflow.add_edge("general", END)
    workflow.add_edge("ml_evaluator", END)
    workflow.add_edge("stock_auth", END)

    return workflow.compile()