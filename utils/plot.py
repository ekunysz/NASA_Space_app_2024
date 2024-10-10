import plotly.graph_objects as go
import numpy as np

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

