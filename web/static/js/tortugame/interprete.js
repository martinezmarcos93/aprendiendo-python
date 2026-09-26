/* TortuGame v1: intérprete del árbol JSON que arma el servidor (tortuscript/juego_ast.py). ADR-006/007/008/009.
 *
 * - No hay eval, new Function ni JavaScript generado: se recorre el árbol y solo existe lo que está acá.
 * - Corre dentro de un Web Worker (en el navegador) o en Node (tests). No toca la página, la red ni el almacenamiento.
 * - Imita a Python en lo que usan los juegos y produce el MISMO registro de eventos que tortuscript/tortugame.py
 *   (lo exigen los tests de conformidad). El azar es mulberry32 con semilla, igual en los dos.
 */
"use strict";
(function (raiz) {
  const LUGARES = ["aldea", "bosque", "cueva", "mazmorra", "castillo"];
  const COLUMNAS = 8, FILAS = 5;
  const TOPES = { pasos: 200000, personajes: 50, eventos: 2000, texto: 2000, nombre: 40, inventario: 100,
                  lista: 10000, profundidad: 100, vida: 10000, fuerza: 1000, caras: 1000 };
  const MAX_ENTERO = Number.MAX_SAFE_INTEGER;

  // ───────────────────────── errores (mismos títulos que tortuscript/error_handler.py) ─────────────────────────
  class ErrorDelChico extends Error {
    constructor(tipo, detalle) { super(detalle || tipo); this.tipo = tipo; this.detalle = detalle || ""; }
  }
  class Pregunta { constructor(texto) { this.texto = texto; } }
  const err = (tipo, detalle) => new ErrorDelChico(tipo, detalle);
  const juego = (detalle) => err("ErrorJuego", detalle);

  const MENSAJES = {
    NameError: (d) => `❌ Nombre desconocido\n\nUsaste «${d}», pero no existe todavía.\n\n💡 Revisá:\n- ¿Creaste «${d}» antes con  ${d} es ...?\n- ¿Está escrito exactamente igual (mayúsculas incluidas)?\n- Si es texto, ¿le faltan las comillas?`,
    TypeError: (d) => d === "mezcla" ? "❌ Estás mezclando texto con números\n\n💡 \"Tengo \" + 12  ❌   →   \"Tengo \" + str(12)  ✅\n   Y si el número vino de preguntar, convertilo con int(...)"
      : "❌ Error de tipo\n\nEstás usando un dato de una forma que no corresponde.\n\n💡 Revisá qué tipo de dato tiene cada variable (texto, número, lista).",
    ZeroDivisionError: () => "❌ División por cero\n\nNo se puede dividir por 0.\n\n💡 Revisá el número de abajo de la división.",
    ValueError: () => "❌ Valor incorrecto\n\nIntentaste convertir algo que no se puede, como int(\"hola\").\n\n💡 Si pediste un número con preguntar, escribí solo dígitos.",
    IndexError: () => "❌ Posición fuera de la lista\n\nPediste un elemento que no existe. Ojo: las listas empiezan en 0.",
    AttributeError: () => "❌ Eso no tiene esa propiedad\n\nEl dato no tiene lo que buscaste después del punto.",
    BucleInfinito: () => "🔁 Tu programa no termina nunca\n\n💡 ¿Hay un mientras cuya condición no deja de cumplirse?",
    Recursion: () => "🌀 Una función se llama a sí misma sin parar\n\n💡 Toda función que se llama a sí misma necesita un caso en el que se detenga.",
    Grande: (d) => `📏 Eso es demasiado grande\n\n${d}`,
    ErrorJuego: (d) => `🎮 El juego no entendió\n\n${d}`,
  };
  function mensaje(e, linea) {
    const texto = (MENSAJES[e.tipo] || MENSAJES.TypeError)(e.detalle);
    return linea ? `${texto}\n\n📍 Mirá la línea ${linea}` : texto;
  }

  // ───────────────────────── azar: mulberry32 (igual que Azar en tortugame.py) ─────────────────────────
  function crearAzar(semilla) {
    let a = semilla >>> 0;
    const siguiente = () => {
      a = (a + 0x6D2B79F5) >>> 0;
      let t = Math.imul(a ^ (a >>> 15), 1 | a) >>> 0;
      t = (((t + (Math.imul(t ^ (t >>> 7), 61 | t) >>> 0)) >>> 0) ^ t) >>> 0;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
    return { siguiente, dado: (caras) => Math.floor(siguiente() * caras) + 1 };
  }

  // ───────────────────────── valores con reglas de Python ─────────────────────────
  class Flotante { constructor(v) { this.v = v; } }            // un float de Python (los int son number de JS)
  class Personaje {                                            // sin prototipo compartido con nada del chico
    constructor(p) { Object.assign(this, p); Object.seal(this); }
  }
  const esEntero = (x) => typeof x === "number";
  const esNumero = (x) => typeof x === "number" || x instanceof Flotante || typeof x === "boolean";
  const aNumero = (x) => (x instanceof Flotante ? x.v : x === true ? 1 : x === false ? 0 : x);
  const esLista = (x) => Array.isArray(x);
  function entero(v) {
    if (!Number.isSafeInteger(v)) throw err("Grande", "Ese número es demasiado grande para un juego.");
    return v;
  }

  function reprFlotante(v) {
    if (Number.isNaN(v)) return "nan";
    if (!Number.isFinite(v)) return v > 0 ? "inf" : "-inf";
    const abs = Math.abs(v);
    if (v !== 0 && (abs >= 1e16 || abs < 1e-4)) {
      const [m, e] = v.toExponential().split("e");
      const signo = e[0] === "-" ? "-" : "+", digitos = e.replace(/^[+-]/, "");
      return `${m}e${signo}${digitos.padStart(2, "0")}`;
    }
    return Number.isInteger(v) ? `${v}.0` : String(v);
  }
  function reprTexto(s) {
    const comilla = s.includes("'") && !s.includes('"') ? '"' : "'";
    let salida = "";
    for (const c of s) {
      if (c === "\\") salida += "\\\\";
      else if (c === comilla) salida += "\\" + c;
      else if (c === "\n") salida += "\\n";
      else if (c === "\t") salida += "\\t";
      else salida += c;
    }
    return comilla + salida + comilla;
  }
  function repr(x) {
    if (typeof x === "string") return reprTexto(x);
    return comoTexto(x);
  }
  function comoTexto(x) {                                        // str() de Python
    if (x === null || x === undefined) return "None";
    if (x === true) return "True";
    if (x === false) return "False";
    if (typeof x === "number") return String(x);
    if (x instanceof Flotante) return reprFlotante(x.v);
    if (typeof x === "string") return x;
    if (esLista(x)) return "[" + x.map(repr).join(", ") + "]";
    if (x instanceof Personaje) return x.nombre;
    if (x && x.esFuncion) return `<function ${x.nombre}>`;
    return String(x);
  }
  function verdadero(x) {
    if (x === null || x === undefined || x === false || x === 0 || x === "") return false;
    if (x instanceof Flotante) return x.v !== 0;
    if (esLista(x)) return x.length > 0;
    return true;
  }
  function igual(a, b) {
    if (esNumero(a) && esNumero(b)) return aNumero(a) === aNumero(b);
    if (esLista(a) && esLista(b)) return a.length === b.length && a.every((v, i) => igual(v, b[i]));
    if (a === null || a === undefined) return b === null || b === undefined;
    return a === b;
  }
  function numeroResultado(v, flotante) {
    return flotante ? new Flotante(v) : entero(v);
  }
  function operar(op, a, b) {
    if (op === "+") {
      if (typeof a === "string" && typeof b === "string") return limitarTexto(a + b);
      if (esLista(a) && esLista(b)) return limitarLista(a.concat(b));
      if (typeof a === "string" || typeof b === "string") throw err("TypeError", "mezcla");
    }
    if (op === "*") {
      const texto = typeof a === "string" ? [a, b] : typeof b === "string" ? [b, a] : null;
      if (texto) {
        if (!esEntero(texto[1])) throw err("TypeError");
        if (texto[1] <= 0) return "";
        if (texto[0].length * texto[1] > TOPES.texto * 50) throw err("Grande", "Ese texto es demasiado largo.");
        return texto[0].repeat(texto[1]);
      }
      const lista = esLista(a) ? [a, b] : esLista(b) ? [b, a] : null;
      if (lista) {
        if (!esEntero(lista[1])) throw err("TypeError");
        let r = [];
        for (let i = 0; i < lista[1]; i++) { r = r.concat(lista[0]); limitarLista(r); }
        return r;
      }
    }
    if (!esNumero(a) || !esNumero(b)) throw err("TypeError", typeof a === "string" || typeof b === "string" ? "mezcla" : "");
    const x = aNumero(a), y = aNumero(b);
    const flot = a instanceof Flotante || b instanceof Flotante;
    switch (op) {
      case "+": return numeroResultado(x + y, flot);
      case "-": return numeroResultado(x - y, flot);
      case "*": return numeroResultado(x * y, flot);
      case "/": if (y === 0) throw err("ZeroDivisionError"); return new Flotante(x / y);
      case "//": if (y === 0) throw err("ZeroDivisionError"); return numeroResultado(Math.floor(x / y), flot);
      case "%": {
        if (y === 0) throw err("ZeroDivisionError");
        const r = x - y * Math.floor(x / y);
        return numeroResultado(flot ? r : Math.round(r), flot);
      }
      case "**": {
        if (!flot && y >= 0) return entero(x ** y);
        return new Flotante(x ** y);
      }
    }
    throw err("TypeError");
  }
  function comparar(op, a, b) {
    switch (op) {
      case "==": return igual(a, b);
      case "!=": return !igual(a, b);
      case "in": case "not in": {
        let esta;
        if (typeof b === "string") { if (typeof a !== "string") throw err("TypeError"); esta = b.includes(a); }
        else if (esLista(b)) esta = b.some((v) => igual(v, a));
        else throw err("TypeError");
        return op === "in" ? esta : !esta;
      }
    }
    let x = a, y = b;
    if (esNumero(a) && esNumero(b)) { x = aNumero(a); y = aNumero(b); }
    else if (!(typeof a === "string" && typeof b === "string")) throw err("TypeError");
    switch (op) {
      case "<": return x < y;
      case "<=": return x <= y;
      case ">": return x > y;
      case ">=": return x >= y;
    }
    throw err("TypeError");
  }
  function limitarTexto(s) {
    if (s.length > TOPES.texto * 50) throw err("Grande", "Ese texto es demasiado largo.");
    return s;
  }
  function limitarLista(l) {
    if (l.length > TOPES.lista) throw err("Grande", `Una lista puede tener hasta ${TOPES.lista} cosas.`);
    return l;
  }

  // ───────────────────────── validación de datos de la API (como _texto / _numero en Python) ─────────────────────────
  function texto(v, que, maximo = TOPES.texto) {
    if (typeof v !== "string") throw juego(`${que} tiene que ser un texto, entre comillas.`);
    if (!v.trim()) throw juego(`${que} no puede estar vacío.`);
    if ([...v].length > maximo) throw juego(`${que} es muy largo (máximo ${maximo} letras).`);
    return v;
  }
  function numero(v, que, min, max) {
    if (typeof v !== "number") throw juego(`${que} tiene que ser un número entero, por ejemplo 10.`);
    if (v < min || v > max) throw juego(`${que} tiene que estar entre ${min} y ${max}.`);
    return v;
  }

  // ───────────────────────── la partida ─────────────────────────
  function ejecutar(arbol, opciones = {}) {
    const azar = crearAzar(opciones.semilla || 0);
    const entradas = [...(opciones.entradas || [])];
    const vacio = Boolean(opciones.completarConVacio);
    const eventos = [];
    const personajes = [];
    let heroeCreado = false, terminado = false, linea = 0, pasos = 0, profundidad = 0;

    const anotar = (t, datos) => {
      if (terminado) return;
      if (eventos.length >= TOPES.eventos) throw juego("Tu juego hizo demasiadas cosas y lo frené. ¿Hay un mientras que no termina?");
      eventos.push({ t, ...datos, l: linea });
    };
    const persona = (x, que = "Eso") => {
      if (!(x instanceof Personaje)) throw juego(`${que} tiene que ser un personaje (creado con heroe o enemigo).`);
      return x;
    };
    function crear(tipo, nombre, vida, fuerza) {
      if (personajes.length >= TOPES.personajes) throw juego(`Tu juego ya tiene ${TOPES.personajes} personajes: no entran más.`);
      nombre = texto(nombre, "El nombre", TOPES.nombre);
      vida = numero(vida, "La vida", 1, TOPES.vida);
      fuerza = numero(fuerza, "La fuerza", 0, TOPES.fuerza);
      let x = 1, y = 2;
      if (tipo === "enemigo") {
        const n = personajes.filter((p) => p.tipo === "enemigo").length;
        x = COLUMNAS - 2 - (Math.floor(n / FILAS) % (COLUMNAS - 2));
        y = (2 + n) % FILAS;
      }
      const p = new Personaje({ id: personajes.length + 1, tipo, nombre, vida, vida_max: vida, fuerza, inventario: [], x, y });
      personajes.push(p);
      anotar("entra", { id: p.id, tipo, nombre, vida, fuerza, x, y });
      return p;
    }

    const api = {
      escena(lugar) {
        if (!LUGARES.includes(lugar)) throw juego(`No conozco el lugar «${String(comoTexto(lugar)).slice(0, 20)}». Probá con: ${LUGARES.join(", ")}.`);
        anotar("escena", { lugar });
      },
      heroe(nombre, vida, fuerza) {
        if (heroeCreado) throw juego("Ya hay un héroe en este juego: se crea una sola vez.");
        const p = crear("heroe", nombre, vida, fuerza); heroeCreado = true; return p;
      },
      enemigo: (nombre, vida, fuerza) => crear("enemigo", nombre, vida, fuerza),
      dado: (caras = 6) => azar.dado(numero(caras, "Las caras del dado", 2, TOPES.caras)),
      atacar(atacante, objetivo) {
        const a = persona(atacante, "Quien ataca"), b = persona(objetivo, "A quien atacás");
        const dano = a.fuerza + azar.dado(6);
        b.vida = Math.max(0, b.vida - dano);
        anotar("ataque", { de: a.id, a: b.id, dano, vida: b.vida });
        return dano;
      },
      curar(quien, cantidad) {
        const p = persona(quien, "A quien curás");
        cantidad = numero(cantidad, "Lo que curás", 0, TOPES.vida);
        p.vida = Math.min(p.vida_max, p.vida + cantidad);
        anotar("cura", { a: p.id, cantidad, vida: p.vida });
        return p.vida;
      },
      vivo: (quien) => persona(quien).vida > 0,
      decir(quien, t) { const p = persona(quien, "Quien habla"); anotar("dice", { id: p.id, texto: texto(t, "Lo que dice") }); },
      dar(quien, objeto) {
        const p = persona(quien, "A quien le das");
        objeto = texto(objeto, "El objeto", TOPES.nombre);
        if (p.inventario.length >= TOPES.inventario) throw juego(`El inventario ya tiene ${TOPES.inventario} cosas: no entra más.`);
        p.inventario.push(objeto);
        anotar("objeto", { a: p.id, objeto });
      },
      tiene: (quien, objeto) => persona(quien).inventario.some((v) => igual(v, objeto)),
      mover(quien, columna, fila) {
        const p = persona(quien, "A quien movés");
        p.x = numero(columna, "La columna", 0, COLUMNAS - 1);
        p.y = numero(fila, "La fila", 0, FILAS - 1);
        anotar("mueve", { id: p.id, x: p.x, y: p.y });
      },
      mision: (t) => anotar("mision", { texto: texto(t, "La misión") }),
      ganar(t = "¡Ganaste!") { anotar("fin", { gano: true, texto: texto(t, "El mensaje") }); terminado = true; },
      perder(t = "Perdiste. ¡Probá otra vez!") { anotar("fin", { gano: false, texto: texto(t, "El mensaje") }); terminado = true; },
      print(...valores) {
        const t = valores.map(comoTexto).join(" ");
        if (t.length > TOPES.texto) throw juego(`Ese texto es muy largo (máximo ${TOPES.texto} letras).`);
        anotar("texto", { texto: t });
      },
      input(pregunta = "") {
        pregunta = comoTexto(pregunta);
        let respuesta;
        if (entradas.length) respuesta = entradas.shift();
        else if (vacio) respuesta = "";
        else throw new Pregunta(pregunta);
        anotar("responde", { pregunta, respuesta });
        return respuesta;
      },
      // funciones comunes del lenguaje
      len(x) { if (typeof x === "string") return [...x].length; if (esLista(x)) return x.length; throw err("TypeError"); },
      range(...a) {
        if (!a.length || a.length > 3 || !a.every(esEntero)) throw err("TypeError");
        const [ini, fin, paso] = a.length === 1 ? [0, a[0], 1] : [a[0], a[1], a[2] === undefined ? 1 : a[2]];
        if (paso === 0) throw err("ValueError");
        const r = [];
        for (let i = ini; paso > 0 ? i < fin : i > fin; i += paso) { r.push(i); limitarLista(r); }
        return r;
      },
      str: (x = "") => comoTexto(x),
      int(x = 0) {
        if (typeof x === "number") return x;
        if (x instanceof Flotante) return entero(Math.trunc(x.v));
        if (typeof x === "boolean") return x ? 1 : 0;
        if (typeof x === "string" && /^\s*[+-]?\d+\s*$/.test(x)) return entero(parseInt(x, 10));
        throw err(typeof x === "string" ? "ValueError" : "TypeError");
      },
      float(x = 0) {
        if (esNumero(x)) return new Flotante(aNumero(x));
        if (typeof x === "string" && /^\s*[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?\s*$/.test(x)) return new Flotante(parseFloat(x));
        throw err(typeof x === "string" ? "ValueError" : "TypeError");
      },
      abs(x) { if (!esNumero(x)) throw err("TypeError"); return x instanceof Flotante ? new Flotante(Math.abs(x.v)) : Math.abs(aNumero(x)); },
      min: (...a) => extremo(a, (x, y) => comparar("<", x, y)),
      max: (...a) => extremo(a, (x, y) => comparar(">", x, y)),
      sum(l) { if (!esLista(l)) throw err("TypeError"); return l.reduce((s, v) => operar("+", s, v), 0); },
      round(x) {
        if (!esNumero(x)) throw err("TypeError");
        const v = aNumero(x), piso = Math.floor(v), resto = v - piso;
        return entero(resto > 0.5 ? piso + 1 : resto < 0.5 ? piso : (piso % 2 === 0 ? piso : piso + 1));  // al par, como Python
      },
    };
    function extremo(args, mejor) {
      const valores = args.length === 1 && esLista(args[0]) ? args[0] : args;
      if (!valores.length) throw err("ValueError");
      return valores.reduce((a, b) => (mejor(b, a) ? b : a));
    }

    // ── el recorrido del árbol ──
    const TIPOS = new Set(["expr", "asignar", "asignar_op", "si", "mientras", "para", "funcion", "devolver", "cortar", "seguir", "nada"]);
    class Retorno { constructor(v) { this.v = v; } }
    const CORTAR = {}, SEGUIR = {};

    function paso() {
      if (++pasos > TOPES.pasos) throw err("BucleInfinito");
    }
    function buscar(nombre, ambito) {
      if (ambito.local && ambito.local.has(nombre)) return ambito.local.get(nombre);
      if (ambito.locales && ambito.locales.has(nombre)) throw err("NameError", nombre);   // como UnboundLocalError
      if (ambito.global.has(nombre)) return ambito.global.get(nombre);
      if (Object.prototype.hasOwnProperty.call(api, nombre)) return api[nombre];
      throw err("NameError", nombre);
    }
    function guardar(nombre, valor, ambito) {
      (ambito.local || ambito.global).set(nombre, valor);
    }
    function correrCuerpo(cuerpo, ambito) {
      for (const s of cuerpo) {
        const r = sentencia(s, ambito);
        if (r !== undefined) return r;
      }
      return undefined;
    }
    function sentencia(s, ambito) {
      if (!s || !TIPOS.has(s.k)) throw err("TypeError");
      linea = s.l; paso();
      switch (s.k) {
        case "expr": valor(s.e, ambito); return undefined;
        case "asignar": asignar(s.d, valor(s.e, ambito), ambito); return undefined;
        case "asignar_op": asignar(s.d, operar(s.op, valor(s.d, ambito), valor(s.e, ambito)), ambito); return undefined;
        case "si": return correrCuerpo(verdadero(valor(s.c, ambito)) ? s.si : s.sino, ambito);
        case "mientras":
          for (;;) {
            linea = s.l; paso();
            if (!verdadero(valor(s.c, ambito))) return undefined;
            const r = correrCuerpo(s.cuerpo, ambito);
            if (r === CORTAR) return undefined;
            if (r instanceof Retorno) return r;
          }
        case "para": {
          const coleccion = valor(s.iter, ambito);
          const elementos = typeof coleccion === "string" ? [...coleccion] : esLista(coleccion) ? [...coleccion] : null;
          if (!elementos) throw err("TypeError");
          for (const e of elementos) {
            linea = s.l; paso();
            guardar(s.var, e, ambito);
            const r = correrCuerpo(s.cuerpo, ambito);
            if (r === CORTAR) return undefined;
            if (r instanceof Retorno) return r;
          }
          return undefined;
        }
        case "funcion": {
          const f = { esFuncion: true, nombre: s.nombre, params: s.params, cuerpo: s.cuerpo, global: ambito.global,
                      locales: new Set(Array.isArray(s.locales) ? s.locales : s.params) };
          guardar(s.nombre, f, ambito);
          return undefined;
        }
        case "devolver": return new Retorno(s.e ? valor(s.e, ambito) : null);
        case "cortar": return CORTAR;
        case "seguir": return SEGUIR;
        case "nada": return undefined;
      }
      return undefined;
    }
    function asignar(d, v, ambito) {
      if (d.k === "var") return guardar(d.id, v, ambito);
      if (d.k === "attr") {
        const p = valor(d.o, ambito);
        if (!(p instanceof Personaje)) throw err("AttributeError");
        if (d.a === "vida") { p.vida = numero(v, "La vida", 0, TOPES.vida); if (p.vida > p.vida_max) p.vida_max = p.vida; }
        else if (d.a === "fuerza") p.fuerza = numero(v, "La fuerza", 0, TOPES.fuerza);
        else if (d.a === "nombre") p.nombre = texto(v, "El nombre", TOPES.nombre);
        else throw err("AttributeError");
        anotar("cambia", { id: p.id, campo: d.a, valor: v });
        return undefined;
      }
      if (d.k === "indice") {
        const l = valor(d.o, ambito), i = valor(d.i, ambito);
        if (!esLista(l) || !esEntero(i)) throw err("TypeError");
        const pos = i < 0 ? l.length + i : i;
        if (pos < 0 || pos >= l.length) throw err("IndexError");
        l[pos] = v;
        return undefined;
      }
      throw err("TypeError");
    }
    function llamar(f, args) {
      if (typeof f === "function") return f(...args);
      if (!f || !f.esFuncion) throw err("TypeError");
      if (args.length !== f.params.length) throw err("TypeError");
      if (++profundidad > TOPES.profundidad) throw err("Recursion");
      const local = new Map(f.params.map((p, i) => [p, args[i]]));
      const lineaAntes = linea;
      try {
        const r = correrCuerpo(f.cuerpo, { global: f.global, local, locales: f.locales });
        linea = lineaAntes;          // terminó bien: lo que sigue es de la línea que la llamó (si falla, queda donde falló)
        return r instanceof Retorno ? r.v : null;
      } finally { profundidad--; }
    }
    function valor(e, ambito) {
      switch (e && e.k) {
        case "num": return e.f ? new Flotante(e.v) : e.v;
        case "texto": return e.v;
        case "const": return e.v;
        case "var": return buscar(e.id, ambito);
        case "op": return operar(e.op, valor(e.a, ambito), valor(e.b, ambito));
        case "unario": {
          const a = valor(e.a, ambito);
          if (e.op === "no") return !verdadero(a);
          if (!esNumero(a)) throw err("TypeError");
          if (e.op === "+") return a;
          return a instanceof Flotante ? new Flotante(-a.v) : entero(-aNumero(a));
        }
        case "logica": {
          let r;
          for (const v of e.vs) {
            r = valor(v, ambito);
            if (e.op === "y" ? !verdadero(r) : verdadero(r)) return r;
          }
          return r;
        }
        case "comparar": {
          let izq = valor(e.vs[0], ambito);
          for (let i = 0; i < e.ops.length; i++) {
            const der = valor(e.vs[i + 1], ambito);
            if (!comparar(e.ops[i], izq, der)) return false;
            izq = der;
          }
          return true;
        }
        case "llamar": {
          const f = buscar(e.f, ambito);
          return llamar(f, e.args.map((a) => valor(a, ambito)));
        }
        case "metodo": {
          const l = valor(e.o, ambito);
          if (!esLista(l)) throw err("AttributeError");
          const args = e.args.map((a) => valor(a, ambito));
          if (e.m === "append") { if (args.length !== 1) throw err("TypeError"); l.push(args[0]); limitarLista(l); return null; }
          if (e.m === "pop") {
            if (!l.length) throw err("IndexError");
            if (!args.length) return l.pop();
            const i = args[0]; if (!esEntero(i)) throw err("TypeError");
            const pos = i < 0 ? l.length + i : i;
            if (pos < 0 || pos >= l.length) throw err("IndexError");
            return l.splice(pos, 1)[0];
          }
          throw err("AttributeError");
        }
        case "attr": {
          const p = valor(e.o, ambito);
          if (!(p instanceof Personaje) || !["nombre", "vida", "vida_max", "fuerza", "inventario"].includes(e.a)) throw err("AttributeError");
          return p[e.a];
        }
        case "indice": {
          const o = valor(e.o, ambito), i = valor(e.i, ambito);
          if (!(esLista(o) || typeof o === "string") || !esEntero(i)) throw err("TypeError");
          const elementos = typeof o === "string" ? [...o] : o;
          const pos = i < 0 ? elementos.length + i : i;
          if (pos < 0 || pos >= elementos.length) throw err("IndexError");
          return elementos[pos];
        }
        case "lista": return limitarLista(e.vs.map((v) => valor(v, ambito)));
        case "si_expr": return verdadero(valor(e.c, ambito)) ? valor(e.si, ambito) : valor(e.sino, ambito);
      }
      throw err("TypeError");
    }

    // ── correr ──
    const resultado = { eventos, error: false, mensaje: "", linea: null, pregunta: null };
    try {
      if (!arbol || arbol.k !== "programa" || !Array.isArray(arbol.cuerpo)) throw err("TypeError");
      correrCuerpo(arbol.cuerpo, { global: new Map(), local: null });
    } catch (e) {
      if (e instanceof Pregunta) resultado.pregunta = e.texto;
      else if (e instanceof ErrorDelChico) { resultado.error = true; resultado.linea = linea || null; resultado.mensaje = mensaje(e, linea); }
      else if (e instanceof RangeError) { resultado.error = true; resultado.linea = linea || null; resultado.mensaje = mensaje(err("Recursion"), linea); }
      else throw e;
    }
    return resultado;
  }

  const TortuGame = { ejecutar, crearAzar, comoTexto, TOPES, LUGARES, COLUMNAS, FILAS };
  raiz.TortuGame = TortuGame;

  // Dentro de un Web Worker: recibe {arbol, semilla, entradas} y devuelve el resultado. Nada más.
  if (typeof raiz.WorkerGlobalScope !== "undefined" && raiz instanceof raiz.WorkerGlobalScope) {
    raiz.onmessage = (ev) => {
      const d = ev.data || {};
      raiz.postMessage(ejecutar(d.arbol, { semilla: d.semilla, entradas: d.entradas }));
    };
  }
})(typeof self !== "undefined" ? self : globalThis);
