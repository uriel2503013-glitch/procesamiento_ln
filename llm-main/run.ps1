param(
    [switch]$Web
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvPython = Join-Path $projectRoot '.venv\Scripts\python.exe'
if (-not (Test-Path $venvPython)) {
    Write-Host 'No se encontró .venv. Crea el entorno virtual primero con: py -m venv .venv' -ForegroundColor Yellow
    exit 1
}

Set-Location $projectRoot
if ($Web) {
    $envFile = Join-Path $projectRoot 'writing-assistant\.env'

    if (-not (Test-Path $envFile)) {
        Write-Host ''
        Write-Host 'Primera configuración: voy a guardar tu OpenAI API Key localmente para la versión web.' -ForegroundColor Cyan
        $apiKey = Read-Host 'Pega tu OpenAI API Key'

        if ([string]::IsNullOrWhiteSpace($apiKey)) {
            Write-Host 'No se recibió ninguna clave. No se puede iniciar la versión web.' -ForegroundColor Red
            exit 1
        }

        $content = @"
OPENAI_API_KEY=$apiKey
OPENAI_MODEL=gpt-4o-mini
OLLAMA_HOST=http://127.0.0.1:11434
OLLAMA_MODEL=qwen2.5:0.5b
"@
        [System.IO.File]::WriteAllText($envFile, $content, [System.Text.UTF8Encoding]::new($false))

        Write-Host 'Clave guardada en writing-assistant\.env' -ForegroundColor Green
    }

    & $venvPython (Join-Path $projectRoot 'writing-assistant\server.py')
}
else {
    & $venvPython (Join-Path $projectRoot 'writing-assistant\app.py')
}