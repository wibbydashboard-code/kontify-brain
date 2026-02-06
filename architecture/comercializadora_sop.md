# SOP: Diagnóstico Técnico - Sector Comercializadora
**Versión:** 1.0
**Rol:** Consultor Senior de Mentores Estratégicos

## 1. Objetivo
Analizar de forma determinista las respuestas de un lead del sector comercializadora e importación para identificar riesgos en aduanas, precios de transferencia y blindaje de activos.

## 2. Entradas (Input)
- `niche_id`: "comercializadora"
- `responses`: Arreglo de preguntas (1-66).

## 3. Lógica de Análisis de Riesgos

### A. Cumplimiento Aduanero e Importación
- **Data Stage y Pedimentos (Q3 & Q8):** Si "No", elevado riesgo de auditorías de aduanas con multas retroactivas (PACO).
- **Padrón de Importadores (Q1):** Estado del registro es crítico para la continuidad operativa.

### B. Precios de Transferencia y Fiscalidad
- **Partes Relacionadas (Q11 & Q12):** La falta de estudio de precios de transferencia es un riesgo de ajuste fiscal masivo por parte del SAT.
- **Valuación de Inventarios (Q16 & Q17):** Inconsistencias aquí impactan directamente el costo de ventas y la utilidad fiscal.

### C. Blindaje de Marcas y Cartera
- **Propiedad de Marcas (Q28 & Q29):** Si las marcas están en la comercializadora, son activos embargables ante problemas operativos.
- **Seguro de Crédito (Q26):** Si no cuentan con protección de cartera, el riesgo de insolvencia de clientes es una amenaza financiera directa.

## 4. Estructura de Salida (Output)
- **Score de Riesgo:** Peso en cumplimiento aduanero y fiscalidad de partes relacionadas.
- **Economic Risk:** Estimar multas de comercio exterior (pueden ser del 70-100% del valor de la mercancía) y ajustes de precios de transferencia.
- **Sales Pitch:** Enfoque en la creación de una "IP-Co" para marcas y servicios de cumplimiento aduanero preventivo.
