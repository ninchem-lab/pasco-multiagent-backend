"""Graph state definition."""

from typing import TypedDict, List, Optional

from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    """Shared state across all nodes in the graph.

    Attributes:
        query: The user's original question.
        messages: Full conversation history passed on each invocation.
        route: The routing decision ('general' or 'tools').
        needs_editing: Whether the response should be polished by the editor.
        draft_response: The raw response from the general or tools node.
        final_response: The final response delivered to the user.
    """

    query: str
    messages: list[BaseMessage]
    route: str
    needs_editing: bool
    draft_response: str
    final_response: str

class AgentState(TypedDict):
    
    # Estado de procesos y tiempo real
    stock_items: dict
    pending_tasks: List[dict]
    authorization_status: str
    # Datos del evaluador ML
    ml_forecast_metrics: Optional[dict]
    expert_score: Optional[int]
    draft_response: str