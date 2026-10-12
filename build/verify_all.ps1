# run every check in one go (15 checks)
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
Write-Output ""
Write-Output "=== 11. TYPING WIRING ==="
python qa_typing.py 2>&1 | Select-Object -Last 2
Write-Output ""
Write-Output "=== 12. TYPING BEHAVIOUR (node) ==="
node test_typing.js 2>&1 | Select-Object -Last 1
Write-Output ""
Write-Output "=== 13. RATE PRESETS (node) ==="
node test_rate.js 2>&1 | Select-Object -Last 1
Write-Output ""
Write-Output "=== 14. READING PAGE (node) ==="
node test_reading.js 2>&1 | Select-Object -Last 1
Write-Output ""
Write-Output "=== 15. ERROR NOTEBOOK / SRS (node) ==="
node test_eb.js 2>&1 | Select-Object -Last 1
Write-Output ""
