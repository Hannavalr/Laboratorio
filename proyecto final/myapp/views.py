from pathlib import Path

from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, render


BASE_DIR = Path(__file__).resolve().parent.parent
MASCOTAS_FILE = BASE_DIR / 'mascotas.txt'
SOLICITUDES_FILE = BASE_DIR / 'solicitudes.txt'


def leer_mascotas():
    mascotas = []
    with MASCOTAS_FILE.open('r', encoding='utf-8') as archivo:
        for linea in archivo:
            campos = linea.strip().split('|')
            if not linea.strip():
                continue
            if len(campos) < 5:
                continue
            nombre, especie, peso, edad, descripcion = campos[:5]
            estado = campos[5] if len(campos) > 5 else 'Disponible'
            mascotas.append({
                'nombre': nombre, 'especie': especie, 'peso': peso,
                'edad': edad, 'descripcion': descripcion, 'estado': estado, 
                'imagen': f'mascotas/{nombre}.jpeg',
            })
    return mascotas


def leer_solicitudes():
    solicitudes = []
    if not SOLICITUDES_FILE.exists():
        return solicitudes
    for indice, linea in enumerate(SOLICITUDES_FILE.read_text(encoding='utf-8').splitlines()):
        campos = linea.split('|')
        if len(campos) < 4:
            continue
        nombre, telefono, correo, mascota = campos[:4]
        estado = campos[4] if len(campos) > 4 else 'Pendiente'
        solicitudes.append({
            'indice': indice, 'nombre': nombre, 'telefono': telefono,
            'correo': correo, 'mascota': mascota, 'estado': estado,
        })
    return solicitudes


def cambiar_estado_solicitud(indice, nuevo_estado):
    lineas = SOLICITUDES_FILE.read_text(encoding='utf-8').splitlines()
    if indice < 0 or indice >= len(lineas):
        return False
    campos = lineas[indice].split('|')
    if len(campos) < 4:
        return False
    lineas[indice] = '|'.join(campos[:4] + [nuevo_estado])
    SOLICITUDES_FILE.write_text('\n'.join(lineas) + ('\n' if lineas else ''), encoding='utf-8')
    return True


def marcar_mascota_adoptada(nombre):
    lineas = MASCOTAS_FILE.read_text(encoding='utf-8').splitlines()
    for indice, linea in enumerate(lineas):
        campos = linea.split('|')

        if campos and campos[0] == nombre:
            campos = campos[:5] + ['Adoptada']
            lineas[indice] = '|'.join(campos)
            MASCOTAS_FILE.write_text('\n'.join(lineas) + '\n', encoding='utf-8')
            return


def home(request):
    mensaje = ''
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        correo = request.POST.get('correo', '').strip()
        mascota = request.POST.get('mascota', '').strip()
        disponibles = {m['nombre'] for m in leer_mascotas() if m['estado'] != 'Adoptada'}

        if not all((nombre, telefono, correo, mascota)) or mascota not in disponibles:
            return HttpResponseBadRequest('Completa los datos y selecciona una mascota disponible.')
        with SOLICITUDES_FILE.open('a', encoding='utf-8') as archivo:
            archivo.write(f'{nombre}|{telefono}|{correo}|{mascota}|Pendiente\n')
        mensaje = '¡Tu solicitud fue registrada exitosamente!'

    todas = [m for m in leer_mascotas() if m['estado'] != 'Adoptada']
    mascotas = todas
    especie = request.GET.get('especie', '')
    edad = request.GET.get('edad', '')

    if especie:
        mascotas = [m for m in mascotas if m['especie'] == especie]
    if edad:
        mascotas = [m for m in mascotas if m['edad'] == edad]
    return render(request, 'index.html', {
        'titulo': 'Huellitas del Valle',
        'descripcion': 'Conoce a las mascotas que esperan un hogar.',
        'mascotas': mascotas, 'todas': todas, 'mensaje': mensaje,
        'especie_sel': especie, 'edad_sel': edad, 'MEDIA_URL': '/media/'
    })


def administracion(request):
    if request.method == 'POST':
        try:
            indice = int(request.POST.get('indice', '-1'))
        except ValueError:
            return HttpResponseBadRequest('Postulación no válida.')
        decision = request.POST.get('decision')
        estados = {'aprobar': 'Aprobada', 'rechazar': 'Rechazada'}
        solicitudes = leer_solicitudes()
        solicitud = next((s for s in solicitudes if s['indice'] == indice), None)
        
        if decision not in estados or solicitud is None or solicitud['estado'] != 'Pendiente':
            return HttpResponseBadRequest('La decisión no es válida o la postulación ya fue revisada.')
        cambiar_estado_solicitud(indice, estados[decision])
        if decision == 'aprobar':
            marcar_mascota_adoptada(solicitud['mascota'])
        return redirect('administracion')

    solicitudes = leer_solicitudes()
    contexto = {
        'solicitudes': solicitudes,
        'pendientes': sum(s['estado'] == 'Pendiente' for s in solicitudes),
        'aprobadas': sum(s['estado'] == 'Aprobada' for s in solicitudes),
        'rechazadas': sum(s['estado'] == 'Rechazada' for s in solicitudes),
    }
    return render(request, 'administracion.html', contexto)
