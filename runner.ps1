# param(
#     [Parameter(ValueFromRemainingArguments = $true)]
#     [string[]]$CliArgs
# )

# $ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
# Set-Location $ScriptDir

# $envFile = Join-Path $ScriptDir ".env"
# $hasEnvFileKey = $false
# if (Test-Path $envFile) {
#     $hasEnvFileKey = [bool](Select-String -Path $envFile -Pattern '^\s*GEMINI_API_KEY\s*=\s*\S+' -Quiet)
# }
# if (-not $hasEnvFileKey) {
#     Write-Error "Gemini API key not found in $envFile. Docker runs now use .env as the single source of truth. Add GEMINI_API_KEY=... to TeacherEvaluation/.env and rerun."
#     exit 1
# }

# if (-not $CliArgs -or $CliArgs.Count -eq 0) {
#     $CliArgs = @(
#         "--video", "samples/Lecture_1_cut_1m_to_5m.mp4",
#         "--output-root", "/outputs/sample_run",
#         "--start-sec", "92.5",
#         "--duration-sec", "60",
#         "--analysis-fps", "12",
#         "--enable-semantic",
#         "--enable-coaching"
#     )
# }

# docker compose run --rm --no-deps --entrypoint python streamlit run_long_experiment.py @CliArgs



cd C:\Users\kesha\OneDrive\Desktop\IPProject\TeacherEvaluation

$env:GEMINI_API_KEY = (
  Get-Content .env |
  Where-Object { $_ -match '^\s*GEMINI_API_KEY\s*=' } |
  Select-Object -First 1
).Split('=',2)[1].Trim()

.\.venv\Scripts\python.exe .\tools\check_gemini_auth.py
