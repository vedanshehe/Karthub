$word = New-Object -ComObject Word.Application
$word.Visible = $false

# 1. Export D:\DBMS_Project_Demo_Sheet_One_Page.docx to PDF
$inPath1 = "D:\DBMS_Project_Demo_Sheet_One_Page.docx"
$outPath1 = "D:\DBMS_Project_Demo_Sheet_One_Page.pdf"
$doc1 = $word.Documents.Open($inPath1)
$doc1.ExportAsFixedFormat($outPath1, 17) # 17 = wdExportFormatPDF
$doc1.Close([ref]$false)
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($doc1) | Out-Null

# 2. Export D:\vedansh\Karthub-\Demo_Sheet.docx to D:\vedansh\Karthub-\Demo_Sheet.pdf
$inPath2 = "D:\vedansh\Karthub-\Demo_Sheet.docx"
$outPath2 = "D:\vedansh\Karthub-\Demo_Sheet.pdf"
$doc2 = $word.Documents.Open($inPath2)
$doc2.ExportAsFixedFormat($outPath2, 17)
$doc2.Close([ref]$false)
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($doc2) | Out-Null

$word.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null

Write-Output "Successfully exported both PDFs!"
