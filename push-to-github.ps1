Set-Location "C:\00-proj\jute-business"

Write-Host "=== JuteVerde: push to GitHub ===" -ForegroundColor Cyan

git init
git checkout -b main
git add .
git commit -m "Initial commit: JuteVerde social media agent"
git remote remove origin
git remote add origin "https://github.com/sameerjain01/jb-jute-social-agent-demo.git"
git push -u origin main

Write-Host "Done! Check: https://github.com/sameerjain01/jb-jute-social-agent-demo" -ForegroundColor Green
