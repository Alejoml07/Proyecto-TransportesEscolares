function buscarProducto(url){
    respuesta = $('#respuesta');
    buscar = $('#buscar').val();
    token = $('input[name="csrfmiddlewaretoken"]').val();
    
    $.ajax({
        url: url,
        type: 'post',
        data: { "buscar": buscar, "csrfmiddlewaretoken": token},
        //dataType: 'json',
        success: function(r){
            respuesta.html(r);
        },
        error: function(error){
            console.log("Error" + error);
        }
    });
}