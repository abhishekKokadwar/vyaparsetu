try {
    $ppt = New-Object -ComObject PowerPoint.Application
    $resolvedPptx = (Resolve-Path 'VyaparSetu_Hacker247_Submission.pptx').Path
    $pres = $ppt.Presentations.Open($resolvedPptx, [Microsoft.Office.Core.MsoTriState]::msoTrue, [Microsoft.Office.Core.MsoTriState]::msoFalse, [Microsoft.Office.Core.MsoTriState]::msoFalse)
    $pdfPath = (Resolve-Path '.').Path + '\VyaparSetu_Hacker247_Submission.pdf'
    $pres.SaveAs($pdfPath, 32)
    $pres.Close()
    $ppt.Quit()
    Write-Host "Exported PDF successfully to $pdfPath"
} catch {
    Write-Host "COM Error: " $_.Exception.Message
}

