$word = New-Object -ComObject Word.Application
$word.Visible = $false

# 1. Export 5-page compliant doc to Database_Design_Document.pdf
$in5 = "D:\vedansh\Karthub-\Database_Design_Document_5Page.docx"
$out5 = "D:\vedansh\Karthub-\Database_Design_Document.pdf"
$d5 = $word.Documents.Open($in5)
$d5.ExportAsFixedFormat($out5, 17)
$d5.Close([ref]$false)
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($d5) | Out-Null

# 2. Export 7-page full mirror to Database_Design_Document_7Page.pdf
$in7 = "D:\vedansh\Karthub-\Database_Design_Document.docx"
$out7 = "D:\vedansh\Karthub-\Database_Design_Document_7Page.pdf"
$d7 = $word.Documents.Open($in7)
$d7.ExportAsFixedFormat($out7, 17)
$d7.Close([ref]$false)
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($d7) | Out-Null

# Also copy 5-page and 7-page docx/pdf to D:\ root for direct visibility
Copy-Item -Force $out5 "D:\Database_Design_Document.pdf"
Copy-Item -Force $out7 "D:\KartHub_Database_Design_Document_7Page.pdf"
Copy-Item -Force $in7 "D:\KartHub_Database_Design_Document.docx"

$word.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null

Write-Output "Successfully exported and copied both design document versions!"
