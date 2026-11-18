$ErrorActionPreference = 'Stop'
$reportPath = Join-Path $PSScriptRoot 'report.docx'
$renderFolder = Join-Path $PSScriptRoot 'rendered'
New-Item -ItemType Directory -Force -Path $renderFolder | Out-Null
$pdfPath = Join-Path $renderFolder 'report.pdf'
$wordApp = $null
$wordDocument = $null
try {
    $wordApp = New-Object -ComObject Word.Application
    Write-Output 'Created private Word automation instance'
    $wordApp.Visible = $true
    $wordApp.DisplayAlerts = 0
    $wordApp.AutomationSecurity = 3
    $wordDocument = $wordApp.Documents.Open($reportPath, $false, $false)
    Write-Output 'Opened report'
    $wordDocument.Repaginate()
    [void]$wordDocument.Fields.Update()
    for ($tocIndex = 1; $tocIndex -le $wordDocument.TablesOfContents.Count; $tocIndex++) {
        $wordDocument.TablesOfContents.Item($tocIndex).Update()
    }
    $wordDocument.Repaginate()
    $wordDocument.Save()
    Write-Output 'Updated fields and saved editable DOCX'
    [pscustomobject]@{
        WordVersion = $wordApp.Version
        Pages = $wordDocument.ComputeStatistics(2)
        TablesOfContents = $wordDocument.TablesOfContents.Count
        InlineImages = $wordDocument.InlineShapes.Count
        Paragraphs = $wordDocument.Paragraphs.Count
    } | ConvertTo-Json | Set-Content -Encoding UTF8 (Join-Path $PSScriptRoot 'evidence/word_render_info.json')
    Write-Output 'Exporting native PDF with SaveAs2'
    $wordDocument.SaveAs2($pdfPath, 17)
    Write-Output 'Exported PDF'
} finally {
    if ($null -ne $wordDocument) { $wordDocument.Close(0) }
    if ($null -ne $wordApp) { $wordApp.Quit() }
    if ($null -ne $wordDocument) { [void][Runtime.InteropServices.Marshal]::ReleaseComObject($wordDocument) }
    if ($null -ne $wordApp) { [void][Runtime.InteropServices.Marshal]::ReleaseComObject($wordApp) }
}
Get-Content (Join-Path $PSScriptRoot 'evidence/word_render_info.json')
