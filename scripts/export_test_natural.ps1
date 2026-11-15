$w = New-Object -ComObject Word.Application
$w.Visible = $false
$d = $w.Documents.Open('D:\test_natural.docx')
$d.ExportAsFixedFormat('D:\test_natural.pdf', 17)
$d.Close([ref]$false)
$w.Quit()
Write-Output "Exported natural PDF successfully"
