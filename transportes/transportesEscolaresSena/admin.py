from django.contrib import admin

# Register your models here.

from .models import Cliente,Beneficiarios,Comentarios,Servicios,Peticiones,Vehiculo

# Register your models here.
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('id','nombre', 'apellido', 'correo', 'direccion', 'documento','fecha_nacimiento', 'usuario', 'clave', 'rol' ) 
    search_fields = ['id','nombre']

@admin.register(Beneficiarios)
class BeneficiariosAdmin(admin.ModelAdmin):
    list_display =  ('id','cliente', 'nombre', 'apellido', 'documento', 'fecha_nacimiento', )
    search_fields = ['nombre','id']

@admin.register(Comentarios)
class ComentariosAdmin(admin.ModelAdmin):
    list_display = ('id','cliente', 'tipo', 'desc', )
    search_fields = ['cliente','id']

@admin.register(Servicios)
class SetviciosAdmin(admin.ModelAdmin):
    list_display = ('id','nombre', 'caracteristicas', )
    search_fields = ['nombre','id']

@admin.register(Peticiones)
class PeticionesAdmin(admin.ModelAdmin):
    list_display =  ('id','cliente', 'servicios',  'direccion', 'colegio', 'horario', 'comentario_add', )
    search_fields = ['id','cliente', 'servicios', ]


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display =  ('placa', 'marca', 'color', 'cliente', 'foto', 'verFoto' )
    search_fields = ['placa','cliente']
    
    def verFoto(self, obj):
        from django.utils.html import format_html
        return format_html('<img src="{}" width="20%" />'.format(obj.foto.url))



