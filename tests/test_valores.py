"""Revisa los valores que muestran las láminas y el laboratorio."""

from __future__ import annotations

import csv
import json
import sqlite3
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ESTUDIANTE = RAIZ / "carpeta-estudiante"
DATOS = RAIZ / "laboratorio" / "data"


def leer(nombre: str) -> list[dict[str, str]]:
    with (ESTUDIANTE / nombre).open(encoding="utf-8", newline="") as archivo:
        return list(csv.DictReader(archivo))


def meta() -> dict:
    return json.loads((DATOS / "meta.json").read_text(encoding="utf-8"))


def conectar() -> sqlite3.Connection:
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    for tabla, archivo in (
        ("clientes", "clientes.csv"),
        ("pedidos", "pedidos.csv"),
        ("reglas", "reglas.csv"),
    ):
        filas = leer(archivo)
        columnas = list(filas[0].keys())
        con.execute(
            f"CREATE TABLE {tabla} ({', '.join(f'{c} TEXT' for c in columnas)})"
        )
        con.executemany(
            f"INSERT INTO {tabla} VALUES ({', '.join('?' for _ in columnas)})",
            [[f.get(c) for c in columnas] for f in filas],
        )
    return con


def test_filas():
    assert len(leer("clientes.csv")) == 1200
    assert len(leer("pedidos.csv")) == 8500
    assert len(leer("reglas.csv")) == 4


def test_r1_consulta_corregida():
    con = conectar()
    malos = con.execute(
        """
        SELECT COUNT(*) FROM clientes
        WHERE email IS NULL OR TRIM(email) = ''
           OR email NOT LIKE '%_@_%._%'
           OR email LIKE '%@%@%'
           OR email LIKE '% %'
        """
    ).fetchone()[0]
    assert malos == 108
    assert round(100 * (1200 - malos) / 1200, 1) == 91.0


def test_r1_consulta_ingenua():
    con = conectar()
    bien = con.execute(
        "SELECT COUNT(*) FROM clientes WHERE email LIKE '%_@_%._%'"
    ).fetchone()[0]
    assert round(100 * bien / 1200, 1) == 94.0


def test_r2_telefonos_vacios():
    con = conectar()
    vacios = con.execute(
        "SELECT COUNT(*) FROM clientes WHERE telefono IS NULL OR TRIM(telefono) = ''"
    ).fetchone()[0]
    assert vacios == 216
    assert round(100 * (1200 - vacios) / 1200, 1) == 82.0


def test_r2_nulos_y_vacios():
    # El CSV distingue nulo (campo vacío) de vacío ("") para el laboratorio.
    lineas = (ESTUDIANTE / "clientes.csv").read_text(encoding="utf-8").splitlines()[1:]
    nulos = vacios = 0
    for linea in lineas:
        campos = []
        actual = ""
        entre_comillas = False
        for caracter in linea:
            if caracter == '"':
                entre_comillas = not entre_comillas
                actual += caracter
            elif caracter == "," and not entre_comillas:
                campos.append(actual)
                actual = ""
            else:
                actual += caracter
        campos.append(actual)
        if campos[3] == "":
            nulos += 1
        elif campos[3] == '""':
            vacios += 1
    assert nulos == 150
    assert vacios == 66


def test_r3_montos():
    con = conectar()
    malos = con.execute(
        "SELECT COUNT(*) FROM pedidos WHERE CAST(monto AS REAL) <= 0"
    ).fetchone()[0]
    assert malos == 51
    assert round(100 * (8500 - malos) / 8500, 1) == 99.4


def test_r4_ultimos_y_anteriores():
    con = conectar()
    corte = meta()["fecha_corte"]
    reciente = con.execute(
        """
        SELECT COUNT(*) AS entregados,
               SUM(CASE WHEN fecha_entrega IS NULL OR TRIM(fecha_entrega) = ''
                        THEN 1 ELSE 0 END) AS sin_fecha
        FROM pedidos
        WHERE estado = 'entregado'
          AND fecha_pedido >= date(?, '-13 days')
        """,
        (corte,),
    ).fetchone()
    anterior = con.execute(
        """
        SELECT COUNT(*) AS entregados,
               SUM(CASE WHEN fecha_entrega IS NULL OR TRIM(fecha_entrega) = ''
                        THEN 1 ELSE 0 END) AS sin_fecha
        FROM pedidos
        WHERE estado = 'entregado'
          AND fecha_pedido BETWEEN date(?, '-27 days') AND date(?, '-14 days')
        """,
        (corte, corte),
    ).fetchone()
    assert reciente["entregados"] == 3492
    assert reciente["sin_fecha"] == 139
    assert round(100 * (3492 - 139) / 3492, 1) == 96.0
    assert anterior["entregados"] == 3478
    assert anterior["sin_fecha"] == 35
    assert round(100 * (3478 - 35) / 3478, 1) == 99.0


def test_r4_causa_en_version_23():
    con = conectar()
    corte = meta()["fecha_corte"]
    filas = con.execute(
        """
        SELECT version_app, COUNT(*) AS fallas
        FROM pedidos
        WHERE estado = 'entregado'
          AND fecha_pedido >= date(?, '-13 days')
          AND (fecha_entrega IS NULL OR TRIM(fecha_entrega) = '')
        GROUP BY version_app
        """,
        (corte,),
    ).fetchall()
    fallas = {fila["version_app"]: fila["fallas"] for fila in filas}
    total = sum(fallas.values())
    assert total == 139
    assert fallas.get("2.3", 0) / total > 0.85


def test_notas_salud_alrededor_de_3_por_ciento():
    pedidos = leer("pedidos.csv")
    llenas = [p for p in pedidos if (p.get("notas") or "").strip()]
    assert len(llenas) == 3485
    salud = meta()["notas_salud"]
    assert 0.025 <= len(salud) / len(llenas) <= 0.035


def test_notas_de_salud_repartidas_y_variadas():
    pedidos = leer("pedidos.csv")
    ids = set(meta()["notas_salud"])
    posiciones = [i for i, p in enumerate(pedidos) if p["id"] in ids]
    assert len(posiciones) >= 25
    # ninguna franja de 50 filas seguidas concentra más de 2
    assert max(
        sum(1 for i in posiciones if s <= i < s + 50)
        for s in range(len(pedidos) - 49)
    ) <= 2
    texto = " ".join(pedidos[i]["notas"].lower() for i in posiciones)
    for forma in ("alergia", "soy celíaca", "diabético"):
        assert forma in texto


def test_verdad_columnas():
    with (DATOS / "verdad_columnas.csv").open(encoding="utf-8", newline="") as archivo:
        verdad = {f["columna"]: f["categoria"] for f in csv.DictReader(archivo)}
    for columna in ("nombre", "email", "telefono", "carrera"):
        assert verdad[f"clientes.{columna}"] == "Personal"
    assert verdad["pedidos.notas"] == "Sensible"
    assert verdad["pedidos.monto"] == "Interna"
    assert verdad["pedidos.version_app"] == "Interna"
