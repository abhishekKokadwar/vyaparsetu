try {
    $ppt = New-Object -ComObject PowerPoint.Application
    $resolvedPptx = (Resolve-Path 'VyaparSetu_Airtel_Sync_Presentation.pptx').Path
    $pdfPath = (Resolve-Path '.').Path + '\VyaparSetu_Airtel_Sync_Presentation.pdf'
    $pres = $ppt.Presentations.Open($resolvedPptx, [Microsoft.Office.Core.MsoTriState]::msoTrue, [Microsoft.Office.Core.MsoTriState]::msoFalse, [Microsoft.Office.Core.MsoTriState]::msoFalse)
    $pres.SaveAs($pdfPath, 32)
    $pres.Close()
    $ppt.Quit()
    Write-Host "Exported PDF successfully to $pdfPath"
} catch {
    Write-Host "COM Error: " $_.Exception.Message
}
