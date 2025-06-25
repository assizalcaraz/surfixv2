document.addEventListener("DOMContentLoaded", () => {
    const cotizacionInput = document.getElementById("cotizacion_dolar");
    const margenGananciaInput = document.getElementById("margen-ganancia");
    const descuentoInput = document.getElementById("descuento-global");
    const descuentoAdicionalInput = document.getElementById("descuento-adicional");
    const tablaProductos = document.querySelector("#presupuesto-body");
    const totalDisplay = document.querySelector("#total");
    const formPresupuesto = document.getElementById("form-presupuesto");

    function actualizarCotizacionDolar() {
        fetch("/listas/api/cotizacion_dolar/")
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
                                data-unidades-x-caja="${unidadesXCaja}">
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
            const cotizacion = parseFloat(cotizacionInput.value) || 1;
            const margenGanancia = parseFloat(margenGananciaInput.value) || 0;
            const descuento = parseFloat(descuentoInput.value) || 0;
            const descuentoAdicional = parseFloat(descuentoAdicionalInput.value) || 0;

            let precio = precioBase * (1 - descuento / 100);
            precio *= (1 - descuentoAdicional / 100);
            precio *= (1 + margenGanancia / 100);
            precio *= cotizacion;

            const newRow = `
                <tr class="product-row" data-id="${id}" data-precio-base="${precioBase}">
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

    [cotizacionInput, margenGananciaInput, descuentoInput, descuentoAdicionalInput].forEach(input => {
        input.addEventListener("input", recalcularPrecios);
    });

    document.addEventListener("input", (event) => {
        if (event.target.classList.contains("cantidad")) {
            recalcularPrecios();
        }
    });

    function recalcularPrecios() {
        const cotizacion = parseFloat(cotizacionInput.value) || 1;
        const margenGanancia = parseFloat(margenGananciaInput.value) || 0;
        const descuento = parseFloat(descuentoInput.value) || 0;
        const descuentoAdicional = parseFloat(descuentoAdicionalInput.value) || 0;

        document.querySelectorAll(".product-row").forEach(row => {
            const precioBase = parseFloat(row.dataset.precioBase) || 0;
            const cantidad = parseFloat(row.querySelector(".cantidad").value) || 1;

            let precio = precioBase * (1 - descuento / 100);
            precio *= (1 - descuentoAdicional / 100);
            precio *= (1 + margenGanancia / 100);
            precio *= cotizacion;

            const subtotal = precio * cantidad;

            row.querySelector(".precio-unitario").textContent = precio.toFixed(2);
            row.querySelector(".subtotal").textContent = subtotal.toFixed(2);
        });

        calcularTotal();
    }

    function calcularTotal() {
        let total = 0;
        document.querySelectorAll(".subtotal").forEach(cell => {
            total += parseFloat(cell.textContent) || 0;
        });
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
        document.getElementById("margen_ganancia_hidden").value = margenGananciaInput.value;
        document.getElementById("descuento_adicional_hidden").value = descuentoAdicionalInput.value;
    });
});
