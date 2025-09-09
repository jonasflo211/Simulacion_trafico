# Simulación de Semáforos Auto-Organizados

Este proyecto implementa una **simulación de tráfico con semáforos auto-organizados**, utilizando `tkinter` para la visualización gráfica.  
Los semáforos se controlan de forma adaptativa según la cantidad de autos que esperan en cada eje, implementando requisitos específicos de control inteligente.

---

## Descripción

- **Intersecciones simuladas**: 4
- **Semáforos por intersección**: 2 (horizontal y vertical)
- **Autos**: generados aleatoriamente en cada carril
- **Lógica de control**: Implementa 7 requisitos específicos de control adaptativo

---

## Requisitos Implementados

1. **Conteo de vehículos**: En cada tiempo, se cuentan los vehículos aproximándose o esperando en rojo a distancia `d`. Cuando el contador excede el umbral `n`, cambia el semáforo.
2. **Tiempo mínimo en verde**: Los semáforos permanecen en verde por un mínimo de `u` ticks.
3. **Protección de pocos vehículos**: Si `m` o menos vehículos van a cruzar un semáforo verde a corta distancia `r`, no se cambia.
4. **Cambio por demanda**: Si no hay vehículos en verde pero sí esperando en rojo, cambia el semáforo.
5. **Detección de congestión**: Si hay vehículos detenidos a corta distancia `e` más allá de un semáforo verde, cambia.
6. **Bloqueo mutuo**: Si hay vehículos detenidos en ambas direcciones a distancia `e`, ambos semáforos se ponen en rojo.
7. **Recuperación**: Cuando una dirección se libera, se restaura el verde en esa dirección.

---

## Parámetros de Configuración

- `d = 100`: Distancia para contar vehículos aproximándose
- `n = 3`: Umbral de vehículos para cambiar semáforo
- `u = 30`: Tiempo mínimo en verde (ticks)
- `m = 2`: Umbral de "pocos" vehículos
- `e = 30`: Distancia corta más allá del semáforo
- `r = 60`: Distancia corta para cruce de vehículos

---

## Lógica de Control de Semáforos

1. **Estado actual**: Cada semáforo puede estar en verde, amarillo o rojo
2. **Transición verde → amarillo**: 
   - Se cumple tiempo mínimo `u` y hay demanda en dirección opuesta
   - Se detectan vehículos detenidos más allá del semáforo
   - Se supera tiempo máximo de espera
3. **Transición amarillo → rojo**: Tiempo fijo de fase amarilla
4. **Transición rojo → verde**: Cuando se libera la intersección opuesta

---

## Características Técnicas

- **Detección de colisiones**: Prevención de choques entre vehículos
- **Gestión de intersecciones**: Control de ocupación para evitar bloqueos
- **Generación aleatoria**: Autos creados dinámicamente en carriles
- **Limpieza automática**: Eliminación de vehículos fuera de pantalla
- **Mecanismos de recuperación**: Fallbacks para prevenir estados atascados

---

## Uso

Ejecutar el script principal para iniciar la simulación. Los semáforos cambiarán automáticamente según las condiciones de tráfico.