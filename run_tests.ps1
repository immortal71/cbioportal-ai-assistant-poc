# PowerShell script to run comprehensive tests
# Navigate to project directory
Set-Location C:\Users\HUAWEI\Downloads\PoC-cbioPortal\cbioportal-ai-assistant-poc

Write-Host "Starting backend server..." -ForegroundColor Green
$job = Start-Job -ScriptBlock {
    Set-Location C:\Users\HUAWEI\Downloads\PoC-cbioPortal\cbioportal-ai-assistant-poc
    python -m uvicorn backend.main:app --port 8000
}

Write-Host "Waiting for server to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 8

Write-Host "`nRunning comprehensive test suite..." -ForegroundColor Cyan
python test_comprehensive_llm.py

Write-Host "`nStopping backend server..." -ForegroundColor Yellow
Stop-Job -Job $job
Remove-Job -Job $job

Write-Host "`nDone!" -ForegroundColor Green
