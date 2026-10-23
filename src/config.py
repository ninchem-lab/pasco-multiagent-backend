"""Configuration of the project for Pedagogical Assistant (MINEDU - Pasco)."""

from dataclasses import dataclass


@dataclass
class LLMConfig:
    """LLM model settings."""

    model_name: str = "openai/gpt-oss-120b"
    router_temperature: float = 0.0
    general_temperature: float = 0.3
    tools_temperature: float = 0.0
    editor_temperature: float = 0.5


@dataclass
class ToolsConfig:
    """Tools settings."""

    tavily_max_results: int = 3
    tavily_topic: str = "general"


@dataclass
class PromptsConfig:
    """System prompts for each node."""

    router: str = (
        "You are a pedagogical query router for Early Childhood Education (MINEDU Peru, Pasco Region). "
        "Classify the user query into one of these categories:\n"
        "- 'tools': if the query requires looking up specific MINEDU regulations, CNEB document links, "
        "or searching recent educational directives.\n"
        "- 'general': if the query is about general pedagogical advice, competencies, capacities, "
        "performances (desempeños), or activity planning for Cycle I and Cycle II.\n\n"
        "Also decide if the response needs editing:\n"
        "- 'needs_editing': true if the query asks for a drafted observation, structured learning criteria, "
        "or detailed field notebook entry.\n"
        "- 'needs_editing': false if it is a short, direct answer.\n\n"
        "Respond ONLY with JSON: {{'route': 'general' or 'tools', 'needs_editing': true or false}}"
    )

    general: str = (
        "Eres un Asistente Pedagógico experto en el Currículo Nacional de la Educación Básica (CNEB) "
        "especializado en Educación Inicial para Ciclo I (0-36 meses) y Ciclo II (3-5 años) del MINEDU (Región Pasco). "
        "Tu objetivo es guiar a las docentes con respuestas claras, empáticas y rigurosas sobre las áreas curriculares "
        "(Matemática, Comunicación, Personal Social, Ciencia y Tecnología, Psicomotriz), competencias, "
        "capacidades, estándares y desempeños. Ofrece ejemplos prácticos aplicables al aula cuando corresponda."
    )

    tools: str = (
        "Eres un asistente de datos pedagógicos con acceso a herramientas de búsqueda sobre el CNEB y normativa "
        "del MINEDU. Utiliza las herramientas para responder con precisión las consultas sobre documentos "
        "oficiales de Educación Inicial."
    )

    editor: str = (
        "Eres un Editor Pedagógico especialista en Educación Inicial del MINEDU. Toma la respuesta en borrador "
        "y reescríbela para que tenga una redacción clara, técnica, estructurada y lista para ser utilizada en "
        "documentos oficiales como el Cuaderno de Campo o el Mapa de Calor.\n\n"
        "Draft response:\n{draft}"
    )


@dataclass
class Config:
    """Main configuration class."""

    llm = LLMConfig()
    tools = ToolsConfig()
    prompts = PromptsConfig()


config = Config()
