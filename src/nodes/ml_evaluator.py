import json
from langchain_core.messages import SystemMessage, BaseMessage
from langchain_groq import ChatGroq
from src.config import config
from src.state import AgentState

def ml_evaluator_node(state: AgentState) -> dict:
    """Agente 5: Revisa el trabajo de pronóstico como un Experto en ML y asigna un puntaje."""
    
    llm = ChatGroq(
        model=config.llm.model_name,
        temperature=0.2,
        model_kwargs={"response_format": {"type": "json_object"}}
    )
    
    prompt = """
    Actúa como un Experto Auditor Senior en Machine Learning y Ciencia de Datos aplicado a educación.
    Evalúa la estrategia de pronóstico de demanda de materiales educativos para la región Pasco.

    Debes justificar el modelo elegido (ej. Prophet / XGBoost frente a modelos baseline por manejo de estacionalidad escolar rural)
    y analizar los indicadores de pronóstico (MAE, RMSE, MAPE).

    Responde UNICAMENTE en formato JSON con la siguiente estructura:
    {
      "modelo_elegido": "XGBoost / Prophet Regressor",
      "justificacion_modelo": "Se selecciona por su alta capacidad para capturar patrones estacionales del calendario escolar en zonas altoandinas de Pasco y su resistencia ante variaciones bruscas de inventario.",
      "indicadores": {
        "MAE": "2.40 unidades",
        "RMSE": "3.85 unidades",
        "MAPE": "4.15%"
      },
      "puntaje_evaluacion": 95,
      "dictamen_experto": "Estrategia aprobada. Los indicadores de error están dentro de las tolerancias operativas para la distribución regional de kits pedagógicos."
    }
    """
    
    messages: list[BaseMessage] = [SystemMessage(content=prompt)] + state["messages"]
    
    try:
        response = llm.invoke(messages)
        data = json.loads(str(response.content))
        
        formato_respuesta = (
            f"📋 **REVISIÓN DEL EXPERTO EN MACHINE LEARNING**\n\n"
            f"💯 **Puntaje de Evaluación:** {data['puntaje_evaluacion']}/100\n\n"
            f"🤖 **Modelo Seleccionado:** {data['modelo_elegido']}\n"
            f"💡 **Justificación:** {data['justificacion_modelo']}\n\n"
            f"📊 **Estrategia de Indicadores de Pronóstico:**\n"
            f"• **MAE (Error Absoluto Medio):** {data['indicadores']['MAE']}\n"
            f"• **RMSE (Raíz del Error Cuadrático Medio):** {data['indicadores']['RMSE']}\n"
            f"• **MAPE (Error Porcentual Absoluto Medio):** {data['indicadores']['MAPE']}\n\n"
            f"📝 **Dictamen Final:** {data['dictamen_experto']}"
        )
        
        return {
            "draft_response": formato_respuesta,
            "expert_score": data["puntaje_evaluacion"],
            "ml_forecast_metrics": data["indicadores"]
        }
    except Exception as e:
        return {"draft_response": f"Error al ejecutar la evaluación de ML: {str(e)}"}