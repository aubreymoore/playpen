#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gluon import *

#from gluon.custom_import import track_changes; track_changes(True) #DO NOT USE IN PRODUCTION

def get_images(species_name):
    import urllib2, json
    species_name = species_name.replace(' ', '+')
    url =  'https://api.bugwood.org/rest/api/subject.json?term={}'.format(species_name)
    bugwood_id = json.loads(urllib2.urlopen(url).read())
    if bugwood_id.get(['items'][0]):
        id = bugwood_id['items'][0]['id']
        url = 'https://api.bugwood.org/rest/api/image.json?page=1&length=5&sub={}'.format(id)
        bugwood_images = json.loads(urllib2.urlopen(url).read())
        return bugwood_images
    else:
        return None
