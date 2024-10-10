import csv
import json
import numpy as np
from models.cuerpos_celestes import CuerpoCeleste

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
    try:
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
    except FileNotFoundError:
        print(f"El archivo {ruta_csv} no fue encontrado.")
        return {}, []
    except Exception as e:
        print(f"Error al procesar el archivo: {e}")
        return {}, []