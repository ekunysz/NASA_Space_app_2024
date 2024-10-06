import numpy as np
import json
import plotly.graph_objects as go
from datetime import datetime
from flask import Flask, render_template, request

app = Flask(__name__)

class Planeta:
    def __init__(self, nombre, a, e, I, L, long_peri, long_node, 
                 a_rate, e_rate, I_rate, L_rate, long_peri_rate, long_node_rate):
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
        planetas[nombre] = Planeta(
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


def calcular_elementos(planeta, fecha):
    j2000 = datetime(2000, 1, 1)
    delta_t = (fecha - j2000).days / 365.25  # Años desde J2000

    a = planeta.a + planeta.a_rate * delta_t
    e = planeta.e + planeta.e_rate * delta_t
    I = planeta.I + planeta.I_rate * delta_t
    L = planeta.L + planeta.L_rate * delta_t
    long_peri = planeta.long_peri + planeta.long_peri_rate * delta_t
    long_node = planeta.long_node + planeta.long_node_rate * delta_t

    return a, e, I, L, long_peri, long_node

def kepler_to_cartesian(a, e, I, L, long_peri, long_node, nu):
    I = np.radians(I)
    long_peri = np.radians(long_peri)
    long_node = np.radians(long_node)
    nu = np.radians(nu)

    r = a * (1 - e**2) / (1 + e * np.cos(nu))
    x = r * (np.cos(long_node) * np.cos(long_peri + nu) - 
              np.sin(long_node) * np.sin(long_peri + nu) * np.cos(I))
    y = r * (np.sin(long_node) * np.cos(long_peri + nu) + 
              np.cos(long_node) * np.sin(long_peri + nu) * np.cos(I))
    z = r * (np.cos(long_node) * np.cos(long_peri + nu) + 
              np.sin(long_node) * np.sin(long_peri + nu)* np.cos(I))

    return x, y, z

def generar_orbita_completa(a, e, I, long_peri, long_node):
    nu_values = np.linspace(0, 360, 360)  # 360 puntos para una órbita completa
    coords_orbita = [kepler_to_cartesian(a, e, I, L=0, long_peri=long_peri, long_node=long_node, nu=nu) for nu in nu_values]
    coords_orbita = np.array(coords_orbita)
    return coords_orbita[:, 0], coords_orbita[:, 1], coords_orbita[:, 2]

def plot_sistema(planetas_cartesianas, orbitales):
    fig = go.Figure()

    # Añadir el Sol
    fig.add_trace(go.Scatter3d(x=[0], y=[0], z=[0],
                                 mode='markers',
                                 marker=dict(size=10, color='yellow'),
                                 name='Sol'))

    # Añadir planetas y sus órbitas
    for nombre, coords in planetas_cartesianas.items():
        # Asegurarse de que coords sea un array
        x, y, z = coords
        fig.add_trace(go.Scatter3d(x=[x], y=[y], z=[z],
                                     mode='markers',
                                     marker=dict(size=5),
                                     name=nombre))
        # Añadir la órbita
        orbit_x, orbit_y, orbit_z = orbitales[nombre]
        fig.add_trace(go.Scatter3d(x=orbit_x, y=orbit_y, z=orbit_z,
                                     mode='lines',
                                     name=f'Órbita de {nombre}',
                                     line=dict(width=2)))

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
    fecha = datetime(2024, 10, 5)  # Fecha actual

    # Cargar los parámetros orbitales desde el archivo JSON
    parametros_orbitales = cargar_parametros_desde_json('parametros_orbitales.json')
    planetas = crear_planetas_desde_json(parametros_orbitales)

    # Obtener cuerpos adicionales del formulario
    if request.method == 'POST':
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
        planetas[nombre] = Planeta(
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
        
    planetas_cartesianas = {}
    orbitales = {}
    for nombre, planeta in planetas.items():
        a, e, I, L, long_peri, long_node = calcular_elementos(planeta, fecha)
        coords = kepler_to_cartesian(a, e, I, L, long_peri, long_node, nu=0)  # Usa nu=0 como posición inicial
        planetas_cartesianas[nombre] = coords

        # Calcular la órbita completa para el planeta
        orbit_x, orbit_y, orbit_z = generar_orbita_completa(a, e, I, long_peri, long_node)
        orbitales[nombre] = (orbit_x, orbit_y, orbit_z)

    figura_html = plot_sistema(planetas_cartesianas, orbitales)
    return render_template('index.html', figura=figura_html)

if __name__ == '__main__':
    app.run(debug=True)
