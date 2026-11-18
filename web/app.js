// EvalúaBeca - interfaz web (paradigma orientado a eventos)
// Toda la interacción se resuelve con listeners: el código no sigue un
// flujo fijo, reacciona a lo que hace el usuario y a eventos propios.

const API = "/api/solicitudes";
const form = document.getElementById("form-solicitud");
const errorForm = document.getElementById("error-form");
const colones = new Intl.NumberFormat("es-CR", { style: "currency", currency: "CRC", maximumFractionDigits: 0 });

// ---- Evento "input": validación y cálculo en vivo -------------------------
form.addEventListener("input", (evento) => {
  const campo = evento.target;
  if (campo.type !== "checkbox") campo.classList.toggle("invalido", !campo.checkValidity());
  if (["ingreso_hogar", "miembros_hogar"].includes(campo.name)) actualizarPerCapita();
});

function actualizarPerCapita() {
  const ingreso = Number(form.ingreso_hogar.value);
  const miembros = Number(form.miembros_hogar.value);
  document.getElementById("ingreso-pc").textContent =
    "Ingreso per cápita: " + (ingreso >= 0 && miembros > 0 ? colones.format(ingreso / miembros) : "—");
}

// ---- Evento "submit": enviar la solicitud a la API -------------------------
form.addEventListener("submit", async (evento) => {
  evento.preventDefault();
  errorForm.hidden = true;
  if (!form.checkValidity()) {
    [...form.elements].forEach((c) => c.willValidate && c.classList.toggle("invalido", !c.checkValidity()));
    return mostrarError("Revise los campos marcados en rojo.");
  }
  const boton = document.getElementById("btn-evaluar");
  boton.disabled = true;
  try {
    const respuesta = await fetch(API, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(leerFormulario()),
    });
    const datos = await respuesta.json();
    if (!respuesta.ok) return mostrarError(mensajeValidacion(datos));
    // Se emite un evento propio; otros componentes reaccionan a él.
    document.dispatchEvent(new CustomEvent("solicitud-evaluada", { detail: datos }));
  } catch {
    mostrarError("No fue posible conectar con el servidor.");
  } finally {
    boton.disabled = false;
  }
});

function leerFormulario() {
  const datos = new FormData(form);
  return {
    carne: datos.get("carne"),
    nombre: datos.get("nombre"),
    carrera: datos.get("carrera"),
    promedio: Number(datos.get("promedio")),
    ingreso_hogar: Number(datos.get("ingreso_hogar")),
    miembros_hogar: Number(datos.get("miembros_hogar")),
    materias: Number(datos.get("materias")),
    condiciones: datos.getAll("condiciones"),
  };
}

function mensajeValidacion(datos) {
  if (!Array.isArray(datos.detail)) return datos.detail || "Error al evaluar.";
  return datos.detail.map((e) => `${e.loc.slice(1).join(".") || "solicitud"}: ${e.msg}`).join(" · ");
}

function mostrarError(texto) {
  errorForm.textContent = texto;
  errorForm.hidden = false;
}

// ---- Suscriptores del evento "solicitud-evaluada" -------------------------
document.addEventListener("solicitud-evaluada", (e) => mostrarDictamen(e.detail));
document.addEventListener("solicitud-evaluada", () => cargarHistorial());

function mostrarDictamen(s) {
  const d = s.dictamen;
  document.getElementById("panel-resultado").hidden = false;
  document.getElementById("resultado").innerHTML = `
    <span class="sello ${d.resultado}">${d.resultado === "aprobada" ? "Aprobada" : "Rechazada"}
      ${d.resultado === "aprobada" ? "· beca " + d.tipo_beca : ""}</span>
    <p>${d.resumen}</p>
    <ul class="criterios">
      ${d.criterios.map((c) => `<li class="${c.cumple ? "cumple" : "no_cumple"}">${c.cumple ? "✔" : "✘"} ${c.explicacion}</li>`).join("")}
    </ul>
    <p class="meta">${s.id} · ${s.nombre} · periodo ${d.periodo}
      ${d.condiciones_aplicadas.length ? "· condición aplicada: " + d.condiciones_aplicadas.join(", ") : ""}</p>`;
}

async function cargarHistorial() {
  const lista = await (await fetch(API)).json();
  const cuerpo = document.getElementById("tabla-historial");
  cuerpo.innerHTML = lista.length
    ? lista.map((s) => `
        <tr><td>${s.id}</td><td>${s.nombre}</td><td>${s.promedio}</td>
        <td><span class="etiqueta ${s.dictamen.resultado}">${s.dictamen.resultado}</span></td>
        <td>${s.dictamen.tipo_beca}</td><td>${new Date(s.fecha).toLocaleString("es-CR")}</td></tr>`).join("")
    : `<tr><td colspan="6" class="vacio">Sin solicitudes todavía</td></tr>`;
}

// ---- Evento de carga de la página -----------------------------------------
document.addEventListener("DOMContentLoaded", cargarHistorial);
