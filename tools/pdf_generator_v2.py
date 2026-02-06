import os
import json
from fpdf import FPDF
import datetime
import math
import unicodedata

class DiagnosticPDF(FPDF):
    def __init__(self):
        super().__init__()
        # Usar fuentes core que soportan latin-1 básico por defecto, 
        # fpdf2 maneja mejor Unicode pero para acentos/ñ requerimos fuentes específicas
        # o normalizar. Dado que es un entorno sin fuentes locales aseguradas:
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
        self.cell(40, 6, safe_text('KONTIFY'), 0, 0, 'L')
        
        self.set_font('helvetica', '', 7)
        self.set_xy(23, 15)
        self.cell(40, 5, safe_text('STRATEGIC CONSULTING GROUP'), 0, 0, 'L')

        # Folio y Fecha (Elegante a la derecha)
        self.set_text_color(180, 180, 180)
        self.set_font('helvetica', 'B', 8)
        self.set_xy(140, 10)
        self.cell(55, 5, safe_text(f"REF NO: {self.folio}"), 0, 1, 'R')
        self.set_xy(140, 15)
        self.cell(55, 5, safe_text(f"DATE: {datetime.date.today().strftime('%d / %m / %Y')}"), 0, 1, 'R')
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
        self.cell(100, 10, safe_text("KONTIFY STRATEGIC CONSULTING - CONFIDENTIAL & PROPRIETARY"), 0, 0, 'L')
        self.cell(0, 10, safe_text(f'PAGE {self.page_no()} OF {{nb}}'), 0, 0, 'R')

    def draw_gauge(self, x, y, score):
        # Asegurar que el score es numérico
        try:
            score = float(score)
        except:
            score = 0
            
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

import unicodedata

def safe_text(txt):
    """
    Normalización de Texto para fpdf2 (Protocolo PMDS-IA).
    Permite acentos y 'ñ' para fuentes core (Helvetica/Arial) usando latin-1.
    """
    if txt is None: return "N/A"
    if not isinstance(txt, str): txt = str(txt)
    
    # Reemplazo de caracteres Unicode "fancy" que rompen fuentes estándar
    replacements = {
        '\u2013': '-', '\u2014': '-', '\u201c': '"', '\u201d': '"',
        '\u2018': "'", '\u2019': "'", '\u2022': '*', '\u2026': '...',
        '\u00a0': ' ', '\ufeff': '', '\u200b': ''
    }
    for k, v in replacements.items():
        txt = txt.replace(k, v)

    # Intentar codificar a latin-1 (soporta á, é, í, ó, ú, ñ, ¿, ¡)
    try:
        return txt.encode('latin-1', 'replace').decode('latin-1')
    except:
        # Fallback a ASCII si hay algo catastrófico
        return txt.encode('ascii', 'ignore').decode('ascii')

def generate_pdf_final(json_data, output_path):
    pdf = DiagnosticPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    data = json_data.get('diagnostic_payload', json_data)
    lead_meta = json_data.get('lead_metadata', data.get('lead_metadata', {}))
    
    # Fallback robusto para Risk Assessment
    risk = data.get('risk_assessment') or data.get('lead_assessment') or data.get('admin_report', {})
    
    # --- HERO SECTION ---
    pdf.set_fill_color(*pdf.bg_color)
    pdf.rect(0, 30, 210, 60, 'F')
    
    pdf.set_xy(15, 40)
    pdf.set_text_color(*pdf.primary_color)
    pdf.set_font('helvetica', 'B', 24)
    pdf.cell(0, 12, safe_text("DIAGNÓSTICO ESTRATÉGICO"), 0, 1)
    
    pdf.set_text_color(*pdf.dark_color)
    pdf.set_font('helvetica', 'B', 11)
    company = str(lead_meta.get('company_name', 'Lead Assessment')).upper()
    rfc = str(lead_meta.get('rfc', 'N/A')).upper()
    giro = str(lead_meta.get('main_activity', lead_meta.get('activity', 'N/A'))).upper()
    
    pdf.cell(0, 7, safe_text(f"CLIENTE: {company}"), 0, 1)
    pdf.set_font('helvetica', 'B', 9)
    pdf.cell(0, 5, safe_text(f"RFC: {rfc} | GIRO: {giro}"), 0, 1)
    pdf.ln(2)
    
    # Gauge Score (Buscar en múltiples lugares)
    score = risk.get('overall_risk_score', risk.get('risk_score', risk.get('score', 0)))
    if score == 0 and 'score' in data: score = data['score']
    
    pdf.draw_gauge(170, 60, score)
    
    pdf.set_xy(15, 75)
    pdf.set_font('helvetica', 'B', 10)
    status_text = "RIESGO CRÍTICO" if float(score) > 70 else "VULNERABILIDAD MODERADA" if float(score) > 30 else "VIGILANCIA PREVENTIVA"
    pdf.cell(100, 5, safe_text(f"ESTADO DE SALUD CORPORATIVA: {status_text}"), 0, 1)
    
    pdf.ln(15)

    # --- FINANCIAL DATA SECTION ---
    fin = lead_meta.get('financial_data', {})
    if fin:
        pdf.set_fill_color(245, 245, 245)
        pdf.rect(15, pdf.get_y(), 180, 20, 'F')
        
        pdf.set_font('helvetica', 'B', 8)
        pdf.set_text_color(100, 100, 100)
        pdf.set_xy(20, pdf.get_y() + 2)
        pdf.cell(40, 5, safe_text("RFC / TAX ID"), 0, 0)
        pdf.cell(45, 5, safe_text("VENTAS (RANGO)"), 0, 0)
        pdf.cell(45, 5, safe_text("UTILIDAD NETA"), 0, 0)
        pdf.cell(45, 5, safe_text("PATRIMONIO ESTIMADO"), 0, 1)
        
        pdf.set_font('helvetica', 'B', 10)
        pdf.set_text_color(0, 0, 0)
        pdf.set_x(20)
        pdf.cell(40, 5, safe_text(str(lead_meta.get('rfc', 'N/A')).upper()), 0, 0)
        
        # Usar el rango de facturación si existe
        sales_val = lead_meta.get('billing_range', fin.get('sales', 'N/A'))
        pdf.cell(45, 5, safe_text(f"$ {sales_val}"), 0, 0)
        pdf.cell(45, 5, safe_text(f"$ {fin.get('profit', '0')}"), 0, 0)
        
        try:
            # Limpiar strings de comas antes de convertir
            a = float(str(fin.get('assets', 0)).replace(',', '').replace('$', ''))
            p = float(str(fin.get('liabilities', 0)).replace(',', '').replace('$', ''))
            ap_str = f"$ {a - p:,.0f}"
        except:
            ap_str = "N/A"
        pdf.cell(45, 5, safe_text(ap_str), 0, 1)
        pdf.ln(10)

    # --- PITCH SECTION (Strategic Recommendation) ---
    pitch = data.get('sales_pitch') or risk.get('summary') or risk.get('recommendation') or "Requiere intervención inmediata."
    if isinstance(pitch, dict): pitch = pitch.get('urgent_recommendation', 'Requiere intervención inmediata.')
    
    pdf.set_fill_color(255, 255, 255)
    pdf.set_draw_color(*pdf.primary_color)
    pdf.set_line_width(0.5)
    
    pdf.set_font('helvetica', 'B', 12)
    pdf.set_text_color(*pdf.primary_color)
    pdf.cell(0, 10, safe_text("ESTRATEGIA RECOMENDADA (PITCH)"), 0, 1)
    
    pdf.set_font('helvetica', 'I', 11)
    pdf.set_text_color(50, 50, 50)
    pdf.multi_cell(0, 6, safe_text(f'"{pitch}"'), 1, 'L')
    pdf.ln(10)

    # --- BOMB SECTION (Hallazgos Críticos) ---
    pdf.set_fill_color(255, 245, 245)
    pdf.set_draw_color(*pdf.danger_color)
    pdf.set_line_width(0.3)
    
    pdf.set_font('helvetica', 'B', 12)
    pdf.set_text_color(*pdf.danger_color)
    pdf.cell(0, 10, safe_text("⚠️ HALLAZGOS DE VULNERABILIDAD CRÍTICA"), 0, 1)
    
    pdf.set_font('helvetica', '', 10)
    pdf.set_text_color(30, 30, 30)
    
    content = data.get('markdown_content') or data.get('findings') or data.get('risk_analysis') or "Análisis técnico pendiente de validación."
    if isinstance(content, list): content = "\n".join(content)
    
    processed_content = str(content).replace('**', '').replace('#', '').replace('*', '*')
    
    pdf.multi_cell(0, 5.5, safe_text(processed_content), 1, 'L', fill=True)
    pdf.ln(10)

    # --- ANSWERS DETAIL SECTION ---
    responses = data.get('responses', [])
    if responses:
        pdf.add_page()
        pdf.set_font('helvetica', 'B', 14)
        pdf.set_text_color(*pdf.primary_color)
        pdf.cell(0, 10, safe_text("DETALLE DE RESPUESTAS TÉCNICAS"), 0, 1)
        pdf.ln(5)
        
        pdf.set_font('helvetica', '', 9)
        pdf.set_text_color(50, 50, 50)
        
        for idx, resp in enumerate(responses):
            q_text = f"{idx+1}. {resp.get('question', 'Pregunta sin texto')}"
            a_text = str(resp.get('answer', 'N/A')).upper()
            
            # Dibujar Pregunta
            pdf.set_font('helvetica', 'B', 9)
            pdf.multi_cell(0, 5, safe_text(q_text), 0, 'L')
            
            # Dibujar Respuesta
            pdf.set_font('helvetica', 'B', 9)
            if a_text in ['SÍ', 'SI']:
                pdf.set_text_color(*pdf.primary_color)
            elif a_text == 'NO':
                pdf.set_text_color(*pdf.danger_color)
            else:
                pdf.set_text_color(100, 100, 100)
            
            pdf.cell(10, 5, "   > ", 0, 0)
            pdf.cell(0, 5, safe_text(a_text), 0, 1)
            pdf.set_text_color(50, 50, 50)
            pdf.ln(2)
            
            if pdf.get_y() > 250:
                pdf.add_page()
    
    pdf.output(output_path)
    print(f"✅ PDF Executivo Big Four generado exitosamente en: {output_path}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        sys.exit(1)
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        json_data = json.load(f)
    generate_pdf_final(json_data, sys.argv[2])
