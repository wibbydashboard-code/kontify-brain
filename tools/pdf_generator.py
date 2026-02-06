import os
import json
from fpdf import FPDF
import markdown2

class DiagnosticPDF(FPDF):
    def header(self):
        # Logo de Mentores Estratégicos (Simulado con texto si no hay imagen)
        self.set_fill_color(0, 123, 255) # Azul Eléctrico
        self.rect(0, 0, 210, 15, 'F')
        
        self.set_text_color(255, 255, 255)
        self.set_font('helvetica', 'B', 12)
        self.cell(0, -5, 'MENTORES ESTRATÉGICOS - DIAGNÓSTICO EJECUTIVO', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(169, 169, 169)
        self.cell(0, 10, f'Página {self.page_no()} | Confidencial - Uso Interno Administrador', 0, 0, 'R')

def generate_pdf(json_data, output_path):
    pdf = DiagnosticPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    data = json_data.get('diagnostic_payload', json_data)
    
    # Título Principal
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('helvetica', 'B', 20)
    pdf.cell(0, 20, f"Reporte: {data.get('lead_metadata', {}).get('company_name', 'Diagnóstico')}", 0, 1, 'L')
    
    # Metadata
    pdf.set_font('helvetica', '', 10)
    pdf.cell(0, 5, f"Fecha: {data.get('lead_metadata', {}).get('timestamp', 'N/A')}", 0, 1)
    pdf.cell(0, 5, f"Contacto: {data.get('lead_metadata', {}).get('contact_name', 'N/A')}", 0, 1)
    pdf.cell(0, 5, f"Email: {data.get('lead_metadata', {}).get('contact_email', 'N/A')}", 0, 1)
    pdf.ln(10)

    # Risk Score Highlight
    score = data.get('risk_assessment', {}).get('overall_risk_score', data.get('lead_score', 'N/A'))
    pdf.set_font('helvetica', 'B', 16)
    pdf.set_fill_color(240, 248, 255)
    pdf.cell(0, 15, f"SCORE DE RIESGO: {score}/100", 1, 1, 'C', fill=True)
    pdf.ln(10)

    # Sales Pitch
    pitch = data.get('sales_pitch', 'N/A')
    if isinstance(pitch, dict):
        pitch = pitch.get('urgent_recommendation', 'N/A')
    
    pdf.set_font('helvetica', 'B', 14)
    pdf.cell(0, 10, "PITCH COMERCIAL SUGERIDO", 0, 1)
    pdf.set_font('helvetica', 'I', 12)
    pdf.set_text_color(0, 123, 255)
    pdf.multi_cell(0, 8, f'"{pitch}"')
    pdf.set_text_color(0, 0, 0)
    pdf.ln(10)

    # Content from markdown
    pdf.set_font('helvetica', 'B', 14)
    pdf.cell(0, 10, "CONTENIDO DETALLADO", 0, 1)
    pdf.set_font('helvetica', '', 11)
    
    raw_markdown = data.get('markdown_content', 'No se generó contenido detallado.')
    # Limpiar markdown de símbolos para PDF básico
    clean_text = raw_markdown.replace('**', '').replace('#', '').replace('*', '-')
    
    pdf.multi_cell(0, 6, clean_text)

    pdf.output(output_path)
    print(f"✅ PDF generado exitosamente en: {output_path}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Uso: python pdf_generator.py [json_input] [pdf_output]")
        sys.exit(1)
        
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    
    generate_pdf(json_data, sys.argv[2])
