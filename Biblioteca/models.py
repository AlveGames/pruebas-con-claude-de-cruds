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


class Socio(Persona):
    """Persona que pide libros prestados. Se identifica con su cédula."""

    CAMPOS = Persona.CAMPOS + ("cedula",)
    OBLIGATORIOS = Persona.OBLIGATORIOS + ("cedula",)

    def __init__(self, id_registro, nombre, apellido, email, cedula):
        super().__init__(id_registro, nombre, apellido, email)
        self.cedula = cedula

    @property
    def cedula(self):
        return self.__cedula

    @cedula.setter
    def cedula(self, valor):
        valor = Socio.limpiar(valor)
        if not (valor.isdigit() and len(valor) == 10):
            raise ValueError("La cédula debe tener 10 números")
        self.__cedula = valor

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos["cedula"] = self.__cedula
        return datos

    def etiqueta(self):
        return f"{self.nombre_completo} · cédula {self.__cedula}"


# =====================================================================
# Libro: hereda directo de ModeloBase (no es una persona)
# =====================================================================
class Libro(ModeloBase):

    CAMPOS = ("titulo", "autor", "isbn", "anio", "disponibles")
    OBLIGATORIOS = ("titulo", "autor", "isbn")

    def __init__(self, id_registro, titulo, autor, isbn, anio=2000, disponibles=1):
        super().__init__(id_registro)
        self.titulo = titulo
        self.autor = autor
        self.isbn = isbn
        self.anio = anio
        self.disponibles = disponibles

    @property
    def titulo(self):
        return self.__titulo

    @titulo.setter
    def titulo(self, valor):
        valor = Libro.limpiar(valor)
        if not valor:
            raise ValueError("El título es obligatorio")
        self.__titulo = valor.title()

    @property
    def autor(self):
        return self.__autor

    @autor.setter
    def autor(self, valor):
        valor = Libro.limpiar(valor)
        if not valor:
            raise ValueError("El autor es obligatorio")
        self.__autor = valor.title()

    @property
    def isbn(self):
        return self.__isbn

    @isbn.setter
    def isbn(self, valor):
        valor = Libro.limpiar(valor).upper()
        if len(valor) < 4:
            raise ValueError("El ISBN debe tener al menos 4 caracteres")
        self.__isbn = valor

    @property
    def anio(self):
        return self.__anio

    @anio.setter
    def anio(self, valor):
        try:
            valor = int(valor)
        except (TypeError, ValueError):
            raise ValueError("El año debe ser un número")
        if not 1000 <= valor <= date.today().year:
            raise ValueError(f"El año debe estar entre 1000 y {date.today().year}")
        self.__anio = valor

    @property
    def disponibles(self):
        return self.__disponibles

    @disponibles.setter
    def disponibles(self, valor):
        try:
            valor = int(valor)
        except (TypeError, ValueError):
            raise ValueError("Los ejemplares disponibles deben ser un número")
        if valor < 0:
            raise ValueError("Los ejemplares disponibles no pueden ser negativos")
        self.__disponibles = valor

    # --- reglas propias del libro (como descontar_stock de Producto) ---
    def prestar(self):
        if self.__disponibles == 0:
            raise ValueError(f"No quedan ejemplares de '{self.__titulo}'")
        self.__disponibles -= 1

    def devolver(self):
        self.__disponibles += 1

    def a_diccionario(self):
        return {
            "id": self.id,
            "titulo": self.__titulo,
            "autor": self.__autor,
            "isbn": self.__isbn,
            "anio": self.__anio,
            "disponibles": self.__disponibles,
        }

    def etiqueta(self):
        return (f"{self.__titulo} · {self.__autor} ({self.__anio}) · "
                f"ISBN {self.__isbn} · {self.__disponibles} disponible(s)")


# =====================================================================
# Préstamo: une a un Socio con un Libro (guarda solo los ids)
# =====================================================================
class Prestamo(ModeloBase):

    CAMPOS = ("socio_id", "libro_id")
    OBLIGATORIOS = ("socio_id", "libro_id")
    MAX_ACTIVOS = 3      # un socio no puede tener más de 3 libros a la vez

    def __init__(self, id_registro, socio_id, libro_id,
                 fecha_prestamo=None, fecha_devolucion=""):
        super().__init__(id_registro)
        self.__socio_id = int(socio_id)
        self.__libro_id = int(libro_id)
        self.__fecha_prestamo = fecha_prestamo or date.today().isoformat()
        self.__fecha_devolucion = fecha_devolucion or ""

    @property
    def socio_id(self):
        return self.__socio_id

    @property
    def libro_id(self):
        return self.__libro_id

    @property
    def fecha_prestamo(self):
        return self.__fecha_prestamo

    @property
    def fecha_devolucion(self):
        return self.__fecha_devolucion

    @property
    def estado(self):
        # CALCULADA: no se guarda, se deduce de la fecha de devolución
        return "Devuelto" if self.__fecha_devolucion else "Activo"

    def devolver(self):
        if self.estado == "Devuelto":
            raise ValueError("Ese préstamo ya fue devuelto")
        self.__fecha_devolucion = date.today().isoformat()

    def a_diccionario(self):
        return {
            "id": self.id,
            "socio_id": self.__socio_id,
            "libro_id": self.__libro_id,
            "fecha_prestamo": self.__fecha_prestamo,
            "fecha_devolucion": self.__fecha_devolucion,
        }

    @classmethod
    def desde_diccionario(cls, datos):
        # Se sobrescribe porque las fechas no están en CAMPOS
        return cls(datos["id"], datos["socio_id"], datos["libro_id"],
                   datos.get("fecha_prestamo"), datos.get("fecha_devolucion", ""))

    def etiqueta(self):
        return (f"Socio {self.__socio_id} · libro {self.__libro_id} · "
                f"desde {self.__fecha_prestamo} · {self.estado}")
