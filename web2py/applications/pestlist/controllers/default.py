# -*- coding: utf-8 -*-

def crop_index():


    def get_image(t1):
        res = db(db.image.t1==t1).select('image_link').first()
        if res:
            return res['_extra']['image_link']
        else:
            return None


    sql = '''SELECT *
             FROM taxon2
             WHERE id IN
                (SELECT t1
                 FROM associate2
                 GROUP BY t1)
             ORDER BY lineage;'''
    crops = db.executesql(sql, as_dict=True)
    return locals()


def pest_list(taxon2_id):
    sql = '''SELECT *
             FROM taxon2
             WHERE id IN
                (SELECT t2
                 FROM associate2
                 WHERE t1={})
             ORDER BY lineage;'''.format(taxon2_id)
    print sql
    return db.executesql(sql, as_dict=True)


def taxon_info(taxon2_id):
    q = db.taxon2.id==taxon2_id
    return db(q).select().first()


def crop_page():

    def get_image(t1):
        res = db(db.image.t1==t1).select('image_link').first()
        if res:
            return res['_extra']['image_link']
        else:
            return None

    def get_factsheets(t1):
        res = db(db.factsheet.t1==t1).select('url').first()
        print res
        if res:
            return res['_extra']['url']
        else:
            return None


    taxon2_id = request.args(0)
    if not taxon2_id:
        return '''No taxon2_id provided!<br>
                  This function expects a parameter.<br>
                  Example:<br>
                  http://127.0.0.1:8000/pestlist/default/crop_page/58'''
    crop_info = taxon_info(taxon2_id)
    pests = pest_list(taxon2_id)
    return locals()














def find_taxon2_problems():
    s = ''
    ranks = {
        'kingdom': 1,
        'phylum':  2,
        'class':   3,
        'order':   4,
        'family':  5,
        'genus':   6,
        'species': 7,
        'subspecies': 8
    }
    for row in db(db.taxon2).select():
        n = len(row.lineage.split('|'))
        if n != ranks[row.trank]:
            s += '{} {} {} {}<br>'.format(
                row.tid, row.trank, row.name, row.lineage)
    return s


def test_tree():
    return dict()


def create_child_node():
    return dict()


def display_taxonomic_tree():
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
            rows = db(db.taxon2).select(orderby=db.taxon2.lineage)
        else:
            rows = db(db.taxon2.lineage.contains(root_taxon)).select(orderby=db.taxon2.lineage)
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
            rows = db(db.taxon2).select(orderby=db.taxon2.lineage)
        else:
            rows = db(db.taxon2.lineage.contains(root_taxon)).select(orderby=db.taxon2.lineage)
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


def display_geo_tree():
    import json
    m = None
    first_node_id = None
    mylist = []

    form=FORM('Root location (leave blank to include all locations):',
        INPUT(_name='root_taxon'),
        INPUT(_type='submit', _value='Load tree'),
    )

    if form.accepts(request,session):

        root_taxon = form.vars.root_taxon
        print(root_taxon)

        if root_taxon == '':
            rows = db(db.geo).select(orderby=db.geo.lineage)
        else:
            rows = db(db.geo.lineage.contains(root_taxon)).select(orderby=db.geo.lineage)
        rows[0].parent_name = '#' # required by jstree to indicate a root node

        #mylist = []
        for row in rows:
            # if parent_tid is null, replace with '#'
            if row.parent_name is None:
                row.parent_name = '#'
            mylist.append({'id':row.name,'parent':row.parent_name,'text': row.name})
        m = json.dumps(mylist)

    elif form.errors:
        response.flash = 'form has errors'

    if mylist:
      first_node_id = mylist[0]['id']
    return dict(form=form, m=m, first_node_id=first_node_id)


def populate_resolved_names_table():

    def insert_mydict(mydict):
        try:
            db.resolved_names.insert(**mydict)
            print('********ADDED {}'.format(mydict['supplied_name_string']))
        except:
            print('NOT ADDED BECAUSE OF DUP? {}'.format(mydict['supplied_name_string']))
            pass
        print(mydict)
        print
        return

    db.resolved_names.truncate() # Delete all records in table
    data = get_extracted_names()['resolved_names']
    for row in data:
        if 'results' in row.keys():
            mydict = {
                'supplied_name_string': row.get('supplied_name_string', None),
                'classification_path': row['results'][0].get('classification_path', None),
                'classification_path_ids': row['results'][0].get('classification_path_ids', None),
                'classification_path_ranks': row['results'][0].get('classification_path_ranks', None)
            }
            insert_mydict(mydict)

    # Now manually insert some more records

    # To get data, go to http://resolver.globalnames.org/
    # Search against the GBIF data source
    # Copy data from JSON or XML

    mydict = {
        'supplied_name_string': 'Musa',
        'classification_path': 'Plantae|Tracheophyta|Liliopsida|Zingiberales|Musaceae|Musa',
        'classification_path_ids': '6|7707728|196|627|4686|2760990',
        'classification_path_ranks': 'kingdom|phylum|class|order|family|genus'
    }
    insert_mydict(mydict)

    mydict = {
        'supplied_name_string': 'Ficus',
        'classification_path': 'Plantae|Tracheophyta|Magnoliopsida|Rosales|Moraceae|Ficus',
        'classification_path_ids': '6|7707728|220|691|6640|2984588',
        'classification_path_ranks': 'kingdom|phylum|class|order|family|genus'
    }
    insert_mydict(mydict)

    mydict = {
        'supplied_name_string':'Artocarpus heterophyllus',
        'classification_path': 'Plantae|Tracheophyta|Magnoliopsida|Rosales|Moraceae|Artocarpus|Artocarpus heterophyllus',
        'classification_path_ids': '6|7707728|220|691|6640|2984563|2984565',
        'classification_path_ranks': 'kingdom|phylum|class|order|family|genus|species'
    }
    insert_mydict(mydict)

    mydict = {
        'supplied_name_string': 'Rosa',
        'classification_path': 'Plantae|Tracheophyta|Magnoliopsida|Rosales|Rosaceae|Rosa',
        'classification_path_ids': '6|7707728|220|691|5015|8395064',
        'classification_path_ranks': 'kingdom|phylum|class|order|family|genus'
    }
    insert_mydict(mydict)

    mydict = {
        'supplied_name_string': 'Colocasia esculenta',
        'classification_path': 'Plantae|Tracheophyta|Liliopsida|Alismatales|Araceae|Colocasia|Colocasia esculenta',
        'classification_path_ids': '6|7707728|196|551|6979|5330758|5330776',
        'classification_path_ranks': 'kingdom|phylum|class|order|family|genus|species'
    }
    insert_mydict(mydict)

    # mydict = {
    #     'supplied_name_string': '',
    #     'classification_path': 'Plantae|Tracheophyta|Liliopsida|Alismatales|Araceae|Colocasia|Colocasia esculenta',
    #     'classification_path_ids': '6|7707728|196|551|6979|5330758|5330776',
    #     'classification_path_ranks': 'kingdom|phylum|class|order|family|genus|species'
    # }
    # insert_mydict(mydict)

    return db(db.resolved_names.id>0).select()


def check_name():
    import requests
    name = 'Nysius pulchellus'
    url = 'http://resolver.globalnames.org/name_resolvers.json'
    params = {'names': name, 'data_source_ids': '11'}
    r = requests.get(url, params)
    mydict = r.json()
    return mydict


def unknown_names():
    # Returns a list of names where 'is_known_name' is False
    # and 'results' are provided
    mydict = {}
    data = get_extracted_names()
    for row in data['resolved_names']:
        if not row['is_known_name']:
            if 'results' in row:
                mydict[row['supplied_name_string']] = row['results']
    return mydict


def annotate2():
    import urllib2
    # Download pestlist web page as a string.
    f = urllib2.urlopen('https://aubreymoore.github.io/crop-pest-list/list.html')
    s = f.read().decode('utf-8')
    for row in db(db.resolved_names.id > 0).select():
        supplied_name_string = row.supplied_name_string
        taxon_id = row.classification_path_ids.split('|')[-1]
        taxon_rank = row.classification_path_ranks.split('|')[-1]
        # Is this a leaf node?
        cp_ids = row.classification_path_ids
        children_count = db(db.resolved_names.classification_path_ids.startswith(cp_ids)).count()
        if children_count == 1: # This is a leaf node
            s = s.replace(supplied_name_string,
                    '{} <a href="http://www.gbif.org/species/{}">{}</a>'
                        .format(supplied_name_string, taxon_id, taxon_id))

    # Now, we replace names not included in the nub taxonomy

    for row in db(db.taxon2.tid.startswith('AM')).select():
        # Check that row is a leaf node; will not work if name is used for multiple taxa
        if db(db.taxon2.lineage.contains(row.name)).count() == 1:
            s = s.replace(row.name, '{} <b>{}</b>'.format(row.name, row.tid))
    return s


def parse_annotated_html():
    import io
    import re
    import pandas as pd

    with io.open('crop-pest-list-annotated.html','r', encoding='utf-8') as f:
        s = f.read()

    # <span class="pest" style="color:red">2083004</span>
    # Note use of nongreedy suffix

    p = re.compile('<span class="(.*?)" .*?>(.*?)</span>')
    m = p.findall(s)

    # m is a list of tuples: [(u'pest', u'1740496'), (u'pest', u'5109882')]

    mylist = []
    host=None; pest=None
    for item in m:
        if item[0] == 'mw-headline':
            # Extract the host code, which is the string between ">" and the
            # end of line.
            host = re.match('.*>(.*?)$', item[1]).group(1)
            pest = None
        if item[0] in ['pest', 'synonym']:
            pest = item[1]
        if host and pest:
            mylist.append({'tid1': host, 'tid2': pest})

    # Add records to associate2 table
    db.associate2.truncate()
    for row in mylist:
        # look up id's
        host_id = db(db.taxon2.tid==row['tid1']).select('id').first()
        pest_id = db(db.taxon2.tid==row['tid2']).select('id').first()
        # Insert if not a duplicate record
        nrows = db(db.associate2.t1==host_id)(db.associate2.t2==pest_id).count()
        if nrows==0:
            db.associate2.insert(t1=host_id, t2=pest_id)
    return {'mylist': mylist, 'host_id': host_id, 'pest_id': pest_id}


def annotate_html():
    import urllib2
    import os
    import io

    if not os.path.exists('crop-pest-list.html'):
        f = urllib2.urlopen('https://aubreymoore.github.io/crop-pest-list/list.html')
        s = f.read()
        print('s: ',s)
        with io.open('crop-pest-list.html','w', encoding='utf-8') as f:
            f.write(s)

    with io.open('crop-pest-list.html','r', encoding='utf-8') as f:
        s = f.read()

    for row in db(db.taxon2.id > 0).select():
        '''
        A taxon is a leaf node if it has no children:
        i.e. There should be no records where *parent_tid* refers to this taxon.
        '''
        if db(db.taxon2.parent_tid==row.tid).count()==0:
            if row.lineage.startswith('Plantae'):
                spanclass = 'host'
            else:
                spanclass = 'pest'
            s = s.replace(row.name, '{}<span class="{}" style="color:red">{}</span>'
            .format(row.name, spanclass, row.tid))

    # Check synonyms
    for row in db(db.syn.id > 0).select():
            s = s.replace(row.synonym, '{}<span class="synonym" style="color:green">{}</span>'
            .format(row.synonym, row.taxon.tid))

    # Annotate locations
    for row in db(db.location_recode.id > 0).select():
        s = s.replace(row.raw_string,
        '''{}<span style="color:blue"><b>{}</b> confirmed:<b>{}
        </b> new_island_record:<b>{}</b></span>'''
        .format(
            row.raw_string,
            row.location,
            row.confirmed,
            row.new_island_record)
        )

    with io.open('crop-pest-list-annotated.html', 'w', encoding='utf-8') as f:
       f.write(s)

    return s


def annotate_locations():
    import urllib2
    # Download pestlist web page as a string.
    f = urllib2.urlopen('https://aubreymoore.github.io/crop-pest-list/list.html')
    s = f.read().decode('utf-8')
    for row in db(db.location_recode.id > 0).select():
        s = s.replace(row.raw_string,
        '''{}<span style="color:blue"> <b>{}</b> confirmed:<b>{}
        </b> new_island_record:<b>{}</b></span>'''
        .format(
            row.raw_string,
            row.location,
            row.confirmed,
            row.new_island_record)
        )
    return s


def harvest_images():
    import urllib2
    query = 'Spodoptera+mauritia'
    #query = query.split(' ')
	#query = '+'.join(query)
    url='https://www.bing.com/images/search?q={}'.format(query)
    f = urllib2.urlopen(url)
    s = f.read().decode('utf-8')
    return locals()




def extract_locations():
    import urllib2
    import re

    # Download pestlist web page as a string.
    f = urllib2.urlopen('https://aubreymoore.github.io/crop-pest-list/list.html')
    s = f.read().decode('utf-8')

    matches = re.findall(r'\s(.=.*)\s', s)
    m = set(matches)
    s = ''
    for item in list(m):
        s += '{}<br>'.format(item)

    return s




def get_extracted_names():
    '''
    Returns the contents of the 'extracted_names_json' field in the first
    record of the 'extracted_names' table.
    '''
    return db(db.extracted_names).select()[0]['extracted_names_json']


def parse_resolved_names2():
    '''
    Parses the JSON data stored in 'db.extracted_names.extracted_names_json' and
    inserts all taxa to a self-referencing table, 'db.taxon2'. Fields in
    this table are:

        tid: taxon id; usually a GBIF taxon id
        parent_tid: tid of the taxon's parent; parent of a root must be '#'
        name: taxon name
        trank: taxon rank (kingdom, phylum, class, order family, genus or species)
        lineage: ancestors of the taxon; eg. lineage for Oryctes rhinoceros is:
            Animalia|Arthropoda|Insecta|Coleoptera|Dynastidae|Oryctes|Oryctes rhinoceros

    Dependancies:
        get_extracted_names
    '''
    resolved_names_list = get_extracted_names()['resolved_names']
    for resolved_name in resolved_names_list:
        results_list = resolved_name.get('results', None)
        if results_list:
            result_dict = results_list[0]
            #lineage = result_dict['classification_path']
            classification_path = result_dict['classification_path'].split('|')
            classification_path_ids = result_dict['classification_path_ids'].split('|')
            classification_path_ranks = result_dict['classification_path_ranks'].split('|')

            print classification_path

            assert classification_path_ranks[0] == 'kingdom'
            assert len(classification_path) == len(classification_path_ids)
            assert len(classification_path_ids) == len(classification_path_ranks)

            for i in range(len(classification_path)):
                if i == 0:
                    parent_tid = '#' # The hash symbol is used by jstree to signify a root node
                else:
                    parent_tid = classification_path_ids[i-1]
                tid = classification_path_ids[i]
                name = classification_path[i]
                trank = classification_path_ranks[i]
                lineage = '|'.join(classification_path[0:i+1])

                try:
                    print('trying to add tid={}, name={}, trank={}, lineage={}'.format(tid, name, trank, lineage))
                    db.taxon2.insert(tid=tid, parent_tid=parent_tid, name=name, trank=trank, lineage=lineage)
                    print( '{} added'.format(name))
                except:
                    print('{} not added - already in DB?'.format(name))
                    pass
    return

#@auth.requires_login()
def show_taxon2():
    grid = SQLFORM.grid(db.taxon2, maxtextlength=1000, paginate=1000)
    return locals()

def show_associate2():
    grid = SQLFORM.smartgrid(db.associate2, linked_tables=['associate2'], maxtextlength=1000, paginate=1000)
    return locals()

def find_names(doc_url):
    '''
    Uses the Global Names Resolver to extract scientific names from 'doc_url'
    which can point to an HTML or PDF document.
    '''
    import requests
    import time

    url = 'http://gnrd.globalnames.org/name_finder.json?'
    #params = {'url': 'https://aubreymoore.github.io/crop-pest-list/list.html'}
    params = {'url': doc_url,
        'data_source_ids': '11',
        'best_match_only': 'true',
        'unique': 'true' }
    r = requests.get(url, params)
    mydict = r.json()
    token_url = mydict['token_url']
    print('token_url: {}'.format(token_url))

    # Poll the token url once a second for 100 s to see if results have been returned.
    i = 0
    while i <= 100:
        i += 1
        time.sleep(1)
        r = requests.get(token_url)
        mydict = r.json()
        status = mydict.get('status','')
        queue_size = mydict.get('queue_size','')
        print('{} status: {} queue_size: {}'.format(i, status, queue_size))
        if status != 303:
            break
    return(mydict)


def doit():
    '''
    Uses the find_names function to extract scientific names from
    'https://aubreymoore.github.io/crop-pest-list/list.html' and stores the
    returned JSON data in db.extracted_names.

    This function runs only when the extracted_names table is empty.

    Dependancies:
        find_names
    '''
    if len(db(db.extracted_names).select())==0:
        doc_url = 'https://aubreymoore.github.io/crop-pest-list/list.html'
        db.extracted_names.insert(extracted_names_json=find_names(doc_url))
        return('Added record.')
    return('Did not add record')


def index():
    return dict(message=T('Welcome to pestlist!'))


@auth.requires_login()
def populate_duo():
    # db.duo_archive.truncate()
    # db.duo.truncate() # Delete all records in table
    data = get_extracted_names()['resolved_names']
    for row in data:
        if 'results' in row:
            results_dict = row['results'][0]
            del row['results']
        else:
            results_dict = {}
        all_dict = row.copy()
        all_dict.update(results_dict)
        print row
        print
        print results_dict
        print
        print all_dict
        print
        db.duo.insert(**all_dict)
    return


@auth.requires_login()
def show_duo():
    # grid = SQLFORM.grid(db.uno, maxtextlength=1000, paginate=1000)
    rows = db(db.duo.id>0).select()
    print(rows)
    return dict(viewthis = rows) # or whatever instead of 'rows'


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())
