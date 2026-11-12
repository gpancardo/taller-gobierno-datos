"""Seis palabras para hoy · video de la lámina 7.

Una sola escena continua (ManimCE). La narración se genera primero con
edge-tts y guarda el tiempo de cada palabra; las animaciones esperan a la
palabra que les toca (`self.en("monto")`). Ver render.sh.

    python pilares.py voz       # voz y tiempo de cada palabra
    manim -qh --fps 30 pilares.py Pilares
    python pilares.py srt       # subtítulos con los tiempos reales
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
SALIDA = RAIZ / "salida"
VOZ = SALIDA / "voz"
VOZ_NOMBRE = "es-MX-DaliaNeural"
VELOCIDAD = "+22%"

# Todo lo que se dice. Los números salen de carpeta-estudiante/*.csv.
NARRACION = {
    "intro": "Hoy usamos seis palabras. "
             "Catálogo, metadatos, clasificación, calidad, linaje y dueño.",
    "catalogo": "El catálogo es la lista de lo que tenemos. "
                "Clientes, con mil doscientas filas. Pedidos, con ocho mil quinientas.",
    "metadatos": "Los metadatos describen a los datos. "
                 "Esta columna es monto, un número. Lo paga el cliente. "
                 "¿En qué moneda? No se sabe: por confirmar.",
    "clasificacion": "Clasificar es decidir qué tan delicado es un dato: pública, interna, personal o sensible. "
                     "El identificador es interno. El nombre, personal. "
                     "Una nota con «alergia al gluten» habla de salud: sensible.",
    "calidad": "Calidad son tres preguntas. ¿Está? Falta el teléfono. "
               "¿Está bien escrito? Este correo tiene dos arrobas. "
               "¿Cuadra? Este pedido, entregado, no tiene fecha. "
               "Cada pregunta es una regla, y se prueba con SQL.",
    "linaje": "El linaje es el camino del dato. "
              "Nace en la app de repartidores, pasa a pedidos y llega al tablero. "
              "Si algo cambia arriba, se nota abajo.",
    "dueno": "Cada regla tiene un dueño. Si falla la del correo, le toca a Atención a clientes.",
    "cierre": "Seis palabras, y en el laboratorio las usas todas.",
}
ORDEN = list(NARRACION)


def normal(palabra: str) -> str:
    sin_acentos = unicodedata.normalize("NFD", palabra.lower())
    return re.sub(r"[^a-z0-9ñ]", "", "".join(c for c in sin_acentos if unicodedata.category(c) != "Mn"))


def duracion(ruta: Path) -> float:
    salida = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(ruta)],
        capture_output=True, text=True, check=True,
    )
    return float(salida.stdout)


# ---------------------------------------------------------------- voz

def generar_voz():
    import asyncio
    import edge_tts

    VOZ.mkdir(parents=True, exist_ok=True)

    async def una(clave: str, texto: str):
        com = edge_tts.Communicate(texto, VOZ_NOMBRE, rate=VELOCIDAD, boundary="WordBoundary")
        palabras, audio = [], bytearray()
        async for trozo in com.stream():
            if trozo["type"] == "audio":
                audio += trozo["data"]
            elif trozo["type"] == "WordBoundary":
                inicio = trozo["offset"] / 1e7
                palabras.append([trozo["text"], inicio, inicio + trozo["duration"] / 1e7])
        (VOZ / f"{clave}.mp3").write_bytes(audio)
        return palabras

    tiempos = {}
    for clave, texto in NARRACION.items():
        tiempos[clave] = {"palabras": asyncio.run(una(clave, texto))}
        tiempos[clave]["duracion"] = duracion(VOZ / f"{clave}.mp3")
        print(f"{clave:14s} {tiempos[clave]['duracion']:5.2f} s")
    (VOZ / "tiempos.json").write_text(json.dumps(tiempos, ensure_ascii=False, indent=1))


# ---------------------------------------------------------------- escena

PAUSA = 0.9  # silencio entre secciones; ahí ocurren las transiciones

if "manim" in sys.modules or __name__ != "__main__":
    from manim import *  # noqa: F403

    config.background_color = "#0E1A4F"

    # Paleta del laboratorio (styles.css), con rojo aclarado para leerse sobre noche.
    NOCHE = "#0E1A4F"
    PANEL = "#15246A"
    AZUL = "#2440B8"
    AZUL_CLARO = "#7B95FF"
    TEXTO = "#EEF2FA"
    TENUE = "#B9C8DE"
    AMARILLO = "#F5C04A"   # "mira aquí"
    ROJO = "#FF6B5E"       # falla / sensible
    CIAN = "#19A3C8"

    GOTICA, FRANKLIN, COURIER = "League Gothic", "Libre Franklin", "Courier Prime"

    PALABRAS = ["catálogo", "metadatos", "clasificación", "calidad", "linaje", "dueño"]
    DEFINICIONES = [
        "La lista de lo que tenemos.",
        "Datos que describen a los datos.",
        "Qué tan delicado es cada dato.",
        "Si podemos confiar en el dato.",
        "El camino que recorre el dato.",
        "Quién responde por cada regla.",
    ]

    def texto(s, tam=32, color=TEXTO, **kw):
        return Text(s, font=FRANKLIN, font_size=tam, color=color, **kw)

    def gotica(s, tam=64, color=TEXTO, **kw):
        return Text(s, font=GOTICA, font_size=tam, color=color, **kw)

    def codigo(s, tam=28, color=TEXTO, **kw):
        return Text(s, font=COURIER, font_size=tam, color=color, **kw)

    def panel(ancho, alto, borde=AZUL_CLARO, relleno=PANEL):
        return RoundedRectangle(
            corner_radius=0.14, width=ancho, height=alto,
            fill_color=relleno, fill_opacity=1, stroke_color=borde, stroke_width=2,
        )

    def tache(tam=0.42, color=ROJO):
        return VGroup(
            Line(UL * tam / 2, DR * tam / 2), Line(DL * tam / 2, UR * tam / 2)
        ).set_stroke(color, width=8)

    def hueco(ancho=1.3, alto=0.46):
        return DashedVMobject(
            RoundedRectangle(corner_radius=0.06, width=ancho, height=alto), num_dashes=22
        ).set_stroke(ROJO, width=3)

    def en_linea(lista, tam, sep="    "):
        """Una sola línea de texto partida en palabras: todas comparten línea base."""
        linea = sep.join(lista)
        t = texto(linea, tam, disable_ligatures=True)  # sin ligaduras: un glifo por carácter, espacios incluidos
        assert len(t) == len(linea), "pango partió los glifos distinto"
        grupos, i = VGroup(), 0
        for palabra in lista:
            grupos.add(VGroup(*t[i:i + len(palabra)]))
            i += len(palabra) + len(sep)
        return grupos

    class Pilares(Scene):
        # ---------------------------------------------------- tiempo

        def seccion(self, clave):
            datos = json.loads((VOZ / "tiempos.json").read_text())[clave]
            self.t0 = self.renderer.time
            self.inicios[clave] = self.t0
            self.palabras = datos["palabras"]
            self.cursor = 0
            self.fin_voz = self.t0 + datos["duracion"]
            self.add_sound(str(VOZ / f"{clave}.mp3"))

        def en(self, palabra):
            """Espera a que la voz diga `palabra` (la siguiente vez que aparece)."""
            buscada = normal(palabra)
            for i in range(self.cursor, len(self.palabras)):
                if normal(self.palabras[i][0]) == buscada:
                    self.cursor = i + 1
                    falta = self.t0 + self.palabras[i][1] - self.renderer.time
                    if falta > 1 / 30:
                        self.wait(falta)
                    return
            raise ValueError(f"'{palabra}' no está en la narración restante")

        def terminar(self, extra=0.0):
            falta = self.fin_voz + extra - self.renderer.time
            if falta > 1 / 30:
                self.wait(falta)

        # ---------------------------------------------------- marco

        def encabezado(self, i):
            t = gotica(PALABRAS[i].upper(), 84).to_corner(UL, buff=0.55)
            d = texto(DEFINICIONES[i], 30, TENUE).next_to(t, DOWN, aligned_edge=LEFT, buff=0.12)
            return VGroup(t, d)

        def mover_marca(self, i):
            """Pinta la palabra i en la tira de abajo."""
            anims = [
                p.animate.set_color(AMARILLO if j == i else TEXTO).set_opacity(1 if j == i else 0.4)
                for j, p in enumerate(self.tira)
            ]
            destino = Line(LEFT, RIGHT).set_stroke(AMARILLO, 4)
            destino.set_width(self.tira[i].width).next_to(self.tira[i], DOWN, buff=0.12)
            anims.append(Transform(self.subrayado, destino))
            return anims

        def cambiar(self, i, salen=()):
            """Transición entre secciones: sale lo anterior, entra el encabezado."""
            nuevo = self.encabezado(i)
            salida = [FadeOut(m) for m in salen] + ([FadeOut(self.cabeza)] if self.cabeza else [])
            self.play(*salida, *self.mover_marca(i), run_time=0.3)
            self.play(FadeIn(nuevo[0], shift=RIGHT * 0.3), FadeIn(nuevo[1], shift=RIGHT * 0.3), run_time=0.2)
            self.cabeza = nuevo

        # ---------------------------------------------------- guion

        def construct(self):
            self.cabeza = None
            self.inicios = {}
            self.intro()
            tarjetas = self.catalogo()
            restos = self.metadatos(tarjetas)
            restos = self.clasificacion(restos)
            restos = self.calidad(restos)
            restos = self.linaje(restos)
            restos = self.dueno(restos)
            self.cierre(restos)
            (SALIDA / "inicios.json").write_text(json.dumps(self.inicios))

        def intro(self):
            self.seccion("intro")
            grande = gotica("SEIS PALABRAS", 150)
            sub = texto("para cuidar los datos", 40, AMARILLO)
            VGroup(grande, sub).arrange(DOWN, buff=0.3).move_to(UP * 1.7)
            self.play(Write(grande), run_time=0.8)
            self.play(FadeIn(sub, shift=UP * 0.2), run_time=0.6)

            filas = VGroup(en_linea(PALABRAS[:3], 52), en_linea(PALABRAS[3:], 52)).arrange(DOWN, buff=0.45)
            filas.move_to(DOWN * 1.3)
            rejilla = VGroup(*filas[0], *filas[1])
            for palabra, mob in zip(["catalogo", "metadatos", "clasificacion", "calidad", "linaje", "dueno"], rejilla):
                self.en(palabra)
                self.play(FadeIn(mob, shift=UP * 0.2), run_time=0.35)
            self.terminar(0)

            # las seis palabras bajan y se vuelven la tira de navegación
            self.tira = en_linea(PALABRAS, 26, sep="       ")
            self.tira.to_edge(DOWN, buff=0.42)
            self.subrayado = Line(LEFT, RIGHT).set_stroke(AMARILLO, 4, opacity=0).set_width(0.01)
            self.subrayado.next_to(self.tira[0], DOWN, buff=0.12)
            self.play(
                FadeOut(VGroup(grande, sub), shift=UP * 0.4),
                FadeOut(rejilla, shift=DOWN * 0.6, scale=0.8),
                LaggedStart(*[FadeIn(w, shift=UP * 0.2) for w in self.tira], lag_ratio=0.08),
                run_time=1.0,
            )
            self.add(self.subrayado)

        def catalogo(self):
            self.cambiar(0)
            self.seccion("catalogo")

            def tarjeta(nombre, columnas, total, cols_grid):
                caja = panel(5.9, 4.0)
                nom = codigo(nombre, 40).move_to(caja.get_corner(UL) + RIGHT * 0.4 + DOWN * 0.5, aligned_edge=LEFT)
                raya = Line(caja.get_left(), caja.get_right()).set_stroke(AZUL_CLARO, 1.5, opacity=0.6)
                raya.set_y(caja.get_top()[1] - 1.45)
                chips = VGroup(*[codigo(c, 24, TENUE) for c in columnas])
                chips.arrange_in_grid(cols=cols_grid, buff=(0.6, 0.24), col_alignments="l" * cols_grid)
                chips.move_to([caja.get_x(), (raya.get_y() + caja.get_bottom()[1]) / 2, 0])
                contador = ValueTracker(0)
                cuenta = always_redraw(
                    lambda: codigo(f"{int(contador.get_value()):,} filas", 28, AMARILLO)
                    .move_to(caja.get_corner(UL) + RIGHT * 0.4 + DOWN * 1.05, aligned_edge=LEFT)
                )
                return VGroup(caja, nom, raya, chips, cuenta), contador, total

            clientes = tarjeta("clientes", ["id", "nombre", "email", "telefono", "carrera", "fecha_registro"], 1200, 2)
            pedidos = tarjeta(
                "pedidos",
                ["id", "cliente_id", "fecha_pedido", "fecha_entrega", "estado", "monto", "notas", "version_app"],
                8500, 2,
            )
            VGroup(clientes[0], pedidos[0]).arrange(RIGHT, buff=0.55).move_to(DOWN * 0.6)

            for (grupo, contador, total), (clave, numero) in zip(
                (clientes, pedidos), (("clientes", "mil"), ("pedidos", "ocho"))
            ):
                self.en(clave)
                self.play(FadeIn(grupo, shift=UP * 0.25), run_time=0.6)
                self.en(numero)
                self.play(contador.animate.set_value(total), run_time=1.3, rate_func=rate_functions.ease_out_cubic)
            self.terminar()
            for grupo, _, _ in (clientes, pedidos):
                grupo[4].clear_updaters()
            return clientes[0], pedidos[0]

        def metadatos(self, tarjetas):
            clientes, pedidos = tarjetas
            chip_monto = pedidos[3][5]
            self.play(FadeOut(clientes), FadeOut(self.cabeza), *self.mover_marca(1), run_time=0.6)
            cabeza = self.encabezado(1)
            self.cabeza = cabeza

            # la columna monto sale de la tabla
            col_caja = panel(2.6, 3.5).move_to(LEFT * 4.6 + DOWN * 0.55)
            col_nom = codigo("monto", 36, AMARILLO).move_to(col_caja.get_top() + DOWN * 0.45)
            col_raya = Line(LEFT, RIGHT).set_width(2.6).set_stroke(AZUL_CLARO, 1.5, 0.6)
            col_raya.set_y(col_caja.get_top()[1] - 0.85).set_x(col_caja.get_x())
            valores = VGroup(*[codigo(v, 30) for v in ("282.25", "59.81", "238.08")], codigo("⋮", 30, TENUE))
            valores.arrange(DOWN, buff=0.32, aligned_edge=RIGHT).next_to(col_raya, DOWN, buff=0.3)

            ficha = panel(7.4, 3.5).move_to(RIGHT * 2.3 + DOWN * 0.55)
            filas_datos = [
                ("columna", "monto"),
                ("tipo", "número"),
                ("guarda", "lo que paga el cliente"),
                ("moneda", "?"),
            ]
            filas = VGroup()
            for clave, valor in filas_datos:
                k = texto(clave, 24, TENUE)
                v = codigo(valor, 28) if clave == "columna" else texto(valor, 30)
                filas.add(VGroup(k, v))
            for k, f in enumerate(filas):
                y = ficha.get_top()[1] - 0.65 - 0.75 * k
                f[0].move_to([ficha.get_left()[0] + 0.5, y, 0], aligned_edge=LEFT)
                f[1].move_to([ficha.get_left()[0] + 2.35, y, 0], aligned_edge=LEFT)
            etiqueta_ficha = texto("ficha de la columna", 22, TENUE).next_to(ficha, UP, aligned_edge=LEFT, buff=0.15)
            enlace = Line(col_caja.get_right(), ficha.get_left()).set_stroke(AMARILLO, 3, 0.8)

            # la columna monto sale de la tabla y el resto se va
            pedidos[3].remove(chip_monto)
            chip_monto.set_z_index(2)
            self.play(
                FadeIn(cabeza[0], shift=RIGHT * 0.3), FadeIn(cabeza[1], shift=RIGHT * 0.3),
                FadeOut(pedidos),
                chip_monto.animate.become(col_nom.copy()).set_z_index(2),
                FadeIn(col_caja, run_time=0.8, rate_func=rate_functions.ease_in_quad), FadeIn(col_raya),
                run_time=0.8,
            )
            col_nom = chip_monto
            self.seccion("metadatos")

            self.en("describen")
            self.play(FadeIn(ficha), FadeIn(etiqueta_ficha), run_time=0.5)
            self.en("monto")
            self.play(Indicate(col_nom, color=AMARILLO, scale_factor=1.15), run_time=0.8)
            self.play(
                LaggedStart(*[FadeIn(v, shift=DOWN * 0.15) for v in valores], lag_ratio=0.2),
                Create(enlace), FadeIn(filas[0], shift=RIGHT * 0.2), run_time=0.8,
            )
            self.en("numero")
            self.play(FadeIn(filas[1], shift=RIGHT * 0.2), run_time=0.4)
            self.en("paga")
            self.play(FadeIn(filas[2], shift=RIGHT * 0.2), run_time=0.4)
            self.en("moneda")
            self.play(FadeIn(filas[3], shift=RIGHT * 0.2), run_time=0.4)
            self.en("sabe")
            self.play(Indicate(filas[3][1], color=ROJO, scale_factor=1.4), run_time=0.7)
            self.en("confirmar")
            por_confirmar = texto("por confirmar", 30, AMARILLO).move_to(filas[3][1], aligned_edge=LEFT)
            marco = SurroundingRectangle(por_confirmar, color=AMARILLO, buff=0.12, corner_radius=0.06)
            self.play(Transform(filas[3][1], por_confirmar), run_time=0.5)
            self.play(Create(marco), run_time=0.5)
            self.terminar()
            return VGroup(col_caja, col_nom, col_raya, valores, ficha, etiqueta_ficha, filas, enlace, marco)

        def clasificacion(self, restos):
            self.cambiar(2, [restos])
            self.seccion("clasificacion")

            niveles = [("PÚBLICA", TENUE), ("INTERNA", AZUL_CLARO), ("PERSONAL", AMARILLO), ("SENSIBLE", ROJO)]
            botes = VGroup()
            for nombre, color in niveles:
                caja = panel(2.95, 2.4, borde=color)
                banda = RoundedRectangle(corner_radius=0.14, width=2.95, height=0.7, fill_color=color,
                                         fill_opacity=1, stroke_width=0).align_to(caja, UP)
                tapa = Rectangle(width=2.95, height=0.2, fill_color=color, fill_opacity=1, stroke_width=0)
                tapa.align_to(banda, DOWN)
                etiqueta = gotica(nombre, 40, NOCHE).move_to(banda)
                botes.add(VGroup(caja, banda, tapa, etiqueta))
            botes.arrange(RIGHT, buff=0.3).move_to(DOWN * 0.6)
            escala_txt = texto("más delicado", 22, TENUE)
            escala = Arrow(botes.get_corner(DL) + DOWN * 0.45, botes.get_corner(DR) + DOWN * 0.45 + LEFT * 2.3,
                           buff=0, stroke_width=3, color=TENUE, max_tip_length_to_length_ratio=0.02)
            escala_txt.next_to(escala, RIGHT, buff=0.2)

            for bote, palabra in zip(botes, ["publica", "interna", "personal", "sensible"]):
                self.en(palabra)
                self.play(FadeIn(bote, shift=UP * 0.2), run_time=0.35)
            self.play(GrowArrow(escala), FadeIn(escala_txt), run_time=0.5)

            def dentro(bote, n):
                return bote[0].get_top() + DOWN * (1.15 + 0.6 * n)

            origen = UP * 1.45
            self.en("identificador")
            chip_id = codigo("id", 30).move_to(origen)
            self.play(FadeIn(chip_id, shift=DOWN * 0.2), run_time=0.35)
            self.en("interno")
            self.play(chip_id.animate.move_to(dentro(botes[1], 0)), run_time=0.6)

            self.en("nombre")
            chip_nom = codigo("nombre", 30).move_to(origen)
            self.play(FadeIn(chip_nom, shift=DOWN * 0.2), run_time=0.35)
            self.en("personal")
            self.play(chip_nom.animate.move_to(dentro(botes[2], 0)), run_time=0.6)

            self.en("nota")
            chip_notas = codigo("notas", 30).move_to(origen + LEFT * 2.2)
            cita = codigo("“Alergia al gluten.”", 26, TEXTO).next_to(chip_notas, RIGHT, buff=0.4)
            self.play(FadeIn(chip_notas, shift=DOWN * 0.2), run_time=0.35)
            self.play(Write(cita), run_time=0.7)
            self.en("salud")
            self.play(cita.animate.set_color(ROJO), run_time=0.4)
            self.en("sensible")
            self.play(
                chip_notas.animate.move_to(dentro(botes[3], 0)),
                FadeOut(cita, target_position=dentro(botes[3], 0)),
                run_time=0.6,
            )
            self.play(Indicate(botes[3][3], color=TEXTO, scale_factor=1.15), run_time=0.6)
            self.terminar()
            return VGroup(botes, escala, escala_txt, chip_id, chip_nom, chip_notas)

        def calidad(self, restos):
            self.cambiar(3, [restos])
            self.seccion("calidad")

            def registro(*campos):
                """campos: (nombre, valor); valor None = hueco rojo."""
                g = VGroup()
                for nombre, valor in campos:
                    v = hueco() if valor is None else valor
                    g.add(VGroup(texto(nombre, 18, TENUE), v).arrange(DOWN, buff=0.1, aligned_edge=LEFT))
                g.arrange(RIGHT, buff=0.45, aligned_edge=UP)
                return VGroup(panel(g.width + 0.6, g.height + 0.4).move_to(g), g)

            casos = [  # filas reales de carpeta-estudiante
                ("¿Está?", registro(("id", codigo("C0014", 22, TENUE)), ("telefono", None)), "R2"),
                ("¿Está bien escrito?", registro(
                    ("id", codigo("C0784", 22, TENUE)),
                    ("email", codigo("paula.ochoa.ponce784@@correo.test", 22, t2c={"@@": ROJO})),
                ), "R1"),
                ("¿Cuadra?", registro(
                    ("id", codigo("P00021", 22, TENUE)), ("estado", codigo("entregado", 22)),
                    ("fecha_entrega", None),
                ), "R4"),
            ]
            filas = VGroup()
            for pregunta, reg, regla in casos:
                filas.add(VGroup(gotica(pregunta, 46), reg, tache(), codigo(regla, 26, AMARILLO)))
            for k, f in enumerate(filas):
                y = 1.05 - 1.3 * k
                f[3].move_to([-6.5, y, 0], aligned_edge=LEFT)
                f[0].move_to([-5.9, y, 0], aligned_edge=LEFT)
                f[1].move_to([-2.35, y, 0], aligned_edge=LEFT)
                f[2].move_to([6.3, y, 0])

            for k, (palabra, evidencia) in enumerate((("esta", "falta"), ("bien", "arrobas"), ("cuadra", "fecha"))):
                self.en(palabra)
                self.play(FadeIn(filas[k][0], shift=RIGHT * 0.2), run_time=0.4)
                self.en(evidencia)
                self.play(FadeIn(filas[k][1]), run_time=0.45)
                self.play(Create(filas[k][2]), run_time=0.35)

            self.en("regla")
            self.play(
                LaggedStart(*[FadeIn(f[3], shift=RIGHT * 0.2) for f in filas], lag_ratio=0.25),
                run_time=0.9,
            )
            self.en("sql")
            sql = texto("cada regla se prueba con SQL", 26, TENUE).move_to([-2.35, -2.65, 0], aligned_edge=LEFT)
            self.play(FadeIn(sql, shift=UP * 0.15), run_time=0.5)
            self.terminar()
            return VGroup(filas, sql)

        def linaje(self, restos):
            self.cambiar(4, [restos])
            self.seccion("linaje")

            def nodo(*contenido, ancho=3.4):
                g = VGroup(*contenido).arrange(DOWN, buff=0.18)
                return VGroup(panel(ancho, 2.1), g)

            app = nodo(texto("App de", 30), texto("repartidores", 30), codigo("versión 2.3", 22, TENUE))
            tabla = nodo(texto("tabla", 22, TENUE), codigo("pedidos", 38))
            alturas = [0.55, 0.85, 0.7, 1.0]
            barras = VGroup(*[
                Rectangle(width=0.32, height=h, fill_color=CIAN, fill_opacity=1, stroke_width=0) for h in alturas
            ]).arrange(RIGHT, buff=0.12, aligned_edge=DOWN)
            tablero = nodo(texto("Tablero", 30), barras)
            VGroup(app, tabla, tablero).arrange(RIGHT, buff=1.05).move_to(DOWN * 0.45)
            f1 = Arrow(app.get_right(), tabla.get_left(), buff=0.12, color=TENUE, stroke_width=4)
            f2 = Arrow(tabla.get_right(), tablero.get_left(), buff=0.12, color=TENUE, stroke_width=4)
            arriba = texto("arriba", 24, TENUE).next_to(app, DOWN, buff=0.35)
            abajo = texto("abajo", 24, TENUE).next_to(tablero, DOWN, buff=0.35)

            def viaje(color, t=0.9):
                punto = Dot(radius=0.11, color=color).move_to(f1.get_start())
                ruta = VMobject().set_points_as_corners([f1.get_start(), f1.get_end(), f2.get_start(), f2.get_end()])
                return punto, MoveAlongPath(punto, ruta, run_time=t, rate_func=rate_functions.ease_in_out_sine)

            self.en("nace")
            self.play(FadeIn(app, shift=UP * 0.2), run_time=0.5)
            self.en("pedidos")
            self.play(GrowArrow(f1), FadeIn(tabla, shift=UP * 0.2), run_time=0.6)
            self.en("tablero")
            self.play(GrowArrow(f2), FadeIn(tablero, shift=UP * 0.2), run_time=0.6)
            punto, anim = viaje(AMARILLO, 1.1)
            self.add(punto)
            self.play(anim)
            self.play(FadeOut(punto), run_time=0.2)

            self.en("cambia")
            self.play(app[0].animate.set_stroke(ROJO, 4), app[1][2].animate.set_color(ROJO),
                      FadeIn(arriba), run_time=0.5)
            punto, anim = viaje(ROJO, 1.0)
            self.add(punto)
            self.play(anim)
            nueva = barras[3].copy().stretch_to_fit_height(0.3, about_edge=DOWN).set_fill(ROJO)
            self.play(FadeOut(punto), Transform(barras[3], nueva), tablero[0].animate.set_stroke(ROJO, 4),
                      FadeIn(abajo), run_time=0.6)
            self.terminar()
            return VGroup(app, tabla, tablero, f1, f2, arriba, abajo)

        def dueno(self, restos):
            self.cambiar(5, [restos])
            self.seccion("dueno")

            reglas = [  # carpeta-estudiante/reglas.csv
                ("R1", "El correo está bien escrito", 0),
                ("R2", "El teléfono no está vacío", 0),
                ("R3", "El monto es mayor que cero", 1),
                ("R4", "Si dice entregado, tiene fecha", 1),
            ]
            tarjetas = VGroup()
            for rid, desc, _ in reglas:
                caja = panel(6.4, 0.78)
                g = VGroup(codigo(rid, 28, AMARILLO), texto(desc, 26)).arrange(RIGHT, buff=0.35)
                g.move_to(caja).align_to(caja.get_left() + RIGHT * 0.3, LEFT)
                tarjetas.add(VGroup(caja, g))
            tarjetas.arrange(DOWN, buff=0.22).move_to(LEFT * 2.55 + DOWN * 0.55)

            duenos = VGroup()
            for nombre in ("Atención a clientes", "Operaciones"):
                caja = panel(4.0, 1.15)
                duenos.add(VGroup(caja, texto(nombre, 30).move_to(caja)))
            duenos.arrange(DOWN, buff=1.0).move_to(RIGHT * 4.6 + DOWN * 0.55)
            lineas = VGroup(*[
                Line(t.get_right(), duenos[d].get_left(), buff=0.1).set_stroke(TENUE, 2.5, 0.7)
                for t, (_, _, d) in zip(tarjetas, reglas)
            ])
            rotulo = texto("dueño", 22, TENUE).next_to(duenos, UP, buff=0.15)

            self.en("regla")
            self.play(LaggedStart(*[FadeIn(t, shift=RIGHT * 0.2) for t in tarjetas], lag_ratio=0.15), run_time=0.9)
            self.en("dueno")
            self.play(FadeIn(duenos), FadeIn(rotulo), LaggedStart(*[Create(l) for l in lineas], lag_ratio=0.1),
                      run_time=0.9)

            self.en("falla")
            x = tache(0.36).next_to(tarjetas[0][0], LEFT, buff=0.2)
            self.play(
                tarjetas[0][0].animate.set_stroke(ROJO, 4), Create(x),
                *[t.animate.set_opacity(0.3) for t in tarjetas[1:]],
                *[l.animate.set_stroke(opacity=0.15) for l in lineas[1:]],
                duenos[1].animate.set_opacity(0.3),
                run_time=0.6,
            )
            self.en("toca")
            self.play(
                lineas[0].animate.set_stroke(AMARILLO, 5, 1),
                duenos[0][0].animate.set_fill(AMARILLO).set_stroke(AMARILLO),
                duenos[0][1].animate.set_color(NOCHE),
                run_time=0.6,
            )
            self.terminar()
            return VGroup(tarjetas, duenos, lineas, rotulo, x)

        def cierre(self, restos):
            self.play(FadeOut(restos), FadeOut(self.cabeza), FadeOut(self.subrayado), run_time=0.6)
            self.seccion("cierre")

            items = VGroup()
            for palabra, definicion in zip(PALABRAS, DEFINICIONES):
                items.add(VGroup(gotica(palabra.upper(), 54).set_opacity(0.35), texto(definicion, 24, TENUE))
                          .arrange(DOWN, buff=0.06))
            items.arrange_in_grid(rows=3, cols=2, buff=(1.6, 0.62)).move_to(UP * 0.45)
            self.play(
                FadeOut(self.tira, shift=DOWN * 0.2),
                LaggedStart(*[FadeIn(it, shift=UP * 0.15) for it in items], lag_ratio=0.1),
                run_time=1.0,
            )
            self.play(LaggedStart(*[it[0].animate.set_opacity(1) for it in items], lag_ratio=0.15), run_time=1.0)

            self.en("laboratorio")
            final = texto("y en el laboratorio las usas todas.", 42, t2c={"laboratorio": AMARILLO})
            final.move_to(DOWN * 2.75)
            self.play(FadeIn(final, shift=UP * 0.2), run_time=0.6)
            self.terminar(0.2)
            self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.5)


# ---------------------------------------------------------------- subtítulos

def escribir_srt():
    tiempos = json.loads((VOZ / "tiempos.json").read_text())

    def hms(t):
        ms = int(round(t * 1000))
        return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"

    inicios = json.loads((SALIDA / "inicios.json").read_text())  # lo escribe la escena
    entradas, n = [], 1
    for clave in ORDEN:
        t = inicios[clave]
        palabras = tiempos[clave]["palabras"]
        frases = re.split(r"(?<=[.?:])\s+", NARRACION[clave])
        i = 0
        for frase in frases:
            n_pal = len([w for w in re.split(r"\s+", frase) if normal(w)])
            grupo = palabras[i:i + n_pal]
            i += n_pal
            if grupo:
                entradas.append(f"{n}\n{hms(t + grupo[0][1])} --> {hms(t + grupo[-1][2] + 0.25)}\n{frase}\n")
                n += 1
    (SALIDA / "pilares.srt").write_text("\n".join(entradas))


if __name__ == "__main__":
    {"voz": generar_voz, "srt": escribir_srt}[sys.argv[1]]()
