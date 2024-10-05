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
    z = r * (np.sin(I) * np.sin(long_peri + nu))

    return x, y, z

def generar_orbita_completa(a, e, I, L, long_peri, long_node):
    nu_values = np.linspace(0, 360, 360)  # 360 puntos para una órbita completa
    coords_orbita = [kepler_to_cartesian(a, e, I, L, long_peri, long_node, nu) for nu in nu_values]
    coords_orbita = np.array(coords_orbita)
    return coords_orbita[:, 0], coords_orbita[:, 1], coords_orbita[:, 2]

def plot_sistema(planetas_cartesianas, orbitas):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Dibujar planetas
    for nombre, coords in planetas_cartesianas.items():
        ax.scatter(coords[0], coords[1], coords[2], label=nombre)

    # Dibujar órbitas
    for nombre, orbita_coords in orbitas.items():
        ax.plot(orbita_coords[0], orbita_coords[1], orbita_coords[2], label=f"Órbita {nombre}")

    ax.set_xlabel('X (AU)')
    ax.set_ylabel('Y (AU)')
    ax.set_zlabel('Z (AU)')
    ax.legend()
    plt.show()

# Función para agregar un planeta
def agregar_planeta(planetas):
    nombre = input("Introduce el nombre del planeta: ")
    a = float(input(f"Introduce el semi-eje mayor (a) para {nombre} en UA: "))
    e = float(input(f"Introduce la excentricidad (e) para {nombre}: "))
    I = float(input(f"Introduce la inclinación (I) para {nombre} en grados: "))
    L = float(input(f"Introduce la longitud media (L) para {nombre} en grados: "))
    long_peri = float(input(f"Introduce la longitud del perihelio para {nombre} en grados: "))
    long_node = float(input(f"Introduce la longitud del nodo ascendente para {nombre} en grados: "))

    # Si quieres que estas tasas sean variables, puedes incluirlas como inputs
    a_rate = 0.0
    e_rate = 0.0
    I_rate = 0.0
    L_rate = 0.0
    long_peri_rate = 0.0
    long_node_rate = 0.0

    nuevo_planeta = Planeta(nombre, a, e, I, L, long_peri, long_node, 
                            a_rate, e_rate, I_rate, L_rate, long_peri_rate, long_node_rate)
    planetas[nombre] = nuevo_planeta
    print(f"Planeta {nombre} agregado con éxito!")

# Función para eliminar un planeta
def eliminar_planeta(planetas):
    nombre = input("Introduce el nombre del planeta a eliminar: ")
    if nombre in planetas:
        del planetas[nombre]
        print(f"Planeta {nombre} eliminado con éxito!")
    else:
        print(f"El planeta {nombre} no existe en el sistema.")

# Ejemplo de uso
fecha = datetime(2024, 10, 5)  # Fecha actual

# Definir planetas y el Sol
planetas = {
    'Sol': Planeta('Sol', 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
    'Mercurio': Planeta('Mercurio', 0.387, 0.2056, 7.005, 252.25, 77.46, 48.33, 
                        0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
    'Venus': Planeta('Venus', 0.723, 0.0067, 3.394, 181.98, 131.53, 76.68, 
                     0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
    'Tierra': Planeta('Tierra', 1.0, 0.0167, 0.0, 100.464, 102.947, 174.791, 
                      0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
    'Marte': Planeta('Marte', 1.524, 0.0934, 1.850, 335.40, 336.23, 49.56, 
                     0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
}

# Menú para agregar o eliminar planetas
while True:
    print("\nOpciones:")
    print("1. Mostrar sistema")
    print("2. Agregar planeta")
    print("3. Eliminar planeta")
    print("4. Salir")

    opcion = input("Selecciona una opción: ")
    
    if opcion == '1':
        # Convertir elementos orbitales a coordenadas cartesianas
        planetas_cartesianas = {}
        orbitas = {}
        for nombre, planeta in planetas.items():
            a, e, I, L, long_peri, long_node = calcular_elementos(planeta, fecha)
            coords = kepler_to_cartesian(a, e, I, L, long_peri, long_node, nu=0)  # Posición actual
            planetas_cartesianas[nombre] = coords
            orbitas[nombre] = generar_orbita_completa(a, e, I, L, long_peri, long_node)  # Órbita completa
        plot_sistema(planetas_cartesianas, orbitas)
    
    elif opcion == '2':
        agregar_planeta(planetas)
    
    elif opcion == '3':
        eliminar_planeta(planetas)
    
    elif opcion == '4':
        print("Saliendo del programa...")
        break

    else:
        print("Opción no válida. Intenta de nuevo.")