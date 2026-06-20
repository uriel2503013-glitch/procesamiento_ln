# Asistente de Escritura Automática

Proyecto académico en Python con dos modos de uso: una consola local que usa Ollama y una interfaz web que usa OpenAI.

## Descripción del proyecto

La aplicación permite trabajar desde terminal o desde el navegador con un menú interactivo para:

1. Generar texto sobre un tema.
2. Mejorar o redactar mejor un texto existente.
3. Resumir un texto largo.
4. Generar un correo formal.

La versión web usa Flask, HTML, CSS y JavaScript. El proyecto sigue organizado de forma modular, con prompts separados y una capa central para la comunicación con el backend elegido.

La app de consola está en `writing-assistant/app.py`.
La app web está en `writing-assistant/server.py`.
La consola usa Ollama.
La web usa OpenAI.

## Estructura

```text
/writing-assistant
 ├── app.py
 ├── server.py
 ├── openai_service.py
 ├── prompts.py
 ├── templates/index.html
 ├── static/styles.css
 ├── static/app.js
 ├── requirements.txt
 ├── README.md
 ├── .env.example

/requirements.txt
```

`writing-assistant/app.py` es la aplicación principal de consola local.
`writing-assistant/server.py` levanta la interfaz web con OpenAI.

## Instalación

1. Ve a la carpeta raíz del proyecto.
2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Entorno virtual en Windows

Si quieres prepararlo desde cero, usa estos comandos en PowerShell desde la carpeta raíz:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Si PowerShell bloquea la activación, ejecuta una vez:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## Configuración de `.env`

1. Copia `writing-assistant/.env.example` y renómbralo a `writing-assistant/.env`.
2. Para la web, agrega tu clave de OpenAI:
   ```env
   OPENAI_API_KEY=tu_api_key_real
   OPENAI_MODEL=gpt-4o-mini
   ```
3. Para la consola local, instala Ollama y usa:
   ```env
   OLLAMA_HOST=http://127.0.0.1:11434
   OLLAMA_MODEL=qwen2.5:0.5b
   ```

## Ejecución

Desde la carpeta raíz del proyecto ejecuta:

```bash
python writing-assistant/app.py
```

Para arrancar la interfaz web:

```bash
python writing-assistant/server.py
```

Desde PowerShell puedes usar:

```powershell
.\run.ps1
```

Para la versión web en PowerShell:

```powershell
.\run.ps1 -Web
```

O en PowerShell, usando el script listo para ejecutar:

```powershell
.\run.ps1
```

También puedes ejecutarla entrando a la subcarpeta:

```bash
cd writing-assistant
python app.py
```

## Funcionalidades

- Generar texto sobre un tema con tono configurable.
- Mejorar redacción, ortografía, estilo y claridad.
- Resumir textos largos en formato breve, detallado o por puntos.
- Redactar correos formales listos para copiar y enviar.
- Usar Ollama en local para la consola.
- Usar OpenAI en la interfaz web.

## Tecnologías utilizadas

- Python
- OpenAI Python SDK oficial
- python-dotenv
- Flask
- HTML, CSS y JavaScript
- rich para una consola más visual
- Ollama para la consola local

## Requisitos

- Python 3.8 o superior.
- `OPENAI_API_KEY` configurada en el archivo `.env` para la web.
- Ollama instalado para la consola local.

## Notas de entrega

- La consola usa Ollama.
- La interfaz web usa OpenAI.
- El proyecto está listo para demostración y entrega académica.
