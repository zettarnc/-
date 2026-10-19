param(
    [Parameter(Mandatory = $true)][string]$Url,
    [Parameter(Mandatory = $true)][ValidatePattern('^[a-zA-Z0-9][a-zA-Z0-9_-]{0,79}$')][string]$LectureId,
    [ValidateSet('chrome', 'edge', 'firefox', 'brave')][string]$Browser,
    [string]$Python = 'python'
)
$ErrorActionPreference = 'Stop'
function Invoke-Checked {
    param([string]$Program, [string[]]$Arguments)
    & $Program @Arguments
    if ($LASTEXITCODE -ne 0) { throw "$Program failed with exit code $LASTEXITCODE" }
}
if ($Url -notmatch '^https://') { throw 'An HTTPS video URL is required.' }
foreach ($program in @($Python)) {
    if (-not (Get-Command $program -ErrorAction SilentlyContinue)) { throw "Missing dependency: $program" }
}
$workRoot = Join-Path $PSScriptRoot 'work'
$lectureDir = Join-Path $workRoot $LectureId
$captureArgs = @((Join-Path $PSScriptRoot 'acquire_video.py'), $Url, $lectureDir)
if ($Browser) { $captureArgs += @('--browser', $Browser) }
Invoke-Checked $Python $captureArgs
