"""Funciones de construcción de prompts para el asistente de escritura."""

from __future__ import annotations


def _system_prompt() -> dict[str, str]:
    return {
        "role": "system",
        "content": (
            "Eres un asistente de escritura profesional en español. "
            "Respondes con claridad, precisión y formato útil para copiar y usar directamente. "
            "Evita explicar tu razonamiento interno."
        ),
    }


def _chat_system_prompt() -> dict[str, str]:
    return {
        "role": "system",
        "content": (
            "Eres un asistente tipo ChatGPT en español. Respondes de forma natural, clara y útil. "
            "Usa formato markdown cuando ayude a la lectura. Si falta contexto, haz una pregunta breve. "
            "No muestres razonamiento interno ni digas que eres un modelo."
        ),
    }


def prompt_generar_texto(*, tema: str, tono: str, longitud: str) -> list[dict[str, str]]:
    """Devuelve mensajes para generar un texto nuevo a partir de un tema."""

    return [
        _system_prompt(),
        {
            "role": "user",
            "content": (
                f"Redacta un texto original en español sobre el tema: {tema}. "
                f"El tono debe ser {tono}. La extensión debe ser {longitud}. "
                "Entrega un texto bien estructurado, natural y listo para entregar."
            ),
        },
    ]


def prompt_mejorar_texto(*, texto: str, enfoque: str) -> list[dict[str, str]]:
    """Devuelve mensajes para corregir y mejorar un texto existente."""

    return [
        _system_prompt(),
        {
            "role": "user",
            "content": (
                f"Mejora el siguiente texto con enfoque en {enfoque}. "
                "Corrige ortografía, gramática y estilo sin cambiar el sentido original. "
                "Devuelve únicamente la versión mejorada:\n\n"
                f"{texto}"
            ),
        },
    ]


def prompt_resumir_texto(*, texto: str, estilo: str) -> list[dict[str, str]]:
    """Devuelve mensajes para resumir un texto largo."""

    instruccion = {
        "breve": "Haz un resumen corto de máximo 5 líneas.",
        "detallado": "Haz un resumen detallado con párrafos claros.",
        "puntos clave": "Resume en viñetas con los puntos clave más importantes.",
    }[estilo]

    return [
        _system_prompt(),
        {
            "role": "user",
            "content": (
                f"{instruccion} Mantén el idioma español y conserva solo la información esencial. "
                f"Texto a resumir:\n\n{texto}"
            ),
        },
    ]


def prompt_correo_formal(*, destinatario: str, motivo: str, puntos: str) -> list[dict[str, str]]:
    """Devuelve mensajes para redactar un correo formal."""

    detalles_extra = f"Puntos obligatorios adicionales:\n{puntos}\n\n" if puntos.strip() else ""

    return [
        _system_prompt(),
        {
            "role": "user",
            "content": (
                f"Redacta un correo formal en español dirigido a {destinatario}. "
                f"El motivo principal del correo es: {motivo}. "
                f"{detalles_extra}"
                "Incluye saludo, cuerpo claro, cierre profesional y despedida. "
                "Entrega solo el correo final, listo para copiar y enviar."
            ),
        },
    ]


def prompt_chat_general(*, historial: list[dict[str, str]], mensaje_usuario: str, max_historial: int = 10) -> list[dict[str, str]]:
    """Devuelve mensajes para una conversación libre tipo ChatGPT."""

    conversaciones_previas = [mensaje for mensaje in historial if mensaje.get("role") in {"user", "assistant"}]
    conversaciones_recientes = conversaciones_previas[-max_historial:]

    return [
        _chat_system_prompt(),
        *conversaciones_recientes,
        {
            "role": "user",
            "content": mensaje_usuario,
        },
    ]