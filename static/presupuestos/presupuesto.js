document.addEventListener("DOMContentLoaded", () => {
    const cotizacionInput = document.getElementById("cotizacion_dolar");
    const margenGananciaInput = document.getElementById("margen-ganancia");
    const descuentoGlobalExtraInput = document.getElementById("descuento_global_extra");
    const tablaProductos = document.querySelector("#presupuesto-body");
    const totalDisplay = document.querySelector("#total");
    const formPresupuesto = document.getElementById("form-presupuesto");

    const valoresPorDefecto = {
        "Abrasivos": { descuento: 67, descuento_adicional: 33.33, margen_ganancia: 35 },
        "Pintura": { descuento: 10, descuento_adicional: 0, margen_ganancia: 35 },
        "Fijador": { descuento: 10, descuento_adicional: 0, margen_ganancia: 35 },
        "Cintas Rapifix": { descuento: 67, descuento_adicional: 20, margen_ganancia: 35 },
        "Fijapel": { descuento: 67, descuento_adicional: 40, margen_ganancia: 35 },
        "Polimero": { descuento: 67, descuento_adicional: 0, margen_ganancia: 35 },
        "Rodillos": { descuento: 67, descuento_adicional: 20, margen_ganancia: 35 },
        "Pinceleta": { descuento: 67, descuento_adicional: 0, margen_ganancia: 35 },
        "Paño": { descuento: 67, descuento_adicional: 20, margen_ganancia: 35 },
        "Venda": { descuento: 67, descuento_adicional: 20, margen_ganancia: 35 }
    };

    function actualizarTablaComposicion(extra = 0) {
        const tbody = document.querySelector("#precio_composicion tbody");
        tbody.innerHTML = "";
        for (const categoria in valoresPorDefecto) {
            const ajustes = valoresPorDefecto[categoria];
            const fila = document.createElement("tr");
            fila.innerHTML = `
                <td>${categoria}</td>
                <td><input type="number" class="input-descuento" data-categoria="${categoria}" data-tipo="descuento" value="${ajustes.descuento}"></td>
                <td><input type="number" class="input-descuento" data-categoria="${categoria}" data-tipo="descuento_adicional" value="${ajustes.descuento_adicional}"></td>
                <td><input type="number" class="input-descuento" data-categoria="${categoria}" data-tipo="margen_ganancia" value="${ajustes.margen_ganancia}"></td>
            `;
            tbody.appendChild(fila);
        }
    }

    actualizarTablaComposicion();

    document.querySelector("#precio_composicion").addEventListener("input", () => {
        document.querySelectorAll(".input-descuento").forEach(input => {
            const cat = input.dataset.categoria;
            const tipo = input.dataset.tipo;
            valoresPorDefecto[cat][tipo] = parseFloat(input.value) || 0;
        });
        recalcularPrecios();
    });

    document.querySelectorAll(".categoria-checkbox").forEach(cb => {
        cb.addEventListener("change", () => {
            const extra = parseFloat(descuentoGlobalExtraInput?.value) || 0;
            actualizarTablaComposicion(extra);
        });
    });

    descuentoGlobalExtraInput?.addEventListener("input", () => {
        const extra = parseFloat(descuentoGlobalExtraInput.value) || 0;
        actualizarTablaComposicion(extra);
    });

    function actualizarCotizacionDolar() {
        fetch(window.COTIZACION_URL || "/listas/api/cotizacion_dolar/")
            .then(response => response.json())
            .then(data => {
                if (data.cotizacion) {
                    cotizacionInput.value = data.cotizacion;
                }
            });
    }
    actualizarCotizacionDolar();

    document.getElementById("product-search").addEventListener("input", function () {
        const query = this.value;
        if (query.length > 2) {
            fetch(`/presupuestos/buscar_producto/?q=${query}`)
                .then(response => response.json())
                .then(data => {
                    let suggestions = "";
                    data.forEach(producto => {
                        let unidadesXCaja = calcularUnidadesPorCaja(producto.ancho);
                        suggestions += `
                            <div class="suggestion-item" 
                                data-id="${producto.id}" 
                                data-nombre="${producto.nombre}" 
                                data-precio="${producto.precio_unidad}" 
                                data-ancho="${producto.ancho}" 
                                data-unidades-x-caja="${unidadesXCaja}" 
                                data-categoria="${producto.categoria}">
                                <strong>${producto.nombre}</strong> - Código: ${producto.codigo}
                            </div>`;
                    });
                    document.getElementById("suggestions").innerHTML = suggestions;
                    document.getElementById("suggestions").style.display = "block";
                })
                .catch(() => {
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
            const categoria = event.target.dataset.categoria;
            const cotizacion = parseFloat(cotizacionInput.value) || 1;
            const ajustes = valoresPorDefecto[categoria] || { descuento: 0, descuento_adicional: 0, margen_ganancia: 0 };

            let precio = precioBase * (1 - ajustes.descuento / 100);
            precio *= (1 - ajustes.descuento_adicional / 100);
            precio *= (1 + ajustes.margen_ganancia / 100);
            precio *= cotizacion;

            const newRow = `
                <tr class="product-row" data-id="${id}" data-precio-base="${precioBase}" data-categoria="${categoria}">
                    <td>${nombre}</td>
                    <td><input type="number" class="cantidad" value="1" min="1"></td>
                    <td class="precio-unitario">${precio.toFixed(2)}</td>
                    <td class="subtotal">${precio.toFixed(2)}</td>
                    <td><button type="button" class="remove-product">Eliminar</button></td>
                </tr>`;
            tablaProductos.insertAdjacentHTML("beforeend", newRow);
            document.getElementById("suggestions").style.display = "none";
            document.getElementById("product-search").value = "";
            recalcularPrecios();
        }

        if (event.target.classList.contains("remove-product")) {
            event.target.closest("tr").remove();
            calcularTotal();
        }
    });

    document.addEventListener("input", (event) => {
        if (event.target.classList.contains("cantidad")) {
            recalcularPrecios();
        }
    });

    function recalcularPrecios() {
        const cotizacion = parseFloat(cotizacionInput.value) || 1;
        const descuentoGlobalExtra = parseFloat(descuentoGlobalExtraInput?.value) || 0;

        document.querySelectorAll(".product-row").forEach(row => {
            const precioBase = parseFloat(row.dataset.precioBase) || 0;
            const cantidad = parseFloat(row.querySelector(".cantidad").value) || 1;
            const categoria = row.dataset.categoria;
            const ajustes = valoresPorDefecto[categoria] || { descuento: 0, descuento_adicional: 0, margen_ganancia: 0 };

            let precio = precioBase * (1 - ajustes.descuento / 100);
            precio *= (1 - ajustes.descuento_adicional / 100);
            precio *= (1 + ajustes.margen_ganancia / 100);
            precio *= cotizacion;

            const subtotal = precio * cantidad;
            row.querySelector(".precio-unitario").textContent = precio.toFixed(2);
            row.querySelector(".subtotal").textContent = subtotal.toFixed(2);
        });

        calcularTotal(descuentoGlobalExtra);
    }

    function calcularTotal(descuentoGlobalExtra = 0) {
        let total = 0;
        document.querySelectorAll(".subtotal").forEach(cell => {
            total += parseFloat(cell.textContent) || 0;
        });
        if (descuentoGlobalExtra > 0) {
            total *= (1 - descuentoGlobalExtra / 100);
        }
        totalDisplay.textContent = total.toFixed(2);
    }

    function calcularUnidadesPorCaja(ancho) {
        const unidadesPorAncho = { 18: 48, 24: 36, 36: 24, 48: 18 };
        return unidadesPorAncho[ancho] || 1;
    }

    formPresupuesto.addEventListener("submit", function () {
        const productos = [];
        document.querySelectorAll(".product-row").forEach(row => {
            productos.push({
                id: row.dataset.id,
                cantidad: row.querySelector(".cantidad").value,
                precioUnitario: row.querySelector(".precio-unitario").textContent,
                subtotal: row.querySelector(".subtotal").textContent
            });
        });

        this.insertAdjacentHTML("beforeend", `<input type="hidden" name="productos" value='${JSON.stringify(productos)}'>`);
        document.getElementById("cotizacion_dolar_hidden").value = cotizacionInput.value;
    });
});
