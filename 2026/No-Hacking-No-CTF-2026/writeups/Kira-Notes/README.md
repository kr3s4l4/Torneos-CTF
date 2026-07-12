Writeup: Kira-Notes - No Hack No CTF 2026

Categoría: Forense / OSINT
Flag: NHNC{n0w_y0u_kn0w_h0w_t0_f0r3ns1c_0x00000Easyyyyyyyyy}
Enunciado

Se nos proporciona un archivo places.sqlite (base de datos de historial de Firefox) junto con sus archivos temporales .sqlite-shm y .sqlite-wal.
Paso 1: Análisis de places.sqlite
bash

sqlite3 places.sqlite
sqlite> .tables
sqlite> SELECT id, url, title FROM moz_places;

El historial revela varias URLs visitadas. La más relevante es:
ID	URL
44	https://drive.proton.me/urls/00MNVW0SHG#do4wWWpAQ0Lw

Este enlace de Proton Drive contiene los archivos del reto. El historial también muestra búsquedas de YouTube relacionadas con K-On y AniOne, revelando que la categoría del reto es Anime.
Paso 2: Descarga de los archivos desde Proton Drive

Accedemos al enlace y descargamos:
text

noth_____.png
of.img
Some Backup 01.png

Paso 3: La imagen truncada noth_____.png

El nombre está incompleto. Al abrir la imagen se ve parcialmente "0x0 kira". La imagen está rota/incompleta.

El nombre completo se deduce como: north0x0kira.png

Esto nos da la primera parte de una posible clave: 0x0kira
Paso 4: Análisis de of.img
bash

file of.img
# DOS/MBR boot sector; partition 1: ID=0xee

Es una imagen de disco. La montamos:
bash

fdisk -l of.img
# of.img1  2048  1021951  498M  Linux filesystem

mkdir /mnt/of_img
mount -o loop,offset=$((2048*512)) of.img /mnt/of_img

Contenido:
text

/mnt/of_img/home/ctf/Downloads/
├── I
├── it
├── let
├── not
├── see
├── will
└── you

Los 7 archivos están vacíos. Sus nombres forman la frase: "I will not let you see it". Es una pista de que hay archivos eliminados/ocultos en la imagen.
Paso 5: Búsqueda de archivos eliminados
bash

umount /mnt/of_img
strings of.img | grep -E "flag|zip|png"

Aparecen referencias a: flag.txt, final.zip, wtf.png

Usamos herramientas forenses. fls muestra $OrphanFiles pero los inodos huérfanos están vacíos. Recurrimos a foremost para carving:
bash

foremost -i of.img -o recuperados

Paso 6: Archivos recuperados

foremost extrae por firmas (magic bytes):
text

recuperados/
├── audit.txt
├── pdf/
│   └── 01019906.pdf
├── png/
│   └── 00543748.png
└── zip/
    └── 00543746.zip

    00543748.png: La versión completa de la imagen que antes estaba rota. Contiene el texto 0x0kira1337.

    00543746.zip: ZIP protegido con contraseña.

    01019906.pdf: PDF auxiliar.

Paso 7: La contraseña del ZIP

Unimos las pistas:
Fuente	Pista
noth_____.png (rota)	0x0kira
00543748.png (recuperada, completa)	0x0kira1337

La contraseña es 0x0kira1337. (El 1337 también aparecía como visitantes en el servidor web del historial.)
Paso 8: Extracción del ZIP

unzip no funciona (PK compat v5.1 requerida). Usamos 7z:
bash

7z x zip/00543746.zip
# Contraseña: 0x0kira1337

Extrae flag.txt:
text

NHNC{n0w_y0u_kn0w_h0w_t0_f0r3ns1c_0x00000Easyyyyyyyyy}

Resumen
Paso	Técnica	Herramienta
1	Análisis de historial Firefox	sqlite3
2	Descarga de archivos	Proton Drive
3	Inspección de imagen rota	Visor de imágenes
4	Montaje y análisis de imagen de disco	fdisk, mount
5	Búsqueda de strings y carving	strings, foremost
6	Recuperación de imagen completa	foremost (PNG)
7	Deducción de contraseña	Pistas visuales
8	Extracción de ZIP	7z
Flag
text

NHNC{n0w_y0u_kn0w_h0w_t0_f0r3ns1c_0x00000Easyyyyyyyyy}
