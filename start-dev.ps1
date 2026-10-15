
$ErrorActionPreference = "Stop"

$ProjectRoot = $PSScriptRoot
$BackendPath = Join-Path $ProjectRoot "backend"
$FrontendPath = Join-Path $ProjectRoot "frontend"
$VenvActivate = Join-Path $BackendPath "venv\Scripts\Activate.ps1"
$FrontendPackage = Join-Path $FrontendPath "package.json"

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "          MyAI Dev Launcher" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Validate the project structure
if (-not (Test-Path $VenvActivate)) {
    Write-Host "ERROR: Backend virtual environment not found:" -ForegroundColor Red
    Write-Host $VenvActivate
    exit 1
}

if (-not (Test-Path $FrontendPackage)) {
    Write-Host "ERROR: Frontend package.json not found:" -ForegroundColor Red
    Write-Host $FrontendPackage
    exit 1
}

# Check whether Ollama is already responding
$OllamaRunning = $false

try {
    $null = Invoke-RestMethod `
        -Uri "http://localhost:11434/api/tags" `
        -TimeoutSec 3

    $OllamaRunning = $true
}
catch {
    $OllamaRunning = $false
}

if ($OllamaRunning) {
    Write-Host "[OK] Ollama is already running." -ForegroundColor Green
}
else {
    Write-Host "[START] Starting Ollama..." -ForegroundColor Yellow

    $OllamaCommand = Get-Command ollama -ErrorAction SilentlyContinue

    if (-not $OllamaCommand) {
        Write-Host "ERROR: Ollama was not found in PATH." -ForegroundColor Red
        Write-Host "Install Ollama or ensure its executable is in PATH."
        exit 1
    }

    Start-Process -FilePath $OllamaCommand.Source `
        -ArgumentList "serve" `
        -WorkingDirectory $ProjectRoot

    # Wait briefly for Ollama to become available
    $OllamaReady = $false

    for ($i = 0; $i -lt 15; $i++) {
        Start-Sleep -Seconds 1

        try {
            $null = Invoke-RestMethod `
                -Uri "http://localhost:11434/api/tags" `
                -TimeoutSec 2

            $OllamaReady = $true
            break
        }
        catch {
            # Continue waiting
        }
    }

    if (-not $OllamaReady) {
        Write-Host "WARNING: Ollama has not responded yet." -ForegroundColor Yellow
        Write-Host "Check Ollama before testing AI chat."
    }
    else {
        Write-Host "[OK] Ollama is responding." -ForegroundColor Green
    }
}

# Start the FastAPI backend in a separate PowerShell window
Write-Host "[START] Launching FastAPI backend..." -ForegroundColor Yellow

$BackendCommand = "Set-Location -LiteralPath '$BackendPath'; . '$VenvActivate'; uvicorn app.main:app --reload"

Start-Process -FilePath "powershell.exe" `
    -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command", $BackendCommand
)

# Start the Vite frontend in a separate PowerShell window
Write-Host "[START] Launching React frontend..." -ForegroundColor Yellow

$FrontendCommand = "Set-Location -LiteralPath '$FrontendPath'; npm run dev"

Start-Process -FilePath "powershell.exe" `
    -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command", $FrontendCommand
)

Write-Host ""
Write-Host "======================================" -ForegroundColor Green
Write-Host "MyAI startup commands launched." -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Green
Write-Host ""
Write-Host "Frontend: http://localhost:5173"
Write-Host "Backend:  http://localhost:8000"
Write-Host "API docs: http://localhost:8000/docs"
Write-Host ""
Write-Host "Check the two terminal windows for startup errors."
Write-Host "Keep those windows open while using MyAI."
Write-Host ""
