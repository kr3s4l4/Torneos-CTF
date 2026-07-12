Writeup: Travel Again - No Hack No CTF 2026

Categoría: OSINT
Puntos: 500
Flag: NHNC{43.1849,143.0325}
📝 Enunciado

    I snapped a photo while passing through a location during my trip. Since the car never stopped, the photo is all I have. I've forgotten where it was—can you identify the location?

    Flag format: NHNC{latitude,longitude} Truncate both the latitude and longitude to 4 decimal places (do not round).

Pista (0 points): "Not the shooting spot — the object itself."
🔍 Investigación
1. Análisis de metadatos

Se ejecutó exiftool sobre la imagen travel_again.jpg. Los metadatos no contenían coordenadas GPS, solo información básica y un perfil ICC de "Google Inc. 2016", indicando que la imagen fue procesada por Google Fotos/Android y los metadatos de ubicación fueron eliminados.
bash

exiftool travel_again.jpg
exiftool -a -u -g1 -ee travel_again.jpg
strings travel_again.jpg

Conclusión: No hay coordenadas en los metadatos. La ubicación debe identificarse visualmente.
2. Búsqueda visual con Google Lens

Se subió la imagen a Google Lens (images.google.com) y Yandex Images para búsqueda inversa. Los resultados no fueron concluyentes al principio, pero ayudaron a identificar elementos clave:

    Dos piedras/rocas verticales sobre un pedestal bajo con una placa conmemorativa

    Un panel informativo cercano

    Un edificio agrícola tipo granero/cobertizo sin paredes laterales, con tejado a dos aguas

    Meseta abierta sin árboles, con montañas nevadas al fondo

    Nieve en el suelo (entorno invernal)

3. Identificación del tipo de monumento

Por la apariencia (dos piedras sobre pedestal bajo con placa, en zona rural abierta), se investigaron monumentos conmemorativos japoneses. Se identificó que correspondía a un Kaitaku Kinenhi (開拓記念碑), monumentos dedicados a los pioneros/colonos que cultivaron las tierras de Hokkaido.

    Palabra clave: Kaitaku (開拓 = colonización)

    Región: Meseta de Tokachi, Hokkaido, Japón

    Características coincidentes: Monumentos de piedra rurales, placa en pedestal, panel informativo, junto a edificios agrícolas históricos

4. Búsqueda en internet del monumento específico

Con los términos "Kaitaku monument Tokachi", "開拓記念碑 十勝" y "Monumento colonización Tokachi panel informativo", se encontró:

    Monumento Conmemorativo de Oshima Ryokichi (大島亮吉記念碑)
    Monumento Histórico No. 127
    Ubicado en Shikaoi (鹿追町), Hokkaido

La descripción oficial confirmaba todas las características:

    Meseta abierta con vistas a las montañas al norte de la llanura de Tokachi

    Panel informativo del Geoparque Tokachi cercano

    Parking para coches (accesible desde carretera)

    Edificaciones rurales alrededor

5. Obtención de coordenadas exactas con Google Earth

Usando Google Earth, se localizó el monumento en Shikaoi y se identificaron tres elementos visibles en la foto:
Elemento	Coordenadas
Monumento Oshima Ryokichi	43°11'07.52"N 143°02'05.58"E
Granero/cobertizo	43°11'12.31"N 143°01'54.03"E
Panel informativo (cartel)	43°11'05.80"N 143°01'57.18"E
6. Interpretación de la pista

La pista decía: "Not the shooting spot — the object itself."

Tras probar las coordenadas del monumento sin éxito, se dedujo que el objeto principal de la foto no era el monumento ni el granero, sino el panel informativo (cartel). Esto encajaba con:

    Ser un punto de interés turístico señalizado

    Visible desde la carretera (foto tomada desde coche en movimiento)

    Ser el "objeto" central de la imagen

7. Conversión a formato flag

Coordenadas del panel informativo: 43°11'05.80"N 143°01'57.18"E

Conversión a grados decimales:

Latitud:
text

43 + (11/60) + (05.80/3600) = 43.184944... → truncado: 43.1849

Longitud:
text

143 + (01/60) + (57.18/3600) = 143.032550... → truncado: 143.0325

Flag final:
text

NHNC{43.1849,143.0325}

🛠️ Herramientas utilizadas
Herramienta	Uso
exiftool	Análisis de metadatos (sin GPS)
Google Lens	Búsqueda visual inversa
Yandex Images	Búsqueda visual complementaria
Búsqueda web	Identificación del tipo de monumento (Kaitaku)
Google Earth	Localización exacta y obtención de coordenadas
🎯 Conclusión

La dificultad del reto residió en tres factores:

    Falta de metadatos GPS (limpiados por Google Photos)

    Entorno rural genérico (meseta abierta nevada sin landmarks urbanos)

    Ambigüedad del "objeto" a geo-localizar (no era el monumento ni el edificio, sino el panel informativo)

La combinación de OSINT visual (Lens + búsqueda inversa), investigación cultural (identificar monumentos Kaitaku japoneses) y la interpretación correcta de la pista fueron clave para resolver el desafío.
