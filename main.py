import requests
import xmlrpc.client
import datetime

# Credenciales
url = 'https://marest-holding-sh.odoo.com'
db = 'diegotangassi-odoo-sh-main-8331495'
username = 'daniel@portalnuva.com'
password = 'D4n13LM4r333st!'

# Verificar conectividad
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
version = common.version()
print("Odoo version:", version)

# Autenticación
uid = common.authenticate(db, username, password, {})
print("Authenticated UID:", uid)

# Llamar al endpoint para usar métodos de los modelos de Odoo
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

# Validar acceso al modelo mrp.workorder
access_mrp = models.execute_kw(db, uid, password, 'mrp.workorder', 'check_access_rights', ['read'], {'raise_exception': False})
print("Access to mrp.workorder:", access_mrp)

# Obtener la fecha de hoy y hace dos días
hoy = datetime.date.today()
fecha_dos_dias_atras = hoy - datetime.timedelta(days=2)

# Filtrar registros por fecha de finalización entre hace dos días y hoy y por name=Tapiz
filtro = [[['state', '=', 'done'], 
           ['date_finished', '>', fecha_dos_dias_atras.strftime("%Y-%m-%d")], 
           ['date_finished', '<=', hoy.strftime("%Y-%m-%d")],
           ['name', '=', 'Tapiz']]]

# Buscar IDs de registros que cumplan con el filtro
ids = models.execute_kw(db, uid, password, 'mrp.workorder', 'search', filtro, {'limit': 100})
print("IDs encontrados en mrp.workorder:", ids)

# Obtener registros seleccionados
atributos = models.execute_kw(db, uid, password, 'mrp.workorder', 'read', [ids], {'fields': ['id', 'name', 'production_id', 'x_studio_empleado', 'finished_lot_id', 'date_start', 'date_finished', 'product_id']})
print("Atributos de mrp.workorder:", atributos)

# Validar acceso al modelo quality.check
access_qc = models.execute_kw(db, uid, password, 'quality.check', 'check_access_rights', ['read'], {'raise_exception': False})
print("Access to quality.check:", access_qc)

# Filtrar registros en quality.check donde measure sea 0 y por name=Tapiz
filtro_qc = [[['measure', '=', 0]]]

# Buscar IDs de registros que cumplan con el filtro
ids_qc = models.execute_kw(db, uid, password, 'quality.check', 'search', filtro_qc, {'limit': 100})
print("IDs encontrados en quality.check:", ids_qc)

# Obtener registros seleccionados de quality.check incluyendo product_id
atributos_qc = models.execute_kw(db, uid, password, 'quality.check', 'read', [ids_qc], {'fields': ['measure','quality_state','x_studio_nombre_de_control','x_studio_empleado','lot_id','point_id','measure_on','test_type_id','production_id','product_id','test_type','quality_state','team_id','company_id']})
print("Atributos de quality.check:", atributos_qc)

# Asociar registros de quality.check con mrp.workorder usando product_id
for attr in atributos:
    attr['quality_checks'] = [qc for qc in atributos_qc if 'product_id' in qc and qc['product_id'] and qc['product_id'][0] == attr['product_id'][0]]

# Definir la URL para la solicitud POST
post_url = 'https://nuvaapp.bubbleapps.io/version-test/api/1.1/wf/crear_ot_pt1'

# Definir los datos del payload
payload = {
    'atributos_mrp_workorder': atributos,
    'atributos_quality_check': atributos_qc
}
print("Payload:", payload)

# Enviar la solicitud POST
response = requests.post(post_url, json=payload)

# Verificar el estado de la respuesta
if response.status_code == 200:
    print('POST request successful')
else:
    print('POST request failed, status code:', response.status_code, "response:", response.text)
