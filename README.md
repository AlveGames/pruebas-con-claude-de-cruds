# Pruebas de CRUDs

Proyectos de práctica con la misma arquitectura de la Guía 2 (MVC + POO + JSON).

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
