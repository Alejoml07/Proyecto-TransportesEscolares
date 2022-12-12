from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse 

#Mensaje tipo cookie temporales 
from django.contrib import messages

#Gestion de errores de base de datos 
from django.db import IntegrityError

from .models import Cliente,Beneficiarios,Comentarios,Servicios,Peticiones, Vehiculo

from django.db.models import Q

from django.core.paginator import Paginator

from django.core.files.storage import FileSystemStorage

from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

from os import remove, path



# Create your views here.

def indexPrimary(request):
    """Se usa para acceder a la landing page del aplicativo

    Returns:
        template:`transportes/indexPrimary.html`
    """
    return render(request, 'transportes/indexPrimary.html')

def indexProveedor(request):
    """Se usa para verificar si el rol del usuario es `P` y redireccionar a la pagina deseada

    Args:
        login: Optine los datos de la sesion de logueo

    Returns:
        template:`transportes/indexProveedor.html`
    """
    login = request.session.get('logueo', False)
    if login and (login[2] == "A" or login[2] == "P"):
        u = Cliente.objects.get(id = login[3] )
        contexto = {'cli' : u}
        return render(request, 'transportes/indexProveedor.html',contexto)
    else:
        if login and (login[2] != "A" and login[2] != "P"):
            messages.warning(request, "Usted no tiene autorización para acceder al módulo...")
            return redirect('transportes:index')
        else:
            messages.warning(request, "Inicie sesión primero...")
            return redirect('transportes:loginFormulario')

def verLogueo(request):
    """Se usa para capturar los datos del usuario logueado y mostrarlos en un template

    Args:
        u: optiene los datos de un unico cliente, obtenido por el id 

    Returns:
        contexto: los datos capturados en `u`
        template:`transportes/login/usuarios/verLogueo.html`
    """
    login = request.session.get('logueo', False)
    if login:
        u = Cliente.objects.get(id = login[3])
        contexto = {'cli' : u}
        return render(request, 'transportes/login/usuarios/verLogueo.html',contexto)
    else:
        messages.warning(request, "Inicie sesión primero...")
        return redirect('transportes:loginFormulario')

def index(request):
    """Se usa para capturar los datos de los clientes y los vehiculos 
    y mostrarlos en un template

    Args:
        u: optiene los datos de un unico cliente, obtenido por el id 
        v: obtiene los datos de todos los vehiculos
        q: obtiene los datos de todos los clientes

    Returns:
        contexto: los datos capturados en `u`,`v`,`q`
        template:`transportes/index.html`
    """
    login = request.session.get('logueo', False)
    if login:
        v = Vehiculo.objects.all()
        q = Cliente.objects.all()
        u = Cliente.objects.get(id = login[3] )
        paginator = Paginator(q, 10) # Mostrar 10 registros por página...
        page_number = request.GET.get('page')
        #Sobreescribir la salida de la consulta.......
        q = paginator.get_page(page_number)
        contexto = {'datos': q, 'vehiculo':v,'cli':u}
        return render(request, 'transportes/index.html',contexto)
    else:
        messages.warning(request, "Inicie sesión primero...")
        return redirect('transportes:loginFormulario')

def loginFormulario(request):
    """Se usa para acceder a el formulario de logueo

    Returns:
        template:`transportes/login/login.html`
    """
    return render(request, 'transportes/login/login.html')

def login(request):
    """Se usa para capturar los datos ingresado en el formulario de logueo
        y validarlos en la base de datos 

    Args:
        user: El dato ingresado en el campo `usuario`
        passw: El dato ingresado en el campo `clave`
    Returns:
        template:`transportes:index`
    """
    if request.method == "POST":
        try:
            user = request.POST["usuario"]
            passw = request.POST["clave"]

            q = Cliente.objects.get(usuario = user, clave = passw)
            # crear la sesión 
            request.session["logueo"] = [q.nombre, q.apellido, q.rol, q.id, q.get_rol_display(),]
            messages.success(request, "Bienvenido!!")
            if q.rol == "P" :                
                return redirect('transportes:indexProveedor')
            else:
                return redirect('transportes:index')
   

        except Cliente.DoesNotExist:
            messages.error(request, "Usuario o contraseña incorrectos...")
            return redirect('transportes:loginFormulario')
        except Exception as e:
            messages.error(request, f"Error: {e}")
            return redirect('transportes:loginFormulario')
    else:
        messages.warning(request, "Usted no ha enviado datos...")
        return redirect('transportes:loginFormulario')

def logout(request):
    """Se usa cerrar la sesion de logueo 
    Returns:
        template:`transportes:index`
    """
    try:
        del request.session["logueo"]
        messages.success(request, "Sesión cerrada correctamente!!")
        return redirect('transportes:index')
    except Exception as e:
        messages.error(request, f"Error: {e}")
        return redirect('transportes:index')
#--------------------------USUARIOS-----------------------------------------------------

def listarUsuario(request):
    """Se usa para obtener los datos de todos los usuarios y enviarlos a un template 

    Args:
        q: recibe todos los objetos del modelo Cliente

    Returns:
        template:`transportes/login/usuarios/listarUsuario.html` y los datos capturados `q`
    """
    #Obtener la sesión
    login = request.session.get('logueo', False)
    if login:
        q = Cliente.objects.all()
        paginator = Paginator(q, 3) # Mostrar 3 registros por página...
        page_number = request.GET.get('page')
        #Sobreescribir la salida de la consulta.......
        q = paginator.get_page(page_number)
        contexto = {'datos': q}
        return render(request, 'transportes/login/usuarios/listarUsuario.html', contexto)
    else:
        messages.warning(request, "Inicie sesión primero...")
        return redirect('transportes:loginFormulario')

def registrarUsuario(request):
    """Se usa para retornar el template en la cual esta ubicado el formulario para registrar usuarios

    Returns:
        template:`transportes/login/usuarios/registrarUsuario.html`
    """
    return render(request, 'transportes/login/usuarios/registrarUsuario.html')
    

def guardarUsuario(request):
    """Obtener los datos ingresados y guardarlos en un nuevo registro de usuario

    Returns:
        template:`transportes:indexPrimary`
    """
    login = request.session.get('logueo', False)

    try:
        
            
            q = Cliente(nombre = request.POST["nombre"],
                        apellido = request.POST["apellido"],
                        correo = request.POST["correo"],
                        direccion = request.POST["direccion"],
                        documento = request.POST["documento"],
                        fecha_nacimiento = request.POST["fecha_nacimiento"],
                        usuario = request.POST["usuario"],
                        clave= request.POST["clave"],
                        rol = request.POST["rol"])
            q.save()
            messages.success(request, "Usuario guardado exitosamente")
        

    except Exception as e:
        messages.error(request, f"Error: {e}")
    if login:
        return redirect('transportes:listarUsuario')
    else:
        return redirect('transportes:indexPrimary')
        


def formularioEditar(request, id):
    """Retorna al formulario con la informacion del cliente y es editable

    Returns:
        template:`transportes/login/usuarios/editarUsuario.html`
    """
    login = request.session.get('logueo', False)
    if login:
        p = Cliente.objects.get(pk = id)
        contexto = { "cliente": p }
        return render(request, 'transportes/login/usuarios/editarUsuario.html', contexto)
    else:
        messages.warning(request, "Inicie sesión primero...")
        return redirect('transportes:loginFormulario')

'''Capturar y guardar los cambios ingresados'''
def actualizarUsuario(request):
    """Se usa para capturar y guardar los cambios ingresados

    Returns:
        template:`transportes/login/usuarios/editarUsuario.html`
    """
    login = request.session.get('logueo', False)

    try:
        if request.method == "POST":
            #Obtener la instancia de producto a modificar
            p =  Cliente.objects.get(pk = request.POST["id"])
            
            p.nombre = request.POST["nombre"]
            p.apellido = request.POST["apellido"]
            p.correo = request.POST["correo"]
            p.direccion = request.POST["direccion"]
            p.documento = request.POST["documento"]
            p.fecha_nacimiento = request.POST["fecha_nacimiento"]
            p.usuario = request.POST["usuario"]
            p.clave= request.POST["clave"]
            p.rol = request.POST["rol"]

            
            p.save()
            messages.success(request, "Usuario actualizado correctamente!!")
        else:
            messages.warning(request, "Usted no ha enviado datos...")
    except Exception as e:
        messages.error(request, f"Error: {e}")

    if login [2] == 'C':
        return redirect('transportes:verLogueo')
    elif login [2] == 'P':
        return redirect('transportes:indexProveedor')
    else:
        return redirect('transportes:listarUsuario')



def eliminarUsuario(request, id):
    """Se usa para obtener los datos de un usuario especifico y lo elimina

    Args:
        p: recibe un cliente especifico capturado por el id

    Returns:
        template:`transportes:listarUsuario` 
    """
    try:
        p =  Cliente.objects.get(pk = id)
        p.delete()
        messages.success(request, "Usuario eliminado correctamente!!")
    except IntegrityError:
        messages.warning(request, "No puede eliminar este producto porque otros registros están relacionados con él....")
    except Exception as e:
        messages.error(request, f"Error: {e}")
    
    return redirect('transportes:listarUsuario')

def buscarProducto(request):
    """Se usa para elaborar un filtro y hace una busqueda de un campo ingresado

    Args:
        q: recibe un cliente especifico capturado por el id

    Returns:
        template:`transportes/login/usuarios/listar_Usuario_ajax.html` y los datos capturados `q`
    """
    login = request.session.get('logueo', False)
    if login:
        if request.method == "POST":
            dato = request.POST["buscar"]
            q = Cliente.objects.filter( Q(nombre__icontains = dato))
            paginator = Paginator(q, 3) # Mostrar 3 registros por página...
            page_number = request.GET.get('page')
            #Sobreescribir la salida de la consulta.......
            q = paginator.get_page(page_number)
            contexto = { "datos": q }
            return render(request, 'transportes/login/usuarios/listar_Usuario_ajax.html', contexto)
        else:
            messages.error(request, "Error no envió datos...")
            return redirect('transportes:listarUsuario')
    else:
        messages.warning(request, "Inicie sesión primero...")
        return redirect('transportes:loginFormulario')
    


#-------------------------BENEFICIARIO--------------------------------------------

def listarBeneficiario(request):
    """Se usa para obtener los datos de todos los beneficiario y enviarlos a un template 

    Args:
        q: recibe todos los objetos del modelo Beneficiario

    Returns:
        template:`transportes/login/beneficiarios/listarBeneficiario.html` y los datos capturados `q`
    """
    login = request.session.get('logueo', False)

    if login and (login[2] == "A" or login[2] == "C"):
        b = Beneficiarios.objects.all()
        paginator = Paginator(b, 3) # Mostrar 3 registros por página...

        page_number = request.GET.get('page')
        #Sobreescribir la salida de la consulta.......
        b = paginator.get_page(page_number)
        contextob = {'datosB': b}

        return render(request, 'transportes/login/beneficiarios/listarBeneficiario.html', contextob)
    else:
        if login and (login[2] != "A" and login[2] != "C"):
            messages.warning(request, "Usted no tiene autorización para acceder al módulo...")
            return redirect('transportes:index')
        else:
            messages.warning(request, "Inicie sesión primero...")
            return redirect('transportes:loginFormulario')

def registrarBeneficiario(request):
    """Se usa para retornar el template en la cual esta ubicado el formulario para registrar benefificiarios

    Returns:
        template:`transportes/login/beneficiarios/registrarBeneficiario.html`
    """
    login = request.session.get('logueo', False)
    if login and (login[2] == "A" or login[2] == "C"):
        dato = login[0]
        u = Cliente.objects.filter( Q(nombre = dato))
        contexto = {'cli': u}
        return render(request, 'transportes/login/beneficiarios/registrarBeneficiario.html', contexto)
    else:
        if login and (login[2] != "A" and login[2] != "C"):
            messages.warning(request, "Usted no tiene autorización para acceder al módulo...")
            return redirect('transportes:index')
        else:
            messages.warning(request, "Inicie sesión primero...")
            return redirect('transportes:loginFormulario')

def guardarBeneficiario(request):
    """Obtener los datos ingresados y guardarlos en un nuevo registro de beneficiario

    Returns:
        template:`transportes:listarBeneficiario`
    """
    try:
        if request.method == "POST":
            u =  Cliente.objects.get(pk = request.POST["cliente"])
            q = Beneficiarios(
                cliente = u,
                nombre = request.POST["nombre"],
                apellido = request.POST["apellido"],
                documento = request.POST["documento"],
                fecha_nacimiento = request.POST["fecha_nacimiento"])
            q.save()

            messages.success(request, "Beneficiario guardado exitosamente")
        else:
            messages.warning(request, "No se han enviado datos...")

    except Exception as e:
        messages.error(request, f"Error: {e}")
    
    return redirect('transportes:listarBeneficiario')

def formularioEditarBeneficiario(request, id):
    """Retorna al formulario con la informacion del beneficiario y es editable

    Returns:
        template:`transportes/login/beneficiarios/editarBeneficiario.html`
    """
    login = request.session.get('logueo', False)
    if login and (login[2] == "A" or login[2] == "C"):
        p = Beneficiarios.objects.get(pk = id)
        c = Cliente.objects.all()
        contexto = { "beneficiario": p, "cli":c }
        return render(request, 'transportes/login/beneficiarios/editarBeneficiario.html', contexto)
    else:
        if login and (login[2] != "A" and login[2] != "C"):
            messages.warning(request, "Usted no tiene autorización para acceder al módulo...")
            return redirect('transportes:index')
        else:
            messages.warning(request, "Inicie sesión primero...")
            return redirect('transportes:loginFormulario')

def actualizarBeneficiario(request):
    """Se usa para capturar y guardar los cambios ingresados

    Returns:
        template:`transportes/login/usuarios/listarBeneficiario.html`
    """
    try:
        if request.method == "POST":
            #Obtener la instancia de producto a modificar
            p =  Beneficiarios.objects.get(pk = request.POST["id"])
            c =  Cliente.objects.get(pk = request.POST["cliente"])
            p.cliente = c
            p.nombre = request.POST["nombre"]
            p.apellido = request.POST["apellido"]
            p.documento = request.POST["documento"]
            p.fecha_nacimiento = request.POST["fecha_nacimiento"]
            

            p.save()
            messages.success(request, "Beneficiario actualizado correctamente!!")
        else:
            messages.warning(request, "Usted no ha enviado datos...")
    except Exception as e:
        messages.error(request, f"Error: {e}")
    
    return redirect('transportes:listarBeneficiario')

def eliminarBeneficiario(request, id):
    """Se usa para obtener los datos de un beneficiario especifico y lo elimina

    Args:
        p: recibe un beneficiario especifico capturado por el id

    Returns:
        template:`transportes:listarBeneficiario` 
    """
    try:
        p =  Beneficiarios.objects.get(pk = id)
        p.delete()
        messages.success(request, "Beneficiario eliminado correctamente!!")
    except IntegrityError:
        messages.warning(request, "No puede eliminar este producto porque otros registros están relacionados con él....")
    except Exception as e:
        messages.error(request, f"Error: {e}")
    
    return redirect('transportes:listarBeneficiario')

def buscarBeneficiario(request):
    """Se usa para elaborar un filtro y hace una busqueda de un campo ingresado

    Args:
        q: recibe un beneficiario especifico capturado por el id

    Returns:
        template:`transportes/login/usuarios/listar_Beneficiario_ajax.html` y los datos capturados `q`
    """
    login = request.session.get('logueo', False)
    if login and (login[2] == "A" or login[2] == "C"):
        if request.method == "POST":
            dato = request.POST["buscar"]
            q = Beneficiarios.objects.filter( Q(nombre__icontains = dato))
            
            paginator = Paginator(q, 3) # Mostrar 3 registros por página...

            page_number = request.GET.get('page')
            #Sobreescribir la salida de la consulta.......
            q = paginator.get_page(page_number)
            
            contexto = { "datosB": q }
            return render(request, 'transportes/login/beneficiarios/listar_Beneficiario_ajax.html', contexto)
        else:
            messages.error(request, "Error no envió datos...")
            return redirect('transportes:listarBeneficiario')
    else:
        if login and (login[2] != "A" and login[2] != "C"):
            messages.warning(request, "Usted no tiene autorización para acceder al módulo...")
            return redirect('transportes:index')
        else:
            messages.warning(request, "Inicie sesión primero...")
            return redirect('transportes:loginFormulario')

#--------------------COMENTARIOS----------------------------------------
def listarComentarios(request):
    """Se usa para obtener los datos de todos los comentario y enviarlos a un template 

    Args:
        q: recibe todos los objetos del modelo Comentarios

    Returns:
        template:`transportes/login/usuarios/listarComentarios.html` y los datos capturados `q`
    """
    login = request.session.get('logueo', False)

    if login:
        c = Comentarios.objects.all()
        paginator = Paginator(c, 3) # Mostrar 3 registros por página...

        page_number = request.GET.get('page')
        #Sobreescribir la salida de la consulta.......
        c = paginator.get_page(page_number)
        contextoC = {'datosC': c}

        return render(request, 'transportes/login/comentarios/listarComentarios.html', contextoC)
    else:
        messages.warning(request, "Inicie sesión primero...")
        return redirect('transportes:loginFormulario')

def listarComentariosProv(request):
    """Se usa para obtener los datos de todos los comentarios y enviarlos a un template 

    Args:
        q: recibe todos los objetos del modelo Comentarios

    Returns:
        template:`transportes/login/usuarios/listar_ComentariosProv.html` y los datos capturados `q`
    """
    login = request.session.get('logueo', False)

    if login and (login[2] == "A" or login[2] == "P"):       
        dato = login[3]
        c = Comentarios.objects.filter( Q(cliente__id = dato))
        paginator = Paginator(c, 3) # Mostrar 3 registros por página...

        page_number = request.GET.get('page')
        #Sobreescribir la salida de la consulta.......
        c = paginator.get_page(page_number)
        contextoC = {'datosC': c}

        return render(request, 'transportes/login/comentarios/listar_ComentariosProv.html', contextoC)
    else:
        if login and (login[2] != "A" and login[2] != "P"):
            messages.warning(request, "Usted no tiene autorización para acceder al módulo...")
            return redirect('transportes:index')
        else:
            messages.warning(request, "Inicie sesión primero...")
            return redirect('transportes:loginFormulario')

def registrarComentarios(request):
    """Se usa para retornar el template en la cual esta ubicado el formulario para registrar comentarios

    Returns:
        template:`transportes/login/usuarios/registrarComentarios.html`
    """
    login = request.session.get('logueo', False)
    if login:
        u = Cliente.objects.all()
        contexto = {'cli': u,}
        return render(request, 'transportes/login/comentarios/registrarComentarios.html',contexto)
    else:
        messages.warning(request, "Inicie sesión primero...")
        return redirect('transportes:loginFormulario')

def guardarComentarios(request):
    """Obtener los datos ingresados y guardarlos en un nuevo registro de comentario

    Returns:
        template:`transportes:indexPrimary`
    """
    try:
        if request.method == "POST":
            u =  Cliente.objects.get(pk = request.POST["cliente"])

            q = Comentarios(
                cliente = u,
                tipo = request.POST["tipo"],
                desc = request.POST["desc"])
            q.save()

            messages.success(request, "Comentario guardado exitosamente")
        else:
            messages.warning(request, "No se han enviado datos...")

    except Exception as e:
        messages.error(request, f"Error: {e}")
    
    return redirect('transportes:index')

def formularioEditarComentarios(request, id):
    """Retorna al formulario con la informacion del comentarios y es editable

    Returns:
        template:`transportes/login/usuarios/editarComentario.html`
    """
    login = request.session.get('logueo', False)
    if login:
        p = Comentarios.objects.get(pk = id)
        c = Cliente.objects.all()
        contexto = { "comentarios": p, "cliente":c }
        return render(request, 'transportes/login/comentarios/editarComentario.html', contexto)
    else:
        messages.warning(request, "Inicie sesión primero...")
        return redirect('transportes:loginFormulario')

def actualizarComentarios(request):
    """Capturar y guardar los cambios ingresados
    Returns:
        template:`transportes/login/usuarios/listarComentarios.html`
    """
    try:
        if request.method == "POST":
            #Obtener la instancia de producto a modificar
            p =  Comentarios.objects.get(pk = request.POST["id"])
            c =  Cliente.objects.get(pk = request.POST["cliente"])
            p.cliente = c
            p.tipo = request.POST["tipo"]
            p.desc = request.POST["desc"]
           
            p.save()
            messages.success(request, "Comentario actualizado correctamente!!")
        else:
            messages.warning(request, "Usted no ha enviado datos...")
    except Exception as e:
        messages.error(request, f"Error: {e}")
    
    return redirect('transportes:listarComentarios')

def eliminarComentarios(request, id):
    """Se usa para obtener los datos de un comentario especifico y lo elimina

    Args:
        p: recibe un comentario especifico capturado por el id

    Returns:
        template:`transportes:listarComentarios` 
    """
    try:
        p = Comentarios.objects.get(pk = id)
        p.delete()
        messages.success(request, "Comentario eliminado correctamente!!")
    except IntegrityError:
        messages.warning(request, "No puede eliminar este producto porque otros registros están relacionados con él....")
    except Exception as e:
        messages.error(request, f"Error: {e}")
    
    return redirect('transportes:listarComentarios')

def buscarComentarios(request):
    """Se usa para elaborar un filtro y hace una busqueda de un campo ingresado

    Args:
        q: recibe un comentarios especifico capturado por el id

    Returns:
        template:`transportes/login/usuarios/listar_Comentarios_ajax.html` y los datos capturados `q`
    """
    login = request.session.get('logueo', False)
    if login:
        if request.method == "POST":
            dato = request.POST["buscar"]
            q = Comentarios.objects.filter( Q(cliente__nombre = dato))
            
            paginator = Paginator(q, 3) # Mostrar 3 registros por página...

            page_number = request.GET.get('page')
            #Sobreescribir la salida de la consulta.......
            q = paginator.get_page(page_number)
            
            contexto = { "datosC": q }
            return render(request, 'transportes/login/comentarios/listar_Comentarios_ajax.html', contexto)
        else:
            messages.error(request, "Error no envió datos...")
            return redirect('transportes:listarComentarios')
    else:
        messages.warning(request, "Inicie sesión primero...")
        return redirect('transportes:loginFormulario')

        

#--------------------SERVICIOS----------------------------------------
def listarServicios(request):
    """Se usa para obtener los datos de todos los servicios y enviarlos a un template 

    Args:
        q: recibe todos los objetos del modelo Servicios

    Returns:
        template:`transportes/login/usuarios/listarServicios.html` y los datos capturados `q`
    """
    login = request.session.get('logueo', False)
    if login and (login[2] == "A"):
        t = Servicios.objects.all()
        paginator = Paginator(t, 3) # Mostrar 3 registros por página...

        page_number = request.GET.get('page')
        #Sobreescribir la salida de la consulta.......
        t = paginator.get_page(page_number)
        contextoT = {'datosT': t}

        return render(request, 'transportes/login/servicios/listarServicios.html', contextoT)
    else:
        if login and (login[2] != "A"):
            messages.warning(request, "Usted no tiene autorización para acceder al módulo...")
            return redirect('transportes:index')
        else:
            messages.warning(request, "Inicie sesión primero...")
            return redirect('transportes:loginFormulario')

def registrarServicios(request):
    """Se usa para retornar el template en la cual esta ubicado el formulario para registrar servicios

    Returns:
        template:`transportes/login/usuarios/registrarUsuario.html`
    """
    login = request.session.get('logueo', False)
    if login and (login[2] == "A"):
        return render(request, 'transportes/login/servicios/registrarServicios.html')
    else:
        if login and (login[2] != "A"):
            messages.warning(request, "Usted no tiene autorización para acceder al módulo...")
            return redirect('transportes:index')
        else:
            messages.warning(request, "Inicie sesión primero...")
            return redirect('transportes:loginFormulario')

def guardarServicios(request):
    """Obtener los datos ingresados y guardarlos en un nuevo registro de servicios

    Returns:
        template:`transportes:indexPrimary`
    """
    try:
        if request.method == "POST":
            q = Servicios(nombre = request.POST["nombre"],caracteristicas = request.POST["caracteristicas"])
            q.save()

            messages.success(request, "servicio guardado exitosamente")
        else:
            messages.warning(request, "No se han enviado datos...")

    except Exception as e:
        messages.error(request, f"Error: {e}")
    
    return redirect('transportes:listarServicios')

def formularioEditarServicios(request, id):
    """Retorna al formulario con la informacion del servicio y es editable

    Returns:
        template:`transportes/login/usuarios/editarServicios.html`
    """
    login = request.session.get('logueo', False)
    if login and (login[2] == "A"):
        p = Servicios.objects.get(pk = id)
        contexto = { "servicios": p }
        return render(request, 'transportes/login/servicios/editarServicios.html', contexto)
    else:
        if login and (login[2] != "A"):
            messages.warning(request, "Usted no tiene autorización para acceder al módulo...")
            return redirect('transportes:index')
        else:
            messages.warning(request, "Inicie sesión primero...")
            return redirect('transportes:loginFormulario')

def actualizarServicios(request):
    """Capturar y guardar los cambios ingresados

    Returns:
        template:`transportes/login/usuarios/listarServicios.html`
    """
    try:
        if request.method == "POST":
            #Obtener la instancia de producto a modificar
            p =  Servicios.objects.get(pk = request.POST["id"])
            
            p.nombre = request.POST["nombre"]
            p.caracteristicas = request.POST["caracteristicas"]
            p.save()
            messages.success(request, "servicio actualizado correctamente!!")
        else:
            messages.warning(request, "Usted no ha enviado datos...")
    except Exception as e:
        messages.error(request, f"Error: {e}")
    
    return redirect('transportes:listarServicios')

def eliminarServicios(request, id):
    """Se usa para obtener los datos de un servicio especifico y lo elimina

    Args:
        p: recibe un cliente especifico capturado por el id

    Returns:
        template:`transportes:listarServicios` 
    """
    try:
        p = Servicios.objects.get(pk = id)
        p.delete()
        messages.success(request, "servicio eliminado correctamente!!")
    except IntegrityError:
        messages.warning(request, "No puede eliminar este producto porque otros registros están relacionados con él....")
    except Exception as e:
        messages.error(request, f"Error: {e}")
    
    return redirect('transportes:listarServicios')

def buscarServicios(request):
    """Se usa para elaborar un filtro y hace una busqueda de un campo ingresado

    Args:
        q: recibe un servicio especifico capturado por el id

    Returns:
        template:`transportes/login/usuarios/listar_Servicios_ajax.html` y los datos capturados `q`
    """
    login = request.session.get('logueo', False)
    if login and (login[2] == "A"):
        if request.method == "POST":
            dato = request.POST["buscar"]
            q = Servicios.objects.filter( Q(nombre__icontains = dato))
            
            paginator = Paginator(q, 3) # Mostrar 3 registros por página...

            page_number = request.GET.get('page')
            #Sobreescribir la salida de la consulta.......
            q = paginator.get_page(page_number)
            
            contexto = { "datosT": q }
            return render(request, 'transportes/login/servicios/listar_Servicios_ajax.html', contexto)
        else:
            messages.error(request, "Error no envió datos...")
            return redirect('transportes:listarServicios')
    else:
        if login and (login[2] != "A"):
            messages.warning(request, "Usted no tiene autorización para acceder al módulo...")
            return redirect('transportes:index')
        else:
            messages.warning(request, "Inicie sesión primero...")
            return redirect('transportes:loginFormulario')



#--------------------PETICIONES----------------------------------------
def listarPeticiones(request):
    """Se usa para obtener los datos de todas las peticiones y enviarlos a un template 

    Args:
        q: recibe todos los objetos del modelo Peticiones

    Returns:
        template:`transportes/login/usuarios/listarPeticiones.html` y los datos capturados `q`
    """
    login = request.session.get('logueo', False)

    if login and (login[2] == "A" or login[2] == "P"):
        p = Peticiones.objects.all()
        paginator = Paginator(p, 3) # Mostrar 3 registros por página...

        page_number = request.GET.get('page')
        #Sobreescribir la salida de la consulta.......
        p = paginator.get_page(page_number)
        contextoP = {'datosP': p}
        return render(request, 'transportes/login/peticiones/listarPeticiones.html', contextoP)
    else:
        if login and (login[2] != "A" and login[2] != "C"):
            messages.warning(request, "Usted no tiene autorización para acceder al módulo...")
            return redirect('transportes:index')
        else:
            messages.warning(request, "Inicie sesión primero...")
            return redirect('transportes:loginFormulario')

def listarPeticionesCli(request):
    """Se usa para obtener los datos de todas las peticions y enviarlos a un template 

    Args:
        q: recibe todos los objetos del modelo Peticiones

    Returns:
        template:`transportes/login/usuarios/listarPeticionesProv.html` y los datos capturados `q`
    """
    login = request.session.get('logueo', False)

    if login and (login[2] == "A" or login[2] == "C"):
        dato = login[3]
        p = Peticiones.objects.filter( Q(beneficiarios__cliente_id = dato))
        paginator = Paginator(p, 3) # Mostrar 3 registros por página...

        page_number = request.GET.get('page')
        #Sobreescribir la salida de la consulta.......
        p = paginator.get_page(page_number)

        contextoP = {'datosP': p}
        return render(request, 'transportes/login/peticiones/listarPeticionesCli.html', contextoP)
    else:
        if login and (login[2] != "A" and login[2] != "C"):
            messages.warning(request, "Usted no tiene autorización para acceder al módulo...")
            return redirect('transportes:index')
        else:
            messages.warning(request, "Inicie sesión primero...")
            return redirect('transportes:loginFormulario') 


def listarPeticionesProv(request):
    """Se usa para obtener los datos de todas las peticions y enviarlos a un template 

    Args:
        q: recibe todos los objetos del modelo Peticiones

    Returns:
        template:`transportes/login/usuarios/listarPeticionesProv.html` y los datos capturados `q`
    """
    login = request.session.get('logueo', False)

    if login and (login[2] == "A" or login[2] == "P"):
        dato = login[3]
        p = Peticiones.objects.filter( Q(cliente__id = dato) & Q(estado = 'Pendiente'))
        paginator = Paginator(p, 3) # Mostrar 3 registros por página...

        page_number = request.GET.get('page')
        #Sobreescribir la salida de la consulta.......
        p = paginator.get_page(page_number)

        contextoP = {'datosP': p}
        return render(request, 'transportes/login/peticiones/listarPeticionesProv.html', contextoP)
    else:
        if login and (login[2] != "A" and login[2] != "P"):
            messages.warning(request, "Usted no tiene autorización para acceder al módulo...")
            return redirect('transportes:index')
        else:
            messages.warning(request, "Inicie sesión primero...")
            return redirect('transportes:loginFormulario') 

def listarPeticionesAceptadas(request):
    """Se usa para obtener los datos de todas las peticions y enviarlos a un template 

    Args:
        q: recibe todos los objetos del modelo Peticiones

    Returns:
        template:`transportes/login/usuarios/listarPeticionesProv.html` y los datos capturados `q`
    """
    login = request.session.get('logueo', False)

    if login and (login[2] == "A" or login[2] == "P"):
        dato = login[3]
        p = Peticiones.objects.filter( Q(cliente__id = dato) & Q(estado = 'Aceptada'))
        paginator = Paginator(p, 3) # Mostrar 3 registros por página...

        page_number = request.GET.get('page')
        #Sobreescribir la salida de la consulta.......
        p = paginator.get_page(page_number)

        contextoP = {'datosP': p}
        return render(request, 'transportes/login/peticiones/listarPeticionesAceptadas.html', contextoP)
    else:
        if login and (login[2] != "A" and login[2] != "P"):
            messages.warning(request, "Usted no tiene autorización para acceder al módulo...")
            return redirect('transportes:index')
        else:
            messages.warning(request, "Inicie sesión primero...")
            return redirect('transportes:loginFormulario')          

def registrarPeticiones(request):
    """Se usa para retornar el template en la cual esta ubicado el formulario para registrar peticiones

    Returns:
        template:`transportes/login/usuarios/registrarPeticiones.html`
    """
    login = request.session.get('logueo', False)
    if login and (login[2] == "A" or login[2] == "C"):
        dato = login[3]
        b = Beneficiarios.objects.filter( Q(cliente__id = dato))
        c = Cliente.objects.all()
        s = Servicios.objects.all()
        contexto = {'cli':c,'servicios':s, 'beneficiario': b}
        return render(request, 'transportes/login/peticiones/registrarPeticiones.html',contexto)
    else:
        if login and (login[2] != "A" and login[2] != "C"):
            messages.warning(request, "Usted no tiene autorización para acceder al módulo...")
            return redirect('transportes:index')
        else:
            messages.warning(request, "Inicie sesión primero...")
            return redirect('transportes:loginFormulario')

def guardarPeticiones(request):
    """Obtener los datos ingresados y guardarlos en un nuevo registro de peticion

    Returns:
        template:`transportes:index`
    """
    try:
        c =  Cliente.objects.get(pk = request.POST["cliente"])
        s =  Servicios.objects.get(pk = request.POST["servicios"])
        b =  Beneficiarios.objects.get(pk = request.POST["beneficiario"])
        if request.method == "POST":
            q = Peticiones(
                cliente = c,
                servicios = s,
                beneficiarios = b,
                estado = request.POST["estado"],
                direccion = request.POST["direccion"],
                colegio = request.POST["colegio"],
                horario = request.POST["horario"],
                comentario_add = request.POST["comentario_add"])
            q.save()

            messages.success(request, "Peticion guardado exitosamente")
        else:
            messages.warning(request, "No se han enviado datos...")

    except Exception as e:
        messages.error(request, f"Error: {e}")
    
    return redirect('transportes:index')

def formularioEditarPeticiones(request, id):
    """Retorna al formulario con la informacion de la peticion y es editable

    Returns:
        template:`transportes/login/usuarios/editarPeticiones.html`
    """
    login = request.session.get('logueo', False)
    if login and (login[2] == "A" or login[2] == "P"):
        p = Peticiones.objects.get(pk = id)
        s = Servicios.objects.all()
        c = Cliente.objects.all()
        b = Beneficiarios.objects.all()
        contexto = { "peticiones": p, "cli":c, 'servicios':s, 'beneficiario': b }
        return render(request, 'transportes/login/peticiones/editarPeticiones.html', contexto)
    else:
        if login and (login[2] != "A" and login[2] != "P"):
            messages.warning(request, "Usted no tiene autorización para acceder al módulo...")
            return redirect('transportes:index')
        else:
            messages.warning(request, "Inicie sesión primero...")
            return redirect('transportes:loginFormulario')

def actualizarPeticiones(request):
    """Capturar y guardar los cambios ingresados

    Returns:
        template:`transportes/login/peticiones/listarPeticiones.html`
    """
    try:
        if request.method == "POST":
            #Obtener la instancia de producto a modificar
            p =  Peticiones.objects.get(pk = request.POST["id"])
            s = Servicios.objects.get(pk = request.POST["servicios"])
            c = Cliente.objects.get(pk = request.POST["cliente"])
            b = Beneficiarios.objects.get(pk = request.POST["beneficiario"])

            p.cliente = c
            p.servicios = s
            p.beneficiarios = b
            p.estado = request.POST["estado"]
            p.direccion = request.POST["direccion"]
            p.colegio = request.POST["colegio"]
            p.horario = request.POST["horario"]
            p.comentario_add = request.POST["comentario_add"]
           

            p.save()
            messages.success(request, "Peticion actualizado correctamente!!")
        else:
            messages.warning(request, "Usted no ha enviado datos...")
    except Exception as e:
        messages.error(request, f"Error: {e}")
    login = request.session.get('logueo', False)
    if login [2] == 'P':
        return redirect('transportes:listarPeticionesProv')
    else:
        return redirect('transportes:listarPeticiones')


def eliminarPeticiones(request, id):
    """Se usa para obtener los datos de un peticiones especifico y lo elimina

    Args:
        p: recibe una peticion especifico capturado por el id

    Returns:
        template:`transportes:listarUsuario` 
    """
    try:
        p =  Peticiones.objects.get(pk = id)
        p.delete()
        messages.success(request, "Peticion eliminado correctamente!!")
    except IntegrityError:
        messages.warning(request, "No puede eliminar este producto porque otros registros están relacionados con él....")
    except Exception as e:
        messages.error(request, f"Error: {e}")
    
    return redirect('transportes:listarPeticiones')

def buscarPeticiones(request):
    """Se usa para elaborar un filtro y hace una busqueda de un campo ingresado

    Args:
        q: recibe una peticion especifica capturada por el id

    Returns:
        template:`transportes/login/usuarios/listar_Peticiones_ajax.html` y los datos capturados `q`
    """
    login = request.session.get('logueo', False)
    if login and (login[2] == "A" or login[2] == "C"):
        if request.method == "POST":
            dato = request.POST["buscar"]
            q = Peticiones.objects.filter( Q(colegio__icontains = dato ) |Q(direccion__icontains = dato ))
            
            paginator = Paginator(q, 3) # Mostrar 3 registros por página...

            page_number = request.GET.get('page')
            #Sobreescribir la salida de la consulta.......
            q = paginator.get_page(page_number)
            
            contexto = { "datosP": q }
            return render(request, 'transportes/login/peticiones/listar_Peticiones_ajax.html', contexto)
        else:
            messages.error(request, "Error no envió datos...")
            return redirect('transportes:listarPeticiones')
    else:
        if login and (login[2] != "A" and login[2] != "C"):
            messages.warning(request, "Usted no tiene autorización para acceder al módulo...")
            return redirect('transportes:index')
        else:
            messages.warning(request, "Inicie sesión primero...")
            return redirect('transportes:loginFormulario')

def boton(request,id):
    try:
        #Obtener la instancia de producto a modificar
        login = request.session.get('logueo', False)
        dato = login[0]
        a = Vehiculo.objects.get(cliente__nombre = dato)
        p = Peticiones.objects.get(pk = id)
        if a.actual > 0:
            a.actual -= 1
            p.estado = 'Aceptada'
            p.save()
            a.save()
            messages.success(request, "Peticion actualizado correctamente!!")
        else:
            messages.warning(request, "No tiene disponibilidad")

    except IntegrityError:
        messages.warning(request, "Usted no ha enviado datos...")
    except Exception as e:
        messages.error(request, f"Error: {e}")
    
    return redirect('transportes:listarPeticionesProv')

def rechazar(request,id):
    try:
        #Obtener la instancia de producto a modificar
        p = Peticiones.objects.get(pk = id)
        p.estado = 'Rechazada'
        p.save()
        messages.success(request, "Peticion actualizado correctamente!!")
    except IntegrityError:
        messages.warning(request, "Usted no ha enviado datos...")
    except Exception as e:
        messages.error(request, f"Error: {e}")
    
    return redirect('transportes:listarPeticionesProv')
 
    
#--------------------VEHICULOS----------------------------------------

def listarVehiculo(request):
    """Se usa para obtener los datos de todos los vehiculos y enviarlos a un template 

    Args:
        q: recibe todos los objetos del modelo Vehiculo

    Returns:
        template:`transportes/login/usuarios/listarVehiculo.html` y los datos capturados `q`
    """
    login = request.session.get('logueo', False)

    if login and (login[2] == "A" or login[2] == "P"):
        b = Vehiculo.objects.all()
        paginator = Paginator(b, 3) # Mostrar 3 registros por página...

        page_number = request.GET.get('page')
        #Sobreescribir la salida de la consulta.......
        v = paginator.get_page(page_number)
        contextob = {'datosV': v}

        return render(request, 'transportes/login/vehiculo/listarVehiculo.html', contextob)
    else:
        if login and (login[2] != "A" and login[2] != "P"):
            messages.warning(request, "Usted no tiene autorización para acceder al módulo...")
            return redirect('transportes:index')
        else:
            messages.warning(request, "Inicie sesión primero...")
            return redirect('transportes:loginFormulario')

def listarVehiculoProv(request):
    """Se usa para obtener vehiculo del usuario logueado y enviarlos a un template 

    Args:
        q: recibe todos los objetos del modelo Vehiculo

    Returns:
        template:`transportes/login/usuarios/listarVehiculoProv.html` y los datos capturados `q`
    """
    login = request.session.get('logueo', False)

    if login and (login[2] == "A" or login[2] == "P"):
        dato = login[3]
        b = Vehiculo.objects.filter( Q(cliente__id = dato))
        paginator = Paginator(b, 3) # Mostrar 3 registros por página...

        page_number = request.GET.get('page')
        #Sobreescribir la salida de la consulta.......
        v = paginator.get_page(page_number)
        contextob = {'datosV': v}

        return render(request, 'transportes/login/vehiculo/listarVehiculoProv.html', contextob)
    else:
        if login and (login[2] != "A" and login[2] != "P"):
            messages.warning(request, "Usted no tiene autorización para acceder al módulo...")
            return redirect('transportes:index')
        else:
            messages.warning(request, "Inicie sesión primero...")
            return redirect('transportes:loginFormulario')

def registrarVehiculo(request):
    """Se usa para retornar el template en la cual esta ubicado el formulario para registrar vehiculo

    Returns:
        template:`transportes/login/usuarios/registrarVehiculo.html`
    """
    login = request.session.get('logueo', False)
    if login and (login[2] == "A" or login[2] == "P"):
        dato = login[3]
        u = Cliente.objects.filter( Q(id = dato))
        contexto = {'cliente': u}
        return render(request, 'transportes/login/vehiculo/registrarVehiculo.html', contexto)
    else:
        if login and (login[2] != "A" and login[2] != "P"):
            messages.warning(request, "Usted no tiene autorización para acceder al módulo...")
            return redirect('transportes:index')
        else:
            messages.warning(request, "Inicie sesión primero...")
            return redirect('transportes:loginFormulario')

def guardarVehiculo(request):
    """Obtener los datos ingresados y guardarlos en un nuevo registro de vehiculo

    Returns:
        template:`transportes:indexPrimary`
    """
    login = request.session.get('logueo', False)

    try:
        if request.method == "POST":
            
            
                
            u = Cliente.objects.get(pk = request.POST["cliente"])
            q = Vehiculo(
                cliente = u,
                placa = request.POST["placa"],
                marca = request.POST["marca"],
                color = request.POST["color"],
                capacidad = request.POST["capacidad"],
                actual = request.POST["actual"]

                )
            q.save()

            messages.success(request, "Vehiculo guardado exitosamente")
        else:
            messages.warning(request, "No se han enviado datos...")

    except Exception as e:
        messages.error(request, f"Error: {e}")
    if login[2] == 'P':
        return redirect('transportes:listarVehiculoProv')
    else:
        return redirect('transportes:listarVehiculo')


def formularioEditarVehiculo(request, id):
    """Retorna al formulario con la informacion del vehiculo y es editable

    Returns:
        template:`transportes/login/usuarios/editarVehiculo.html`
    """
    login = request.session.get('logueo', False)
    if login and (login[2] == "A" or login[2] == "P"):
        p = Vehiculo.objects.get(pk = id)
        c = Cliente.objects.all()
        contexto = { "vehiculo": p, "cliente":c }
        return render(request, 'transportes/login/vehiculo/editarVehiculo.html', contexto)
    else:
        if login and (login[2] != "A" and login[2] != "P"):
            messages.warning(request, "Usted no tiene autorización para acceder al módulo...")
            return redirect('transportes:index')
        else:
            messages.warning(request, "Inicie sesión primero...")
            return redirect('transportes:loginFormulario')

'''Capturar y guardar los cambios ingresados'''
def actualizarVehiculo(request):
    """Capturar y guardar los cambios ingresados

    Returns:
        template:`transportes/login/vehiculos/listarVehiculo.html`
    """
    login = request.session.get('logueo', False)

    try:
        if request.method == "POST":
            #Obtener la instancia de producto a modificar
            p =  Vehiculo.objects.get(pk = request.POST["id"])
            c =  Cliente.objects.get(pk = request.POST["cliente"])
            p.cliente = c
            p.placa = request.POST["placa"]
            p.marca = request.POST["marca"]
            p.color = request.POST["color"]
            p.capacidad = request.POST["capacidad"]
            p.actual = request.POST["actual"]


            p.save()
            messages.success(request, "Vehiculo actualizado correctamente!!")
        else:
            messages.warning(request, "Usted no ha enviado datos...")
    except Exception as e:
        messages.error(request, f"Error: {e}")
    
    if login[2] == 'P':
        return redirect('transportes:listarVehiculoProv')
    else:
        return redirect('transportes:listarVehiculo')
def eliminarVehiculo(request, id):
    """Se usa para obtener los datos de un vehiculo especifico y lo elimina

    Args:
        p: recibe un vehiculo especifico capturado por el id

    Returns:
        template:`transportes:listarVehiculo` 
    """
    try:
        p =Vehiculo.objects.get(pk = id)
        p.delete()
        messages.success(request, "Vehiculo eliminado correctamente!!")
    except IntegrityError:
        messages.warning(request, "No puede eliminar este producto porque otros registros están relacionados con él....")
    except Exception as e:
        messages.error(request, f"Error: {e}")
    
    return redirect('transportes:listarVehiculo')

def buscarVehiculo(request):
    """Se usa para elaborar un filtro y hace una busqueda de un campo ingresado

    Args:
        q: recibe un vehiculo especifico capturado por el id

    Returns:
        template:`transportes/login/usuarios/listar_Vehiculo_ajax.html` y los datos capturados `q`
    """
    login = request.session.get('logueo', False)
    if login and (login[2] == "A" or login[2] == "P"):
        if request.method == "POST":
            dato = request.POST["buscar"]
            q = Vehiculo.objects.filter( Q(id__icontains = dato))
            
            paginator = Paginator(q, 3) # Mostrar 3 registros por página...

            page_number = request.GET.get('page')
            #Sobreescribir la salida de la consulta.......
            q = paginator.get_page(page_number)
            
            contexto = { "datosV": q }
            return render(request, 'transportes/login/vehiculo/listar_Vehiculo_ajax.html', contexto)
        else:
            messages.error(request, "Error no envió datos...")
            return redirect('transportes:listarVehiculo')
    else:
        if login and (login[2] != "A" and login[2] != "P"):
            messages.warning(request, "Usted no tiene autorización para acceder al módulo...")
            return redirect('transportes:index')
        else:
            messages.warning(request, "Inicie sesión primero...")
            return redirect('transportes:loginFormulario')

def verUsuario(request, id):
    login = request.session.get('logueo', False)

    if login:
        p = Cliente.objects.get(pk = id)
        dato = p.nombre
        v = Vehiculo.objects.filter( Q(cliente__nombre = dato))
        c = Comentarios.objects.filter( Q(cliente__nombre = dato))
        contexto = { "cli": p, "comentarios":c, 'vehiculo':v}
        return render(request, 'transportes/login/usuarios/verUsuario.html', contexto)
    else:
        messages.warning(request, "Inicie sesión primero...")
        return redirect('transportes:loginFormulario')