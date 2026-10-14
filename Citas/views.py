# views.py es el CONTROLADOR: decide y guarda. Nunca usa print() ni input().
# Todo devuelve (True/False, "mensaje"), listas u objetos; la Vista los muestra.
import os
from abc import ABC, abstractmethod

from models import Paciente, Medico, Cita
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
# PACIENTES  (molde: SocioController de Biblioteca)  · regla única: cédula y email
# =====================================================================
class PacienteController(CrudBase):

    def __init__(self, archivo=os.path.join(BASE, "data", "pacientes.json")):
        self.nombre = "paciente"
        self.campos = Paciente.CAMPOS
        self.gestor = GestorJSON(archivo)

        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Paciente.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for paciente in self.lista:
            datos.append(paciente.a_diccionario())
        self.gestor.guardar(datos)

    def obtener(self, id_paciente):
        for paciente in self.lista:
            if paciente.id == id_paciente:
                return paciente
        return None

    def leer(self):
        return self.lista

    def buscar(self, texto):
        texto = texto.strip().lower()
        encontrados = []
        if texto == "":
            return encontrados

        for paciente in self.lista:
            if (texto in paciente.nombre.lower()
                    or texto in paciente.apellido.lower()
                    or texto in paciente.cedula):
                encontrados.append(paciente)
        return encontrados

    def siguiente(self):
        mayor = 0
        for paciente in self.lista:
            if paciente.id > mayor:
                mayor = paciente.id
        return mayor + 1

    def repetido(self, cedula, email, id_actual=None):
        cedula = str(cedula).strip()
        email = str(email).strip().lower()
        for otro in self.lista:
            if otro.id == id_actual:
                continue
            if otro.cedula == cedula:
                return f"La cédula {cedula} ya está registrada"
            if otro.email == email:
                return f"El email {email} ya está registrado"
        return None

    def crear(self, datos):
        error = self.repetido(datos.get("cedula", ""), datos.get("email", ""))
        if error:
            return False, error

        try:
            paciente = Paciente(self.siguiente(),
                                datos.get("nombre", ""),
                                datos.get("apellido", ""),
                                datos.get("email", ""),
                                datos.get("cedula", ""),
                                datos.get("telefono", ""))
        except ValueError as error:
            return False, str(error)

        self.lista.append(paciente)
        self.guardar()
        return True, f"Paciente creado: {paciente.etiqueta()}"

    def actualizar(self, id_paciente, datos):
        if not datos:
            return False, "No se indicó ningún cambio"

        paciente = self.obtener(id_paciente)
        if paciente is None:
            return False, f"No existe paciente con id {id_paciente}"

        error = self.repetido(datos.get("cedula", paciente.cedula),
                              datos.get("email", paciente.email),
                              id_actual=id_paciente)
        if error:
            return False, error

        try:
            nuevo = Paciente(paciente.id,
                             datos.get("nombre", paciente.nombre),
                             datos.get("apellido", paciente.apellido),
                             datos.get("email", paciente.email),
                             datos.get("cedula", paciente.cedula),
                             datos.get("telefono", paciente.telefono))
        except ValueError as error:
            return False, str(error)

        posicion = self.lista.index(paciente)
        self.lista[posicion] = nuevo
        self.guardar()
        return True, f"Paciente {id_paciente} actualizado"

    def eliminar(self, id_paciente):
        paciente = self.obtener(id_paciente)
        if paciente is None:
            return False, f"No existe paciente con id {id_paciente}"

        self.lista.remove(paciente)
        self.guardar()
        return True, f"Paciente {id_paciente} eliminado"


# =====================================================================
# MÉDICOS  (molde: DocenteController)  · regla única: email
# =====================================================================
class MedicoController(CrudBase):

    def __init__(self, archivo=os.path.join(BASE, "data", "medicos.json")):
        self.nombre = "médico"
        self.campos = Medico.CAMPOS
        self.gestor = GestorJSON(archivo)

        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Medico.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for medico in self.lista:
            datos.append(medico.a_diccionario())
        self.gestor.guardar(datos)

    def obtener(self, id_medico):
        for medico in self.lista:
            if medico.id == id_medico:
                return medico
        return None

    def leer(self):
        return self.lista

    def buscar(self, texto):
        texto = texto.strip().lower()
        encontrados = []
        if texto == "":
            return encontrados

        for medico in self.lista:
            if (texto in medico.nombre.lower()
                    or texto in medico.apellido.lower()
                    or texto in medico.especialidad.lower()):
                encontrados.append(medico)
        return encontrados

    def siguiente(self):
        mayor = 0
        for medico in self.lista:
            if medico.id > mayor:
                mayor = medico.id
        return mayor + 1

    def crear(self, datos):
        email = str(datos.get("email", "")).strip().lower()
        for medico in self.lista:
            if medico.email == email:
                return False, f"El email {email} ya está registrado"

        try:
            medico = Medico(self.siguiente(),
                            datos.get("nombre", ""),
                            datos.get("apellido", ""),
                            datos.get("email", ""),
                            datos.get("especialidad", ""))
        except ValueError as error:
            return False, str(error)

        self.lista.append(medico)
        self.guardar()
        return True, f"Médico creado: {medico.etiqueta()}"

    def actualizar(self, id_medico, datos):
        if not datos:
            return False, "No se indicó ningún cambio"

        medico = self.obtener(id_medico)
        if medico is None:
            return False, f"No existe médico con id {id_medico}"

        if "email" in datos:
            email = str(datos["email"]).strip().lower()
            for otro in self.lista:
                if otro.email == email and otro.id != id_medico:
                    return False, f"El email {email} ya está registrado"

        try:
            nuevo = Medico(medico.id,
                           datos.get("nombre", medico.nombre),
                           datos.get("apellido", medico.apellido),
                           datos.get("email", medico.email),
                           datos.get("especialidad", medico.especialidad))
        except ValueError as error:
            return False, str(error)

        posicion = self.lista.index(medico)
        self.lista[posicion] = nuevo
        self.guardar()
        return True, f"Médico {id_medico} actualizado"

    def eliminar(self, id_medico):
        medico = self.obtener(id_medico)
        if medico is None:
            return False, f"No existe médico con id {id_medico}"

        self.lista.remove(medico)
        self.guardar()
        return True, f"Médico {id_medico} eliminado"


# =====================================================================
# CITAS  (molde: MatriculaController)
# Regla clave: un médico no puede tener dos citas a la misma hora
# =====================================================================
class CitaController(CrudBase):

    def __init__(self, pacientes, medicos,
                 archivo=os.path.join(BASE, "data", "citas.json")):
        self.nombre = "cita"
        self.campos = Cita.CAMPOS
        self.gestor = GestorJSON(archivo)
        self.pacientes = pacientes
        self.medicos = medicos

        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Cita.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for cita in self.lista:
            datos.append(cita.a_diccionario())
        self.gestor.guardar(datos)

    def obtener(self, id_cita):
        for cita in self.lista:
            if cita.id == id_cita:
                return cita
        return None

    def leer(self):
        return self.lista

    def buscar(self, texto):
        # Se busca por fecha, estado o motivo
        texto = texto.strip().lower()
        encontrados = []
        if texto == "":
            return encontrados

        for cita in self.lista:
            if (texto in cita.fecha
                    or texto in cita.estado.lower()
                    or texto in cita.motivo.lower()):
                encontrados.append(cita)
        return encontrados

    def siguiente(self):
        mayor = 0
        for cita in self.lista:
            if cita.id > mayor:
                mayor = cita.id
        return mayor + 1

    def validar(self, cita, id_actual=None):
        """Revisa existencia y choques de horario. Devuelve error o None."""
        if self.pacientes.obtener(cita.paciente_id) is None:
            return f"No existe un paciente con id {cita.paciente_id}"
        if self.medicos.obtener(cita.medico_id) is None:
            return f"No existe un médico con id {cita.medico_id}"

        for otra in self.lista:
            if otra.id == id_actual or otra.estado == "Cancelada":
                continue
            if otra.fecha == cita.fecha and otra.hora == cita.hora:
                if otra.medico_id == cita.medico_id:
                    return f"El médico ya tiene una cita el {cita.fecha} a las {cita.hora}"
                if otra.paciente_id == cita.paciente_id:
                    return f"El paciente ya tiene una cita el {cita.fecha} a las {cita.hora}"
        return None

    def crear(self, datos):
        # Primero el MODELO valida formato de fecha y hora
        try:
            cita = Cita(self.siguiente(),
                        int(datos.get("paciente_id", 0)),
                        int(datos.get("medico_id", 0)),
                        datos.get("fecha", ""),
                        datos.get("hora", ""),
                        datos.get("motivo", ""))
        except ValueError as error:
            mensaje = str(error)
            if "invalid literal" in mensaje:
                mensaje = "Los ids de paciente y médico deben ser números"
            return False, mensaje

        # Después el CONTROLADOR revisa contra las demás citas
        error = self.validar(cita)
        if error:
            return False, error

        self.lista.append(cita)
        self.guardar()
        return True, f"Cita {cita.id} agendada: {cita.fecha} a las {cita.hora}"

    def actualizar(self, id_cita, datos):
        if not datos:
            return False, "No se indicó ningún cambio"

        cita = self.obtener(id_cita)
        if cita is None:
            return False, f"No existe cita con id {id_cita}"
        if cita.estado != "Pendiente":
            return False, f"No se puede reprogramar una cita {cita.estado.lower()}"

        try:
            nueva = Cita(cita.id,
                         int(datos.get("paciente_id", cita.paciente_id)),
                         int(datos.get("medico_id", cita.medico_id)),
                         datos.get("fecha", cita.fecha),
                         datos.get("hora", cita.hora),
                         datos.get("motivo", cita.motivo))
        except ValueError as error:
            mensaje = str(error)
            if "invalid literal" in mensaje:
                mensaje = "Los ids de paciente y médico deben ser números"
            return False, mensaje

        error = self.validar(nueva, id_actual=id_cita)
        if error:
            return False, error

        posicion = self.lista.index(cita)
        self.lista[posicion] = nueva
        self.guardar()
        return True, f"Cita {id_cita} reprogramada"

    def eliminar(self, id_cita):
        cita = self.obtener(id_cita)
        if cita is None:
            return False, f"No existe cita con id {id_cita}"

        self.lista.remove(cita)
        self.guardar()
        return True, f"Cita {id_cita} eliminada"

    # --- métodos propios de citas ---
    def cambiar_estado(self, id_cita, accion):
        """accion: 'atender' o 'cancelar'. El MODELO decide si se puede."""
        cita = self.obtener(id_cita)
        if cita is None:
            return False, f"No existe cita con id {id_cita}"

        try:
            if accion == "atender":
                cita.atender()
            else:
                cita.cancelar()
        except ValueError as error:
            return False, str(error)

        self.guardar()
        return True, f"Cita {id_cita}: {cita.estado}"

    def agenda(self, medico_id, fecha):
        """Texto con las citas de un médico en un día, ordenadas por hora."""
        medico = self.medicos.obtener(medico_id)
        if medico is None:
            return None

        del_dia = []
        for cita in self.lista:
            if cita.medico_id == medico_id and cita.fecha == fecha.strip():
                del_dia.append(cita)
        del_dia.sort(key=lambda cita: cita.hora)

        texto = f"AGENDA DE {medico.etiqueta().upper()}\n"
        texto += f"Fecha: {fecha}\n" + "-" * 50 + "\n"
        if len(del_dia) == 0:
            texto += "  Sin citas ese día\n"
        for cita in del_dia:
            paciente = self.pacientes.obtener(cita.paciente_id)
            nombre = paciente.nombre_completo if paciente else "paciente eliminado"
            texto += f"  {cita.hora}  {nombre:<22} {cita.estado}\n"
        texto += "-" * 50
        return texto

    def citas_por_especialidad(self):
        """DICCIONARIO especialidad -> cantidad de citas."""
        conteo = {}
        for cita in self.lista:
            medico = self.medicos.obtener(cita.medico_id)
            especialidad = medico.especialidad if medico else "Sin médico"
            conteo[especialidad] = conteo.get(especialidad, 0) + 1
        return conteo
