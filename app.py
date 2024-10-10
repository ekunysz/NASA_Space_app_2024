import numpy as np
import pandas as pd
import csv
import json
import plotly.graph_objects as go
from datetime import datetime
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

class CuerpoCeleste:
    def __init__(self, nombre, a, e, I, L, long_peri, long_node,
                 a_rate=0, e_rate=0, I_rate=0, L_rate=0, long_peri_rate=0, long_node_rate=0, diametro=0):
        self.nombre = nombre
        self.a = a
        self.e = e
        self.I = I
        self.L = L
        self.long_peri = long_peri
        self.long_node = long_node
        self.a_rate = a_rate
        self.e_rate = e_rate
        self.I_rate = I_rate
        self.L_rate = L_rate
        self.long_peri_rate = long_peri_rate
        self.long_node_rate = long_node_rate
        self.diametro = diametro

# Función para cargar parámetros desde el archivo JSON
def cargar_parametros_desde_json(archivo):
    with open(archivo, 'r') as file:
        return json.load(file)

# Función para crear instancias de Planeta a partir de los parámetros cargados
def crear_planetas_desde_json(parametros):
    planetas = {}
    for nombre, datos in parametros.items():
        planetas[nombre] = CuerpoCeleste(
            nombre=nombre,
            a=datos['a'],
            a_rate=datos['a_rate'],
            e=datos['e'],
            e_rate=datos['e_rate'],
            I=datos['I'],
            I_rate=datos['I_rate'],
            L=datos['L'],
            L_rate=datos['L_rate'],
            long_peri=datos['long_peri'],
            long_peri_rate=datos['long_peri_rate'],
            long_node=datos['long_node'],
            long_node_rate=datos['long_node_rate'],
            diametro=['diametro']
        )
    return planetas

def cargar_cometas_desde_csv(ruta_csv):
    cometas = {}
    nombres_cometas = []  # Lista para almacenar nombres de cometas
    with open(ruta_csv, mode='r') as archivo_csv:
        lector = csv.DictReader(archivo_csv)
        for fila in lector:
            nombre = fila['full_name']
            e = float(fila['e'])  # Excentricidad
            a = float(fila['a'])  # semi eje mayor
            I = float(fila['i'])  # Inclinación
            long_peri = float(fila['w'])  # Longitud del periapsis
            long_node = float(fila['om'])  # Longitud del nodo ascendente

            # Calcular el período orbital P (en años) usando la tercera ley de Kepler
            P = np.sqrt(a ** 3)  # P en años, donde a está en unidades AU

            # Para simplificar, asumiremos que el tiempo desde el perihelio es 0
            t = 0  # Tiempo en días desde el perihelio
            T = 0  # Tiempo del perihelio (0 para simplificación)
            M = (2 * np.pi / P) * (t - T)  # Anomalía media

            # Calcular L (longitud media)
            L = M + long_peri + long_node  # Asegúrate de que las unidades sean consistentes

            # Ajustar L para que esté en el rango [0, 360]
            L = L % 360

            # Crear el objeto CuerpoCeleste
            cometas[nombre] = CuerpoCeleste(nombre, a, e, I, L, long_peri, long_node)
            nombres_cometas.append(nombre)  # Agregar nombre de cometa a la lista
    return cometas, nombres_cometas  # Devolver también la lista de nombres de cometas

def calcular_elementos(cuerpo, fecha):
    j2000 = datetime(2000, 1, 1)
    delta_t = (fecha - j2000).days / 365.25  # Años desde J2000

    a = cuerpo.a + cuerpo.a_rate * delta_t
    e = cuerpo.e + cuerpo.e_rate * delta_t
    I = cuerpo.I + cuerpo.I_rate * delta_t
    L = cuerpo.L + cuerpo.L_rate * delta_t
    long_peri = cuerpo.long_peri + cuerpo.long_peri_rate * delta_t
    long_node = cuerpo.long_node + cuerpo.long_node_rate * delta_t

    # Calcular el argumento del periastro (ω)
    omega = long_peri - long_node

    return a, e, I, L, omega, long_node

def kepler_to_cartesian(a, e, I, L, omega, long_node, nu):
    I = np.radians(I)
    omega = np.radians(omega)
    long_node = np.radians(long_node)
    nu = np.radians(nu)

    # Calculo de la distancia (vector r)
    r = a * (1 - e**2) / (1 + e * np.cos(nu))

    # Posición en el plano orbital
    x_orb = r * np.cos(nu)
    y_orb = r * np.sin(nu)
    z_orb = 0

    # Rotación por el argumento del periapsis (ω)
    x1 = x_orb * np.cos(omega) - y_orb * np.sin(omega)
    y1 = x_orb * np.sin(omega) + y_orb * np.cos(omega)
    z1 = z_orb

    # Rotación por la inclinación (i)
    x2 = x1
    y2 = y1 * np.cos(I)
    z2 = y1 * np.sin(I)

    # Rotación por la longitud del nodo ascendente (Ω)
    x = x2 * np.cos(long_node) - y2 * np.sin(long_node)
    y = x2 * np.sin(long_node) + y2 * np.cos(long_node)
    z = z2

    return x, y, z

def generar_orbita_completa(a, e, I, omega, long_node):
    nu_values = np.linspace(0, 360, 720)  # 360 puntos para una órbita completa
    coords_orbita = [kepler_to_cartesian(a, e, I, L=0, omega=omega, long_node=long_node, nu=nu) for nu in nu_values]
    coords_orbita = np.array(coords_orbita)
    return coords_orbita[:, 0], coords_orbita[:, 1], coords_orbita[:, 2]

def plot_sistema(cuerpos_cartesianos, orbitales, nombres_cometas, axis_range):
    fig = go.Figure()

    # Escala de diámetros para los planetas (ajustado manualmente)
    diametros = {
        'Mercury': 3.8 * (1/109),
        'Venus': 9.5 * (1/109),
        'Earth': 10.0 * (1/109),
        'Mars': 5.3 * (1/109),
        'Jupiter': 54.85 * (1/109),
        'Satur': 45.7 * (1/109),
        'Uranius': 39.8 * (1/109),
        'Neptune': 38.6 * (1/109),
    }

    # Colores reales de los planetas
    colores_planetas = {
        'Mercury': 'gray',
        'Venus': 'palegoldenrod',
        'Earth': 'cyan',
        'Mars': 'red',
        'Jupiter': 'peru',
        'Saturn': 'khaki',
        'Uranius': 'lightseagreen',
        'Neptune': '#7DF9FF',
    }

    # Función para crear una esfera
    def crear_esfera(x_center, y_center, z_center, radius, resolution=50):
        u = np.linspace(0, 2 * np.pi, resolution)
        v = np.linspace(0, np.pi, resolution)
        x = radius * np.outer(np.cos(u), np.sin(v)) + x_center
        y = radius * np.outer(np.sin(u), np.sin(v)) + y_center
        z = radius * np.outer(np.ones(np.size(u)), np.cos(v)) + z_center
        return x, y, z

    # Ajustar la escala de los radios para que las esferas sean más realistas
    escala_radio = 0.1  # Ajuste general para que los tamaños sean visibles pero proporcionales

    # Añadir el Sol como esfera
    sol_x, sol_y, sol_z = crear_esfera(0, 0, 0, radius=1 * escala_radio)  # Tamaño ajustado del Sol
    fig.add_trace(go.Surface(x=sol_x, y=sol_y, z=sol_z, colorscale=[[0, 'yellow'], [1, 'yellow']], 
                             name='Sun', showscale=False, 
                             lighting=dict(ambient=0.8, specular=0.3, roughness=0.9)))

    # Añadir planetas con efectos de iluminación
    for nombre, coords in cuerpos_cartesianos.items():
        # Obtener las coordenadas actuales del planeta
        x, y, z = coords

        # Determinar el color según el nombre del cuerpo celeste
        color_planeta = colores_planetas.get(nombre, 'green')  # Usar color real del planeta o verde por defecto
        radius = diametros.get(nombre, 0.05) * escala_radio  # Escalar el tamaño según el diámetro del planeta 0.05 default

        # Añadir el planeta como esfera con sombras y luces
        planeta_x, planeta_y, planeta_z = crear_esfera(x, y, z, radius=radius)
        fig.add_trace(go.Surface(x=planeta_x, y=planeta_y, z=planeta_z, 
                                 colorscale=[[0, color_planeta], [1, color_planeta]], 
                                 name=nombre,
                                 showscale=False,
                                 lighting=dict(ambient=0.1, diffuse=0.9, roughness=0.35, specular=0.3),
                                 lightposition=dict(x=0, y=0, z=0)))  # El Sol en el origen

        # Añadir la órbita
        orbit_x, orbit_y, orbit_z = orbitales[nombre]
        fig.add_trace(go.Scatter3d(x=orbit_x, y=orbit_y, z=orbit_z,
                                     mode='lines',
                                     name=f'Orbit of {nombre}',
                                     line=dict(width=3, dash='dot', color=color_planeta)))

    # Configurar el layout para tener fondo negro y líneas blancas
    fig.update_layout(scene=dict(
                        xaxis=dict(title='X (AU)',
                                   backgroundcolor='black',
                                   gridcolor='white',
                                   showbackground=True,
                                   range=axis_range),
                        yaxis=dict(title='Y (AU)',
                                   backgroundcolor='black',
                                   gridcolor='white',
                                   showbackground=True,
                                   range=axis_range),
                        zaxis=dict(title='Z (AU)',
                                   backgroundcolor='black',
                                   gridcolor='white',
                                   showbackground=True,
                                   range=axis_range)
                      ),
                      margin=dict(l=0, r=0, b=0, t=0),
                      paper_bgcolor='black',
                      font_color='white')
                    

    return fig.to_html(full_html=False)


# Definir el rango para los ejes como una variable global
axis_range = [-20, 20]

@app.route('/', methods=['GET', 'POST'])
def index():

    fecha = datetime.now()  #Fecha actual

    # Cargar los parámetros orbitales desde el archivo JSON
    parametros_orbitales = cargar_parametros_desde_json('parametros_orbitales.json')
    cuerpos = crear_planetas_desde_json(parametros_orbitales)

    # Obtener cuerpos adicionales del formulario
    if request.method == 'POST':
        # Obtener la fecha y hora del formulario
        fecha_hora_str = request.form.get('fecha_hora')
        
        # Si no se proporciona la fecha, usar la actual
        if fecha_hora_str:
            try:
                # Intentar convertir el string en un objeto datetime
                fecha = datetime.strptime(fecha_hora_str, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                # Si el formato no es correcto, usar la fecha actual
                fecha = datetime.now()
        else:
            # Usar la fecha y hora actual por defecto
            fecha = datetime.now()

        # Imprimir la fecha y hora procesada
        print(f"Fecha y hora: {fecha}")

        # Asegúrate de que el formulario envíe todos los campos necesarios
        nombre = request.form.get('nombre')
        a = float(request.form.get('a'))
        a_rate = float(request.form.get('a_rate', 0.0))
        e = float(request.form.get('e'))
        e_rate = float(request.form.get('e_rate', 0.0))
        I = float(request.form.get('I'))
        I_rate = float(request.form.get('I_rate', 0.0))
        L = float(request.form.get('L'))
        L_rate = float(request.form.get('L_rate', 0.0))
        long_peri = float(request.form.get('long_peri'))
        long_peri_rate = float(request.form.get('long_peri_rate', 0.0))
        long_node = float(request.form.get('long_node'))
        long_node_rate = float(request.form.get('long_node_rate', 0.0))
        
        # Añadir el nuevo planeta al diccionario
        cuerpos[nombre] = CuerpoCeleste(
            nombre=nombre,
            a=a,
            a_rate=a_rate,
            e=e,
            e_rate=e_rate,
            I=I,
            I_rate=I_rate,
            L=L,
            L_rate=L_rate,
            long_peri=long_peri,
            long_peri_rate=long_peri_rate,
            long_node=long_node,
            long_node_rate=long_node_rate
        )
        
     # Cargar cometas desde CSV
    cometas, nombres_cometas = cargar_cometas_desde_csv('comets.csv')

    # Unir cuerpos celestes y cometas
    cuerpos.update(cometas)   
    
    cuerpos_cartesianos = {}
    orbitales = {}

    for nombre, cuerpo in cuerpos.items():
        a, e, I, L, long_peri, long_node = calcular_elementos(cuerpo, fecha)
        coords = kepler_to_cartesian(a, e, I, L, long_peri, long_node, nu=0)  # Usa nu=0 como posición inicial
        cuerpos_cartesianos[nombre] = coords

        # Calcular la órbita completa para el planeta
        orbit_x, orbit_y, orbit_z = generar_orbita_completa(a, e, I, long_peri, long_node)
        orbitales[nombre] = (orbit_x, orbit_y, orbit_z)


    # Generar la figura
    figura_html = plot_sistema(cuerpos_cartesianos, orbitales, nombres_cometas, axis_range)

    return render_template('index.html', figura=figura_html)

axis_range = [-20, 20]  # Rango por defecto

@app.route('/change_range', methods=['POST'])
def change_range():
    global axis_range  # Usar la variable global

    # Obtener la escala seleccionada desde la solicitud POST
    escala_seleccionada = request.json.get('escala', 20)  # Valor por defecto es 20
    
    if escala_seleccionada == 20:
        axis_range = [-20, 20]
    elif escala_seleccionada == 1500:
        axis_range = [-1500, 1500]

    # Recalcular la figura para la nueva escala
    parametros_orbitales = cargar_parametros_desde_json('parametros_orbitales.json')
    cuerpos = crear_planetas_desde_json(parametros_orbitales)
    cometas, nombres_cometas = cargar_cometas_desde_csv('comets.csv')
    cuerpos.update(cometas)
    
    cuerpos_cartesianos = {}
    orbitales = {}

    fecha = datetime.now()
    
    for nombre, cuerpo in cuerpos.items():
        a, e, I, L, long_peri, long_node = calcular_elementos(cuerpo, fecha)
        coords = kepler_to_cartesian(a, e, I, L, long_peri, long_node, nu=0)
        cuerpos_cartesianos[nombre] = coords
        orbit_x, orbit_y, orbit_z = generar_orbita_completa(a, e, I, long_peri, long_node)
        orbitales[nombre] = (orbit_x, orbit_y, orbit_z)

    # Generar la figura actualizada
    figura_html = plot_sistema(cuerpos_cartesianos, orbitales, nombres_cometas, axis_range)
    
    return jsonify({'figura': figura_html})  # Asegúrate de que 'figura_html' sea el HTML que representa el gráfico


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
