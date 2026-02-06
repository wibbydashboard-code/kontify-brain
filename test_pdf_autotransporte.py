
import json
import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'tools'))
from pdf_generator_v2 import generate_pdf_final

dummy_data = {
    "lead_metadata": {
        "company_name": "TRANSPORTES LOGISTICOS SA",
        "rfc": "TLOG900101XYZ",
        "main_activity": "AUTOTRANSPORTE DE CARGA",
        "financial_data": {"sales": "50M - 100M", "profit": "5M", "assets": "20M", "liabilities": "5M"}
    },
    "diagnostic_payload": {
        "risk_assessment": {
            "overall_risk_score": 82,
            "risk_level": "RIESGO CRÍTICO",
            "critical_finding": "Falta de Blindaje en Activos y Régimen no optimizado."
        },
        "markdown_content": "### Hallazgos\n- Falta de Holding\n- Activos en operativa",
        "responses": [
            {"question": "¿Bajo qué régimen tributario operan sus empresas actualmente?", "answer": "Régimen de Coordinados"},
            {"question": "¿Cuenta con una empresa dedicada exclusivamente al mantenimiento de equipo?", "answer": "SÍ"},
            {"question": "¿Tiene blindada la cuenta bancaria principal contra embargos?", "answer": "NO"}
        ]
    }
}

output_pdf = "test_autotransporte_report.pdf"
try:
    generate_pdf_final(dummy_data, output_pdf)
    if os.path.exists(output_pdf):
        print(f"✅ PDF generated successfully: {output_pdf}")
    else:
        print("❌ PDF generation failed.")
except Exception as e:
    print(f"❌ Error during PDF generation: {e}")
