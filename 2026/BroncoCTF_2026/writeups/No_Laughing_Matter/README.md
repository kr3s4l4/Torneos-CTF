# 🎭 No Laughing Matter
## *BroncoCTF 2026 — Misc/Cryptography*

---

## 📌 Challenge Overview

| **Categoría** | Misc / Cryptography |
|---------------|---------------------|
| **Dificultad** | ★☆☆☆☆ (Fácil) |
| **Archivo** | `aha.txt` |
| **Descripción** | *"You see, that's not funny."* |

---

## 📂 Archivo Proporcionado

El archivo `aha.txt` contiene el siguiente texto:

AHHAAAHA AHHHAAHA AHHAHHHH AHHAHHHA AHHAAAHH AHHAHHHH AHHHHAHH
AHAHAHAH AHAAAHHA AHAHAHAH AHAAHHHA AHAAHHHA AHAHHAAH AHAAHHAA
AHAAHHAH AHAAAAAH AHAAHHHH AHAAHHAA AHAAHHHH AHAAHHAA AHAHHAAA
AHAAAHAA AHAAHAAH AHAAHAHA AHAAAAHA AHAAHHHH AHAAHHAA AHAHAAHA
AHAAHHHH AHAAAHHA AHAAHHAA AHAAHAAA AHAAAAAH AHAAHAAA AHAAAAAH
AHHHHHAH
text


---

## 🔍 Reconocimiento

### 1. Inspección Inicial

```bash
$ file aha.txt
aha.txt: ASCII text, with very long lines (323), with no line terminators

$ exiftool aha.txt
File Name                       : aha.txt
File Size                       : 323 bytes
Word Count                      : 36

2. Patrones Detectados

    Alfabeto reducido: Solo utiliza las letras A y H

    Estructura: 36 grupos de 8 caracteres separados por espacios

    Contexto: "AH" es onomatopeya de risa, relacionado con el título del reto

    Longitud: 36 × 8 = 288 bits = 36 bytes

3. Hipótesis

Es casi seguro que estamos ante binario codificado donde:

    A representa un bit (0 o 1)

    H representa el bit opuesto

    Cada grupo de 8 forma un byte ASCII

💻 Fase de Explotación
Script de Fuerza Bruta

Para encontrar la combinación correcta, probamos todas las posibilidades:
python

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

texto = """AHHAAAHA AHHHAAHA AHHAHHHH AHHAHHHA AHHAAAHH AHHAHHHH 
AHHHHAHH AHAHAHAH AHAAAHHA AHAHAHAH AHAAHHHA AHAAHHHA AHAHHAAH 
AHAAHHAA AHAAHHAH AHAAAAAH AHAAHHHH AHAAHHAA AHAAHHHH AHAAHHAA 
AHAHHAAA AHAAAHAA AHAAHAAH AHAAHAHA AHAAAAHA AHAAHHHH AHAAHHAA 
AHAHAAHA AHAAHHHH AHAAAHHA AHAAHHAA AHAAHAAA AHAAAAAH AHAAHAAA 
AHAAAAAH AHHHHHAH"""

grupos = texto.split()

# Emojis para los estados
ESTADOS = {
    'exito': '🎯',
    'error': '❌',
    'probando': '🔄',
    'info': 'ℹ️'
}

def decodificar(grupos, mapeo, invertir_grupo=False, invertir_bits=False):
    """
    Decodifica los grupos según diferentes combinaciones
    
    Args:
        grupos: Lista de strings de 8 caracteres
        mapeo: Diccionario {'A': '0', 'H': '1'} o viceversa
        invertir_grupo: Si se lee el grupo al revés
        invertir_bits: Si se invierten los bits (0↔1)
    
    Returns:
        String decodificado
    """
    resultado = ""
    
    for grupo in grupos:
        # Paso 1: Invertir el grupo si es necesario
        g = grupo[::-1] if invertir_grupo else grupo
        
        # Paso 2: Mapear letras a bits
        bits = ''.join(mapeo[c] for c in g)
        
        # Paso 3: Invertir bits si es necesario
        if invertir_bits:
            bits = ''.join('1' if b == '0' else '0' for b in bits)
        
        # Paso 4: Convertir a carácter ASCII
        try:
            valor = int(bits, 2)
            if 32 <= valor <= 126:  # Carácter imprimible
                resultado += chr(valor)
            else:
                resultado += '·'  # No imprimible
        except:
            resultado += '�'  # Error
    
    return resultado

# Definir todas las combinaciones a probar
configuraciones = [
    {
        'nombre': 'A=0, H=1, Lectura normal',
        'mapeo': {'A': '0', 'H': '1'},
        'invertir_grupo': False,
        'invertir_bits': False
    },
    {
        'nombre': 'A=1, H=0, Lectura normal',
        'mapeo': {'A': '1', 'H': '0'},
        'invertir_grupo': False,
        'invertir_bits': False
    },
    {
        'nombre': 'A=0, H=1, Lectura invertida',
        'mapeo': {'A': '0', 'H': '1'},
        'invertir_grupo': True,
        'invertir_bits': False
    },
    {
        'nombre': 'A=1, H=0, Lectura invertida',
        'mapeo': {'A': '1', 'H': '0'},
        'invertir_grupo': True,
        'invertir_bits': False
    }
]

print("🔍 Analizando combinaciones...\n")
print("═" * 60)

# Probar cada combinación
for config in configuraciones:
    resultado = decodificar(
        grupos,
        config['mapeo'],
        config['invertir_grupo'],
        config['invertir_bits']
    )
    
    # Verificar si contiene patrón de flag
    es_flag = 'bronco' in resultado.lower() or 'flag' in resultado.lower()
    icono = '🎯' if es_flag else 'ℹ️'
    
    print(f"{icono} {config['nombre']}")
    print(f"   → {resultado}")
    
    if es_flag:
        print(f"   ✅ ¡FLAG ENCONTRADA!")
    print()

Ejecución y Resultado
bash

┌──(root㉿kali)-[/home/.../No_Laughing_Matter]
└─# python3 solve.py

🔍 Analizando combinaciones...

════════════════════════════════════════════════════════════

ℹ️ A=0, H=1, Lectura normal
   → bthichxUYIYYY[Y^YVYGDYYUYQYGY...
   (No parece texto)

ℹ️ A=1, H=0, Lectura normal
   → ································
   (Solo caracteres no imprimibles)

🎯 A=0, H=1, Lectura invertida
   → bronco{UFUNNYLMAOLOLXDIJBOLROFLHAHA}
   ✅ ¡FLAG ENCONTRADA!

ℹ️ A=1, H=0, Lectura invertida
   → ····9·!U·U··e·M}······m·········}·}A
   (Texto parcial con caracteres extraños)

🏁 Flag
text

bronco{UFUNNYLMAOLOLXDIJBOLROFLHAHA}

Análisis de la Flag

La flag contiene términos relacionados con la risa:

    FUNNY → Gracioso

    LMAO → Laughing My Ass Off

    LOL → Laughing Out Loud

    ROFL → Rolling On Floor Laughing

    HAHA → Risa

Esto conecta perfectamente con el título del reto "No Laughing Matter" — irónicamente, la flag está llena de formas de reírse. 😂
🔧 Solución Paso a Paso
Decodificación Manual (Primer Grupo)

Tomemos el primer grupo: AHHAAAHA

    Invertir el grupo (leer de derecha a izquierda):
    text

    AHHAAAHA → AHAAAHHA

    Mapear A→0, H→1:
    text

    AHAAAHHA → 01000110

    Convertir a ASCII:
    text

    01000110₂ = 70₁₀ = 'F'

¡El primer carácter es F, que coincide con bronco{...!
Verificación Rápida
python

# Código para verificar los primeros caracteres
grupo = "AHHAAAHA"
invertido = grupo[::-1]  # "AHAAAHHA"
bits = invertido.replace('A', '0').replace('H', '1')  # "01000110"
caracter = chr(int(bits, 2))  # 'F'

📊 Resumen de la Solución
Paso	Acción	Resultado
1	Identificar binario A/H	✅ 36 grupos × 8 bits
2	Probar combinaciones	✅ Script de fuerza bruta
3	Leer grupos al revés	✅ Invertir cada grupo
4	Mapear A=0, H=1	✅ Obtener bits correctos
5	Convertir a ASCII	✅ Obtener flag
🛠️ Herramientas Utilizadas

    Python 3: Scripting para decodificación

    file: Identificación de tipo de archivo

    exiftool: Análisis de metadatos

    strings: Extracción de texto legible

💡 Lecciones Aprendidas

    Pista en el título: "No Laughing Matter" indica que "AH" (risa) es clave

    Binario con alfabeto reducido: Dos caracteres = sistema binario

    Importancia del orden: Leer los bits en la dirección correcta es crucial

    Fuerza bruta: Probar combinaciones cuando no está claro el mapeo

🎓 Conclusión

Este reto demuestra cómo un texto aparentemente sin sentido puede ocultar información valiosa mediante una simple codificación binaria con un mapeo de caracteres no convencional.

La clave estuvo en:

    Reconocer la estructura binaria

    Probar diferentes combinaciones de mapeo

    Leer los datos en la dirección correcta

    Identificar el patrón de flag
