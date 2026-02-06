
import sys
import os
import json
import uuid

# Añadir directorio de tools al path
sys.path.append(os.path.join(os.getcwd(), 'tools'))

from process_diagnostic import run_diagnostic
from pdf_generator_v2 import generate_pdf_final
from notificator import notify_all

def test_auditoria_maestra():
    print("🎯 Iniciando AUDITORÍA_MAESTRA_PEÑA...")
    
    # Datos de entrada simulados (Lo que enviaría el frontend)
    payload = {
        "lead_metadata": {
            "company_name": "AUDITORÍA_MAESTRA_PEÑA",
            "contact_name": "Ing. José Peña",
            "contact_role": "Director General",
            "contact_email": "jose.pena@constructora.com",
            "contact_phone": "5512345678",
            "niche_id": "constructora",
            "billing_range": "50M - 100M",
            "rfc": "CPN010203XYZ",
            "main_activity": "CONSTRUCCIÓN DE OBRA CIVIL E INDUSTRIAL",
            "financial_data": {
                "sales": "85M",
                "profit": "12M",
                "assets": "45M",
                "liabilities": "15M"
            }
        },
        "responses": [
            {"question": "¿Cuenta con registro REPSE vigente?", "answer": "NO"},
            {"question": "¿Tiene blindados los activos fijos en una PropCo?", "answer": "NO"},
            {"question": "¿Maneja contratos de obra a precio alzado?", "answer": "SÍ"},
            {"question": "¿Tiene implementado el SIROC en todas sus obras?", "answer": "SÍ"}
        ]
    }
    
    request_id = str(uuid.uuid4())[:8]
    
    try:
        # 1. IA Analysis
        print("🤖 Consultando motor de IA...")
        results = run_diagnostic(payload)
        
        if 'error' in results:
            print(f"❌ Error en IA: {results['error']}")
            return

        results['lead_metadata'] = payload['lead_metadata']
        results['responses'] = payload['responses']
        
        # 2. PDF Generation
        print("📄 Generando Reporte PDF Pro...")
        pdf_filename = f"KONTIFY_AUDITORIA_PEÑA_{request_id}.pdf"
        pdf_path = os.path.join('reports', pdf_filename)
        if not os.path.exists('reports'): os.makedirs('reports')
        
        generate_pdf_final(results, pdf_path)
        print(f"✅ PDF generado: {pdf_path}")
        
        # 3. CRM Sync (Sheets)
        print("📊 Sincronizando con Google Sheets...")
        pdf_url = f"http://test-server/reports/{pdf_filename}"
        notify_all(results, pdf_url)
        
        print("\n✨ AUDITORÍA COMPLETADA CON ÉXITO.")
        print(f"RFC: {payload['lead_metadata']['rfc']}")
        print(f"Actividad: {payload['lead_metadata']['main_activity']}")
        
    except Exception as e:
        print(f"💥 Error crítico en la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_auditoria_maestra()
