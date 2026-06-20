"""CLI principal del Asistente de Escritura Automática."""

from __future__ import annotations

import os

from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

from openai_service import OpenAIServiceError, generar_respuesta
from prompts import (
    prompt_correo_formal,
    prompt_chat_general,
    prompt_generar_texto,
    prompt_mejorar_texto,
    prompt_resumir_texto,
)


console = Console()


def limpiar_pantalla() -> None:
    """Limpia la consola según el sistema operativo."""

    os.system("cls" if os.name == "nt" else "clear")


def mostrar_banner() -> None:
    """Muestra la cabecera visual de la aplicación."""

    banner = Panel(
        "[bold cyan]Asistente de Escritura Automática[/bold cyan]\n"
        "[white]Chat tipo ChatGPT en terminal, con Ollama en local.[/white]",
        title="✍️  Writing Assistant Chat",
        border_style="cyan",
        padding=(1, 2),
    )
    console.print(banner)


def mostrar_ayuda_chat() -> None:
    console.print("[bold yellow]Comandos rápidos[/bold yellow]")
    console.print("[cyan]/texto[/cyan] Generar texto sobre un tema")
    console.print("[cyan]/mejorar[/cyan] Mejorar o reescribir un texto")
    console.print("[cyan]/resumen[/cyan] Resumir un texto")
    console.print("[cyan]/correo[/cyan] Redactar un correo formal")
    console.print("[cyan]/limpiar[/cyan] Borrar el historial")
    console.print("[cyan]/salir[/cyan] Cerrar la terminal")


def imprimir_respuesta_chat(contenido: str) -> None:
    panel = Panel(Markdown(contenido.strip() or "(Sin contenido)"), border_style="green", padding=(1, 2))
    console.print(panel)


def pedir_multilinea(prompt: str) -> str:
    console.print(f"\n[bold]{prompt}[/bold]")
    console.print("[dim]Finaliza con una línea que contenga solo FIN.[/dim]")
    lineas: list[str] = []
    while True:
        linea = input()
        if linea.strip().upper() == "FIN":
            break
        lineas.append(linea)
    return "\n".join(lineas).strip()


def construir_prompt_especial(comando: str) -> list[dict[str, str]]:
    if comando == "/texto":
        tema = Prompt.ask("Tema").strip()
        estilo = Prompt.ask("Tono", choices=["formal", "neutral", "creativo", "persuasivo"], default="neutral")
        longitud = Prompt.ask("Extensión", choices=["corta", "media", "larga"], default="media")
        return prompt_generar_texto(tema=tema, tono=estilo, longitud=longitud)

    if comando == "/mejorar":
        texto = pedir_multilinea("Pega o escribe el texto que quieres mejorar")
        enfoque = Prompt.ask("Enfoque", choices=["ortografía", "estilo", "claridad", "completo"], default="completo")
        return prompt_mejorar_texto(texto=texto, enfoque=enfoque)

    if comando == "/resumen":
        texto = pedir_multilinea("Pega el texto que deseas resumir")
        estilo = Prompt.ask("Tipo", choices=["breve", "detallado", "puntos clave"], default="breve")
        return prompt_resumir_texto(texto=texto, estilo=estilo)

    if comando == "/correo":
        destinatario = Prompt.ask("Destinatario o cargo").strip()
        motivo = Prompt.ask("Motivo principal").strip()
        puntos = pedir_multilinea("Puntos adicionales")
        return prompt_correo_formal(destinatario=destinatario, motivo=motivo, puntos=puntos)

    return []


def main() -> None:
    """Punto de entrada de la aplicación de consola."""

    load_dotenv()

    limpiar_pantalla()
    mostrar_banner()

    console.print("[yellow]Escribe como si hablaras con ChatGPT. Usa /ayuda para ver comandos.[/yellow]")
    console.print("[yellow]La consola usa Ollama por defecto.[/yellow]")

    historial: list[dict[str, str]] = []
    mostrar_ayuda_chat()

    while True:
        console.print()
        entrada = Prompt.ask("Tú").strip()

        if not entrada:
            continue

        comando = entrada.lower()

        try:
            if comando in {"/salir", "/exit", "salir"}:
                console.print("[bold green]Saliendo del asistente. Hasta luego.[/bold green]")
                break

            if comando in {"/ayuda", "/help"}:
                mostrar_ayuda_chat()
                continue

            if comando == "/limpiar":
                historial.clear()
                limpiar_pantalla()
                mostrar_banner()
                console.print("[yellow]Historial limpiado.[/yellow]")
                continue

            if comando in {"/texto", "/mejorar", "/resumen", "/correo"}:
                mensajes = construir_prompt_especial(comando)
                if not mensajes:
                    console.print("[red]No se pudo construir esa solicitud.[/red]")
                    continue
                respuesta = generar_respuesta(mensajes, backend="ollama")
                historial.append({"role": "user", "content": entrada})
                historial.append({"role": "assistant", "content": respuesta})
                imprimir_respuesta_chat(respuesta)
                continue

            mensajes = prompt_chat_general(historial=historial, mensaje_usuario=entrada)
            respuesta = generar_respuesta(mensajes, backend="ollama")
            historial.append({"role": "user", "content": entrada})
            historial.append({"role": "assistant", "content": respuesta})
            imprimir_respuesta_chat(respuesta)

        except OpenAIServiceError as error:
            console.print(f"[red]Error del servicio:[/red] {error}")
        except Exception as error:  # pragma: no cover - protección general de la CLI
            console.print(f"[red]Ocurrió un error inesperado:[/red] {error}")


if __name__ == "__main__":
    main()