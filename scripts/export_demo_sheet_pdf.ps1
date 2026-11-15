$word = New-Object -ComObject Word.Application
$word.Visible = $false
$inPath = "D:\vedansh\Karthub-\Demo_Sheet.docx"
$outPath = "D:\vedansh\Karthub-\Demo_Sheet.pdf"

$doc = $word.Documents.Open($inPath)
# 17 = wdExportFormatPDF
$doc.ExportAsFixedFormat($outPath, 17)
$doc.Close([ref]$false)
$word.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($doc) | Out-Null
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
Write-Output "Exported Demo_Sheet.pdf successfully!"
