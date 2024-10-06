import numpy as np
import pandas as pd
import csv
import json
import plotly.graph_objects as go
from datetime import datetime
from flask import Flask, render_template, request

app = Flask(__name__)

class CuerpoCeleste:
    def __init__(self, nombre, a, e, I, L, long_peri, long_node, 
                 a_rate=0, e_rate=0, I_rate=0, L_rate=0, long_peri_rate=0, long_node_rate=0):
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
            long_node_rate=datos['long_node_rate']
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
            q = float(fila['q'])  # Perihelio

            # Calcular el semieje mayor a partir de q
            a = q / (1 - e)

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

    return a, e, I, L, long_peri, long_node

def kepler_to_cartesian(a, e, I, L, long_peri, long_node, nu):
    I = np.radians(I)
    long_peri = np.radians(long_peri)
    long_node = np.radians(long_node)
    nu = np.radians(nu)

    # Calculo de la distancia (vector r)
    r = a * (1 - e**2) / (1 + e * np.cos(nu))

    # Posición en el plano orbital
    x_orb = r * np.cos(nu)
    y_orb = r * np.sin(nu)
    z_orb = 0

    # Rotación por el argumento del periapsis (ω)
    x1 = x_orb * np.cos(long_peri) - y_orb * np.sin(long_peri)
    y1 = x_orb * np.sin(long_peri) + y_orb * np.cos(long_peri)
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

def generar_orbita_completa(a, e, I, long_peri, long_node):
    nu_values = np.linspace(0, 360, 720)  # 360 puntos para una órbita completa
    coords_orbita = [kepler_to_cartesian(a, e, I, L=0, long_peri=long_peri, long_node=long_node, nu=nu) for nu in nu_values]
    coords_orbita = np.array(coords_orbita)
    return coords_orbita[:, 0], coords_orbita[:, 1], coords_orbita[:, 2]

def plot_sistema(cuerpos_cartesianos, orbitales, nombres_cometas):
    fig = go.Figure()

    # Añadir el Sol
    fig.add_trace(go.Scatter3d(x=[0], y=[0], z=[0],
                                 mode='markers',
                                 marker=dict(size=10, color='yellow'),
                                 name='Sol'))

    # Definir los colores
    color_planeta = 'green'  # Color para los planetas
    color_cometa = 'rgba(255, 0, 0, 0.5)'  # Color rojo con opacidad

    # Añadir planetas y sus órbitas
    for nombre, coords in cuerpos_cartesianos.items():
        # Asegurarse de que coords sea un array
        x, y, z = coords
    
        # Determinar el color según el nombre del cuerpo celeste
        if nombre in nombres_cometas:  # Si el nombre está en la lista de nombres de cometas
            color = color_cometa
        else:
            color = color_planeta  # Si no, es un planeta

        # Añadir el cuerpo celeste    
        fig.add_trace(go.Scatter3d(x=[x], y=[y], z=[z],
                                     mode='markers',
                                     marker=dict(size=5),
                                     name=nombre))
        # Añadir la órbita
        orbit_x, orbit_y, orbit_z = orbitales[nombre]
        fig.add_trace(go.Scatter3d(x=orbit_x, y=orbit_y, z=orbit_z,
                                     mode='lines',
                                     name=f'Órbita de {nombre}',
                                     line=dict(width=2, dash='dot', color=color)))  # Usar el mismo color

    # Configurar el layout para tener fondo negro y líneas blancas
    fig.update_layout(scene=dict(
                        xaxis=dict(title='X (AU)',
                                   backgroundcolor='black',
                                   gridcolor='white',
                                   showbackground=True),
                        yaxis=dict(title='Y (AU)',
                                   backgroundcolor='black',
                                   gridcolor='white',
                                   showbackground=True),
                        zaxis=dict(title='Z (AU)',
                                   backgroundcolor='black',
                                   gridcolor='white',
                                   showbackground=True)
                      ),
                      margin=dict(l=0, r=0, b=0, t=0),
                      paper_bgcolor='black',  # Fondo general de la gráfica
                      font_color='white')  # Color del texto


    # Retornar la figura en formato HTML
    return fig.to_html(full_html=False)


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
    figura_html = plot_sistema(cuerpos_cartesianos, orbitales, nombres_cometas)

    return render_template('index.html', figura=figura_html)

if __name__ == '__main__':
    app.run(debug=True)
