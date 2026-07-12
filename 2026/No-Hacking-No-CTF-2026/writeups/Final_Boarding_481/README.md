Writeup: Final Boarding (OSINT)
Enunciado

    On the last day of the trip, I stood in front of the boarding gate, ready to board my flight home. That day in Japan marked the end of Golden Week, and the airport was packed with travelers preparing to return home. Before boarding, I took a photo of the aircraft in front of me; it was the flight I was about to take.

    Find: The date the photo was taken & The IATA flight number.

    Flag format: NHNC{YYYYMMDD_FLIGHT}

Paso 1: Análisis de metadatos (EXIF)

Ejecutamos exiftool sobre la imagen Final_boarding.png:
bash

exiftool Final_boarding.png

Hallazgos clave:
Metadato	Valor
Date/Time Original	2026:05:05 14:49:53+09:00
Make / Model	Google Pixel 8
Software	HDR+ 1.0.888945374zd
GPS Img Direction	134° (Magnetic North)
Offset Time	+09:00 (JST - Japón)

Conclusión: La foto fue tomada el 5 de mayo de 2026 a las 14:49 hora de Japón, durante el final de la Golden Week.
Paso 2: Identificación visual de la aeronave

Examinando la imagen se observa:

    Avión de color gris con una estrella naranja en la cola → Jetstar Japan

    Matrícula visible en la cola: JA06JJ

    Pasarela de embarque con logo SMBC

    Vehículos de ground handling: BS-004, G1852

    Aeronave tipo Airbus A320neo

Conclusión: Aerolínea Jetstar Japan (código IATA: GK), avión con matrícula JA06JJ.
Paso 3: Búsqueda OSINT del vuelo

Con la matrícula y la fecha, buscamos en bases de datos de aviación:

    Intentamos FlightRadar24 y ADSB Exchange, pero el historial gratuito no llegaba hasta mayo 2026.

    Probamos Google Dorks como "JA06JJ" "May 5" 2026.

    Hallazgo definitivo: Usando Flightera.net con la URL:
    text

    https://www.flightera.net/es/planes/JA06JJ/2026-05-05%2000_00

    Se encontró el historial completo de JA06JJ para el 5 de mayo de 2026.

Vuelo encontrado: GK55 (Osaka-Kansai KIX → Taipei TPE).
Paso 4: Construcción de la flag

    Fecha: 20260505

    Vuelo IATA: GK55

Flag:
text

NHNC{20260505_GK55}

Resumen de técnicas utilizadas
Técnica	Herramienta
Extracción de metadatos	exiftool
Búsqueda de archivos incrustados	binwalk, foremost, strings
Identificación de aeronave	Observación visual + búsqueda de matrícula
OSINT (fuentes abiertas)	flightera.net
Google Dorks	Búsquedas con matrícula y fecha

¡Reto resuelto! 🏆
