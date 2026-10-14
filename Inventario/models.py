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
# PROVEEDOR
# =====================================================================
class Proveedor(ModeloBase):

    CAMPOS = ("nombre", "ruc", "telefono")
    OBLIGATORIOS = ("nombre", "ruc")

    def __init__(self, id_registro, nombre, ruc, telefono=""):
        super().__init__(id_registro)
        self.nombre = nombre
        self.ruc = ruc
        self.telefono = telefono

    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        valor = Proveedor.limpiar(valor)
        if not valor:
            raise ValueError("El nombre es obligatorio")
        self.__nombre = valor.title()

    @property
    def ruc(self):
        return self.__ruc

    @ruc.setter
    def ruc(self, valor):
        valor = Proveedor.limpiar(valor)
        if not (valor.isdigit() and len(valor) == 13):
            raise ValueError("El RUC debe tener 13 números")
        self.__ruc = valor

    @property
    def telefono(self):
        return self.__telefono

    @telefono.setter
    def telefono(self, valor):
        valor = Proveedor.limpiar(valor)
        if valor and not valor.isdigit():
            raise ValueError("El teléfono solo puede tener números")
        self.__telefono = valor

    def a_diccionario(self):
        return {"id": self.id, "nombre": self.__nombre,
                "ruc": self.__ruc, "telefono": self.__telefono}

    def etiqueta(self):
        return f"{self.__nombre} · RUC {self.__ruc}"


# =====================================================================
# PRODUCTO: guarda solo el id del proveedor (agregación)
# =====================================================================
class Producto(ModeloBase):

    CAMPOS = ("nombre", "codigo", "precio", "stock", "proveedor_id")
    OBLIGATORIOS = ("nombre", "codigo", "precio")
    STOCK_MINIMO = 5

    def __init__(self, id_registro, nombre, codigo, precio, stock=0, proveedor_id=None):
        super().__init__(id_registro)
        self.nombre = nombre
        self.codigo = codigo
        self.precio = precio
        self.stock = stock
        self.proveedor_id = proveedor_id

    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        valor = Producto.limpiar(valor)
        if not valor:
            raise ValueError("El nombre es obligatorio")
        self.__nombre = valor.title()

    @property
    def codigo(self):
        return self.__codigo

    @codigo.setter
    def codigo(self, valor):
        valor = Producto.limpiar(valor).upper()
        if len(valor) < 3:
            raise ValueError("El código debe tener al menos 3 caracteres")
        self.__codigo = valor

    @property
    def precio(self):
        return self.__precio

    @precio.setter
    def precio(self, valor):
        try:
            valor = round(float(valor), 2)
        except (TypeError, ValueError):
            raise ValueError("El precio debe ser un número")
        if valor <= 0:
            raise ValueError("El precio debe ser mayor a 0")
        self.__precio = valor

    @property
    def stock(self):
        return self.__stock

    @stock.setter
    def stock(self, valor):
        try:
            valor = int(valor or 0)
        except (TypeError, ValueError):
            raise ValueError("El stock debe ser un número entero")
        if valor < 0:
            raise ValueError("El stock no puede ser negativo")
        self.__stock = valor

    @property
    def proveedor_id(self):
        return self.__proveedor_id

    @proveedor_id.setter
    def proveedor_id(self, valor):
        valor = Producto.limpiar(valor)
        self.__proveedor_id = int(valor) if valor.isdigit() and int(valor) > 0 else None

    @property
    def stock_bajo(self):
        return self.__stock < Producto.STOCK_MINIMO

    @property
    def valor_total(self):
        return round(self.__precio * self.__stock, 2)

    # --- reglas propias ---
    def entrada(self, cantidad):
        self.__stock += cantidad

    def salida(self, cantidad):
        if cantidad > self.__stock:
            raise ValueError(f"Stock insuficiente de {self.__nombre}: quedan {self.__stock}")
        self.__stock -= cantidad

    def a_diccionario(self):
        return {"id": self.id, "nombre": self.__nombre, "codigo": self.__codigo,
                "precio": self.__precio, "stock": self.__stock,
                "proveedor_id": self.__proveedor_id}

    def etiqueta(self):
        aviso = " ⚠ stock bajo" if self.stock_bajo else ""
        return f"{self.__codigo} · {self.__nombre} · ${self.__precio:.2f} · stock {self.__stock}{aviso}"


# =====================================================================
# MOVIMIENTO: una entrada o salida de stock (como una venta pequeña)
# =====================================================================
class Movimiento(ModeloBase):

    CAMPOS = ("producto_id", "tipo", "cantidad")
    OBLIGATORIOS = ("producto_id", "tipo", "cantidad")
    TIPOS = ("entrada", "salida")

    def __init__(self, id_registro, producto_id, tipo, cantidad, fecha=None):
        super().__init__(id_registro)
        self.__producto_id = int(producto_id)
        self.tipo = tipo
        self.cantidad = cantidad
        self.__fecha = fecha or date.today().isoformat()

    @staticmethod
    def es_tipo_valido(tipo):
        return str(tipo).strip().lower() in Movimiento.TIPOS

    @property
    def producto_id(self):
        return self.__producto_id

    @property
    def tipo(self):
        return self.__tipo

    @tipo.setter
    def tipo(self, valor):
        if not Movimiento.es_tipo_valido(valor):
            raise ValueError(f"Tipo inválido. Use: {', '.join(Movimiento.TIPOS)}")
        self.__tipo = Movimiento.limpiar(valor).lower()

    @property
    def cantidad(self):
        return self.__cantidad

    @cantidad.setter
    def cantidad(self, valor):
        try:
            valor = int(valor)
        except (TypeError, ValueError):
            raise ValueError("La cantidad debe ser un número entero")
        if valor <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")
        self.__cantidad = valor

    @property
    def fecha(self):
        return self.__fecha

    def a_diccionario(self):
        return {"id": self.id, "producto_id": self.__producto_id, "tipo": self.__tipo,
                "cantidad": self.__cantidad, "fecha": self.__fecha}

    @classmethod
    def desde_diccionario(cls, datos):
        return cls(datos["id"], datos["producto_id"], datos["tipo"],
                   datos["cantidad"], datos.get("fecha"))

    def etiqueta(self):
        signo = "+" if self.__tipo == "entrada" else "-"
        return f"{self.__fecha} · producto {self.__producto_id} · {self.__tipo} {signo}{self.__cantidad}"
