from src.state import AgentState

def stock_auth_node(state: AgentState) -> dict:
    stock_actual = {
        "Kits de Psicomotricidad (Inicial)": 45,
        "Kits de Cuentos Ilustrados": 120,
        "Bloques Lógicos de Matemática": 80,
        "Guías Pedagógicas CNEB 2026": 200
    }
    
    query = state["messages"][-1].content.lower() if state.get("messages") else ""
    
    if "autorizar" in query or "aprobar" in query:
        return {
            "draft_response": "✅ **ESTADO DE PROCESO: AUTORIZADO**\n\nLa asignación de materiales pedagógicos para Pasco ha sido aprobada manualmente en tiempo real.",
            "authorization_status": "APPROVED",
            "stock_items": stock_actual
        }
    
    res = "📦 **STOCK DE MATERIALES PEDAGÓGICOS (TIEMPO REAL)**\n\n"
    for item, cant in stock_actual.items():
        res += f"• **{item}:** {cant} unidades disponibles\n"
    res += "\n⚠️ *Nota: Para procesar la asignación requiere orden de **AUTORIZACIÓN MANUAL**.*"
    
    return {"draft_response": res, "authorization_status": "PENDING", "stock_items": stock_actual}