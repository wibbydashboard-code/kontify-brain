import os
import json
from fpdf import FPDF
import datetime

class DiagnosticPDF(FPDF):
    def __init__(self):
        super().__init__()
        # self.add_font('Poppins', '', 'public/assets/Poppins-Regular.ttf')
        self.folio = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    def header(self):
        # Fondo decorativo superior
        self.set_fill_color(0, 0, 0)
        self.rect(0, 0, 210, 25, 'F')
        
        # Logo placeholder (Simulado con colores de marca)
        self.set_xy(10, 5)
        self.set_fill_color(193, 255, 114) # Verde Neón
        self.rect(10, 14, 8, 8, 'F')
        
        self.set_text_color(255, 255, 255)
        self.set_font('helvetica', 'B', 16)
        self.set_xy(20, 13)
        self.cell(40, 10, 'Kontify', 0, 0, 'L')
        
        self.set_font('helvetica', '', 8)
        self.set_xy(20, 19)
        self.cell(40, 5, 'Mentores Estratégicos', 0, 0, 'L')

        # Folio y Fecha
        self.set_text_color(150, 150, 150)
        self.set_font('helvetica', '', 9)
        self.set_xy(150, 13)
        self.cell(50, 5, f"Folio: {self.folio}", 0, 1, 'R')
        self.set_xy(150, 18)
        self.cell(50, 5, f"Fecha: {datetime.date.today().strftime('%d/%m/%Y')}", 0, 1, 'R')
        self.ln(15)

    def footer(self):
        self.set_y(-30)
        self.set_font('helvetica', '', 7)
        self.set_text_color(100, 100, 100)
        
        # Aviso de Privacidad
        footer_text = "Aviso de Privacidad: Los datos recabados en este diagnóstico son tratados con estricta confidencialidad por Kontify. Sus datos personales están protegidos conforme a la Ley Federal de Protección de Datos Personales. Este documento constituye un diagnóstico preliminar basado en información autodeclarada."
        self.multi_cell(0, 3, footer_text, 0, 'C')
        
        self.set_y(-10)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()} | Kontify - Mentores Estratégicos', 0, 0, 'C')

def generate_pdf_final(json_data, output_path):
    pdf = DiagnosticPDF()
    pdf.set_auto_page_break(auto=True, margin=35)
    pdf.add_page()
    
    data = json_data.get('diagnostic_payload', json_data)
    
    # Hero Section
    pdf.set_text_color(0, 123, 255)
    pdf.set_font('helvetica', 'B', 22)
    pdf.cell(0, 20, "DIAGNÓSTICO DE RIESGO CORPORATIVO", 0, 1, 'L')
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('helvetica', 'B', 14)
    pdf.cell(0, 10, f"Cliente: {data.get('lead_metadata', {}).get('company_name', 'Diagnóstico')}", 0, 1)
    pdf.ln(5)

    # Risk Meter (Simulado)
    score = data.get('lead_score', data.get('risk_assessment', {}).get('overall_risk_score', 0))
    pdf.set_fill_color(240, 240, 240)
    pdf.rect(10, pdf.get_y(), 190, 15, 'F')
    
    fill_width = (score / 100) * 190
    if score > 70: pdf.set_fill_color(255, 50, 50)
    elif score > 40: pdf.set_fill_color(255, 200, 0)
    else: pdf.set_fill_color(193, 255, 114)
    
    pdf.rect(10, pdf.get_y(), fill_width, 15, 'F')
    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(0, 15, f"SCORE DE RIESGO: {score}/100", 0, 1, 'C')
    pdf.ln(10)

    # Pitch Box
    pitch = data.get('sales_pitch', 'N/A')
    if isinstance(pitch, dict): pitch = pitch.get('urgent_recommendation', 'N/A')
    
    pdf.set_fill_color(230, 242, 255)
    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(0, 10, "ESTRATEGIA RECOMENDADA (PITCH)", 0, 1)
    pdf.set_font('helvetica', 'I', 11)
    pdf.set_text_color(0, 80, 160)
    pdf.multi_cell(0, 7, f'"{pitch}"', 1, 'L', fill=True)
    pdf.set_text_color(0, 0, 0)
    pdf.ln(10)

    # Detailed Content
    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(0, 10, "HALLAZGOS Y ANÁLISIS TÉCNICO", 0, 1)
    pdf.set_font('helvetica', '', 10)
    
    content = data.get('markdown_content', '')
    clean_content = content.replace('**', '').replace('#', '').replace('*', '-')
    pdf.multi_cell(0, 5, clean_content)

    pdf.output(output_path)
    print(f"✅ PDF final de Kontify generado en: {output_path}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Uso: python pdf_generator.py [json_input] [pdf_output]")
        sys.exit(1)
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    generate_pdf_final(json_data, sys.argv[2])
