"""
Genera el instructivo del contador en formato Word (.docx)
"""
from docx import Document
from docx.shared import Pt, RGBColor, Inches, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import copy

doc = Document()

# ── Estilos globales ────────────────────────────────────────────────────────
style = doc.styles['Normal']
style.font.name = 'Calibri'
style.font.size = Pt(11)

# Márgenes de página
from docx.oxml import OxmlElement
section = doc.sections[0]
section.page_width  = Inches(8.5)
section.page_height = Inches(11)
section.left_margin   = Cm(2.5)
section.right_margin  = Cm(2.5)
section.top_margin    = Cm(2.0)
section.bottom_margin = Cm(2.0)

AZUL       = RGBColor(0x1E, 0x40, 0xAF)   # azul oscuro
AZUL_CLARO = RGBColor(0xDB, 0xEA, 0xFE)   # fondo azul claro
GRIS_CLARO = RGBColor(0xF3, 0xF4, 0xF6)   # fondo gris
VERDE      = RGBColor(0x16, 0x6A, 0x34)   # verde oscuro
NARANJA    = RGBColor(0xC2, 0x51, 0x0A)   # naranja
BLANCO     = RGBColor(0xFF, 0xFF, 0xFF)
NEGRO      = RGBColor(0x11, 0x18, 0x27)

def set_cell_bg(cell, hex_color):
    """Poner color de fondo a celda."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)

def set_cell_borders(cell, top=True, bottom=True, left=True, right=True, color='CCCCCC'):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    for side, flag in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        if flag:
            el = OxmlElement(f'w:{side}')
            el.set(qn('w:val'), 'single')
            el.set(qn('w:sz'), '4')
            el.set(qn('w:space'), '0')
            el.set(qn('w:color'), color)
            tcBorders.append(el)
    tcPr.append(tcBorders)

def add_heading(text, level=1, color=AZUL):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14 if level == 1 else 8)
    p.paragraph_format.space_after  = Pt(4)
    run = p.add_run(text)
    run.bold = True
    run.font.color.rgb = color
    run.font.size = Pt({1: 16, 2: 13, 3: 11.5}.get(level, 11))
    return p

def add_body(text, bold=False, color=None, size=None, space_before=0, space_after=4):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after  = Pt(space_after)
    run = p.add_run(text)
    run.bold = bold
    run.font.size = Pt(size or 11)
    if color:
        run.font.color.rgb = color
    return p

def add_tip(text, icon='💡', bg='EFF6FF', border_color='BFDBFE'):
    """Caja de tip con fondo azul."""
    t = doc.add_table(rows=1, cols=1)
    t.alignment = WD_TABLE_ALIGNMENT.LEFT
    cell = t.cell(0, 0)
    set_cell_bg(cell, bg)
    set_cell_borders(cell, color=border_color)
    cell.paragraphs[0].clear()
    run = cell.paragraphs[0].add_run(f'{icon}  {text}')
    run.font.size = Pt(10.5)
    run.font.color.rgb = RGBColor(0x1E, 0x40, 0xAF)
    cell.paragraphs[0].paragraph_format.space_before = Pt(4)
    cell.paragraphs[0].paragraph_format.space_after  = Pt(4)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)

def add_separator():
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after  = Pt(2)
    pPr = p._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '6')
    bottom.set(qn('w:space'), '1')
    bottom.set(qn('w:color'), 'BFDBFE')
    pBdr.append(bottom)
    pPr.append(pBdr)

def add_step(num, text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent   = Cm(0.5)
    p.paragraph_format.space_before  = Pt(1)
    p.paragraph_format.space_after   = Pt(2)
    r1 = p.add_run(f'  {num}.  ')
    r1.bold = True
    r1.font.color.rgb = AZUL
    r1.font.size = Pt(11)
    r2 = p.add_run(text)
    r2.font.size = Pt(11)

def add_bullet(text, indent=0.8):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.left_indent  = Cm(indent)
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after  = Pt(2)
    run = p.add_run(text)
    run.font.size = Pt(11)

# ════════════════════════════════════════════════════════════════════════════
# PORTADA
# ════════════════════════════════════════════════════════════════════════════

# Bloque azul de encabezado simulado con tabla
header_tbl = doc.add_table(rows=1, cols=1)
header_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
hc = header_tbl.cell(0, 0)
set_cell_bg(hc, '1E40AF')
hc.width = Inches(5.5)

p_title = hc.paragraphs[0]
p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_title.paragraph_format.space_before = Pt(14)
p_title.paragraph_format.space_after  = Pt(4)
r = p_title.add_run('INSTRUCTIVO DE USO')
r.bold = True
r.font.size = Pt(20)
r.font.color.rgb = BLANCO

p_sub = hc.add_paragraph()
p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_sub.paragraph_format.space_after = Pt(4)
r2 = p_sub.add_run('Panel de Contabilidad')
r2.font.size = Pt(14)
r2.font.color.rgb = RGBColor(0xBF, 0xDB, 0xFE)

p_emp = hc.add_paragraph()
p_emp.alignment = WD_ALIGN_PARAGRAPH.CENTER
p_emp.paragraph_format.space_after = Pt(14)
r3 = p_emp.add_run('Alfa Vidrio y Aluminio · Sistema ERP')
r3.font.size = Pt(11)
r3.font.color.rgb = RGBColor(0x93, 0xC5, 0xFD)

doc.add_paragraph().paragraph_format.space_after = Pt(6)

# ════════════════════════════════════════════════════════════════════════════
# SECCIÓN 1 — ACCESO
# ════════════════════════════════════════════════════════════════════════════
add_heading('1.  Cómo entrar al sistema', level=1)
add_separator()
doc.add_paragraph().paragraph_format.space_after = Pt(2)

add_step(1, 'Abre Google Chrome o Edge.')
add_step(2, 'En la barra de direcciones escribe:  alfavidrioyaluminio.com  (o el link que te proporcionó el administrador).')
add_step(3, 'Inicia sesión con tu correo y contraseña de empleado.')
add_step(4, 'En el menú lateral izquierdo busca  "Contabilidad"  →  "Panel Contador".')

add_tip('Si olvidaste tu contraseña, pídele al administrador que la restablezca desde el módulo Usuarios.')

# ════════════════════════════════════════════════════════════════════════════
# SECCIÓN 2 — PESTAÑAS
# ════════════════════════════════════════════════════════════════════════════
add_heading('2.  Las 8 pestañas del panel', level=1)
add_separator()

tab_data = [
    ('#',  'Pestaña',        'Para qué sirve'),
    ('1',  'Resumen',        'Vista rápida del estado financiero: por cobrar, por pagar, vencido y utilidad neta.'),
    ('2',  'Reportes',       'Tabla y gráfica mensual de facturado vs gastos vs utilidad. Desglose por categoría.'),
    ('3',  'Clientes',       'Saldo pendiente y vencido por cada cliente. Ventas del mes en curso.'),
    ('4',  'Inventario',     'Valor del stock en almacén (costo y venta). Requiere precios capturados en productos.'),
    ('5',  'x Cobrar',       'Lista completa de facturas de clientes con antigüedad y filtros por estado.'),
    ('6',  'x Pagar',        'Facturas de proveedores pendientes de pago.'),
    ('7',  'Cotizaciones',   'Vista de solo lectura de todas las cotizaciones emitidas por ventas.'),
    ('8',  'Comprobantes',   'Historial de todos los pagos recibidos, agrupados por mes.'),
]

tbl = doc.add_table(rows=len(tab_data), cols=3)
tbl.style = 'Table Grid'
tbl.alignment = WD_TABLE_ALIGNMENT.LEFT

col_widths = [Cm(1.0), Cm(3.5), Cm(10.5)]
for i, row in enumerate(tbl.rows):
    for j, cell in enumerate(row.cells):
        cell.width = col_widths[j]
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after  = Pt(3)
        if i == 0:
            set_cell_bg(cell, '1E40AF')
            r = p.add_run(tab_data[i][j])
            r.bold = True
            r.font.color.rgb = BLANCO
            r.font.size = Pt(10)
        else:
            bg = 'EFF6FF' if i % 2 == 0 else 'FFFFFF'
            set_cell_bg(cell, bg)
            r = p.add_run(tab_data[i][j])
            if j == 1:
                r.bold = True
                r.font.color.rgb = AZUL
            r.font.size = Pt(10)

doc.add_paragraph().paragraph_format.space_after = Pt(4)

# ════════════════════════════════════════════════════════════════════════════
# SECCIÓN 3 — DETALLE DE CADA PESTAÑA
# ════════════════════════════════════════════════════════════════════════════
add_heading('3.  Guía detallada por pestaña', level=1)
add_separator()

# 3.1 Resumen
add_heading('3.1  Resumen', level=2)
add_body('Al abrir el panel, esta es la primera pantalla. Muestra cuatro tarjetas en la parte superior:')

kpi_data = [
    ('Tarjeta', 'Qué significa', 'Color'),
    ('Por Cobrar',    'Dinero que los clientes deben a la empresa',     'Azul'),
    ('Por Pagar',     'Facturas de proveedores aún sin liquidar',       'Naranja'),
    ('Vencido',       'Saldo que ya superó la fecha límite de pago',    'Rojo'),
    ('Utilidad Neta', 'Total cobrado menos el total de gastos',         'Verde'),
]
tbl2 = doc.add_table(rows=len(kpi_data), cols=3)
tbl2.style = 'Table Grid'
for i, row in enumerate(tbl2.rows):
    for j, cell in enumerate(row.cells):
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after  = Pt(3)
        if i == 0:
            set_cell_bg(cell, '374151')
            r = p.add_run(kpi_data[i][j])
            r.bold = True
            r.font.color.rgb = BLANCO
            r.font.size = Pt(10)
        else:
            set_cell_bg(cell, 'F9FAFB' if i % 2 == 0 else 'FFFFFF')
            r = p.add_run(kpi_data[i][j])
            r.font.size = Pt(10)
doc.add_paragraph().paragraph_format.space_after = Pt(4)

add_body('Cómo registrar un pago desde Resumen:', bold=True)
add_step(1, 'Busca la factura pendiente en la sección "Cuentas por Cobrar".')
add_step(2, 'Haz clic en la fila de esa factura para expandir el detalle.')
add_step(3, 'Verifica los conceptos y el monto.')
add_step(4, 'Presiona el botón verde "Marcar como pagada".')

add_tip('El saldo, los KPIs y el reporte mensual se actualizan automáticamente al guardar el pago.', icon='✅')

# 3.2 Reportes
add_heading('3.2  Reportes', level=2)
add_body('Muestra el desempeño financiero mes a mes. Pasos para usarlo:')
add_step(1, 'Selecciona el año con los botones en la esquina superior derecha.')
add_step(2, 'La gráfica de barras muestra  azul = facturado  vs  naranja = gastos.')
add_step(3, 'En la tabla mensual revisa: Sin IVA · IVA · Con IVA · Cobrado · Gastos · Utilidad.')
add_step(4, 'El mes actual aparece resaltado en azul claro.')
add_step(5, 'El renglón "Total" al final suma todo el año.')
add_step(6, 'Más abajo verás los gastos del mes actual desglosados por categoría con barras de porcentaje.')

add_tip('Para el cierre mensual: la columna "Utilidad" debe ser positiva. Si es negativa (en rojo), los gastos superaron lo cobrado ese mes.', icon='⚠️', bg='FFF7ED', border_color='FED7AA')

# 3.3 Clientes
add_heading('3.3  Clientes', level=2)
add_body('Muestra el estado de cuenta de todos los clientes.')
add_body('Cómo usarlo:', bold=True)
add_bullet('Usa el buscador para encontrar un cliente específico.')
add_bullet('Filtra por "Con vencido" para ver solo los que deben algo atrasado.')
add_bullet('La columna "Saldo Vencido" en rojo indica urgencia de cobro.')
add_bullet('Al final de la página verás las ventas facturadas del mes en curso.')

# 3.4 Inventario
add_heading('3.4  Inventario', level=2)
add_body('Muestra el valor del stock en almacén. Útil para reportes de activos.')
add_tip('Si los valores aparecen en $0.00, es porque aún no se capturan precios en el módulo Inventario → Productos. Solicítalo al encargado de almacén.', icon='📦')

# 3.5 Por Cobrar / Por Pagar
add_heading('3.5  Por Cobrar y Por Pagar', level=2)
add_body('Lista completa de todas las facturas. Puedes filtrar por estado:')
filt_data = [
    ('Estado',    'Significado'),
    ('Borrador',  'Factura creada pero no enviada al cliente'),
    ('Enviada',   'Factura enviada, esperando pago'),
    ('Vencida',   'El plazo de pago ya pasó sin recibir el total'),
    ('Pagada',    'Cobro registrado completo'),
    ('Cancelada', 'Factura anulada'),
]
tbl3 = doc.add_table(rows=len(filt_data), cols=2)
tbl3.style = 'Table Grid'
for i, row in enumerate(tbl3.rows):
    for j, cell in enumerate(row.cells):
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after  = Pt(3)
        if i == 0:
            set_cell_bg(cell, '374151')
            r = p.add_run(filt_data[i][j])
            r.bold = True
            r.font.color.rgb = BLANCO
            r.font.size = Pt(10)
        else:
            set_cell_bg(cell, 'F9FAFB' if i % 2 == 0 else 'FFFFFF')
            r = p.add_run(filt_data[i][j])
            r.font.size = Pt(10)
doc.add_paragraph().paragraph_format.space_after = Pt(4)

add_body('La columna "Antigüedad" indica cuánto tiempo lleva sin pagarse:')
add_bullet('"Al corriente" → dentro del plazo (verde)')
add_bullet('"0-30 días" → poco tiempo vencida (verde claro)')
add_bullet('"31-60 días" → requiere seguimiento (amarillo)')
add_bullet('"61-90 días" → urgente (naranja)')
add_bullet('"+90 días" → crítico, posible incobrable (rojo)')

# 3.6 Cotizaciones
add_heading('3.6  Cotizaciones', level=2)
add_body('Vista de solo lectura de las cotizaciones generadas por el equipo de ventas.')
add_tip('Para crear o editar cotizaciones: ve al menú lateral → CRM → Cotizaciones. El contador solo puede consultarlas.', icon='👁️')

# 3.7 Comprobantes
add_heading('3.7  Comprobantes', level=2)
add_body('Historial de pagos recibidos, agrupados por mes. Útil para conciliación bancaria.')
add_body('Para eliminar un pago duplicado:', bold=True)
add_step(1, 'Pasa el cursor sobre la fila del pago.')
add_step(2, 'Aparece el ícono de basura (🗑️) al extremo derecho.')
add_step(3, 'Haz clic y confirma la eliminación.')

add_tip('Solo elimina pagos si fueron registrados por error. La eliminación no se puede deshacer.', icon='⚠️', bg='FFF7ED', border_color='FED7AA')

# ════════════════════════════════════════════════════════════════════════════
# SECCIÓN 4 — MÓDULOS ADICIONALES
# ════════════════════════════════════════════════════════════════════════════
add_heading('4.  Módulos adicionales del menú', level=1)
add_separator()

mod_data = [
    ('Módulo',      'Ruta en el menú',                    'Para qué'),
    ('Facturas',    'Contabilidad → Facturas',             'Crear y editar facturas de forma manual.'),
    ('Gastos',      'Contabilidad → Gastos',              'Registrar gastos: renta, nómina, materiales, publicidad, etc.'),
    ('Cuentas',     'Contabilidad → Plan de Cuentas',     'Catálogo de cuentas contables (activos, pasivos, ingresos, etc.).'),
]
tbl4 = doc.add_table(rows=len(mod_data), cols=3)
tbl4.style = 'Table Grid'
for i, row in enumerate(tbl4.rows):
    for j, cell in enumerate(row.cells):
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after  = Pt(3)
        if i == 0:
            set_cell_bg(cell, '1E40AF')
            r = p.add_run(mod_data[i][j])
            r.bold = True
            r.font.color.rgb = BLANCO
            r.font.size = Pt(10)
        else:
            set_cell_bg(cell, 'EFF6FF' if i % 2 == 0 else 'FFFFFF')
            r = p.add_run(mod_data[i][j])
            if j == 0:
                r.bold = True
                r.font.color.rgb = AZUL
            r.font.size = Pt(10)
doc.add_paragraph().paragraph_format.space_after = Pt(4)

# ════════════════════════════════════════════════════════════════════════════
# SECCIÓN 5 — FLUJO DIARIO
# ════════════════════════════════════════════════════════════════════════════
add_heading('5.  Flujo de trabajo recomendado', level=1)
add_separator()

flow_data = [
    ('Frecuencia', 'Actividad',                                           'Dónde'),
    ('Diario',     'Revisar facturas vencidas y registrar pagos del día', 'Panel → Resumen o x Cobrar'),
    ('Diario',     'Capturar gastos del día (combustible, compras, etc.)', 'Contabilidad → Gastos'),
    ('Semanal',    'Dar seguimiento a clientes con saldo atrasado',       'Panel → Clientes'),
    ('Semanal',    'Verificar comprobantes vs estado de cuenta bancario', 'Panel → Comprobantes'),
    ('Mensual',    'Revisar reporte del mes anterior',                    'Panel → Reportes'),
    ('Mensual',    'Confirmar que cobrado = suma de comprobantes',        'Panel → Comprobantes'),
    ('Mensual',    'Exportar tabla mensual para el cierre contable',      'Panel → Reportes (imprimir)'),
]
tbl5 = doc.add_table(rows=len(flow_data), cols=3)
tbl5.style = 'Table Grid'
for i, row in enumerate(tbl5.rows):
    for j, cell in enumerate(row.cells):
        p = cell.paragraphs[0]
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after  = Pt(3)
        if i == 0:
            set_cell_bg(cell, '1E3A5F')
            r = p.add_run(flow_data[i][j])
            r.bold = True
            r.font.color.rgb = BLANCO
            r.font.size = Pt(10)
        else:
            frec = flow_data[i][0]
            bg = {'Diario': 'EFF6FF', 'Semanal': 'F0FDF4', 'Mensual': 'FFFBEB'}.get(frec, 'FFFFFF')
            set_cell_bg(cell, bg)
            r = p.add_run(flow_data[i][j])
            if j == 0:
                r.bold = True
                r.font.color.rgb = {'Diario': RGBColor(0x1D, 0x4E, 0xD8),
                                    'Semanal': RGBColor(0x15, 0x80, 0x3D),
                                    'Mensual': RGBColor(0xB4, 0x5A, 0x09)}.get(frec, NEGRO)
            r.font.size = Pt(10)
doc.add_paragraph().paragraph_format.space_after = Pt(4)

# ════════════════════════════════════════════════════════════════════════════
# SECCIÓN 6 — PREGUNTAS FRECUENTES
# ════════════════════════════════════════════════════════════════════════════
add_heading('6.  Preguntas frecuentes', level=1)
add_separator()

faqs = [
    ('¿Por qué una factura dice "Vencida" si ya pagaron?',
     'El sistema no actualiza el estado automáticamente. Entra a esa factura en la pestaña "x Cobrar", expándela y presiona "Marcar como pagada".'),
    ('¿Dónde registro la nómina quincenal?',
     'Ve a Contabilidad → Gastos → "+ Nuevo gasto". Selecciona la categoría "Salarios", anota el monto y la fecha.'),
    ('¿Cómo sé cuánto se facturó en el año?',
     'Panel Contador → Reportes → selecciona el año → revisa el renglón "Total" al final de la tabla.'),
    ('¿Puedo ver el avance de los proyectos de obra?',
     'Sí, desde el menú lateral ve a "Proyectos". El contador tiene acceso de solo lectura para consultar el estado de cada obra.'),
    ('¿Qué hago si un cliente paga de forma parcial?',
     'Entra a la factura, expándela y usa "Marcar como pagada" solo cuando el pago sea completo. Para pagos parciales, contacta al administrador para registrar un pago manual.'),
    ('¿Cómo imprimo el reporte mensual?',
     'Panel → Reportes → selecciona el año y mes → presiona Ctrl+P en el navegador para imprimir o guardar como PDF.'),
]

for q, a in faqs:
    # Pregunta
    pq = doc.add_paragraph()
    pq.paragraph_format.space_before = Pt(6)
    pq.paragraph_format.space_after  = Pt(2)
    pq.paragraph_format.left_indent  = Cm(0.3)
    rq = pq.add_run('❓  ' + q)
    rq.bold = True
    rq.font.color.rgb = AZUL
    rq.font.size = Pt(11)
    # Respuesta
    pa = doc.add_paragraph()
    pa.paragraph_format.space_before = Pt(1)
    pa.paragraph_format.space_after  = Pt(2)
    pa.paragraph_format.left_indent  = Cm(1.2)
    ra = pa.add_run(a)
    ra.font.size = Pt(10.5)
    ra.font.color.rgb = RGBColor(0x37, 0x41, 0x51)

# ════════════════════════════════════════════════════════════════════════════
# PIE DE PÁGINA
# ════════════════════════════════════════════════════════════════════════════
doc.add_paragraph().paragraph_format.space_after = Pt(10)
add_separator()

footer_p = doc.add_paragraph()
footer_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
footer_p.paragraph_format.space_before = Pt(6)
r_f = footer_p.add_run('Sistema ERP · Alfa Vidrio y Aluminio · Para soporte contactar al administrador del sistema')
r_f.font.size = Pt(9)
r_f.font.color.rgb = RGBColor(0x9C, 0xA3, 0xAF)

# ── Guardar ─────────────────────────────────────────────────────────────────
out_path = r'C:\Users\HP\Desktop\Instructivo_Contador_Alfa.docx'
doc.save(out_path)
print(f'Guardado en: {out_path}')
