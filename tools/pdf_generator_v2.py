import os
import json
from fpdf import FPDF
import datetime
import math

class DiagnosticPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.folio = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        self.primary_color = (0, 123, 255)   # Electric Blue
        self.dark_color = (33, 37, 41)       # Dark Gray/Black
        self.bg_color = (249, 249, 249)     # Light Gray
        self.danger_color = (220, 53, 69)     # Red
        self.set_auto_page_break(auto=True, margin=25)

    def header(self):
        # Fondo decorativo superior (Big Four Style)
        self.set_fill_color(*self.dark_color)
        self.rect(0, 0, 210, 30, 'F')
        
        # Logo Kontify (Alineado a la izquierda)
        self.set_xy(15, 8)
        self.set_fill_color(193, 255, 114) # Verde Neón
        self.rect(15, 10, 6, 6, 'F')
        
        self.set_text_color(255, 255, 255)
        self.set_font('helvetica', 'B', 16)
        self.set_xy(23, 10)
        self.cell(40, 6, 'KONTIFY', 0, 0, 'L')
        
        self.set_font('helvetica', '', 7)
        self.set_xy(23, 15)
        self.cell(40, 5, 'STRATEGIC CONSULTING GROUP', 0, 0, 'L')

        # Folio y Fecha (Elegante a la derecha)
        self.set_text_color(180, 180, 180)
        self.set_font('helvetica', 'B', 8)
        self.set_xy(140, 10)
        self.cell(55, 5, f"REF NO: {self.folio}", 0, 1, 'R')
        self.set_xy(140, 15)
        self.cell(55, 5, f"DATE: {datetime.date.today().strftime('%d / %m / %Y')}", 0, 1, 'R')
        self.ln(25)

    def footer(self):
        self.set_y(-20)
        self.set_font('helvetica', 'I', 7)
        self.set_text_color(150, 150, 150)
        
        # Línea divisoria
        self.set_draw_color(230, 230, 230)
        self.line(15, self.get_y(), 195, self.get_y())
        
        # Aviso de Privacidad elegante
        self.set_y(-15)
        self.cell(100, 10, "KONTIFY STRATEGIC CONSULTING - CONFIDENTIAL & PROPRIETARY", 0, 0, 'L')
        self.cell(0, 10, f'PAGE {self.page_no()} OF {{nb}}', 0, 0, 'R')

    def draw_gauge(self, x, y, score):
        # Fondo del gauge
        self.set_draw_color(230, 230, 230)
        self.set_line_width(4)
        r = 15
        
        # Dibujar arco de fondo (Simulado con segmentos)
        steps = 50
        for i in range(steps + 1):
            angle = math.pi + (i / steps) * math.pi
            px = x + r * math.cos(angle)
            py = y + r * math.sin(angle)
            if i == 0: self.set_xy(px, py)
            else: self.line(last_x, last_y, px, py)
            last_x, last_y = px, py

        # Dibujar arco de progreso (Degradado Amarillo -> Naranja -> Rojo)
        if score > 70: self.set_draw_color(220, 53, 69) # Red
        elif score > 40: self.set_draw_color(255, 165, 0) # Orange
        else: self.set_draw_color(255, 215, 0) # Gold
        
        score_steps = int((score / 100) * steps)
        for i in range(score_steps + 1):
            angle = math.pi + (i / steps) * math.pi
            px = x + r * math.cos(angle)
            py = y + r * math.sin(angle)
            if i == 0: pass
            else: self.line(last_x, last_y, px, py)
            last_x, last_y = px, py

        # Texto del score
        self.set_xy(x - 20, y - 5)
        self.set_text_color(*self.dark_color)
        self.set_font('helvetica', 'B', 14)
        self.cell(40, 10, f"{score}%", 0, 0, 'C')

def generate_pdf_final(json_data, output_path):
    pdf = DiagnosticPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    data = json_data.get('diagnostic_payload', json_data)
    lead_meta = data.get('lead_metadata', {})
    risk = data.get('risk_assessment', {})
    
    # --- HERO SECTION ---
    pdf.set_fill_color(*pdf.bg_color)
    pdf.rect(0, 30, 210, 60, 'F')
    
    pdf.set_xy(15, 40)
    pdf.set_text_color(*pdf.primary_color)
    pdf.set_font('helvetica', 'B', 24)
    pdf.cell(0, 12, "DIAGNÓSTICO ESTRATÉGICO", 0, 1)
    
    pdf.set_text_color(*pdf.dark_color)
    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(0, 8, f"CLIENTE: {lead_meta.get('company_name', 'Lead Assessment').upper()}", 0, 1)
    pdf.ln(2)
    
    # Gauge Score
    score = risk.get('overall_risk_score', 0)
    pdf.draw_gauge(170, 60, score)
    
    pdf.set_xy(15, 75)
    pdf.set_font('helvetica', 'B', 10)
    status_text = "RIESGO CRÍTICO" if score > 70 else "VULNERABILIDAD MODERADA" if score > 30 else "VIGILANCIA PREVENTIVA"
    pdf.cell(100, 5, f"ESTADO DE SALUD CORPORATIVA: {status_text}", 0, 1)
    
    pdf.ln(15)

    # --- PITCH SECTION (Strategic Recommendation) ---
    pitch = data.get('sales_pitch', '')
    if isinstance(pitch, dict): pitch = pitch.get('urgent_recommendation', 'Requiere intervención inmediata.')
    
    pdf.set_fill_color(255, 255, 255)
    pdf.set_draw_color(*pdf.primary_color)
    pdf.set_line_width(0.5)
    
    pdf.set_font('helvetica', 'B', 12)
    pdf.set_text_color(*pdf.primary_color)
    pdf.cell(0, 10, "ESTRATEGIA RECOMENDADA (PITCH)", 0, 1)
    
    # Reemplazar frases clave con negritas (simulado en PDF multi_cell no es fácil, usaremos estilo Italic para destacar)
    pdf.set_font('helvetica', 'I', 11)
    pdf.set_text_color(50, 50, 50)
    pdf.multi_cell(0, 6, f'"{pitch}"', 1, 'L')
    pdf.ln(10)

    # --- BOMB SECTION (Hallazgos Críticos) ---
    pdf.set_fill_color(255, 245, 245)
    pdf.set_draw_color(*pdf.danger_color)
    pdf.set_line_width(0.3)
    
    pdf.set_font('helvetica', 'B', 12)
    pdf.set_text_color(*pdf.danger_color)
    pdf.cell(0, 10, "⚠️ HALLAZGOS DE VULNERABILIDAD CRÍTICA", 0, 1)
    
    pdf.set_font('helvetica', '', 10)
    pdf.set_text_color(30, 30, 30)
    
    content = data.get('markdown_content', '')
    # Filtrar solo hallazgos de alto impacto para esta sección si es posible, o limpiar el markdown
    processed_content = content.replace('**', '').replace('#', '').replace('*', '•')
    
    pdf.multi_cell(0, 5.5, processed_content, 1, 'L', fill=True)
    
    pdf.output(output_path)
    print(f"✅ PDF Executivo Big Four generado en: {output_path}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        sys.exit(1)
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    generate_pdf_final(json_data, sys.argv[2])
