// Ejecuta de verdad web/static/js/tortuga.js (sin navegador) con un canvas falso que anota los colores.
// Lo corre tests/test_js.py (se saltea si no hay Node). Solo módulos de Node: sin dependencias.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";

const CODIGO = readFileSync(new URL("../../web/static/js/tortuga.js", import.meta.url), "utf8");

function cargar(colorTortuga) {
  const dataset = colorTortuga ? { colorTortuga } : {};
  const contexto = { document: { documentElement: { dataset }, getElementById: () => null }, Math, Object };
  vm.createContext(contexto);
  vm.runInContext(CODIGO + "\n;globalThis.Lienzo = Lienzo;", contexto);
  return contexto.Lienzo;
}

/** Un contexto 2D que anota cada fillStyle y strokeStyle que se usa para pintar. */
function canvasFalso() {
  const usados = { rellenos: [], trazos: [] };
  const ctx = new Proxy({}, {
    get: (obj, prop) => (prop in obj ? obj[prop] : () => {}),
    set: (obj, prop, valor) => {
      if (prop === "fillStyle") usados.rellenos.push(valor);
      if (prop === "strokeStyle") usados.trazos.push(valor);
      obj[prop] = valor; return true;
    },
  });
  return { canvas: { getContext: () => ctx }, usados };
}

test("el cuerpo usa el color del nivel y el lápiz arranca verde", () => {
  const Lienzo = cargar("#2563eb");
  const { canvas, usados } = canvasFalso();
  Lienzo.crear(canvas).dibujar([{ o: "avanzar", v: 50, l: 1 }]);
  assert.ok(usados.rellenos.includes("#2563eb"), "el cuerpo se pinta con el color del nivel");
  assert.ok(usados.trazos.includes("#16a34a"), "la línea se pinta con el lápiz verde");
});

test("color cambia el lápiz, no el cuerpo", () => {
  const Lienzo = cargar("#2563eb");
  const { canvas, usados } = canvasFalso();
  Lienzo.crear(canvas).dibujar([{ o: "color", v: "red", l: 1 }, { o: "avanzar", v: 50, l: 2 }]);
  assert.ok(usados.trazos.includes("red"));
  assert.ok(usados.rellenos.includes("#2563eb"));
  assert.ok(!usados.rellenos.includes("red"), "el cuerpo no toma el color del lápiz");
});

test("sin color de nivel, el cuerpo es verde", () => {
  const Lienzo = cargar(null);
  const { canvas, usados } = canvasFalso();
  Lienzo.crear(canvas).dibujar([{ o: "avanzar", v: 10, l: 1 }]);
  assert.ok(usados.rellenos.includes("#16a34a"));
});

test("el estado del lápiz: arranca verde y abajo; color y subir_lapiz lo cambian", () => {
  const Lienzo = cargar(null);
  const e = Lienzo.nuevoEstado();
  assert.equal(e.color, "#16a34a");
  Lienzo.aplicar(e, { o: "color", v: "blue" });
  Lienzo.aplicar(e, { o: "subir_lapiz" });
  Lienzo.aplicar(e, { o: "avanzar", v: 30 });
  assert.equal(e.color, "blue");
  assert.equal(e.trazos.length, 0, "con el lápiz arriba no deja línea");
});

test("el laberinto se dibuja con paredes grises y la vista lo encuadra entero", () => {
  const Lienzo = cargar(null);
  const lab = { paredes: [[-30, 30, -30, -130], [30, 30, 30, -130]], salida: [0, -100] };
  const vista = Lienzo.vistaLaberinto(lab);
  assert.equal(vista.cx, 0);
  assert.equal(vista.cy, -50);
  const { canvas, usados } = canvasFalso();
  const lienzo = Lienzo.crear(canvas);
  lienzo.usarLaberinto(lab);
  assert.ok(usados.trazos.includes("#6b7280"));
});
