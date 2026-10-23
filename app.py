"""
Interfaz de chat en Streamlit para el Asistente Pedagógico CNEB (Región Pasco).
"""

from typing import TypedDict

import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage

from src.graph import build_graph


load_dotenv()


# Etiquetas mostradas en la interfaz a medida que el grafo ejecuta cada nodo
NODE_LABELS: dict[str, str] = {
    "router": "🔀 Consulta clasificada",
    "general": "🧠 Agente Pedagógico (CNEB Pasco)",
    "tools": "🔧 Buscador de Normativa MINEDU",
    "editor": "✍️ Redacción pulida por Editor Pedagógico",
    "skip_editor": "",
}

SUGGESTED_QUESTIONS: list[str] = [
    "¿Qué desempeño aplica para conteo en niños de 5 años?",
    "¿Cuáles son las capacidades de la competencia Construye su identidad?",
    "Sugiéreme un criterio de evaluación para el área de Comunicación en 4 años",
    "¿Qué diferencia hay entre los desempeños de Ciclo I y Ciclo II?",
]


class ChatMessage(TypedDict):
    """Estructura de un mensaje para mostrar en la interfaz."""

    role: str
    content: str
    path: list[str]


st.set_page_config(page_title="Asistente Pedagógico - Región Pasco", page_icon="👧", layout="centered")

st.markdown(
    """
    <style>
        .block-container { padding-top: 2rem; }
        .stChatMessage { border-radius: 12px; margin-bottom: 0.5rem; }
        .stCaption { color: #888; font-size: 0.75rem; margin-top: 4px; }
        div[data-testid="stSidebarContent"] { padding-top: 2rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Barra lateral con información y preguntas sugeridas
with st.sidebar:
    st.markdown("## 👧 Asistente Pedagógico IA")
    st.markdown(
        "Orientación especializada en el Currículo Nacional de Educación Inicial (CNEB - MINEDU) para la Región Pasco."
    )
    st.divider()

    st.markdown("#### 💡 Preguntas recomendadas")
    for question in SUGGESTED_QUESTIONS:
        st.markdown(f"- *{question}*")

    st.divider()
    st.markdown("#### 🤖 Desarrollado con")
    st.markdown("- [LangGraph](https://github.com/langchain-ai/langgraph)")
    st.markdown("- [Groq](https://groq.com/) (llama-3.3-70b)")
    st.markdown("- [Tavily](https://tavily.com/) Search")

    if st.button("🗑️ Limpiar conversación", use_container_width=True):
        st.session_state.messages = []
        st.session_state.history = []
        st.rerun()

st.markdown("## 👧 Asistente Pedagógico de Educación Inicial")
st.markdown(
    "Tu consultor con IA para planificación, competencias, capacidades y desempeñados del CNEB (Región Pasco)."
)
st.divider()

# Historial de chat y memoria de LangChain
if "messages" not in st.session_state:
    st.session_state.messages = []

if "history" not in st.session_state:
    st.session_state.history = []

if "graph" not in st.session_state:
    st.session_state.graph = build_graph()


def render_message(msg: ChatMessage) -> None:
    """Renderiza un mensaje de chat junto con la ruta de nodos recorrida."""
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["path"]:
            st.caption(" → ".join(msg["path"]))


# Renderizar los mensajes previos
for message in st.session_state.messages:
    render_message(message)

if prompt := st.chat_input("Escribe tu consulta pedagógica sobre el CNEB..."):
    st.session_state.messages.append({"role": "user", "content": prompt, "path": []})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        status = st.empty()
        response = ""
        path: list[str] = []

        # Ejecución del grafo en tiempo real
        for chunk in st.session_state.graph.stream(
            {
                "query": prompt,
                "messages": st.session_state.history + [HumanMessage(content=prompt)],
            },
            stream_mode="updates",
        ):
            node = next(iter(chunk))
            label = NODE_LABELS.get(node, "")
            if label:
                path.append(label)
                status.caption(" → ".join(path))
            if "final_response" in chunk[node]:
                response = chunk[node]["final_response"]

        status.empty()
        if not response:
            response = "No se pudo generar una respuesta pedagógica. Por favor, intenta de nuevo."
        st.markdown(response)
        if path:
            st.caption(" → ".join(path))

    # Guardar en la memoria de LangChain
    st.session_state.history.append(HumanMessage(content=prompt))
    st.session_state.history.append(AIMessage(content=response))
    st.session_state.messages.append(
        {"role": "assistant", "content": response, "path": path}
    )