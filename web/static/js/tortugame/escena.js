/* TortuGame: dibuja la escena en un <canvas> y escribe lo que pasa (para leer y para lectores de pantalla).
 * Recibe el registro de eventos que devolvió el intérprete; no ejecuta nada del chico.
 * `aplicar` y `describir` son puros (sin DOM): se prueban en Node. */
"use strict";
const Escena = (() => {
  const COLUMNAS = 8, FILAS = 5, ANCHO = 640, ALTO = 400;
  const CELDA = { w: ANCHO / COLUMNAS, h: ALTO / FILAS };
  const FONDOS = { aldea: "#cfe8b8", bosque: "#7fb77e", cueva: "#9a9a9a", mazmorra: "#5b4a73", castillo: "#8fa9d6" };

  function nuevoEstado() {
    return { lugar: "aldea", personajes: new Map(), mision: null, globo: null, golpe: null, fin: null };
  }

  /** Aplica un evento al estado (puro). */
  function aplicar(e, ev) {
    const p = e.personajes.get(ev.id ?? ev.a);
    e.globo = null; e.golpe = null;
    switch (ev.t) {
      case "escena": e.lugar = ev.lugar; break;
      case "entra": e.personajes.set(ev.id, { id: ev.id, tipo: ev.tipo, nombre: ev.nombre, vida: ev.vida, vida_max: ev.vida,
                                              fuerza: ev.fuerza, x: ev.x, y: ev.y }); break;
      case "ataque": { const b = e.personajes.get(ev.a); if (b) b.vida = ev.vida; e.golpe = { id: ev.a, texto: `-${ev.dano}` }; break; }
      case "cura": if (p) p.vida = ev.vida; e.golpe = { id: ev.a, texto: `+${ev.cantidad}`, cura: true }; break;
      case "dice": e.globo = { id: ev.id, texto: ev.texto }; break;
      case "mueve": if (p) { p.x = ev.x; p.y = ev.y; } break;
      case "cambia": if (p) { p[ev.campo] = ev.valor; if (ev.campo === "vida" && ev.valor > p.vida_max) p.vida_max = ev.valor; } break;
      case "mision": e.mision = ev.texto; break;
      case "fin": e.fin = { gano: ev.gano, texto: ev.texto }; break;
    }
    return e;
  }

  /** El evento contado con palabras (puro). */
  function describir(ev, e) {
    const nombre = (id) => (e.personajes.get(id) || {}).nombre || "alguien";
    switch (ev.t) {
      case "escena": return `🗺️ Llegás a: ${ev.lugar}`;
      case "entra": return `${ev.tipo === "heroe" ? "🦸" : "👾"} Aparece ${ev.nombre} (❤️ ${ev.vida}, 💪 ${ev.fuerza})`;
      case "ataque": return `⚔️ ${nombre(ev.de)} ataca a ${nombre(ev.a)}: -${ev.dano} (le queda ❤️ ${ev.vida})`;
      case "cura": return `💚 ${nombre(ev.a)} se cura ${ev.cantidad} (❤️ ${ev.vida})`;
      case "dice": return `💬 ${nombre(ev.id)}: «${ev.texto}»`;
      case "objeto": return `🎒 ${nombre(ev.a)} consigue: ${ev.objeto}`;
      case "mueve": return `👣 ${nombre(ev.id)} se mueve a (${ev.x}, ${ev.y})`;
      case "cambia": return `✨ ${nombre(ev.id)}: ${ev.campo} ahora es ${ev.valor}`;
      case "mision": return `🎯 Misión: ${ev.texto}`;
      case "texto": return ev.texto;
      case "responde": return `❓ ${ev.pregunta} → ${ev.respuesta}`;
      case "fin": return `${ev.gano ? "🏆" : "💀"} ${ev.texto}`;
    }
    return "";
  }

  function crear(canvas, lista) {
    const ctx = canvas.getContext("2d");
    let e = nuevoEstado();
    let ejecucion = 0;

    function emoji(texto, x, y, tam) {
      ctx.font = `${tam}px sans-serif`; ctx.textAlign = "center"; ctx.textBaseline = "middle"; ctx.fillText(texto, x, y);
    }
    function pintar() {
      ctx.fillStyle = FONDOS[e.lugar] || FONDOS.aldea; ctx.fillRect(0, 0, ANCHO, ALTO);
      ctx.strokeStyle = "rgba(0,0,0,.08)"; ctx.lineWidth = 1;
      for (let c = 1; c < COLUMNAS; c++) { ctx.beginPath(); ctx.moveTo(c * CELDA.w, 0); ctx.lineTo(c * CELDA.w, ALTO); ctx.stroke(); }
      for (let f = 1; f < FILAS; f++) { ctx.beginPath(); ctx.moveTo(0, f * CELDA.h); ctx.lineTo(ANCHO, f * CELDA.h); ctx.stroke(); }
      for (const p of e.personajes.values()) {
        const cx = p.x * CELDA.w + CELDA.w / 2, cy = p.y * CELDA.h + CELDA.h / 2 - 6;
        ctx.globalAlpha = p.vida > 0 ? 1 : 0.35;
        emoji(p.tipo === "heroe" ? "🦸" : "👾", cx, cy, 34);
        ctx.globalAlpha = 1;
        ctx.fillStyle = "#111827"; ctx.font = "bold 12px sans-serif"; ctx.fillText(p.nombre.slice(0, 12), cx, cy + 26);
        const parte = p.vida_max ? Math.max(0, p.vida) / p.vida_max : 0;
        ctx.fillStyle = "#1f2937"; ctx.fillRect(cx - 26, cy + 34, 52, 6);
        ctx.fillStyle = parte > 0.5 ? "#16a34a" : parte > 0.2 ? "#ca8a04" : "#dc2626"; ctx.fillRect(cx - 26, cy + 34, 52 * parte, 6);
      }
      if (e.golpe) {
        const p = e.personajes.get(e.golpe.id);
        if (p) { ctx.fillStyle = e.golpe.cura ? "#15803d" : "#b91c1c"; ctx.font = "bold 22px sans-serif";
                 ctx.fillText(e.golpe.texto, p.x * CELDA.w + CELDA.w / 2 + 24, p.y * CELDA.h + 14); }
      }
      if (e.globo) {
        const p = e.personajes.get(e.globo.id);
        if (p) {
          const texto = e.globo.texto.length > 40 ? e.globo.texto.slice(0, 39) + "…" : e.globo.texto;
          ctx.font = "14px sans-serif";
          const w = Math.min(ANCHO - 8, ctx.measureText(texto).width + 16);
          const x = Math.max(4, Math.min(ANCHO - w - 4, p.x * CELDA.w + CELDA.w / 2 - w / 2)), y = Math.max(4, p.y * CELDA.h - 30);
          ctx.fillStyle = "#fff"; ctx.strokeStyle = "#111827"; ctx.fillRect(x, y, w, 24); ctx.strokeRect(x, y, w, 24);
          ctx.fillStyle = "#111827"; ctx.textAlign = "left"; ctx.fillText(texto, x + 8, y + 12);
        }
      }
      if (e.mision) {
        ctx.fillStyle = "rgba(17,24,39,.75)"; ctx.fillRect(0, 0, ANCHO, 26);
        ctx.fillStyle = "#fde68a"; ctx.font = "bold 14px sans-serif"; ctx.textAlign = "left"; ctx.textBaseline = "middle";
        ctx.fillText(`🎯 ${e.mision}`.slice(0, 80), 8, 13);
      }
      if (e.fin) {                                      // abajo: no tapa a los personajes
        const y = ALTO - 36;
        ctx.fillStyle = "rgba(17,24,39,.8)"; ctx.fillRect(0, ALTO - 72, ANCHO, 72);
        emoji(e.fin.gano ? "🏆" : "💀", 40, y, 34);
        ctx.fillStyle = "#fff"; ctx.font = "bold 20px sans-serif"; ctx.textAlign = "center";
        ctx.fillText(e.fin.texto.slice(0, 50), ANCHO / 2 + 20, y);
      }
    }
    function escribir(texto) {
      if (!texto) return;
      const li = document.createElement("li"); li.textContent = texto; lista.appendChild(li);
      li.scrollIntoView({ block: "nearest" });
    }
    const esperar = (ms) => new Promise((r) => setTimeout(r, ms));

    return {
      reiniciar() { ejecucion++; e = nuevoEstado(); lista.textContent = ""; pintar(); },
      detener() { ejecucion++; },
      /** Anima el registro evento por evento. Devuelve false si se detuvo. */
      async reproducir(eventos, { rapido } = {}) {
        const id = ++ejecucion;
        e = nuevoEstado(); lista.textContent = ""; pintar();
        for (const ev of eventos) {
          if (id !== ejecucion) return false;
          const texto = describir(ev, e);
          aplicar(e, ev); pintar(); escribir(texto);
          if (!rapido && ev.t !== "texto" && ev.t !== "responde") await esperar(ev.t === "dice" ? 700 : 380);
        }
        return id === ejecucion;
      },
      pintar,
    };
  }

  return { crear, nuevoEstado, aplicar, describir, COLUMNAS, FILAS };
})();
