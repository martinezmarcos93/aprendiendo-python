// Seguridad del intérprete TortuGame (docs/experimental/MODELO_DE_AMENAZAS_RUNTIME_JUEGOS.md, A1–A9).
// Se le da JSON armado a mano, como si alguien se salteara al servidor: nada debe escaparse ni colgarse.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";

const CODIGO = readFileSync(new URL("../../web/static/js/tortugame/interprete.js", import.meta.url), "utf8");
function cargar() {
  const contexto = { Math, Object, Number, String, Array, Map, Set, Error, RangeError, JSON };
  vm.createContext(contexto);
  vm.runInContext(CODIGO, contexto);
  return contexto.TortuGame;
}
const TG = cargar();
const programa = (...cuerpo) => ({ k: "programa", cuerpo });
const expr = (e, l = 1) => ({ k: "expr", e, l });
const llamar = (f, ...args) => ({ k: "llamar", f, args });
const texto = (v) => ({ k: "texto", v });
const num = (v) => ({ k: "num", v });
const correr = (arbol) => TG.ejecutar(arbol, { semilla: 1 });

test("A1: el intérprete no contiene eval, Function, red ni importScripts", () => {
  const sinComentarios = CODIGO.replace(/\/\*[\s\S]*?\*\//g, "").replace(/\/\/.*$/gm, "");
  for (const prohibido of ["eval(", "new Function", "Function(", "fetch(", "XMLHttpRequest", "WebSocket", "importScripts",
    "localStorage", "indexedDB", "document.", "setTimeout(\"", "innerHTML"]) {
    assert.ok(!sinComentarios.includes(prohibido), `no debe aparecer ${prohibido}`);
  }
});

test("A2: nombres del prototipo de JS no existen para el juego", () => {
  for (const nombre of ["constructor", "__proto__", "toString", "hasOwnProperty", "valueOf", "prototype"]) {
    const r = correr(programa(expr(llamar(nombre))));
    assert.equal(r.error, true, nombre);
    assert.match(r.mensaje, /Nombre desconocido/);
  }
});

test("A2: atributos y métodos fuera de la lista blanca se rechazan", () => {
  const heroe = { k: "asignar", d: { k: "var", id: "h" }, e: llamar("heroe", texto("A"), num(10), num(1)), l: 1 };
  for (const a of ["constructor", "__proto__", "prototype", "x"]) {
    const r = correr(programa(heroe, expr({ k: "attr", o: { k: "var", id: "h" }, a }, 2)));
    assert.equal(r.error, true, a);
  }
  for (const m of ["constructor", "map", "splice", "__proto__"]) {
    const r = correr(programa(expr({ k: "metodo", o: { k: "lista", vs: [] }, m, args: [] })));
    assert.equal(r.error, true, m);
  }
  const r = correr(programa(heroe, { k: "asignar", d: { k: "attr", o: { k: "var", id: "h" }, a: "__proto__" }, e: num(1), l: 2 }));
  assert.equal(r.error, true);
});

test("nodos desconocidos o mal formados dan error, no se ejecutan", () => {
  for (const arbol of [programa({ k: "eval", l: 1 }), programa(expr({ k: "js", codigo: "1" })), { k: "otro" }, null, programa(null)]) {
    const r = correr(arbol);
    assert.equal(r.error, true);
  }
});

test("A7: un bucle infinito se frena", () => {
  const r = correr(programa({ k: "mientras", c: { k: "const", v: true }, cuerpo: [{ k: "nada", l: 2 }], l: 1 }));
  assert.equal(r.error, true);
  assert.match(r.mensaje, /no termina nunca/);
});

test("A7: una función que se llama sin parar se frena", () => {
  const f = { k: "funcion", nombre: "f", params: [], locales: [], cuerpo: [{ k: "devolver", e: llamar("f"), l: 2 }], l: 1 };
  const r = correr(programa(f, expr(llamar("f"), 3)));
  assert.equal(r.error, true);
  assert.match(r.mensaje, /se llama a sí misma/);
});

test("A8: listas y textos gigantes se frenan", () => {
  const lista = correr(programa(expr({ k: "op", op: "*", a: { k: "lista", vs: [num(0)] }, b: num(10 ** 7) })));
  assert.equal(lista.error, true);
  const textoLargo = correr(programa(expr({ k: "op", op: "*", a: texto("ja"), b: num(10 ** 7) })));
  assert.equal(textoLargo.error, true);
  const grande = correr(programa(expr({ k: "op", op: "**", a: num(10), b: num(100) })));
  assert.equal(grande.error, true);
});

test("A9: demasiados personajes o eventos se frenan", () => {
  const muchos = { k: "para", var: "i", iter: llamar("range", num(60)),
    cuerpo: [expr(llamar("enemigo", texto("E"), num(1), num(1)), 2)], l: 1 };
  assert.equal(correr(programa(muchos)).error, true);
  const hablar = { k: "mientras", c: { k: "const", v: true }, l: 1,
    cuerpo: [expr(llamar("print", texto("x")), 2)] };
  const r = correr(programa(hablar));
  assert.equal(r.error, true);
  assert.ok(r.eventos.length <= TG.TOPES.eventos);
});

test("A5: los textos del juego llegan como datos, sin interpretar", () => {
  const r = correr(programa(expr(llamar("print", texto("<img src=x onerror=alert(1)>")))));
  assert.equal(r.eventos[0].texto, "<img src=x onerror=alert(1)>");
});

test("el resultado es solo datos (se puede serializar y no trae funciones)", () => {
  const h = { k: "asignar", d: { k: "var", id: "h" }, e: llamar("heroe", texto("A"), num(10), num(1)), l: 1 };
  const r = correr(programa(h, expr(llamar("print", { k: "var", id: "h" }), 2)));
  const copia = JSON.stringify(r);
  assert.equal(JSON.stringify(JSON.parse(copia)), copia);
  assert.ok(!copia.includes("function"));
});
