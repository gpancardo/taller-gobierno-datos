/* Laboratorio de gobierno de datos · Antojo Campus
   Todo corre en el navegador con sql.js. No hay servidor. */

const DATOS = window.DATOS_TALLER || {};
const FACILITADOR = new URLSearchParams(location.search).get("facilitador") === "1";

const REGLAS = {
  R1: { titulo: "R1 · El correo está bien escrito", meta: 95, tabla: "clientes" },
  R2: { titulo: "R2 · El teléfono no está vacío", meta: 95, tabla: "clientes" },
  R3: { titulo: "R3 · El monto es mayor que cero", meta: 99, tabla: "pedidos" },
  R4: { titulo: "R4 · Si dice entregado, tiene fecha", meta: 95, tabla: "pedidos" },
};

const SOLUCIONES = {
  R1: `-- R1 corregida: 91%
SELECT ROUND(100.0 * SUM(
  CASE WHEN email IS NOT NULL AND TRIM(email) <> ''
        AND email LIKE '%_@_%._%'
        AND email NOT LIKE '%@%@%'
        AND email NOT LIKE '% %'
  THEN 1 ELSE 0 END) / COUNT(*), 1) AS porcentaje
FROM clientes;`,
  R2: `-- R2: 82%
SELECT ROUND(100.0 * SUM(
  CASE WHEN telefono IS NOT NULL AND TRIM(telefono) <> ''
  THEN 1 ELSE 0 END) / COUNT(*), 1) AS porcentaje
FROM clientes;`,
  R3: `-- R3: 99.4%
SELECT ROUND(100.0 * SUM(
  CASE WHEN CAST(monto AS REAL) > 0 THEN 1 ELSE 0 END
) / COUNT(*), 1) AS porcentaje
FROM pedidos;`,
  R4: `-- R4 últimos 14 días: 96%
SELECT ROUND(100.0 * SUM(
  CASE WHEN fecha_entrega IS NOT NULL AND TRIM(fecha_entrega) <> ''
  THEN 1 ELSE 0 END) / COUNT(*), 1) AS porcentaje
FROM pedidos
WHERE estado = 'entregado'
  AND fecha_pedido >= date((SELECT MAX(fecha_pedido) FROM pedidos), '-13 days');

-- Para los 14 días anteriores cambia el filtro por:
-- AND fecha_pedido BETWEEN date((SELECT MAX(fecha_pedido) FROM pedidos), '-27 days')
--                       AND date((SELECT MAX(fecha_pedido) FROM pedidos), '-14 days')`,
};

const CONSULTA_LINAJE = `SELECT fecha_pedido,
       version_app,
       COUNT(*) AS entregas_sin_fecha
FROM pedidos
WHERE estado = 'entregado'
  AND (fecha_entrega IS NULL OR TRIM(fecha_entrega) = '')
  AND fecha_pedido >= date((SELECT MAX(fecha_pedido) FROM pedidos), '-13 days')
GROUP BY fecha_pedido, version_app
ORDER BY fecha_pedido, version_app;`;

let db = null;
let reglaActual = "R1";
let periodoR4 = "ultimos";
let inicioParada3 = null;
let solucionVisible = false;
let filasNotas = [];
const resultados = {
  R1: null,
  R2: null,
  R3: null,
  R4: { ultimos: null, anteriores: null },
};

function escapar(valor) {
  return String(valor ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

/* ---------- CSV y datos ---------- */

function parseCSV(texto) {
  const filas = [];
  let fila = [];
  let campo = "";
  let entreComillas = false;
  let campoCitado = false;

  const cerrarCampo = () => {
    fila.push(campoCitado ? campo : campo === "" ? null : campo);
    campo = "";
    campoCitado = false;
  };

  for (let i = 0; i < texto.length; i += 1) {
    const c = texto[i];
    if (entreComillas) {
      if (c === '"') {
        if (texto[i + 1] === '"') {
          campo += '"';
          i += 1;
        } else {
          entreComillas = false;
        }
      } else {
        campo += c;
      }
    } else if (c === '"') {
      entreComillas = true;
      campoCitado = true;
    } else if (c === ",") {
      cerrarCampo();
    } else if (c === "\n") {
      cerrarCampo();
      if (fila.length > 1 || fila[0] !== null) filas.push(fila);
      fila = [];
    } else if (c !== "\r") {
      campo += c;
    }
  }
  if (campo !== "" || fila.length) {
    cerrarCampo();
    filas.push(fila);
  }

  if (!filas.length) return [];
  const encabezado = filas[0];
  return filas.slice(1).map((valores) => {
    const objeto = {};
    encabezado.forEach((nombre, i) => {
      objeto[nombre] = valores[i] ?? null;
    });
    return objeto;
  });
}

function cargarCSV(nombre) {
  return parseCSV(DATOS[nombre] || "");
}

const clientes = cargarCSV("clientes.csv");
const pedidos = cargarCSV("pedidos.csv");
const reglas = cargarCSV("reglas.csv");
const verdadColumnas = cargarCSV("verdad_columnas.csv");
const linaje = DATOS["linaje.json"] || { nodos: [], enlaces: [] };
const meta = DATOS["meta.json"] || {};

/* ---------- Base de datos ---------- */

function crearBase() {
  const columnas = {
    clientes: [
      ["id", "TEXT"], ["nombre", "TEXT"], ["email", "TEXT"],
      ["telefono", "TEXT"], ["carrera", "TEXT"], ["fecha_registro", "TEXT"],
    ],
    pedidos: [
      ["id", "TEXT"], ["cliente_id", "TEXT"], ["fecha_pedido", "TEXT"],
      ["fecha_entrega", "TEXT"], ["estado", "TEXT"], ["monto", "REAL"],
      ["notas", "TEXT"], ["version_app", "TEXT"],
    ],
    reglas: [
      ["id", "TEXT"], ["descripcion", "TEXT"], ["tabla", "TEXT"],
      ["meta", "INTEGER"], ["dueno", "TEXT"],
    ],
  };

  const datos = { clientes, pedidos, reglas };

  Object.entries(columnas).forEach(([tabla, cols]) => {
    db.run(`CREATE TABLE ${tabla} (${cols.map(([c, t]) => `${c} ${t}`).join(", ")})`);
    const marcas = cols.map(() => "?").join(", ");
    const insercion = db.prepare(`INSERT INTO ${tabla} VALUES (${marcas})`);
    datos[tabla].forEach((fila) => {
      const valores = cols.map(([c, tipo]) => {
        const v = fila[c];
        if (v === null || v === "") return v === "" ? "" : null;
        if (tipo === "REAL") return Number(v);
        if (tipo === "INTEGER") return Number(v);
        return v;
      });
      insercion.run(valores);
    });
    insercion.free();
  });
}

async function iniciarBase() {
  try {
    if (!window.initSqlJs) throw new Error("No se cargó sql.js.");
    const SQL = await window.initSqlJs({ wasmBinary: window.SQL_WASM_BINARY });
    db = new SQL.Database();
    crearBase();
  } catch (error) {
    console.error("No se pudo iniciar la base:", error);
    const mensaje = document.getElementById("mensaje-sql");
    if (mensaje) {
      mensaje.textContent = "No se pudo abrir la base de datos. Recarga la página.";
      mensaje.className = "mensaje error visible";
    }
  }
}

/* ---------- Parada 1: catalogar ---------- */

function perfilColumna(tabla, columna) {
  const filas = tabla === "clientes" ? clientes : pedidos;
  let llenas = 0;
  const ejemplos = [];
  for (const fila of filas) {
    const valor = fila[columna];
    if (valor !== null && String(valor).trim() !== "") {
      llenas += 1;
      if (ejemplos.length < 5 && !ejemplos.includes(String(valor))) {
        ejemplos.push(String(valor));
      }
    }
  }
  return {
    llenas,
    total: filas.length,
    porcentaje: filas.length ? (100 * llenas) / filas.length : 0,
    ejemplos,
  };
}

function tipoDe(columna) {
  if (columna.startsWith("fecha")) return "Fecha";
  if (columna === "monto" || columna === "meta") return "Número";
  return "Texto";
}

function pintarCatalogo() {
  const resumen = document.getElementById("tablas-resumen");
  resumen.innerHTML = [
    ["clientes", clientes, "Personas"],
    ["pedidos", pedidos, "Pedidos de 28 días"],
    ["reglas", reglas, "Reglas de calidad"],
  ]
    .map(
      ([nombre, filas, texto]) => `
      <div class="tabla-mini">
        <strong>${escapar(nombre)}</strong>
        <span>${filas.length} filas</span>
        <p>${escapar(texto)}</p>
      </div>`
    )
    .join("");

  const columnas = [
    ...["id", "nombre", "email", "telefono", "carrera", "fecha_registro"].map((c) => ["clientes", c]),
    ...["id", "cliente_id", "fecha_pedido", "fecha_entrega", "estado", "monto", "notas", "version_app"].map((c) => ["pedidos", c]),
  ];

  document.getElementById("columnas-fichas").innerHTML = columnas
    .map(([tabla, columna]) => {
      const perfil = perfilColumna(tabla, columna);
      return `
        <article class="ficha">
          <p class="tabla-nombre">${escapar(tabla)}</p>
          <h3>${escapar(columna)}</h3>
          <p class="lleno">Lleno: ${perfil.porcentaje.toFixed(0)}% · ${perfil.llenas} de ${perfil.total}</p>
          <p class="nota">Tipo: ${tipoDe(columna)}</p>
          <ul>${perfil.ejemplos.map((e) => `<li>${escapar(e)}</li>`).join("")}</ul>
        </article>`;
    })
    .join("");

  document.getElementById("casillas-diccionario").innerHTML = columnas
    .map(
      ([tabla, columna]) => `
      <label>
        <input type="checkbox" value="${escapar(tabla + "." + columna)}">
        <span>${escapar(tabla)} · <code>${escapar(columna)}</code></span>
      </label>`
    )
    .join("");

  const esquema = document.getElementById("lista-esquema");
  if (esquema) {
    esquema.innerHTML = `
      <p><strong>clientes</strong> (1,200 filas)</p>
      <ul>${["id", "nombre", "email", "telefono", "carrera", "fecha_registro"].map((c) => `<li>${c} · ${tipoDe(c)}</li>`).join("")}</ul>
      <p><strong>pedidos</strong> (8,500 filas)</p>
      <ul>${["id", "cliente_id", "fecha_pedido", "fecha_entrega", "estado", "monto", "notas", "version_app"].map((c) => `<li>${c} · ${tipoDe(c)}</li>`).join("")}</ul>`;
  }
}

function normalizar(texto) {
  return texto.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "");
}

function revisarDiccionario() {
  const texto = document.getElementById("diccionario").value;
  const resumen = document.getElementById("resumen-diccionario");
  if (!texto.trim()) {
    resumen.textContent = "Pega primero el diccionario.";
    return;
  }
  const columnas = [
    "id", "nombre", "email", "telefono", "carrera", "fecha_registro",
    "cliente_id", "fecha_pedido", "fecha_entrega", "estado", "monto",
    "notas", "version_app",
  ];
  const plano = normalizar(texto);
  const mencionadas = columnas.filter((c) => plano.includes(normalizar(c)));
  const faltan = columnas.filter((c) => !mencionadas.includes(c));
  const partes = [`El diccionario menciona ${mencionadas.length} de 13 nombres de columna.`];
  if (faltan.length) {
    partes.push(`No veo: ${faltan.map((c) => `\`${c}\``).join(", ")}.`);
  }
  if (!plano.includes("por confirmar")) {
    partes.push("Falta decir “por confirmar” en lo que no se puede saber.");
  }
  const marcadas = [...document.querySelectorAll("#casillas-diccionario input:checked")].length;
  partes.push(`Marcaste ${marcadas} columnas con descripción dudosa.`);
  resumen.textContent = partes.join(" ");
}

/* ---------- Parada 2: clasificar ---------- */

function pintarColumnasClasificadas() {
  document.getElementById("tabla-columnas").innerHTML = `
    <table>
      <thead>
        <tr>
          <th>Columna</th>
          <th>Mi agente acertó</th>
          <th class="respuesta">Respuesta correcta</th>
          <th class="respuesta">Motivo</th>
        </tr>
      </thead>
      <tbody>
        ${verdadColumnas
          .map((fila, i) => {
            const [tabla, columna] = fila.columna.split(".");
            return `<tr>
              <td>${escapar(tabla)} · <strong>${escapar(columna)}</strong></td>
              <td><input type="checkbox" class="acierto" id="acierto-${i}" aria-label="Mi agente acertó en ${escapar(columna)}"></td>
              <td class="respuesta">${escapar(fila.categoria)}</td>
              <td class="respuesta">${escapar(fila.motivo)}</td>
            </tr>`;
          })
          .join("")}
      </tbody>
    </table>`;
  document.querySelectorAll(".acierto").forEach((c) => c.addEventListener("change", contarAciertos));
}

function contarAciertos() {
  const n = document.querySelectorAll(".acierto:checked").length;
  document.getElementById("num-acierto").textContent = `${n} de ${verdadColumnas.length}`;
}

function sinAcentos(t) {
  return t.normalize("NFD").replace(/[\u0300-\u036f]/g, "").toLowerCase();
}

function buscarNotas() {
  const q = sinAcentos(document.getElementById("buscar-nota").value.trim());
  const salida = document.getElementById("resultado-busqueda");
  if (!q) {
    salida.textContent = "";
    return;
  }
  const n = pedidos.filter((p) => p.notas && sinAcentos(p.notas).includes(q)).length;
  salida.textContent = `${n} notas tienen “${document.getElementById("buscar-nota").value.trim()}”.`;
}

function verNotasSalud() {
  const ids = new Set(meta.notas_salud || []);
  const todas = pedidos.filter((p) => ids.has(p.id));
  const paso = Math.max(1, Math.floor(todas.length / 10));
  const diez = todas.filter((_, i) => i % paso === 0).slice(0, 10);
  document.getElementById("lista-salud").innerHTML = `
    <table>
      <thead><tr><th>Pedido</th><th>Nota</th></tr></thead>
      <tbody>${diez.map((p) => `<tr><td>${escapar(p.id)}</td><td>${escapar(p.notas)}</td></tr>`).join("")}</tbody>
    </table>
    <p class="nota">Son 10 de ${todas.length}. ¿Tu agente clasificó <code>notas</code> como Sensible?</p>`;
}

/* ---------- Parada 3: medir ---------- */

function pintarRegla() {
  const regla = REGLAS[reglaActual];
  document.getElementById("regla-titulo").textContent = regla.titulo;
  document.getElementById("regla-meta").textContent = `Meta: ${regla.meta}%`;
  document.querySelectorAll(".regla").forEach((boton) => {
    boton.classList.toggle("activa", boton.dataset.regla === reglaActual);
  });

  const guardada = leerGuardado(`sql-${reglaActual}`) || "";
  document.getElementById("sql").value = guardada;
  document.getElementById("resultado-sql").innerHTML = "";
  document.getElementById("mensaje-sql").className = "mensaje";
  document.getElementById("mensaje-sql").textContent = "";
  if (solucionVisible) {
    verSolucion();
  } else {
    document.getElementById("solucion-sql")?.remove();
  }
}

function leerGuardado(clave) {
  try {
    return localStorage.getItem(clave);
  } catch {
    return null;
  }
}

function guardar(clave, valor) {
  try {
    localStorage.setItem(clave, valor);
  } catch {
    /* sin almacenamiento: no pasa nada */
  }
}

function distancia(a, b) {
  const m = a.length;
  const n = b.length;
  const tabla = Array.from({ length: m + 1 }, (_, i) => [i, ...Array(n).fill(0)]);
  for (let j = 1; j <= n; j += 1) tabla[0][j] = j;
  for (let i = 1; i <= m; i += 1) {
    for (let j = 1; j <= n; j += 1) {
      tabla[i][j] = Math.min(
        tabla[i - 1][j] + 1,
        tabla[i][j - 1] + 1,
        tabla[i - 1][j - 1] + (a[i - 1] === b[j - 1] ? 0 : 1)
      );
    }
  }
  return tabla[m][n];
}

const TODAS_LAS_COLUMNAS = [
  "id", "nombre", "email", "telefono", "carrera", "fecha_registro",
  "cliente_id", "fecha_pedido", "fecha_entrega", "estado", "monto",
  "notas", "version_app",
];

const ALIAS = {
  correo: "email",
  correos: "email",
  mail: "email",
  telefono_cliente: "telefono",
  celular: "telefono",
  monto_total: "monto",
  total: "monto",
  fecha: "fecha_pedido",
  fecha_entrega_pedido: "fecha_entrega",
  nombre_cliente: "nombre",
  id_cliente: "cliente_id",
  app: "version_app",
  version: "version_app",
};

function sugerirColumna(nombre) {
  const limpio = normalizar(nombre).replace(/[^a-z0-9_]/g, "");
  if (ALIAS[limpio]) return ALIAS[limpio];
  let mejor = null;
  let menor = Infinity;
  TODAS_LAS_COLUMNAS.forEach((columna) => {
    const d = distancia(limpio, columna);
    if (d < menor) {
      menor = d;
      mejor = columna;
    }
  });
  return menor <= 4 ? mejor : null;
}

function explicarError(mensaje) {
  const columna = mensaje.match(/no such column:?\s*([^\s]+)/i);
  if (columna) {
    const nombre = columna[1].replaceAll('"', "").replaceAll("`", "");
    const sugerida = sugerirColumna(nombre);
    if (sugerida) {
      return `No existe la columna \`${nombre}\`. Se llama \`${sugerida}\`.`;
    }
    return `No existe la columna \`${nombre}\`. Revisa la lista de columnas en “Ver tablas y columnas”.`;
  }
  const tabla = mensaje.match(/no such table:?\s*([^\s]+)/i);
  if (tabla) {
    return `No existe la tabla \`${tabla[1]}\`. Las tablas son \`clientes\`, \`pedidos\` y \`reglas\`.`;
  }
  if (/syntax error/i.test(mensaje)) {
    return "Hay un error de escritura en la consulta. Revisa comas, paréntesis y comillas.";
  }
  const funcion = mensaje.match(/no such function:?\s*([^\s]+)/i);
  if (funcion) {
    return `SQLite no tiene la función \`${funcion[1]}\`. Revisa el nombre.`;
  }
  return "La consulta no corrió. Revisa la escritura y vuelve a intentar.";
}

function mostrarMensaje(texto, clase = "") {
  const caja = document.getElementById("mensaje-sql");
  caja.textContent = texto;
  caja.className = "mensaje visible " + clase;
}

function pintarResultado(resultado) {
  const contenedor = document.getElementById("resultado-sql");
  if (!resultado) {
    contenedor.innerHTML = "";
    return;
  }
  const limite = Math.min(resultado.values.length, 30);
  const filas = resultado.values.slice(0, limite);
  contenedor.innerHTML = `
    <table>
      <thead><tr>${resultado.columns.map((c) => `<th>${escapar(c)}</th>`).join("")}</tr></thead>
      <tbody>
        ${filas
          .map(
            (fila) =>
              `<tr>${fila
                .map((v) => `<td class="num">${escapar(v)}</td>`)
                .join("")}</tr>`
          )
          .join("")}
      </tbody>
    </table>
    ${resultado.values.length > limite ? `<p class="nota">Se muestran ${limite} de ${resultado.values.length} filas.</p>` : ""}`;
}

function correrSQL() {
  if (!db) {
    mostrarMensaje("La base todavía no está lista. Espera un momento.", "error");
    return;
  }
  const sql = document.getElementById("sql").value.trim();
  if (!sql) {
    mostrarMensaje("Escribe una consulta primero.", "error");
    return;
  }
  if (/\b(drop|delete|update|insert|alter|create|replace|attach)\b/i.test(sql)) {
    mostrarMensaje("En este laboratorio las consultas solo leen. No modifiques los datos.", "error");
    return;
  }

  let resultadosSQL = [];
  try {
    resultadosSQL = db.exec(sql);
  } catch (error) {
    mostrarMensaje(explicarError(String(error.message || error)), "error");
    pintarResultado(null);
    return;
  }
  if (!resultadosSQL.length) {
    mostrarMensaje("La consulta no devolvió datos. Debe devolver un solo número: el porcentaje.", "error");
    pintarResultado(null);
    return;
  }

  const ultimo = resultadosSQL[resultadosSQL.length - 1];
  pintarResultado(ultimo);

  if (ultimo.columns.length !== 1) {
    mostrarMensaje(
      "La consulta devolvió varias columnas. Para el tablero necesito un solo número: el porcentaje.",
      "error"
    );
    return;
  }
  if (ultimo.values.length !== 1) {
    mostrarMensaje(
      `La consulta devolvió ${ultimo.values.length} filas. Para el tablero necesito un solo número: el porcentaje.`,
      "error"
    );
    return;
  }

  let valor = Number(ultimo.values[0][0]);
  if (!Number.isFinite(valor)) {
    mostrarMensaje("El resultado no es un número. La consulta debe devolver el porcentaje.", "error");
    return;
  }
  const pareceConteo =
    /\bCOUNT\s*\(\s*\*\s*\)/i.test(sql) &&
    !/\/\s*COUNT\s*\(/i.test(sql) &&
    !/\b100(\.0*)?\s*\*/i.test(sql);

  let convertido = false;
  if (pareceConteo) {
    mostrarMensaje(
      "Ese resultado es un conteo, no un porcentaje. Divide entre el total y multiplica por 100.",
      "error"
    );
    return;
  }
  if (valor >= 0 && valor <= 1 && !Number.isInteger(valor)) {
    valor *= 100;
    convertido = true;
  }
  if (valor < 0 || valor > 100) {
    mostrarMensaje(
      "El resultado no es un porcentaje entre 0 y 100. Si contaste fallas, divide entre el total y multiplica por 100.",
      "error"
    );
    return;
  }

  valor = Math.round(valor * 10) / 10;
  if (reglaActual === "R4") {
    resultados.R4[periodoR4] = valor;
  } else {
    resultados[reglaActual] = valor;
  }
  guardar(`sql-${reglaActual}`, sql);
  pintarTablero();

  const regla = REGLAS[reglaActual];
  const cumple = valor >= regla.meta;
  let texto = `La regla ${reglaActual} quedó en ${valor.toFixed(1)}%. Meta ${regla.meta}%. ${cumple ? "Cumple." : "No cumple."}`;
  if (convertido) texto += " Tomé el resultado como porcentaje.";
  if (reglaActual === "R1" && valor >= 93.5) {
    texto += " Ojo: esta consulta parece la ingenua. Deja pasar correos con dos arrobas o con espacios.";
  }
  mostrarMensaje(texto, cumple ? "bien" : "error");
}

function pintarTablero() {
  ["R1", "R2", "R3"].forEach((regla) => {
    const valor = resultados[regla];
    const tile = document.querySelector(`.tile[data-regla="${regla}"]`);
    const cajaValor = document.getElementById(`valor-${regla}`);
    const estado = document.getElementById(`estado-${regla}`);
    tile.classList.remove("cumple", "no-cumple");
    if (valor === null) {
      cajaValor.textContent = "—";
      estado.textContent = "Sin dato";
      return;
    }
    cajaValor.textContent = `${valor.toFixed(1)}%`;
    const cumple = valor >= REGLAS[regla].meta;
    estado.textContent = cumple ? "Cumple" : "No cumple";
    tile.classList.add(cumple ? "cumple" : "no-cumple");
  });

  const valorR4 = resultados.R4[periodoR4];
  const tileR4 = document.querySelector('.tile[data-regla="R4"]');
  const cajaR4 = document.getElementById("valor-R4");
  const estadoR4 = document.getElementById("estado-R4");
  tileR4.classList.remove("cumple", "no-cumple");
  document.getElementById("meta-R4").textContent =
    periodoR4 === "ultimos" ? "Meta 95% · últimos 14 días" : "Meta 95% · 14 días anteriores";
  if (valorR4 === null) {
    cajaR4.textContent = "—";
    estadoR4.textContent = "Sin dato";
  } else {
    cajaR4.textContent = `${valorR4.toFixed(1)}%`;
    const cumple = valorR4 >= REGLAS.R4.meta;
    estadoR4.textContent = cumple ? "Cumple" : "No cumple";
    tileR4.classList.add(cumple ? "cumple" : "no-cumple");
  }
}

function verSolucion() {
  solucionVisible = true;
  document.getElementById("solucion-sql")?.remove();
  const bloque = document.createElement("pre");
  bloque.id = "solucion-sql";
  bloque.className = "codigo";
  bloque.textContent = SOLUCIONES[reglaActual];
  const mensaje = document.getElementById("mensaje-sql");
  mensaje.before(bloque);
}

function actualizarRelojSolucion() {
  const boton = document.getElementById("ver-solucion");
  const reloj = document.getElementById("reloj-solucion");
  if (!boton) return;
  if (FACILITADOR) {
    boton.disabled = false;
    reloj.textContent = "Modo facilitador: disponible ahora.";
    return;
  }
  if (inicioParada3 === null) {
    boton.disabled = true;
    reloj.textContent = "La solución se activa a los 3 minutos.";
    return;
  }
  const segundos = Math.floor((Date.now() - inicioParada3) / 1000);
  const faltan = Math.max(0, 180 - segundos);
  if (faltan === 0) {
    boton.disabled = false;
    reloj.textContent = "";
    return;
  }
  boton.disabled = true;
  const minutos = Math.floor(faltan / 60);
  const resto = String(faltan % 60).padStart(2, "0");
  reloj.textContent = `La solución se activa en ${minutos}:${resto}.`;
}

/* ---------- Parada 4: rastrear ---------- */

function pintarLinaje() {
  const porId = Object.fromEntries((linaje.nodos || []).map((n) => [n.id, n]));
  const niveles = [
    ["app_repartidores", "app_clientes"],
    ["pedidos", "clientes"],
    ["regla_R4", "regla_R1", "regla_R2"],
    ["tablero"],
  ];

  document.getElementById("linaje").innerHTML = niveles
    .map((nivel, indice) => {
      const nodos = nivel
        .map((id) => {
          const nodo = porId[id];
          if (!nodo) return "";
          let clase = "";
          if (id.startsWith("app_")) clase = "fuente";
          else if (id.startsWith("regla_")) clase = "regla";
          else if (id === "tablero") clase = "tablero";
          return `<article class="nodo ${clase}" data-nodo="${escapar(id)}">
            <h3>${escapar(nodo.nombre)}</h3>
            <p class="dueno">Dueño: ${escapar(nodo.dueno)}</p>
            <p>${escapar(nodo.frase)}</p>
          </article>`;
        })
        .join("");
      const flecha = indice < niveles.length - 1 ? '<div class="flecha">↓</div>' : "";
      return `<div class="nivel">${nodos}</div>${flecha}`;
    })
    .join("");
}

function correrLinaje() {
  if (!db) {
    document.getElementById("conclusion-linaje").hidden = false;
    document.getElementById("conclusion-linaje").textContent = "La base todavía no está lista.";
    return;
  }
  let resultado;
  try {
    const salida = db.exec(CONSULTA_LINAJE);
    resultado = salida[0];
  } catch (error) {
    document.getElementById("resultado-linaje").innerHTML = "";
    const caja = document.getElementById("conclusion-linaje");
    caja.hidden = false;
    caja.textContent = explicarError(String(error.message || error));
    return;
  }

  const contenedor = document.getElementById("resultado-linaje");
  if (!resultado) {
    contenedor.innerHTML = "";
    return;
  }
  contenedor.innerHTML = `
    <table>
      <thead><tr>${resultado.columns.map((c) => `<th>${escapar(c)}</th>`).join("")}</tr></thead>
      <tbody>
        ${resultado.values
          .map(
            (fila) =>
              `<tr>${fila.map((v) => `<td class="num">${escapar(v)}</td>`).join("")}</tr>`
          )
          .join("")}
      </tbody>
    </table>`;

  const iVersion = resultado.columns.indexOf("version_app");
  const iFallas = resultado.columns.indexOf("entregas_sin_fecha");
  let total = 0;
  let v23 = 0;
  resultado.values.forEach((fila) => {
    const fallas = Number(fila[iFallas]);
    total += fallas;
    if (fila[iVersion] === "2.3") v23 += fallas;
  });

  const causa = document.querySelector('.nodo[data-nodo="app_repartidores"]');
  causa?.classList.remove("causa");
  const caja = document.getElementById("conclusion-linaje");
  caja.hidden = false;
  if (total > 0 && v23 / total > 0.85) {
    causa?.classList.add("causa");
    caja.className = "conclusion";
    caja.textContent = `${v23} de ${total} entregas sin fecha vienen de la versión 2.3. La causa está en app_repartidores, que es de Tecnología.`;
  } else {
    caja.className = "conclusion";
    caja.textContent = `${v23} de ${total} entregas sin fecha vienen de la versión 2.3. La versión 2.3 no explica la mayoría.`;
  }
}

/* ---------- Parada 5: contar ---------- */

function contarPalabras(texto) {
  return texto.trim() ? texto.trim().split(/\s+/).length : 0;
}

function valoresDelTablero() {
  const valores = new Set([95, 99]);
  ["R1", "R2", "R3"].forEach((r) => {
    if (resultados[r] !== null) valores.add(Number(resultados[r].toFixed(1)));
  });
  if (resultados.R4.ultimos !== null) valores.add(Number(resultados.R4.ultimos.toFixed(1)));
  if (resultados.R4.anteriores !== null) valores.add(Number(resultados.R4.anteriores.toFixed(1)));
  if (FACILITADOR) {
    [91, 82, 99.4, 96, 99].forEach((v) => valores.add(v));
  }
  return valores;
}

function revisarMensaje() {
  const texto = document.getElementById("mensaje-mariana").value;
  const caja = document.getElementById("respuesta-revision");
  if (!texto.trim()) {
    caja.className = "mensaje visible error";
    caja.textContent = "Escribe primero el mensaje.";
    return;
  }

  const palabras = contarPalabras(texto);
  const numeros = (texto.match(/\d+(?:\.\d+)?/g) || []).map(Number).filter((n) => n >= 50);
  const permitidos = valoresDelTablero();
  const fuera = numeros.filter((n) => !permitidos.has(Number(n.toFixed(1))));
  const pide = /(revis|corrig|arregl|prioriz|asign|pide|pedir|decide|decid|actualiz|confirma|aprueba|autoriza|manda|solicita|agenda)/i.test(texto);
  const marcas = ["check-corto", "check-numeros", "check-peticion"].map(
    (id) => document.getElementById(id).checked
  );

  const partes = [];
  partes.push(palabras <= 120 ? `Corto: ${palabras} palabras.` : `Largo: ${palabras} palabras. Recorta a 120 o menos.`);
  partes.push(
    fuera.length === 0
      ? "Los números que usas están en el tablero."
      : `Estos números no están en el tablero: ${fuera.join(", ")}.`
  );
  partes.push(pide ? "Pide algo concreto." : "No veo una petición concreta. Pide revisar, corregir o asignar algo.");
  if (!marcas.every(Boolean)) {
    partes.push("Falta marcar alguna casilla de la lista.");
  }

  const todoBien = palabras <= 120 && fuera.length === 0 && pide && marcas.every(Boolean);
  caja.className = "mensaje visible " + (todoBien ? "bien" : "error");
  caja.textContent = partes.join(" ") + (todoBien ? " El mensaje tiene lo necesario." : "");
}

/* ---------- Navegación y arranque ---------- */

function activarParada(numero) {
  document.querySelectorAll(".parada").forEach((seccion) => {
    seccion.classList.toggle("activa", seccion.id === `parada-${numero}`);
  });
  document.querySelectorAll(".parada-boton").forEach((boton) => {
    boton.classList.toggle("activa", boton.dataset.parada === String(numero));
  });
  if (numero === "3" && inicioParada3 === null) {
    inicioParada3 = Date.now();
    actualizarRelojSolucion();
  }
}

function conectarEventos() {
  document.querySelectorAll(".parada-boton").forEach((boton) => {
    boton.addEventListener("click", () => activarParada(boton.dataset.parada));
  });

  document.getElementById("revisar-diccionario").addEventListener("click", revisarDiccionario);

  document.getElementById("buscar-nota").addEventListener("input", buscarNotas);
  document.getElementById("ver-salud").addEventListener("click", verNotasSalud);
  document.getElementById("ver-respuestas").addEventListener("click", () => {
    document.body.classList.toggle("ver-respuestas");
  });

  document.querySelectorAll(".regla").forEach((boton) => {
    boton.addEventListener("click", () => {
      reglaActual = boton.dataset.regla;
      pintarRegla();
    });
  });

  document.getElementById("correr-sql").addEventListener("click", correrSQL);
  document.getElementById("ver-solucion").addEventListener("click", verSolucion);
  document.getElementById("sql").addEventListener("keydown", (evento) => {
    if ((evento.ctrlKey || evento.metaKey) && evento.key === "Enter") {
      evento.preventDefault();
      correrSQL();
    }
  });

  document.querySelectorAll(".periodo-boton").forEach((boton) => {
    boton.addEventListener("click", () => {
      periodoR4 = boton.dataset.periodo;
      document.querySelectorAll(".periodo-boton").forEach((b) => {
        b.classList.toggle("activa", b === boton);
      });
      pintarTablero();
    });
  });

  document.getElementById("correr-linaje").addEventListener("click", correrLinaje);

  document.getElementById("mensaje-mariana").addEventListener("input", () => {
    document.getElementById("conteo-palabras").textContent = contarPalabras(
      document.getElementById("mensaje-mariana").value
    );
  });
  document.getElementById("revisar-mensaje").addEventListener("click", revisarMensaje);

  setInterval(actualizarRelojSolucion, 1000);
}

async function iniciar() {
  if (FACILITADOR) document.body.classList.add("facilitador");

  pintarCatalogo();
  pintarColumnasClasificadas();
  contarAciertos();
  pintarLinaje();
  document.getElementById("consulta-linaje").textContent = CONSULTA_LINAJE;
  pintarRegla();
  pintarTablero();
  conectarEventos();
  actualizarRelojSolucion();

  if (FACILITADOR) {
    resultados.R1 = 91;
    resultados.R2 = 82;
    resultados.R3 = 99.4;
    resultados.R4.ultimos = 96;
    resultados.R4.anteriores = 99;
    pintarTablero();
  }

  await iniciarBase();
}

iniciar();
