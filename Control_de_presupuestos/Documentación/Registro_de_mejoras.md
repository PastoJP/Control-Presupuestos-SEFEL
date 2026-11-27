# Registro de mejoras

## Mejora 01 - Identidad visual corporativa

- Fecha: 26/11/2026
- Versión base: 2.0
- Tipo: Mejora estética.

### Cambios realizados
- Incorporación de los colores corporativos de SEFEL.
- Actualización del encabezado y botones principales.
- Corrección del color de selección del menú lateral.

### Justificación
Adaptar la interfaz a la identidad visual de la empresa.

### Resultado
Cambio visual completado.

### Pruebas
Se realizaron ocho comprobaciones de regresión,
verificando el inicio de sesión, la navegación,
los permisos de usuario y el cierre de sesión.

Resultado: 8 de 8 comprobaciones satisfactorias.

Estado: Completado.

---

## Mejora N.º 02 - Implementación del maestro de recursos

- Fecha: 27/11/2026
- Versión base: 2.0
- Requerimiento relacionado: HU-01 / RF-01
- Estado: Completado

### Objetivo

Incorporar un catálogo centralizado de recursos para
la elaboración de APU y presupuestos.

### Cambios realizados

- Respaldo preventivo de la base de datos.
- Creación de la tabla recursos en SQLite.
- Desarrollo de funciones de registro y consulta.
- Edición, activación y desactivación de recursos.
- Implementación de un buscador.
- Creación de la interfaz gráfica del maestro de recursos.
- Validación de los datos ingresados.
- Restricción de operaciones según el rol del usuario.
- Integración con todos los menús de navegación.

### Archivos modificados

- database.py
- sefel.db
- main_view.py
- budget_view.py
- expenses_view.py
- compare_view.py

### Archivos creados

- resources_view.py

### Resultado obtenido

El maestro de recursos funciona correctamente en
las pruebas realizadas. Se mantienen los permisos
de los usuarios y las funcionalidades anteriores.

No se reportaron defectos durante las pruebas.

### Evidencias

Las capturas de pantalla se encuentran documentadas
en la Evidencia N.º 02 del Registro de evidencias.

