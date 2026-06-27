# Build audx.exe as a standalone Windows executable
pyinstaller --onefile --name audx audx/__main__.py
Write-Host "Built: dist\audx.exe"
