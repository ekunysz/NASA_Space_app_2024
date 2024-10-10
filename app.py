from datetime import datetime
from flask import Flask, render_template, request, jsonify
from models.cuerpos_celestes import CuerpoCeleste
from utils.datos import cargar_parametros_desde_json, crear_planetas_desde_json, cargar_cometas_desde_csv
from utils.astro import calcular_elementos, kepler_to_cartesian, generar_orbita_completa
from utils.plot import plot_sistema

app = Flask(__name__)

# Definir el rango para los ejes como una variable global
axis_range = [-20, 20]

@app.route('/', methods=['GET', 'POST'])
def index():

    fecha = datetime.now()  #Fecha actual

    # Cargar los parámetros orbitales desde el archivo JSON
    parametros_orbitales = cargar_parametros_desde_json('data/parametros_orbitales.json')
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
    cometas, nombres_cometas = cargar_cometas_desde_csv('data/comets.csv')

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
