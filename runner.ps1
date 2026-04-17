param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$CliArgs
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

$envFile = Join-Path $ScriptDir ".env"
$hasShellKey = -not [string]::IsNullOrWhiteSpace($env:GEMINI_API_KEY) -or -not [string]::IsNullOrWhiteSpace($env:GOOGLE_API_KEY)
$hasEnvFileKey = $false
if (Test-Path $envFile) {
    $hasEnvFileKey = [bool](Select-String -Path $envFile -Pattern '^\s*GEMINI_API_KEY\s*=\s*\S+' -Quiet)
}
if (-not $hasShellKey -and -not $hasEnvFileKey) {
    Write-Error "Gemini API key not found in shell environment or $envFile. Set GEMINI_API_KEY in the shell that runs Docker Compose, or add GEMINI_API_KEY=... to TeacherEvaluation/.env."
    exit 1
}

if (-not $CliArgs -or $CliArgs.Count -eq 0) {
    $CliArgs = @(
        "--video", "samples/Lecture_1_cut_1m_to_5m.mp4",
        "--output-root", "/outputs/sample_run",
        "--start-sec", "92.5",
        "--duration-sec", "60",
        "--analysis-fps", "12",
        "--enable-semantic",
        "--enable-coaching"
    )
}

docker compose run --rm --no-deps --entrypoint python streamlit run_long_experiment.py @CliArgs
