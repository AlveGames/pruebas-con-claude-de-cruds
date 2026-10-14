# views.py es el CONTROLADOR: decide y guarda. Nunca usa print() ni input().
# Todo devuelve (True/False, "mensaje"), listas u objetos; la Vista los muestra.
import os
from abc import ABC, abstractmethod

from models import Proveedor, Producto, Movimiento
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
# PROVEEDORES  (molde: EstudianteController)  · regla única: RUC
# =====================================================================
class ProveedorController(CrudBase):

    def __init__(self, archivo=os.path.join(BASE, "data", "proveedores.json")):
        self.nombre = "proveedor"
        self.campos = Proveedor.CAMPOS
        self.gestor = GestorJSON(archivo)

        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Proveedor.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for proveedor in self.lista:
            datos.append(proveedor.a_diccionario())
        self.gestor.guardar(datos)

    def obtener(self, id_proveedor):
        for proveedor in self.lista:
            if proveedor.id == id_proveedor:
                return proveedor
        return None

    def leer(self):
        return self.lista

    def buscar(self, texto):
        texto = texto.strip().lower()
        encontrados = []
        if texto == "":
            return encontrados

        for proveedor in self.lista:
            if texto in proveedor.nombre.lower() or texto in proveedor.ruc:
                encontrados.append(proveedor)
        return encontrados

    def siguiente(self):
        mayor = 0
        for proveedor in self.lista:
            if proveedor.id > mayor:
                mayor = proveedor.id
        return mayor + 1

    def crear(self, datos):
        ruc = str(datos.get("ruc", "")).strip()
        for proveedor in self.lista:
            if proveedor.ruc == ruc:
                return False, f"El RUC {ruc} ya está registrado"

        try:
            proveedor = Proveedor(self.siguiente(),
                                  datos.get("nombre", ""),
                                  datos.get("ruc", ""),
                                  datos.get("telefono", ""))
        except ValueError as error:
            return False, str(error)

        self.lista.append(proveedor)
        self.guardar()
        return True, f"Proveedor creado: {proveedor.etiqueta()}"

    def actualizar(self, id_proveedor, datos):
        if not datos:
            return False, "No se indicó ningún cambio"

        proveedor = self.obtener(id_proveedor)
        if proveedor is None:
            return False, f"No existe proveedor con id {id_proveedor}"

        if "ruc" in datos:
            ruc = str(datos["ruc"]).strip()
            for otro in self.lista:
                if otro.ruc == ruc and otro.id != id_proveedor:
                    return False, f"El RUC {ruc} ya está registrado"

        try:
            nuevo = Proveedor(proveedor.id,
                              datos.get("nombre", proveedor.nombre),
                              datos.get("ruc", proveedor.ruc),
                              datos.get("telefono", proveedor.telefono))
        except ValueError as error:
            return False, str(error)

        posicion = self.lista.index(proveedor)
        self.lista[posicion] = nuevo
        self.guardar()
        return True, f"Proveedor {id_proveedor} actualizado"

    def eliminar(self, id_proveedor):
        proveedor = self.obtener(id_proveedor)
        if proveedor is None:
            return False, f"No existe proveedor con id {id_proveedor}"

        self.lista.remove(proveedor)
        self.guardar()
        return True, f"Proveedor {id_proveedor} eliminado"


# =====================================================================
# PRODUCTOS  (molde: MateriaController)  · regla única: código
# Depende de proveedores (como la materia depende del docente)
# =====================================================================
class ProductoController(CrudBase):

    def __init__(self, proveedores, archivo=os.path.join(BASE, "data", "productos.json")):
        self.nombre = "producto"
        self.campos = Producto.CAMPOS
        self.gestor = GestorJSON(archivo)
        self.proveedores = proveedores

        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Producto.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for producto in self.lista:
            datos.append(producto.a_diccionario())
        self.gestor.guardar(datos)

    def obtener(self, id_producto):
        for producto in self.lista:
            if producto.id == id_producto:
                return producto
        return None

    def leer(self):
        return self.lista

    def buscar(self, texto):
        texto = texto.strip().lower()
        encontrados = []
        if texto == "":
            return encontrados

        for producto in self.lista:
            if texto in producto.nombre.lower() or texto in producto.codigo.lower():
                encontrados.append(producto)
        return encontrados

    def siguiente(self):
        mayor = 0
        for producto in self.lista:
            if producto.id > mayor:
                mayor = producto.id
        return mayor + 1

    def proveedor_existe(self, proveedor_id):
        """Vacío está bien (sin proveedor). Si viene, debe existir."""
        if str(proveedor_id).strip() in ("", "0", "None"):
            return True
        try:
            return self.proveedores.obtener(int(proveedor_id)) is not None
        except ValueError:
            return False

    def crear(self, datos):
        codigo = str(datos.get("codigo", "")).strip().upper()
        for producto in self.lista:
            if producto.codigo == codigo:
                return False, f"El código {codigo} ya está registrado"

        if not self.proveedor_existe(datos.get("proveedor_id", "")):
            return False, f"No existe un proveedor con id {datos.get('proveedor_id')}"

        try:
            producto = Producto(self.siguiente(),
                                datos.get("nombre", ""),
                                datos.get("codigo", ""),
                                datos.get("precio", ""),
                                datos.get("stock", 0),
                                datos.get("proveedor_id", ""))
        except ValueError as error:
            return False, str(error)

        self.lista.append(producto)
        self.guardar()
        return True, f"Producto creado: {producto.etiqueta()}"

    def actualizar(self, id_producto, datos):
        if not datos:
            return False, "No se indicó ningún cambio"

        producto = self.obtener(id_producto)
        if producto is None:
            return False, f"No existe producto con id {id_producto}"

        if "codigo" in datos:
            codigo = str(datos["codigo"]).strip().upper()
            for otro in self.lista:
                if otro.codigo == codigo and otro.id != id_producto:
                    return False, f"El código {codigo} ya está registrado"

        if "proveedor_id" in datos and not self.proveedor_existe(datos["proveedor_id"]):
            return False, f"No existe un proveedor con id {datos['proveedor_id']}"

        try:
            nuevo = Producto(producto.id,
                             datos.get("nombre", producto.nombre),
                             datos.get("codigo", producto.codigo),
                             datos.get("precio", producto.precio),
                             datos.get("stock", producto.stock),
                             datos.get("proveedor_id", producto.proveedor_id))
        except ValueError as error:
            return False, str(error)

        posicion = self.lista.index(producto)
        self.lista[posicion] = nuevo
        self.guardar()
        return True, f"Producto {id_producto} actualizado"

    def eliminar(self, id_producto):
        producto = self.obtener(id_producto)
        if producto is None:
            return False, f"No existe producto con id {id_producto}"

        self.lista.remove(producto)
        self.guardar()
        return True, f"Producto {id_producto} eliminado"

    # --- reportes propios ---
    def con_stock_bajo(self):
        resultado = []
        for producto in self.lista:
            if producto.stock_bajo:
                resultado.append(producto)
        return resultado

    def valor_inventario(self):
        total = 0
        for producto in self.lista:
            total += producto.valor_total
        return round(total, 2)


# =====================================================================
# MOVIMIENTOS  (molde: VentaController)
# Cada entrada o salida cambia el stock del producto
# =====================================================================
class MovimientoController(CrudBase):

    def __init__(self, productos, archivo=os.path.join(BASE, "data", "movimientos.json")):
        self.nombre = "movimiento"
        self.campos = Movimiento.CAMPOS
        self.gestor = GestorJSON(archivo)
        self.productos = productos

        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Movimiento.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for movimiento in self.lista:
            datos.append(movimiento.a_diccionario())
        self.gestor.guardar(datos)

    def obtener(self, id_movimiento):
        for movimiento in self.lista:
            if movimiento.id == id_movimiento:
                return movimiento
        return None

    def leer(self):
        return self.lista

    def buscar(self, texto):
        # Se busca por tipo ("entrada" / "salida") o por fecha
        texto = texto.strip().lower()
        encontrados = []
        if texto == "":
            return encontrados

        for movimiento in self.lista:
            if texto in movimiento.tipo or texto in movimiento.fecha:
                encontrados.append(movimiento)
        return encontrados

    def siguiente(self):
        mayor = 0
        for movimiento in self.lista:
            if movimiento.id > mayor:
                mayor = movimiento.id
        return mayor + 1

    def crear(self, datos):
        try:
            producto_id = int(datos.get("producto_id", 0))
        except (TypeError, ValueError):
            return False, "El id del producto debe ser un número"

        producto = self.productos.obtener(producto_id)
        if producto is None:
            return False, f"No existe un producto con id {producto_id}"

        try:
            movimiento = Movimiento(self.siguiente(), producto_id,
                                    datos.get("tipo", ""),
                                    datos.get("cantidad", ""))
            # El PRODUCTO revisa si alcanza el stock
            if movimiento.tipo == "entrada":
                producto.entrada(movimiento.cantidad)
            else:
                producto.salida(movimiento.cantidad)
        except ValueError as error:
            return False, str(error)

        self.lista.append(movimiento)
        self.guardar()
        self.productos.guardar()      # el producto cambió su stock
        return True, f"Movimiento registrado. Stock de {producto.nombre}: {producto.stock}"

    def actualizar(self, id_movimiento, datos):
        return False, "Los movimientos no se editan; registre uno nuevo que lo corrija"

    def eliminar(self, id_movimiento):
        return False, "Los movimientos no se eliminan; son el historial del inventario"

    # --- reporte propio ---
    def kardex(self, producto_id):
        """Texto con todos los movimientos de un producto (como la factura)."""
        producto = self.productos.obtener(producto_id)
        if producto is None:
            return None

        texto = f"KARDEX DE {producto.nombre.upper()} ({producto.codigo})\n"
        texto += "-" * 45 + "\n"
        entradas = 0
        salidas = 0
        for movimiento in self.lista:
            if movimiento.producto_id == producto_id:
                texto += f"  {movimiento.fecha}  {movimiento.tipo:<8} {movimiento.cantidad:>5}\n"
                if movimiento.tipo == "entrada":
                    entradas += movimiento.cantidad
                else:
                    salidas += movimiento.cantidad
        texto += "-" * 45 + "\n"
        texto += f"  Entradas: {entradas}  Salidas: {salidas}  Stock actual: {producto.stock}"
        return texto
