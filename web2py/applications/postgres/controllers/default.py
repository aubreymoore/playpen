# -*- coding: utf-8 -*-
def index():
    return 'This is the index page.'

def pest_list(taxon_id):
    sql = '''SELECT *
             FROM taxon
             WHERE id IN
                (SELECT t2
                 FROM associate
                 WHERE t1={})
             ORDER BY lineage;'''.format(taxon_id)
    print sql
    return db.executesql(sql, as_dict=True)


def taxon_info(taxon_id):
    q = db.taxon.id==taxon_id
    return db(q).select().first()


def populate_image_table_from_bugwood():
    import bugwood
    # for row in db().select(db.taxon.ALL, limitby=(100, 120)):
    for row in db().select(db.taxon.ALL):
        children_count = db(db.taxon.lineage.startswith(row.lineage)).count()
        if children_count == 1: # This is a leaf node
            print(row.id, row.lineage)
            response = bugwood.get_images(row.name)
            if response:
                for r in response['rows']:
                    taxon = row.id
                    url = 'https:{}192x128/{}.jpg'.format(r['baseimgurl'], r['imgnum'])
                    attribution = '{}, {}'.format(r['photographer'], r['organization'])
                    source_url = 'https://www.invasive.org/browse/detail.cfm?imgnum={}'.format(r['imgnum'])
                    db.image.update_or_insert(db.image.url==url, taxon=taxon, url=url, attribution=attribution, source_url=source_url)


def doit():
    x = db.executesql("select * from taxon limit 10;")
    return locals


def get_taxon_id(tid):
    myquery = db.taxon.tid==tid
    myrows = db(myquery).select('id')
    return myrows[0]['id']


def get_images(t1):
    return db(db.image.t1==t1).select()


def test_get_images():
    return get_images(request.args[0])


def display_tax_tree():
    import json
    # Important: root nodes must have 'parent':'#'
    m = None
    #root_taxon = ''

    form=FORM('Root taxon (leave blank to include all taxa):',
        INPUT(_name='root_taxon'),
        INPUT(_type='submit'),
    )

    if form.accepts(request,session):

        root_taxon = form.vars.root_taxon
        print(root_taxon)

        #level_dict = {'kingdom':1,'phylum':2,'class':3,'order':4,'family':5,'genus':6,'species':7}
        if root_taxon == '':
            rows = db(db.taxon).select(orderby=db.taxon.lineage)
        else:
            rows = db(db.taxon.lineage.contains(root_taxon)).select(orderby=db.taxon.lineage)
        rows[0].parent_tid = '#' # required by jstree to indicate a root node

        # MAYBE THE FOLLOWING SHOULD BE MOVED INTO THE VIEW (display_taxonomic_tree)

        mylist = []
        for row in rows:
            # if parent_tid is null, replace with '#'
            if row.parent_tid is None:
                row.parent_tid = '#'

            if row.trank in ['genus','species']:
                text = '{} <b><i>{}</i></b>'.format(row.trank, row.name)
            else:
                text = '{} <b>{}</b>'.format(row.trank, row.name)
            mylist.append({'id':row.tid,'parent':row.parent_tid,'text':text})
        m = json.dumps(mylist)

    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'Please select a root taxon and press "SUBMIT QUERY".'
    return dict(form=form, m=m)


def crop_index():
    return {}


def crop_page():

    def get_image(t1):
        images = get_images(t1)
        if images:
            return get_images(t1)[0]
        else:
            return None

    def get_synonyms(t1):
        res = db(db.synonym2.t1==t1).select('name')
        if res:
            return res
        else:
            return None

    # def get_vernacular_names(t1):
    #     res = db(db.vernacular.t1==t1).select('name')
    #     if res:
    #         return res
    #     else:
    #         return None

    # def get_factsheets(t1):
    #     res = db(db.factsheet.t1==t1).select('url').first()
    #     print res
    #     if res:
    #         return res['_extra']['url']
    #     else:
    #         return None

    # def get_geo(t1):
    #     res = db(db.geo.t1==t1).select('name')
    #     if res:
    #         return res
    #     else:
    #         return None

    taxon_id = request.args(0)
    if not taxon_id:
        return '''No taxon_id provided!<br>
                  This function expects a parameter.<br>
                  Example:<br>
                  http://127.0.0.1:8000/pestlist/default/crop_page/58'''
    crop_info = taxon_info(taxon_id)
    pests = pest_list(taxon_id)
    return locals()


def populate_taxon_table():
    fname = '/home/aubreymoore/lineage_list.txt'
    with open(fname) as f:
        lineages = f.read().splitlines()
    lineages.sort()

    for lineage in lineages:
        print('lineage: {}'.format(lineage))
        taxa = lineage.split('|')
        if len(taxa)==1:
            db.taxon.update_or_insert(name=taxa[-1], parent_id=None)
            db.commit()
        else:
            parent_lineage = '|'.join(taxa[:-1])
            sql = "select * from taxon where lineage LIKE '{}'".format(parent_lineage)
            rows = db.executesql(sql, as_dict=True)
            print(sql)
            print(rows)
            parent_id = rows[0]['id']
            db.taxon.update_or_insert(name=taxa[-1], parent_id=parent_id)
            db.commit()

    aaa = 'FINISHED'
    return locals()

# def populate_name_table():
#     for row in db().select(db.taxon.id, db.taxon.name):
#         db.name.update_or_insert(taxon=row['id'], name=row['name'], name_type=2)
#     aaa ='FINISHED'
#     return locals()
