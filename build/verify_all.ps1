# run every check in one go
$ErrorActionPreference = "Continue"
Write-Output "=== 1. BUILD ==="
python build.py 2>&1 | Select-Object -First 1
Write-Output ""
Write-Output "=== 2. MODULE CHECK ==="
python modcheck.py 2>&1 | Select-Object -Last 3
Write-Output ""
Write-Output "=== 3. STRUCTURE + COVERAGE AUDIT ==="
python audit.py 2>&1 | Select-Object -Last 3
Write-Output ""
Write-Output "=== 4. TOPIC GROUNDING ==="
python check_vocab2.py 2>&1 | Select-Object -Last 1
Write-Output ""
Write-Output "=== 5. FUNCTIONAL (node) ==="
node verify.js 2>&1 | Select-Object -Last 1
Write-Output ""
Write-Output "=== 6. SIMPLIFIED CHARACTERS ==="
& .\scan_s2t.ps1 2>&1 | Select-Object -Last 1
Write-Output ""
Write-Output "=== 7. NEW-LESSON QA ==="
python qa_new.py 2>&1 | Select-Object -Last 1
Write-Output ""
Write-Output "=== 8. INTERNAL LINKS ==="
python check_links.py 2>&1 | Select-Object -Last 1
Write-Output ""
Write-Output "=== 9. GRAMMAR CLAIMS (cross-refs / verb three-forms) ==="
python qa_claims.py 2>&1 | Select-Object -Last 1
Write-Output ""
Write-Output "=== 10. A2 KEY TOPIC ATTRIBUTION ==="
python qa_topics.py 2>&1 | Select-Object -Last 1
