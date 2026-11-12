#!/usr/bin/env python3
"""Datos inventados de Antojo Campus para el taller.

Semilla fija. La fecha de corte se cambia con FECHA_CORTE.
Escribe clientes.csv, pedidos.csv y reglas.csv en la carpeta del
estudiante y en laboratorio/data.

    python generador/generar_datos.py
"""

from __future__ import annotations

import json
import os
import random
import unicodedata
from datetime import date, timedelta
from pathlib import Path

SEMILLA = 2026
N_CLIENTES = 1200
N_PEDIDOS = 8500
DIAS = 28

RAIZ = Path(__file__).resolve().parent.parent
CARPETA_ESTUDIANTE = RAIZ / "carpeta-estudiante"
DATOS_LAB = RAIZ / "laboratorio" / "data"


class Vacio:
    """Valor que se escribe como cadena vacía entre comillas.

    Sirve para distinguir un campo vacío de un campo nulo.
    """


VACIO = Vacio()


def fecha_corte() -> date:
    valor = os.environ.get("FECHA_CORTE", "").strip()
    return date.fromisoformat(valor) if valor else date.today()


def csv_campo(valor) -> str:
    if valor is VACIO:
        return '""'
    if valor is None:
        return ""
    texto = str(valor)
    if any(c in texto for c in ',"\r\n') or texto != texto.strip():
        return '"' + texto.replace('"', '""') + '"'
    return texto


def escribir_csv(ruta: Path, columnas: list[str], filas: list[list]) -> None:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    lineas = [",".join(columnas)]
    lineas += [",".join(csv_campo(v) for v in fila) for fila in filas]
    ruta.write_text("\n".join(lineas) + "\n", encoding="utf-8")


NOMBRES = [
    "Ana", "Luis", "María", "Jorge", "Sofía", "Diego", "Valeria", "Emiliano",
    "Camila", "Mateo", "Renata", "Santiago", "Ximena", "Sebastián", "Paula",
    "Rodrigo", "Fernanda", "Iván", "Daniela", "Héctor", "Lucía", "Óscar",
    "Regina", "Alejandro", "Mariana", "Ricardo", "Jimena", "César", "Natalia",
    "Andrés", "Gabriela", "Miguel", "Carolina", "Raúl", "Adriana", "Felipe",
    "Mónica", "Javier", "Silvia", "Tomás",
]

APELLIDOS = [
    "Herrera", "Mendoza", "Vargas", "Cortés", "Rojas", "Navarro", "Salazar",
    "Domínguez", "Fuentes", "Aguilar", "Trejo", "Carrillo", "Ortiz", "Peña",
    "Ríos", "Solís", "Cabrera", "León", "Mejía", "Ponce", "Zavala", "Arroyo",
    "Bautista", "Cervantes", "Duarte", "Escobar", "Franco", "Galván", "Hidalgo",
    "Ibarra", "Juárez", "Lozano", "Mora", "Núñez", "Ochoa", "Palacios",
    "Quiroz", "Ramírez", "Sandoval", "Tapia",
]

CARRERAS = [
    "Administración", "Arquitectura", "Biología", "Contaduría", "Derecho",
    "Diseño gráfico", "Economía", "Ingeniería en Sistemas", "Medicina",
    "Psicología",
]

# Fallas de correo. Suma 108, así que 1092 de 1200 están bien: 91%.
FALLAS_CORREO = [
    ("doble_arroba", 24),
    ("sin_arroba", 30),
    ("sin_punto", 24),
    ("vacio", 18),
    ("espacios", 12),
]

NOTAS_SALUD = [
    "Soy celíaca. Sin pan, por favor.",
    "Soy celíaco, sin harina.",
    "Alergia al cacahuate.",
    "Alergia a los mariscos. Sin camarón.",
    "Soy diabética, sin azúcar.",
    "Soy diabético. Sin azúcar en la bebida.",
    "Tengo intolerancia a la lactosa.",
    "Alergia al gluten. Sin tortilla de harina.",
    "Soy alérgica al huevo. Sin mayonesa.",
    "Soy alérgico a la nuez.",
    "No puedo comer camarón.",
    "Tengo enfermedad celíaca.",
    "Soy alérgica al gluten. Cambien el pan.",
    "Soy alérgico al cacahuate, revisen la salsa.",
    "Tengo diabetes. Sin postre.",
]

NOTAS_AMBIGUAS = [
    "Sin gluten, por favor.",
    "Sin azúcar, por favor.",
    "Sin lactosa.",
    "Sin mariscos, por favor.",
    "Sin harina, por favor.",
    "Sin leche.",
    "Sin trigo, por favor.",
    "Sin endulzante.",
    "Sin queso.",
    "Sin nueces, por si acaso.",
]

NOTAS_normales = [
    "Sin cebolla.", "Salsa aparte.", "Extra picante.", "Sin tomate.",
    "Tocar el timbre.", "Dejar en recepción.", "Sin servilletas.",
    "Con dos salsas.", "Bien cocido.", "Sin hielo.", "Sin pepinillos.",
    "Poco picante.", "Sin lechuga.", "Con cubiertos.", "Sin popote.",
    "Tortilla aparte.", "Sin crema.", "Con extra queso.", "Sin sal.",
    "Con limón aparte.", "Sin cilantro.", "Sin aguacate.", "Sin chile.",
    "Salsa verde aparte.", "Sin aderezo.", "Bien caliente.", "Sin papas.",
    "Dos tortillas extra.", "Sin tocino.", "Sin piña.", "Sin verduras.",
    "Sin refresco.", "Poco queso.", "Sin catsup.", "Sin jitomate.",
]


def hacer_clientes(corte: date) -> tuple[list[list], list[str]]:
    """1200 clientes. 108 correos mal escritos y 216 teléfonos vacíos."""
    azar = random.Random(SEMILLA + 1)

    fallas: list[str] = []
    for tipo, cantidad in FALLAS_CORREO:
        fallas += [tipo] * cantidad
    fallas += ["ok"] * (N_CLIENTES - len(fallas))
    azar.shuffle(fallas)

    # 150 nulos y 66 vacíos = 216. 984 de 1200 = 82%.
    telefonos: list = [None] * 150 + [VACIO] * 66
    telefonos += [
        f"+52 55 {azar.randint(1000, 9999)} {azar.randint(1000, 9999)}"
        for _ in range(700)
    ]
    telefonos += [
        f"55 {azar.randint(1000, 9999)} {azar.randint(1000, 9999)}"
        for _ in range(N_CLIENTES - len(telefonos))
    ]
    azar.shuffle(telefonos)

    filas: list[list] = []
    usados: set[str] = set()
    for i in range(N_CLIENTES):
        nombre = f"{azar.choice(NOMBRES)} {azar.choice(APELLIDOS)} {azar.choice(APELLIDOS)}"
        while nombre in usados:
            nombre = f"{azar.choice(NOMBRES)} {azar.choice(APELLIDOS)} {azar.choice(APELLIDOS)}"
        usados.add(nombre)

        normal = unicodedata.normalize("NFKD", nombre)
        normal = "".join(c for c in normal if not unicodedata.combining(c))
        local = normal.lower().replace(" ", ".") + f"{i + 1:03d}"

        tipo = fallas[i]
        if tipo == "doble_arroba":
            email = f"{local}@@correo.test"
        elif tipo == "sin_arroba":
            email = f"{local}correo.test"
        elif tipo == "sin_punto":
            email = f"{local}@correo"
        elif tipo == "vacio":
            email = VACIO
        elif tipo == "espacios":
            email = f"{local} @correo.test" if i % 2 else f"{local}@ correo.test"
        else:
            email = f"{local}@correo.test"

        registro = corte - timedelta(days=azar.randint(30, 1095))
        filas.append(
            [
                f"C{i + 1:04d}",
                nombre,
                email,
                telefonos[i],
                azar.choice(CARRERAS),
                registro.isoformat(),
            ]
        )
    return filas, [f[0] for f in filas]


def hacer_pedidos(corte: date) -> tuple[list[list], dict]:
    """8500 pedidos de 28 días.

    La versión 2.3 de la app de repartidores sale hace 14 días y trae
    entregas sin fecha. Eso baja R4 de 99% a 96%.
    """
    azar = random.Random(SEMILLA + 2)
    info: list[dict] = []
    contador = 0

    # total, entregados, fallas de fecha y de esas cuántas son de la 2.3
    periodos = [
        (14, 4258, 3492, 139, 124, 2130),  # últimos 14 días
        (14, 4242, 3478, 35, 0, 0),        # 14 días anteriores
    ]

    for numero, (dias, total, entregados, fallas, fallas_23, pedidos_23) in enumerate(periodos):
        # Un día por cada fila, repartido parejo.
        dias_lista = []
        for d in range(dias):
            dias_lista += [d] * (total // dias)
        dias_lista += list(range(total % dias))
        azar.shuffle(dias_lista)

        cancelados = round(total * 0.08)
        en_camino = round(total * 0.05)
        pendientes = total - entregados - cancelados - en_camino
        estados = (
            ["entregado"] * entregados
            + ["cancelado"] * cancelados
            + ["en_camino"] * en_camino
            + ["pendiente"] * pendientes
        )
        azar.shuffle(estados)

        versiones = ["2.3"] * pedidos_23 + ["2.2"] * (total - pedidos_23)
        azar.shuffle(versiones)

        indices = list(range(total))
        azar.shuffle(indices)

        candidatos_23 = [
            i for i in indices
            if estados[i] == "entregado" and versiones[i] == "2.3"
        ]
        candidatos_22 = [
            i for i in indices
            if estados[i] == "entregado" and versiones[i] == "2.2"
        ]
        sin_fecha = set(azar.sample(candidatos_23, fallas_23))
        sin_fecha |= set(azar.sample(candidatos_22, fallas - fallas_23))

        for i in indices:
            contador += 1
            fecha = corte - timedelta(days=dias_lista[i] + numero * 14)
            info.append(
                {
                    "id": f"P{contador:05d}",
                    "fecha": fecha,
                    "estado": estados[i],
                    "entrega": fecha.isoformat()
                    if estados[i] == "entregado" and i not in sin_fecha
                    else None,
                    "version": versiones[i],
                }
            )

    n = len(info)

    # Notas llenas en ~41% de los pedidos: 3485.
    # Las 105 de salud van repartidas por todo el archivo (una por tramo de 81 filas,
    # en un lugar al azar): una muestra corta casi nunca las ve.
    paso = n // 105
    salud_idx = [k * paso + azar.randrange(paso) for k in range(105)]
    resto = azar.sample(sorted(set(range(n)) - set(salud_idx)), 3485 - 105)
    notas: dict[int, str] = {idx: azar.choice(NOTAS_SALUD) for idx in salud_idx}
    for k, idx in enumerate(resto):
        notas[idx] = azar.choice(NOTAS_AMBIGUAS if k < 15 else NOTAS_normales)

    # Montos: 51 no mayores que cero -> 8449/8500 = 99.4% cumplen R3.
    indices_malos = set(azar.sample(range(n), 51))

    filas = []
    for i, p in enumerate(info):
        if i in indices_malos:
            monto = 0.0 if len(filas) % 9 else -round(azar.uniform(20, 90), 2)
        else:
            monto = round(azar.uniform(45, 350), 2)
        filas.append(
            [
                p["id"],
                f"C{azar.randint(1, N_CLIENTES):04d}",
                p["fecha"].isoformat(),
                p["entrega"],
                p["estado"],
                f"{monto:.2f}",
                notas.get(i),
                p["version"],
            ]
        )

    ids_salud = sorted(
        info[idx]["id"] for idx, nota in notas.items() if nota in NOTAS_SALUD
    )
    ids_ambiguas = sorted(
        info[idx]["id"] for idx, nota in notas.items() if nota in NOTAS_AMBIGUAS
    )
    meta = {
        "fecha_corte": corte.isoformat(),
        "notas_salud": ids_salud,
        "notas_ambiguas": ids_ambiguas,
    }
    return filas, meta


REGLAS = [
    ["R1", "El correo está bien escrito", "clientes", 95, "Atención a clientes"],
    ["R2", "El teléfono no está vacío", "clientes", 95, "Atención a clientes"],
    ["R3", "El monto es mayor que cero", "pedidos", 99, "Operaciones"],
    ["R4", 'Si dice "entregado", tiene fecha de entrega', "pedidos", 95, "Operaciones"],
]

LINAJE = {
    "nodos": [
        {
            "id": "app_repartidores",
            "nombre": "App de repartidores",
            "dueno": "Tecnología",
            "frase": "De aquí sale la versión de app con la que se reparte cada pedido.",
        },
        {
            "id": "app_clientes",
            "nombre": "App de clientes",
            "dueno": "Tecnología",
            "frase": "Aquí la persona escribe su correo y su teléfono.",
        },
        {
            "id": "clientes",
            "nombre": "clientes",
            "dueno": "Atención a clientes",
            "frase": "Tabla con una fila por persona.",
        },
        {
            "id": "pedidos",
            "nombre": "pedidos",
            "dueno": "Operaciones",
            "frase": "Tabla con un fila por pedido.",
        },
        {
            "id": "regla_R4",
            "nombre": "R4 · entrega con fecha",
            "dueno": "Operaciones",
            "frase": "Cuenta cuántos entregados tienen fecha.",
        },
        {
            "id": "regla_R1",
            "nombre": "R1 · correo",
            "dueno": "Atención a clientes",
            "frase": "Cuenta cuántos correos están bien escritos.",
        },
        {
            "id": "regla_R2",
            "nombre": "R2 · teléfono",
            "dueno": "Atención a clientes",
            "frase": "Cuenta cuántos teléfonos tienen algo.",
        },
        {
            "id": "tablero",
            "nombre": "Tablero de Mariana",
            "dueno": "Dirección",
            "frase": "Muestra el porcentaje de cada regla.",
        },
    ],
    "enlaces": [
        ["app_repartidores", "pedidos"],
        ["app_clientes", "clientes"],
        ["clientes", "regla_R1"],
        ["clientes", "regla_R2"],
        ["pedidos", "regla_R4"],
        ["regla_R1", "tablero"],
        ["regla_R2", "tablero"],
        ["regla_R4", "tablero"],
    ],
}


VERDAD_COLUMNAS = [
    ("clientes.id", "Interna", "Es un identificador interno; no dice nada de la persona."),
    ("clientes.nombre", "Personal", "Identifica a una persona."),
    ("clientes.email", "Personal", "Permite contactar a una persona."),
    ("clientes.telefono", "Personal", "Permite contactar a una persona."),
    ("clientes.carrera", "Personal", "Dice qué estudia una persona concreta."),
    ("clientes.fecha_registro", "Interna", "Es un dato de operación de la app."),
    ("pedidos.id", "Interna", "Es un identificador interno."),
    ("pedidos.cliente_id", "Interna", "Es un código interno; por sí solo no identifica a nadie."),
    ("pedidos.fecha_pedido", "Interna", "Es un dato de operación."),
    ("pedidos.fecha_entrega", "Interna", "Es un dato de operación."),
    ("pedidos.estado", "Interna", "Es un dato de operación."),
    ("pedidos.monto", "Interna", "Es un dato de operación; no es de una persona."),
    ("pedidos.notas", "Sensible", "Texto libre: algunas notas revelan la salud de una persona."),
    ("pedidos.version_app", "Interna", "Es un dato técnico de la app de repartidores."),
]


def main() -> None:
    corte = fecha_corte()
    clientes, _ = hacer_clientes(corte)
    pedidos, meta = hacer_pedidos(corte)

    for destino in (CARPETA_ESTUDIANTE, DATOS_LAB):
        destino.mkdir(parents=True, exist_ok=True)
        escribir_csv(
            destino / "clientes.csv",
            ["id", "nombre", "email", "telefono", "carrera", "fecha_registro"],
            clientes,
        )
        escribir_csv(
            destino / "pedidos.csv",
            ["id", "cliente_id", "fecha_pedido", "fecha_entrega", "estado",
             "monto", "notas", "version_app"],
            pedidos,
        )
        escribir_csv(
            destino / "reglas.csv",
            ["id", "descripcion", "tabla", "meta", "dueno"],
            REGLAS,
        )

    DATOS_LAB.mkdir(parents=True, exist_ok=True)
    (DATOS_LAB / "linaje.json").write_text(
        json.dumps(LINAJE, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (DATOS_LAB / "meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    escribir_csv(
        DATOS_LAB / "verdad_columnas.csv",
        ["columna", "categoria", "motivo"],
        [list(f) for f in VERDAD_COLUMNAS],
    )
    # El laboratorio lee todo de un solo archivo para abrir sin servidor.
    archivos = ["clientes.csv", "pedidos.csv", "reglas.csv", "verdad_columnas.csv",
                "linaje.json", "meta.json"]
    datos = {a: (DATOS_LAB / a).read_text(encoding="utf-8") for a in archivos}
    datos["linaje.json"] = json.loads(datos["linaje.json"])
    datos["meta.json"] = json.loads(datos["meta.json"])
    (DATOS_LAB / "datos.js").write_text(
        "window.DATOS_TALLER = " + json.dumps(datos, ensure_ascii=False) + ";\n",
        encoding="utf-8",
    )

    print(f"Fecha de corte: {corte.isoformat()}")
    print(f"clientes.csv  {len(clientes)} filas")
    print(f"pedidos.csv   {len(pedidos)} filas")


if __name__ == "__main__":
    main()
