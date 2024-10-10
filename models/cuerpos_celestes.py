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
