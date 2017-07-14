# -*- coding: utf-8 -*-

# -------------------------------------------------------------------------
# This scaffolding model makes your app work on Google App Engine too
# File is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

if request.global_settings.web2py_version < "2.14.1":
    raise HTTP(500, "Requires web2py 2.13.3 or newer")

# -------------------------------------------------------------------------
# if SSL/HTTPS is properly configured and you want all HTTP requests to
# be redirected to HTTPS, uncomment the line below:
# -------------------------------------------------------------------------
# request.requires_https()

# -------------------------------------------------------------------------
# app configuration made easy. Look inside private/appconfig.ini
# -------------------------------------------------------------------------
from gluon.contrib.appconfig import AppConfig

# -------------------------------------------------------------------------
# once in production, remove reload=True to gain full speed
# -------------------------------------------------------------------------
myconf = AppConfig(reload=True)

if not request.env.web2py_runtime_gae:
    # ---------------------------------------------------------------------
    # if NOT running on Google App Engine use SQLite or other DB
    # ---------------------------------------------------------------------
    db = DAL('postgres://aubreymoore:canada12@localhost/import_test',
             pool_size=myconf.get('db.pool_size'),
             migrate_enabled=myconf.get('db.migrate'),
             check_reserved=['all'])
else:
    # ---------------------------------------------------------------------
    # connect to Google BigTable (optional 'google:datastore://namespace')
    # ---------------------------------------------------------------------
    db = DAL('google:datastore+ndb')
    # ---------------------------------------------------------------------
    # store sessions and tickets there
    # ---------------------------------------------------------------------
    session.connect(request, response, db=db)
    # ---------------------------------------------------------------------
    # or store session in Memcache, Redis, etc.
    # from gluon.contrib.memdb import MEMDB
    # from google.appengine.api.memcache import Client
    # session.connect(request, response, db = MEMDB(Client()))
    # ---------------------------------------------------------------------

# -------------------------------------------------------------------------
# by default give a view/generic.extension to all actions from localhost
# none otherwise. a pattern can be 'controller/function.extension'
# -------------------------------------------------------------------------
response.generic_patterns = ['*'] if request.is_local else []
# -------------------------------------------------------------------------
# choose a style for forms
# -------------------------------------------------------------------------
response.formstyle = myconf.get('forms.formstyle')  # or 'bootstrap3_stacked' or 'bootstrap2' or other
response.form_label_separator = myconf.get('forms.separator') or ''

# -------------------------------------------------------------------------
# (optional) optimize handling of static files
# -------------------------------------------------------------------------
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'

# -------------------------------------------------------------------------
# (optional) static assets folder versioning
# -------------------------------------------------------------------------
# response.static_version = '0.0.0'

# -------------------------------------------------------------------------
# Here is sample code if you need for
# - email capabilities
# - authentication (registration, login, logout, ... )
# - authorization (role based authorization)
# - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
# - old style crud actions
# (more options discussed in gluon/tools.py)
# -------------------------------------------------------------------------

from gluon.tools import Auth, Service, PluginManager

# host names must be a list of allowed host names (glob syntax allowed)
auth = Auth(db, host_names=myconf.get('host.names'))
service = Service()
plugins = PluginManager()

# -------------------------------------------------------------------------
# create all tables needed by auth if not custom tables
# -------------------------------------------------------------------------
auth.define_tables(username=False, signature=False, migrate=False)

# -------------------------------------------------------------------------
# configure email
# -------------------------------------------------------------------------
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else myconf.get('smtp.server')
mail.settings.sender = myconf.get('smtp.sender')
mail.settings.login = myconf.get('smtp.login')
mail.settings.tls = myconf.get('smtp.tls') or False
mail.settings.ssl = myconf.get('smtp.ssl') or False

# -------------------------------------------------------------------------
# configure auth policy
# -------------------------------------------------------------------------
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

# -------------------------------------------------------------------------
# Define your tables below (or better in another model file) for example
#
# >>> db.define_table('mytable', Field('myfield', 'string'))
#
# Fields can be 'string','text','password','integer','double','boolean'
#       'date','time','datetime','blob','upload', 'reference TABLENAME'
# There is an implicit 'id integer autoincrement' field
# Consult manual for more options, validators, etc.
#
# More API examples for controllers:
#
# >>> db.mytable.insert(myfield='value')
# >>> rows = db(db.mytable.myfield == 'value').select(db.mytable.ALL)
# >>> for row in rows: print row.id, row.myfield
# -------------------------------------------------------------------------


# db.define_table('test', Field('alpha'))


# db.define_table('taxon2',
#     Field('tid', unique=True),
#     Field('parent_tid'),
#     Field('name'),
#     Field('trank', compute=lambda r: compute_taxon_rank(r['parent_tid'])),
#     Field('lineage', compute=lambda r: compute_taxon_lineage(r['parent_tid'], r['name'])),
#     format='%(name)s',
#     migrate=False,
#     fake_migrate=True
# )
# # For root nodes, parent_tid is NULL; otherwise parent_node must refer to an existing tid
# db.taxon2.parent_tid.requires = IS_NULL_OR(IS_IN_DB(db, 'taxon2.tid', '%(name)s'))


'''
taxon
'''
db.define_table('taxon',
    Field('parent_id'),
    Field('name'),
    Field('lineage', compute=lambda r: compute_taxon_lineage(r['parent_id'], r['name'])),
    Field('trank', compute=lambda r: compute_taxon_rank(r['parent_id'])),
    format='%(name)s',
)
# For root nodes, parent_tid is NULL; otherwise parent_node must refer to an existing tid
db.taxon.parent_id.requires = IS_NULL_OR(IS_IN_DB(db, 'taxon.id', '%(lineage)s'))

def insert_name_record(row, id):
    db.name.update_or_insert(taxon=id, name=row['name'], name_type=2)

db.taxon._after_insert.append(lambda row,id: insert_name_record(row, id))

def compute_taxon_lineage(parent_id, name):
    rows = db(db.taxon.id==parent_id).select(db.taxon.lineage)
    if len(rows) > 0:
        s = '{}|{}'.format(rows[0]['lineage'], name)
    else:
        s = name
    return s

def compute_taxon_rank(parent_id):
    ranks = ['kingdom','phylum','class','order','family','genus','species','subspecies']
    rows = db(db.taxon.id==parent_id).select(db.taxon.lineage)
    if len(rows) > 0:
        n = len(rows[0].lineage.split('|'))
        s = ranks[n]
    else:
        s = 'kingdom'
    return s


'''
name_type
'''
db.define_table('name_type',
    Field('name_type', unique=True),
    format='%(name_type)s',
)


'''
name
'''
# db.define_table('name',
#     Field('taxon', db.taxon),
#     Field('name_type', db.name_type),
#     Field('name'),
#     format='%(name)s',
# )


'''
name
'''
db.define_table('name',
    Field('taxon', db.taxon),
    Field('name_type', db.name_type),
    Field('name'),
    format='%(name)s',
)



'''
image
'''
db.define_table('image',
    Field('taxon', db.taxon),
    Field('url', unique=True),
    Field('attribution'),
    Field('source_url'),
    Field('weight', type='integer', default=0),
)


'''
associate
'''
db.define_table('associate',
    Field('taxon1', db.taxon),
    Field('taxon2', db.taxon),
    Field('association', default='plant host|herbivore'),
    Field('note'),
)


db.define_table('biblio_type',
    Field('biblio_type'),
    format='%(biblio_type)s'
)


db.define_table('biblio',
    Field('biblio_type', db.biblio_type),
    Field('reference'),
    Field('url'),
    format='%(bibkey)s'
)


db.define_table('name_biblio',
    Field('name1', db.name),
    Field('biblio', db.biblio),
)


'''
geo
'''
db.define_table('geo',
    Field('name', unique=True),
    Field('parent_name'),
    Field('lineage', compute=lambda r: compute_geo_lineage(r['parent_name'], r['name'])),
    format='%(name)s',
)
# For root nodes, parent_tid is NULL; otherwise parent_node must refer to an existing tid
db.geo.parent_name.requires = IS_NULL_OR(IS_IN_DB(db, 'geo.name', '%(name)s'))

def compute_geo_lineage(parent_name, name):
    rows = db(db.geo.name==parent_name).select(db.geo.lineage)
    if len(rows) > 0:
        s = '{}|{}'.format(rows[0]['lineage'], name)
    else:
        s = name
    return s


'''
distribution
'''
db.define_table('distribution',
    Field('taxon', db.name),
    Field('geo', db.geo),
    Field('biblio', db.biblio),
    Field('first_record', type='boolean')
)


# -------------------------------------------------------------------------
# after defining tables, uncomment below to enable auditing
# -------------------------------------------------------------------------
# auth.enable_record_versioning(db)

# -------------------------------------------------------------------------
# HELPER FUNCTIONS - Can be called from views.
# -------------------------------------------------------------------------


'''
Returns a single image record for a taxon.
'''
def get_image(taxon_id):
    sql = '''
        select *
        from image
        where taxon={taxon_id}
        limit 1
        '''.format(taxon_id=taxon_id)
    res = db.executesql(sql, as_dict=True)
    if res:
        return res[0]
    else:
        return None


'''
Returns taxon records for all crops.
'''
def get_crops():
    sql = '''
        select taxon.*
        from associate, taxon
        where associate.taxon1=taxon.id
        group by taxon.id
        order by taxon.lineage
        '''
    return db.executesql(sql, as_dict=True)
