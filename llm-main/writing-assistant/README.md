# Asistente de Escritura Automática

Proyecto en Python que ofrece dos formas de uso: una consola local con Ollama y una interfaz web con OpenAI.

## Qué hace

El asistente permite:

- generar texto a partir de un tema,
- mejorar o reescribir un texto existente,
- resumir contenido largo,
- redactar correos formales.

La consola no requiere API key. La interfaz web sí usa OpenAI y guarda la clave solo en el servidor.

## Estructura

```text
writing-assistant/
├── app.py
├── server.py
├── openai_service.py
├── prompts.py
├── requirements.txt
├── README.md
├── .env.example
├── static/
│   ├── app.js
│   └── styles.css
└── templates/
    └── index.html
```

## Instalación

1. Ve a la carpeta del proyecto:

```bash
cd writing-assistant
```

2. Instala las dependencias:

```bash
pip install -r requirements.txt
```

## Configuración

1. Copia `.env.example` a `.env` dentro de `writing-assistant/`.
2. Si vas a usar la interfaz web, define tu clave de OpenAI.
3. Si vas a usar la consola, instala Ollama y configura:

```env
OPENAI_API_KEY=tu_api_key_real
OPENAI_MODEL=gpt-4o-mini
OLLAMA_HOST=http://127.0.0.1:11434
OLLAMA_MODEL=qwen2.5:0.5b
```

Si no defines `OPENAI_MODEL`, el proyecto usa `gpt-4o-mini` por defecto.
La consola usa `OLLAMA_HOST` y `OLLAMA_MODEL`; la web usa `OPENAI_API_KEY` y `OPENAI_MODEL`.

Para usar Ollama:

1. Instala Ollama desde https://ollama.com.
2. Abre una terminal y ejecuta `ollama pull qwen2.5:0.5b`.
3. Deja Ollama corriendo en tu equipo.

## Ejecución

Para iniciar la consola local:

```bash
python app.py
```

Para iniciar la interfaz web con OpenAI:

```bash
python server.py
```

Al arrancar el servidor web, el navegador se abre automáticamente en `http://127.0.0.1:5000`.

Si prefieres lanzar todo desde PowerShell, también puedes usar:

```powershell
.\run.ps1
```

Para la versión web desde PowerShell:

```powershell
.\run.ps1 -Web
```

## Funcionalidades

- Menú interactivo en terminal con formato visual usando `rich`.
- Interfaz web con Flask, HTML, CSS y JavaScript.
- Consola local con Ollama.
- Web con OpenAI.
- Prompts separados para mantener la lógica organizada.
- Validación básica de entradas antes de llamar al backend.

## Tecnologías utilizadas

- Python
- Flask
- OpenAI Python SDK
- python-dotenv
- rich
- Ollama para la consola local

## Requisitos

- Python 3.8 o superior.
- Archivo `.env` configurado con `OPENAI_API_KEY` para la web.
- Ollama instalado si quieres usar la consola local.

## Notas

- `app.py` usa Ollama en local.
- `server.py` usa OpenAI en la web.
- El proyecto está preparado para usarse localmente y como demo académica.