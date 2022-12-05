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
    return render(request, 'transportes/indexPrimary.html')

def indexProveedor(request):

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
    login = request.session.get('logueo', False)
    if login:
        u = Cliente.objects.get(id = login[3])
        contexto = {'cli' : u}
        return render(request, 'transportes/login/usuarios/verLogueo.html',contexto)
    else:
        messages.warning(request, "Inicie sesión primero...")
        return redirect('transportes:loginFormulario')

def index(request):
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
    return render(request, 'transportes/login/login.html')

def login(request):
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

    Args:
        
    
    Returns:
        
    """
    try:
        if request.method == "POST":
            if request.FILES:
                fss = FileSystemStorage()
                f = request.FILES["foto"]
                file = fss.save("transportes/fotos/" + f.name, f)
            else:
                file = 'transportes/fotos/default.webp'
            
            q = Cliente(nombre = request.POST["nombre"],
                        apellido = request.POST["apellido"],
                        correo = request.POST["correo"],
                        direccion = request.POST["direccion"],
                        documento = request.POST["documento"],
                        fecha_nacimiento = request.POST["fecha_nacimiento"],
                        foto = file,
                        usuario = request.POST["usuario"],
                        clave= request.POST["clave"],
                        rol = request.POST["rol"])
            q.save()
            messages.success(request, "Usuario guardado exitosamente")
        else:
            messages.warning(request, "No se han enviado datos...")

    except Exception as e:
        messages.error(request, f"Error: {e}")
    
    return redirect('transportes:indexPrimary')
        

'''Retorna a un template con la información de un usuario especifico'''



'''Retorna al formulario con la informacion del cliente y es editable'''
def formularioEditar(request, id):
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
            p.foto = request.POST["foto"]
            p.usuario = request.POST["usuario"]
            p.clave= request.POST["clave"]
            p.rol = request.POST["rol"]

            
            p.save()
            messages.success(request, "Usuario actualizado correctamente!!")
        else:
            messages.warning(request, "Usted no ha enviado datos...")
    except Exception as e:
        messages.error(request, f"Error: {e}")
    
    return redirect('transportes:listarUsuario')

'''Toma un usuario especifico y lo elimina '''
def eliminarUsuario(request, id):
    try:
        p =  Cliente.objects.get(pk = id)
         #Obtener ruta de la foto
        foto = str(BASE_DIR) + str(p.foto.url) 
        
        #Averiguar si existe la foto en esa ruta obtenida
        if path.exists(foto):
            #Caso especial no borrar foto por defecto.
            if p.foto.url != '/uploads/transportes/fotos/default.webp':
                remove(foto)
        else:
            messages.warning(request, "No se encontró la foto...")
        p.delete()
        messages.success(request, "Usuario eliminado correctamente!!")
    except IntegrityError:
        messages.warning(request, "No puede eliminar este producto porque otros registros están relacionados con él....")
    except Exception as e:
        messages.error(request, f"Error: {e}")
    
    return redirect('transportes:listarUsuario')

'''Elabora un filtro y hace una busqueda de un campo ingresado'''
def buscarProducto(request):
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

'''Obtener los Beneficiarios y enviarlos a un template'''
def listarBeneficiario(request):
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

'''Retorna a al template para registrar nuevos beneficiarios'''
def registrarBeneficiario(request):
    login = request.session.get('logueo', False)
    if login and (login[2] == "A" or login[2] == "C"):
        u = Cliente.objects.all()
        contexto = {'cli': u}
        return render(request, 'transportes/login/beneficiarios/registrarBeneficiario.html', contexto)
    else:
        if login and (login[2] != "A" and login[2] != "C"):
            messages.warning(request, "Usted no tiene autorización para acceder al módulo...")
            return redirect('transportes:index')
        else:
            messages.warning(request, "Inicie sesión primero...")
            return redirect('transportes:loginFormulario')

'''Obtener los datos ingresados y guardarlos en un nuevo registro de beneficiario'''
def guardarBeneficiario(request):
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

'''Retorna al formulario con la informacion del beneficiario y es editable'''
def formularioEditarBeneficiario(request, id):
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

'''Capturar y guardar los cambios ingresados'''
def actualizarBeneficiario(request):
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

'''Toma un beneficiario especifico y lo elimina '''
def eliminarBeneficiario(request, id):
    try:
        p =  Beneficiarios.objects.get(pk = id)
        p.delete()
        messages.success(request, "Beneficiario eliminado correctamente!!")
    except IntegrityError:
        messages.warning(request, "No puede eliminar este producto porque otros registros están relacionados con él....")
    except Exception as e:
        messages.error(request, f"Error: {e}")
    
    return redirect('transportes:listarBeneficiario')

'''Elabora un filtro y hace una busqueda de un campo ingresado'''
def buscarBeneficiario(request):
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
'''Obtener los comentarios y enviarlos a un template'''
def listarComentarios(request):
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
    login = request.session.get('logueo', False)

    if login and (login[2] == "A" or login[2] == "P"):       
        dato = login[0]
        c = Comentarios.objects.filter( Q(cliente__nombre = dato))
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
    login = request.session.get('logueo', False)
    if login:
        u = Cliente.objects.all()
        contexto = {'cli': u,}
        return render(request, 'transportes/login/comentarios/registrarComentarios.html',contexto)
    else:
        messages.warning(request, "Inicie sesión primero...")
        return redirect('transportes:loginFormulario')

'''Obtener los datos ingresados y guardarlos en un nuevo registro de Comentarios'''
def guardarComentarios(request):
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
    
    return redirect('transportes:listarComentarios')

'''Retorna al formulario con la informacion del comentario y es editable'''
def formularioEditarComentarios(request, id):
    login = request.session.get('logueo', False)
    if login:
        p = Comentarios.objects.get(pk = id)
        c = Cliente.objects.all()
        contexto = { "comentarios": p, "cliente":c }
        return render(request, 'transportes/login/comentarios/editarComentario.html', contexto)
    else:
        messages.warning(request, "Inicie sesión primero...")
        return redirect('transportes:loginFormulario')

'''Capturar y guardar los cambios ingresados'''
def actualizarComentarios(request):
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

'''Toma un comentario especifico y lo elimina '''
def eliminarComentarios(request, id):
    try:
        p = Comentarios.objects.get(pk = id)
        p.delete()
        messages.success(request, "Comentario eliminado correctamente!!")
    except IntegrityError:
        messages.warning(request, "No puede eliminar este producto porque otros registros están relacionados con él....")
    except Exception as e:
        messages.error(request, f"Error: {e}")
    
    return redirect('transportes:listarComentarios')

'''Elabora un filtro y hace una busqueda de un campo ingresado'''
def buscarComentarios(request):
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
'''Obtener los servicios y enviarlos a un template'''
def listarServicios(request):
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

'''Retorna a al template para registrar nuevos servicios'''
def registrarServicios(request):
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

'''Obtener los datos ingresados y guardarlos en un nuevo registro de servicios'''
def guardarServicios(request):
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

'''Retorna al formulario con la informacion del servicio y es editable'''
def formularioEditarServicios(request, id):
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

'''Capturar y guardar los cambios ingresados'''
def actualizarServicios(request):
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

'''Toma un beneficiario especifico y lo elimina '''
def eliminarServicios(request, id):
    try:
        p = Servicios.objects.get(pk = id)
        p.delete()
        messages.success(request, "servicio eliminado correctamente!!")
    except IntegrityError:
        messages.warning(request, "No puede eliminar este producto porque otros registros están relacionados con él....")
    except Exception as e:
        messages.error(request, f"Error: {e}")
    
    return redirect('transportes:listarServicios')

'''Elabora un filtro y hace una busqueda de un campo ingresado'''
def buscarServicios(request):
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
'''Obtener los peticiones y enviarlos a un template'''
def listarPeticiones(request):
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

def listarPeticionesProv(request):
    login = request.session.get('logueo', False)

    if login and (login[2] == "A" or login[2] == "P"):
        dato = login[0]
        p = Peticiones.objects.filter( Q(cliente__nombre = dato))
        paginator = Paginator(p, 3) # Mostrar 3 registros por página...

        page_number = request.GET.get('page')
        #Sobreescribir la salida de la consulta.......
        p = paginator.get_page(page_number)
        contextoP = {'datosP': p}

        return render(request, 'transportes/login/peticiones/listarPeticionesProv.html', contextoP)
    else:
        if login and (login[2] != "A" and login[2] != "C"):
            messages.warning(request, "Usted no tiene autorización para acceder al módulo...")
            return redirect('transportes:index')
        else:
            messages.warning(request, "Inicie sesión primero...")
            return redirect('transportes:loginFormulario')           

'''Retorna a al template para registrar nuevos peticiones'''
def registrarPeticiones(request):
    login = request.session.get('logueo', False)
    if login and (login[2] == "A" or login[2] == "C"):
        
        c = Cliente.objects.all()
        s = Servicios.objects.all()
        contexto = {'cli':c,'servicios':s}
        return render(request, 'transportes/login/peticiones/registrarPeticiones.html',contexto)
    else:
        if login and (login[2] != "A" and login[2] != "C"):
            messages.warning(request, "Usted no tiene autorización para acceder al módulo...")
            return redirect('transportes:index')
        else:
            messages.warning(request, "Inicie sesión primero...")
            return redirect('transportes:loginFormulario')

'''Obtener los datos ingresados y guardarlos en un nuevo registro de peticion'''
def guardarPeticiones(request):
    try:
        c =  Cliente.objects.get(pk = request.POST["cliente"])
        s =  Servicios.objects.get(pk = request.POST["servicios"])


        if request.method == "POST":
            q = Peticiones(
                cliente = c,
                servicios = s,
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

'''Retorna al formulario con la informacion de la peticion y es editable'''
def formularioEditarPeticiones(request, id):
    login = request.session.get('logueo', False)
    if login and (login[2] == "A" or login[2] == "C"):
        p = Peticiones.objects.get(pk = id)
        s = Servicios.objects.all()
        c = Cliente.objects.all()
        contexto = { "peticiones": p, "cli":c, 'servicios':s }
        return render(request, 'transportes/login/peticiones/editarPeticiones.html', contexto)
    else:
        if login and (login[2] != "A" and login[2] != "C"):
            messages.warning(request, "Usted no tiene autorización para acceder al módulo...")
            return redirect('transportes:index')
        else:
            messages.warning(request, "Inicie sesión primero...")
            return redirect('transportes:loginFormulario')

'''Capturar y guardar los cambios ingresados'''
def actualizarPeticiones(request):
    try:
        if request.method == "POST":
            #Obtener la instancia de producto a modificar
            p =  Peticiones.objects.get(pk = request.POST["id"])
            s = Servicios.objects.get(pk = request.POST["servicios"])
            c = Cliente.objects.get(pk = request.POST["cliente"])


            p.cliente = c
            p.servicios = s
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
    
    return redirect('transportes:listarPeticiones')

'''Toma una petición especifico y lo elimina '''
def eliminarPeticiones(request, id):
    try:
        p =  Peticiones.objects.get(pk = id)
        p.delete()
        messages.success(request, "Peticion eliminado correctamente!!")
    except IntegrityError:
        messages.warning(request, "No puede eliminar este producto porque otros registros están relacionados con él....")
    except Exception as e:
        messages.error(request, f"Error: {e}")
    
    return redirect('transportes:listarPeticiones')

'''Elabora un filtro y hace una busqueda de un campo ingresado'''
def buscarPeticiones(request):
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

    
#--------------------VEHICULOS----------------------------------------

'''Obtener los Vehiculos y enviarlos a un template'''
def listarVehiculo(request):
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
    login = request.session.get('logueo', False)

    if login and (login[2] == "A" or login[2] == "P"):
        dato = login[0]
        b = Vehiculo.objects.filter( Q(cliente__nombre = dato))
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

'''Retorna a al template para registrar nuevos vehiculos'''
def registrarVehiculo(request):
    login = request.session.get('logueo', False)
    if login and (login[2] == "A" or login[2] == "P"):
        u = Cliente.objects.all()
        contexto = {'cliente': u}
        return render(request, 'transportes/login/vehiculo/registrarVehiculo.html', contexto)
    else:
        if login and (login[2] != "A" and login[2] != "P"):
            messages.warning(request, "Usted no tiene autorización para acceder al módulo...")
            return redirect('transportes:index')
        else:
            messages.warning(request, "Inicie sesión primero...")
            return redirect('transportes:loginFormulario')

'''Obtener los datos ingresados y guardarlos en un nuevo registro de vehiculo'''
def guardarVehiculo(request):
    try:
        if request.method == "POST":
            
            if request.FILES:
                fss = FileSystemStorage()
                f = request.FILES["foto"]
                file = fss.save("transportes/fotos/" + f.name, f)
            else:
                file = 'transportes/fotos/default.webp'
                
            u = Cliente.objects.get(pk = request.POST["cliente"])
            q = Vehiculo(
                proveedor = u,
                placa = request.POST["placa"],
                marca = request.POST["marca"],
                color = request.POST["color"],
                foto = file)
            q.save()

            messages.success(request, "Vehiculo guardado exitosamente")
        else:
            messages.warning(request, "No se han enviado datos...")

    except Exception as e:
        messages.error(request, f"Error: {e}")
    
    return redirect('transportes:listarVehiculo')

'''Retorna al formulario con la informacion del vehiculo y es editable'''
def formularioEditarVehiculo(request, id):
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
    try:
        if request.method == "POST":
            #Obtener la instancia de producto a modificar
            p =  Vehiculo.objects.get(pk = request.POST["id"])
            c =  Cliente.objects.get(pk = request.POST["cliente"])
            p.cliente = c
            p.placa = request.POST["placa"]
            p.marca = request.POST["marca"]
            p.color = request.POST["color"]
            p.foto = request.POST["foto"]

            p.save()
            messages.success(request, "Vehiculo actualizado correctamente!!")
        else:
            messages.warning(request, "Usted no ha enviado datos...")
    except Exception as e:
        messages.error(request, f"Error: {e}")
    
    return redirect('transportes:listarVehiculo')

'''Toma un vehiculo especifico y lo elimina '''
def eliminarVehiculo(request, id):
    try:
        p =Vehiculo.objects.get(pk = id)
        
         #Obtener ruta de la foto
        foto = str(BASE_DIR) + str(p.foto.url) 
        
        #Averiguar si existe la foto en esa ruta obtenida
        if path.exists(foto):
            #Caso especial no borrar foto por defecto.
            if p.foto.url != '/uploads/transportes/fotos/default.webp':
                remove(foto)
        else:
            messages.warning(request, "No se encontró la foto...")
            
        p.delete()
        messages.success(request, "Vehiculo eliminado correctamente!!")
    except IntegrityError:
        messages.warning(request, "No puede eliminar este producto porque otros registros están relacionados con él....")
    except Exception as e:
        messages.error(request, f"Error: {e}")
    
    return redirect('transportes:listarVehiculo')

'''Elabora un filtro y hace una busqueda de un campo ingresado'''
def buscarVehiculo(request):
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
        c = Comentarios.objects.all()
        v = Vehiculo.objects.all()
        contexto = { "cli": p, "comentarios":c, 'vehiculo':v}
        return render(request, 'transportes/login/usuarios/verUsuario.html', contexto)
    else:
        messages.warning(request, "Inicie sesión primero...")
        return redirect('transportes:loginFormulario')