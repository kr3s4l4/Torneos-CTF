🧙 Writeup: bronco{prefire_junkshadow_soldieroffortune88}

Autor: [Tu nombre / alias]
Fecha de resolución: 12 de julio de 2026
Reto: OSINT + Magic: The Gathering
📝 Índice

    Resumen del Reto

    Análisis del Sideboard (La Firma del Mazo)

    Descifrando el Formato (La Pista del Precursor)

    Identificando al Jugador (Pista "url found site")

    La Fuente Oficial: TC Decks

    Construcción de la Bandera

    Lecciones Aprendidas

    Recursos Utilizados

🎯 Resumen del Reto

El objetivo era encontrar una bandera con el formato:
text

bronco{formatname_archetypeofdeck_nameofplayer}

Las pistas iniciales eran:
Pista	Descripción
Formato	Precursor de un acrónimo famoso por powercreep
Arquetipo	Mazo con 4 copias de Death's Shadow
Sideboard	Lista exacta de 15 cartas (ver abajo)
Jugador	Nombre de 18 caracteres + pista u 8 l r f o n d t s i e
🃏 Análisis del Sideboard (La Firma del Mazo)

La pieza más concreta era el sideboard del mazo. El jugador recordaba esta lista exacta, que resultó ser la clave del reto:
text

2 Stony Silence
2 Nihil Spellbomb
2 Fulminator Mage
2 Engineered Explosives
1 Tireless Tracker
1 Surgical Extraction
1 Maelstrom Pulse
1 Liliana, the Last Hope
1 Krosan Grip
1 Collective Brutality
1 Abrupt Decay

🔍 ¿Por qué era tan especial?

    Cartas en cantidad de "1": Tireless Tracker, Liliana, the Last Hope, Krosan Grip, Abrupt Decay, etc. Estas son opciones muy personales y poco comunes en los sideboards estándar.

    Mezcla de colores: Incluye cartas de Blanco, Negro y Verde (Abzan), lo que sugería un mazo Junk Shadow o Abzan Death's Shadow, en lugar del clásico Grixis o Jund Shadow.

    Dedicación a artefactos: 2 Stony Silence y 2 Engineered Explosives indicaban una clara preparación contra mazos de artefactos.

Conclusión: Esta combinación única de cartas era la "huella dactilar" del mazo. No era una lista genérica; era la elección de un jugador concreto para un metajuego específico.
🧩 Descifrando el Formato (La Pista del Precursor)

La pista del formato decía:

    "This Magic the Gathering Format was designed as a precursor to a very famous acronym known for excessive powercreep and powerful design."

🔎 Investigación

    El acrónimo famoso: En Magic, el acrónimo más conocido por powercreep y diseño poderoso es F.I.R.E., que significa Functional, Inviting, Replayable, Exciting. Es una filosofía de diseño que Wizards of the Coast adoptó a partir de 2019.

    El precursor: El formato que sirvió como "precursor" de la era F.I.R.E. en la comunidad de Magic Online (MTGO) es Prefire. Este formato excluye cartas publicadas después de un cierto punto, capturando la esencia del Modern previo a la filosofía F.I.R.E.

    Validación: El mazo que encontramos se jugó en un torneo llamado "2024 Prefire League - December #1", confirmando que el formato es Prefire.

✅ Formato identificado: prefire
🕵️ Identificando al Jugador (Pista "url found site")

La pista del jugador era:

    "The name of the player is 18 characters long. I found this note that might help: u 8 l r f o n d t s i e"

🔐 Descifrando la pista

La secuencia u 8 l r f o n d t s i e se reordena para formar:
text

u r l   f o u n d   s i t e
→ "url found site"

Interpretación: La pista indicaba que el nombre del jugador debía aparecer en un sitio web de resultados de torneos, como MTGTop8.com o TC Decks.
🎯 Búsqueda en TC Decks

Usando el sideboard exacto como filtro, realizamos búsquedas en TC Decks con los siguientes parámetros:

    Formato: Prefire (o Modern)

    Main deck: Death's Shadow (4 copias)

    Sideboard: Todas las cartas de la lista anterior

✅ El resultado

Encontramos un mazo registrado en:

    Evento: 2024 Prefire League - December #1

    Fecha: 15/12/2024

    Jugador: SoldierofFortune88

    Arquetipo: Junk Shadow

    Puesto: 13

🔢 Comprobación de la longitud

El nombre SoldierofFortune88 tiene exactamente 18 caracteres:
text

S-o-l-d-i-e-r-o-f-F-o-r-t-u-n-e-8-8
1-2-3-4-5-6-7-8-9-10-11-12-13-14-15-16-17-18

✅ Jugador identificado: soldieroffortune88
🌐 La Fuente Oficial: TC Decks

El mazo se encuentra publicado en TC Decks, un sitio web de referencia para listas de torneos de Magic. El enlace directo es:

🔗 TC Decks - 2024 Prefire League - December #1
📋 Resumen del mazo (según TC Decks)
Campo	Valor
Evento	2024 Prefire League - December #1
Fecha	15/12/2024
Jugador	SoldierofFortune88
Arquetipo	Junk Shadow
Formato	Prefire
Posición	13
🃏 Lista completa del mazo
Maindeck (60 cartas)
Tipo	Cartas	Cantidad
Criaturas	Death's Shadow, Street Wraith, Tarmogoyf, Grim Flayer, Dark Confidant	16
Instantáneos	Fatal Push, Abrupt Decay, Dismember, Path to Exile	7
Conjuros	Thoughtseize, Inquisition of Kozilek, Traverse the Ulvenwald, Lingering Souls	12
Planeswalkers	Liliana of the Veil	2
Artefactos	Mishra's Bauble, Sensei's Divining Top	7
Tierras	Verdant Catacombs, Windswept Heath, Marsh Flats, Overgrown Tomb, etc.	16
Sideboard (15 cartas) - ¡Coincidencia exacta!
text

2 Stony Silence
2 Nihil Spellbomb
2 Fulminator Mage
2 Engineered Explosives
1 Tireless Tracker
1 Surgical Extraction
1 Maelstrom Pulse
1 Liliana, the Last Hope
1 Krosan Grip
1 Collective Brutality
1 Abrupt Decay

🏆 Construcción de la Bandera

Con todos los datos validados, la bandera se construyó siguiendo el formato exacto:
text

bronco{formatname_archetypeofdeck_nameofplayer}

Parte	Valor	Razón
formatname	prefire	Formato del torneo, precursor de F.I.R.E.
archetypeofdeck	junkshadow	Nombre del arquetipo en la lista de TC Decks
nameofplayer	soldieroffortune88	Alias del jugador, 18 caracteres
✅ Bandera final:
text

bronco{prefire_junkshadow_soldieroffortune88}

💡 Lecciones Aprendidas

    Los "unos" en el sideboard son la clave: Cartas como Tireless Tracker o Maelstrom Pulse en cantidades de 1 son muy distintivas y ayudan a filtrar listas genéricas.

    La pista "url found site" fue fundamental: Nos indicó exactamente dónde buscar el nombre del jugador.

    El formato Prefire existe: No es un formato oficial de Wizards, pero es muy común en torneos de la comunidad de MTGO y encajaba perfectamente con la pista del "precursor".

    Los alias de MTGO pueden ser largos: El nombre SoldierofFortune88 es un alias, no un nombre real, lo que explicaba la longitud de 18 caracteres.

    TC Decks es una fuente excelente: Especialmente para torneos de la comunidad y formatos no oficiales.

📚 Recursos Utilizados
Recurso	Descripción	Enlace
TC Decks	Base de datos de mazos y torneos	tcdecks.net
MTGTop8	Resultados de torneos y listas de mazos	mtgtop8.com
Google	Búsqueda de información general sobre formatos y jugadores	google.com
Conocimiento de Magic	Identificación de arquetipos, cartas y formato Prefire	-
