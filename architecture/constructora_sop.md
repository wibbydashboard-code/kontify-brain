# SOP: Diagnóstico Técnico - Sector Constructora
**Versión:** 1.0
**Rol:** Consultor Senior de Mentores Estratégicos

## 1. Objetivo
Analizar de forma determinista las respuestas de un lead del sector construcción para identificar riesgos fiscales, patrimoniales y operativos, generando un pitch de venta basado en soluciones de blindaje.

## 2. Entradas (Input)
- `niche_id`: "constructora"
- `responses`: Arreglo de preguntas (1-66) y respuestas del usuario.

## 3. Lógica de Análisis de Riesgos
La IA debe priorizar la detección de los siguientes patrones críticos:

### A. Riesgo Operativo y Seguridad Social (Prioridad Alta)
- **SIROC (Q3):** Si "No", señalar riesgo inminente de multas del IMSS y paralización de obras.
- **REPSE (Q2):** Si "No", invalidación de deducibilidad de facturas de subcontratistas.
- **Cierre de Obra (Q12):** Si "No", riesgo de auditorías de oficina por periodos no cerrados.

### B. Riesgo Patrimonial (Prioridad Crítica)
- **PropCo/Operativa (Q5 & Q10):** Si los inmuebles o la tierra están en la misma empresa que opera la obra, existe un riesgo de embargo total ante demandas laborales o multas fiscales.
- **Blindaje de Activos (Q41-Q55):** Si hay más de 5 respuestas negativas en esta sección, el diagnóstico debe enfocarse en la creación de una estructura de "Holding" o "PropCo".

### C. Eficiencia Fiscal (Prioridad Media)
- **IVA (Q26 & Q27):** Falta de prorrateo en mezcla de tasas (vivienda/comercial) genera pérdidas financieras directas.
- **Deducción de Terrenos (Q34):** Si "No", se está omitiendo un beneficio fiscal clave del Art. 191 LISR.

## 4. Estructura de Salida (Output)
Debe seguir estrictamente el `Diagnostic Payload` definido en `gemini.md`.

- **Score de Riesgo:** 
    - 0-30: Saludable
    - 31-60: Riesgo Moderado
    - 61-100: Riesgo Crítico (Requiere intervención inmediata)
- **Economic Risk:** Estimar el impacto en términos de "Costo de multas estimadas (10-30% del valor de obra)" o "Pérdida de deducibilidad".
- **Sales Pitch:** Debe ser autoritario. Ejemplo: "Usted tiene sus activos más valiosos expuestos al riesgo operativo de la construcción. Necesitamos migrar a un modelo de PropCo de inmediato."

## 5. Casos Extremos
- Si el usuario respondió menos del 20% del cuestionario: Marcar como "Diagnóstico Inconcluso por alta opacidad - Riesgo por falta de visibilidad".
