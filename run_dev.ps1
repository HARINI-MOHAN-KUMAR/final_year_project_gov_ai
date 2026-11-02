param(
    [switch]$Fast
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Adaptive directory detection (works from root or from govguide-ai folder)
if (Test-Path (Join-Path $ScriptDir "backend")) {
    $GovGuideDir = $ScriptDir
    $BackendDir = Join-Path $ScriptDir "backend"
    $FrontendDir = Join-Path $ScriptDir "frontend"
} else {
    $GovGuideDir = Join-Path $ScriptDir "govguide-ai"
    $BackendDir = Join-Path $GovGuideDir "backend"
    $FrontendDir = Join-Path $GovGuideDir "frontend"
}

$PythonExe = Join-Path $BackendDir ".venv\Scripts\python.exe"
$FrontendUrl = if ($Fast) { "http://127.0.0.1:8000" } else { "http://127.0.0.1:5173" }

function Invoke-CheckedCommand {
    param(
        [string]$FilePath,
        [string[]]$Arguments,
        [string]$WorkingDirectory,
        [string]$FailureMessage
    )

    Push-Location $WorkingDirectory
    try {
        & $FilePath @Arguments
        if ($LASTEXITCODE -ne 0) {
            throw "$FailureMessage (exit code $LASTEXITCODE)."
        }
    }
    finally {
        Pop-Location
    }
}

# Find Python in PATH (check 'python' then 'py')
$Python = Get-Command python -ErrorAction SilentlyContinue
if (-not $Python) {
    $Python = Get-Command py -ErrorAction SilentlyContinue
}

if (-not (Test-Path $PythonExe)) {
    if (-not $Python) {
        throw "Python 3.11 or newer is required. Install Python and add it to PATH."
    }
    Write-Host "Creating Python virtual environment in .venv..." -ForegroundColor Cyan
    Invoke-CheckedCommand $Python.Source @("-m", "venv", ".venv") $BackendDir "Could not create the backend virtual environment"
}

$PythonVersion = & $PythonExe -c "import sys; print('.'.join(map(str, sys.version_info[:2])))"
if ($LASTEXITCODE -ne 0 -or [version]$PythonVersion -lt [version]"3.11") {
    throw "Python 3.11 or newer is required for the backend (found $PythonVersion)."
}

# Verify backend core dependencies
Push-Location $BackendDir
$PreviousErrorActionPreference = $ErrorActionPreference
try {
    $ErrorActionPreference = "Continue"
    & $PythonExe -c "import app.main" 2>$null
    $DependenciesReady = $LASTEXITCODE -eq 0
}
finally {
    $ErrorActionPreference = $PreviousErrorActionPreference
    Pop-Location
}
if (-not $DependenciesReady) {
    Write-Host "Installing backend dependencies from requirements.txt..." -ForegroundColor Cyan
    Invoke-CheckedCommand $PythonExe @("-m", "pip", "install", "-r", "requirements.txt") $BackendDir "Backend dependency installation failed"
}

# Verify Node.js / npm
$Npm = Get-Command npm.cmd -ErrorAction SilentlyContinue
if (-not $Npm) {
    $Npm = Get-Command npm -ErrorAction SilentlyContinue
}
if (-not $Npm) {
    throw "Node.js 18 or newer (including npm) is required. Install Node.js and add it to PATH."
}
if (-not (Test-Path (Join-Path $FrontendDir "node_modules\vite"))) {
    Write-Host "Installing frontend dependencies with npm install..." -ForegroundColor Cyan
    Invoke-CheckedCommand $Npm.Source @("install") $FrontendDir "Frontend dependency installation failed"
}

# Ensure .env exists in backend
$BackendEnv = Join-Path $BackendDir ".env"
$EnvExample = Join-Path $GovGuideDir ".env.example"
if (-not (Test-Path $BackendEnv) -and (Test-Path $EnvExample)) {
    Copy-Item $EnvExample $BackendEnv
    Write-Host "Created backend .env from example configuration." -ForegroundColor Green
}

# Build frontend if fast mode
if ($Fast) {
    Write-Host "Building frontend for single-port mode..." -ForegroundColor Cyan
    Invoke-CheckedCommand $Npm.Source @("run", "build") $FrontendDir "Frontend build failed"
}

Write-Host "`nStarting GovGuide AI services..." -ForegroundColor Cyan
$BackendCommand = "title GovGuide Backend (8000) && cd /d `"$BackendDir`" && `"$PythonExe`" -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
$BackendProcess = Start-Process -FilePath $env:ComSpec -ArgumentList @("/k", $BackendCommand) -PassThru

$FrontendProcess = $null
if (-not $Fast) {
    $FrontendCommand = "title GovGuide Frontend (5173) && cd /d `"$FrontendDir`" && npm.cmd run dev -- --host 127.0.0.1"
    $FrontendProcess = Start-Process -FilePath $env:ComSpec -ArgumentList @("/k", $FrontendCommand) -PassThru
}

Write-Host "Waiting for backend service to become ready..." -ForegroundColor Cyan
$BackendReady = $false
for ($Attempt = 0; $Attempt -lt 45; $Attempt++) {
    try {
        $null = Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 "http://127.0.0.1:8000/health"
        $BackendReady = $true
        break
    }
    catch {
        Start-Sleep -Seconds 1
    }
}
if (-not $BackendReady) {
    throw "Backend did not become ready. Check the backend console window for error messages."
}

if (-not $Fast) {
    Write-Host "Waiting for frontend service to become ready..." -ForegroundColor Cyan
    $FrontendReady = $false
    for ($Attempt = 0; $Attempt -lt 30; $Attempt++) {
        try {
            $null = Invoke-WebRequest -UseBasicParsing -TimeoutSec 2 $FrontendUrl
            $FrontendReady = $true
            break
        }
        catch {
            Start-Sleep -Seconds 1
        }
    }
    if (-not $FrontendReady) {
        throw "Frontend did not become ready. Check the frontend console window for error messages."
    }
}

Write-Host "`n========================================================" -ForegroundColor Green
Write-Host " GovGuide AI is running!" -ForegroundColor Green
Write-Host "   Frontend: $FrontendUrl" -ForegroundColor White
Write-Host "   Backend:  http://127.0.0.1:8000" -ForegroundColor White
Write-Host "   API Docs: http://127.0.0.1:8000/api/docs" -ForegroundColor White
Write-Host "========================================================`n" -ForegroundColor Green

Start-Process $FrontendUrl

Write-Host "Press Ctrl+C to stop this monitor or close the server windows when finished.`n" -ForegroundColor Yellow

try {
    while ($true) {
        Start-Sleep -Seconds 2
    }
}
finally {
    # If the user terminates this script, notify them
    Write-Host "`nLauncher monitor stopped." -ForegroundColor Cyan
}
