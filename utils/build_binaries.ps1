# Note LF EOL to use multiline commands

# Uses WSL with Debian 12 installed to build binaries
wsl -e bash -c "
source ../.venv/debian-venv/bin/activate &&
python -m PyInstaller \
    --noconfirm \
    --onefile \
    --add-data=../.env:. \
    --specpath=../build \
    --workpath=../build \
    --distpath=../Debian-12-dist \
    ../client.py
"

Write-Output `n`n

wsl -e bash -c "
python -m PyInstaller \
    --noconfirm \
    --onefile \
    --add-data=../.env:. \
    --specpath=../build \
    --workpath=../build \
    --distpath=../Debian-12-dist \
    ../server.py
"
