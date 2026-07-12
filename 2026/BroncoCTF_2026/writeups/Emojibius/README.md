# 🌊 Emojibius - BroncoCTF 2026

## "Sometimes you can tell what's written all over someone's face."

---

## 📡 Misión

Nuestra agencia de inteligencia ha interceptado una transmisión extraña. Parece que la Generación Z ha desarrollado un nuevo lenguaje... Encontramos una imagen críptica de una persona mayor en un servidor cercano. ¿Podrás recuperar el mensaje secreto?

---

## 🗂️ Archivos

| Archivo | Contenido |
|---------|-----------|
| `intercepted_signals.txt` | Secuencia de emojis |
| `imagen.png` | 5 emojis + cuadrícula de caracteres |

---

## 👁️‍🗨️ Inspección

### `intercepted_signals.txt`

```txt
🍎🍎 🍎🦊 🍎🍐 🍎🐶 🍎🎈 🍎🍐 🦊🍎 🦊🦊 🦊🍐 🦊🐶 🦊🎈 🍐🍎 🍐🦊 🍐🍐 🍎🦊 🍐🍐 🍎🎈 🍎🦊 🍐🍎 🍎🐶 🍐🐶 🍐🎈 🐶🍎

Imagen
text

🍎 🦊 🍐 🐶 🎈

bronc
{em0j
1s_g3
}adfh
iklpq

🧩 Pistas

    "Emojibius" → Emoji + ? (¿Obi-Wan? ¿Kenobi? Referencia a la imagen del anciano)

    ".tidalw" → ¿Tidal Wave? 🌊

    "Sometimes you can tell what's written all over someone's face" → Emojis de caras → expresiones → sistema de codificación basado en emojis

🔬 Análisis
1️⃣ Identificamos los símbolos

Hay 5 emojis únicos:
Emoji	Nombre
🍎	Manzana
🦊	Zorro
🍐	Pera
🐶	Perro
🎈	Globo

5 símbolos → Sistema Base 5 ✅
2️⃣ Asignamos valores
Emoji	Valor
🍎	0
🦊	1
🍐	2
🐶	3
🎈	4
3️⃣ Estructura de la transmisión

La secuencia está formada por pares de emojis:
text

🍎🍎 → par 1
🍎🦊 → par 2
🍎🍐 → par 3
...

Cada par representa un número en base 5 de 2 dígitos:
text

valor = (primer_emoji × 5) + segundo_emoji

Rango posible: 0 a 24 (25 combinaciones)
4️⃣ La imagen: una tabla de sustitución

Los 25 caracteres forman una cuadrícula 5×5:
text

      0  1  2  3  4
   ┌───────────────
 0 │ b  r  o  n  c
 1 │ {  e  m  0  j
 2 │ 1  s  _  g  3
 3 │ }  a  d  f  h
 4 │ i  k  l  p  q

Cada índice (0-24) apunta a una posición en esta tabla.
5️⃣ Decodificamos
Par	Cálculo	Índice	Carácter
🍎🍎	0×5+0	0	b
🍎🦊	0×5+1	1	r
🍎🍐	0×5+2	2	o
🍎🐶	0×5+3	3	n
🍎🎈	0×5+4	4	c
🍎🍐	0×5+2	2	o
🦊🍎	1×5+0	5	{
🦊🦊	1×5+1	6	e
🦊🍐	1×5+2	7	m
🦊🐶	1×5+3	8	0
🦊🎈	1×5+4	9	j
🍐🍎	2×5+0	10	1
🍐🦊	2×5+1	11	s
🍐🍐	2×5+2	12	_
🍎🦊	0×5+1	1	r
🍐🍐	2×5+2	12	_
🍎🎈	0×5+4	4	c
🍎🦊	0×5+1	1	r
🍐🍎	2×5+0	10	1
🍎🐶	0×5+3	3	n
🍐🐶	2×5+3	13	g
🍐🎈	2×5+4	14	3
🐶🍎	3×5+0	15	}
6️⃣ Mensaje reconstruido
text

b r o n c o { e m 0 j 1 s _ r _ c r 1 n g 3 }

🏁 Flag
text

bronco{em0j1s_r_cr1ng3}

    🔥 Traducción: bronco{emojis_r_creeping3}
    (Los números son leetspeak: 0=o, 1=i, 3=e)

🐍 Script de Solución
python

#!/usr/bin/env python3
# emojibius_solver.py

import re

# Mapeo de emojis → valores (Base 5)
EMOJI_TO_VAL = {
    '🍎': 0,
    '🦊': 1,
    '🍐': 2,
    '🐶': 3,
    '🎈': 4
}

# Cuadrícula 5×5 de la imagen
GRID = [
    ['b', 'r', 'o', 'n', 'c'],
    ['{', 'e', 'm', '0', 'j'],
    ['1', 's', '_', 'g', '3'],
    ['}', 'a', 'd', 'f', 'h'],
    ['i', 'k', 'l', 'p', 'q']
]

def decode_emojis(emoji_sequence: str) -> str:
    """Decodifica una secuencia de pares de emojis."""
    # Limpiar y extraer pares
    cleaned = emoji_sequence.replace(' ', '')
    pairs = re.findall(r'(.{2})', cleaned)
    
    flag = ''
    for pair in pairs:
        # Convertir par a índice
        a = EMOJI_TO_VAL[pair[0]]
        b = EMOJI_TO_VAL[pair[1]]
        index = a * 5 + b
        
        # Obtener carácter de la cuadrícula
        row = index // 5
        col = index % 5
        flag += GRID[row][col]
    
    return flag

if __name__ == '__main__':
    with open('intercepted_signals.txt', 'r') as f:
        data = f.read().strip()
    
    flag = decode_emojis(data)
    print(f'🚩 Flag: {flag}')

🧠 Conceptos Aprendidos
Concepto	Aplicación
Sistemas Numéricos	Base 5 con 5 símbolos
Codificación por Pares	Cada 2 emojis = 1 carácter
Tabla de Sustitución	Cuadrícula 5×5 para mapear índices
Leetspeak	Sustitución 0→o, 1→i, 3→e
Esteganografía	Información oculta en la imagen
🎯 Conclusión

El reto combinó:

    Criptografía (base 5 + tabla de sustitución)

    Esteganografía (información en la imagen)

    Observación (identificar los 5 emojis y la cuadrícula)

La flag final es:
text

bronco{em0j1s_r_cr1ng3}
