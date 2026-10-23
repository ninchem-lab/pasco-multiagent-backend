from fastapi import FastAPI
from pydantic import BaseModel
import os
import sys

# Asegurar que reconozca los módulos de la carpeta src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.graph import build_graph

app = FastAPI()
graph = build_graph()

class ChatPayload(BaseModel):
    message: str

@app.post("/api/chat")
def chat_endpoint(payload: ChatPayload):
    try:
        # Le indicamos a la IA que evite sintaxis de Markdown compleja
        prompt_modificado = payload.message + "\n\n(Importante: Responde en texto plano simple con saltos de línea claros. No uses tablas con |, ni numerales ##, ni negritas **)."
        
        inputs = {"messages": [("user", prompt_modificado)]}
        result = graph.invoke(inputs)
        
        # Extraer la respuesta del grafo
        draft = result.get("draft_response", "No se obtuvo respuesta.")
        return {"status": "success", "response": draft}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    