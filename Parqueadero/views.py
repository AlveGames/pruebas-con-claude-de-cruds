# views.py es el CONTROLADOR: decide y guarda. Nunca usa print() ni input().
# Todo devuelve (True/False, "mensaje"), listas u objetos; la Vista los muestra.
import os
from abc import ABC, abstractmethod

from models import Vehiculo, Ticket
from shared.json_manager import GestorJSON

BASE = os.path.dirname(os.path.abspath(__file__))


# =====================================================================
# ABSTRACCIÓN: lo que todo controlador debe tener
# =====================================================================
class CrudBase(ABC):

    @abstractmethod
    def leer(self):
        pass

    @abstractmethod
    def buscar(self, texto):
        pass

    @abstractmethod
    def siguiente(self):
        pass

    @abstractmethod
    def crear(self, datos):
        pass

    @abstractmethod
    def actualizar(self, id_registro, datos):
        pass

    @abstractmethod
    def eliminar(self, id_registro):
        pass


# =====================================================================
# VEHÍCULOS  (molde: LibroController)  · regla única: placa
# =====================================================================
class VehiculoController(CrudBase):

    def __init__(self, archivo=os.path.join(BASE, "data", "vehiculos.json")):
        self.nombre = "vehículo"
        self.campos = Vehiculo.CAMPOS
        self.gestor = GestorJSON(archivo)

        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Vehiculo.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for vehiculo in self.lista:
            datos.append(vehiculo.a_diccionario())
        self.gestor.guardar(datos)

    def obtener(self, id_vehiculo):
        for vehiculo in self.lista:
            if vehiculo.id == id_vehiculo:
                return vehiculo
        return None

    def obtener_por_placa(self, placa):
        placa = str(placa).strip().upper()
        for vehiculo in self.lista:
            if vehiculo.placa == placa:
                return vehiculo
        return None

    def leer(self):
        return self.lista

    def buscar(self, texto):
        texto = texto.strip().lower()
        encontrados = []
        if texto == "":
            return encontrados

        for vehiculo in self.lista:
            if (texto in vehiculo.placa.lower()
                    or texto in vehiculo.tipo
                    or texto in vehiculo.propietario.lower()):
                encontrados.append(vehiculo)
        return encontrados

    def siguiente(self):
        mayor = 0
        for vehiculo in self.lista:
            if vehiculo.id > mayor:
                mayor = vehiculo.id
        return mayor + 1

    def crear(self, datos):
        if self.obtener_por_placa(datos.get("placa", "")) is not None:
            return False, f"La placa {str(datos.get('placa')).strip().upper()} ya está registrada"

        try:
            vehiculo = Vehiculo(self.siguiente(),
                                datos.get("placa", ""),
                                datos.get("tipo", ""),
                                datos.get("propietario", ""))
        except ValueError as error:
            return False, str(error)

        self.lista.append(vehiculo)
        self.guardar()
        return True, f"Vehículo registrado: {vehiculo.etiqueta()}"

    def actualizar(self, id_vehiculo, datos):
        if not datos:
            return False, "No se indicó ningún cambio"

        vehiculo = self.obtener(id_vehiculo)
        if vehiculo is None:
            return False, f"No existe vehículo con id {id_vehiculo}"

        if "placa" in datos:
            otro = self.obtener_por_placa(datos["placa"])
            if otro is not None and otro.id != id_vehiculo:
                return False, f"La placa {otro.placa} ya está registrada"

        try:
            nuevo = Vehiculo(vehiculo.id,
                             datos.get("placa", vehiculo.placa),
                             datos.get("tipo", vehiculo.tipo),
                             datos.get("propietario", vehiculo.propietario))
        except ValueError as error:
            return False, str(error)

        posicion = self.lista.index(vehiculo)
        self.lista[posicion] = nuevo
        self.guardar()
        return True, f"Vehículo {id_vehiculo} actualizado"

    def eliminar(self, id_vehiculo):
        vehiculo = self.obtener(id_vehiculo)
        if vehiculo is None:
            return False, f"No existe vehículo con id {id_vehiculo}"

        self.lista.remove(vehiculo)
        self.guardar()
        return True, f"Vehículo {id_vehiculo} eliminado"


# =====================================================================
# TICKETS  (molde: PrestamoController de Biblioteca)
# Entrada -> ticket abierto. Salida -> se cierra y se cobra.
# =====================================================================
class TicketController(CrudBase):

    CAPACIDAD = {"auto": 10, "moto": 5}     # espacios por tipo

    def __init__(self, vehiculos, archivo=os.path.join(BASE, "data", "tickets.json")):
        self.nombre = "ticket"
        self.campos = Ticket.CAMPOS
        self.gestor = GestorJSON(archivo)
        self.vehiculos = vehiculos

        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Ticket.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for ticket in self.lista:
            datos.append(ticket.a_diccionario())
        self.gestor.guardar(datos)

    def obtener(self, id_ticket):
        for ticket in self.lista:
            if ticket.id == id_ticket:
                return ticket
        return None

    def leer(self):
        return self.lista

    def buscar(self, texto):
        # Se busca por estado ("abierto" / "cerrado") o por fecha
        texto = texto.strip().lower()
        encontrados = []
        if texto == "":
            return encontrados

        for ticket in self.lista:
            if texto in ticket.estado.lower() or texto in ticket.entrada:
                encontrados.append(ticket)
        return encontrados

    def siguiente(self):
        mayor = 0
        for ticket in self.lista:
            if ticket.id > mayor:
                mayor = ticket.id
        return mayor + 1

    def adentro(self):
        """LISTA de tickets abiertos (vehículos que siguen en el parqueadero)."""
        resultado = []
        for ticket in self.lista:
            if ticket.estado == "Abierto":
                resultado.append(ticket)
        return resultado

    def ocupados(self, tipo):
        cuenta = 0
        for ticket in self.adentro():
            vehiculo = self.vehiculos.obtener(ticket.vehiculo_id)
            if vehiculo is not None and vehiculo.tipo == tipo:
                cuenta += 1
        return cuenta

    def crear(self, datos):
        """Registra la ENTRADA de un vehículo."""
        try:
            vehiculo_id = int(datos.get("vehiculo_id", 0))
        except (TypeError, ValueError):
            return False, "El id del vehículo debe ser un número"

        vehiculo = self.vehiculos.obtener(vehiculo_id)
        if vehiculo is None:
            return False, f"No existe un vehículo con id {vehiculo_id}"

        for ticket in self.adentro():
            if ticket.vehiculo_id == vehiculo_id:
                return False, f"El vehículo {vehiculo.placa} ya está adentro (ticket {ticket.id})"

        if self.ocupados(vehiculo.tipo) >= self.CAPACIDAD[vehiculo.tipo]:
            return False, f"No hay espacios libres para {vehiculo.tipo}"

        ticket = Ticket(self.siguiente(), vehiculo_id, datos.get("entrada") or None)
        self.lista.append(ticket)
        self.guardar()
        return True, f"Ticket {ticket.id}: entrada de {vehiculo.placa} a las {ticket.entrada}"

    def actualizar(self, id_ticket, datos):
        return False, "Los tickets no se editan; use la opción Registrar salida"

    def eliminar(self, id_ticket):
        ticket = self.obtener(id_ticket)
        if ticket is None:
            return False, f"No existe ticket con id {id_ticket}"

        self.lista.remove(ticket)
        self.guardar()
        return True, f"Ticket {id_ticket} eliminado"

    # --- métodos propios ---
    def registrar_salida(self, id_ticket, salida=None):
        ticket = self.obtener(id_ticket)
        if ticket is None:
            return False, f"No existe ticket con id {id_ticket}"

        vehiculo = self.vehiculos.obtener(ticket.vehiculo_id)
        tipo = vehiculo.tipo if vehiculo else "auto"

        try:
            horas = ticket.cerrar(tipo, salida)
        except ValueError as error:
            return False, str(error)

        self.guardar()
        return True, f"Salida registrada: {horas} hora(s) · total ${ticket.total:.2f}"

    def disponibilidad(self):
        """DICCIONARIO tipo -> (ocupados, capacidad)."""
        resultado = {}
        for tipo, capacidad in self.CAPACIDAD.items():
            resultado[tipo] = (self.ocupados(tipo), capacidad)
        return resultado

    def recaudado(self):
        total = 0
        for ticket in self.lista:
            total += ticket.total
        return round(total, 2)
