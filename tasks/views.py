from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import FormularioTareas
from .models import Tarea
from django.utils import timezone
from django.contrib.auth.decorators import login_required

# Create your views here.
def inicio(request):    
    return render(request, 'inicio.html')

def crearusuario(request):
    if request.method =='GET':
        return render(request, 'crearusuario.html', {'form': UserCreationForm})
    else: 
        if request.POST['password1'] == request.POST['password2']:            
            try:
                user = User.objects.create_user(username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('tareas')
            except IntegrityError:
                return render(request, 'crearusuario.html', {'form': UserCreationForm, 'error': 'El usuario ya existe'})
        return render(request, 'crearusuario.html', {'form': UserCreationForm, 'error': 'Las contraseñas no coinciden'})

@login_required   
def tareas(request):
    tarea = Tarea.objects.filter(usuario=request.user, fecha_completada__isnull=True)
    return render(request, 'tareas.html', {'tareas': tarea})

@login_required
def tareas_completadas(request):
    tarea = Tarea.objects.filter(usuario=request.user, fecha_completada__isnull=False). order_by('-id')
    return render(request, 'tareas.html', {'tareas': tarea})

@login_required
def crear_tarea(request):
    if request.method == 'GET':
        return render(request, 'creartarea.html', {'form': FormularioTareas})
    else:
        try:
            form = FormularioTareas(request.POST)
            nueva_tarea = form.save(commit=False)
            nueva_tarea.usuario = request.user
            nueva_tarea.save()
            return redirect('tareas')
        except ValueError:
            return render(request, 'creartarea.html', {'form': FormularioTareas, 'error': 'Por favor ingrese datos válidos'})
        
@login_required
def detalle_tarea(request, tarea_id):
    if request.method == 'GET':
        tarea = get_object_or_404(Tarea, pk=tarea_id, usuario=request.user)
        form = FormularioTareas(instance=tarea)
        return render(request, 'detalle_tarea.html', {'tarea': tarea, 'form': form})
    else:
        try:
            tarea = get_object_or_404(Tarea, pk=tarea_id, usuario=request.user)
            form = FormularioTareas(request.POST, instance=tarea)
            form.save()
            return redirect('tareas')
        except ValueError:
            return render(request, 'detalle_tarea.html', {'tarea': tarea, 'form': form, 'error': "Error actualizando la tarea"})

@login_required
def tarea_completada(request, tarea_id):
    tarea = get_object_or_404(Tarea, pk=tarea_id, usuario=request.user)
    if request.method == 'POST':
        tarea.fecha_completada = timezone.now()
        tarea.save()
        return redirect('tareas')

@login_required
def borrar_tarea(request, tarea_id):
    tarea = get_object_or_404(Tarea, pk=tarea_id, usuario=request.user)
    if request.method == 'POST':
        tarea.delete()
        return redirect('tareas')

@login_required
def cerrarsesion(request):
    logout(request)
    return redirect('inicio')

def ingresar(request):
    if request.method == 'GET':
        return render (request, 'ingresar.html', {'form': AuthenticationForm})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render (request, 'ingresar.html', {'form': AuthenticationForm, 'error': 'Usuario o contraseña es incorrecto'})
        else:
            login(request, user)
            return redirect('tareas')