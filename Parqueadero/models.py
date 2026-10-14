# models.py es el MODELO: define qué es cada cosa y sus reglas propias.
# Cada objeto se valida solo con sus setters. No imprime ni guarda nada.
from abc import ABC, abstractmethod
import math
from datetime import datetime


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


FORMATO = "%Y-%m-%d %H:%M"     # ej: 2026-10-14 08:30


# =====================================================================
# VEHÍCULO
# =====================================================================
class Vehiculo(ModeloBase):

    CAMPOS = ("placa", "tipo", "propietario")
    OBLIGATORIOS = ("placa", "tipo")
    TIPOS = ("auto", "moto")

    def __init__(self, id_registro, placa, tipo, propietario=""):
        super().__init__(id_registro)
        self.placa = placa
        self.tipo = tipo
        self.propietario = propietario

    @staticmethod
    def es_placa_valida(texto):
        """Formato ecuatoriano: 3 letras, guion, 3 o 4 números. Ej: GBA-1234"""
        texto = str(texto).strip().upper()
        partes = texto.split("-")
        if len(partes) != 2:
            return False
        letras, numeros = partes
        return (len(letras) == 3 and letras.isalpha()
                and numeros.isdigit() and len(numeros) in (3, 4))

    @property
    def placa(self):
        return self.__placa

    @placa.setter
    def placa(self, valor):
        if not Vehiculo.es_placa_valida(valor):
            raise ValueError("Placa inválida. Use el formato ABC-1234")
        self.__placa = Vehiculo.limpiar(valor).upper()

    @property
    def tipo(self):
        return self.__tipo

    @tipo.setter
    def tipo(self, valor):
        valor = Vehiculo.limpiar(valor).lower()
        if valor not in Vehiculo.TIPOS:
            raise ValueError(f"Tipo inválido. Use: {', '.join(Vehiculo.TIPOS)}")
        self.__tipo = valor

    @property
    def propietario(self):
        return self.__propietario

    @propietario.setter
    def propietario(self, valor):
        self.__propietario = Vehiculo.limpiar(valor).title()

    def a_diccionario(self):
        return {"id": self.id, "placa": self.__placa,
                "tipo": self.__tipo, "propietario": self.__propietario}

    def etiqueta(self):
        dueno = f" · {self.__propietario}" if self.__propietario else ""
        return f"{self.__placa} · {self.__tipo}{dueno}"


# =====================================================================
# TICKET: registra la entrada y la salida de un vehículo y cobra
# =====================================================================
class Ticket(ModeloBase):

    CAMPOS = ("vehiculo_id",)
    OBLIGATORIOS = ("vehiculo_id",)
    TARIFAS = {"auto": 1.00, "moto": 0.50}     # dólares por hora o fracción

    def __init__(self, id_registro, vehiculo_id, entrada=None, salida="", total=0):
        super().__init__(id_registro)
        self.__vehiculo_id = int(vehiculo_id)
        self.__entrada = entrada or datetime.now().strftime(FORMATO)
        self.__salida = salida or ""
        self.__total = float(total or 0)

    @staticmethod
    def calcular_horas(entrada, salida):
        """Horas cobradas: toda fracción cuenta como hora completa, mínimo 1."""
        inicio = datetime.strptime(entrada, FORMATO)
        fin = datetime.strptime(salida, FORMATO)
        if fin < inicio:
            raise ValueError("La salida no puede ser antes que la entrada")
        minutos = (fin - inicio).total_seconds() / 60
        return max(1, math.ceil(minutos / 60))

    @property
    def vehiculo_id(self):
        return self.__vehiculo_id

    @property
    def entrada(self):
        return self.__entrada

    @property
    def salida(self):
        return self.__salida

    @property
    def total(self):
        return self.__total

    @property
    def estado(self):
        return "Cerrado" if self.__salida else "Abierto"

    def cerrar(self, tipo_vehiculo, salida=None):
        if self.estado == "Cerrado":
            raise ValueError("Ese ticket ya fue cerrado")
        salida = salida or datetime.now().strftime(FORMATO)
        try:
            horas = Ticket.calcular_horas(self.__entrada, salida)
        except ValueError as error:
            if "does not match" in str(error):
                raise ValueError("La fecha debe tener el formato AAAA-MM-DD HH:MM")
            raise
        self.__salida = salida
        self.__total = round(horas * Ticket.TARIFAS[tipo_vehiculo], 2)
        return horas

    def a_diccionario(self):
        return {"id": self.id, "vehiculo_id": self.__vehiculo_id,
                "entrada": self.__entrada, "salida": self.__salida,
                "total": self.__total}

    @classmethod
    def desde_diccionario(cls, datos):
        return cls(datos["id"], datos["vehiculo_id"], datos.get("entrada"),
                   datos.get("salida", ""), datos.get("total", 0))

    def etiqueta(self):
        if self.estado == "Abierto":
            return f"Vehículo {self.__vehiculo_id} · entró {self.__entrada} · ADENTRO"
        return (f"Vehículo {self.__vehiculo_id} · {self.__entrada} → "
                f"{self.__salida} · ${self.__total:.2f}")
