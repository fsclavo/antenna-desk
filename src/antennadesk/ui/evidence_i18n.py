# SPDX-FileCopyrightText: 2026 Fernando Sclavo
# SPDX-License-Identifier: GPL-3.0-or-later
"""Spanish translations for the evidence registry text.

The evidence registry stays in the domain and keeps the original bibliographic
references.  Reports request ``evidence.<template>.<field>`` from the report
labeler; a missing field falls back to the English registry text.
"""

from __future__ import annotations

EVIDENCE_SPANISH: dict[str, dict[str, str]] = {
    "wire_dipole": {
        "source": (
            "NEC-2 User's Guide, ejemplos 1 y 3; ARRL Antenna Book, 24.ª ed., cap. 2, pág. 2.12"
        ),
        "tolerance": "0,05 Ω de impedancia; 0,15 dB de ganancia",
        "limitation": (
            "Solo espacio libre y los casos de suelo publicados. La flecha "
            "opcional del hilo usa una aproximación parabólica de nueve "
            "segmentos y no forma parte de la comparación con la referencia "
            "publicada."
        ),
    },
    "folded_dipole": {
        "source": (
            "ARRL Antenna Book, 24.ª ed., cap. 2, págs. 2.12-2.13: un dipolo "
            "plegado de conductores iguales tiene la misma ganancia y cuatro "
            "veces la resistencia"
        ),
        "tolerance": "0,2 dB de ganancia; 0,5 en la relación de resistencia",
        "limitation": "No hay referencia independiente de impedancia absoluta.",
    },
    "loop": {
        "source": (
            "ARRL Antenna Book, 24.ª ed., cap. 5, pág. 5.4, para el caso "
            "cuadrado; la corrección poligonal es una regla inicial calibrada"
        ),
        "tolerance": "15 Ω solo para el preset cuadrado",
        "limitation": (
            "El delta y los polígonos de cantidad de lados arbitraria son estructurales."
        ),
    },
    "quad_loop": {
        "source": (
            "ARRL Antenna Book, 24.ª ed., cap. 5, pág. 5.4: aproximadamente 120 Ω en resonancia"
        ),
        "tolerance": "15 Ω",
        "limitation": "Solo la geometría cuadrada publicada.",
    },
    "delta_loop": {
        "source": (
            "ON4UN, Low-Band DXing, cap. 10: la circunferencia resonante del "
            "lazo delta es aproximadamente 1,05-1,06 longitudes de onda"
        ),
        "tolerance": "1% en la circunferencia resonante",
        "limitation": (
            "Solo la circunferencia; la impedancia de alimentación y la "
            "polarización dependen de la posición de alimentación y la altura."
        ),
    },
    "magnetic_loop": {
        "source": (
            "Geometría de lazo pequeño con un capacitor de sintonía serie "
            "ideal; no hay referencia numérica independiente para el diseño "
            "generado"
        ),
        "tolerance": "No aplicable (estructural)",
        "limitation": (
            "El capacitor es un elemento RLC serie ideal con ESR opcional; el "
            "lazo de acoplamiento, la tensión del capacitor y los mecanismos "
            "detallados de pérdida no están modelados. Sintonizá la "
            "capacitancia con el solver o una medición."
        ),
    },
    "vertical": {
        "source": (
            "Reglas prácticas de longitud de ARRL: 234/f para una vertical de "
            "cuarto de onda y 585/f para una vertical de 5/8 de onda"
        ),
        "tolerance": "0,5% en la longitud del radiador",
        "limitation": (
            "La ganancia y la impedancia de alimentación dependen de la "
            "cantidad de radiales, el suelo y cualquier sombrero capacitivo; "
            "esos factores no están validados independientemente."
        ),
    },
    "loaded_vertical": {
        "source": (
            "K7MEM, «Short Loaded Vertical», citando ARRL Antenna Book, 17.ª "
            "ed., págs. 16-5 a 16-11: un látigo de 102 in a 14,1 MHz necesita "
            "una bobina de carga de base de 4,511 µH"
        ),
        "tolerance": (
            "5% en la longitud del látigo de 102 in y en la inductancia de 4,511 µH de la bobina"
        ),
        "limitation": (
            "Solo el ejemplo móvil publicado de 14,1 MHz tiene referencia. La "
            "bobina es una carga serie ideal; la Q de la bobina, el suelo y la "
            "instalación móvil no están modelados. Las demás verticales "
            "cargadas siguen siendo experimentales."
        ),
    },
    "yagi": {
        "source": "Preset NBS TN-688 de 5 elementos, 9,2 dBd (11,35 dBi)",
        "tolerance": "0,5 dB",
        "limitation": (
            "Solo el preset publicado; la geometría editada de los elementos "
            "es experimental. El elemento alimentado plegado opcional y la "
            "adaptación beta/hairpin cambian la impedancia de alimentación y no "
            "tienen referencia independiente de impedancia. Las puntas cónicas "
            "son solo geométricas; la corrección por montaje en el boom no está "
            "modelada. Las adaptaciones gamma no están modeladas por NEC-2 aquí."
        ),
    },
    "moxon": {
        "source": ("L. B. Cebik, W4RNL, «The Moxon Rectangle: A Review», tabla 1 y texto"),
        "tolerance": (
            "1,5 Ω real; 5 Ω de reactancia; 0,3 dB de ganancia; mejor que 30 dB "
            "de relación frente/espalda"
        ),
        "limitation": (
            "Con referencia solo a 14,17 MHz; las dimensiones escaladas a otra "
            "frecuencia o editadas son un punto de partida heurístico."
        ),
    },
    "ocfd": {
        "source": ("R. Sanders, VK2WB, «Analysis of the Off Centre Fed (OCF) dipole», tabla 1"),
        "tolerance": ("Rango publicado de 200-350 Ω, no una tolerancia numérica estricta"),
        "limitation": ("La fuente no especifica completamente su modelo de suelo EZNEC."),
    },
    "inverted_v": {
        "source": (
            "ARRL, «Wire Antennas for the Beginner»: la longitud total de la V "
            "invertida de 120 grados es 465,6/f MHz en pies"
        ),
        "tolerance": "1% en la longitud total para el caso de 120 grados",
        "limitation": (
            "El caso de 90 grados y la desintonía por suelo usan reglas "
            "iniciales empíricas separadas; la ganancia y la impedancia de "
            "alimentación no están validadas independientemente."
        ),
    },
    "inverted_l": {
        "source": (
            "Geometría inicial de hilo alimentado en el extremo y doblado; no "
            "hay referencia numérica independiente"
        ),
        "tolerance": "No aplicable (estructural)",
        "limitation": (
            "La altura vertical, el tramo horizontal, el suelo y la adaptación "
            "determinan el resultado; sintonizalos con el solver o una medición."
        ),
    },
    "fan_dipole": {
        "source": ("Regla inicial de media onda por banda; el acoplamiento mutuo no está modelado"),
        "tolerance": "No aplicable (estructural)",
        "limitation": (
            "Un abanico acoplado no es una combinación en paralelo de dipolos independientes."
        ),
    },
    "trap_dipole": {
        "source": (
            "RSARS, «W3DZZ Multi-band Antenna 80-40-20-15-10m»: secciones "
            "interior de 33 ft y exterior de 22 ft, trampas de 7,1 MHz, "
            "5,024 µH y 100 pF"
        ),
        "tolerance": ("1% en las secciones de 33/22 ft; 2% en la resonancia de la trampa"),
        "limitation": (
            "La línea de alimentación y el sintonizador no están modelados; la "
            "trampa es un LC paralelo ideal, y las dimensiones iniciales por "
            "defecto son un dipolo con trampas de tamaño completo para 80/20 m, "
            "no el W3DZZ."
        ),
    },
    "t2fd": {
        "source": "Regla inicial de banda ancha wide-long de Cebik",
        "tolerance": "No es una tolerancia numérica estricta",
        "limitation": "La resistencia de terminación y el transformador son ideales.",
    },
    "endfed": {
        "source": (
            "Kit ARRL de antena de media onda alimentada en el extremo: 66 ft "
            "en 40 m, 33 ft en 20 m, 16 ft en 10 m, transformador 49:1, "
            "aproximadamente 2500 Ω; PA9X: contrapeso de 0,05λ de la longitud "
            "de onda más larga"
        ),
        "tolerance": (
            "5% en la longitud del hilo de media onda; contrapeso de 0,05λ; relación 49:1"
        ),
        "limitation": (
            "El transformador 49:1 es una relación ideal; el contrapeso es un "
            "hilo recto; la altura, el suelo y el choke de modo común no están "
            "modelados."
        ),
    },
    "sloper": {
        "source": (
            "Manual del operador de la Chameleon Antenna CHA LEFS Feather: "
            "radiador EFHW de 66,5 ft, transformador 49:1, extremo lejano a "
            "unas 25 ft, transformador de alimentación a unas 3 ft; patrones "
            "sloper probados en 40/20/15/10 m"
        ),
        "tolerance": "5% en la longitud del radiador y las alturas de instalación",
        "limitation": (
            "El transformador, la línea de alimentación, el choke y el "
            "acoplamiento con el sitio no están modelados; el sloper por "
            "defecto del editor va de 10 m a 0,5 m, así que la geometría "
            "publicada es un punto de partida, no el valor por defecto."
        ),
    },
    "random_wire": {
        "source": "Geometría de hilo aleatorio con plan de bandas asistido por sintonizador",
        "tolerance": "No aplicable (estructural)",
        "limitation": "No se declara precisión.",
    },
    "g5rv": {
        "source": ("Dimensiones G5RV publicadas; modelo de línea de transmisión sin pérdidas"),
        "tolerance": "No es una tolerancia numérica estricta",
        "limitation": (
            "La pérdida de la línea no está modelada; la adaptación depende de la instalación."
        ),
    },
    "zs6bkw": {
        "source": (
            "Valores de ROE de Cebik/W4RNL: 1,15, 1,47 y 1,56 en 40/20/10 m; "
            "variante comercial de 27,5 m"
        ),
        "tolerance": "0,3 de ROE",
        "limitation": "Modelo de línea sin pérdidas.",
    },
    "zepp": {
        "source": (
            "ARRL Antenna Book, 24.ª ed., cap. 20: un Zepp verdadero es un "
            "radiador de media onda alimentado en el extremo, adaptado por una "
            "línea de hilos abiertos de cuarto de onda; W8JI, «End-fed vertical "
            "J-pole and horizontal Zepp»: un stub de 1/4λ que alimenta un "
            "elemento de 1/2λ con un balun de corriente 1:1 en el sintonizador"
        ),
        "tolerance": (
            "5% en las longitudes iniciales de media onda y cuarto de onda; la "
            "separación y el radio de los conductores determinan la impedancia "
            "del stub"
        ),
        "limitation": (
            "Solo dimensiones iniciales. El choke de modo común 1:1, la línea "
            "de alimentación coaxil, la corriente de modo común y la instalación "
            "no están modelados; el balance del stub se degrada en armónicos "
            "pares y la adaptación requiere sintonía."
        ),
    },
    "j_pole": {
        "source": (
            "M0UKD, «Slim Jim and J Pole calculator»: un J Pole mide 0,75λ de "
            "alto, con un radiador de 0,5λ y un stub de adaptación de 0,25λ; "
            "ARRL QST, feb. 2003, dimensiones convencionales de J-pole para 2 m"
        ),
        "tolerance": (
            "1% en las secciones de media onda y cuarto de onda; 10% en la "
            "altura total respecto de la construcción ARRL para 2 m"
        ),
        "limitation": (
            "Solo dimensiones iniciales; el desplazamiento de alimentación de "
            "50 Ω, el suelo, el mástil y el acoplamiento con la línea de "
            "alimentación no están validados independientemente."
        ),
    },
    "slim_jim": {
        "source": (
            "F. Judd, G2BCX, «Slim Jim - 2 metre aerial», Practical Wireless, "
            "1978: unos 60 in en total a 145 MHz; calculadora M0UKD: radiador "
            "de 0,5λ sobre un stub de 0,25λ con una pequeña separación"
        ),
        "tolerance": (
            "1% en las secciones de media onda y cuarto de onda; 5% en la longitud total a 2 m"
        ),
        "limitation": (
            "Solo dimensiones iniciales; el punto de alimentación, la separación "
            "del pliegue y el efecto de la línea de alimentación no están "
            "validados independientemente."
        ),
    },
    "ringo": {
        "source": "Geometría inicial del radiador y anillo Ringo",
        "tolerance": "No aplicable (estructural)",
        "limitation": "No hay referencia numérica independiente.",
    },
    "half_square": {
        "source": (
            "L. B. Cebik, W4RNL, «SCVs: A Family Album», tabla 1 (7,15 MHz): "
            "62,4 ft horizontal por 39 ft vertical, aproximadamente 4,6 dBi y "
            "65 ohm"
        ),
        "tolerance": ("5% en las dimensiones horizontal y vertical escaladas por frecuencia"),
        "limitation": (
            "Solo geometría inicial publicada de espacio libre y máxima "
            "ganancia. El patrón, la impedancia de alimentación, el suelo, la "
            "altura de los soportes, la línea de alimentación y la red de "
            "adaptación no están validados independientemente."
        ),
    },
    "bobtail_curtain": {
        "source": (
            "L. B. Cebik, W4RNL, «SCVs: A Family Album», tabla 1 (7,15 MHz): "
            "125 ft horizontal por 38 ft vertical, aproximadamente 6,3 dBi y "
            "40 ohm en la unión del hilo central con el horizontal superior"
        ),
        "tolerance": ("5% en las dimensiones horizontal y vertical escaladas por frecuencia"),
        "limitation": (
            "Solo geometría inicial publicada de espacio libre y máxima "
            "ganancia. El patrón, la impedancia de alimentación según la altura "
            "de alimentación, el suelo, la altura de los soportes y la línea de "
            "alimentación no están validados independientemente."
        ),
    },
    "biquad": {
        "source": (
            "Martybugs, «Biquad Antenna Construction» (según Trevor Marshall), "
            "2,44 GHz: dos lazos cuadrados con lados de cuarto de onda (unos "
            "31 mm), separación de reflector de 15 mm y reflector sólido "
            "cuadrado de 123 mm; 11-12 dBi medidos"
        ),
        "tolerance": "2% en el lado del lazo; 10% en la separación del reflector",
        "limitation": (
            "Solo el lado del lazo y la separación iniciales tienen referencia. "
            "El modelo usa un reflector de rectángulo de hilos y rieles "
            "compartidos, no el reflector sólido publicado, por lo que no se "
            "reproducen la ganancia, la impedancia de alimentación, el ancho de "
            "banda ni los efectos del suelo. Sintonizá o medí la antena "
            "instalada."
        ),
    },
    "double_biquad": {
        "source": (
            "Martybugs, «Double Biquad Antenna», 2,4 GHz: dos biquads lado a "
            "lado sobre un reflector sólido de 110 x 220 mm, aproximadamente "
            "13-14 dBi; la plantilla es una pila vertical de cuatro lazos con "
            "reflector de hilos"
        ),
        "tolerance": "No aplicable (discrepancia estructural)",
        "limitation": (
            "El doble biquad publicado es un par lado a lado sobre un reflector "
            "sólido, mientras que la plantilla apila cuatro lazos verticalmente "
            "alrededor de rieles compartidos con un reflector de hilos. La "
            "topología diferente cambia la distribución de corriente y la "
            "impedancia de alimentación, así que la ganancia y las dimensiones "
            "publicadas no son una referencia directa. Se mantiene experimental."
        ),
    },
    "beverage": {
        "source": (
            "W. Silver, N0AX, y F. Donovan, W3LPL, «The Beverage Antenna, 100 "
            "Years Later», QST, noviembre de 2021, págs. 55-57: longitud "
            "inicial de una longitud de onda, terminación de 500 ohm y altura "
            "típica de 6-10 ft"
        ),
        "tolerance": (
            "1% en la longitud inicial de una longitud de onda; terminación nominal de 500 ohm"
        ),
        "limitation": (
            "Solo la longitud inicial, la terminación y la regla de altura "
            "tienen referencia. La terminación es un hilo vertical corto con "
            "una resistencia serie, no un sistema de tierra completo. La "
            "ganancia, el patrón, la eficiencia de terminación, la "
            "conductividad del suelo y la línea de alimentación no están "
            "validadas independientemente."
        ),
    },
    "loaded_dipole": {
        "source": (
            "R. Hiller, W5RH, «Designing a Coil-Loaded (short) Dipole», BVARC, "
            "3,91 MHz: 62 ft en total, bobinas a aproximadamente 50% hacia cada "
            "lado, 38,6 uH cada una; resistencia de alimentación EZNEC de "
            "8/21/25 ohm a 25/35/50 ft"
        ),
        "tolerance": "No aplicable (modelo de suelo no especificado)",
        "limitation": (
            "El ejemplo publicado es un dipolo portátil específico de 3,91 MHz "
            "y 62 ft; su modelo de suelo EZNEC no se indica, así que la "
            "resistencia de alimentación no se pudo reproducir de forma "
            "confiable. Los valores por defecto genéricos de la plantilla usan "
            "una posición de bobina diferente. La Q de la bobina, la pérdida de "
            "núcleo, la autocapacitancia, la resistencia de contacto de los "
            "enlaces y la instalación portátil no están modelados. Se mantiene "
            "experimental."
        ),
    },
    "phased_vertical": {
        "source": (
            "Radiadores verticales separados un cuarto de onda con progresión "
            "ideal lineal de fase y amplitud; no hay referencia numérica "
            "independiente para el arreglo generado"
        ),
        "tolerance": "No aplicable (estructural)",
        "limitation": (
            "El solver de hilos incluye el acoplamiento mutuo, pero la red "
            "combinadora, la adaptación por elemento, la pérdida de la línea de "
            "alimentación, la eficiencia de la pantalla de radiales y la "
            "instalación no están modeladas. La impedancia y la ROE informadas "
            "se refieren solo a la alimentación principal. Verificá el patrón y "
            "la adaptación con el solver o una medición."
        ),
    },
    "quad_beam": {
        "source": (
            "Lazos cuadrados de lado cuarto de onda con reflector escalado y "
            "director opcional, separación de un quinto de onda y alimentación "
            "en el centro de un lado; no hay referencia numérica independiente "
            "para el haz generado"
        ),
        "tolerance": "No aplicable (estructural)",
        "limitation": (
            "Los lazos cuadrados son polígonos ideales de hilos delgados. Los "
            "separadores, los efectos del boom y el mástil, el recorrido de la "
            "línea de alimentación y la red de adaptación no están modelados. "
            "El lado de cuarto de onda y la separación de un quinto de onda son "
            "heurísticas iniciales; la ganancia, la relación frente/espalda y "
            "la impedancia de alimentación no están validadas independientemente."
        ),
    },
    "discone": {
        "source": (
            "Cono de hilos radiales inclinados un cuarto de onda con disco "
            "superior de 0,7x y una pequeña separación de alimentación; no hay "
            "referencia numérica independiente para el discono generado"
        ),
        "tolerance": "No aplicable (estructural)",
        "limitation": (
            "El cono y el disco son aproximaciones de hilos radiales, no "
            "superficies sólidas. El coaxil, el mástil y la transición de "
            "alimentación no están modelados. La impedancia, el ancho de banda "
            "y el patrón de radiación no están validados independientemente; la "
            "forma es un punto de partida para la simulación."
        ),
    },
    "trap_yagi": {
        "source": (
            "Yagi de dos bandas con un par de trampas LC paralelas ideales por "
            "elemento; no hay referencia numérica independiente para el arreglo "
            "con trampas generado"
        ),
        "tolerance": "No aplicable (estructural)",
        "limitation": (
            "Las trampas son cargas LC paralelas ideales sin pérdida de núcleo "
            "ni dieléctrica. El montaje en el boom, el hardware de las trampas, "
            "la línea de alimentación y la red de adaptación no están modelados. "
            "La ganancia, la relación frente/espalda y la impedancia en "
            "cualquiera de las bandas no están validadas independientemente."
        ),
    },
    "hexbeam": {
        "source": (
            "Steve Hunt, G3TXQ, «A Broadband Hexbeam», antenneX n.º 128, "
            "diciembre de 2007: referencia de 20 m a 14,184 MHz con semilongitud "
            "del excitador de 219 in, semilongitud del reflector de 207 in, "
            "separación de puntas de 24 in y radio de giro de 130 in"
        ),
        "tolerance": (
            "1% en las semilongitudes publicadas del excitador y reflector, la "
            "separación de puntas y el radio de giro"
        ),
        "limitation": (
            "El modelo reconstruye el camino de hilo doblado en W/U a partir de "
            "las longitudes publicadas; no reproduce el marco comercial exacto, "
            "la flecha de los separadores, el balun de alimentación ni el "
            "anidamiento multibanda. La ganancia, la relación frente/espalda y "
            "la impedancia no están validadas independientemente."
        ),
    },
    "doublet": {
        "source": (
            "VU3DXR, «94-Foot Multi Band Doublet Antenna»: 94 ft en total, "
            "41 ft de línea de escalera de 450 Ω, balun de corriente 1:1 y "
            "sintonizador"
        ),
        "tolerance": (
            "5% en las longitudes del radiador y la línea de alimentación; línea de 450 Ω"
        ),
        "limitation": (
            "El sintonizador y el balun no están modelados; la longitud de la "
            "línea de alimentación, su impedancia y la instalación dominan la "
            "adaptación. El valor por defecto del editor es un dipolo de media "
            "onda, así que el diseño de 94 ft es un punto de partida."
        ),
    },
    "custom": {
        "source": "Geometría de hilos definida por el usuario",
        "tolerance": "No aplicable",
        "limitation": "No se declara precisión; solo importación y diagnósticos.",
    },
}
