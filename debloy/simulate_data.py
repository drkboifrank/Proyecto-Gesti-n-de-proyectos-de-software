"""
Simulacion de datos realistas para Alfa Vidrio y Aluminio
Periodo: Enero 2021 - Mayo 2025 (~4.5 años)
"""
import subprocess, random, uuid
from datetime import datetime, timedelta

random.seed(42)

def uid(): return str(uuid.uuid4())
def esc(s): return str(s).replace("'", "''") if s else ''
def dt(d): return d.strftime('%Y-%m-%d %H:%M:%S')
def ds(d): return d.strftime('%Y-%m-%d')
def rand_dt(a, b):
    return a + timedelta(days=random.randint(0, (b-a).days))
def rand_amount(lo, hi):
    return round(random.uniform(lo, hi), 2)
def round2(x): return round(x, 2)

START = datetime(2021, 1, 15)
END   = datetime(2025, 5, 30)

# ── IDs fijos conocidos ──────────────────────────────────────────────────────
USERS = {
    'anita':   'de4bf392-40aa-405a-b97b-ee5c2373d61b',
    'sinai':   'dbf25d07-0b51-4716-b06f-5f2b7a8da502',
    'eben':    '696b1c8e-be3e-41ae-a47b-4fb84e714737',
    'juliette':'a9d506dc-d8d6-4b9f-b6c7-684d1f8a197b',
    'fidel':   'a0f28cff-c322-421a-a12f-acdb8edec046',
    'miguel':  '1938a833-b4ad-4994-8739-5a09a1ec068a',
}
PRODUCTS = [
    {'id':'3cb6f416-0288-46f1-b6f0-f6723566f2a9','sku':'VENT-CUAD-001','name':'Ventana cuadriculada','lo':3500,'hi':8000},
    {'id':'6e44734f-392e-44ce-9851-9c9a0c96a2f8','sku':'VENT-CORR-001','name':'Ventana corrediza lisa','lo':4000,'hi':9500},
    {'id':'49557d8a-34b1-4be8-aadc-d3fcc7a729d2','sku':'PTA-ABAT-001','name':'Puerta abatible aluminio','lo':6000,'hi':14000},
    {'id':'e493c9ff-a65e-424b-b231-fb008854e327','sku':'PTA-CORR-001','name':'Puerta corrediza aluminio','lo':7000,'hi':16000},
    {'id':'656a3ba8-1c2d-4863-a28c-b1703963249f','sku':'PTA-PRIN-001','name':'Puerta principal','lo':15000,'hi':42000},
    {'id':'cba33ae7-4ed7-4100-84b7-2d3644b9292c','sku':'CANC-BANO-RECT','name':'Cancel baño recto plastico','lo':4500,'hi':9500},
    {'id':'88519d42-ca56-4b85-8af3-755b635209c2','sku':'CANC-BANO-ESC','name':'Cancel baño escuadra','lo':5200,'hi':11000},
    {'id':'2e6dce96-797a-406b-a04f-777ab0932fd1','sku':'CANC-BANO-VT','name':'Cancel vidrio templado','lo':9000,'hi':21000},
    {'id':'53a6e510-9708-46c9-915c-0e5fa8939404','sku':'CANC-BANO-BAC','name':'Cancel sistema Bacalar','lo':13000,'hi':26000},
    {'id':'e5bf37ca-d95f-4e84-af55-c64863281a8a','sku':'CANC-BANO-OAX','name':'Cancel sistema Oaxaca','lo':11000,'hi':23000},
    {'id':'4bd544dd-5455-4ef9-ba93-ea899d0d1eea','sku':'TECHO-BAS-001','name':'Techo basico aluminio','lo':20000,'hi':65000},
]
ACCTS = {
    'cash':    '4b9bef41-7030-465b-867a-de240d0f7c82',
    'ar':      '336aba48-1c04-41c6-ae62-9d03cc4d3f49',
    'revenue': '168fca67-6d43-409a-8c3d-3fbe0b6a8501',
    'svc_rev': 'a51c3937-fcd9-4077-8dfa-647271c1a2b8',
    'cogs':    '743e0f8f-0831-4b69-ad96-bdefd120b98b',
    'opex':    'd83ff731-4ab2-4a0f-8c8d-3b71f71ab954',
    'salaries':'57513892-b34b-4e9c-951e-b77fd3cbc897',
    'rent':    '05b9a847-4a88-490c-8e1e-ad160e5af92d',
}

# ── Ejecutar SQL en contenedor ───────────────────────────────────────────────
def run_sql(container, dbname, sql):
    proc = subprocess.run(
        ['docker','exec','-i', container,'psql','-U','erp','-d',dbname],
        input=sql.encode('utf-8'),
        capture_output=True
    )
    if proc.returncode != 0:
        print(f"ERROR en {container}/{dbname}:")
        print(proc.stderr.decode('utf-8')[:500])
    else:
        print(f"OK {container}/{dbname}: {proc.stdout.decode('utf-8').strip()[:120]}")

# ════════════════════════════════════════════════════════════════════════════
#  1. LIMPIAR datos de prueba viejos (no los productos reales ni usuarios)
# ════════════════════════════════════════════════════════════════════════════
print("=== Limpiando datos de prueba ===")
clean_crm = """
DELETE FROM report_entries;
DELETE FROM daily_reports;
DELETE FROM project_evidencias;
DELETE FROM project_checklist_items;
DELETE FROM project_bitacora;
DELETE FROM project_expenses;
DELETE FROM project_workers;
DELETE FROM projects;
DELETE FROM sales_order_lines;
DELETE FROM sales_orders;
DELETE FROM quote_lines;
DELETE FROM quotes;
DELETE FROM opportunities;
DELETE FROM marketing_tasks;
DELETE FROM calendar_events;
DELETE FROM delivery_note_lines;
DELETE FROM delivery_notes;
DELETE FROM workers;
DELETE FROM customers;
"""
clean_inv = """
DELETE FROM purchase_order_items;
DELETE FROM purchase_orders;
DELETE FROM stock_movements;
DELETE FROM stock_lines;
DELETE FROM warehouses;
DELETE FROM suppliers;
DELETE FROM products WHERE sku IN ('234wa','3r5','PROD-1779393750048','PROD-1779465009416','PROD-1779468985492','erttgf');
"""
clean_acc = """
DELETE FROM payments;
DELETE FROM invoice_lines;
DELETE FROM invoices;
DELETE FROM journal_lines;
DELETE FROM journal_entries;
DELETE FROM expenses;
"""
run_sql('alfa20-db-crm-1',       'crm_db',       clean_crm)
run_sql('alfa20-db-inventory-1', 'inventory_db',  clean_inv)
run_sql('alfa20-db-accounting-1','accounting_db', clean_acc)

# ════════════════════════════════════════════════════════════════════════════
#  2. CRM — WORKERS
# ════════════════════════════════════════════════════════════════════════════
print("\n=== Workers ===")
WID = {
    'carlos':   uid(), 'roberto': uid(), 'jose':     uid(),
    'fernando': uid(), 'luis':    uid(), 'mario':    uid(), 'pedro': uid(),
}
workers_sql = f"""
INSERT INTO workers(id,name,phone,trade,active,created_at) VALUES
 ('{WID["carlos"]}', 'Carlos Mendez Tzuc',    '9981234501', 'Fabricador/Instalador', true, '2021-01-15 08:00:00'),
 ('{WID["roberto"]}','Roberto Dzul Chan',      '9981234502', 'Fabricador',            true, '2021-01-15 08:00:00'),
 ('{WID["jose"]}',   'Jose Tun Uicab',         '9981234503', 'Instalador',            true, '2021-02-01 08:00:00'),
 ('{WID["fernando"]}','Fernando Ek Cauich',    '9981234504', 'Instalador',            true, '2022-03-01 08:00:00'),
 ('{WID["luis"]}',   'Luis Canul Poot',        '9981234505', 'Fabricador',            true, '2022-04-01 08:00:00'),
 ('{WID["mario"]}',  'Mario Poot Sosa',        '9981234506', 'Instalador',            true, '2023-01-10 08:00:00'),
 ('{WID["pedro"]}',  'Pedro Balam Chan',       '9981234507', 'Fabricador',            true, '2023-06-01 08:00:00');
"""
run_sql('alfa20-db-crm-1', 'crm_db', workers_sql)

# ════════════════════════════════════════════════════════════════════════════
#  3. INVENTORY — Warehouse + Suppliers
# ════════════════════════════════════════════════════════════════════════════
print("\n=== Almacen + Proveedores ===")
WH_ID = uid()
S_IDS = [uid(), uid(), uid(), uid()]
inv_setup = f"""
INSERT INTO warehouses(id,name,address,is_active) VALUES
 ('{WH_ID}','Almacen Principal Cancun','Av. Kabah Mz 10 Lt 5, SM 64, Cancun QR',true);

INSERT INTO suppliers(id,name,contact_name,email,phone,address,tax_id,notes,is_active,created_at,updated_at) VALUES
 ('{S_IDS[0]}','ALMEXA Aluminio','Jorge Herrera','ventas@almexa.mx','8001234001',
  'Av. Industrial 450, Guadalajara Jal','ALM-010101-AAA',
  'Proveedor principal de perfiles de aluminio. Credito 30 dias.',true,
  '2021-01-20 09:00:00','2021-01-20 09:00:00'),
 ('{S_IDS[1]}','Vitro Vidrio Industrial','Ana Perez','ventas@vitro.mx','8001234002',
  'Av. Revolucion 1200, Monterrey NL','VIT-020202-BBB',
  'Proveedor de vidrio float y templado. Entrega en 5 dias habiles.',true,
  '2021-01-20 09:00:00','2021-01-20 09:00:00'),
 ('{S_IDS[2]}','Ferreteria Cancun Sur','Pedro May','ferrecanc@gmail.com','9981234003',
  'Av. Tulum 305, SM 14, Cancun QR','FCS-030303-CCC',
  'Herrajes, tornilleria y consumibles locales. Credito 15 dias.',true,
  '2021-02-01 09:00:00','2021-02-01 09:00:00'),
 ('{S_IDS[3]}','Perfiles y Extrusiones del Caribe','Luis Cetina','ventas@pecsa.mx','9981234004',
  'Carretera Cancun-Merida Km 12, QR','PEC-040404-DDD',
  'Perfiles especiales y laminas de aluminio. Entrega rapida en QRoo.',true,
  '2022-06-01 09:00:00','2022-06-01 09:00:00');
"""
run_sql('alfa20-db-inventory-1', 'inventory_db', inv_setup)

# Stock inicial en almacen para los productos existentes
stock_sql = ""
for p in PRODUCTS:
    sl_id = uid()
    qty = random.randint(3, 18)
    stock_sql += f"""
INSERT INTO stock_lines(id,product_id,warehouse_id,quantity,updated_at)
VALUES('{sl_id}','{p["id"]}','{WH_ID}',{qty},'2025-01-01 08:00:00')
ON CONFLICT DO NOTHING;
"""
run_sql('alfa20-db-inventory-1', 'inventory_db', stock_sql)

# ════════════════════════════════════════════════════════════════════════════
#  4. CRM — CLIENTES (50 clientes realistas Cancun/Riviera Maya)
# ════════════════════════════════════════════════════════════════════════════
print("\n=== Clientes ===")
raw_customers = [
    # (nombre, tipo, email, telefono, ciudad, direccion, rfc, notas)
    ("Constructora Caribe S.A. de C.V.",'company','contacto@ccaribe.mx','9981100001','Cancun',
     'Av. Bonampak 201 OF 302, SM 6, Cancun QR','CCB-880510-AA1',
     'Constructora hotelera. Proyectos grandes. Pago 50% anticipo.'),
    ("Hotel Krystal Grand Cancun",'company','compras@krystalgrand.mx','9981100002','Cancun',
     'Blvd. Kukulcan Km 9.5, Zona Hotelera, Cancun QR','HKG-920301-BB2',
     'Hotel 5 estrellas. Mantenimiento anual de canceles.'),
    ("Inmobiliaria Peninsula S.A.",'company','obras@peninsula.mx','9981100003','Cancun',
     'Av. Cobá 12 PH, SM 20, Cancun QR','IPE-001215-CC3',
     'Desarrolladora de condominios. Cliente frecuente.'),
    ("Juan Carlos Molina Pérez",'individual','jcmolina@gmail.com','9981200001','Cancun',
     'Calle Nispero 45 SM 502, Cancun QR',None,'Residencia particular. Muy puntual en pagos.'),
    ("María Fernanda Ruiz",'individual','mfruiz@hotmail.com','9981200002','Cancun',
     'Av. Huayacan Mz 8 Lt 12, Cancun QR',None,'Casa en fraccionamiento. Referida por Carlos Molina.'),
    ("Restaurante La Habichuela",'company','admin@habichuela.com.mx','9981100004','Cancun',
     'Margaritas 25, SM 22, Cancun QR','RLH-851120-DD4',
     'Renovacion de fachada. Cliente desde 2021.'),
    ("Desarrollos Riviera Maya S.A.",'company','ing.obras@drm.mx','9981100005','Playa del Carmen',
     'Av. 10 Norte 245, Playa del Carmen QR','DRM-970605-EE5',
     'Constructora de residencias premium. Alta frecuencia.'),
    ("Marco Antonio Cetina Dzul",'individual','macetina@gmail.com','9841200001','Playa del Carmen',
     'Calle Flamingo 88, PDC QR',None,'Casa propia. Solicita factura siempre.'),
    ("Corporativo Sunset Hotels",'company','procurement@sunsethotels.mx','9981100006','Cancun',
     'Blvd. Kukulcan Km 14.5, ZH Cancun QR','CSH-010820-FF6',
     'Cadena de 3 hoteles. Pago a 45 dias.'),
    ("Patricia Hernandez Vega",'individual','patriher@gmail.com','9981200003','Cancun',
     'Sm 507 Mz 12 Lt 3, Cancun QR',None,'Residencia. Solicito cancel baño y ventanas.'),
    ("Grupo Constructor Riviera",'company','gerencia@gcriviera.mx','9981100007','Cancun',
     'Av. Nichupte 320, SM 44, Cancun QR','GCR-030210-GG7',
     'Constructora mediana. Proyectos en colonias residenciales.'),
    ("Roberto Sansores May",'individual','rsansores@outlook.com','9981200004','Cancun',
     'Calle Laurel 22, Fracc. Las Palmas, Cancun QR',None,'Ampliacion de casa. Buen cliente.'),
    ("Spa & Wellness Tulum",'company','contacto@spawellnesstulum.mx','9841100001','Tulum',
     'Carr. Tulum-Coba Km 2.5, Tulum QR','SWT-150301-HH8',
     'Canceles y ventanas para spa. Proyectos de lujo.'),
    ("Irma Consuelo Balam Chan",'individual','ibalam@gmail.com','9981200005','Cancun',
     'SM 92 Mz 5 Lt 8, Cancun QR',None,'Segunda vivienda. Paga al contado.'),
    ("Constructora MH Group",'company','obras@mhgroup.mx','9981100008','Cancun',
     'Av. Kabah 45 OF 12, SM 64, Cancun QR','MHG-120405-II9',
     'Constructora local. Muchos proyectos residenciales.'),
    ("Carlos Alberto Tun Pech",'individual','catun@hotmail.com','9981200006','Cancun',
     'Calle Orquidea 15, SM 59, Cancun QR',None,'Negocio local. Cancel de oficina.'),
    ("Villas del Mar S.A. de C.V.",'company','admin@villasdel mar.mx','9981100009','Puerto Morelos',
     'Av. Rojo Gomez 205, Puerto Morelos QR','VDM-040720-JJ0',
     'Fraccionamiento de villas. 20-30 unidades por lote.'),
    ("Ana Lucía Dzul Cauich",'individual','alucia.dzul@gmail.com','9981200007','Cancun',
     'SM 308 Mz 3 Lt 4, Cancun QR',None,'Cocina integral y canceleria baño.'),
    ("Hotel Boutique Azul",'company','recepcion@hotelazul.mx','9841100002','Isla Mujeres',
     'Hidalgo 85, Isla Mujeres QR','HBA-990910-KK1',
     'Pequeño hotel boutique. Renovacion cada 3 años.'),
    ("Luis Fernando Ek May",'individual','lfek@gmail.com','9981200008','Cancun',
     'Av. Lopez Portillo Km 3, SM 75, Cancun QR',None,'Taller mecanico. Puerta industrial.'),
    ("Condominios Coral S.A.",'company','administracion@condcoral.mx','9981100010','Cancun',
     'Blvd. Kukulcan Km 5, ZH Cancun QR','CCS-061115-LL2',
     'Condominio residencial 120 dptos. Contrato de mantenimiento anual.'),
    ("Jorge Emilio Canul Poot",'individual','jecanul@yahoo.com.mx','9841200002','Playa del Carmen',
     'Calle 14 Norte 320, PDC QR',None,'Restaurante. Fachada de aluminio y vidrio.'),
    ("Arq. Sofia Mendez Torres",'individual','arq.sofia@gmail.com','9981200009','Cancun',
     'SM 25 Mz 6 Lt 10, Cancun QR',None,'Arquitecta. Proyectos de clientes propios. Contacto clave.'),
    ("Grupo Inmobiliario Xcaret",'company','compras@xcaret-group.mx','9841100003','Playa del Carmen',
     'Av. 30 Sur 750, PDC QR','GIX-010101-MM3',
     'Gran desarrolladora. Pedidos masivos cada 6 meses.'),
    ("Miguel Angel Poot Chan",'individual','mapoot@gmail.com','9981200010','Cancun',
     'SM 521 Mz 11 Lt 2, Cancun QR',None,'Casa nueva. Todas las ventanas y puertas.'),
    ("Ferretería y Herrajes del Sureste",'company','ventas@fhsureste.mx','9981100011','Cancun',
     'Av. Tulum 180, SM 14, Cancun QR','FHS-880201-NN4',
     'Compra material para reventa. Descuento acordado 8%.'),
    ("Beatriz Elena Chable May",'individual','bchable@hotmail.com','9981200011','Cancun',
     'Calle Gladiola 33, SM 63, Cancun QR',None,'Casa remodelacion. Cancel y ventanas.'),
    ("Resort & Spa Bahia Principe",'company','mantenimiento@bahiaprincipe.mx','9981100012','Akumal',
     'Carr. Chetumal-Pto Juarez Km 250, Akumal QR','RSB-940505-OO5',
     'Resort 5 estrellas. Contratos anuales de mantenimiento.'),
    ("Ernesto Villanueva Chi",'individual','evillanueva@gmail.com','9981200012','Cancun',
     'SM 314 Mz 2 Lt 5, Cancun QR',None,'Oficina contable. Canceleria interior.'),
    ("Desarrolladora Costa Mujeres",'company','proyectos@costamujeres.mx','9981100013','Cancun',
     'Av. Bonampak 505 OF 801, Cancun QR','DCM-080320-PP6',
     'Zona nueva norte Cancun. Alto crecimiento.'),
    ("Claudia Patricia Uicab Tun",'individual','cpuicab@gmail.com','9981200013','Cancun',
     'SM 508 Mz 9 Lt 7, Cancun QR',None,'Residencia. Techo de aluminio para patio.'),
    ("Constructor Independiente Ramirez",'individual','j.ramirez.const@gmail.com','9841200003','Playa del Carmen',
     'Calle 38 Sur 125, PDC QR',None,'Maestro de obra independiente. Compra para sus clientes.'),
    ("Hotel Fiesta Inn Cancun",'company','compras@fiestainn-cancun.mx','9981100014','Cancun',
     'Av. Tulum 26 SM 4, Cancun QR','HFI-870615-QQ7',
     'Hotel de negocios. Renovacion por fases.'),
    ("Enrique de la Cruz Sosa",'individual','edelacruz@gmail.com','9981200014','Cancun',
     'SM 44 Mz 7 Lt 14, Cancun QR',None,'Casa ampliacion. Sala de tv con cancel.'),
    ("Centro Comercial Malecón Americas",'company','admin@maleconamericas.mx','9981100015','Cancun',
     'Av. Bonampak esq. Nichupte, SM 4, Cancun QR','CMA-030808-RR8',
     'Centro comercial. Locales comerciales y mantenimiento.'),
    ("Norma Edith Cauich Balam",'individual','necauich@gmail.com','9981200015','Cancun',
     'SM 59 Mz 3 Lt 1, Cancun QR',None,'Primera compra. Canceleria baño nuevo.'),
    ("Inversiones Turísticas del Caribe",'company','finanzas@itcaribe.mx','9981100016','Cancun',
     'Blvd. Kukulcan Km 8, ZH Cancun QR','ITC-020218-SS9',
     'Fondo de inversión inmobiliaria. Proyecto Zona Hotelera.'),
    ("Pedro José Moo Dzib",'individual','pjmoo@hotmail.com','9841200004','Cancun',
     'SM 73 Mz 15 Lt 8, Cancun QR',None,'Panaderia. Mostrador de vidrio y aluminio.'),
    ("Arquitectos Asociados Rivera",'company','proyectos@aarst.mx','9981100017','Cancun',
     'Av. Sayil 350 OF 5, SM 26, Cancun QR','AAR-050405-TT0',
     'Despacho de arquitectura. Subcontratamos para sus proyectos.'),
    ("Gloria Marina Tzuc Chan",'individual','gloritzuc@gmail.com','9981200016','Cancun',
     'SM 524 Mz 6 Lt 3, Cancun QR',None,'Casa propia. Puerta principal y ventanas.'),
    ("Oficinas Corporativas Cancun",'company','facilities@ofc-cancun.mx','9981100018','Cancun',
     'Av. Cobá 452 OF 1202, SM 20, Cancun QR','OCC-060910-UU1',
     'Torre de oficinas. Canceleria de vidrio para salas de juntas.'),
    ("Fernando Alberto Chi Pool",'individual','fachi@gmail.com','9981200017','Cancun',
     'SM 513 Mz 4 Lt 6, Cancun QR',None,'Remodelacion completa.'),
    ("Residencias El Palmar S.A.",'company','obra@elpalmar.mx','9981100019','Cancun',
     'Av. Huayacan Mz 1 Lt 1, Cancun QR','REP-100115-VV2',
     'Fraccionamiento 60 casas. Contrato global por fases.'),
    ("Mariana Gpe. Sansores Ek",'individual','msansores@gmail.com','9981200018','Cancun',
     'SM 516 Mz 8 Lt 12, Cancun QR',None,'Cancel de baño y ventana recamara.'),
    ("Taller Mecanico Kukulcan",'individual','tmkukulcan@gmail.com','9981200019','Cancun',
     'Av. Lopez Portillo 850, SM 68, Cancun QR',None,'Puerta enrollable de aluminio.'),
    ("Constructora Punta Norte",'company','licitaciones@puntanorte.mx','9981100020','Cancun',
     'Av. Colosio Km 8.5, SM 307, Cancun QR','CPN-110520-WW3',
     'Zona norte Cancun. Casas de interes medio.'),
    ("Isabel Cristina Pool Tun",'individual','icrool@hotmail.com','9981200020','Cancun',
     'SM 529 Mz 2 Lt 9, Cancun QR',None,'Casa nueva. Ventanas sala y recamaras.'),
    ("Clinica Dental Smile Plus",'company','admin@smileplus.mx','9981100021','Cancun',
     'Av. Kabah 215 Local 3, SM 33, Cancun QR','CDS-130605-XX4',
     'Clinica dental. Cancel de vidrio para consultorios.'),
    ("Alicia Beatriz May Caamal",'individual','abmay@gmail.com','9981200021','Cancun',
     'SM 97 Mz 7 Lt 15, Cancun QR',None,'Azotea. Techo de aluminio y cancel.'),
    ("Grupo Hotelero Poseidon",'company','mantenimiento@ghposeidon.mx','9981100022','Cancun',
     'Blvd. Kukulcan Km 17, ZH Cancun QR','GHP-920830-YY5',
     'Cadena de 2 hoteles. Reemplazo de ventanas por temporadas.'),
]

CID = {}  # customer_name -> uuid
customers_sql = ""
for i, c in enumerate(raw_customers):
    name, ctype, email, phone, city, addr, rfc, notes = c
    cid = uid()
    CID[name] = cid
    created = rand_dt(START, datetime(2021, 12, 31))
    rfc_val = f"'{esc(rfc)}'" if rfc else 'NULL'
    customers_sql += f"""
INSERT INTO customers(id,name,customer_type,email,phone,address,city,country,tax_id,notes,created_at,updated_at,created_by_id)
VALUES('{cid}','{esc(name)}','{ctype}','{esc(email)}','{esc(phone)}',
       '{esc(addr)}','{esc(city)}','Mexico',{rfc_val},'{esc(notes)}',
       '{dt(created)}','{dt(created)}','{USERS["anita"]}');
"""

run_sql('alfa20-db-crm-1', 'crm_db', customers_sql)
customer_ids = list(CID.values())

# ════════════════════════════════════════════════════════════════════════════
#  5. CRM — COTIZACIONES + PEDIDOS + PROYECTOS
# ════════════════════════════════════════════════════════════════════════════
print("\n=== Cotizaciones, Pedidos, Proyectos ===")

project_statuses_by_year = {
    2021: ['entregado','garantia'],
    2022: ['entregado','garantia','cancelado'],
    2023: ['entregado','garantia'],
    2024: ['entregado','instalando','fabricando','garantia'],
    2025: ['cotizado','confirmado','fabricando','instalando','entregado'],
}
proj_status_now = {
    'entregado': 'entregado',
    'garantia': 'garantia',
    'instalando': 'instalando',
    'fabricando': 'fabricando',
    'confirmado': 'confirmado',
    'cotizado': 'cotizado',
    'cancelado': 'cancelado',
}

# Meses con mas actividad (temporada alta Nov-Apr)
def month_weight(m):
    return 1.6 if m in [11,12,1,2,3,4] else 1.0

sellers = ['Anita', 'Sinai']
seller_ids = [USERS['anita'], USERS['sinai']]
proj_types = [
    ('Canceleria de baño','cancel'),
    ('Ventanas sala y comedor','ventanas'),
    ('Puerta principal y lateral','puertas'),
    ('Techo de patio','techo'),
    ('Cancel y ventanas recamara','mixto'),
    ('Canceleria completa','cancel'),
    ('Ventanas y puertas residencial','mixto'),
    ('Puerta corrediza terraza','puertas'),
    ('Canceleria de baño maestro','cancel'),
    ('Ventanales sala','ventanas'),
    ('Fachada aluminio y vidrio','fachada'),
    ('Cancel vidrio templado','cancel'),
    ('Canceleria baño y ventanas','mixto'),
    ('Techo aluminio y cristal','techo'),
    ('Ventanas corredizas recamaras','ventanas'),
]
cancun_colonias = [
    'SM 502 Mz 5 Lt 3, Cancun QR',
    'SM 507 Mz 8 Lt 12, Cancun QR',
    'SM 59 Mz 3 Lt 7, Cancun QR',
    'SM 44 Mz 11 Lt 1, Cancun QR',
    'Fracc. Las Palmas, Cancun QR',
    'SM 524 Mz 4 Lt 9, Cancun QR',
    'SM 92 Mz 6 Lt 2, Cancun QR',
    'Av. Huayacan Mz 2 Lt 5, Cancun QR',
    'SM 308 Mz 1 Lt 8, Cancun QR',
    'SM 316 Mz 9 Lt 4, Cancun QR',
    'Calle Flamingo 45, PDC QR',
    'Av. 10 Norte 380, PDC QR',
    'Carr. Puerto Morelos Km 15, QR',
    'SM 64 Mz 7 Lt 11, Cancun QR',
    'Blvd. Bahia 20, Cancun QR',
]

# Notas de bitacora realistas
bitacora_templates = [
    ('proyecto_creado', 'Proyecto creado. Se confirmo anticipo del 50%.'),
    ('fabricacion', 'Se inicia fabricacion de perfiles. Material en almacen.'),
    ('fabricacion', 'Corte de aluminio completado. En proceso de ensamble.'),
    ('fabricacion', 'Fabricacion de marcos terminada. Pendiente instalacion de vidrio.'),
    ('fabricacion', 'Vidrio instalado en marcos. Revision de medidas OK.'),
    ('instalacion', 'Equipo de instalacion asignado. Confirmada visita con cliente.'),
    ('instalacion', 'Instalacion iniciada. Preparacion de vanos en obra.'),
    ('instalacion', 'Instalacion al 60%. Pendiente ajuste de herrajes.'),
    ('instalacion', 'Instalacion completada. Limpieza de obra realizada.'),
    ('entrega', 'Obra entregada al cliente. Firma de conformidad obtenida.'),
    ('pago', 'Se recibio pago de finiquito. Transferencia bancaria confirmada.'),
    ('garantia', 'Cliente reporto ajuste en cancel. Tecnico enviado el mismo dia.'),
    ('visita', 'Visita de medicion realizada. Confirmadas dimensiones del proyecto.'),
    ('nota', 'Cliente solicito cambio de color a blanco colonial. Ajustado en pedido.'),
    ('nota', 'Coordinacion con cliente para fecha de instalacion confirmada.'),
]

quotes_sql = ""
orders_sql = ""
order_lines_sql = ""
projects_sql = ""
proj_workers_sql = ""
bitacora_sql = ""
proj_expenses_sql = ""
quote_lines_sql = ""

quote_counter = 100
order_counter = 100

all_order_ids = []  # list of (order_id, order_number, total, customer_id, created_date, project_id)

# Generar ~260 cotizaciones en 4.5 años
# Distribuir por mes con pesos de temporada
months_range = []
cur = datetime(2021, 1, 1)
while cur <= datetime(2025, 5, 1):
    w = month_weight(cur.month)
    # base 4-6 quotes/month
    n = int(random.gauss(5, 1.5) * w)
    n = max(1, min(n, 10))
    months_range.append((cur, n))
    cur = (cur.replace(day=1) + timedelta(days=32)).replace(day=1)

for (month_dt, nquotes) in months_range:
    year = month_dt.year
    for _ in range(nquotes):
        qid = uid()
        quote_counter += 1
        qnum = f"COT-{year}-{str(quote_counter).zfill(4)}"
        cid = random.choice(customer_ids)
        q_date = rand_dt(month_dt, min(month_dt + timedelta(days=28), END))
        seller_name, seller_uid = random.choice(list(zip(sellers, seller_ids)))

        # Lineas de cotizacion: 1-4 productos
        n_lines = random.randint(1, 4)
        subtotal = 0.0
        for li in range(n_lines):
            p = random.choice(PRODUCTS)
            qty = random.randint(1, 3)
            unit_price = round(random.uniform(p['lo'], p['hi']), 2)
            line_total = round(qty * unit_price, 2)
            subtotal += line_total
            ql_id = uid()
            quote_lines_sql += f"""
INSERT INTO quote_lines(id,quote_id,product_id,description,quantity,unit_price,total_price)
VALUES('{ql_id}','{qid}','{p["id"]}','{esc(p["name"])}',{qty},{unit_price},{line_total});
"""
        subtotal = round2(subtotal)
        tax = round2(subtotal * 0.16)
        total = round2(subtotal + tax)
        valid = q_date + timedelta(days=30)

        # Status: 70% aceptadas si en 2021-2024, 50% en 2025
        r = random.random()
        if year <= 2023:
            if r < 0.62: qstatus = 'accepted'
            elif r < 0.80: qstatus = 'sent'
            elif r < 0.90: qstatus = 'rejected'
            elif r < 0.95: qstatus = 'expired'
            else: qstatus = 'draft'
        elif year == 2024:
            if r < 0.58: qstatus = 'accepted'
            elif r < 0.75: qstatus = 'sent'
            elif r < 0.88: qstatus = 'rejected'
            else: qstatus = 'expired'
        else:  # 2025
            if r < 0.40: qstatus = 'accepted'
            elif r < 0.65: qstatus = 'sent'
            elif r < 0.80: qstatus = 'draft'
            else: qstatus = 'rejected'

        pt = random.choice(['50% anticipo, 50% contra entrega',
                             '70% anticipo, 30% instalacion',
                             '100% al inicio',
                             '40% anticipo, 60% entrega'])
        quotes_sql += f"""
INSERT INTO quotes(id,number,customer_id,status,valid_until,subtotal,tax_amount,total,
                   payment_terms,assigned_to_id,assigned_to_name,with_tax,created_at)
VALUES('{qid}','{qnum}','{cid}','{qstatus}','{dt(valid)}',
       {subtotal},{tax},{total},'{esc(pt)}',
       '{seller_uid}','{seller_name}',true,'{dt(q_date)}');
"""

        if qstatus != 'accepted':
            continue

        # ── Pedido ────────────────────────────────────────────────────────
        order_counter += 1
        oid = uid()
        onum = f"PED-{year}-{str(order_counter).zfill(4)}"
        o_date = q_date + timedelta(days=random.randint(1, 5))

        # Status del pedido segun año
        if year <= 2022:
            ostatus = random.choice(['delivered','delivered','delivered','shipped','cancelled'])
        elif year == 2023:
            ostatus = random.choice(['delivered','delivered','delivered','shipped'])
        elif year == 2024:
            ostatus = random.choice(['delivered','delivered','shipped','processing','confirmed'])
        else:
            ostatus = random.choice(['confirmed','processing','draft','confirmed'])

        orders_sql += f"""
INSERT INTO sales_orders(id,number,customer_id,quote_id,status,subtotal,tax_amount,total,
                          assigned_to_id,assigned_to_name,created_at,updated_at)
VALUES('{oid}','{onum}','{cid}','{qid}','{ostatus}',
       {subtotal},{tax},{total},
       '{seller_uid}','{seller_name}','{dt(o_date)}','{dt(o_date)}');
"""
        # lineas de orden = mismas que cotizacion aproximado
        for li in range(n_lines):
            p = random.choice(PRODUCTS)
            qty = random.randint(1, 3)
            up = round(random.uniform(p['lo'], p['hi']), 2)
            lt = round2(qty * up)
            ol_id = uid()
            order_lines_sql += f"""
INSERT INTO sales_order_lines(id,order_id,product_id,description,quantity,unit_price,total_price)
VALUES('{ol_id}','{oid}','{p["id"]}','{esc(p["name"])}',{qty},{up},{lt});
"""

        # ── Proyecto ──────────────────────────────────────────────────────
        if ostatus in ('cancelled','draft') and random.random() < 0.7:
            all_order_ids.append((oid, onum, total, cid, o_date, None))
            continue

        pid = uid()
        pname, ptype = random.choice(proj_types)
        addr = random.choice(cancun_colonias)
        p_start = o_date + timedelta(days=random.randint(3, 14))

        if year <= 2023:
            pstatus = random.choice(['entregado','entregado','garantia','entregado'])
            p_end = p_start + timedelta(days=random.randint(10, 45))
            closed = p_end + timedelta(days=random.randint(1, 5))
        elif year == 2024:
            if month_dt.month <= 9:
                pstatus = random.choice(['entregado','garantia','entregado'])
                p_end = p_start + timedelta(days=random.randint(8, 40))
                closed = p_end + timedelta(days=2)
            else:
                pstatus = random.choice(['entregado','instalando','fabricando'])
                p_end = p_start + timedelta(days=random.randint(15, 50))
                closed = None
        else:  # 2025
            pstatus = random.choice(['cotizado','confirmado','fabricando','instalando','entregado'])
            p_end = p_start + timedelta(days=random.randint(10, 35))
            closed = p_end if pstatus == 'entregado' else None

        priority = random.choice(['baja','media','media','alta'])
        advance = round2(total * random.choice([0.40, 0.50, 0.50, 0.70]))
        fab_dt_val = 'NULL' if pstatus == 'cotizado' else f"'{ds(p_start + timedelta(days=3))}'"
        del_dt_val = 'NULL' if pstatus in ('cotizado','confirmado') else f"'{ds(p_end)}'"
        closed_val = f"'{ds(closed)}'" if closed else 'NULL'
        warranty = random.choice([6, 12, 12, 24])

        colors = ['Natural','Blanco colonial','Negro mate','Bronze','Champagne','Blanco brillante']
        color = random.choice(colors)
        fab_names = random.choice(['Carlos Mendez', 'Roberto Dzul', 'Carlos Mendez, Roberto Dzul',
                                    'Luis Canul', 'Pedro Balam', 'Luis Canul, Pedro Balam'])
        inst_names = random.choice(['Jose Tun', 'Fernando Ek', 'Mario Poot',
                                     'Jose Tun, Fernando Ek', 'Fernando Ek, Mario Poot'])
        pmethods = ['transfer','transfer','transfer','cash','card']
        pm = random.choice(pmethods)
        banks = ['BBVA','Banorte','HSBC','Santander','Banamex']
        pbank = random.choice(banks) if pm == 'transfer' else 'NULL_BANK'

        projects_sql += f"""
INSERT INTO projects(id,name,customer_id,quote_number,status,address,start_date,end_date,
                     created_at,updated_at,order_id,priority,color_spec,
                     total_amount,advance_amount,fabrication_date,delivery_date,closed_date,
                     fabricator_names,installer_names,payment_method,payment_bank,warranty_months)
VALUES('{pid}','{esc(pname)}','{cid}','{qnum}','{pstatus}',
       '{esc(addr)}','{dt(p_start)}','{dt(p_end)}',
       '{dt(o_date)}','{dt(o_date)}','{oid}','{priority}','{esc(color)}',
       {total},{advance},{fab_dt_val},{del_dt_val},{closed_val},
       '{esc(fab_names)}','{esc(inst_names)}','{pm}','{esc(pbank)}',{warranty});
"""

        # Asignar workers al proyecto
        fab_workers = [WID['carlos'], WID['roberto'], WID['luis'], WID['pedro']]
        ins_workers = [WID['jose'], WID['fernando'], WID['mario']]
        n_fab = random.randint(1, 2)
        n_ins = random.randint(1, 2)
        used_workers = set()
        for wk in random.sample(fab_workers, min(n_fab, len(fab_workers))):
            if wk not in used_workers:
                proj_workers_sql += f"""
INSERT INTO project_workers(id,project_id,worker_id,role)
VALUES('{uid()}','{pid}','{wk}','fabricador');
"""
                used_workers.add(wk)
        for wk in random.sample(ins_workers, min(n_ins, len(ins_workers))):
            if wk not in used_workers:
                proj_workers_sql += f"""
INSERT INTO project_workers(id,project_id,worker_id,role)
VALUES('{uid()}','{pid}','{wk}','instalador');
"""
                used_workers.add(wk)

        # Bitacora (2-5 entradas segun status)
        bita_events = [
            (o_date, 'proyecto_creado', f'Proyecto creado desde pedido {onum}. Anticipo de ${advance:,.0f} recibido.', 'sistema'),
        ]
        if pstatus not in ('cotizado',):
            d = p_start
            bita_events.append((d, 'fabricacion', 'Medicion en obra completada. Se confirman dimensiones del proyecto.', 'supervisor'))
            d += timedelta(days=2)
            bita_events.append((d, 'fabricacion', f'Inicio de fabricacion. Color: {color}. Perfiles solicitados a almacen.', 'supervisor'))
        if pstatus in ('instalando','entregado','garantia'):
            d = p_start + timedelta(days=random.randint(5, 12))
            bita_events.append((d, 'fabricacion', 'Fabricacion completada. Material listo para instalacion.', 'supervisor'))
            d += timedelta(days=2)
            bita_events.append((d, 'instalacion', f'Instalacion iniciada. Equipo: {inst_names}.', 'supervisor'))
        if pstatus in ('entregado','garantia'):
            d = p_end - timedelta(days=1)
            bita_events.append((d, 'instalacion', 'Instalacion finalizada. Limpieza de obra y revision con cliente.', 'supervisor'))
            bita_events.append((p_end, 'entrega', f'Obra entregada. Cliente conforme. Finiquito de ${total-advance:,.0f} recibido.', 'supervisor'))
        if pstatus == 'garantia' and year < 2025:
            d = p_end + timedelta(days=random.randint(30, 120))
            bita_events.append((d, 'garantia', 'Llamada de seguimiento. Cliente satisfecho con el trabajo.', 'vendedor'))

        for bev_date, bact, bdet, btype in bita_events:
            bitacora_sql += f"""
INSERT INTO project_bitacora(id,project_id,user_name,action,details,created_at,activity_type)
VALUES('{uid()}','{pid}','Eben Supervision','{esc(bact)}','{esc(bdet)}','{dt(bev_date)}','{btype}');
"""

        # Gastos del proyecto (materiales, mano de obra)
        if pstatus not in ('cotizado','confirmado'):
            mat_cost = round2(total * random.uniform(0.28, 0.38))
            mano_cost = round2(total * random.uniform(0.12, 0.18))
            proj_expenses_sql += f"""
INSERT INTO project_expenses(id,project_id,category,description,amount,expense_date,created_by,created_at)
VALUES('{uid()}','{pid}','materiales','Perfiles de aluminio, vidrio y herrajes para {esc(pname)}',
       {mat_cost},'{dt(p_start + timedelta(days=1))}','Eben Supervision','{dt(p_start + timedelta(days=1))}');
INSERT INTO project_expenses(id,project_id,category,description,amount,expense_date,created_by,created_at)
VALUES('{uid()}','{pid}','mano_obra','Pago de fabricacion e instalacion de {esc(pname)}',
       {mano_cost},'{dt(p_start + timedelta(days=7))}','Eben Supervision','{dt(p_start + timedelta(days=7))}');
"""
            if random.random() < 0.3:
                extra = round2(total * random.uniform(0.02, 0.05))
                proj_expenses_sql += f"""
INSERT INTO project_expenses(id,project_id,category,description,amount,expense_date,created_by,created_at)
VALUES('{uid()}','{pid}','transporte','Flete y transporte de materiales a obra',
       {extra},'{dt(p_start + timedelta(days=3))}','Eben Supervision','{dt(p_start + timedelta(days=3))}');
"""

        all_order_ids.append((oid, onum, total, cid, o_date, pid))

# Ejecutar por partes para no saturar
print("  Insertando cotizaciones...")
run_sql('alfa20-db-crm-1', 'crm_db', quotes_sql)
print("  Insertando lineas de cotizacion...")
run_sql('alfa20-db-crm-1', 'crm_db', quote_lines_sql)
print("  Insertando pedidos...")
run_sql('alfa20-db-crm-1', 'crm_db', orders_sql)
print("  Insertando lineas de pedidos...")
run_sql('alfa20-db-crm-1', 'crm_db', order_lines_sql)
print("  Insertando proyectos...")
run_sql('alfa20-db-crm-1', 'crm_db', projects_sql)
print("  Insertando project workers...")
run_sql('alfa20-db-crm-1', 'crm_db', proj_workers_sql)
print("  Insertando bitacora...")
run_sql('alfa20-db-crm-1', 'crm_db', bitacora_sql)
print("  Insertando gastos de proyecto...")
run_sql('alfa20-db-crm-1', 'crm_db', proj_expenses_sql)

# ════════════════════════════════════════════════════════════════════════════
#  6. CRM — OPORTUNIDADES
# ════════════════════════════════════════════════════════════════════════════
print("\n=== Oportunidades ===")
opp_titles = [
    'Proyecto canceleria hotel', 'Ventanas residencial nueva', 'Fachada aluminio comercial',
    'Cancel baño remodelacion', 'Techo de patio aluminio', 'Puertas entrada edificio',
    'Canceleria oficinas', 'Ventanales departamento', 'Porta automatica local',
    'Techo palapa aluminio', 'Ventanas condominio', 'Cancel spa hotel',
    'Reemplazo ventanas hotel', 'Puerta principal residencia', 'Canceleria baño lujo',
    'Vidrios templados locales', 'Sistema Bacalar hotel', 'Ventanas fraccionamiento',
    'Puerta corrediza terraza', 'Fachada vidrio oficinas',
]
opp_stages_pool = ['new','contacted','visit','quoted','won','won','won','lost','negotiation','proposal']
opps_sql = ""
for i in range(75):
    o_id = uid()
    cid = random.choice(customer_ids)
    title = random.choice(opp_titles) + f' #{random.randint(1,99)}'
    stage = random.choice(opp_stages_pool)
    exp_rev = round2(random.uniform(8000, 120000))
    prob = {'new':15,'contacted':30,'visit':45,'quoted':65,'negotiation':70,'proposal':75,'won':100,'lost':0}[stage]
    o_date = rand_dt(START, END)
    close = o_date + timedelta(days=random.randint(15, 60))
    assigned = random.choice(['Anita', 'Sinai'])
    loc = random.choice(cancun_colonias)
    opps_sql += f"""
INSERT INTO opportunities(id,title,customer_id,stage,expected_revenue,probability,assigned_to,
                           expected_close,created_at,updated_at,location)
VALUES('{o_id}','{esc(title)}','{cid}','{stage}',{exp_rev},{prob},'{assigned}',
       '{dt(close)}','{dt(o_date)}','{dt(o_date)}','{esc(loc)}');
"""
run_sql('alfa20-db-crm-1', 'crm_db', opps_sql)

# ════════════════════════════════════════════════════════════════════════════
#  7. CRM — TAREAS DE MARKETING
# ════════════════════════════════════════════════════════════════════════════
print("\n=== Marketing Tasks ===")
campaigns = [
    'Temporada Alta 2021','Promo Navidad 2021','Arranque 2022',
    'Semana Santa 2022','Expo Construye 2022','Temporada Alta 2022',
    'Reactivacion 2023','Promo Hoteles 2023','Redes Sociales Q3 2023',
    'Cierre año 2023','Arranque 2024','Promo Cancun Centro 2024',
    'Expo Construye 2024','Temporada Alta 2024-2025','Redes Sociales 2025',
]
mkt_titles = [
    'Publicacion Instagram antes/despues', 'Presupuesto Facebook Ads', 'Visita fotografica obra terminada',
    'Envio de catalogo por WhatsApp', 'Diseño grafico promo temporada', 'Actualizacion Google My Business',
    'Video instalacion cancel', 'Cotizacion anuncio revista', 'Seguimiento leads Facebook',
    'Email marketing clientes frecuentes', 'Publicacion en OLX/Marketplace', 'Llamadas de seguimiento cotizaciones',
    'Diseño banner obra nueva', 'Perfil de cliente satisfecho', 'Propuesta patrocinio evento local',
]
mkt_stages = ['por_hacer','en_progreso','completado','completado','completado','en_revision']
mkt_sql = ""
for i in range(65):
    mt_id = uid()
    m_date = rand_dt(START, END)
    due = m_date + timedelta(days=random.randint(3, 21))
    stage = random.choice(mkt_stages)
    if m_date > datetime(2025, 3, 1):
        stage = random.choice(['por_hacer','en_progreso','en_revision'])
    prio = random.choice(['low','medium','medium','high'])
    camp = random.choice(campaigns)
    title = random.choice(mkt_titles)
    mkt_sql += f"""
INSERT INTO marketing_tasks(id,title,stage,priority,assigned_to,due_date,campaign,created_at,updated_at)
VALUES('{mt_id}','{esc(title)}','{stage}','{prio}','Juliette',
       '{dt(due)}','{esc(camp)}','{dt(m_date)}','{dt(m_date)}');
"""
run_sql('alfa20-db-crm-1', 'crm_db', mkt_sql)

# ════════════════════════════════════════════════════════════════════════════
#  8. CRM — EVENTOS DE CALENDARIO
# ════════════════════════════════════════════════════════════════════════════
print("\n=== Calendario ===")
cal_sql = ""
ev_types = [
    ('Visita de medicion', 'blue'), ('Instalacion obra', 'green'),
    ('Reunion con cliente', 'purple'), ('Entrega de proyecto', 'orange'),
    ('Cita cotizacion', 'yellow'), ('Seguimiento garantia', 'red'),
]
for i in range(55):
    ev_id = uid()
    title, color = random.choice(ev_types)
    cid = random.choice(customer_ids)
    ev_dt = rand_dt(START, END)
    ev_end = ev_dt + timedelta(hours=random.randint(1, 4))
    creator = random.choice(['Anita', 'Eben Supervision', 'Sinai'])
    cal_sql += f"""
INSERT INTO calendar_events(id,title,start_date,end_date,all_day,color,customer_id,
                              created_by,created_at,updated_at)
VALUES('{ev_id}','{esc(title + " - cliente")}','{dt(ev_dt)}','{dt(ev_end)}',
       false,'{color}','{cid}','{creator}','{dt(ev_dt)}','{dt(ev_dt)}');
"""
run_sql('alfa20-db-crm-1', 'crm_db', cal_sql)

# ════════════════════════════════════════════════════════════════════════════
#  9. ACCOUNTING — FACTURAS + PAGOS
# ════════════════════════════════════════════════════════════════════════════
print("\n=== Facturas y Pagos ===")
inv_sql = ""
inv_lines_sql = ""
pay_sql = ""
inv_counter = 1000

# Facturas basadas en pedidos reales
customer_names = {v: k for k, v in CID.items()}

for (oid, onum, total, cid, o_date, proj_id) in all_order_ids:
    if o_date > END: continue
    inv_counter += 1
    inv_id = uid()
    inv_num = f"FAC-{o_date.year}-{str(inv_counter).zfill(4)}"
    subtotal = round2(total / 1.16)
    tax = round2(total - subtotal)
    issue_dt = o_date + timedelta(days=random.randint(1, 3))
    due_dt = issue_dt + timedelta(days=30)

    # Buscar nombre del cliente (simplificado)
    cname = next((n for n, i in CID.items() if i == cid), 'Cliente')

    # Status de factura
    if issue_dt.year <= 2023:
        istatus = random.choice(['paid','paid','paid','paid','overdue'])
    elif issue_dt.year == 2024:
        if issue_dt.month <= 9:
            istatus = random.choice(['paid','paid','overdue','paid'])
        else:
            istatus = random.choice(['paid','sent','overdue'])
    else:
        istatus = random.choice(['sent','paid','draft','paid'])

    paid_amount = total if istatus == 'paid' else (round2(total * 0.5) if istatus == 'overdue' else 0.0)
    uso_cfdi = random.choice(['G01','G03','I01','S01'])
    forma_pago = random.choice(['03','04','01'])  # 03=transferencia, 04=tarjeta, 01=efectivo

    inv_sql += f"""
INSERT INTO invoices(id,number,invoice_type,status,partner_id,partner_name,issue_date,due_date,
                      subtotal,tax_amount,total,paid_amount,order_id,
                      uso_cfdi,forma_de_pago,created_at)
VALUES('{inv_id}','FAC-{o_date.year}-{str(inv_counter).zfill(4)}','customer','{istatus}',
       '{cid}','{esc(cname[:40])}','{ds(issue_dt)}','{ds(due_dt)}',
       {subtotal},{tax},{total},{paid_amount},'{onum}',
       '{uso_cfdi}','{forma_pago}','{dt(issue_dt)}');
"""
    # Linea de factura
    il_id = uid()
    inv_lines_sql += f"""
INSERT INTO invoice_lines(id,invoice_id,description,quantity,unit_price,total_price,account_id)
VALUES('{il_id}','{inv_id}','Fabricacion e instalacion segun pedido {onum}',
       1,{subtotal},{subtotal},'{ACCTS["revenue"]}');
"""
    # Pago si fue pagado
    if istatus == 'paid':
        pay_id = uid()
        pay_dt = issue_dt + timedelta(days=random.randint(1, 15))
        method = random.choice(['transfer','transfer','transfer','cash','card'])
        ref = f"REF{random.randint(100000,999999)}" if method == 'transfer' else ''
        pay_sql += f"""
INSERT INTO payments(id,invoice_id,amount,payment_date,method,reference,created_at)
VALUES('{pay_id}','{inv_id}',{total},'{ds(pay_dt)}','{method}','{ref}','{dt(pay_dt)}');
"""
    elif istatus == 'overdue' and paid_amount > 0:
        # Pago parcial
        pay_id = uid()
        pay_dt = issue_dt + timedelta(days=random.randint(5, 20))
        pay_sql += f"""
INSERT INTO payments(id,invoice_id,amount,payment_date,method,reference,created_at)
VALUES('{pay_id}','{inv_id}',{paid_amount},'{ds(pay_dt)}','transfer',
       'REF{random.randint(100000,999999)}','{dt(pay_dt)}');
"""

run_sql('alfa20-db-accounting-1', 'accounting_db', inv_sql)
run_sql('alfa20-db-accounting-1', 'accounting_db', inv_lines_sql)
run_sql('alfa20-db-accounting-1', 'accounting_db', pay_sql)

# ════════════════════════════════════════════════════════════════════════════
# 10. ACCOUNTING — GASTOS OPERATIVOS (54 meses)
# ════════════════════════════════════════════════════════════════════════════
print("\n=== Gastos operativos ===")
exp_sql = ""
cur = datetime(2021, 1, 1)
while cur <= datetime(2025, 5, 31):
    y = cur.year
    m = cur.month
    day5  = cur.replace(day=5)
    day10 = cur.replace(day=10)
    day15 = cur.replace(day=15)
    day20 = cur.replace(day=20)
    day28 = cur.replace(day=28) if m != 2 else cur.replace(day=27)

    # Renta mensual (crece ~5% anual)
    renta = round2(15000 * (1.05 ** (y - 2021)))
    exp_sql += f"""
INSERT INTO expenses(id,date,description,category,amount,supplier_name,reference,created_by,created_at)
VALUES('{uid()}','{ds(day5)}','Renta mensual taller y showroom','rent',{renta},
       'Bienes Raices Cancun S.A.','REC-{y}{str(m).zfill(2)}','Miguel Che','{dt(day5)}');
"""
    # Nomina (cada 15 dias - quincenas)
    # 2021: 3 trabajadores, 2022: 5, 2023+: 7
    n_workers_pay = 3 if y == 2021 else (5 if y == 2022 else 7)
    sal_por_quincena = round2(n_workers_pay * 6500)
    exp_sql += f"""
INSERT INTO expenses(id,date,description,category,amount,supplier_name,reference,created_by,created_at)
VALUES('{uid()}','{ds(day15)}','Nomina quincena 1 - {n_workers_pay} colaboradores','salaries',{sal_por_quincena},
       'Nomina Interna','QNA1-{y}{str(m).zfill(2)}','Miguel Che','{dt(day15)}');
INSERT INTO expenses(id,date,description,category,amount,supplier_name,reference,created_by,created_at)
VALUES('{uid()}','{ds(day28)}','Nomina quincena 2 - {n_workers_pay} colaboradores','salaries',{sal_por_quincena},
       'Nomina Interna','QNA2-{y}{str(m).zfill(2)}','Miguel Che','{dt(day28)}');
"""
    # Luz y agua
    luz = round2(random.uniform(2800, 4500))
    exp_sql += f"""
INSERT INTO expenses(id,date,description,category,amount,supplier_name,reference,created_by,created_at)
VALUES('{uid()}','{ds(day10)}','Electricidad y agua taller','utilities',{luz},
       'CFE / CAPA','CFE-{y}{str(m).zfill(2)}','Miguel Che','{dt(day10)}');
"""
    # Gasolina / transporte
    gas = round2(random.uniform(4200, 7800))
    exp_sql += f"""
INSERT INTO expenses(id,date,description,category,amount,supplier_name,reference,created_by,created_at)
VALUES('{uid()}','{ds(day20)}','Combustible vehiculos de trabajo','fuel',{gas},
       'PEMEX Cancun','FUEL-{y}{str(m).zfill(2)}','Eben Supervision','{dt(day20)}');
"""
    # Internet y telefonia
    tel = round2(random.uniform(1200, 1800))
    exp_sql += f"""
INSERT INTO expenses(id,date,description,category,amount,supplier_name,reference,created_by,created_at)
VALUES('{uid()}','{ds(day5)}','Internet y plan telefonico empresarial','utilities',{tel},
       'Telmex / Telcel','TEL-{y}{str(m).zfill(2)}','Miguel Che','{dt(day5)}');
"""
    # Publicidad (Facebook/Google Ads)
    pub = round2(random.uniform(2500, 9000) * month_weight(m))
    exp_sql += f"""
INSERT INTO expenses(id,date,description,category,amount,supplier_name,reference,created_by,created_at)
VALUES('{uid()}','{ds(day10)}','Publicidad digital Facebook e Instagram Ads','advertising',{pub},
       'Meta / Google Ads','ADS-{y}{str(m).zfill(2)}','Juliette','{dt(day10)}');
"""
    # Herramientas y mantenimiento (cada 2 meses)
    if m % 2 == 0:
        herr = round2(random.uniform(1500, 5500))
        exp_sql += f"""
INSERT INTO expenses(id,date,description,category,amount,supplier_name,reference,created_by,created_at)
VALUES('{uid()}','{ds(day15)}','Herramientas y mantenimiento de equipo','tools',{herr},
       'Herramientas del Sureste','HERR-{y}{str(m).zfill(2)}','Eben Supervision','{dt(day15)}');
"""
    # Compra de materiales consumibles (tornillos, selladores, etc.)
    mat = round2(random.uniform(3000, 12000) * month_weight(m))
    exp_sql += f"""
INSERT INTO expenses(id,date,description,category,amount,supplier_name,reference,created_by,created_at)
VALUES('{uid()}','{ds(day20)}','Materiales consumibles: sellador, tornilleria, esquineros','materials',{mat},
       'Ferreteria Cancun Sur','MAT-{y}{str(m).zfill(2)}','Carlos Mendez','{dt(day20)}');
"""
    # Avanzar al siguiente mes
    cur = (cur.replace(day=1) + timedelta(days=32)).replace(day=1)

run_sql('alfa20-db-accounting-1', 'accounting_db', exp_sql)

# ════════════════════════════════════════════════════════════════════════════
# 11. INVENTORY — Movimientos de stock
# ════════════════════════════════════════════════════════════════════════════
print("\n=== Movimientos de inventario ===")
mov_sql = ""
for p in PRODUCTS:
    # Entrada inicial
    mov_sql += f"""
INSERT INTO stock_movements(id,product_id,warehouse_id,movement_type,quantity,reference,notes,created_at)
VALUES('{uid()}','{p["id"]}','{WH_ID}','in_',{random.randint(5,15)},
       'INV-INICIAL','Inventario inicial al arranque del sistema','2021-01-15 08:00:00');
"""
    # Entradas y salidas periodicas
    cur_dt = datetime(2021, 3, 1)
    while cur_dt <= END:
        if random.random() < 0.6:
            entrada = random.randint(2, 8)
            mov_sql += f"""
INSERT INTO stock_movements(id,product_id,warehouse_id,movement_type,quantity,reference,notes,created_at)
VALUES('{uid()}','{p["id"]}','{WH_ID}','in_',{entrada},
       'COMP-{cur_dt.strftime("%Y%m")}','Compra a proveedor','{dt(cur_dt)}');
"""
        if random.random() < 0.7:
            salida = random.randint(1, 4)
            mov_sql += f"""
INSERT INTO stock_movements(id,product_id,warehouse_id,movement_type,quantity,reference,notes,created_at)
VALUES('{uid()}','{p["id"]}','{WH_ID}','out',{salida},
       'OBRA-{cur_dt.strftime("%Y%m")}','Salida para proyecto','{ dt(cur_dt + timedelta(days=5))}');
"""
        cur_dt = (cur_dt.replace(day=1) + timedelta(days=32)).replace(day=1)

run_sql('alfa20-db-inventory-1', 'inventory_db', mov_sql)

print("\n✅ Simulacion completada exitosamente.")
print("   Abre http://localhost en tu navegador y haz Ctrl+F5")
