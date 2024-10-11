import numpy as np
from datetime import datetime

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
