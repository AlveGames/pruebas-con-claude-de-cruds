# models.py es el MODELO: define qué es cada cosa y sus reglas propias.
# Cada objeto se valida solo con sus setters. No imprime ni guarda nada.
from abc import ABC, abstractmethod
from datetime import date


# =====================================================================
# ABSTRACCIÓN: base de todos los modelos (igual que en la tarea)
# =====================================================================
class ModeloBase(ABC):

    CAMPOS = ()
    OBLIGATORIOS = ()

    def __init__(self, id_registro):
        self.__id = int(id_registro)

    @property
    def id(self):
        return self.__id

    @staticmethod
    def limpiar(texto):
        return str(texto).strip()

    @abstractmethod
    def a_diccionario(self):
        pass

    @abstractmethod
    def etiqueta(self):
        pass

    @classmethod
    def desde_diccionario(cls, datos):
        valores = {campo: datos.get(campo, "") for campo in cls.CAMPOS}
        return cls(datos["id"], **valores)

    def __str__(self):
        return f"[{self.id}] {self.etiqueta()}"


# =====================================================================
# HERENCIA: Persona -> Socio
# =====================================================================
class Persona(ModeloBase):

    CAMPOS = ("nombre", "apellido", "email")
    OBLIGATORIOS = ("nombre", "apellido", "email")

    def __init__(self, id_registro, nombre, apellido, email):
        super().__init__(id_registro)
        self.nombre = nombre
        self.apellido = apellido
        self.email = email

    @staticmethod
    def es_email_valido(texto):
        texto = str(texto).strip()
        if texto.count("@") != 1:
            return False
        usuario, dominio = texto.split("@")
        return len(usuario) > 0 and "." in dominio and not dominio.endswith(".")

    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        valor = Persona.limpiar(valor)
        if not valor:
            raise ValueError("El nombre es obligatorio")
        self.__nombre = valor.title()

    @property
    def apellido(self):
        return self.__apellido

    @apellido.setter
    def apellido(self, valor):
        valor = Persona.limpiar(valor)
        if not valor:
            raise ValueError("El apellido es obligatorio")
        self.__apellido = valor.title()

    @property
    def email(self):
        return self.__email

    @email.setter
    def email(self, valor):
        valor = Persona.limpiar(valor)
        if not Persona.es_email_valido(valor):
            raise ValueError(f"Email inválido: '{valor}'")
        self.__email = valor.lower()

    @property
    def nombre_completo(self):
        return f"{self.__nombre} {self.__apellido}"

    def a_diccionario(self):
        return {
            "id": self.id,
            "nombre": self.__nombre,
            "apellido": self.__apellido,
            "email": self.__email,
        }




class Paciente(Persona):

    CAMPOS = Persona.CAMPOS + ("cedula", "telefono")
    OBLIGATORIOS = Persona.OBLIGATORIOS + ("cedula",)

    def __init__(self, id_registro, nombre, apellido, email, cedula, telefono=""):
        super().__init__(id_registro, nombre, apellido, email)
        self.cedula = cedula
        self.telefono = telefono

    @property
    def cedula(self):
        return self.__cedula

    @cedula.setter
    def cedula(self, valor):
        valor = Paciente.limpiar(valor)
        if not (valor.isdigit() and len(valor) == 10):
            raise ValueError("La cédula debe tener 10 números")
        self.__cedula = valor

    @property
    def telefono(self):
        return self.__telefono

    @telefono.setter
    def telefono(self, valor):
        valor = Paciente.limpiar(valor)
        if valor and not valor.isdigit():
            raise ValueError("El teléfono solo puede tener números")
        self.__telefono = valor

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos["cedula"] = self.__cedula
        datos["telefono"] = self.__telefono
        return datos

    def etiqueta(self):
        return f"{self.nombre_completo} · cédula {self.__cedula}"


class Medico(Persona):

    CAMPOS = Persona.CAMPOS + ("especialidad",)
    OBLIGATORIOS = Persona.OBLIGATORIOS + ("especialidad",)

    def __init__(self, id_registro, nombre, apellido, email, especialidad):
        super().__init__(id_registro, nombre, apellido, email)
        self.especialidad = especialidad

    @property
    def especialidad(self):
        return self.__especialidad

    @especialidad.setter
    def especialidad(self, valor):
        valor = Medico.limpiar(valor)
        if not valor:
            raise ValueError("La especialidad es obligatoria")
        self.__especialidad = valor.title()

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos["especialidad"] = self.__especialidad
        return datos

    def etiqueta(self):
        return f"Dr(a). {self.nombre_completo} · {self.__especialidad}"


# =====================================================================
# CITA: une a un Paciente con un Médico en una fecha y hora
# =====================================================================
class Cita(ModeloBase):

    CAMPOS = ("paciente_id", "medico_id", "fecha", "hora", "motivo")
    OBLIGATORIOS = ("paciente_id", "medico_id", "fecha", "hora")
    HORA_INICIO = 8      # 08:00
    HORA_FIN = 17        # la última cita empieza a las 16:30
    ESTADOS = ("Pendiente", "Atendida", "Cancelada")

    def __init__(self, id_registro, paciente_id, medico_id, fecha, hora,
                 motivo="", estado="Pendiente"):
        super().__init__(id_registro)
        self.__paciente_id = int(paciente_id)
        self.__medico_id = int(medico_id)
        self.fecha = fecha
        self.hora = hora
        self.motivo = motivo
        self.__estado = estado if estado in Cita.ESTADOS else "Pendiente"

    @staticmethod
    def es_hora_valida(texto):
        """Formato HH:MM, en punto o y media, dentro del horario de atención."""
        texto = str(texto).strip()
        partes = texto.split(":")
        if len(partes) != 2 or not (partes[0].isdigit() and partes[1].isdigit()):
            return False
        hora, minutos = int(partes[0]), int(partes[1])
        return Cita.HORA_INICIO <= hora < Cita.HORA_FIN and minutos in (0, 30)

    @property
    def paciente_id(self):
        return self.__paciente_id

    @property
    def medico_id(self):
        return self.__medico_id

    @property
    def fecha(self):
        return self.__fecha

    @fecha.setter
    def fecha(self, valor):
        valor = Cita.limpiar(valor)
        try:
            date.fromisoformat(valor)
        except ValueError:
            raise ValueError("La fecha debe tener el formato AAAA-MM-DD")
        self.__fecha = valor

    @property
    def hora(self):
        return self.__hora

    @hora.setter
    def hora(self, valor):
        if not Cita.es_hora_valida(valor):
            raise ValueError(f"Hora inválida: use HH:00 o HH:30 entre "
                             f"{Cita.HORA_INICIO:02d}:00 y {Cita.HORA_FIN - 1:02d}:30")
        horas, minutos = str(valor).strip().split(":")
        self.__hora = f"{int(horas):02d}:{int(minutos):02d}"

    @property
    def motivo(self):
        return self.__motivo

    @motivo.setter
    def motivo(self, valor):
        self.__motivo = Cita.limpiar(valor).capitalize()

    @property
    def estado(self):
        return self.__estado

    def atender(self):
        if self.__estado != "Pendiente":
            raise ValueError(f"No se puede atender una cita {self.__estado.lower()}")
        self.__estado = "Atendida"

    def cancelar(self):
        if self.__estado != "Pendiente":
            raise ValueError(f"No se puede cancelar una cita {self.__estado.lower()}")
        self.__estado = "Cancelada"

    def a_diccionario(self):
        return {"id": self.id, "paciente_id": self.__paciente_id,
                "medico_id": self.__medico_id, "fecha": self.__fecha,
                "hora": self.__hora, "motivo": self.__motivo, "estado": self.__estado}

    @classmethod
    def desde_diccionario(cls, datos):
        return cls(datos["id"], datos["paciente_id"], datos["medico_id"],
                   datos["fecha"], datos["hora"], datos.get("motivo", ""),
                   datos.get("estado", "Pendiente"))

    def etiqueta(self):
        return (f"{self.__fecha} {self.__hora} · paciente {self.__paciente_id} · "
                f"médico {self.__medico_id} · {self.__estado}")
