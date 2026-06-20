"""Servicio centralizado para consumir la API oficial de OpenAI."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from dotenv import load_dotenv

try:  # pragma: no cover - dependencia opcional para modo remoto
    from openai import APIError, AuthenticationError, OpenAI, OpenAIError
except ImportError:  # pragma: no cover - el modo local no requiere el paquete
    APIError = AuthenticationError = OpenAIError = None
    OpenAI = None


DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
DEFAULT_OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:0.5b")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
ENV_PATH = Path(__file__).resolve().with_name(".env")


class OpenAIServiceError(RuntimeError):
    """Error controlado para la capa de servicio de OpenAI."""


def _modo_local_forzado() -> bool:
    """Indica si debe usarse la salida local sin llamar a OpenAI."""

    valor = os.getenv("WRITING_ASSISTANT_LOCAL_ONLY", "").strip().lower()
    return valor in {"1", "true", "yes", "on"}


def _backend_preferido() -> str:
    """Devuelve el backend configurado: auto, openai, ollama o local."""

    backend = os.getenv("WRITING_ASSISTANT_BACKEND", "auto").strip().lower()
    return backend if backend in {"auto", "openai", "ollama", "local"} else "auto"


def _es_error_de_cuota(error: Exception) -> bool:
    """Detecta errores de cuota o limitación para caer a modo local."""

    texto = str(error).lower()
    codigo = getattr(error, "code", None)
    status_code = getattr(error, "status_code", None)
    return (
        codigo in {"insufficient_quota", "rate_limit_exceeded"}
        or status_code == 429
        or "insufficient_quota" in texto
        or "exceeded your current quota" in texto
        or "rate limit" in texto
    )


def _obtener_cliente() -> OpenAI:
    """Crea el cliente oficial usando la API key de entorno."""

    if OpenAI is None:
        raise OpenAIServiceError("El paquete openai no está instalado.")

    load_dotenv(dotenv_path=ENV_PATH, override=True)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise OpenAIServiceError("OPENAI_API_KEY no está configurada.")

    return OpenAI(api_key=api_key)


def _obtener_cliente_con_api_key(api_key: str | None) -> OpenAI:
    """Crea un cliente usando una clave explícita o la clave del entorno."""

    if OpenAI is None:
        raise OpenAIServiceError("El paquete openai no está instalado.")

    load_dotenv(dotenv_path=ENV_PATH, override=True)
    clave = (api_key or "").strip() or os.getenv("OPENAI_API_KEY")
    if not clave:
        raise OpenAIServiceError("OPENAI_API_KEY no está configurada.")

    return OpenAI(api_key=clave)


def _generar_respuesta_openai(
    mensajes: Iterable[dict[str, str]],
    *,
    model: str | None = None,
    temperature: float = 0.7,
    max_tokens: int = 900,
    api_key: str | None = None,
) -> str:
    """Genera una respuesta usando OpenAI."""

    if OpenAI is None:
        raise OpenAIServiceError("El paquete openai no está instalado.")

    mensajes_lista = list(mensajes)
    if not mensajes_lista:
        raise OpenAIServiceError("No se proporcionaron mensajes para enviar al modelo.")

    cliente = _obtener_cliente_con_api_key(api_key)
    modelo_a_usar = model or DEFAULT_MODEL

    try:
        respuesta = cliente.chat.completions.create(
            model=modelo_a_usar,
            messages=mensajes_lista,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        contenido = respuesta.choices[0].message.content
        if not contenido:
            raise OpenAIServiceError("La API no devolvió contenido de texto.")
        return contenido.strip()

    except AuthenticationError as error:
        raise OpenAIServiceError("Autenticación fallida. Revisa tu OPENAI_API_KEY.") from error
    except APIError as error:
        if _es_error_de_cuota(error):
            raise OpenAIServiceError("CUOTA_OPENAI") from error
        raise OpenAIServiceError(f"La API de OpenAI respondió con un error: {error}") from error
    except OpenAIError as error:
        if _es_error_de_cuota(error):
            raise OpenAIServiceError("CUOTA_OPENAI") from error
        raise OpenAIServiceError(f"Error al comunicarse con OpenAI: {error}") from error
    except Exception as error:  # pragma: no cover - salvaguarda general
        raise OpenAIServiceError(f"Error inesperado en OpenAI: {error}") from error


def _generar_respuesta_ollama(
    mensajes: Iterable[dict[str, str]],
    *,
    model: str | None = None,
    temperature: float = 0.7,
    max_tokens: int = 900,
) -> str:
    """Genera una respuesta usando la API local de Ollama."""

    mensajes_lista = list(mensajes)
    if not mensajes_lista:
        raise OpenAIServiceError("No se proporcionaron mensajes para enviar al modelo.")

    modelo_a_usar = model or DEFAULT_OLLAMA_MODEL
    payload = {
        "model": modelo_a_usar,
        "messages": mensajes_lista,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": max_tokens,
        },
    }

    solicitud = Request(
        f"{OLLAMA_HOST.rstrip('/')}/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(solicitud, timeout=120) as respuesta:
            datos = json.loads(respuesta.read().decode("utf-8"))

        contenido = (datos.get("message") or {}).get("content")
        if not contenido:
            raise OpenAIServiceError("Ollama no devolvió contenido de texto.")
        return str(contenido).strip()

    except (HTTPError, URLError, TimeoutError, ValueError) as error:
        raise OpenAIServiceError(f"Error al comunicarse con Ollama: {error}") from error


def _intentar_ollama_o_local(
    mensajes: Iterable[dict[str, str]],
    *,
    temperature: float = 0.7,
    max_tokens: int = 900,
) -> str:
    """Intenta Ollama y finalmente cae al modo local."""

    mensajes_lista = list(mensajes)

    try:
        return _generar_respuesta_ollama(
            mensajes_lista,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    except OpenAIServiceError:
        return _generar_respuesta_local(mensajes_lista)


def _normalizar_texto(texto: str) -> str:
    """Compacta espacios y líneas para generar salidas locales legibles."""

    lineas = [linea.strip() for linea in texto.splitlines() if linea.strip()]
    return " ".join(lineas)


def _extraer_primera_coincidencia(patron: str, texto: str, por_defecto: str = "") -> str:
    coincidencia = re.search(patron, texto, flags=re.IGNORECASE | re.DOTALL)
    if not coincidencia:
        return por_defecto
    return coincidencia.group(1).strip()


def _generar_texto_local(tema: str, tono: str, longitud: str) -> str:
    apertura = f"El tema de {tema} invita a reflexionar sobre su impacto en la vida cotidiana y profesional."
    desarrollo = (
        f"Desde un tono {tono}, conviene explicar sus beneficios, desafíos y posibilidades de aplicación "
        "con un lenguaje claro y directo."
    )
    cierre = "En conclusión, se trata de un asunto relevante que merece atención, análisis y una mirada práctica."

    if longitud == "corta":
        return f"{apertura} {cierre}"
    if longitud == "larga":
        return f"{apertura}\n\n{desarrollo}\n\nAdemás, conviene aportar ejemplos concretos, datos de contexto y una conclusión que invite a la acción. {cierre}"
    return f"{apertura}\n\n{desarrollo}\n\n{cierre}"


def _mejorar_texto_local(texto: str, enfoque: str) -> str:
    texto_limpio = _normalizar_texto(texto)
    if not texto_limpio:
        return "No se proporcionó texto para mejorar."

    if enfoque == "ortografía":
        return texto_limpio
    if enfoque == "estilo":
        return f"Versión con mejor estilo:\n\n{texto_limpio}"
    if enfoque == "claridad":
        return f"Versión más clara y directa:\n\n{texto_limpio}"

    return f"Texto mejorado:\n\n{texto_limpio}"


def _resumir_texto_local(texto: str, estilo: str) -> str:
    texto_limpio = _normalizar_texto(texto)
    if not texto_limpio:
        return "No se proporcionó texto para resumir."

    oraciones = [fragmento.strip() for fragmento in re.split(r"(?<=[.!?])\s+", texto_limpio) if fragmento.strip()]
    ideas = oraciones[:4] if oraciones else [texto_limpio[:200]]

    if estilo == "puntos clave":
        return "Puntos clave:\n" + "\n".join(f"- {idea}" for idea in ideas)
    if estilo == "detallado":
        return "Resumen detallado:\n\n" + " ".join(ideas)

    return "Resumen breve:\n\n" + " ".join(ideas[:2])


def _correo_formal_local(destinatario: str, motivo: str, puntos: str) -> str:
    puntos_limpios = [linea.strip("-• \t") for linea in puntos.splitlines() if linea.strip()]
    detalles = "\n".join(f"- {punto}" for punto in puntos_limpios) if puntos_limpios else "- [Agrega aquí los detalles importantes]"

    return (
        f"Estimado/a {destinatario}:\n\n"
        f"Me dirijo a usted con el fin de {motivo}.\n\n"
        f"Detalles a considerar:\n{detalles}\n\n"
        "Quedo atento/a a su confirmación o a cualquier información adicional que considere necesaria.\n\n"
        "Atentamente,\n"
        "[Tu nombre]"
    )


def _generar_respuesta_local(mensajes: Iterable[dict[str, str]]) -> str:
    mensaje_usuario = ""
    for mensaje in mensajes:
        if mensaje.get("role") == "user":
            mensaje_usuario = mensaje.get("content", "")

    if not mensaje_usuario:
        return "No se pudo interpretar la solicitud en modo local."

    if mensaje_usuario.lower().startswith(("explícame", "explicame", "qué es", "que es", "cómo", "como", "dame", "ayúdame", "ayudame")):
        return (
            "Claro. Te respondo de forma directa:\n\n"
            f"{mensaje_usuario.strip().rstrip('?')}\n\n"
            "Si quieres, puedo ampliarlo, resumirlo o darte un ejemplo práctico."
        )

    if "Redacta un texto original" in mensaje_usuario:
        tema = _extraer_primera_coincidencia(r"tema:\s*(.*?)(?:\.|\n|$)", mensaje_usuario, "el tema indicado")
        tono = _extraer_primera_coincidencia(r"El tono debe ser\s*(.*?)(?:\.|\n|$)", mensaje_usuario, "neutral")
        longitud = _extraer_primera_coincidencia(r"La extensión debe ser\s*(.*?)(?:\.|\n|$)", mensaje_usuario, "media")
        return _generar_texto_local(tema, tono, longitud)

    if "Mejora el siguiente texto" in mensaje_usuario:
        enfoque = _extraer_primera_coincidencia(r"enfoque en\s*(.*?)(?:\.|\n|$)", mensaje_usuario, "completo")
        texto = mensaje_usuario.split("Devuelve únicamente la versión mejorada:", 1)[-1].strip()
        return _mejorar_texto_local(texto, enfoque)

    if "Haz un resumen corto" in mensaje_usuario or "Haz un resumen detallado" in mensaje_usuario or "Resume en viñetas" in mensaje_usuario:
        estilo = "breve"
        if "resumen detallado" in mensaje_usuario.lower():
            estilo = "detallado"
        elif "viñetas" in mensaje_usuario.lower():
            estilo = "puntos clave"

        texto = mensaje_usuario.split("Texto a resumir:", 1)[-1].strip()
        return _resumir_texto_local(texto, estilo)

    if "Redacta un correo formal" in mensaje_usuario:
        destinatario = _extraer_primera_coincidencia(r"dirigido a\s*(.*?)(?:\.|\n|$)", mensaje_usuario, "la persona destinataria")
        motivo = _extraer_primera_coincidencia(r"motivo principal del correo es:\s*(.*?)(?:\.|\n|$)", mensaje_usuario, "el motivo indicado")
        puntos = _extraer_primera_coincidencia(r"Puntos obligatorios adicionales:\s*(.*?)(?:\n\n|Incluye saludo,|$)", mensaje_usuario, "")
        return _correo_formal_local(destinatario, motivo, puntos)

    return (
        "Modo local activo. No pude identificar una plantilla específica, pero puedes volver a intentar "
        "con una solicitud más concreta."
    )


def generar_respuesta(
    mensajes: Iterable[dict[str, str]],
    *,
    backend: str | None = None,
    model: str | None = None,
    temperature: float = 0.7,
    max_tokens: int = 900,
    api_key: str | None = None,
) -> str:
    """Llama al modelo de OpenAI y devuelve solo el texto generado."""

    mensajes_lista = list(mensajes)
    if not mensajes_lista:
        raise OpenAIServiceError("No se proporcionaron mensajes para enviar al modelo.")

    if _modo_local_forzado():
        return _generar_respuesta_local(mensajes_lista)

    backend_preferido = (backend or _backend_preferido()).strip().lower()

    if backend_preferido == "local":
        return _generar_respuesta_local(mensajes_lista)

    if backend_preferido == "ollama":
        return _intentar_ollama_o_local(
            mensajes_lista,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    if backend_preferido == "openai":
        try:
            return _generar_respuesta_openai(
                mensajes_lista,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=api_key,
            )
        except OpenAIServiceError:
            raise

    if os.getenv("OPENAI_API_KEY") and OpenAI is not None:
        try:
            return _generar_respuesta_openai(
                mensajes_lista,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=api_key,
            )
        except OpenAIServiceError as error:
            if str(error) == "CUOTA_OPENAI":
                return _intentar_ollama_o_local(
                    mensajes_lista,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            return _intentar_ollama_o_local(
                mensajes_lista,
                temperature=temperature,
                max_tokens=max_tokens,
            )

    return _intentar_ollama_o_local(
        mensajes_lista,
        temperature=temperature,
        max_tokens=max_tokens,
    )