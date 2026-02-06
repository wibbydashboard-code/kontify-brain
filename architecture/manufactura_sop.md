# SOP: Diagnóstico Técnico - Sector Manufactura
**Versión:** 1.0
**Rol:** Consultor Senior de Mentores Estratégicos

## 1. Objetivo
Analizar de forma determinista las respuestas de un lead del sector manufactura/transformación para identificar riesgos en activos fijos, costeo, cumplimiento laboral y blindaje patrimonial.

## 2. Entradas (Input)
- `niche_id`: "manufactura"
- `responses`: Arreglo de preguntas (1-66).

## 3. Lógica de Análisis de Riesgos

### A. Gestión de Activos y Maquinaria
- **Propiedad de Maquinaria (Q11 & Q18):** Si la maquinaria está en la misma empresa que opera la nómina y la producción, riesgo de embargo laboral inminente sobre el corazón del negocio.
- **Leasing y Seguros (Q11, Q15, Q16):** La falta de seguros de interrupción de negocio es un punto de fallo crítico para la continuidad operativa.

### B. Costeo e Inventarios
- **Sistemas de Costeo (Q26 & Q29):** La falta de un sistema de costos integrado al ERP sugiere falta de visibilidad en márgenes y posibles fugas financieras.
- **Materialidad y Mermas (Q28 & Q36):** Riesgo de rechazo de deducciones por parte del SAT si no se documenta correctamente la materialidad de materias primas.

### C. Cumplimiento Laboral y Blindaje
- **REPSE y Nómina (Q41 & Q42):** Fundamental verificar que los servicios especializados estén en cumplimiento para evitar responsabilidad solidaria y no deducibilidad.
- **Patentes y Marcas (Q4 & Q9):** La falta de una IP-Co expone los intangibles de la fábrica a riesgos operativos.

## 4. Estructura de Salida (Output)
- **Score de Riesgo:** Peso en blindaje de activos y cumplimiento laboral de planta.
- **Economic Risk:** Estimar impacto por paros de planta (Lucro cesante) y multas de la STPS o IMSS.
- **Sales Pitch:** Enfoque en la segregación de activos (PropCo para planta, AssetCo para maquinaria) y optimización del costo fiscal mediante materialidad robusta.
