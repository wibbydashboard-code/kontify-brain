# PROTOCOLO PMDS-IA (Versión Adaptada: Kontify Python Core)
**Firma:** Mentores Estratégicos  
**Versión:** 1.2.1-PY  
**Estado:** Ley Marcial Operativa  

---

## 🛑 1. PRINCIPIOS DE SEGURIDAD Y GOBERNANZA (ZERO-FAILURE)

1. **Validación de Esquema Obligatoria:** Antes de cualquier procesamiento, el sistema DEBE validar la existencia y formato de los campos maestros: `company_name`, `rfc`, `activity`, `email` y `answers`.
2. **UTF-8 como Estándar Único:** Se prohíbe el uso de `latin-1`. Todo string debe ser codificado/decodificado en UTF-8 para soportar acentos, comillas y la letra "ñ" sin romper el sistema.
3. **Logs JSON Estructurados:** Todo error debe generar un log en formato JSON que incluya:
   - `requestId`: UUID único por sesión de diagnóstico.
   - `timestamp`: Fecha y hora exacta.
   - `errorCode`: Clasificación del fallo.
   - `context`: Datos que causaron el error (sin información sensible).

---

## 🏗️ 2. ESTÁNDAR DE INTEGRACIÓN (CRM & PDF)

### A. Sincronización con Google Sheets
* **Atomicidad:** La escritura en la hoja `1zYPKfP1xObqhxkRNmaTjCbjI-jPR1Vec2c9uMHH0sVg` debe ser prioritaria.
* **Mapeo de Columnas Sagrado:**
  - **Columna K:** RFC (Sanitizado y en mayúsculas).
  - **Columna L:** Actividad Principal (Texto íntegro capturado de la Fase 1).

### B. Generación de Reportes PDF
* **Unicode Support:** El motor de PDF (FPDF/ReportLab) debe cargar fuentes que soporten caracteres especiales (ej. DejaVuSans).
* **Sección de Auditoría:** Todo PDF debe incluir al final el "DETALLE DE RESPUESTAS TÉCNICAS" para dar transparencia al diagnóstico.
* **No 0% Policy:** Si el motor de IA no recibe datos suficientes, el sistema debe arrojar un error de validación en lugar de generar un reporte vacío (0.0%).

---

## 📂 3. ORGANIZACIÓN DEL PROYECTO (PYTHON ESTRUCTURADO)

* `server.py`: Orquestador de rutas y validación de entrada.
* `brain.py`: Motor de lógica con Gemini API y cálculo de Score.
* `notificator.py`: Gestión de conectividad externa (Sheets, Slack, Mail).
* `architecture/*.md`: Repositorio de vectores de riesgo y SOPs por nicho.

---

## 🔄 4. FLUJO DE TRABAJO DEL AGENTE (THE LOOP)

1. **Fase de Verificación:** Leer el estado actual de los archivos y los logs de error antes de escribir código.
2. **Fase de Implementación:** Aplicar cambios atómicos. Si se modifica un SOP (.md), se debe verificar el impacto en el parser del `server.py`.
3. **Fase de Auditoría:** Realizar un test con el nombre "STRESS_TEST_PEÑA" para asegurar que los caracteres especiales no bloqueen el flujo.

---

## 🛡️ 5. CLASIFICACIÓN DE SEVERIDAD

* **🔴 ERROR CRÍTICO:** Fallo en registro de Sheets, PDF vacío, error de codec 'latin-1', omisión de RFC.
  - *Acción:* **BLOQUEO TOTAL.** No se permite despliegue hasta su resolución.
* **🟡 WARNING:** Estética de UI, falta de comentarios, optimización de prompt.
  - *Acción:* Registro en bitácora para resolución posterior.