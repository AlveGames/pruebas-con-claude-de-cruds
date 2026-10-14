# main.py es la VISTA: lo único que habla con el usuario (input / print).
# No valida ni guarda: le pide todo a los controladores de views.py.
from shared.herramientas import (
    imprimir_titulo, imprimir_exito, imprimir_error, imprimir_info, confirmar
)
from views import PacienteController, MedicoController, CitaController


class Menu:

    def __init__(self):
        self.pacientes = PacienteController()
        self.medicos = MedicoController()
        self.citas = CitaController(self.pacientes, self.medicos)

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
            imprimir_titulo("SISTEMA DE CITAS MÉDICAS")
            print("  1. Pacientes")
            print("  2. Médicos")
            print("  3. Citas")
            print("  4. Reporte general")
            print("  5. Citas por especialidad")
            print("  0. Salir\n")
            opcion = input("Opción: ").strip()

            if opcion == "1":
                self.menu_crud(self.pacientes)
            elif opcion == "2":
                self.menu_crud(self.medicos)
            elif opcion == "3":
                self.menu_crud(self.citas)
            elif opcion == "4":
                self.reporte_general()
            elif opcion == "5":
                self.ver_por_especialidad()
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
            print(f"  1. Crear {controlador.nombre}")
            print("  2. Ver todos")
            print("  3. Buscar")
            print("  4. Ver por id")
            print("  5. Actualizar")
            print("  6. Eliminar")
            if controlador == self.citas:
                print("  7. Marcar como atendida")
                print("  8. Cancelar cita")
                print("  9. Agenda de un médico")
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
            elif opcion == "7" and controlador == self.citas:
                self.cambiar_estado("atender")
            elif opcion == "8" and controlador == self.citas:
                self.cambiar_estado("cancelar")
            elif opcion == "9" and controlador == self.citas:
                self.ver_agenda()
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
            datos[campo] = input(f"{campo.capitalize()}: ")   # fecha: AAAA-MM-DD, hora: HH:MM

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

    # ---------- solo para citas ----------
    def cambiar_estado(self, accion):
        imprimir_titulo("ATENDER CITA" if accion == "atender" else "CANCELAR CITA")
        exito, mensaje = self.citas.cambiar_estado(self.pedir_entero("Id de la cita: "), accion)
        self.mostrar_resultado(exito, mensaje)
        self.pausa()

    def ver_agenda(self):
        imprimir_titulo("AGENDA")
        medico_id = self.pedir_entero("Id del médico: ")
        fecha = input("Fecha (AAAA-MM-DD): ")
        texto = self.citas.agenda(medico_id, fecha)
        if texto is None:
            imprimir_error("No existe ese médico")
        else:
            print(texto)
        self.pausa()

    # ---------- reportes ----------
    def reporte_general(self):
        # POLIMORFISMO: un solo bucle para los 3; cada objeto usa su etiqueta()
        imprimir_titulo("REPORTE GENERAL")
        for controlador in (self.pacientes, self.medicos, self.citas):
            print(f"=== {controlador.nombre.upper()}S ({len(controlador.leer())}) ===")
            for objeto in controlador.leer():
                print(f"  {objeto}")
            print()
        self.pausa()

    def ver_por_especialidad(self):
        imprimir_titulo("CITAS POR ESPECIALIDAD")
        conteo = self.citas.citas_por_especialidad()
        if len(conteo) == 0:
            imprimir_info("Todavía no hay citas")
        for especialidad, cantidad in conteo.items():
            print(f"  {especialidad:<25} {cantidad} cita(s)")
        self.pausa()


if __name__ == "__main__":
    try:
        Menu().ejecutar()
    except KeyboardInterrupt:
        print("\nPrograma interrumpido por el usuario.")
