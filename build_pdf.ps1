param(
    [string]$Source = 'notes/software-repository-management.md',
    [string]$Output = 'output/pdf/software-repository-management.pdf',
    [string]$Python = 'python',
    [string]$Font
)
$ErrorActionPreference = 'Stop'
Push-Location -LiteralPath $PSScriptRoot
try {
    & $Python (Join-Path $PSScriptRoot 'validate_markdown.py') $Source
    if ($LASTEXITCODE -ne 0) { throw 'Markdown validation failed.' }
    $renderArgs = @((Join-Path $PSScriptRoot 'md_to_pdf.py'), $Source, $Output)
    if ($Font) { $renderArgs += @('--font', $Font) }
    & $Python @renderArgs
    if ($LASTEXITCODE -ne 0) { throw 'PDF generation failed.' }
    Write-Output "PDF created: $Output. Review the rendered pages before publishing."
} finally {
    Pop-Location
}
