// EvalúaBeca - interfaz web (paradigma orientado a eventos)
// La interfaz no sigue un flujo fijo: cada acción del usuario dispara un
// evento y los manejadores (handlers) registrados reaccionan a él. Además
// se usan eventos propios (CustomEvent) para comunicar componentes sin
// que se conozcan entre sí.

const API = "/api";
const $ = (selector) => document.querySelector(selector);
const form = $("#form-solicitud");
const colones = new Intl.NumberFormat("es-CR", { style: "currency", currency: "CRC", maximumFractionDigits: 0 });
const NOMBRES = {
  promedio: "Promedio académico", ingreso: "Ingreso per cápita", carga_academica: "Carga académica",
  promedio_minimo: "Promedio mínimo", promedio_minimo_condicion: "Promedio mínimo con condición especial",
  ingreso_per_capita_maximo: "Ingreso per cápita máximo", ingreso_per_capita_prioridad: "Ingreso per cápita para beca total",
  materias_minimas: "Materias mínimas matriculadas", ingreso_prioritario: "ingreso per cápita prioritario",
  condicion_especial: "condición especial reconocida", discapacidad: "Discapacidad", jefe_de_hogar: "Jefe(a) de hogar",
  zona_vulnerable: "Zona vulnerable", primera_generacion: "Primera generación universitaria",
};
const nombre = (clave) => NOMBRES[clave] || clave;

// Pequeño bus de eventos sobre document
const emitir = (tipo, detalle) => document.dispatchEvent(new CustomEvent(tipo, { detail: detalle }));
const escuchar = (tipo, manejador) => document.addEventListener(tipo, (e) => manejador(e.detail));

// ===== Navegación por pestañas ==============================================
$("#pestanas").addEventListener("click", (e) => {
  const boton = e.target.closest("button[data-pestana]");
  if (boton) emitir("pestana-cambiada", boton.dataset.pestana);
});

escuchar("pestana-cambiada", (pestana) => {
  document.querySelectorAll("#pestanas button").forEach((b) => b.classList.toggle("activa", b.dataset.pestana === pestana));
  document.querySelectorAll(".vista").forEach((v) => (v.hidden = v.id !== `vista-${pestana}`));
});
escuchar("pestana-cambiada", (p) => p === "historial" && cargarHistorial());
escuchar("pestana-cambiada", (p) => p === "estadisticas" && cargarEstadisticas());
escuchar("pestana-cambiada", (p) => p === "criterios" && cargarCriterios());

// ===== Formulario: validación en vivo y envío ===============================
form.addEventListener("input", (e) => {
  const campo = e.target;
  if (campo.type !== "checkbox") campo.classList.toggle("invalido", !campo.checkValidity());
  if (["ingreso_hogar", "miembros_hogar"].includes(campo.name)) actualizarPerCapita();
});

form.addEventListener("reset", () => {
  setTimeout(actualizarPerCapita);
  form.querySelectorAll(".invalido").forEach((c) => c.classList.remove("invalido"));
  $("#error-form").hidden = true;
});

function actualizarPerCapita() {
  const ingreso = Number(form.ingreso_hogar.value), miembros = Number(form.miembros_hogar.value);
  $("#ingreso-pc").textContent = "Ingreso per cápita: " +
    (form.ingreso_hogar.value && miembros > 0 ? colones.format(ingreso / miembros) : "—");
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  $("#error-form").hidden = true;
  if (!form.checkValidity()) {
    [...form.elements].forEach((c) => c.willValidate && c.classList.toggle("invalido", !c.checkValidity()));
    return mostrarError("Revise los campos marcados en rojo.");
  }
  const boton = $("#btn-evaluar");
  boton.disabled = true;
  try {
    const r = await fetch(`${API}/solicitudes`, {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(leerFormulario()),
    });
    const datos = await r.json();
    if (!r.ok) return mostrarError(mensajeValidacion(datos));
    emitir("solicitud-evaluada", datos);
  } catch {
    mostrarError("No fue posible conectar con el servidor.");
  } finally {
    boton.disabled = false;
  }
});

function leerFormulario() {
  const d = new FormData(form);
  return {
    carne: d.get("carne"), nombre: d.get("nombre"), carrera: d.get("carrera"),
    promedio: Number(d.get("promedio")), ingreso_hogar: Number(d.get("ingreso_hogar")),
    miembros_hogar: Number(d.get("miembros_hogar")), materias: Number(d.get("materias")),
    condiciones: d.getAll("condiciones"),
  };
}

const mensajeValidacion = (datos) => Array.isArray(datos.detail)
  ? datos.detail.map((e) => `${e.loc.slice(1).join(".") || "solicitud"}: ${e.msg}`).join(" · ")
  : datos.detail || "Error al evaluar.";

function mostrarError(texto) {
  $("#error-form").textContent = texto;
  $("#error-form").hidden = false;
}

// ===== Suscriptores de "solicitud-evaluada" =================================
escuchar("solicitud-evaluada", (s) => ($("#resultado").innerHTML = htmlDictamen(s)));
escuchar("solicitud-evaluada", (s) => avisar(`${s.id} evaluada: ${s.dictamen.resultado}`));

function htmlDictamen(s) {
  const d = s.dictamen;
  const motivo = d.motivos_tipo.length ? ` por ${d.motivos_tipo.map(nombre).join(" y ")}` : "";
  return `
    <span class="sello ${d.resultado}">${d.resultado === "aprobada" ? `Aprobada · beca ${d.tipo_beca}` : "Rechazada"}</span>
    <p>${d.resumen}${d.resultado === "aprobada" ? ` Se asigna beca ${d.tipo_beca}${motivo}.` : ""}</p>
    <ul class="criterios">
      ${d.criterios.map((c) => `<li class="${c.cumple ? "cumple" : "no_cumple"}">${c.cumple ? "✔" : "✘"} ${c.explicacion}</li>`).join("")}
    </ul>
    <p class="meta">${s.id} · ${s.nombre} · periodo ${d.periodo}
      ${d.condiciones_aplicadas.length ? "· condición aplicada: " + d.condiciones_aplicadas.map(nombre).join(", ") : ""}</p>`;
}

function avisar(texto) {
  document.title = `EvalúaBeca · ${texto}`;
}

// ===== Historial: filtros, búsqueda y detalle ===============================
let temporizador;
$("#filtro-texto").addEventListener("input", () => {        // debounce: espera a que el usuario deje de escribir
  clearTimeout(temporizador);
  temporizador = setTimeout(cargarHistorial, 250);
});
$("#filtro-resultado").addEventListener("change", cargarHistorial);
$("#filtro-tipo").addEventListener("change", cargarHistorial);

async function cargarHistorial() {
  const parametros = new URLSearchParams(Object.entries({
    buscar: $("#filtro-texto").value.trim(), resultado: $("#filtro-resultado").value, tipo: $("#filtro-tipo").value,
  }).filter(([, valor]) => valor));
  const lista = await (await fetch(`${API}/solicitudes?${parametros}`)).json();
  $("#tabla-historial").innerHTML = lista.length
    ? lista.map((s) => `
        <tr data-id="${s.id}"><td>${s.id}</td><td>${s.nombre}</td><td>${s.carrera}</td><td>${s.promedio}</td>
        <td><span class="etiqueta ${s.dictamen.resultado}">${s.dictamen.resultado}</span></td>
        <td>${s.dictamen.tipo_beca}</td><td>${new Date(s.fecha).toLocaleString("es-CR")}</td></tr>`).join("")
    : `<tr><td colspan="7" class="vacio">No hay solicitudes con esos filtros</td></tr>`;
}

// Delegación de eventos: un solo listener para todas las filas
$("#tabla-historial").addEventListener("click", (e) => {
  const fila = e.target.closest("tr[data-id]");
  if (fila) emitir("detalle-solicitado", fila.dataset.id);
});

escuchar("detalle-solicitado", async (id) => {
  const s = await (await fetch(`${API}/solicitudes/${id}`)).json();
  $("#modal-contenido").innerHTML = `
    <h2>Solicitud ${s.id}</h2>
    <div class="datos">
      <div><span>Estudiante:</span> ${s.nombre}</div><div><span>Carné:</span> ${s.carne}</div>
      <div><span>Carrera:</span> ${s.carrera}</div><div><span>Promedio:</span> ${s.promedio}</div>
      <div><span>Ingreso del hogar:</span> ${colones.format(s.ingreso_hogar)}</div><div><span>Miembros:</span> ${s.miembros_hogar}</div>
      <div><span>Materias:</span> ${s.materias}</div><div><span>Condiciones:</span> ${s.condiciones.map(nombre).join(", ") || "ninguna"}</div>
    </div>
    ${htmlDictamen(s)}`;
  $("#modal").hidden = false;
});

const cerrarModal = () => ($("#modal").hidden = true);
$("#cerrar-modal").addEventListener("click", cerrarModal);
$("#modal").addEventListener("click", (e) => e.target.id === "modal" && cerrarModal());
document.addEventListener("keydown", (e) => e.key === "Escape" && cerrarModal());

// ===== Estadísticas =========================================================
async function cargarEstadisticas() {
  const e = await (await fetch(`${API}/estadisticas`)).json();
  const tarjetas = [
    ["Solicitudes", e.total], ["Aprobadas", e.aprobadas], ["Rechazadas", e.rechazadas],
    ["Tasa de aprobación", `${e.tasa_aprobacion}%`], ["Promedio general", e.promedio_general],
  ];
  $("#indicadores").innerHTML = tarjetas.map(([n, v]) => `<div class="indicador"><div class="valor">${v}</div><div class="nombre">${n}</div></div>`).join("");
  $("#graf-incumplidos").innerHTML = barras(e.criterios_incumplidos, "rojo") || `<p class="vacio">Ningún criterio incumplido.</p>`;
  $("#graf-carreras").innerHTML = barras(e.por_carrera) || `<p class="vacio">Sin datos.</p>`;
}

function barras(datos, clase = "") {
  const pares = Object.entries(datos);
  const maximo = Math.max(...pares.map(([, v]) => v), 1);
  return `<div class="barras">${pares.map(([k, v]) => `
    <div class="fila-barra"><span>${nombre(k)}</span>
      <div class="pista"><div class="relleno ${clase}" style="width:${(v / maximo) * 100}%"></div></div><b>${v}</b></div>`).join("")}</div>`;
}

// ===== Criterios vigentes (leídos de Prolog) ================================
async function cargarCriterios() {
  const c = await (await fetch(`${API}/criterios`)).json();
  const formato = (k, v) => (k.startsWith("ingreso") ? colones.format(v) : v);
  $("#tabla-criterios").innerHTML = `
    <p><b>Periodo vigente:</b> ${c.periodo}</p>
    <table class="criterios-tabla"><thead><tr><th>Hecho en Prolog</th><th>Descripción</th><th>Valor</th></tr></thead><tbody>
      ${Object.entries(c.umbrales).map(([k, v]) => `<tr><td><code>umbral(${k}, ${v})</code></td><td>${nombre(k)}</td><td>${formato(k, v)}</td></tr>`).join("")}
    </tbody></table>
    <h3>Condiciones especiales reconocidas</h3>
    <p>${c.condiciones_especiales.map((x) => `<span class="etiqueta aprobada">${nombre(x)}</span>`).join(" ")}</p>`;
}

// ===== Carga inicial ========================================================
document.addEventListener("DOMContentLoaded", () => emitir("pestana-cambiada", "evaluar"));
