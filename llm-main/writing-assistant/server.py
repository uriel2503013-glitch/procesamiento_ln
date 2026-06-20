"""Servidor web Flask para el Asistente de Escritura Automática."""

from __future__ import annotations

import os
from pathlib import Path
import threading
import webbrowser

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

from openai_service import OpenAIServiceError, generar_respuesta
from prompts import (
    prompt_correo_formal,
    prompt_generar_texto,
    prompt_mejorar_texto,
    prompt_resumir_texto,
)


ENV_PATH = Path(__file__).resolve().with_name(".env")

load_dotenv(dotenv_path=ENV_PATH, override=True)

app = Flask(__name__)


@app.get("/")
def home():
    """Renderiza la interfaz principal."""

    return render_template("index.html")


@app.post("/api/generate")
def api_generate():
    """Procesa las acciones del asistente desde el frontend."""

    data = request.get_json(silent=True) or {}
    action = (data.get("action") or "").strip()

    try:
        load_dotenv(dotenv_path=ENV_PATH, override=True)
        if not os.getenv("OPENAI_API_KEY"):
            return jsonify({"ok": False, "error": "Falta configurar OPENAI_API_KEY en .env para usar la versión web."}), 400

        if action == "generate_text":
            tema = (data.get("tema") or "").strip()
            tono = (data.get("tono") or "neutral").strip()
            longitud = (data.get("longitud") or "media").strip()
            if not tema:
                return jsonify({"ok": False, "error": "Debes escribir un tema."}), 400

            mensajes = prompt_generar_texto(tema=tema, tono=tono, longitud=longitud)

        elif action == "improve_text":
            texto = (data.get("texto") or "").strip()
            enfoque = (data.get("enfoque") or "completo").strip()
            if not texto:
                return jsonify({"ok": False, "error": "Debes escribir un texto."}), 400

            mensajes = prompt_mejorar_texto(texto=texto, enfoque=enfoque)

        elif action == "summarize_text":
            texto = (data.get("texto") or "").strip()
            estilo = (data.get("estilo") or "breve").strip()
            if not texto:
                return jsonify({"ok": False, "error": "Debes escribir un texto para resumir."}), 400

            mensajes = prompt_resumir_texto(texto=texto, estilo=estilo)

        elif action == "formal_email":
            destinatario = (data.get("destinatario") or "").strip()
            motivo = (data.get("motivo") or "").strip()
            puntos = (data.get("puntos") or "").strip()
            if not destinatario or not motivo:
                return jsonify({"ok": False, "error": "Debes completar destinatario y motivo."}), 400

            mensajes = prompt_correo_formal(destinatario=destinatario, motivo=motivo, puntos=puntos)

        else:
            return jsonify({"ok": False, "error": "Acción no válida."}), 400

        respuesta = generar_respuesta(mensajes, backend="openai")
        return jsonify({"ok": True, "result": respuesta})

    except OpenAIServiceError as error:
        return jsonify({"ok": False, "error": str(error)}), 500
    except Exception as error:
        return jsonify({"ok": False, "error": f"Error inesperado: {error}"}), 500


if __name__ == "__main__":
    threading.Timer(1.0, lambda: webbrowser.open("http://127.0.0.1:5000")).start()
    app.run(host="127.0.0.1", port=5000, debug=True)