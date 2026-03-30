import tkinter as tk
from tkinter import *
from tkinter import messagebox, simpledialog
from random import *

with open("palabras_todas.txt", 'r', encoding='utf-8') as archivo:
    lineas = [linea.strip().lower() for linea in archivo]

class JuegoBatallaNaval:
    def __init__(self, root, nombre_usuario):
        self.root = root
        self.nombre_usuario = nombre_usuario
        self.root.title("Batalla Naval")

        # Tablero de la computadora
        self.tablero_computadora = [[0] * 10 for _ in range(10)]
        self.botones_computadora = [[None] * 10 for _ in range(10)]
        self.frame_computadora = tk.Frame(self.root, padx=10, pady=10, borderwidth=2, relief="ridge")
        self.frame_computadora.grid(row=0, column=0)
        self.label_computadora = tk.Label(self.frame_computadora, text="Tablero de la Computadora", font=("Helvetica", 14, "bold"))
        self.label_computadora.grid(row=0, column=0)

        # Tablero del usuario
        self.tablero_usuario = [[0] * 10 for _ in range(10)]
        self.botones_usuario = [[None] * 10 for _ in range(10)]
        self.frame_usuario = tk.Frame(self.root, padx=10, pady=10, borderwidth=2, relief="ridge")
        self.frame_usuario.grid(row=0, column=1)
        self.label_usuario = tk.Label(self.frame_usuario, text=f"Tablero de {self.nombre_usuario}", font=("Helvetica", 14, "bold"))
        self.label_usuario.grid(row=0, column=0)

        self.barcos = [
            [[1, 1, 1]],           # Barco de tamaño 3
            [[0, 1, 1], [1, 1, 1], [0, 1, 1]],  # Barco de tamaño 3 en forma de "T"
            [[1, 1, 1], [0, 1, 0], [1, 1, 1]],  # Barco de tamaño 3 en forma de "X"
            [[1, 1, 0], [0, 1, 0], [0, 1, 1]]   # Barco de tamaño 3 en forma de "L"
        ]
        self.cantidades = [3, 1, 1, 1]

        self.colocar_barcos_computadora()
        self.crear_tableros()

        self.turno_usuario = True  # Bandera para alternar entre turnos del usuario y la computadora
        self.ataques_pendientes = []  # Lista de coordenadas pendientes por disparar
        self.coordenadas_atacadas = set()  # Conjunto de coordenadas atacadas
        self.barcos_usuario = self.generar_barcos_usuario()  # Generar barcos del usuario
        self.barco_actual = 0
        self.orientacion_actual = '0'  # Orientación inicial del barco

        # Marco y botón para mostrar y girar el barco actual. Y ejemplo de acierto y fallo
        self.frame_barco_actual = tk.Frame(self.root)
        self.frame_barco_actual.grid(row=1, column=0, columnspan=2, pady=10)
        # Etiqueta para "Barco actual"
        self.label_barco_actual = tk.Label(self.frame_barco_actual, text="Barco actual:", font=("Helvetica", 14, "bold"))
        self.label_barco_actual.grid(row=0, column=4, padx=10)
        # Canvas para mostrar el barco actual
        self.canvas_barco_actual = tk.Canvas(self.frame_barco_actual, width=100, height=100)
        self.canvas_barco_actual.grid(row=0, column=5, padx=10)
        # Botón para girar el barco actual
        self.boton_girar = tk.Button(self.frame_barco_actual, text="Girar", cursor="hand2", command=self.girar_barco, width=10, height=2)
        self.boton_girar.grid(row=0, column=6, padx=10)

        # Mostrar tableros en la consola
        self.mostrar_tableros()

        # Botones de control
        self.frame_controles = tk.Frame(self.root)
        self.frame_controles.grid(row=3, column=0, columnspan=2, sticky="se", padx=10, pady=10)  # Sticky "se" para alinear abajo a la derecha
        self.boton_volver = tk.Button(self.frame_controles, text="Volver", cursor="hand2", command=self.volver_menu, width=10, height=3)
        self.boton_volver.grid(row=0, column=1, padx=(10, 0))  # Añade espacio a la izquierda del botón "Volver"
        self.boton_reiniciar = tk.Button(self.frame_controles, text="Reiniciar", cursor="hand2", command=self.reiniciar_partida, width=10, height=3)
        self.boton_reiniciar.grid(row=0, column=0, padx=(0, 10))  # Añade espacio a la derecha del botón "Reiniciar"

        self.mostrar_barco_actual()  # Mostrar el primer barco a colocar

    def volver_menu(self):
        # Destruir todos los widgets en la ventana actual
        for widget in self.root.winfo_children():
            widget.destroy()
        # Volver al menú principal
        self.app = Aplicacion(self.root)

    def reiniciar_partida(self):
        # Destruir todos los widgets en la ventana actual
        for widget in self.root.winfo_children():
            widget.destroy()
        # Reiniciar el juego de batalla naval
        self.juego_batalla_naval = JuegoBatallaNaval(self.root, self.nombre_usuario)

    def mostrar_tableros(self):
        print("Tablero de la Computadora:")
        for fila in self.tablero_computadora:
            print(" ".join(str(casilla) for casilla in fila))
        print()

    def crear_tableros(self):
        for i in range(10):
            for j in range(10):
                # Tablero de la computadora
                boton_computadora = tk.Button(self.frame_computadora, state="disabled", relief="sunken", text=" ", width=4, height=2, command=lambda fila=i, col=j: self.disparar_usuario(fila, col))
                boton_computadora.grid(row=i + 1, column=j + 1, padx=1, pady=1)
                self.botones_computadora[i][j] = boton_computadora
    
                # Tablero del usuario
                boton_usuario = tk.Button(self.frame_usuario, text=" ", cursor="hand2", width=4, height=2, command=lambda fila=i, col=j: self.colocar_barco_usuario(fila, col))
                boton_usuario.grid(row=i + 1, column=j + 1, padx=1, pady=1)
                self.botones_usuario[i][j] = boton_usuario

    def colocar_barcos_computadora(self):
        colocacion_exitosa = False
        while not colocacion_exitosa:
            self.tablero_computadora = [[0] * 10 for _ in range(10)]

            colocacion_exitosa = True

            for barco, cantidad in zip(self.barcos, self.cantidades):
                for _ in range(cantidad):
                    colocacion_barco_exitosa = False
                    cont = 0
                    while not colocacion_barco_exitosa and cont < 1000 and colocacion_exitosa:
                        fila_computadora = randint(0, 9)
                        col_computadora = randint(0, 9)
                        orientacion = choice(['0', '90', '180', '270'])
                        barco_rotado = self.rotar_barco(barco, orientacion)
                        cont += 1
                        if cont == 1000:
                            colocacion_exitosa = False
                        if self.verificar_posicion(self.tablero_computadora, fila_computadora, col_computadora, barco_rotado):
                            for i in range(len(barco_rotado)):
                                for j in range(len(barco_rotado[0])):
                                    self.tablero_computadora[fila_computadora + i][col_computadora + j] = barco_rotado[i][j]
                            colocacion_barco_exitosa = True

    def rotar_barco(self, barco, orientacion):
        if orientacion == '0':
            return barco
        elif orientacion == '90':
            filas = len(barco)
            columnas = len(barco[0])
            return [[barco[filas - 1 - j][i] for j in range(filas)] for i in range(columnas)]
        elif orientacion == '180':
            return [[barco[len(barco) - 1 - i][len(barco[0]) - 1 - j] for j in range(len(barco[0]))] for i in range(len(barco))]
        elif orientacion == '270':
            filas = len(barco)
            columnas = len(barco[0])
            return [[barco[j][columnas - 1 - i] for j in range(filas)] for i in range(columnas)]

    def verificar_posicion(self, tablero, fila, col, barco):
        if fila < 0 or col < 0 or fila + len(barco) > 10 or col + len(barco[0]) > 10:
            return False
        for i in range(fila, fila + len(barco)):
            for j in range(col, col + len(barco[0])):
                if barco[i - fila][j - col] == 1:
                    for ni in range(i - 1, i + 2):
                        for nj in range(j - 1, j + 2):
                            if 0 <= ni < 10 and 0 <= nj < 10 and tablero[ni][nj] != 0:
                                return False
        return True

    def generar_barcos_usuario(self):
        barcos_usuario = []
        for barco, cantidad in zip(self.barcos, self.cantidades):
            for _ in range(cantidad):
                barcos_usuario.append(barco)
        return barcos_usuario

    def mostrar_barco_actual(self):
        self.canvas_barco_actual.delete("all")  # Limpiar el canvas
        if self.barco_actual < len(self.barcos_usuario):
            barco = self.barcos_usuario[self.barco_actual]
            barco_rotado = self.rotar_barco(barco, self.orientacion_actual)
            filas = len(barco_rotado)
            columnas = len(barco_rotado[0])
            for i in range(filas):
                for j in range(columnas):
                    if barco_rotado[i][j] == 1:
                        self.canvas_barco_actual.create_rectangle(j * 20, i * 20, (j + 1) * 20, (i + 1) * 20, fill="gray")

    def girar_barco(self):
        orientaciones = ['0', '90', '180', '270']
        indice_actual = orientaciones.index(self.orientacion_actual)
        self.orientacion_actual = orientaciones[(indice_actual + 1) % 4]
        self.mostrar_barco_actual()

    def colocar_barco_usuario(self, fila, col):
        if self.barco_actual >= len(self.barcos_usuario):
            return  # Si ya se colocaron todos los barcos, no hacer nada

        barco = self.barcos_usuario[self.barco_actual]
        barco_rotado = self.rotar_barco(barco, self.orientacion_actual)
        if self.verificar_posicion(self.tablero_usuario, fila, col, barco_rotado):
            self.marcar_posicion(self.tablero_usuario, fila, col, barco_rotado)
            self.barco_actual += 1
            if self.barco_actual >= len(self.barcos_usuario):
                self.comenzar_juego()
            else:
                self.mostrar_barco_actual()
        else:
            messagebox.showwarning("Posición inválida", "No puedes colocar el barco aquí.")

    def marcar_posicion(self, tablero, fila, col, barco):
        for i in range(len(barco)):
            for j in range(len(barco[0])):
                if barco[i][j] == 1:
                    tablero[fila + i][col + j] = barco[i][j]
                    self.botones_usuario[fila + i][col + j].config(bg="gray", state="disabled")

    def comenzar_juego(self):
            # Limpiar el canvas que muestra el barco actual
        self.canvas_barco_actual.delete("all")

        # Cambiar la etiqueta que indica el barco actual
        self.label_barco_actual.config(text="Es tu turno!", font=("Helvetica", 14, "bold"))

        # Eliminar el botón de girar
        self.boton_girar.destroy()
        for i in range(10):
            for j in range(10):
                self.botones_usuario[i][j].config(state="disabled", cursor="arrow")
                self.botones_computadora[i][j].config(state="normal", cursor="hand2", relief="raised")
        
        self.label_acierto = tk.Label(self.frame_barco_actual, text="Acierto", font=("Helvetica", 12))
        self.label_acierto.grid(row=0, column=0, padx=5)
        self.boton_acierto = tk.Button(self.frame_barco_actual, width=2, height=1, bd=1, bg="red", state="disabled")
        self.boton_acierto.grid(row=0, column=1, padx=5)
        self.label_fallo = tk.Label(self.frame_barco_actual, text="Fallo", font=("Helvetica", 12))
        self.label_fallo.grid(row=0, column=2, padx=5)
        self.boton_fallo = tk.Button(self.frame_barco_actual, width=2, height=1, bd=1, bg="blue", state="disabled")
        self.boton_fallo.grid(row=0, column=3, padx=5)

    def disparar_usuario(self, fila, col):
        if self.turno_usuario:
            if self.tablero_computadora[fila][col] == 1:
                self.botones_computadora[fila][col].config(text="*", bg="red", state="disabled")
                self.tablero_computadora[fila][col] = 0
                if self.verificar_ganador():
                    return
            else:
                self.botones_computadora[fila][col].config(text="x", bg="blue", state="disabled")
                self.turno_usuario = False
                if self.verificar_ganador():
                    return
                self.disparar_computadora()
                self.label_barco_actual.config(text="Es turno de la maquina!", font=("Helvetica", 14, "bold"))

    def disparar_computadora(self):
        self.root.after(1500, self.disparar_computadora_2)

    def disparar_computadora_2(self):
        if not self.turno_usuario:
            fila, col = self.seleccionar_objetivo()
            self.coordenadas_atacadas.add((fila, col))
            if self.tablero_usuario[fila][col] == 1:
                self.botones_usuario[fila][col].config(text="*", bg="red")
                self.tablero_usuario[fila][col] = 0
                self.agregar_ataques_pendientes(fila, col)
                if self.verificar_ganador():
                    return
                # Programar el siguiente disparo después de 1 segundo
                self.root.after(1500, self.disparar_computadora_2)
            else:
                self.botones_usuario[fila][col].config(text="x", bg="blue")
                self.turno_usuario = True
                self.label_barco_actual.config(text="Es tu turno!", font=("Helvetica", 14, "bold"))

    def seleccionar_objetivo(self):
        while self.ataques_pendientes:
            fila, col = self.ataques_pendientes.pop(0)
            if (fila, col) not in self.coordenadas_atacadas:
                return fila, col
        while True:
            fila = randint(0, 9)
            col = randint(0, 9)
            if (fila, col) not in self.coordenadas_atacadas:
                return fila, col

    def agregar_ataques_pendientes(self, fila, col):
        for i in range(-1, 2):
            for j in range(-1, 2):
                nueva_fila = fila + i
                nueva_col = col + j
                if (i == 0 or j == 0) and 0 <= nueva_fila < 10 and 0 <= nueva_col < 10:
                    if (nueva_fila, nueva_col) not in self.coordenadas_atacadas:
                        self.ataques_pendientes.append((nueva_fila, nueva_col))

    def verificar_ganador(self):
        barcos_computadora = sum(sum(fila) for fila in self.tablero_computadora)
        if barcos_computadora == 0:
            messagebox.showinfo("¡Felicidades!", "¡Has ganado! Has derribado todos los barcos de la computadora.")
            self.label_barco_actual.config(text="Ganaste :)", font=("Helvetica", 14, "bold"))
            return True
        barcos_usuario = sum(sum(fila) for fila in self.tablero_usuario)
        if barcos_usuario == 0:
            messagebox.showinfo("¡Lo siento!", "¡La computadora ha ganado! Ha derribado todos tus barcos.")
            self.label_barco_actual.config(text="Perdiste :,(", font=("Helvetica", 14, "bold"))
            return True
        return False

class JuegoSopaLetras:
    def __init__(self, root, nombre_usuario, palabras_validas):
        self.root = root
        self.nombre_usuario = nombre_usuario
        self.root.title("Sopa De Letras")

        self.palabras_validas = palabras_validas
        self.tablero = self.generar_tablero()
        self.botones = []
        self.tiempo_restante = 0  # Tiempo en segundos
        self.temporizador_corriendo = False
        self.palabras_ingresadas = []
        self.palabras_validas_encontradas = []
        self.letras_usadas = set()
        self.color_indice = 0
        self.colores = ['yellow', 'lightblue', 'lightgreen', 'orange', 'pink', 'lightgrey']
        self.crear_tablero()

        self.label_usuario = tk.Label(root, text=f"Tablero del jugador: {nombre_usuario}")
        self.label_usuario.grid(row=0, column=10)

        self.boton_reiniciar = tk.Button(root, text="Reiniciar Con\nUn Nuevo Tablero", command=self.reiniciar_juego, cursor="hand2")
        self.boton_reiniciar.grid(row=1, column=10)

        self.label_tiempo = tk.Label(root, text=f"Tiempo restante: {self.tiempo_restante} s")
        self.label_tiempo.grid(row=2, column=10)

        self.boton_volver = tk.Button(root, text="Volver", command=self.volver, cursor="hand2", width=10, height=3)
        self.boton_volver.grid(row=9, column=10)#, sticky='se', padx=100, pady=10)

        self.boton_empezar = tk.Button(root, text="Empezar Juego", command=self.empezar_juego, cursor="hand2", height=3)
        self.boton_empezar.grid(row=3, column=10)

        self.entry_palabra = tk.Entry(root)
        self.entry_palabra.grid(row=4, column=10, pady=(10, 0))
        self.entry_palabra.bind("<Return>", lambda event: self.ingresar_palabra())

        self.boton_verificar = tk.Button(root, text="Ingresar palabra", command=self.ingresar_palabra, cursor="hand2")
        self.boton_verificar.grid(row=5, column=10, pady=(10, 0))

        self.ocultar_botones_juego()

    def ocultar_botones_juego(self):
        self.entry_palabra.grid_remove()
        self.boton_verificar.grid_remove()
        self.boton_reiniciar.grid_remove()

    def mostrar_botones_juego(self):
        self.entry_palabra.grid()
        self.boton_verificar.grid()
        self.boton_reiniciar.grid()

    def generar_tablero(self):
        letras = 'AAAAABBCCCDDEEEEFFGGHIIIJKLLMMNNÑOOOOPPPQRRSSSTTUUUVWXYZ'
        tablero = []
        for _ in range(10):
            fila = [choice(letras) for _ in range(10)]
            tablero.append(fila)
        return tablero

    def crear_tablero(self):
        if self.botones:
            for fila in self.botones:
                for boton in fila:
                    boton.grid_forget()
        self.botones = []
        for i in range(10):
            fila_botones = []
            for j in range(10):
                boton = tk.Button(self.root, width=6, height=3, bg='black', state="disabled", font=("Roboto Cn", 9, "bold"))
                boton.grid(row=i, column=j, padx=1, pady=1)
                fila_botones.append(boton)
            self.botones.append(fila_botones)

    def reiniciar_juego(self):
        if self.temporizador_corriendo:
            self.root.after_cancel(self.temporizador_corriendo)
            self.temporizador_corriendo = False
        # Eliminar todos los widgets de la ventana principal
        for widget in self.root.winfo_children():
            widget.destroy()
        # Crear una nueva instancia de JuegoSopaLetras
        self.juego_sopa_letras = JuegoSopaLetras(self.root, self.nombre_usuario, self.palabras_validas)

    def ingresar_palabra(self):
        palabra = self.entry_palabra.get().strip().upper()
        if not palabra:
            messagebox.showerror("Error", "Debe ingresar una palabra.")
            return
        self.palabras_ingresadas.append(palabra)
        self.entry_palabra.delete(0, tk.END)

    def puede_formarse_en_tablero(self, palabra):
        if len(palabra) < 3:
            return False  # Si la palabra tiene menos de tres letras, devolver False
        def dfs(x, y, index, visitado):
            if index == len(palabra):
                return True
            if (x < 0 or x >= 10 or y < 0 or y >= 10 or self.tablero[x][y] != palabra[index] or 
                (x, y) in visitado or (x, y) in self.letras_usadas):
                return False
            visitado.add((x, y))
            direcciones = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
            for dx, dy in direcciones:
                if dfs(x + dx, y + dy, index + 1, visitado):
                    return True
            visitado.remove((x, y))
            return False

        for i in range(10):
            for j in range(10):
                if self.tablero[i][j] == palabra[0]:
                    if dfs(i, j, 0, set()):
                        return True
        return False

    def marcar_palabra(self, palabra):
        # Función recursiva para buscar la palabra en el tablero usando DFS
        def dfs(x, y, index, visitado, camino):
            # Si hemos encontrado todas las letras de la palabra
            if index == len(palabra):
                return True
            # Si estamos fuera del tablero, la letra actual no coincide, o ya hemos visitado esta posición
            if (x < 0 or x >= 10 or y < 0 or y >= 10 or self.tablero[x][y] != palabra[index] or 
                (x, y) in visitado or (x, y) in self.letras_usadas):
                return False
            # Marcar la posición actual como visitada
            visitado.add((x, y))
            # Agregar la posición actual al camino de letras que forman la palabra
            camino.append((x, y))
            # Direcciones para moverse en el tablero (vertical, horizontal y diagonal)
            direcciones = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
            # Intentar continuar la búsqueda en todas las direcciones
            for dx, dy in direcciones:
                if dfs(x + dx, y + dy, index + 1, visitado, camino):
                    return True
            # Si no se encontró la palabra, deshacer las marcas
            visitado.remove((x, y))
            camino.pop()
            return False

        # Variable para seguir buscando incluso después de encontrar una instancia de la palabra
        encontrado = False
        color_actual = self.colores[self.color_indice]

        # Intentar encontrar la palabra en el tablero
        for i in range(10):
            for j in range(10):
                # Si la letra inicial de la palabra coincide con la del tablero en esta posición
                if self.tablero[i][j] == palabra[0]:
                    visitado = set()
                    camino = []
                    # Si se puede formar la palabra desde esta posición
                    if dfs(i, j, 0, visitado, camino):
                        if palabra.lower() in self.palabras_validas and len(palabra) >= 3:
                            # Marcar todas las posiciones del camino de color_actual y bloquear los botones
                            for x, y in camino:
                                self.botones[x][y].config(bg=color_actual, text=self.tablero[x][y], state="disabled")
                                # Añadir las posiciones marcadas a letras_usadas para que no se reutilicen
                                self.letras_usadas.add((x, y))
                            encontrado = True  # Marcar que se encontró al menos una instancia
                        else: #ver de que color marcar
                            # Marcar todas las posiciones del camino de rojo y bloquear los botones
                            for x, y in camino:
                                self.botones[x][y].config(bg="darkred", text=self.tablero[x][y], state="disabled")
                                # Añadir las posiciones marcadas a letras_usadas para que no se reutilicen
                                self.letras_usadas.add((x, y))

        if encontrado == True:
            # Cambiar al siguiente color para la próxima palabra
            self.color_indice = (self.color_indice + 1) % len(self.colores)

    def terminar_juego(self):
        if self.temporizador_corriendo:
            self.root.after_cancel(self.temporizador_corriendo)
            self.temporizador_corriendo = False

        validas = []
        invalidas = []
        for palabra in self.palabras_ingresadas:
            if palabra.lower() in self.palabras_validas and self.puede_formarse_en_tablero(palabra):
                validas.append(palabra)
                self.marcar_palabra(palabra)
            else:
                invalidas.append(palabra)
                self.marcar_palabra(palabra)

        puntuacion = sum(len(palabra) * 10 for palabra in validas)
        self.mostrar_puntos(puntuacion, validas, invalidas)

    def mostrar_puntos(self, puntuacion, validas, invalidas):
        messagebox.showinfo("Puntuación", f"Tu puntuación es: {puntuacion}\nPalabras encontradas: {', '.join(validas)}\nPalabras no encontradas o no válidas(rojo): {', '.join(invalidas)}")

    def actualizar_tiempo(self):
        if self.tiempo_restante > 0:
            self.tiempo_restante -= 1
            self.label_tiempo.config(text=f"Tiempo restante: {self.tiempo_restante} s")
            self.temporizador_corriendo = self.root.after(1000, self.actualizar_tiempo)
        else:
            self.terminar_juego()

    def volver(self):
        if self.temporizador_corriendo:
            self.root.after_cancel(self.temporizador_corriendo)
            self.temporizador_corriendo = None
        # Destruir todos los widgets en la ventana actual
        for widget in self.root.winfo_children():
            widget.destroy()
        # Volver al menú principal
        self.app = Aplicacion(self.root)

    def empezar_juego(self):
        tiempo_minutos = simpledialog.askinteger("Tiempo de juego", "Ingrese el tiempo de juego en minutos:")
        self.palabras_ingresadas = []
        self.palabras_validas_encontradas = []
        self.letras_usadas = set()
        if tiempo_minutos is not None and tiempo_minutos > 0:
            # Cancelar el temporizador actual si está en ejecución
            if self.temporizador_corriendo:
                self.root.after_cancel(self.temporizador_corriendo)
                self.temporizador_corriendo = None
            self.tiempo_restante = tiempo_minutos * 60
            self.label_tiempo.config(text=f"Tiempo restante: {self.tiempo_restante} s")
            self.temporizador_corriendo = self.root.after(1000, self.actualizar_tiempo)
            self.mostrar_tablero()
            self.mostrar_botones_juego()

    def mostrar_tablero(self):
        for i in range(10):
            for j in range(10):
                self.botones[i][j].config(bg='white', text=self.tablero[i][j], state="disabled")

class Aplicacion:
    def __init__(self, root):
        self.root = root
        self.root.title("Juegos Divertidos")
        self.marco = tk.Frame(self.root)
        self.marco.pack(expand=True, fill=tk.BOTH, pady=20)  # Ajusta el empaquetado para que se expanda y llene el espacio, con un relleno vertical

        # Etiqueta y campo de entrada para el nombre del usuario
        self.etiqueta_nombre = tk.Label(self.marco, text="Introduce tu nombre:")
        self.etiqueta_nombre.pack(pady=(10, 5))  # Ajusta el espacio alrededor de la etiqueta
        self.entrada_nombre = tk.Entry(self.marco)
        self.entrada_nombre.insert(0, "Jugador")
        self.entrada_nombre.pack(pady=(5, 50))

        # Botones centrados y más grandes
        self.boton_batalla_naval = tk.Button(self.marco, text="Batalla Naval", cursor="hand2", command=self.iniciar_batalla_naval, width=20, height=5)
        self.boton_batalla_naval.pack(side=tk.LEFT, padx=10)  # Ajusta el espacio alrededor del botón
        self.boton_sopa_letras = tk.Button(self.marco, text="Sopa de Letras", cursor="hand2", command=self.iniciar_sopa_letras, width=20, height=5)
        self.boton_sopa_letras.pack(side=tk.LEFT, padx=10)  # Ajusta el espacio alrededor del botón

        # Botón para salir
        self.boton_salir = tk.Button(self.marco, text="Salir", cursor="hand2", command=self.root.destroy, width=20, height=5)
        self.boton_salir.pack(side=tk.RIGHT, padx=10)  # Ubica el botón en la esquina inferior derecha

        # Centra el marco dentro de la ventana
        self.marco.place(relx=0.5, rely=0.4, anchor=tk.CENTER)  # Ajusta la posición relativa del marco

    def iniciar_batalla_naval(self):
        nombre_usuario = self.entrada_nombre.get()
        if nombre_usuario:
            for widget in self.root.winfo_children():
                widget.destroy()
            self.juego_batalla_naval = JuegoBatallaNaval(self.root, nombre_usuario)

    def iniciar_sopa_letras(self):
        nombre_usuario = self.entrada_nombre.get()
        if nombre_usuario:
            for widget in self.root.winfo_children():
                widget.destroy()
            self.juego_sopa_letras = JuegoSopaLetras(self.root, nombre_usuario, lineas)

if __name__ == "__main__":
    root = tk.Tk()
    app = Aplicacion(root)
    root.state('zoomed')  # Maximizar la ventana al iniciar
    root.mainloop()
