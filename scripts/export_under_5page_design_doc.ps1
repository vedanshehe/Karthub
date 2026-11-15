$word = New-Object -ComObject Word.Application
$word.Visible = $false

$inPath = "D:\vedansh\Karthub-\Database_Design_Document.docx"
$outPath1 = "D:\vedansh\Karthub-\Database_Design_Document.pdf"
$outPath2 = "D:\Database_Design_Document.pdf"

$doc = $word.Documents.Open($inPath)
$doc.ExportAsFixedFormat($outPath1, 17)
$doc.Close([ref]$false)
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($doc) | Out-Null

Copy-Item -Force $outPath1 $outPath2
Copy-Item -Force $inPath "D:\Database_Design_Document.docx"
Copy-Item -Force $inPath "D:\KartHub_Database_Design_Document.docx"

$word.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null

Write-Output "Successfully exported Database_Design_Document.pdf!"
