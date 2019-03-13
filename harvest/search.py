import logging
import os
import time
import types

import requests

from utils import scihub_credentials,get_s2_new_naming_convention

#aoi ='POLYGON ((-1.984891597597141 42.9448387446552, -1.367038590164367 42.93539924782252, -1.363815009256022 42.55505005702414, -1.984891597597141 42.56454765255964, -1.984891597597141 42.9448387446552))'
aoi = 'POLYGON ((126.1897881917999 37.00946973762048, 126.8246998672189 36.99266125474486, 126.8282076665306 36.74289944205459, 126.4353341436195 36.58814444438993, 126.3055455690863 36.61630485758916, 126.1897881917999 37.00946973762048))'




def search_scihub_s3():
    sci_user, sci_passwd, sci_url = scihub_credentials()

    url = sci_url
    url += '/dhus/search?q='
    #url += '*34SFJ* AND '
    #url += 'footprint:"Intersects(' + aoi.geom.wkt.encode('utf-8') + ')" '
    #url += 'AND beginPosition:[' + fist_day + 'T00:00:00.000Z TO ' + last_day + 'T23:59:59.999Z] '
    #url += 'AND endPosition:[' + fist_day + 'T00:00:00.000Z TO ' + last_day + 'T23:59:59.999Z] '
    url += 'platformname:Sentinel-3 '
    url += '&format=json'

    starting = -100
    max_pagination_count = 100
    while max_pagination_count == 100:

        x = 0
        while True:
            # set starting point, increasing every time by 100
            starting += max_pagination_count
            url_pagination = url + '&start=%d&rows=100' % starting

            session = requests.Session()
            session.auth = (sci_user, sci_passwd)
            session.stream = True
            resp = session.get(url_pagination)
            if resp.status_code == 200:
                response = resp.json()
                # reset max_pagination_count variable, in order to exit from loop or not
                max_pagination_count = len(response['feed']['entry'])
                if starting == 0:
                    total_results = response['feed']['opensearch:totalResults']
                    # logger.info('Search request for the %s month has been successfully submitted -- URL: %s',
                    # fist_day.split('-')[1], url_pagination)
                    # logger.info('Total results: %s', total_results)
                resp.close()
                break
            else:
                logging.info('Something happened: \tStatus Code: %d, \tReason: %s,', resp.status_code,
                               resp.reason)
                logging.info('URL: %s' % url)
                time.sleep(300)
                x = 1
                break

        if x==1:
            break

        for prod in range(len(response['feed']['entry'])):
            try:
                # get str metadata
                meta_str = {meta['name']: meta['content'] for meta in response['feed']['entry'][prod]['str']}
                print response['feed']['entry'][prod]
                break
                # get tile object
                identifier = meta_str['identifier']
                tile = get_s2_new_naming_convention(identifier)[-2]


                meta_date = {meta['name']: meta['content'] for meta in response['feed']['entry'][prod]['date']}

                # get cloud coverage metadata
                cloud_coverage = 0
                if type(response['feed']['entry'][prod]['double']) is types.DictType:
                    cloud_coverage = float(response['feed']['entry'][prod]['double']['content'])
                elif type(response['feed']['entry'][prod]['double']) is types.ListType:
                    meta_double = {meta['name']: meta['content'] for meta in
                                   response['feed']['entry'][prod]['double']}
                    cloud_coverage = float(meta_double['cloudcoverpercentage'])

                selected_metadata = {
                    'uuid': meta_str['uuid'],
                    'identifier': identifier,
                    'filename': meta_str['filename'],
                    'instrument': meta_str['instrumentshortname'],
                    'product_type': meta_str['producttype'],
                    'cloud_cover_percentage': cloud_coverage,
                    'sensing_date': meta_date['beginposition'],
                    'ingestion_date': meta_date['ingestiondate'],
                    'orbit_number': response['feed']['entry'][prod]['int'][0]['content'],
                    'relative_orbit_number': response['feed']['entry'][prod]['int'][1]['content'],
                    'pass_direction': meta_str['orbitdirection'],
                    'size': meta_str['size'],
                    'url_download': response['feed']['entry'][prod]['link'][0]['href'],
                    'url_checksum': response['feed']['entry'][prod]['link'][0]['href'][
                                    :-6] + 'Checksum/Value/$value',
                }
                print selected_metadata['identifier']


            except:
                print "problem"
                continue
        break

def search_scihub_s2():
    sci_user, sci_passwd, sci_url = scihub_credentials()

    url = sci_url
    url += '/dhus/search?q='
    #url += '*34SFJ* AND '
    #url += 'footprint:"Intersects(' + aoi.geom.wkt.encode('utf-8') + ')" '
    #url += 'AND beginPosition:[' + fist_day + 'T00:00:00.000Z TO ' + last_day + 'T23:59:59.999Z] '
    #url += 'AND endPosition:[' + fist_day + 'T00:00:00.000Z TO ' + last_day + 'T23:59:59.999Z] '
    url += 'platformname:Sentinel-2 '
    url += '&format=json'

    starting = -100
    max_pagination_count = 100
    while max_pagination_count == 100:

        x = 0
        while True:
            # set starting point, increasing every time by 100
            starting += max_pagination_count
            url_pagination = url + '&start=%d&rows=100' % starting

            session = requests.Session()
            session.auth = (sci_user, sci_passwd)
            session.stream = True
            resp = session.get(url_pagination)
            if resp.status_code == 200:
                response = resp.json()
                # reset max_pagination_count variable, in order to exit from loop or not
                max_pagination_count = len(response['feed']['entry'])
                if starting == 0:
                    total_results = response['feed']['opensearch:totalResults']
                    # logger.info('Search request for the %s month has been successfully submitted -- URL: %s',
                    # fist_day.split('-')[1], url_pagination)
                    # logger.info('Total results: %s', total_results)
                resp.close()
                break
            else:
                logging.info('Something happened: \tStatus Code: %d, \tReason: %s,', resp.status_code,
                               resp.reason)
                logging.info('URL: %s' % url)
                time.sleep(300)
                x = 1
                break

        if x==1:
            break

        for prod in range(len(response['feed']['entry'])):
            try:
                # get str metadata
                meta_str = {meta['name']: meta['content'] for meta in response['feed']['entry'][prod]['str']}
                print response['feed']['entry'][prod]
                break
                # get tile object
                identifier = meta_str['identifier']
                tile = get_s2_new_naming_convention(identifier)[-2]


                meta_date = {meta['name']: meta['content'] for meta in response['feed']['entry'][prod]['date']}

                # get cloud coverage metadata
                cloud_coverage = 0
                if type(response['feed']['entry'][prod]['double']) is types.DictType:
                    cloud_coverage = float(response['feed']['entry'][prod]['double']['content'])
                elif type(response['feed']['entry'][prod]['double']) is types.ListType:
                    meta_double = {meta['name']: meta['content'] for meta in
                                   response['feed']['entry'][prod]['double']}
                    cloud_coverage = float(meta_double['cloudcoverpercentage'])

                selected_metadata = {
                    'uuid': meta_str['uuid'],
                    'identifier': identifier,
                    'filename': meta_str['filename'],
                    'instrument': meta_str['instrumentshortname'],
                    'product_type': meta_str['producttype'],
                    'cloud_cover_percentage': cloud_coverage,
                    'sensing_date': meta_date['beginposition'],
                    'ingestion_date': meta_date['ingestiondate'],
                    'orbit_number': response['feed']['entry'][prod]['int'][0]['content'],
                    'relative_orbit_number': response['feed']['entry'][prod]['int'][1]['content'],
                    'pass_direction': meta_str['orbitdirection'],
                    'size': meta_str['size'],
                    'url_download': response['feed']['entry'][prod]['link'][0]['href'],
                    'url_checksum': response['feed']['entry'][prod]['link'][0]['href'][
                                    :-6] + 'Checksum/Value/$value',
                }
                print selected_metadata['identifier']


            except:
                print "problem"
                continue
        break







'''
def search_spacenoa_s2():
    sci_user, sci_passwd, sci_url = noa_credentials()

    url = sci_url
    url += '/dhus/search?q='
    #url += '*34SFJ* AND '
    # url += 'footprint:"Intersects(' + aoi.geom.wkt.encode('utf-8') + ')" '
    # url += 'AND beginPosition:[' + fist_day + 'T00:00:00.000Z TO ' + last_day + 'T23:59:59.999Z] '
    # url += 'AND endPosition:[' + fist_day + 'T00:00:00.000Z TO ' + last_day + 'T23:59:59.999Z] '
    url += 'platformname:Sentinel-2 '
    url += '&format=json'

    starting = -100
    max_pagination_count = 100
    while max_pagination_count == 100:

        x = 0
        while True:
            # set starting point, increasing every time by 100
            starting += max_pagination_count
            url_pagination = url + '&start=%d&rows=100' % starting

            session = requests.Session()
            session.auth = (sci_user, sci_passwd)
            session.stream = True
            resp = session.get(url_pagination)
            if resp.status_code == 200:
                response = resp.json()
                # reset max_pagination_count variable, in order to exit from loop or not
                max_pagination_count = len(response['feed']['entry'])
                if starting == 0:
                    total_results = response['feed']['opensearch:totalResults']
                    # logger.info('Search request for the %s month has been successfully submitted -- URL: %s',
                    # fist_day.split('-')[1], url_pagination)
                    # logger.info('Total results: %s', total_results)
                resp.close()
                break
            else:
                logging.info('Something happened: \tStatus Code: %d, \tReason: %s,', resp.status_code,
                             resp.reason)
                logging.info('URL: %s' % url)
                time.sleep(300)
                x = 1
                break

        if x == 1:
            break
        cnt = 0
        for prod in range(len(response['feed']['entry'])):
                cnt+=1
                #try:
                # get str metadata
                meta_str = {meta['name']: meta['content'] for meta in response['feed']['entry'][prod]['str']}
                print response[

...
'''

#search_spacenoa_s1(aoi)
#search_scihub_s5(aoi)
#search_austria_s1(aoi)
#search_sara_s1(aoi)
#search_portugal_s1(aoi)
#search_sedas_s1(aoi)
#search_nsdc_s1(aoi)
#search_colhub_s1(aoi)

os.environ.setdefault("DJANGO_SETTINGS_MODULE","eopen.settings")
import django
django.setup()
import models
scores = {}
for hub in models.hubs.objects.all():
    print hub

print scores


'''

test_url = "https://scihub.copernicus.eu/dhus/odata/v1/Products('daacd7ae-4c57-4c85-b7ee-8ec401b1e890')/$value"
test_checksum = "https://scihub.copernicus.eu/dhus/odata/v1/Products('daacd7ae-4c57-4c85-b7ee-8ec401b1e890')/Checksum/Value/$value"
ws_tmp = '/mnt/mirrorsite/data/recap_modeling/Lithuania_2018Final/test'
import os


def scihub_credentials():

    sci_user = "thanasisdrivas"
    sci_passwd = "Nopassaran123"
    sci_url = "https://scihub.copernicus.eu"

    return (sci_user, sci_passwd, sci_url)


sci_user,sci_passwd, sci_url = scihub_credentials()
while True:
    session = requests.Session()
    session.auth = (sci_user, sci_passwd)
    session.stream = True
    resp = session.get(test_url)
    if resp.status_code == 200:
        logging.info('Session status code: %d of ', resp.status_code)
        break
    else:
        logging.info('Something happened: \tStatus Code: %d, \tReason: %s, \tFilename: %s ',resp.status_code, resp.reason, p.filename)
        time.sleep(300)

ws_tmp = '/mnt/mirrorsite/data/recap_modeling/Lithuania_2018Final/test'
import requests
import time

CHUNK_SIZE = 2**12  # Bytes
TIME_EXPIRE = time.time() + 5 # Seconds


data = ''
buffer = resp.raw.read(CHUNK_SIZE)
while buffer:
    data += buffer
    buffer = resp.raw.read(CHUNK_SIZE)

    if TIME_EXPIRE < time.time():
        # Quit after 5 seconds.
        data += buffer
        break

resp.raw.release_conn()

print "Read %s bytes out of %s expected." % (len(data), resp.headers.get('content-length'))
'''

