import tkinter as tk
import random
import time

# Parámetros de simulación
ANCHO_VENTANA = 1000
ALTO_VENTANA = 700
r = 60  # zona de stop antes del semáforo
LONGITUD_CARRETERA = 400
SIZE_INTERSECCION = 120
MARGEN_ELIMINACION = 100
TIEMPO_VERDE = 80
TIEMPO_AMARILLO = 20
TIEMPO_ROJO = 80
VELOCIDAD_AUTO = 2
PASO_TIEMPO = 50  # ms entre pasos del loop
ESPACIO_ENTRE_AUTOS = 25  # distancia de seguridad (px)
TIEMPO_ENTRE_AUTOS = 60  # ticks de cooldown antes de generar otro en el mismo carril
MAX_AUTOS_POR_CARRIL = 1
ANCHO_CARRIL = 15
SEPARACION_CARRILES = 5

#parámetros para los requerimientos
d = 100  # distancia para contar vehículos
n = 3    # umbral de vehículos para cambiar semáforo
u = 30   # tiempo mínimo en verde (en ticks)
m = 2    # umbral de pocos vehículos
e = 30   # distancia corta más allá del semáforo

# Lista global de intersecciones
intersecciones_globales = []

# Clase Semáforo
class Semaforo:
    def __init__(self, canvas, x, y, orient='vertical'):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.orient = orient  # 'vertical' o 'horizontal'
        self.estado = "rojo"
        self.timer = 0

        # Dibujar cuerpo y luces
        self.cuerpo = self.canvas.create_rectangle(x-12, y-35, x+12, y+35, fill="black", outline="gray")
        self.luces = {
            "rojo": self.canvas.create_oval(x-10, y-30, x+10, y-10, fill="gray20", outline="white"),
            "amarillo": self.canvas.create_oval(x-10, y-10, x+10, y+10, fill="gray20", outline="white"),
            "verde": self.canvas.create_oval(x-10, y+10, x+10, y+30, fill="gray20", outline="white")
        }

        self.raise_front()
        self._encender("rojo")

    def raise_front(self):
        try:
            self.canvas.tag_raise(self.cuerpo)
        except Exception:
            pass
        for luz in self.luces.values():
            try:
                self.canvas.tag_raise(luz)
            except Exception:
                pass

    def _encender(self, color):
        colores = {"rojo": "red", "amarillo": "yellow", "verde": "lime"}
        for c, luz in self.luces.items():
            self.canvas.itemconfig(luz, fill=colores[c] if c == color else "gray20")
        self.estado = color
        self.timer = 0

    def cambiar(self, estado):
        self._encender(estado)
        self.raise_front()

    def tick(self):
        self.timer += 1


# Clase Auto
class Auto:
    contador_global = 0

    def __init__(self, canvas, x, y, direccion, interseccion_id):
        self.canvas = canvas
        self.direccion = direccion
        self.interseccion_actual_id = interseccion_id
        self.paso_interseccion = False
        self.detenido = False
        self.detenido_por_semaforo = False
        colores_posibles = ["red", "blue", "yellow", "white", "gray", "purple", "cyan"]
        color_auto = random.choice(colores_posibles)
        Auto.contador_global += 1
        self.id_auto = Auto.contador_global

        if direccion == "E-O":
            self.obj = canvas.create_rectangle(x, y-8, x+22, y+8, fill=color_auto, outline="black", width=1)
        elif direccion == "O-E":
            self.obj = canvas.create_rectangle(x-22, y-8, x, y+8, fill=color_auto, outline="black", width=1)
        elif direccion == "N-S":
            self.obj = canvas.create_rectangle(x-8, y, x+8, y+22, fill=color_auto, outline="black", width=1)
        elif direccion == "S-N":
            self.obj = canvas.create_rectangle(x-8, y-22, x+8, y, fill=color_auto, outline="black", width=1)
        else:
            self.obj = canvas.create_rectangle(x-10, y-6, x+10, y+6, fill=color_auto, outline="black")

        cx, cy = self.centro()
        self.label = canvas.create_text(cx, cy, text=str(self.id_auto), font=("Arial", 6, "bold"))
        self.canvas.tag_raise(self.obj)
        self.canvas.tag_raise(self.label)

    def mover(self, dx, dy):
        self.canvas.move(self.obj, dx, dy)
        self.canvas.move(self.label, dx, dy)

    def pos(self):
        return self.canvas.coords(self.obj)

    def centro(self):
        x1, y1, x2, y2 = self.pos()
        return ((x1 + x2) / 2, (y1 + y2) / 2)

    def detectar_interseccion_actual(self):
        centro_x, centro_y = self.centro()
        for interseccion in intersecciones_globales:
            int_x, int_y = interseccion.posicion
            margen = SIZE_INTERSECCION * 1.5
            if (int_x - margen <= centro_x <= int_x + margen and
                int_y - margen <= centro_y <= int_y + margen):
                self.interseccion_actual_id = interseccion.id
                return interseccion
        self.interseccion_actual_id = None
        return None

    def en_interseccion(self, interseccion):
        if interseccion is None:
            return False
        centro_x, centro_y = self.centro()
        int_x, int_y = interseccion.posicion
        return (abs(centro_x - int_x) < SIZE_INTERSECCION//2 and abs(centro_y - int_y) < SIZE_INTERSECCION//2)

    def colisiona_con(self, otro_auto):
        x1, y1, x2, y2 = self.pos()
        ox1, oy1, ox2, oy2 = otro_auto.pos()
        return not (x2 < ox1 or x1 > ox2 or y2 < oy1 or y1 > oy2)


# Clase Intersección
class Interseccion:
    def __init__(self, canvas, x, y, id):
        self.canvas = canvas
        self.posicion = (x, y)
        self.id = id
        self.ocupando_interseccion = []

        self.dibujar_carreteras()

        offset = SIZE_INTERSECCION // 2 + 12
        self.semaforo_h = Semaforo(canvas, x + offset, y - ANCHO_CARRIL - 5)
        self.semaforo_v = Semaforo(canvas, x - ANCHO_CARRIL - 5, y + offset)

        if id % 2 == 0:
            self.semaforo_h.cambiar("verde")
            self.semaforo_v.cambiar("rojo")
        else:
            self.semaforo_h.cambiar("rojo")
            self.semaforo_v.cambiar("verde")

        self.autos = {"E-O": [], "O-E": [], "N-S": [], "S-N": []}
        self.cooldowns = {"E-O": 0, "O-E": 0, "N-S": 0, "S-N": 0}
        self.timer_h = 0
        self.timer_v = 0
        
        # Contadores para los nuevos requerimientos
        self.contador_h = 0  # contador de vehículos esperando en horizontal
        self.contador_v = 0  # contador de vehículos esperando en vertical
        self.tiempo_verde_h = 0  # tiempo que lleva en verde horizontal
        self.tiempo_verde_v = 0  # tiempo que lleva en verde vertical

        intersecciones_globales.append(self)

    def dibujar_carreteras(self):
        x, y = self.posicion
        color_asfalto = "#2b2b2b"
        color_linea = "white"

        # Horizontales
        self.canvas.create_rectangle(x-LONGITUD_CARRETERA, y-ANCHO_CARRIL-SEPARACION_CARRILES,
                                     x+LONGITUD_CARRETERA, y-SEPARACION_CARRILES,
                                     fill=color_asfalto, outline=color_asfalto)
        self.canvas.create_rectangle(x-LONGITUD_CARRETERA, y+SEPARACION_CARRILES,
                                     x+LONGITUD_CARRETERA, y+ANCHO_CARRIL+SEPARACION_CARRILES,
                                     fill=color_asfalto, outline=color_asfalto)

        # Verticales
        self.canvas.create_rectangle(x-ANCHO_CARRIL-SEPARACION_CARRILES, y-LONGITUD_CARRETERA,
                                     x-SEPARACION_CARRILES, y+LONGITUD_CARRETERA,
                                     fill=color_asfalto, outline=color_asfalto)
        self.canvas.create_rectangle(x+SEPARACION_CARRILES, y-LONGITUD_CARRETERA,
                                     x+ANCHO_CARRIL+SEPARACION_CARRILES, y+LONGITUD_CARRETERA,
                                     fill=color_asfalto, outline=color_asfalto)

        # Líneas de detención
        r = SIZE_INTERSECCION // 2
        self.canvas.create_line(x-r, y-ANCHO_CARRIL-SEPARACION_CARRILES, x-r, y-SEPARACION_CARRILES, fill=color_linea, width=2)
        self.canvas.create_line(x+r, y+SEPARACION_CARRILES, x+r, y+ANCHO_CARRIL+SEPARACION_CARRILES, fill=color_linea, width=2)
        self.canvas.create_line(x-ANCHO_CARRIL-SEPARACION_CARRILES, y-r, x-SEPARACION_CARRILES, y-r, fill=color_linea, width=2)
        self.canvas.create_line(x+SEPARACION_CARRILES, y+r, x+ANCHO_CARRIL+SEPARACION_CARRILES, y+r, fill=color_linea, width=2)

        # Líneas centrales discontinuas
        for i in range(-LONGITUD_CARRETERA, LONGITUD_CARRETERA, 40):
            self.canvas.create_line(x+i, y-(ANCHO_CARRIL//2 + SEPARACION_CARRILES),
                                    x+i+20, y-(ANCHO_CARRIL//2 + SEPARACION_CARRILES),
                                    fill=color_linea, width=2, dash=(8,6))
            self.canvas.create_line(x+i, y+(ANCHO_CARRIL//2 + SEPARACION_CARRILES),
                                    x+i+20, y+(ANCHO_CARRIL//2 + SEPARACION_CARRILES),
                                    fill=color_linea, width=2, dash=(8,6))
            self.canvas.create_line(x-(ANCHO_CARRIL//2 + SEPARACION_CARRILES), y+i,
                                    x-(ANCHO_CARRIL//2 + SEPARACION_CARRILES), y+i+20,
                                    fill=color_linea, width=2, dash=(8,6))
            self.canvas.create_line(x+(ANCHO_CARRIL//2 + SEPARACION_CARRILES), y+i,
                                    x+(ANCHO_CARRIL//2 + SEPARACION_CARRILES), y+i+20,
                                    fill=color_linea, width=2, dash=(8,6))

    def obtener_punto_generacion(self, dir):
        if dir == "E-O":
            return (50, self.posicion[1] - SEPARACION_CARRILES - ANCHO_CARRIL/2)
        elif dir == "O-E":
            return (ANCHO_VENTANA - 50, self.posicion[1] + SEPARACION_CARRILES + ANCHO_CARRIL/2)
        elif dir == "N-S":
            return (self.posicion[0] - SEPARACION_CARRILES - ANCHO_CARRIL/2, 50)
        elif dir == "S-N":
            return (self.posicion[0] + SEPARACION_CARRILES + ANCHO_CARRIL/2, ALTO_VENTANA - 50)

    def _puede_generar_aqui(self, dir, px, py):
        for inter in intersecciones_globales:
            for a in inter.autos[dir]:
                ax, ay = a.centro()
                if dir in ("E-O", "O-E"):
                    if abs(ay - py) < ANCHO_CARRIL*1.5 and abs(ax - px) < ESPACIO_ENTRE_AUTOS:
                        return False
                else:
                    if abs(ax - px) < ANCHO_CARRIL*1.5 and abs(ay - py) < ESPACIO_ENTRE_AUTOS:
                        return False
        return True

    def generar_autos(self):
        for dir in self.autos.keys():
            if len(self.autos[dir]) >= MAX_AUTOS_POR_CARRIL:
                continue
            if self.cooldowns[dir] > 0:
                self.cooldowns[dir] -= 1
                continue
            if random.random() < 0.03:
                px, py = self.obtener_punto_generacion(dir)
                if self._puede_generar_aqui(dir, px, py):
                    auto = Auto(self.canvas, px, py, dir, self.id)
                    self.autos[dir].append(auto)
                    self.cooldowns[dir] = TIEMPO_ENTRE_AUTOS

    def contar_vehiculos_aproximando(self, direccion, distancia):
        """Cuenta vehículos aproximándose o esperando en rojo a una distancia d"""
        hx, hy = self.posicion
        count = 0
        
        if direccion == "horizontal":
            # Contar autos E-O que están antes del semáforo y dentro de distancia d
            for auto in self.autos["E-O"]:
                cx, cy = auto.centro()
                if cx < hx and hx - cx <= distancia:
                    # Solo contar si está detenido (esperando en rojo)
                    if auto.detenido:
                        count += 1
            # Contar autos O-E que están antes del semáforo y dentro de distancia d
            for auto in self.autos["O-E"]:
                cx, cy = auto.centro()
                if cx > hx and cx - hx <= distancia:
                    # Solo contar si está detenido (esperando en rojo)
                    if auto.detenido:
                        count += 1
        else:  # vertical
            # Contar autos N-S que están antes del semáforo y dentro de distancia d
            for auto in self.autos["N-S"]:
                cx, cy = auto.centro()
                if cy < hy and hy - cy <= distancia:
                    # Solo contar si está detenido (esperando en rojo)
                    if auto.detenido:
                        count += 1
            # Contar autos S-N que están antes del semáforo y dentro de distancia d
            for auto in self.autos["S-N"]:
                cx, cy = auto.centro()
                if cy > hy and cy - hy <= distancia:
                    # Solo contar si está detenido (esperando en rojo)
                    if auto.detenido:
                        count += 1
                    
        return count

    def contar_vehiculos_cruzando(self, direccion, distancia):
        """Cuenta vehículos que van a cruzar un semáforo verde a corta distancia r"""
        hx, hy = self.posicion
        count = 0
        r_corta = 60  # distancia corta para cruce
        
        if direccion == "horizontal":
            # Contar autos E-O que están cerca del semáforo y pueden cruzar (no detenidos)
            for auto in self.autos["E-O"]:
                cx, cy = auto.centro()
                if cx < hx and hx - cx <= r_corta and not auto.detenido:
                    count += 1
            # Contar autos O-E que están cerca del semáforo y pueden cruzar (no detenidos)
            for auto in self.autos["O-E"]:
                cx, cy = auto.centro()
                if cx > hx and cx - hx <= r_corta and not auto.detenido:
                    count += 1
        else:  # vertical
            # Contar autos N-S que están cerca del semáforo y pueden cruzar (no detenidos)
            for auto in self.autos["N-S"]:
                cx, cy = auto.centro()
                if cy < hy and hy - cy <= r_corta and not auto.detenido:
                    count += 1
            # Contar autos S-N que están cerca del semáforo y pueden cruzar (no detenidos)
            for auto in self.autos["S-N"]:
                cx, cy = auto.centro()
                if cy > hy and cy - hy <= r_corta and not auto.detenido:
                    count += 1
                    
        return count

    def hay_vehiculos_detenidos_mas_alla(self, direccion, distancia_e):
        """Verifica si hay vehículos detenidos más allá del semáforo a corta distancia e"""
        hx, hy = self.posicion
        e_corta = 30  # distancia corta más allá del semáforo
        
        if direccion == "horizontal":
            # Verificar autos E-O después del semáforo (yendo hacia la derecha)
            for auto in self.autos["E-O"]:
                cx, cy = auto.centro()
                if cx > hx and cx - hx <= e_corta and auto.detenido:
                    return True
            # Verificar autos O-E después del semáforo (yendo hacia la izquierda)
            for auto in self.autos["O-E"]:
                cx, cy = auto.centro()
                if cx < hx and hx - cx <= e_corta and auto.detenido:
                    return True
        else:  # vertical
            # Verificar autos N-S después del semáforo (yendo hacia abajo)
            for auto in self.autos["N-S"]:
                cx, cy = auto.centro()
                if cy > hy and cy - hy <= e_corta and auto.detenido:
                    return True
            # Verificar autos S-N después del semáforo (yendo hacia arriba)
            for auto in self.autos["S-N"]:
                cx, cy = auto.centro()
                if cy < hy and hy - cy <= e_corta and auto.detenido:
                    return True
                    
        return False

    def actualizar_semaforos(self):
        # Actualizar contadores y tiempos
        self.semaforo_h.tick()
        self.semaforo_v.tick()
        
        # Contar vehículos aproximándose o esperando a distancia d
        self.contador_h = self.contar_vehiculos_aproximando("horizontal", d)
        self.contador_v = self.contar_vehiculos_aproximando("vertical", d)
        
        # Actualizar tiempos en verde
        if self.semaforo_h.estado == "verde":
            self.tiempo_verde_h += 1
        if self.semaforo_v.estado == "verde":
            self.tiempo_verde_v += 1
            
        # Fallback para prevenir semáforos atascados
        if self.semaforo_h.estado == "verde" and self.tiempo_verde_h > 150:
            self.semaforo_h.cambiar("amarillo")
            self.tiempo_verde_h = -20
            return
        if self.semaforo_v.estado == "verde" and self.tiempo_verde_v > 150:
            self.semaforo_v.cambiar("amarillo")
            self.tiempo_verde_v = -20
            return
            
        # Manejo correcto de amber - asegurar transición completa
        if self.semaforo_h.estado == "amarillo":
            self.tiempo_verde_h += 1
            if self.tiempo_verde_h >= 0:  # Fin del tiempo amarillo
                self.semaforo_h.cambiar("rojo")
                self.semaforo_v.cambiar("verde")
                self.contador_h = 0
                self.tiempo_verde_h = 0
                self.tiempo_verde_v = 0
                return
            return  # No hacer más verificaciones mientras está en amber
                
        if self.semaforo_v.estado == "amarillo":
            self.tiempo_verde_v += 1
            if self.tiempo_verde_v >= 0:  # Fin del tiempo amarillo
                self.semaforo_v.cambiar("rojo")
                self.semaforo_h.cambiar("verde")
                self.contador_v = 0
                self.tiempo_verde_v = 0
                self.tiempo_verde_h = 0
                return
            return  # No hacer más verificaciones mientras está en amber
            
        # Fallback para ambos rojos
        if self.semaforo_h.estado == "rojo" and self.semaforo_v.estado == "rojo":
            # Activar el que tiene más demanda
            if self.contador_h >= self.contador_v and self.contador_h > 0:
                self.semaforo_h.cambiar("verde")
                self.contador_h = 0
                self.tiempo_verde_h = 0
                return
            elif self.contador_v > 0:
                self.semaforo_v.cambiar("verde")
                self.contador_v = 0
                self.tiempo_verde_v = 0
                return
            else:
                # Si no hay demanda, activar horizontal por defecto
                self.semaforo_h.cambiar("verde")
                self.contador_h = 0
                self.tiempo_verde_h = 0
                return
            
        # Lógica principal
        if self.semaforo_h.estado == "verde":
            # Cambiar después del tiempo mínimo si hay demanda en vertical
            if self.tiempo_verde_h >= u:
                if self.contador_v > 0:
                    self.semaforo_h.cambiar("amarillo")
                    self.tiempo_verde_h = -20
                    return
                # Fallback: cambiar periódicamente
                elif self.tiempo_verde_h > 100:
                    self.semaforo_h.cambiar("amarillo")
                    self.tiempo_verde_h = -20
                    return
                        
        elif self.semaforo_v.estado == "verde":
            # Cambiar después del tiempo mínimo si hay demanda en horizontal
            if self.tiempo_verde_v >= u:
                if self.contador_h > 0:
                    self.semaforo_v.cambiar("amarillo")
                    self.tiempo_verde_v = -20
                    return
                # Fallback: cambiar periódicamente
                elif self.tiempo_verde_v > 100:
                    self.semaforo_v.cambiar("amarillo")
                    self.tiempo_verde_v = -20
                    return

    def debe_detener_por_semaforo(self, auto, dir):
        if auto.paso_interseccion:
            return False
        interseccion_actual = auto.detectar_interseccion_actual()
        if interseccion_actual is None:
            return False
        centro_x, centro_y = auto.centro()
        x, y = interseccion_actual.posicion
        zona_stop = 25
        if dir == "E-O":
            if x - SIZE_INTERSECCION//2 - zona_stop <= centro_x <= x - SIZE_INTERSECCION//2:
                return interseccion_actual.semaforo_h.estado in ["rojo", "amarillo"]
        elif dir == "O-E":
            if x + SIZE_INTERSECCION//2 <= centro_x <= x + SIZE_INTERSECCION//2 + zona_stop:
                return interseccion_actual.semaforo_h.estado in ["rojo", "amarillo"]
        elif dir == "N-S":
            if y - SIZE_INTERSECCION//2 - zona_stop <= centro_y <= y - SIZE_INTERSECCION//2:
                return interseccion_actual.semaforo_v.estado in ["rojo", "amarillo"]
        elif dir == "S-N":
            if y + SIZE_INTERSECCION//2 <= centro_y <= y + SIZE_INTERSECCION//2 + zona_stop:
                return interseccion_actual.semaforo_v.estado in ["rojo", "amarillo"]
        return False


# Clase Simulación
class Simulacion:
    def __init__(self, canvas):
        self.canvas = canvas
        self.intersecciones = []
        global intersecciones_globales
        intersecciones_globales = []
        self.intersecciones.append(Interseccion(canvas, 250, 200, 0))
        self.intersecciones.append(Interseccion(canvas, 750, 200, 1))
        self.intersecciones.append(Interseccion(canvas, 250, 500, 2))
        self.intersecciones.append(Interseccion(canvas, 750, 500, 3))

    def _autos_por_dir_global(self, dir):
        pares = []
        for inter in self.intersecciones:
            for a in inter.autos[dir]:
                pares.append((inter, a))
        return pares

    def _orden_para_dir(self, dir, pares):
        if dir == "E-O":
            return sorted(pares, key=lambda p: p[1].centro()[0], reverse=True)
        if dir == "O-E":
            return sorted(pares, key=lambda p: p[1].centro()[0])
        if dir == "N-S":
            return sorted(pares, key=lambda p: p[1].centro()[1], reverse=True)
        if dir == "S-N":
            return sorted(pares, key=lambda p: p[1].centro()[1])

    def _hay_auto_adelante_global(self, auto, direccion, distancia_min=15):
        cx, cy = auto.centro()
        for inter in self.intersecciones:
            for otro in inter.autos[direccion]:
                if otro is auto:
                    continue
                ox, oy = otro.centro()
                if direccion == "E-O" and ox > cx and abs(oy - cy) < ANCHO_CARRIL * 1.5:
                    umbral = distancia_min + (ESPACIO_ENTRE_AUTOS if otro.detenido else 0)
                    if ox - cx < umbral and ox - cx > 0:
                        return True
                elif direccion == "O-E" and ox < cx and abs(oy - cy) < ANCHO_CARRIL * 1.5:
                    umbral = distancia_min + (ESPACIO_ENTRE_AUTOS if otro.detenido else 0)
                    if cx - ox < umbral and cx - ox > 0:
                        return True
                elif direccion == "N-S" and oy > cy and abs(ox - cx) < ANCHO_CARRIL * 1.5:
                    umbral = distancia_min + (ESPACIO_ENTRE_AUTOS if otro.detenido else 0)
                    if oy - cy < umbral and oy - cy > 0:
                        return True
                elif direccion == "S-N" and oy < cy and abs(ox - cx) < ANCHO_CARRIL * 1.5:
                    umbral = distancia_min + (ESPACIO_ENTRE_AUTOS if otro.detenido else 0)
                    if cy - oy < umbral and cy - oy > 0:
                        return True
        return False

    def _gestionar_ocupacion_interseccion(self, auto):
        inter_actual = auto.detectar_interseccion_actual()
        if inter_actual:
            int_x, int_y = inter_actual.posicion
            # Verificar si el auto está en la intersección
            if auto.en_interseccion(inter_actual):
                auto.paso_interseccion = True
                auto.detenido = False
                # Asegurarse de que el auto no esté ya en la lista
                if auto not in inter_actual.ocupando_interseccion:
                    inter_actual.ocupando_interseccion.append(auto)
            else:
                # Si el auto ya no está en la intersección
                if auto in inter_actual.ocupando_interseccion:
                    inter_actual.ocupando_interseccion.remove(auto)
                
                # Resetear paso_interseccion cuando el auto sale completamente
                if auto.paso_interseccion:
                    cx, cy = auto.centro()
                    # Verificar si el auto ya pasó completamente la intersección
                    margen_salida = SIZE_INTERSECCION//2 + 50
                    if ((auto.direccion == "E-O" and cx > int_x + margen_salida) or
                        (auto.direccion == "O-E" and cx < int_x - margen_salida) or
                        (auto.direccion == "N-S" and cy > int_y + margen_salida) or
                        (auto.direccion == "S-N" and cy < int_y - margen_salida)):
                        auto.paso_interseccion = False
                        
                # Manejar ocupación de intersección por otros autos
                if not auto.en_interseccion(inter_actual) and len(inter_actual.ocupando_interseccion) > 0:
                    offset = SIZE_INTERSECCION / 4.0
                    permitir = True
                    for occ in inter_actual.ocupando_interseccion:
                        if occ.direccion != auto.direccion:
                            permitir = False
                            break
                        occ_cx, occ_cy = occ.centro()
                        if auto.direccion == "E-O":
                            if not (occ_cx > int_x + offset):
                                permitir = False
                                break
                        elif auto.direccion == "O-E":
                            if not (occ_cx < int_x - offset):
                                permitir = False
                                break
                        elif auto.direccion == "N-S":
                            if not (occ_cy > int_y + offset):
                                permitir = False
                                break
                        elif auto.direccion == "S-N":
                            if not (occ_cy < int_y - offset):
                                permitir = False
                                break
                    if not permitir:
                        return True
        return False

    def _mover_por_direccion(self, direccion):
        pares = self._autos_por_dir_global(direccion)
        ordenados = self._orden_para_dir(direccion, pares)
        for inter, auto in ordenados:
            puede_mover = True
            
            # Verificar semáforo
            if inter.debe_detener_por_semaforo(auto, direccion):
                puede_mover = False
                auto.detenido_por_semaforo = True
            else:
                auto.detenido_por_semaforo = False
                
            # Verificar colisión con auto adelante
            if puede_mover and self._hay_auto_adelante_global(auto, direccion, distancia_min=ESPACIO_ENTRE_AUTOS):
                puede_mover = False
                
            # Verificar ocupación de intersección
            if puede_mover and self._gestionar_ocupacion_interseccion(auto):
                puede_mover = False
                
            # Actualizar estado detenido
            auto.detenido = not puede_mover
            
            # Mover si se puede
            if puede_mover:
                if direccion == "E-O":
                    auto.mover(VELOCIDAD_AUTO, 0)
                elif direccion == "O-E":
                    auto.mover(-VELOCIDAD_AUTO, 0)
                elif direccion == "N-S":
                    auto.mover(0, VELOCIDAD_AUTO)
                elif direccion == "S-N":
                    auto.mover(0, -VELOCIDAD_AUTO)

                # Manejar salida de intersección - más robusto
                inter_actual = auto.detectar_interseccion_actual()
                if inter_actual is not None and auto in inter_actual.ocupando_interseccion:
                    cx, cy = auto.centro()
                    int_x, int_y = inter_actual.posicion
                    # Remover de ocupando_interseccion cuando sale - más generoso con los límites
                    margen_salida = SIZE_INTERSECCION//2 + 40
                    if ((direccion == "E-O" and cx > int_x + margen_salida) or
                        (direccion == "O-E" and cx < int_x - margen_salida) or
                        (direccion == "N-S" and cy > int_y + margen_salida) or
                        (direccion == "S-N" and cy < int_y - margen_salida)):
                        if auto in inter_actual.ocupando_interseccion:
                            inter_actual.ocupando_interseccion.remove(auto)
                            
                # Fallback: forzar salida de intersección si está atascado
                if inter_actual is not None and auto in inter_actual.ocupando_interseccion:
                    # Si el auto ha estado mucho tiempo en la intersección, forzar salida
                    if hasattr(auto, 'tiempo_en_interseccion'):
                        auto.tiempo_en_interseccion += 1
                        if auto.tiempo_en_interseccion > 100:  # 100 ticks máximo
                            if auto in inter_actual.ocupando_interseccion:
                                inter_actual.ocupando_interseccion.remove(auto)
                            if hasattr(auto, 'tiempo_en_interseccion'):
                                delattr(auto, 'tiempo_en_interseccion')
                    else:
                        auto.tiempo_en_interseccion = 0
                else:
                    if hasattr(auto, 'tiempo_en_interseccion'):
                        delattr(auto, 'tiempo_en_interseccion')

    def _eliminar_fuera_pantalla(self):
        for inter in self.intersecciones:
            for dir, lista_autos in inter.autos.items():
                for auto in list(lista_autos):
                    x1, y1, x2, y2 = auto.pos()
                    if (x2 < -MARGEN_ELIMINACION or x1 > ANCHO_VENTANA + MARGEN_ELIMINACION or
                        y2 < -MARGEN_ELIMINACION or y1 > ALTO_VENTANA + MARGEN_ELIMINACION):
                        inter.canvas.delete(auto.obj)
                        inter.canvas.delete(auto.label)
                        if auto in inter.ocupando_interseccion:
                            inter.ocupando_interseccion.remove(auto)
                        if hasattr(auto, 'tiempo_en_interseccion'):
                            delattr(auto, 'tiempo_en_interseccion')
                        lista_autos.remove(auto)

    def paso(self):
        for inter in self.intersecciones:
            inter.generar_autos()
            inter.actualizar_semaforos()
        for dir in ("E-O","O-E","N-S","S-N"):
            self._mover_por_direccion(dir)
        self._eliminar_fuera_pantalla()


# Interfaz gráfica (main)
root = tk.Tk()
root.title("Simulación de 4 intersecciones - Semáforos Autoorganizados")
canvas = tk.Canvas(root, width=ANCHO_VENTANA, height=ALTO_VENTANA, bg="#86c06f")
canvas.pack()

sim = Simulacion(canvas)

def actualizar():
    sim.paso()
    root.after(PASO_TIEMPO, actualizar)

root.after(PASO_TIEMPO, actualizar)
root.mainloop()