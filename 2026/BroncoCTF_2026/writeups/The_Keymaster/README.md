The Keymaster - Writeup
📋 Descripción del Reto

    The Keymaster has split a flag into 8 keys and hid them in plain sight.

    Quite literally, as they're on our advertisement page!

    Ready your cursor-pointers, pull out your trusty inspection panel, and find them quickly, detective!

El reto consiste en encontrar 8 partes de una bandera escondidas en diferentes lugares de la página web de BroncoCTF. Cada parte está precedida por un número (1 -, 2 -, etc.) que indica su posición en la flag final.
🔍 Metodología de Búsqueda
1. Inspección del Código Fuente HTML

Lo primero es abrir la página y analizar el código fuente. Podemos hacerlo con:

    Ctrl+U (Ver código fuente)

    F12 → pestaña "Elements"

    curl -s https://broncosec.com/BroncoCTF

2. Parte 1: 1 - bronco{h

📌 Ubicación: Footer de la página

Al final del código HTML, en el pie de página, encontramos:
html

<p class="md:text-base text-sm md:font-normal text-zinc-100">
    ...
    <br/>
    1 - bronco{h
</p>

Parte 1: bronco{h
3. Parte 3: 3 - 0und_th3

📌 Ubicación: Atributo title del botón "Join the Competition"
html

<button class="registration_Button" style="z-index:1">
    <a title="3 - 0und_th3" href="https://broncoctf.ctfd.io/">
        Join the Competition
    </a>
</button>

Parte 3: 0und_th3
4. Parte 4: 4 - m_4ll_w1

📌 Ubicación: Cookie

Al inspeccionar las cookies de la página (F12 → Application → Cookies), encontramos que la cookie asociada al emoji 🙋 contiene la parte 4.
html

<span id="cookie" class="cursor-pointer">🙋</span>

Parte 4: m_4ll_w1
5. Parte 5: 5 - th_4b501

📌 Ubicación: Comentario HTML oculto entre el código

Revisando el código fuente en busca de 5 -, encontramos:
text

!!! 5 - th_4b501 !!!

Parte 5: th_4b501
6. Parte 6: 6 - ut31y_n0

📌 Ubicación: Parámetro KEY en un enlace
html

<a href="/BroncoCTF?KEY=6-ut31y_n0" class="relative group block p-2 h-full w-full">
    <div class="...">
        <h4 class="...">BroncoCTF 2026...?</h4>
    </div>
</a>

Parte 6: ut31y_n0
7. Parte 7: 7 - _w0rr135

📌 Ubicación: Archivo 7.txt

En el texto de la página encontramos un enlace a un archivo:
html

BroncoCTF <a href="/7.txt" download="7.txt">2026</a> will be our fifth CTF...

Al acceder a https://broncosec.com/7.txt obtenemos:
text

7 - _w0rr135

Parte 7: _w0rr135
8. Parte 8: 8 - _4t_411}

📌 Ubicación: Atributo alt de una imagen
html

<img src="correct-flag-colorized.svg" alt="8 - _4t_411}" class="large-icon ..."/>

Parte 8: _4t_411}
9. Parte 2: 2 - 3y_y0u_f ⭐

📌 Ubicación: Archivo JavaScript (la más difícil de encontrar)

Inspeccionando los archivos JavaScript cargados por la página, encontramos en / _next/static/chunks/e785679bf8074938.js:
javascript

// ... código ofuscado ...
e.firstChild.textContent+="2 - 3y_y0u_f"
// ... más código ...

Parte 2: 3y_y0u_f
🧩 Ensamblaje de la Bandera

Ordenando las partes según los números encontrados:
#	Parte
1	bronco{h
2	3y_y0u_f
3	0und_th3
4	m_4ll_w1
5	th_4b501
6	ut31y_n0
7	_w0rr135
8	_4t_411}
🚩 Flag Final
text

bronco{h3y_y0u_f0und_th3m_4ll_w1th_4b501ut31y_n0_w0rr135_4t_411}

📝 Tabla Resumen
Parte	Fragmento	Ubicación
1	bronco{h	Footer de la página
2	3y_y0u_f	Archivo JavaScript (e785679bf8074938.js)
3	0und_th3	Atributo title del botón
4	m_4ll_w1	Cookie
5	th_4b501	Comentario HTML
6	ut31y_n0	Parámetro KEY en URL
7	_w0rr135	Archivo 7.txt
8	_4t_411}	Atributo alt de imagen
🛠️ Herramientas Utilizadas

    Navegador: Inspección de elementos, consola, cookies

    curl: Para descargar archivos y analizar respuestas

    grep: Para buscar patrones en archivos descargados

💡 Lecciones Aprendidas

    Revisar todos los lugares posibles: HTML, CSS, JavaScript, cookies, archivos, headers

    Buscar patrones: Las partes tenían el formato número - texto

    No confiar en lo visible: La parte 2 estaba ofuscada en un archivo JS

    Usar herramientas adecuadas: La inspección del navegador y curl son esenciales

📂 Archivos Relacionados

    7.txt → Contiene la parte 7

    e785679bf8074938.js → Archivo JS con la parte 2

    correct-flag-colorized.svg → Imagen con la parte 8 en su alt
