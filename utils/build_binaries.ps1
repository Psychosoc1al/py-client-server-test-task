# Uses WSL with Debian 12 installed to build binaries
wsl -e bash -c "python -m PyInstaller --clean --add-data '../.env:.' --specpath ../build --workpath ../build --distpath ../Debian-12-dist  --onefile ../client.py"
Write-Output `n`n
wsl -e bash -c "python -m PyInstaller --clean --add-data '../.env:.' --specpath ../build --workpath ../build --distpath ../Debian-12-dist  --onefile ../server.py"
