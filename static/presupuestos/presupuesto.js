document.addEventListener("DOMContentLoaded", () => {
    console.log("📢 Script presupuesto.js cargado correctamente");

    const cotizacionInput = document.getElementById("cotizacion_dolar");
    const margenGananciaInput = document.getElementById("margen-ganancia");
    const descuentoInput = document.getElementById("descuento-global");
    const tablaProductos = document.querySelector("#presupuesto-body");
    const totalDisplay = document.querySelector("#total");
    const formPresupuesto = document.getElementById("form-presupuesto");

    function actualizarCotizacionDolar() {
        console.log("🔄 Solicitando cotización del dólar...");
        fetch("/listas/api/cotizacion_dolar/")
            .then(response => response.json())
            .then(data => {
                if (data.cotizacion) {
                    cotizacionInput.value = data.cotizacion;
                    console.log("✅ Cotización actualizada:", data.cotizacion);
                } else {
                    console.error("❌ Error al obtener la cotización del dólar:", data.error);
                }
            })
            .catch(error => console.error("❌ Error en la solicitud de cotización:", error));
    }
    actualizarCotizacionDolar();

    document.getElementById("product-search").addEventListener("input", function () {
        const query = this.value;
        if (query.length > 2) {
            console.log("🔍 Buscando productos con:", query);
            fetch(`/presupuestos/buscar_producto/?q=${query}`)
                .then(response => response.json())
                .then(data => {
                    let suggestions = "";
                    data.forEach(producto => {
                        let unidadesXCaja = calcularUnidadesPorCaja(producto.ancho);
                        console.log(`📦 Unidades por caja (${producto.nombre}): ${unidadesXCaja}`);

                        suggestions += `
                            <div class="suggestion-item" 
                                data-id="${producto.id}" 
                                data-nombre="${producto.nombre}" 
                                data-precio="${producto.precio_unidad}" 
                                data-ancho="${producto.ancho}" 
                                data-unidades-x-caja="${unidadesXCaja}">
                                <strong>${producto.nombre}</strong> - Código: ${producto.codigo}
                            </div>`;
                    });
                    document.getElementById("suggestions").innerHTML = suggestions;
                    document.getElementById("suggestions").style.display = "block";
                })
                .catch(() => {
                    console.error("❌ Error al buscar productos");
                    document.getElementById("suggestions").innerHTML = "<div class='error'>Error al buscar productos</div>";
                    document.getElementById("suggestions").style.display = "block";
                });
        } else {
            document.getElementById("suggestions").style.display = "none";
        }
    });

    document.addEventListener("click", (event) => {
        if (event.target.classList.contains("suggestion-item")) {
            const id = event.target.dataset.id;
            const nombre = event.target.dataset.nombre;
            const precioBase = parseFloat(event.target.dataset.precio) || 0;
            const ancho = parseInt(event.target.dataset.ancho) || 0;
            const unidadesXCaja = calcularUnidadesPorCaja(ancho);
            const cotizacion = parseFloat(cotizacionInput.value) || 1;
            const margenGanancia = parseFloat(margenGananciaInput.value) || 0;
            const descuento = parseFloat(descuentoInput.value) || 0;

            if (!precioBase || isNaN(precioBase)) {
                console.error("❌ Precio base inválido:", precioBase);
                return;
            }

            const precioConDescuento = precioBase * (1 - descuento / 100);
            const precioFinal = precioConDescuento * (1 + margenGanancia / 100) * cotizacion;
            const precioCaja = precioFinal * unidadesXCaja;

            console.log(`📌 Producto agregado: ${nombre}`);
            console.log(`➡️ Precio unidad: ${precioFinal.toFixed(2)}, Precio caja: ${precioCaja.toFixed(2)}, Unidades por caja: ${unidadesXCaja}`);

            const newRow = `
                <tr class="product-row" data-id="${id}" data-precio-base="${precioBase}" data-unidades-x-caja="${unidadesXCaja}" data-tipo-precio="unidad">
                    <td>${nombre}</td>
                    <td><input type="number" class="cantidad" value="1" min="1"></td>
                    <td>
                        <button type="button" class="toggle-precio">Unidad</button>
                    </td>
                    <td class="precio-unitario">${precioFinal.toFixed(2)}</td>
                    <td class="subtotal">${precioFinal.toFixed(2)}</td>
                    <td><button type="button" class="remove-product">Eliminar</button></td>
                </tr>`;
            tablaProductos.insertAdjacentHTML("beforeend", newRow);
            document.getElementById("suggestions").style.display = "none";
            document.getElementById("product-search").value = "";
            recalcularPrecios();
        }
    });

    document.addEventListener("click", (event) => {
        if (event.target.classList.contains("remove-product")) {
            event.target.closest("tr").remove();
            calcularTotal();
        }

        if (event.target.classList.contains("toggle-precio")) {
            const row = event.target.closest("tr");
            const tipoPrecio = row.dataset.tipoPrecio === "unidad" ? "caja" : "unidad";
            row.dataset.tipoPrecio = tipoPrecio;
            event.target.textContent = tipoPrecio.charAt(0).toUpperCase() + tipoPrecio.slice(1);
            recalcularPrecios();
        }
    });

    function recalcularPrecios() {
        document.querySelectorAll(".product-row").forEach(row => {
            const precioBase = parseFloat(row.dataset.precioBase) || 0;
            const cantidadInput = row.querySelector(".cantidad");
            let cantidad = parseFloat(cantidadInput.value) || 1;
            const unidadesXCaja = parseInt(row.dataset.unidadesXcaja) || 1;
            const tipoPrecio = row.dataset.tipoPrecio;

            if (!precioBase || isNaN(precioBase)) {
                console.error("❌ Precio base inválido en recalculo:", precioBase);
                return;
            }

            const precioFinal = precioBase * (1 - descuentoInput.value / 100) * (1 + margenGananciaInput.value / 100) * cotizacionInput.value;
            const precioCaja = precioFinal * unidadesXCaja;

            // Ajustar la cantidad según el tipo de precio
            if (tipoPrecio === "caja") {
                cantidad *= unidadesXCaja;
            }

            const precioActualizado = tipoPrecio === "unidad" ? precioFinal : precioCaja;
            const subtotal = precioActualizado * cantidad;

            console.log(`📢 Recalculando precio: ${tipoPrecio === "unidad" ? "Unidad" : "Caja"}`);
            console.log(`➡️ Nuevo precio: ${precioActualizado.toFixed(2)}, Subtotal: ${subtotal.toFixed(2)}, Unidades por caja: ${unidadesXCaja}`);

            row.querySelector(".precio-unitario").textContent = precioActualizado.toFixed(2);
            row.querySelector(".subtotal").textContent = subtotal.toFixed(2);
        });

        calcularTotal();
    }

    function calcularTotal() {
        let total = 0;
        document.querySelectorAll(".subtotal").forEach(subtotalCell => {
            total += parseFloat(subtotalCell.textContent) || 0;
        });
        totalDisplay.textContent = `$${total.toFixed(2)}`;
    }

    function calcularUnidadesPorCaja(ancho) {
        const unidadesPorAncho = { 18: 48, 24: 36, 36: 24, 48: 18 };
        return unidadesPorAncho[ancho] || 1;
    }

    formPresupuesto.addEventListener("submit", function (e) {
        const productos = [];
        document.querySelectorAll(".product-row").forEach(row => {
            productos.push({
                id: row.dataset.id,
                cantidad: row.querySelector(".cantidad").value,
                precio: row.querySelector(".precio-unitario").textContent,
                subtotal: row.querySelector(".subtotal").textContent
            });
        });

        this.insertAdjacentHTML("beforeend", `<input type="hidden" name="productos" value='${JSON.stringify(productos)}'>`);
    });

});
