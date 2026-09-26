// Corre programas de TortuGame con el intérprete JS: lee [{arbol, semilla, entradas}] por stdin y escribe los
// resultados por stdout. Lo usa tests/test_tortugame.py para comparar con la implementación de Python.
import { readFileSync } from "node:fs";
import vm from "node:vm";

const codigo = readFileSync(new URL("../../web/static/js/tortugame/interprete.js", import.meta.url), "utf8");
const contexto = { Math, Object, Number, String, Array, Map, Set, Error, RangeError, JSON };
vm.createContext(contexto);
vm.runInContext(codigo, contexto);
const pedidos = JSON.parse(readFileSync(0, "utf8"));
const salida = pedidos.map((p) => contexto.TortuGame.ejecutar(p.arbol, { semilla: p.semilla, entradas: p.entradas || [] }));
process.stdout.write(JSON.stringify(salida));
