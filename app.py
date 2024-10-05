import numpy as np
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

    # Definir planetas (incluyendo el Sol)
    planetas = {
        'Sol': Planeta('Sol', 0, 0, 0, 0, 0, 0, 
                       0, 0, 0, 0, 0, 0),
        'Mercurio': Planeta('Mercurio', 0.387, 0.2056, 7.005, 252.250, 77.457, 48.331, 
                            0, 0, 0, 0, 0, 0),
        'Venus': Planeta('Venus', 0.723, 0.0068, 3.394, 181.979, 131.532, 76.680, 
                         0, 0, 0, 0, 0, 0),
        'Tierra': Planeta('Tierra', 1.000, 0.0167, 0.000, 100.464, 102.947, 174.791, 
                          0, 0, 0, 0, 0, 0),
        'Marte': Planeta('Marte', 1.524, 0.0934, 1.850, 335.40, 336.23, 49.56, 
                         0, 0, 0, 0, 0, 0),
        'Júpiter': Planeta('Júpiter', 5.203, 0.0484, 1.304, 34.404, 14.331, 100.464, 
                           0, 0, 0, 0, 0, 0),
        'Saturno': Planeta('Saturno', 9.537, 0.0542, 2.485, 50.077, 92.431, 113.665, 
                           0, 0, 0, 0, 0, 0),
        'Urano': Planeta('Urano', 19.191, 0.0472, 0.773, 314.202, 170.954, 74.015, 
                         0, 0, 0, 0, 0, 0),
        'Neptuno': Planeta('Neptuno', 30.069, 0.0086, 1.769, 304.880, 44.964, 131.784, 
                           0, 0, 0, 0, 0, 0)
    }

    # Obtener cuerpos adicionales del formulario
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        a = float(request.form.get('a'))
        e = float(request.form.get('e'))
        I = float(request.form.get('I'))
        L = float(request.form.get('L'))
        long_peri = float(request.form.get('long_peri'))
        long_node = float(request.form.get('long_node'))
        
        planetas[nombre] = Planeta(nombre, a, e, I, L, long_peri, long_node, 
                                    0, 0, 0, 0, 0, 0)

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
