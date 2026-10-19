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
foreach ($program in @($Python, 'ffmpeg', 'ffprobe')) {
    if (-not (Get-Command $program -ErrorAction SilentlyContinue)) { throw "Missing dependency: $program" }
}
Invoke-Checked $Python @('-m', 'yt_dlp', '--version')
$workRoot = Join-Path $PSScriptRoot 'work'
$lectureDir = Join-Path $workRoot $LectureId
if (Test-Path -LiteralPath $lectureDir) { throw "Work directory already exists: $lectureDir. Choose a new LectureId." }
New-Item -ItemType Directory -Path (Join-Path $lectureDir 'frames') -Force | Out-Null
$commonArgs = @('-m', 'yt_dlp', '--no-playlist')
if ($Browser) { $commonArgs += @('--cookies-from-browser', $Browser) }
Push-Location -LiteralPath $lectureDir
try {
    $metadataLines = & $Python @commonArgs '--dump-single-json' '--skip-download' $Url
    if ($LASTEXITCODE -ne 0) { throw 'Metadata acquisition failed.' }
    $metadataString = $metadataLines -join "`n"
    $metadata = $metadataString | ConvertFrom-Json
    if ($metadata._type -eq 'playlist' -or $metadata.entries) { throw 'Select a single video/part before continuing.' }
    $metadataString | Set-Content -LiteralPath 'metadata.json' -Encoding utf8
    Invoke-Checked $Python ($commonArgs + @('--write-subs', '--write-auto-subs', '--sub-langs', 'zh.*,ai-zh,en.*', '--convert-subs', 'srt', '--skip-download', '-o', 'captions.%(ext)s', $Url))
    Invoke-Checked $Python ($commonArgs + @('-f', 'bv*+ba/b', '--merge-output-format', 'mp4', '-o', 'video.%(ext)s', $Url))
    $videoCandidates = @(Get-ChildItem -LiteralPath $lectureDir -File | Where-Object { $_.Name -match '^video\.(mp4|mkv|webm|mov)$' })
    if ($videoCandidates.Count -ne 1) { throw 'Expected exactly one downloaded video.' }
    $videoPath = $videoCandidates[0].FullName
    $probeLines = & ffprobe '-v' 'error' '-show_format' '-show_streams' '-of' 'json' $videoPath
    if ($LASTEXITCODE -ne 0) { throw 'ffprobe failed.' }
    ($probeLines -join "`n") | Set-Content -LiteralPath 'media-info.json' -Encoding utf8
    Invoke-Checked 'ffmpeg' @('-n', '-i', $videoPath, '-vf', 'fps=1/15', '-q:v', '3', 'frames/frame_%05d.jpg')
    $subtitleCandidates = @(Get-ChildItem -LiteralPath $lectureDir -Filter '*.srt' -File | Select-Object -ExpandProperty Name)
    [ordered]@{
        source_url = $Url
        title = $metadata.title
        duration_seconds = $metadata.duration
        subtitle_candidates = $subtitleCandidates
        subtitle_selection = 'pending'
        frame_sampling_seconds = 15
        semantic_review = 'pending'
        notes_generation = 'pending'
    } | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath 'acquisition.json' -Encoding utf8
    if ($subtitleCandidates.Count -eq 0) { Write-Warning 'No SRT obtained. OCR or ASR is required before a complete note can be verified.' }
    Write-Output "Acquisition finished: $lectureDir. Select and verify subtitles and frames before writing notes."
} finally {
    Pop-Location
}
