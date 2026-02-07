# DIAGNÓSTICO DE SALUD — KONTIFY (PMDS-IA)
**Fecha:** 2026-02-06

## Diagnóstico
El error persistía por una cadena de fallas de cableado y validación:
1. **Encoding Ghost (latin-1)**: Existían lecturas/escrituras sin UTF-8 en scripts auxiliares, lo que abría la puerta a errores con acentos/ñ en rutas o logs.
2. **Respuestas truncadas**: La normalización descartaba respuestas sin `question`, dejando el payload vacío aunque existiera `q_index`, causando 0.0%.
3. **Prompt insuficiente para multiselección**: La instrucción no explicitaba el tratamiento de opciones múltiples y podía degradar la evaluación.
4. **Parser de SOP frágil con [OPTIONS:]**: El parser dependía de coincidencias rígidas y podía omitir opciones si el tag venía con variaciones de formato.
5. **CRM con errores 403/invalid_grant**: La sincronización a Sheets podía fallar por permisos insuficientes o credenciales inválidas, silenciando señales operativas clave.

## Acciones Correctivas Ejecutadas
- **UTF-8 obligatorio** en todas las lecturas/escrituras críticas del proyecto.
- **Normalización robusta de `responses`** (soporta `q_index`/`category_id`) y bloqueo del flujo si están vacías.
- **Prompt ampliado** con conteo de respuestas y reglas explícitas para opciones múltiples.
- **Parser de SOP robusto** para capturar `[OPTIONS:]` con variaciones y en línea o siguiente línea.
- **Logs de error explícitos** para 403 e invalid_grant en Google Sheets (incluye posible bloqueo Render).

## Resultado Esperado
- Eliminación de reportes vacíos (0.0%).
- Estabilidad con caracteres latinos (ñ/acentos) en todo el flujo.
- Diagnósticos consistentes y auditables bajo PMDS-IA.

## Prueba de Estrés
La simulación requerida está preparada en test_stress_pena.py con la empresa:
**"Construcción e Ingeniería Peña S.A."**

Para confirmar ejecución real, el entorno debe contar con:
- GEMINI_API_KEY válida
- Credenciales de Google Sheets compartidas con la cuenta de servicio
