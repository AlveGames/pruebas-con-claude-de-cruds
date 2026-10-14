# Pruebas de CRUDs

Proyectos de práctica con la misma arquitectura de la Guía 2 (MVC + POO + JSON).
Cada carpeta es independiente: se puede copiar sola y ejecutar su `main.py`.

| Carpeta | Entidades | Lo que la hace distinta |
|---|---|---|
| `Biblioteca` | Socio, Libro, Préstamo | stock de ejemplares, máx. 3 préstamos, devolver |
| `Inventario` | Proveedor, Producto, Movimiento | entradas/salidas de stock, kardex, stock bajo |
| `Citas` | Paciente, Médico, Cita | fecha y hora validadas, sin choques de horario, atender/cancelar |
| `Parqueadero` | Vehículo, Ticket | placa con formato, capacidad por tipo, cobro por horas |

Todas tienen la misma forma: **1 o 2 entidades simples** + **1 entidad que depende de las otras** + **reportes**.

## Biblioteca

```
Biblioteca/
├── models.py   ← MODELO: ModeloBase, Persona, Socio, Libro, Prestamo
├── views.py    ← CONTROLADOR: CrudBase + SocioController, LibroController, PrestamoController
├── main.py     ← VISTA: menú
├── shared/     ← herramientas y GestorJSON
└── data/       ← se crea solo al guardar
```

Ejecutar: abrir `Biblioteca/main.py` y darle play.

### A qué se parece cada controlador

| Biblioteca | Se copió de | Regla única | Lo especial |
|---|---|---|---|
| `SocioController` | `EstudianteController` | cédula y email | — |
| `LibroController` | `ProductoController` | ISBN | maneja ejemplares disponibles |
| `PrestamoController` | `MatriculaController` / `VentaController` | — | recibe socios y libros, revisa que existan, máx. 3 activos por socio, devolver, historial |

### Dónde está cada regla

- **Modelo** (un solo dato): cédula de 10 números, ISBN mínimo 4 caracteres, año válido, disponibles ≥ 0, no prestar si no quedan ejemplares, no devolver dos veces.
- **Controlador** (mira a todos): cédula/email/ISBN repetidos, socio y libro existen, máximo 3 préstamos activos, no prestar dos veces el mismo libro al mismo socio.

### Receta para un CRUD nuevo

1. Copiar un controlador que se parezca.
2. `Ctrl + H` con **Coincidir mayúsculas** (`Alt + C`) y **Buscar en selección** (`Alt + L`): primero `socio` → `nuevo`, luego `Socio` → `Nuevo`.
3. Cambiar a mano: archivo `.json`, regla única, campos de `buscar`, parámetros de `crear` y `actualizar`.
4. Revisar: clase con Mayúscula, variable con minúscula, paréntesis cerrados, **ninguna coma al final**.

## Inventario

| Controlador | Se parece a | Regla única | Lo especial |
|---|---|---|---|
| `ProveedorController` | `EstudianteController` | RUC (13 números) | — |
| `ProductoController` | `MateriaController` | código | recibe proveedores y revisa que el proveedor exista |
| `MovimientoController` | `VentaController` | — | cada entrada/salida cambia el stock; no se editan ni eliminan; kardex |

## Citas

| Controlador | Se parece a | Regla única | Lo especial |
|---|---|---|---|
| `PacienteController` | `SocioController` | cédula y email | — |
| `MedicoController` | `DocenteController` | email | — |
| `CitaController` | `MatriculaController` | — | el médico y el paciente no pueden tener dos citas a la misma hora; atender, cancelar, agenda |

En el modelo: la fecha debe ser `AAAA-MM-DD` y la hora `HH:00` o `HH:30` entre 08:00 y 16:30.

## Parqueadero

| Controlador | Se parece a | Regla única | Lo especial |
|---|---|---|---|
| `VehiculoController` | `LibroController` | placa (`ABC-1234`) | tipo: auto o moto |
| `TicketController` | `PrestamoController` | — | capacidad por tipo, no entrar dos veces, salida cobra $1/h auto y $0.50/h moto (fracción = hora completa) |
