param(
    [string]$OutputRoot = "/outputs/thesis_batch_round2"
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path $ScriptDir -Parent
$Runner = Join-Path $RepoRoot "runner.ps1"

if (-not (Test-Path $Runner)) {
    Write-Error "Could not find runner.ps1 at $Runner"
    exit 1
}

$clips = @(
    @{
        Id = "mit_linear_eq"
        Video = "clips/mit_ocw_linear_eq_180_240.mp4"
        Note = "Classic blackboard interaction and audience re-engagement"
    },
    @{
        Id = "stanford_hbb"
        Video = "clips/stanford_hbb_300_360.mp4"
        Note = "Energetic lecture-hall delivery with room scanning"
    },
    @{
        Id = "yale_rome"
        Video = "clips/yale_rome_180_240.mp4"
        Note = "Humanities lecture with moderate movement and re-engagement"
    },
    @{
        Id = "stanford_give_lecture"
        Video = "clips/stanford_give_lecture_180_240.mp4"
        Note = "Speaker-centric communication clip with expressive gestures"
    }
)

Set-Location $RepoRoot

foreach ($clip in $clips) {
    Write-Host ""
    Write-Host "=== Running $($clip.Id) ===" -ForegroundColor Cyan
    Write-Host $clip.Note -ForegroundColor DarkGray
    & $Runner `
        --video $clip.Video `
        --output-root "$OutputRoot/$($clip.Id)" `
        --enable-semantic `
        --enable-coaching

    if ($LASTEXITCODE -ne 0) {
        Write-Error "Run failed for $($clip.Id)"
        exit $LASTEXITCODE
    }
}

Write-Host ""
Write-Host "All four thesis batch runs completed under $OutputRoot" -ForegroundColor Green
