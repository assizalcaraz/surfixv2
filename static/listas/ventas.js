const COTIZACION_URL = window.COTIZACION_URL || "/cotizacion/";

$(document).ready(function() {
    var valoresPorDefecto = {
        "Abrasivos": { descuento: 67, descuento_adicional: 30, margen_ganancia: 35 },
        "Pintura": { descuento: 10, descuento_adicional: 0, margen_ganancia: 35 },
        "Fijador": { descuento: 10, descuento_adicional: 0, margen_ganancia: 35 },
        "Cintas Rapifix": { descuento: 67, descuento_adicional: 20, margen_ganancia: 35 },
        "Fijapel": { descuento: 67, descuento_adicional: 40, margen_ganancia: 35 },
        "Polimero": { descuento: 67, descuento_adicional: 0, margen_ganancia: 35 },
        "Rodillos": { descuento: 67, descuento_adicional: 20, margen_ganancia: 35 },
        "Pinceleta": { descuento: 67, descuento_adicional: 0, margen_ganancia: 35 },
        "Paño": { descuento: 67, descuento_adicional: 20, margen_ganancia: 35 },
        "Venda": { descuento: 67, descuento_adicional: 20, margen_ganancia: 35 },
    };

    function actualizarCotizacionDolar() {
        fetch(COTIZACION_URL)
            .then(response => response.json())
            .then(data => {
                if (data.cotizacion) {
                    $("#cotizacion_dolar").val(data.cotizacion);
                    calcular_precio_final();
                } else {
                    console.error("Error al obtener la cotización del dólar:", data.error);
                }
            })
            .catch(error => console.error("Error en la solicitud de cotización:", error));
    }

    actualizarCotizacionDolar();

    $(".categoria-checkbox").on("change", function() {
        var categoriasSeleccionadas = $(".categoria-checkbox:checked").map(function() {
            return $(this).val();
        }).get();

        $("#lista_precios tbody").empty();
        $(".producto-row").each(function() {
            var categoria = $(this).data("categoria");
            if (categoriasSeleccionadas.includes(categoria)) {
                $("#lista_precios tbody").append($(this).clone());
            }
        });
        actualizarComposicionPrecio(categoriasSeleccionadas);
        calcular_precio_final();
    });

    function calcular_precio_final() {
        var categorias = {};
        $("#precio_composicion tbody tr").each(function() {
            var categoria = $(this).find(".categoria").val();
            var descuento = parseFloat($(this).find(".descuento").val());
            var descuento_adicional = parseFloat($(this).find(".descuento_adicional").val());
            var margen_ganancia = parseFloat($(this).find(".margen_ganancia").val());

            categorias[categoria] = {
                descuento: isNaN(descuento) ? 0 : descuento,
                descuento_adicional: isNaN(descuento_adicional) ? 0 : descuento_adicional,
                margen_ganancia: isNaN(margen_ganancia) ? 0 : margen_ganancia
            };
        });

        var cotizacion = parseFloat($("#cotizacion_dolar").val()) || 1;

        $("#lista_precios tbody tr").each(function() {
            var categoria = $(this).data("categoria");
            var precio_base = parseFloat($(this).find(".precio").text().replace(',', '.'));

            if (categorias[categoria]) {
                var d = categorias[categoria];
                var precio_descuento = precio_base * (1 - d.descuento / 100);
                var precio_descuento_adicional = precio_descuento * (1 - d.descuento_adicional / 100);
                var precio_final = precio_descuento_adicional * (1 + d.margen_ganancia / 100) * cotizacion;
                $(this).find(".precio_final").text(precio_final.toFixed(2).replace('.', ',').replace(/\B(?=(\d{3})+(?!\d))/g, "."));
            }
        });
    }

    function actualizarComposicionPrecio(categoriasSeleccionadas) {
        $("#precio_composicion tbody").empty();
        categoriasSeleccionadas.forEach(function(categoria) {
            var valores = valoresPorDefecto[categoria] || {descuento: 0, descuento_adicional: 0, margen_ganancia: 0};
            var fila = `
                <tr>
                    <td><input type="text" class="categoria" value="${categoria}" readonly></td>
                    <td><input type="number" class="descuento" step="0.01" value="${valores.descuento}"></td>
                    <td><input type="number" class="descuento_adicional" step="0.01" value="${valores.descuento_adicional}"></td>
                    <td><input type="number" class="margen_ganancia" step="0.01" value="${valores.margen_ganancia}"></td>
                </tr>
            `;
            $("#precio_composicion tbody").append(fila);
        });

        $("#precio_composicion input").on("input", calcular_precio_final);
    }

    $("#precio_composicion input, #cotizacion_dolar").on("input", calcular_precio_final);

    $("#exportar_pdf").on("click", function() {
        var cotizacion = $("#cotizacion_dolar").val();
        $("#cotizacion_dolar_hidden").val(cotizacion);

        var descuentos = {}, adicionales = {}, margenes = {};

        $("#precio_composicion tbody tr").each(function() {
            var categoria = $(this).find(".categoria").val();
            descuentos[categoria] = parseFloat($(this).find(".descuento").val()) || 0;
            adicionales[categoria] = parseFloat($(this).find(".descuento_adicional").val()) || 0;
            margenes[categoria] = parseFloat($(this).find(".margen_ganancia").val()) || 0;
        });

        for (var cat in descuentos) {
            [
                { name: "descuento_", val: descuentos[cat] },
                { name: "descuento_adicional_", val: adicionales[cat] },
                { name: "margen_ganancia_", val: margenes[cat] }
            ].forEach(e => {
                $("<input>").attr({
                    type: "hidden",
                    name: e.name + cat,
                    value: e.val.toFixed(2)
                }).appendTo("#exportar_pdf_form");
            });
        }

        $("#lista_precios tbody tr").each(function() {
            var id = $(this).find(".id").val();
            if (id) {
                $("<input>").attr({
                    type: "hidden",
                    name: "ids[]",
                    value: id
                }).appendTo("#exportar_pdf_form");
            }
        });
    });
});
