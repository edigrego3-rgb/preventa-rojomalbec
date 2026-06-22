import os
from fpdf import FPDF
from .utils import redondear_precio

class PDF(FPDF):
    def header(self):
        pass
        
    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Pagina {self.page_no()} / {{nb}} - Generado por Rojo Malbec", align="C")

def crear_pdf_catalogo(df_catalogo, margen_global, output_path, logo_path=None):
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # Colores
    color_bordo = (139, 0, 0)
    color_dorado = (200, 160, 32)
    color_texto = (40, 40, 40)
    
    # Logo
    if logo_path and os.path.exists(logo_path):
        try:
            pdf.image(logo_path, x=85, y=10, w=40)
            pdf.ln(45)
        except:
            pdf.ln(10)
    else:
        pdf.ln(10)
        
    pdf.set_font("helvetica", "B", 24)
    pdf.set_text_color(*color_bordo)
    pdf.cell(0, 10, "Catalogo de Productos", align="C", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", "", 12)
    pdf.set_text_color(*color_dorado)
    pdf.cell(0, 10, "Rojo Malbec - Sales, Blends e Infusiones", align="C", new_x="LMARGIN", new_y="NEXT")
    
    pdf.ln(10)
    
    categorias = df_catalogo.groupby("Categoria")
    
    for cat_name, cat_df in categorias:
        if cat_df.empty:
            continue
            
        # Remover emojis (truco rápido: saltear primeros 2 caracteres si es emoji + espacio)
        cat_clean = cat_name[2:].strip() if len(cat_name) > 2 else cat_name
            
        pdf.set_font("helvetica", "B", 16)
        pdf.set_fill_color(*color_bordo)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 10, f"  {cat_clean}", fill=True, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)
        
        for idx, row in cat_df.iterrows():
            nombre = row["Nombre"]
            # Sanitizar texto para FPDF (Latin-1)
            nombre_sano = nombre.encode('latin-1', 'replace').decode('latin-1')
            
            costo = float(row["Precio_Mayorista"])
            precio_sugerido = redondear_precio(costo * (1 + (margen_global / 100)))
            
            pdf.set_font("helvetica", "B", 12)
            pdf.set_text_color(*color_texto)
            pdf.cell(140, 8, nombre_sano)
            
            pdf.set_font("helvetica", "B", 14)
            pdf.set_text_color(*color_dorado)
            pdf.cell(50, 8, f"$ {precio_sugerido:,}", align="R", new_x="LMARGIN", new_y="NEXT")
            
            pdf.set_draw_color(220, 220, 220)
            pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 190, pdf.get_y())
            pdf.ln(4)
            
            if pdf.get_y() > 260:
                pdf.add_page()
                
        pdf.ln(5)
        
    pdf.output(output_path)
    return output_path
