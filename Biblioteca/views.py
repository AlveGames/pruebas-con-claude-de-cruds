# views.py es el CONTROLADOR: decide y guarda. Nunca usa print() ni input().
# Todo devuelve (True/False, "mensaje"), listas u objetos; la Vista los muestra.
import os
from abc import ABC, abstractmethod

from models import Socio, Libro, Prestamo
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
# SOCIOS  (molde: EstudianteController)
# Regla única: cédula y email
# =====================================================================
class SocioController(CrudBase):

    def __init__(self, archivo=os.path.join(BASE, "data", "socios.json")):
        self.nombre = "socio"
        self.campos = Socio.CAMPOS
        self.gestor = GestorJSON(archivo)

        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Socio.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for socio in self.lista:
            datos.append(socio.a_diccionario())
        self.gestor.guardar(datos)

    def obtener(self, id_socio):
        for socio in self.lista:
            if socio.id == id_socio:
                return socio
        return None

    def leer(self):
        return self.lista

    def buscar(self, texto):
        texto = texto.strip().lower()
        encontrados = []
        if texto == "":
            return encontrados

        for socio in self.lista:
            if (texto in socio.nombre.lower()
                    or texto in socio.apellido.lower()
                    or texto in socio.email
                    or texto in socio.cedula):
                encontrados.append(socio)
        return encontrados

    def siguiente(self):
        mayor = 0
        for socio in self.lista:
            if socio.id > mayor:
                mayor = socio.id
        return mayor + 1

    def repetido(self, cedula, email, id_actual=None):
        """Devuelve un mensaje si la cédula o el email ya los usa otro socio."""
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
            socio = Socio(self.siguiente(),
                          datos.get("nombre", ""),
                          datos.get("apellido", ""),
                          datos.get("email", ""),
                          datos.get("cedula", ""))
        except ValueError as error:
            return False, str(error)

        self.lista.append(socio)
        self.guardar()
        return True, f"Socio creado: {socio.etiqueta()}"

    def actualizar(self, id_socio, datos):
        if not datos:
            return False, "No se indicó ningún cambio"

        socio = self.obtener(id_socio)
        if socio is None:
            return False, f"No existe socio con id {id_socio}"

        error = self.repetido(datos.get("cedula", socio.cedula),
                              datos.get("email", socio.email),
                              id_actual=id_socio)
        if error:
            return False, error

        try:
            nuevo = Socio(socio.id,
                          datos.get("nombre", socio.nombre),
                          datos.get("apellido", socio.apellido),
                          datos.get("email", socio.email),
                          datos.get("cedula", socio.cedula))
        except ValueError as error:
            return False, str(error)

        posicion = self.lista.index(socio)
        self.lista[posicion] = nuevo
        self.guardar()
        return True, f"Socio {id_socio} actualizado"

    def eliminar(self, id_socio):
        socio = self.obtener(id_socio)
        if socio is None:
            return False, f"No existe socio con id {id_socio}"

        self.lista.remove(socio)
        self.guardar()
        return True, f"Socio {id_socio} eliminado"


# =====================================================================
# LIBROS  (molde: ProductoController de ventas)
# Regla única: ISBN
# =====================================================================
class LibroController(CrudBase):

    def __init__(self, archivo=os.path.join(BASE, "data", "libros.json")):
        self.nombre = "libro"
        self.campos = Libro.CAMPOS
        self.gestor = GestorJSON(archivo)

        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Libro.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for libro in self.lista:
            datos.append(libro.a_diccionario())
        self.gestor.guardar(datos)

    def obtener(self, id_libro):
        for libro in self.lista:
            if libro.id == id_libro:
                return libro
        return None

    def leer(self):
        return self.lista

    def buscar(self, texto):
        texto = texto.strip().lower()
        encontrados = []
        if texto == "":
            return encontrados

        for libro in self.lista:
            if (texto in libro.titulo.lower()
                    or texto in libro.autor.lower()
                    or texto in libro.isbn.lower()):
                encontrados.append(libro)
        return encontrados

    def siguiente(self):
        mayor = 0
        for libro in self.lista:
            if libro.id > mayor:
                mayor = libro.id
        return mayor + 1

    def crear(self, datos):
        isbn = str(datos.get("isbn", "")).strip().upper()
        for libro in self.lista:
            if libro.isbn == isbn:
                return False, f"El ISBN {isbn} ya está registrado"

        try:
            libro = Libro(self.siguiente(),
                          datos.get("titulo", ""),
                          datos.get("autor", ""),
                          datos.get("isbn", ""),
                          datos.get("anio", "") or 2000,
                          datos.get("disponibles", "") or 1)
        except ValueError as error:
            return False, str(error)

        self.lista.append(libro)
        self.guardar()
        return True, f"Libro creado: {libro.etiqueta()}"

    def actualizar(self, id_libro, datos):
        if not datos:
            return False, "No se indicó ningún cambio"

        libro = self.obtener(id_libro)
        if libro is None:
            return False, f"No existe libro con id {id_libro}"

        if "isbn" in datos:
            isbn = str(datos["isbn"]).strip().upper()
            for otro in self.lista:
                if otro.isbn == isbn and otro.id != id_libro:
                    return False, f"El ISBN {isbn} ya está registrado"

        try:
            nuevo = Libro(libro.id,
                          datos.get("titulo", libro.titulo),
                          datos.get("autor", libro.autor),
                          datos.get("isbn", libro.isbn),
                          datos.get("anio", libro.anio),
                          datos.get("disponibles", libro.disponibles))
        except ValueError as error:
            return False, str(error)

        posicion = self.lista.index(libro)
        self.lista[posicion] = nuevo
        self.guardar()
        return True, f"Libro {id_libro} actualizado"

    def eliminar(self, id_libro):
        libro = self.obtener(id_libro)
        if libro is None:
            return False, f"No existe libro con id {id_libro}"

        self.lista.remove(libro)
        self.guardar()
        return True, f"Libro {id_libro} eliminado"


# =====================================================================
# PRÉSTAMOS  (molde: MatriculaController / VentaController)
# Depende de los otros dos controladores
# =====================================================================
class PrestamoController(CrudBase):

    def __init__(self, socios, libros,
                 archivo=os.path.join(BASE, "data", "prestamos.json")):
        self.nombre = "préstamo"
        self.campos = Prestamo.CAMPOS
        self.gestor = GestorJSON(archivo)

        # Usa los controladores de socios y libros para revisar que existan
        self.socios = socios
        self.libros = libros

        self.lista = []
        for datos in self.gestor.leer():
            self.lista.append(Prestamo.desde_diccionario(datos))

    def guardar(self):
        datos = []
        for prestamo in self.lista:
            datos.append(prestamo.a_diccionario())
        self.gestor.guardar(datos)

    def obtener(self, id_prestamo):
        for prestamo in self.lista:
            if prestamo.id == id_prestamo:
                return prestamo
        return None

    def leer(self):
        return self.lista

    def buscar(self, texto):
        # Se busca por estado ("activo" / "devuelto") o por fecha
        texto = texto.strip().lower()
        encontrados = []
        if texto == "":
            return encontrados

        for prestamo in self.lista:
            if (texto in prestamo.estado.lower()
                    or texto in prestamo.fecha_prestamo):
                encontrados.append(prestamo)
        return encontrados

    def siguiente(self):
        mayor = 0
        for prestamo in self.lista:
            if prestamo.id > mayor:
                mayor = prestamo.id
        return mayor + 1

    def activos_de(self, socio_id):
        resultado = []
        for prestamo in self.lista:
            if prestamo.socio_id == socio_id and prestamo.estado == "Activo":
                resultado.append(prestamo)
        return resultado

    def crear(self, datos):
        try:
            socio_id = int(datos.get("socio_id", 0))
            libro_id = int(datos.get("libro_id", 0))
        except (TypeError, ValueError):
            return False, "Los ids de socio y libro deben ser números"

        # 1. ¿Existen?
        socio = self.socios.obtener(socio_id)
        if socio is None:
            return False, f"No existe un socio con id {socio_id}"
        libro = self.libros.obtener(libro_id)
        if libro is None:
            return False, f"No existe un libro con id {libro_id}"

        # 2. Reglas que miran a TODOS los préstamos
        activos = self.activos_de(socio_id)
        if len(activos) >= Prestamo.MAX_ACTIVOS:
            return False, f"{socio.nombre_completo} ya tiene {Prestamo.MAX_ACTIVOS} libros prestados"
        for prestamo in activos:
            if prestamo.libro_id == libro_id:
                return False, "Ese socio ya tiene prestado ese libro"

        # 3. Regla del libro (la revisa el MODELO)
        try:
            libro.prestar()
        except ValueError as error:
            return False, str(error)

        prestamo = Prestamo(self.siguiente(), socio_id, libro_id)
        self.lista.append(prestamo)
        self.guardar()
        self.libros.guardar()      # el libro cambió sus disponibles
        return True, f"Préstamo {prestamo.id}: '{libro.titulo}' para {socio.nombre_completo}"

    def actualizar(self, id_prestamo, datos):
        # Igual que las ventas: un préstamo no se edita, se devuelve
        return False, "Los préstamos no se editan; use la opción Devolver"

    def eliminar(self, id_prestamo):
        prestamo = self.obtener(id_prestamo)
        if prestamo is None:
            return False, f"No existe préstamo con id {id_prestamo}"

        # Si estaba activo, el libro vuelve al estante
        if prestamo.estado == "Activo":
            libro = self.libros.obtener(prestamo.libro_id)
            if libro is not None:
                libro.devolver()
                self.libros.guardar()

        self.lista.remove(prestamo)
        self.guardar()
        return True, f"Préstamo {id_prestamo} eliminado"

    # --- métodos propios de préstamos ---
    def devolver(self, id_prestamo):
        prestamo = self.obtener(id_prestamo)
        if prestamo is None:
            return False, f"No existe préstamo con id {id_prestamo}"

        try:
            prestamo.devolver()
        except ValueError as error:
            return False, str(error)

        libro = self.libros.obtener(prestamo.libro_id)
        if libro is not None:
            libro.devolver()
            self.libros.guardar()

        self.guardar()
        return True, f"Préstamo {id_prestamo} devuelto"

    def historial(self, socio_id):
        """Texto con todos los préstamos de un socio (como el boletín)."""
        socio = self.socios.obtener(socio_id)
        if socio is None:
            return None

        texto = f"HISTORIAL DE {socio.nombre_completo.upper()}\n"
        texto += f"Cédula: {socio.cedula}\n"
        texto += "-" * 55 + "\n"

        prestamos = []
        for prestamo in self.lista:
            if prestamo.socio_id == socio_id:
                prestamos.append(prestamo)

        if len(prestamos) == 0:
            texto += "  No tiene préstamos\n"
        for prestamo in prestamos:
            libro = self.libros.obtener(prestamo.libro_id)
            titulo = libro.titulo if libro else "libro eliminado"
            texto += f"  {titulo:<28} {prestamo.fecha_prestamo}  {prestamo.estado}\n"

        texto += "-" * 55 + "\n"
        texto += f"  Activos: {len(self.activos_de(socio_id))} de {Prestamo.MAX_ACTIVOS}"
        return texto

    def mas_prestados(self):
        """DICCIONARIO título -> veces prestado, ordenado de mayor a menor."""
        conteo = {}
        for prestamo in self.lista:
            libro = self.libros.obtener(prestamo.libro_id)
            titulo = libro.titulo if libro else "libro eliminado"
            conteo[titulo] = conteo.get(titulo, 0) + 1
        return dict(sorted(conteo.items(), key=lambda par: par[1], reverse=True))
