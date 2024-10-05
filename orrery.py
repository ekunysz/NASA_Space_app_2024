import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from datetime import datetime

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
    delta_t = (fecha - j2000).days / 365.25  # AÃ±os desde J2000

    a = planeta.a + planeta.a_rate * delta_t
    e = planeta.e + planeta.e_rate * delta_t
    I = planeta.I + planeta.I_rate * delta_t
    L = planeta.L + planeta.L_rate * delta_t
    long_peri = planeta.long_peri + planeta.long_peri_rate * delta_t
    long_node = planeta.long_node + planeta.long_node_rate * delta_t

    return a, e, I, L, long_peri, long_node

def kepler_to_cartesian(a, e, I, L, long_peri, long_node, nu=0):
    I = np.radians(I)
    long_peri = np.radians(long_peri)
    long_node = np.radians(long_node)
    nu = np.radians(nu)

    r = a * (1 - e**2) / (1 + e * np.cos(nu))
    x = r * (np.cos(long_node) * np.cos(long_peri + nu) - 
              np.sin(long_node) * np.sin(long_peri + nu) * np.cos(I))
    y = r * (np.sin(long_node) * np.cos(long_peri + nu) + 
              np.cos(long_node) * np.sin(long_peri + nu) * np.cos(I))
    z = r * (np.sin(I) * np.sin(long_peri + nu))

    return x, y, z

def plot_sistema(planetas_cartesianas):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    for nombre, coords in planetas_cartesianas.items():
        ax.scatter(coords[0], coords[1], coords[2], label=nombre)

    ax.set_xlabel('X (AU)')
    ax.set_ylabel('Y (AU)')
    ax.set_zlabel('Z (AU)')
    ax.legend()
    plt.show()

# Ejemplo de uso
fecha = datetime(2024, 10, 5)  # Fecha actual

# Definir planetas
planetas = {
    'Planeta1': Planeta('Planeta1', 1.0, 0.0167, 0.0, 100.464, 102.947, 174.791, 
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
    'Planeta2': Planeta('Planeta2', 1.524, 0.0934, 1.850, 335.40, 336.23, 49.56, 
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
}

planetas_cartesianas = {}
for nombre, planeta in planetas.items():
    a, e, I, L, long_peri, long_node = calcular_elementos(planeta, fecha)
    coords = kepler_to_cartesian(a, e, I, L, long_peri, long_node)
    planetas_cartesianas[nombre] = coords

plot_sistema(planetas_cartesianas)
