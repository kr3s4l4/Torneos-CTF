#!/usr/bin/env python3

texto = "AHHAAAHA AHHHAAHA AHHAHHHH AHHAHHHA AHHAAAHH AHHAHHHH AHHHHAHH AHAHAHAH AHAAAHHA AHAHAHAH AHAAHHHA AHAAHHHA AHAHHAAH AHAAHHAA AHAAHHAH AHAAAAAH AHAAHHHH AHAAHHAA AHAAHHHH AHAAHHAA AHAHHAAA AHAAAHAA AHAAHAAH AHAAHAHA AHAAAAHA AHAAHHHH AHAAHHAA AHAHAAHA AHAAHHHH AHAAAHHA AHAAHHAA AHAAHAAA AHAAAAAH AHAAHAAA AHAAAAAH AHHHHHAH"

grupos = texto.split()

print("Probando 4 combinaciones:\n")

combinaciones = [
    ("A=0, H=1, normal", False, False),
    ("A=1, H=0, normal", False, True),
    ("A=0, H=1, invertido", True, False),
    ("A=1, H=0, invertido", True, True),
]

for nombre, invertir_grupo, mapeo_invertido in combinaciones:
    resultado = ""
    for grupo in grupos:
        # Invertir el grupo si es necesario
        g = grupo[::-1] if invertir_grupo else grupo
        
        # Mapear A y H a bits
        if mapeo_invertido:
            # A=1, H=0
            bits = g.replace('A', '1').replace('H', '0')
        else:
            # A=0, H=1
            bits = g.replace('A', '0').replace('H', '1')
        
        # Convertir a ASCII
        try:
            char = chr(int(bits, 2))
            if 32 <= ord(char) <= 126:
                resultado += char
            else:
                resultado += '·'
        except:
            resultado += '·'
    
    print(f"{nombre}:")
    print(f"  {resultado[:100]}...")
    if 'flag' in resultado.lower() or 'bronco' in resultado.lower():
        print(f"  🎯 ¡FLAG ENCONTRADA!")
        print(f"  Completa: {resultado}")
    print()

# Mostrar la flag completa si se encontró
print("\n" + "="*50)
print("Si ves 'bronco{' o 'flag{' arriba, esa es la flag completa")
print("="*50)
