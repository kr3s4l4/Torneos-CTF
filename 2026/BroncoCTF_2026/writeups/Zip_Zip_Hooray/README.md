Writeup: BroncoCTF 2026 - "Zip, Zip, Hooray!"
📋 Información del Reto

    Nombre: Zip, Zip, Hooray!

    Categoría: Forensics / Miscelánea

    Dificultad: Media

    Puntos: 500

    Descripción:

        "I was trying to compress my files and my script got a little carried away... Can you help me find my original file?"

        Hint: the 7z files are password protected, and the password is the name of the first file inside

🔍 Reconocimiento Inicial
Archivo Proporcionado

El reto nos entrega un archivo llamado challenge.zip que, al intentar descomprimirlo con unzip, falla:
bash

┌──(root㉿kali)-[/home/kr3s4l4/TorneosCTF/BroncoCTF_2026]
└─# unzip challenge.zip
Archive:  challenge.zip
  End-of-central-directory signature not found.
  Either this file is not a zipfile, or it constitutes one disk of a multi-part archive.
note:  challenge.zip may be a plain executable, not an archive

Análisis Inicial
bash

# Renombrar para análisis
mv challenge.zip challenge

# Identificar tipo real
file challenge
challenge: gzip compressed data, was "layer1.tar", last modified: Sat Feb 28 02:39:52 2026

# Ver cabecera
xxd challenge | head -n 5
00000000: 1f8b 0808 7855 a269 02ff 6c61 7965 7231  ....xU.i..layer1
00000010: 2e74 6172 00ec ba67 5453 d1d7 3e88 5214  .tar...gTS..>.R.

Observación: El archivo es en realidad un GZIP que contiene un TAR llamado layer1.tar.
🗂️ Estructura de Capas

El reto consiste en 285 capas de compresión anidadas que siguen un patrón específico:
Patrón Identificado
Tipo de Capa	Números	Contraseña	Formato
IMPARES	1, 3, 5, 7, ...	Sin contraseña	.tar.gz, .bz2, .zip
PARES	2, 4, 6, 8, ...	Con contraseña	.7z
Secuencia Típica
text

layerN.7z (par, con contraseña)
    ↓ (contraseña = layer(N+2).zip)
layer(N+2).zip (sin contraseña)
    ↓
layer(N+3).tar.gz (sin contraseña)
    ↓
layer(N+4).bz2 (sin contraseña)
    ↓
layer(N+4) (7z, con contraseña)
    ↓ (contraseña = layer(N+6).zip)
...

🔧 Herramientas Utilizadas
Herramienta	Propósito
file	Identificar tipo de archivo
xxd / hexdump	Ver cabeceras mágicas
gunzip	Descomprimir GZIP
tar	Extraer archivos TAR
bunzip2	Descomprimir BZIP2
unzip	Descomprimir ZIP
7z	Descomprimir 7-Zip
binwalk	Extracción automática (opcional)
exiftool	Metadatos de archivos
bash	Automatización
🚀 Metodología de Extracción
Paso 1: Extracción Inicial
bash

# Renombrar a .gz y descomprimir
mv challenge challenge.gz
gunzip challenge.gz

# Extraer TAR
tar -xvf challenge
# Resultado: layer2.bz2

Paso 2: Identificar el Patrón de Contraseñas
bash

# Extraer layer2.bz2
bunzip2 layer2.bz2
# Resultado: layer2 (7z)

# Listar contenido del 7z para ver el nombre interno
7z l layer2
# Muestra: layer4.zip

# Extraer con la contraseña
7z x -p"layer4.zip" layer2
# Resultado: layer4.zip

Paso 3: Extracción Automatizada

Debido a las 285 capas, la extracción manual es inviable. Se creó un script automatizado:
Script de Extracción Completo
bash

#!/bin/bash
# ultra_extractor.sh - Extracción automática de todas las capas

echo "Iniciando extracción masiva..."
CONT=0

while true; do
    # Buscar cualquier archivo comprimido
    F=$(ls -t 2>/dev/null | grep -E "\.(gz|bz2|zip|tar|7z)$|^layer[0-9]+$" | head -1)
    [ -z "$F" ] && break
    [ -d "$F" ] && continue
    
    CONT=$((CONT + 1))
    [ $((CONT % 50)) -eq 0 ] && echo "   Procesadas $CONT capas..."
    
    # Extraer según tipo
    if file "$F" | grep -q "7-zip"; then
        P=$(7z l "$F" 2>/dev/null | grep -E "\.(zip|tar|gz|bz2|7z)" | head -1 | awk '{print $NF}')
        7z x -p"$P" "$F" -y 2>/dev/null || 7z x -p"${P%.*}" "$F" -y 2>/dev/null
    elif file "$F" | grep -q "gzip"; then
        [[ "$F" == *.tar.gz ]] && tar -xzvf "$F" 2>/dev/null || gunzip -f "$F" 2>/dev/null
    elif file "$F" | grep -q "bzip2"; then
        bunzip2 -f "$F" 2>/dev/null
    elif file "$F" | grep -q "Zip"; then
        unzip -o "$F" 2>/dev/null
    elif file "$F" | grep -q "tar"; then
        tar -xvf "$F" 2>/dev/null
    fi
    
    mkdir -p p 2>/dev/null
    mv "$F" p/ 2>/dev/null
done

echo "✅ Completado! $CONT capas procesadas"
echo ""
echo "🔍 FLAG ENCONTRADA:"
find . -type f -name "*flag*" -o -name "*.txt" | xargs cat 2>/dev/null

Script con Progreso y Manejo de Errores
bash

#!/bin/bash
# extractor_completo.sh - Versión con progreso detallado

echo "========================================="
echo "   EXTRACTOR AUTOMÁTICO - MODO INFINITO"
echo "========================================="
echo ""

TOTAL=0
EXITOS=0
ERRORES=0

extract_any() {
    local FILE="$1"
    [ ! -f "$FILE" ] && return 1
    
    local TYPE=$(file -b "$FILE")
    
    case "$TYPE" in
        *"7-zip archive"*)
            local INNER=$(7z l "$FILE" 2>/dev/null | grep -E "\.(zip|tar|gz|bz2|7z)" | head -1 | awk '{print $NF}')
            if [ -n "$INNER" ]; then
                7z x -p"$INNER" "$FILE" -y 2>/dev/null && return 0
                7z x -p"${INNER%.*}" "$FILE" -y 2>/dev/null && return 0
            fi
            7z x "$FILE" -y 2>/dev/null && return 0
            return 1
            ;;
        *"gzip compressed"*)
            if [[ "$FILE" == *.tar.gz ]] || [[ "$FILE" == *.tgz ]]; then
                tar -xzvf "$FILE" 2>/dev/null && return 0
            else
                gunzip -f "$FILE" 2>/dev/null && return 0
            fi
            return 1
            ;;
        *"bzip2 compressed"*)
            bunzip2 -f "$FILE" 2>/dev/null && return 0
            return 1
            ;;
        *"Zip archive"*)
            unzip -o "$FILE" 2>/dev/null && return 0
            return 1
            ;;
        *"POSIX tar archive"*)
            tar -xvf "$FILE" 2>/dev/null && return 0
            return 1
            ;;
        *)
            return 1
            ;;
    esac
}

while true; do
    ARCHIVO=$(ls -t 2>/dev/null | grep -E "\.(gz|bz2|zip|tar|7z)$|^layer[0-9]+$" | head -1)
    [ -z "$ARCHIVO" ] && break
    [ -d "$ARCHIVO" ] && continue
    
    TOTAL=$((TOTAL + 1))
    echo -n "[$TOTAL] Extrayendo: $ARCHIVO ... "
    
    if extract_any "$ARCHIVO"; then
        echo "✅ OK"
        EXITOS=$((EXITOS + 1))
    else
        echo "❌ ERROR"
        ERRORES=$((ERRORES + 1))
        mkdir -p errores 2>/dev/null
        mv "$ARCHIVO" errores/ 2>/dev/null
        continue
    fi
    
    mkdir -p procesados 2>/dev/null
    mv "$ARCHIVO" procesados/ 2>/dev/null
    
    if [ $((TOTAL % 10)) -eq 0 ]; then
        echo "   📊 Progreso: $TOTAL archivos procesados"
        echo "   📁 Archivos restantes: $(ls -1 2>/dev/null | grep -E '\.(gz|bz2|zip|tar|7z)$|^layer[0-9]+$' | wc -l)"
        echo ""
    fi
    
    if find . -maxdepth 1 -type f \( -name "*flag*" -o -name "*.txt" \) 2>/dev/null | grep -q .; then
        echo ""
        echo "🎉 ¡POSIBLE FLAG ENCONTRADA!"
        find . -maxdepth 1 -type f \( -name "*flag*" -o -name "*.txt" \) -exec cat {} \; 2>/dev/null | head -20
        echo ""
        echo "Continuando por si hay más capas..."
        echo ""
    fi
done

echo ""
echo "========================================="
echo "           RESUMEN FINAL"
echo "========================================="
echo "📊 Total archivos procesados: $TOTAL"
echo "✅ Exitosos: $EXITOS"
echo "❌ Errores: $ERRORES"
echo ""

find . -type f \( -name "*flag*" -o -name "*.txt" -o -name "*.flag" \) -not -path "./procesados/*" -not -path "./errores/*" 2>/dev/null | while read -r FLAG; do
    echo ""
    echo "📄 Archivo: $FLAG"
    echo "---"
    cat "$FLAG" 2>/dev/null | head -50
    echo "---"
done

echo "✨ ¡PROCESO COMPLETADO!"

🏆 Obtención de la Flag
Salida Final del Script
text

[285] Extrayendo: layer1000.zip ... Archive:  layer1000.zip
  inflating: flag.txt                
✅ OK

🎉 ¡POSIBLE FLAG ENCONTRADA!
bronco{i_h4te_f1l3_c0mpr3ssi0n}
Continuando por si hay más capas...

✅ No hay más archivos para extraer

=========================================
           RESUMEN FINAL
=========================================
📊 Total archivos procesados: 285
✅ Exitosos: 285
❌ Errores: 0

🔍 Buscando flags en todos los archivos...

📄 Archivo: ./flag.txt
---
bronco{i_h4te_f1l3_c0mpr3ssi0n}---

✨ ¡PROCESO COMPLETADO!

Flag Final
text

bronco{i_h4te_f1l3_c0mpr3ssi0n}

📊 Estadísticas del Reto
Métrica	Valor
Total de capas	285
Archivos 7z con contraseña	~143
Archivos sin contraseña	~142
Tamaño total procesado	~128 MB
Tiempo de extracción	~3-5 minutos
Última capa	layer1000.zip
💡 Lecciones Aprendidas
1. Identificación de Formatos

    Usar file para determinar el tipo real de archivo

    Verificar cabeceras mágicas con xxd o hexdump

    Las extensiones pueden ser engañosas

2. Patrones en CTFs

    Buscar patrones en los nombres de archivos

    Identificar secuencias numéricas

    La pista del reto es clave: "la contraseña es el nombre del primer archivo dentro"

3. Automatización

    Scripts en bash para tareas repetitivas

    Manejo de errores y casos límite

    Uso de herramientas como file, 7z, tar, unzip

4. Herramientas Útiles

    7z l: Listar contenido sin extraer

    file -b: Output limpio para scripts

    Redirección de errores 2>/dev/null

    -y para respuestas automáticas

🛠️ Comandos Útiles
Extracción Individual
bash

# GZIP
gunzip archivo.gz

# TAR
tar -xvf archivo.tar

# GZIP + TAR
tar -xzvf archivo.tar.gz

# BZIP2
bunzip2 archivo.bz2

# ZIP
unzip archivo.zip

# 7-Zip (con contraseña)
7z x -p"contraseña" archivo.7z

# Listar contenido 7z
7z l archivo.7z

Automatización
bash

# Monitorear progreso
watch -n 2 'ls -1 | grep -E "\.(gz|bz2|zip|tar|7z)$|^layer[0-9]+$" | wc -l'

# Buscar flag
find . -name "*flag*" -o -name "*.txt" | xargs cat

# Limpiar archivos temporales
rm -rf procesados/ p/ errores/

📝 Reflexión Final

Este reto demuestra la importancia de:

    Paciencia: 285 capas requieren perseverancia

    Automatización: La extracción manual sería imposible

    Observación: Identificar patrones es crucial

    Conocimiento de herramientas: Saber usar las herramientas adecuadas

    Pensamiento lateral: La pista de las contraseñas fue clave

La flag es un claro mensaje del creador del reto:

    i_h4te_f1l3_c0mpr3ssi0n

📎 Apéndice: Estructura de Directorios Final
text

BroncoCTF_2026/
├── challenge               # Archivo original (GZIP)
├── ctf_token               # Token del CTF
├── flag.txt                # ¡FLAG ENCONTRADA!
├── procesados/             # 285 archivos procesados
│   ├── layer1.tar
│   ├── layer2.7z
│   ├── ...
│   └── layer1000.zip
├── p/                      # Archivos procesados (script rápido)
└── errores/                # Archivos con errores (vacío)
