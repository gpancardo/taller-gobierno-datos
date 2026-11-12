// Captura el laboratorio real paso a paso. Uso: node capturar.mjs
import puppeteer from "puppeteer-core";
import { readFileSync, mkdirSync } from "node:fs";
import { fileURLToPath } from "node:url";
import path from "node:path";

const aqui = path.dirname(fileURLToPath(import.meta.url));
const lab = path.resolve(aqui, "../../laboratorio/index.html");
const salida = path.join(aqui, "capturas");
mkdirSync(salida, { recursive: true });
const pasos = JSON.parse(readFileSync(path.join(aqui, "pasos.json"), "utf8"));
const rotulos = Object.fromEntries(pasos.map((p) => [p.id, p.rotulo]));

const MENSAJE = "Mariana: el correo cumple 91% y el teléfono 82%; la meta de ambos es 95%. " +
  "La entrega con fecha (R4) bajó de 99% a 96% porque la versión 2.3 de la app de repartidores no guarda la fecha. " +
  "Te pido que Operaciones revise esa versión esta semana.";

const navegador = await puppeteer.launch({
  executablePath: "/usr/bin/google-chrome",
  args: ["--no-sandbox"],
  defaultViewport: { width: 1920, height: 1080 },
});
const page = await navegador.newPage();
const errores = [];
page.on("pageerror", (e) => errores.push(String(e)));
page.on("console", (m) => m.type() === "error" && errores.push(m.text()));
await page.goto("file://" + lab);
await page.waitForFunction(() => typeof db !== "undefined" && db, { timeout: 20000 });

const esperar = (ms) => new Promise((r) => setTimeout(r, ms));
const tab = (n) => page.click(`.parada-boton[data-parada="${n}"]`);
const ir = (sel) => page.evaluate((s) => document.querySelector(s).scrollIntoView({ block: "start" }), sel);
const arriba = () => page.evaluate(() => window.scrollTo(0, 0));
const escribirSQL = async (texto) => {
  await page.evaluate((t) => { document.getElementById("sql").value = t; }, texto);
};
const correr = async () => { await page.click("#correr-sql"); await esperar(400); };
const soluciones = () => page.evaluate(() => SOLUCIONES);

async function foto(id) {
  await page.evaluate((r) => {
    document.getElementById("rotulo-video")?.remove();
    const b = document.createElement("div");
    b.id = "rotulo-video";
    b.textContent = r;
    b.style.cssText = "position:fixed;left:0;bottom:0;right:0;padding:14px 40px;background:#0E1A4F;" +
      "color:#fff;font:56px 'League Gothic',sans-serif;letter-spacing:.03em;text-transform:uppercase;z-index:99";
    document.body.appendChild(b);
  }, rotulos[id]);
  await esperar(250);
  await page.screenshot({ path: path.join(salida, `${id}.png`) });
  console.log("captura", id);
}

// Parada 1
await foto("inicio");
await tab(1); await esperar(300); await arriba(); await foto("p1_tarea");
await ir("#columnas-fichas"); await foto("p1_fichas");
await page.evaluate(() => {
  document.getElementById("diccionario").value =
    "# Diccionario\n\n## pedidos\n- monto: lo que paga el cliente, en pesos mexicanos.\n- version_app: versión de la app de clientes.\n- notas: texto libre del cliente.";
});
for (const col of ["monto", "version_app"]) {
  await page.evaluate((c) => {
    const el = [...document.querySelectorAll("#casillas-diccionario label")].find((l) => l.textContent.includes(c));
    el?.querySelector("input")?.click();
  }, col);
}
await ir("#diccionario"); await foto("p1_revisar");

// Parada 2
await tab(2); await esperar(300); await arriba(); await foto("p2_tarea");
await page.type("#buscar-nota", "alergia");
await page.click("#ver-salud");
await esperar(300); await ir("#buscar-nota"); await foto("p2_notas");
await page.evaluate(() => document.querySelectorAll(".acierto").forEach((c, i) => { if (i !== 12) c.click(); }));
await page.click("#ver-respuestas");
await esperar(300); await ir("#tabla-columnas"); await foto("p2_respuestas");

// Parada 3
await tab(3); await esperar(300); await arriba();
await escribirSQL("SELECT ROUND(100.0 * SUM(CASE WHEN email LIKE '%_@_%._%' THEN 1 ELSE 0 END) / COUNT(*), 1) AS porcentaje\nFROM clientes;");
await correr(); await foto("p3_ingenua");
const S = await soluciones();
await escribirSQL(S.R1); await correr(); await foto("p3_corregida");
for (const r of ["R2", "R3", "R4"]) {
  await page.click(`.regla[data-regla="${r}"]`);
  await escribirSQL(S[r]); await correr();
}
await ir("#tablero"); await foto("p3_tablero");
await page.click('.periodo-boton[data-periodo="anteriores"]'); await esperar(300);
await foto("p3_periodo");

// Parada 4
await tab(4); await esperar(300); await arriba(); await foto("p4_linaje");
await page.click("#correr-linaje"); await esperar(500);
await ir("#correr-linaje"); await foto("p4_causa");

// Parada 5
await tab(5); await esperar(300); await arriba();
await page.evaluate((m) => {
  const t = document.getElementById("mensaje-mariana");
  t.value = m; t.dispatchEvent(new Event("input"));
}, MENSAJE);
await foto("p5_mensaje");
for (const id of ["check-corto", "check-numeros", "check-peticion"]) await page.click("#" + id);
await page.click("#revisar-mensaje");
await esperar(300); await foto("p5_revisar");

// Cierre
await tab(1); await arriba(); await foto("cierre");

await navegador.close();
if (errores.length) { console.log("ERRORES EN CONSOLA:\n" + errores.join("\n")); process.exit(1); }
console.log("sin errores en consola");
