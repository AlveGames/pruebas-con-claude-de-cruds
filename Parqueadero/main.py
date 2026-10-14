# main.py es la VISTA: lo único que habla con el usuario (input / print).
# No valida ni guarda: le pide todo a los controladores de views.py.
from shared.herramientas import (
    imprimir_titulo, imprimir_exito, imprimir_error, imprimir_info, confirmar
)
from views import VehiculoController, TicketController


class Menu:

    def __init__(self):
        self.vehiculos = VehiculoController()
        self.tickets = TicketController(self.vehiculos)

    # ---------- ayudas ----------
    def pausa(self):
        input("\nPresione Enter para continuar...")

    def pedir_entero(self, texto):
        try:
            return int(input(texto))
        except ValueError:
            return None

    def mostrar_resultado(self, exito, mensaje):
        if exito:
            imprimir_exito(mensaje)
        else:
            imprimir_error(mensaje)

    # ---------- menú principal ----------
    def ejecutar(self):
        while True:
            imprimir_titulo("SISTEMA DE PARQUEADERO")
            print("  1. Vehículos")
            print("  2. Tickets (entradas y salidas)")
            print("  3. Reporte general")
            print("  4. Espacios disponibles y recaudación")
            print("  0. Salir\n")
            opcion = input("Opción: ").strip()

            if opcion == "1":
                self.menu_crud(self.vehiculos)
            elif opcion == "2":
                self.menu_crud(self.tickets)
            elif opcion == "3":
                self.reporte_general()
            elif opcion == "4":
                self.ver_disponibilidad()
            elif opcion == "0":
                imprimir_info("¡Hasta luego! 👋")
                break
            else:
                imprimir_error("Opción no válida")
                self.pausa()

    def menu_crud(self, controlador):
        titulo = controlador.nombre.upper() + "S"

        while True:
            imprimir_titulo(titulo)
            if controlador == self.tickets:
                print("  1. Registrar entrada")
            else:
                print(f"  1. Crear {controlador.nombre}")
            print("  2. Ver todos")
            print("  3. Buscar")
            print("  4. Ver por id")
            print("  5. Actualizar")
            print("  6. Eliminar")
            if controlador == self.tickets:
                print("  7. Registrar salida y cobrar")
                print("  8. Ver vehículos adentro")
            print("  0. Volver\n")
            opcion = input("Opción: ").strip()

            if opcion == "1":
                self.crear(controlador)
            elif opcion == "2":
                self.ver_todos(controlador)
            elif opcion == "3":
                self.buscar(controlador)
            elif opcion == "4":
                self.ver_por_id(controlador)
            elif opcion == "5":
                self.actualizar(controlador)
            elif opcion == "6":
                self.eliminar(controlador)
            elif opcion == "7" and controlador == self.tickets:
                self.registrar_salida()
            elif opcion == "8" and controlador == self.tickets:
                self.ver_adentro()
            elif opcion == "0":
                break
            else:
                imprimir_error("Opción no válida")
                self.pausa()

    # ---------- operaciones ----------
    def crear(self, controlador):
        imprimir_titulo(f"CREAR {controlador.nombre.upper()}")
        datos = {}
        for campo in controlador.campos:
            datos[campo] = input(f"{campo.capitalize()}: ")

        exito, mensaje = controlador.crear(datos)
        self.mostrar_resultado(exito, mensaje)
        self.pausa()

    def ver_todos(self, controlador):
        imprimir_titulo(controlador.nombre.upper() + "S")
        lista = controlador.leer()
        if len(lista) == 0:
            imprimir_info("No hay registros todavía.")
        else:
            for objeto in lista:
                print(f"  {objeto}")
            imprimir_info(f"Total: {len(lista)}")
        self.pausa()

    def buscar(self, controlador):
        imprimir_titulo(f"BUSCAR {controlador.nombre.upper()}")
        texto = input("Buscar: ")
        encontrados = controlador.buscar(texto)
        if len(encontrados) == 0:
            imprimir_info(f"Sin coincidencias para '{texto}'.")
        else:
            for objeto in encontrados:
                print(f"  {objeto}")
        self.pausa()

    def ver_por_id(self, controlador):
        imprimir_titulo(f"VER {controlador.nombre.upper()}")
        objeto = controlador.obtener(self.pedir_entero("Id: "))
        if objeto is None:
            imprimir_error("No encontrado")
        else:
            for clave, valor in objeto.a_diccionario().items():
                print(f"  {clave.capitalize()}: {valor}")
        self.pausa()

    def actualizar(self, controlador):
        imprimir_titulo(f"ACTUALIZAR {controlador.nombre.upper()}")
        id_registro = self.pedir_entero("Id: ")
        objeto = controlador.obtener(id_registro)
        if objeto is None:
            imprimir_error("No encontrado")
            self.pausa()
            return

        imprimir_info(f"Editando: {objeto.etiqueta()}")
        print("Deje en blanco lo que no quiera cambiar.\n")
        cambios = {}
        for campo in controlador.campos:
            actual = getattr(objeto, campo)
            nuevo = input(f"{campo.capitalize()} [{actual}]: ").strip()
            if nuevo != "":
                cambios[campo] = nuevo

        exito, mensaje = controlador.actualizar(id_registro, cambios)
        self.mostrar_resultado(exito, mensaje)
        self.pausa()

    def eliminar(self, controlador):
        imprimir_titulo(f"ELIMINAR {controlador.nombre.upper()}")
        id_registro = self.pedir_entero("Id: ")
        objeto = controlador.obtener(id_registro)
        if objeto is None:
            imprimir_error("No encontrado")
            self.pausa()
            return

        imprimir_info(f"Se eliminará: {objeto.etiqueta()}")
        if confirmar("¿Confirma?"):
            exito, mensaje = controlador.eliminar(id_registro)
            self.mostrar_resultado(exito, mensaje)
        else:
            imprimir_info("Operación cancelada")
        self.pausa()

    # ---------- solo para tickets ----------
    def registrar_salida(self):
        imprimir_titulo("REGISTRAR SALIDA")
        id_ticket = self.pedir_entero("Id del ticket: ")
        salida = input("Salida AAAA-MM-DD HH:MM (Enter = ahora): ").strip()
        exito, mensaje = self.tickets.registrar_salida(id_ticket, salida or None)
        self.mostrar_resultado(exito, mensaje)
        self.pausa()

    def ver_adentro(self):
        imprimir_titulo("VEHÍCULOS ADENTRO")
        tickets = self.tickets.adentro()
        if len(tickets) == 0:
            imprimir_info("El parqueadero está vacío")
        for ticket in tickets:
            vehiculo = self.vehiculos.obtener(ticket.vehiculo_id)
            placa = vehiculo.placa if vehiculo else "?"
            print(f"  Ticket {ticket.id:<4} {placa:<10} desde {ticket.entrada}")
        self.pausa()

    # ---------- reportes ----------
    def reporte_general(self):
        # POLIMORFISMO: un solo bucle para los 2; cada objeto usa su etiqueta()
        imprimir_titulo("REPORTE GENERAL")
        for controlador in (self.vehiculos, self.tickets):
            print(f"=== {controlador.nombre.upper()}S ({len(controlador.leer())}) ===")
            for objeto in controlador.leer():
                print(f"  {objeto}")
            print()
        self.pausa()

    def ver_disponibilidad(self):
        imprimir_titulo("ESPACIOS Y RECAUDACIÓN")
        for tipo, (ocupados, capacidad) in self.tickets.disponibilidad().items():
            print(f"  {tipo.capitalize():<6} {ocupados}/{capacidad} ocupados · "
                  f"{capacidad - ocupados} libres")
        imprimir_info(f"Total recaudado: ${self.tickets.recaudado():.2f}")
        self.pausa()


if __name__ == "__main__":
    try:
        Menu().ejecutar()
    except KeyboardInterrupt:
        print("\nPrograma interrumpido por el usuario.")
