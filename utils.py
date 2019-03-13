import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","eopen.settings")
import django
django.setup()
import logger
import logging
import requests
import time
import types
import time
from datetime import datetime, date, timedelta
from harvest.models import hubs_lastaccess,sentinel3_Products,sentinel2_Products,sentinel1_Products,hubs,hubs_credentials
from django.contrib.gis.geos import GEOSGeometry
from django.utils import timezone
import numpy as np
from django.contrib.gis.geos import MultiPolygon


def tests1(aoi):

    from xml.etree import ElementTree

    currentresults = 0
    for h in hubs.objects.filter(hubname='scihub'):
        sci_url = h.hublink
        lastdate = hubs_lastaccess.objects.get(hubid_id= h.id).accessdate
        for hc in hubs_credentials.objects.filter(hub_id=h.id):
            sci_user=hc.username
            sci_passwd = hc.password
            break
    lday = lastdate.day
    lmonth = lastdate.month
    lyear = lastdate.year
    cday, cmonth, cyear = current_time()
    fist_day = date(2018, 1, 1).strftime('%Y-%m-%d')
    last_day = date(cyear, cmonth, cday).strftime('%Y-%m-%d')
    print "Searching from ", fist_day, " to ", last_day
    url = sci_url
    #url += '/dhus/odata/v1/DeletedProducts'#/search?q='
    url += '/dhus/odata/v1/Products?$filter=Online eq false'#/search?q='

    #url += '*34SFJ* AND '
    #url += 'footprint:"Intersects(' + aoi + ')" '
    #url += 'beginPosition:[' + fist_day + 'T00:00:00.000Z TO ' + last_day + 'T23:59:59.999Z] '
    #url += 'AND endPosition:[' + fist_day + 'T00:00:00.000Z TO ' + last_day + 'T23:59:59.999Z] '
    #url += 'platformname:Sentinel-1 '
    #url += '&format=json'
    retrieving_products = {}
    session = requests.Session()
    session.auth = (sci_user, sci_passwd)
    session.stream = True
    starting = -100
    resp = session.get(url)
    print resp.status_code
    if resp.status_code == 200:
        max_pagination_count = 100
        currentresults = 0
        while max_pagination_count == 100:
            x = 0
            while True:
                # set starting point, increasing every time by 100
                starting += max_pagination_count
                #url_pagination = url + '&start=%d&rows=100' % starting
                session = requests.Session()
                session.auth = (sci_user, sci_passwd)
                session.stream = True
                resp = session.get(url)
                if resp.status_code == 200:
                    import xmltodict,json
                    o = xmltodict.parse(resp.raw)
                    a = json.loads(json.dumps(o))
                    cnt = 0
                    for item in a['feed']['entry']:
                        cnt+=1
                        print item['content']
                    print cnt
                    exit()
                    tree = ElementTree.parse(resp.raw)
                    root = ElementTree.fromstring(resp.raw)
                    for item in root:
                        if item.text:
                            print item.text


                    try:
                        max_pagination_count = len(response['feed']['entry'])
                    except:
                        x = 1
                        resp.close()
                        break
                    currentresults += max_pagination_count
                    print currentresults
                    if starting == 0:
                        print "Hello"
                        total_results = response['feed']['opensearch:totalResults']
                    resp.close()
                    break
                else:
                    x = 1

                    logging.info('Something happened: \tStatus Code: %d, \tReason: %s,', resp.status_code,
                                 resp.reason)
                    logging.info('URL: %s' % url)
                    break
                    time.sleep(300)

            if x == 1:
                print "Something went wrong on response"
                break
            print round(currentresults/float(total_results)*100,2),"%"

def get_details(hub,product):
    for h in hubs.objects.filter(hubname=hub):
        sci_url = h.hublink
        lastdate = hubs_lastaccess.objects.get(hubid_id=h.id,product=product).accessdate
        for hc in hubs_credentials.objects.filter(hub_id=h.id):
            sci_user = hc.username
            sci_passwd = hc.password
            break
    return sci_user,sci_passwd,lastdate,sci_url

def date_details(adate):
    return adate.day,adate.month,adate.year



### Sentinel 1 search functions ###
def search_scihub_s1(aoi):

    #get important details for hub
    sci_user, sci_passwd, lastdate, sci_url = get_details('scihub','s1')

    #get date info from last time api was active
    lday,lmonth,lyear = date_details(lastdate)

    currentresults = 0

    #format last access time point
    lastime = 'T' + str(lastdate.time()) + 'Z'
    starting_date = str(lastdate.date()) + lastime

    # keep info in order to update last access time point
    h = hubs_lastaccess.objects.get(hubid_id=2, product='s1')
    h.accessdate = datetime.now(tz=timezone.utc)

    # construct url for API
    logging.info("Start searching scihub from %s",starting_date)
    url = sci_url
    url += '/dhus/search?q='
    url += 'ingestiondate:[' + starting_date + ' TO NOW] '
    url += 'platformname:Sentinel-1 '
    url += '&format=json'

    #ready to ask for products
    retrieving_products = {}
    products = {}
    starting = -100
    max_pagination_count = 100
    logging.info("Collecting S1 metadata...")

    #results are in multiple pages, 100 per page
    while max_pagination_count == 100:
        stop = 0
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
                try:
                    max_pagination_count = len(response['feed']['entry'])
                except:
                    stop = 1
                    resp.close()
                    break
                currentresults += max_pagination_count
                if starting == 0:
                    total_results = response['feed']['opensearch:totalResults']
                resp.close()
                break
            else:
                stop = 1
                break
                logging.info('Something happened: \tStatus Code: %d, \tReason: %s,', resp.status_code,resp.reason)
                logging.info('URL: %s' % url)
                time.sleep(300)

        if stop == 1:
            break

        logging.info("Completed %f percent",round(currentresults/float(total_results)*100,2))

        #get data for every product in response
        for prod in range(len(response['feed']['entry'])):
            try:
                # get str metadata
                meta_str = {meta['name']: meta['content'] for meta in response['feed']['entry'][prod]['str']}
                wkt_footprint = meta_str['footprint']

                if not 'MULTI' in wkt_footprint:
                    x = GEOSGeometry(wkt_footprint, srid=4326)
                    geom_footprint = MultiPolygon(x, srid=4326)
                else:
                    geom_footprint = GEOSGeometry(wkt_footprint, srid=4326)

                identifier = meta_str['identifier']
                meta_date = {meta['name']: meta['content'] for meta in response['feed']['entry'][prod]['date']}
                try:
                    swath = meta_str['swathidentifier']
                except:
                    swath = ''

                quicklook = ''

                selected_metadata = {
                    'uuid': meta_str['uuid'],
                    'identifier': identifier,
                    'wkt_footprint':wkt_footprint,
                    'filename': meta_str['filename'],
                    'instrument': meta_str['instrumentshortname'],
                    'product_type': meta_str['producttype'],
                    'sensing_date': meta_date['beginposition'],
                    'ingestion_date': meta_date['ingestiondate'],
                    'orbit_number': response['feed']['entry'][prod]['int'][0]['content'],
                    'relative_orbit_number': response['feed']['entry'][prod]['int'][1]['content'],
                    'pass_direction': meta_str['orbitdirection'],
                    'size': meta_str['size'],
                    'polarization':meta_str['polarisationmode'],
                    'swath': swath,
                    'quicklook':quicklook,
                    'geom_footprint':geom_footprint,
                    'sensor':meta_str['sensoroperationalmode'],
                    'url_download': response['feed']['entry'][prod]['link'][0]['href'],
                    'url_checksum': response['feed']['entry'][prod]['link'][0]['href'][
                                    :-6] + 'Checksum/Value/$value',
                }
                k = (identifier[11:])
                products[k] = selected_metadata
            except Exception as e:
                print "Exception:",e
                continue

    #end of multiple pages results => store them to db
    retrieving_products[1] = products
    cnt = 0
    # save the products
    for m, p in retrieving_products.items():
        for t, data in p.items():
            p = sentinel1_Products(
                uuid=data['uuid'],
                identifier=data['identifier'],
                filename=data['filename'],
                url_download=data['url_download'],
                url_checksum=data['url_checksum'],
                instrument=data['instrument'],
                product_type=data['product_type'],
                sensing_date=data['sensing_date'],
                ingestion_date=data['ingestion_date'],
                orbit_number=data['orbit_number'],
                relative_orbit_number=data['relative_orbit_number'],
                pass_direction=data['pass_direction'],
                wkt_footprint=data['wkt_footprint'],
                size=data['size'],
                source=sci_url,
                sensor_operational_mode=data['sensor'],
                polarization=data['polarization'],
                swath=data['swath'],
                score=0,
                geom_footprint=data['geom_footprint'],
                source2_id=2,
                quicklook = data['quicklook']
            )

            #if not sentinel1_Products.objects.filter(source=sci_url, filename=data['filename']).exists():
            #if not (p.identifier,p.source) in stored:
            p.save()
            cnt+=1
    #if everything is ok, update last access time for the specific hub
    if cnt>0:
        h.save()

    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(level=logging.INFO, filename="/home/userdev/eopen.log")
    logging.info("Sentinel 2 - Search, New Products:%d" %(cnt))

def search_spacenoa_s1(aoi):

    # get important details for hub
    sci_user, sci_passwd, lastdate, sci_url = get_details('noa','s1')

    # get date info from last time api was active
    lday, lmonth, lyear = date_details(lastdate)

    currentresults = 0

    # format last access time point
    lastime = 'T' + str(lastdate.time()) + 'Z'
    starting_date = str(lastdate.date()) + lastime

    # construct url for API
    logging.info("Start searching Greek Mirror from %s", starting_date)
    url = sci_url
    url += '/dhus/search?q='
    url += 'ingestiondate:[' + starting_date + ' TO NOW] '
    url += 'platformname:Sentinel-1 '
    url += '&format=json'

    # ready to ask for products
    retrieving_products = {}
    products = {}
    starting = -100
    max_pagination_count = 100
    logging.info("Collecting S1 metadata...")
    c1 = 0
    c2 = 0
    # results are in multiple pages, 100 per page
    while max_pagination_count == 100:
        stop = 0
        while True:
            # set starting point, increasing every time by 100
            starting += max_pagination_count
            url_pagination = url + '&start=%d&rows=100' % starting
            session = requests.Session()
            session.auth = (sci_user, sci_passwd)
            session.stream = True
            resp = session.get(url_pagination)
            if resp.status_code == 200:
                # update last access time point
                h = hubs_lastaccess.objects.get(hubid_id=3,product='s1')
                h.accessdate = datetime.now(tz=timezone.utc)
                h.save()
                #exit()
                response = resp.json()
                try:
                    max_pagination_count = len(response['feed']['entry'])
                except:
                    stop = 1
                    resp.close()
                    break
                currentresults += max_pagination_count
                if starting == 0:
                    total_results = response['feed']['opensearch:totalResults']
                resp.close()
                break
            else:
                stop = 1
                break
                logging.info('Something happened: \tStatus Code: %d, \tReason: %s,', resp.status_code, resp.reason)
                logging.info('URL: %s' % url)
                time.sleep(300)

        if stop == 1:
            break
        cnt = 0
        logging.info("Completed %f percent", round(currentresults / float(total_results) * 100, 2))

        cnt = 0
        for prod in range(len(response['feed']['entry'])):
            cnt += 1
            try:
                meta_str = {meta['name']: meta['content'] for meta in response['feed']['entry'][prod]['str']}
                wkt_footprint = meta_str['footprint']

                if not 'MULTI' in wkt_footprint:
                    x = GEOSGeometry(wkt_footprint, srid=4326)
                    geom_footprint = MultiPolygon(x, srid=4326)
                else:
                    geom_footprint = GEOSGeometry(wkt_footprint, srid=4326)

                identifier = meta_str['identifier']
                meta_date = {meta['name']: meta['content'] for meta in response['feed']['entry'][prod]['date']}
                try:
                    swath = meta_str['swathidentifier']
                except:
                    swath = ''

                selected_metadata = {
                    'uuid': meta_str['uuid'],
                    'identifier': identifier,
                    'filename': meta_str['filename'],
                    'instrument': meta_str['instrumentshortname'],
                    'product_type': meta_str['producttype'],
                    'sensing_date': meta_date['beginposition'],
                    'ingestion_date': meta_date['ingestiondate'],
                    'orbit_number': response['feed']['entry'][prod]['int'][0]['content'],
                    'relative_orbit_number': response['feed']['entry'][prod]['int'][1]['content'],
                    'pass_direction': meta_str['orbitdirection'],
                    'size': meta_str['size'],
                    'polarization': meta_str['polarisationmode'],
                    'sensor': meta_str['sensoroperationalmode'],
                    'url_download': response['feed']['entry'][prod]['link'][0]['href'],
                    'url_checksum': response['feed']['entry'][prod]['link'][0]['href'][
                                    :-6] + 'Checksum/Value/$value',
                    'wkt_footprint': wkt_footprint,
                    'swath' : swath,
                    'geom_footprint': geom_footprint,
                }
                k = (identifier[11:])
                products[k] = selected_metadata
            except:
                # exc_type, exc_obj, exc_tb = sys.exc_info()
                logging.info("Error in metadata response")
                continue

    retrieving_products[1] = products
    start_time = time.time()
    cnt = 0
    print len
    # save the products
    for m, p in retrieving_products.items():
        for t, data in p.items():
            p = sentinel1_Products(
                uuid=data['uuid'],
                identifier=data['identifier'],
                filename=data['filename'],
                url_download=data['url_download'],
                url_checksum=data['url_checksum'],
                instrument=data['instrument'],
                product_type=data['product_type'],
                sensing_date=data['sensing_date'],
                ingestion_date=data['ingestion_date'],
                orbit_number=data['orbit_number'],
                relative_orbit_number=data['relative_orbit_number'],
                pass_direction=data['pass_direction'],
                wkt_footprint=data['wkt_footprint'],
                size=data['size'],
                source=sci_url,
                sensor_operational_mode=data['sensor'],
                polarization=data['polarization'],
                swath=data['swath'],
                score=0,
                geom_footprint=data['geom_footprint']
            )

            # if not sentinel1_Products.objects.filter(source=sci_url, filename=data['filename']).exists():
            # if not (p.identifier,p.source) in stored:
            p.save()
            cnt += 1
    logging.info("New Products:%d", cnt)

def search_finhub_s1(aoi):

    #get important details for hub
    sci_user, sci_passwd, lastdate, sci_url = get_details('finhub','s1')

    #get date info from last time api was active
    lday,lmonth,lyear = date_details(lastdate)

    currentresults = 0

    #format last access time point
    lastime = 'T' + str(lastdate.time()) + 'Z'
    starting_date = str(lastdate.date()) + lastime


    # construct url for API
    logging.info("Start searching Finhub from %s",starting_date)
    url = sci_url
    url += '/search?q='
    url += 'ingestiondate:[' + starting_date + ' TO NOW] '
    url += 'platformname:Sentinel-1 '
    url += '&format=json'

    #ready to ask for products
    retrieving_products = {}
    products = {}
    starting = -100
    max_pagination_count = 100
    logging.info("Collecting S1 metadata ...")

    #results are in multiple pages, 100 per page
    while max_pagination_count == 100:
        stop = 0
        while True:
            # set starting point, increasing every time by 100
            starting += max_pagination_count
            url_pagination = url + '&start=%d&rows=100' % starting
            session = requests.Session()
            session.auth = (sci_user, sci_passwd)
            session.stream = True
            resp = session.get(url_pagination)
            if resp.status_code == 200:

                # update last access time point
                h = hubs_lastaccess.objects.get(hubid_id=1,product='s1')
                h.accessdate = datetime.now(tz=timezone.utc)
                h.save()

                response = resp.json()
                try:
                    max_pagination_count = len(response['feed']['entry'])
                except:
                    stop = 1
                    resp.close()
                    break
                currentresults += max_pagination_count
                if starting == 0:
                    total_results = response['feed']['opensearch:totalResults']
                resp.close()
                break
            else:
                stop = 1
                break
                logging.info('Something happened: \tStatus Code: %d, \tReason: %s,', resp.status_code,resp.reason)
                logging.info('URL: %s' % url)
                time.sleep(300)

        if stop == 1:
            break
        cnt = 0
        logging.info("Completed %f percent",round(currentresults/float(total_results)*100,2))


        #get data for every product in response
        for prod in range(len(response['feed']['entry'])):
            cnt+=1
            try:
                # get str metadata
                meta_str = {meta['name']: meta['content'] for meta in response['feed']['entry'][prod]['str']}
                wkt_footprint = meta_str['footprint']

                if not 'MULTI' in wkt_footprint:
                    x = GEOSGeometry(wkt_footprint, srid=4326)
                    geom_footprint = MultiPolygon(x, srid=4326)
                else:
                    geom_footprint = GEOSGeometry(wkt_footprint, srid=4326)

                identifier = meta_str['identifier']
                meta_date = {meta['name']: meta['content'] for meta in response['feed']['entry'][prod]['date']}
                try:
                    swath = meta_str['swathidentifier']
                except:
                    swath = ''
                selected_metadata = {
                    'uuid': meta_str['uuid'],
                    'identifier': identifier,
                    'wkt_footprint':wkt_footprint,
                    'filename': meta_str['filename'],
                    'instrument': meta_str['instrumentshortname'],
                    'product_type': meta_str['producttype'],
                    'sensing_date': meta_date['beginposition'],
                    'ingestion_date': meta_date['ingestiondate'],
                    'orbit_number': response['feed']['entry'][prod]['int'][0]['content'],
                    'relative_orbit_number': response['feed']['entry'][prod]['int'][1]['content'],
                    'pass_direction': meta_str['orbitdirection'],
                    'size': meta_str['size'],
                    'polarization':meta_str['polarisationmode'],
                    'swath': swath,
                    'geom_footprint': geom_footprint,
                    'sensor':meta_str['sensoroperationalmode'],
                    'url_download': response['feed']['entry'][prod]['link'][0]['href'],
                    'url_checksum': response['feed']['entry'][prod]['link'][0]['href'][
                                    :-6] + 'Checksum/Value/$value',
                }
                k = (identifier[11:])
                products[k] = selected_metadata
            except Exception as e:
                print "Exception:",e
                continue

    retrieving_products[1] = products
    start_time = time.time()

    cnt = 0
    # save the products
    for m, p in retrieving_products.items():
        for t, data in p.items():
            p = sentinel1_Products(
                uuid=data['uuid'],
                identifier=data['identifier'],
                filename=data['filename'],
                url_download=data['url_download'],
                url_checksum=data['url_checksum'],
                instrument=data['instrument'],
                product_type=data['product_type'],
                sensing_date=data['sensing_date'],
                ingestion_date=data['ingestion_date'],
                orbit_number=data['orbit_number'],
                relative_orbit_number=data['relative_orbit_number'],
                pass_direction=data['pass_direction'],
                wkt_footprint=data['wkt_footprint'],
                size=data['size'],
                source=sci_url,
                sensor_operational_mode=data['sensor'],
                polarization=data['polarization'],
                swath=data['swath'],
                score=0,
                geom_footprint=data['geom_footprint']
            )

            #if not sentinel1_Products.objects.filter(source=sci_url, filename=data['filename']).exists():
            #if not (p.identifier,p.source) in stored:
            p.save()
            cnt+=1
    logging.info("New Products:%d",cnt)

### Sentinel 2 search functions ###

def search_scihub_s2(aoi):
    # get important details for hub
    sci_user, sci_passwd, lastdate, sci_url = get_details('scihub', 's2')

    # get date info from last time api was active
    lday, lmonth, lyear = date_details(lastdate)

    currentresults = 0

    # format last access time point
    lastime = 'T' + str(lastdate.time()) + 'Z'
    starting_date = str(lastdate.date()) + lastime

    # construct url for API
    #logging.info("Start searching from %s", starting_date)
    url = sci_url
    url += '/dhus/search?q='
    #url += 'ingestiondate:[' + starting_date + ' TO NOW] '
    url += 'beginPosition:[' + '2018-05-01' + 'T00:00:00.000Z TO ' + '2018-05-31' + 'T23:59:59.999Z] '
    url += 'AND endPosition:[' + '2018-05-01' + 'T00:00:00.000Z TO ' + '2018-05-31' + 'T23:59:59.999Z] '
    url += 'platformname:Sentinel-2 '
    url += '&format=json'

    # ready to ask for products
    retrieving_products = {}
    products = {}
    starting = -100
    max_pagination_count = 100
    logging.info("Collecting results...")
    currentresults = 0
    current_page = 0
    while max_pagination_count == 100:
        current_page+=1
        stop = 0
        while True:
            starting += max_pagination_count
            url_pagination = url + '&start=%d&rows=100' % starting
            session = requests.Session()
            session.auth = (sci_user, sci_passwd)
            session.stream = True
            resp = session.get(url_pagination)
            if resp.status_code == 200:

                # update last access time point
                h = hubs_lastaccess.objects.get(hubid_id=2, product='s2')
                h.accessdate = datetime.now(tz=timezone.utc)
                #h.save()

                response = resp.json()

                try:
                    max_pagination_count = len(response['feed']['entry'])
                except:
                    stop = 1
                    resp.close()
                    break

                currentresults += max_pagination_count

                if starting == 0:
                    total_results = response['feed']['opensearch:totalResults']
                    print total_results
                    pages = int(total_results)/100
                resp.close()
                break
            else:
                logging.info('Something happened: \tStatus Code: %d, \tReason: %s,', resp.status_code,
                             resp.reason)
                logging.info('URL: %s' % url)
                stop = 1
                break
        if stop == 1:
            break
        print current_page,'/',pages
        #print round(currentresults/float(total_results)*100,2),"%"

        for prod in range(len(response['feed']['entry'])):
            try:
                # get str metadata

                meta_str = {meta['name']: meta['content'] for meta in response['feed']['entry'][prod]['str']}
                quicklook = response['feed']['entry'][prod]['link'][2]['href']

                # get tile object
                identifier = meta_str['identifier']

                selected_tile = get_s2_new_naming_convention(identifier)[-2]

                wkt_footprint = meta_str['footprint']

                # geom_footprint = GEOSGeometry(wkt_footprint, srid=4326)

                if not 'MULTI' in wkt_footprint:
                    x = GEOSGeometry(wkt_footprint, srid=4326)
                    geom_footprint = MultiPolygon(x, srid=4326)
                else:
                    geom_footprint = GEOSGeometry(wkt_footprint, srid=4326)

                meta_date = {meta['name']: meta['content'] for meta in response['feed']['entry'][prod]['date']}
                # get cloud coverage metadata
                try:
                    if type(response['feed']['entry'][prod]['double']) is types.DictType:
                        cloud_coverage = float(response['feed']['entry'][prod]['double']['content'])
                    elif type(response['feed']['entry'][prod]['double']) is types.ListType:
                        meta_double = {meta['name']: meta['content'] for meta in
                                       response['feed']['entry'][prod]['double']}
                        cloud_coverage = float(meta_double['cloudcoverpercentage'])
                except Exception as e:
                    print e
                    cloud_coverage = None
                    logging.debug('Sentinel 2 Searching - Exception on cloud coverage %s' %(e))
                #print "Cloud",cloud_coverage
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
                    'tile_name': selected_tile,
                    'wkt_footprint': wkt_footprint,
                    'geom_footprint': geom_footprint,
                    'quicklook':quicklook,
                    'source2_id':2

                }
                k = (meta_str['uuid'])
                products[k] = selected_metadata
            except Exception as e:
                print "problem",e
                continue

    print len(products)
    retrieving_products[1] = products
    cnt = 0
    # save the products
    for m, p in retrieving_products.items():
        for t, data in p.items():
            try:
                p = sentinel2_Products(
                    uuid=data['uuid'],
                    identifier=data['identifier'],
                    filename=data['filename'],
                    url_download=data['url_download'],
                    url_checksum=data['url_checksum'],
                    instrument=data['instrument'],
                    product_type=data['product_type'],
                    sensing_date=data['sensing_date'],
                    ingestion_date=data['ingestion_date'],
                    orbit_number=data['orbit_number'],
                    relative_orbit_number=data['relative_orbit_number'],
                    pass_direction=data['pass_direction'],
                    wkt_footprint=data['wkt_footprint'],
                    cloud_coverage=data['cloud_cover_percentage'],
                    size=data['size'],
                    tile_name=data['tile_name'],
                    source=sci_url,
                    geom_footprint=data['geom_footprint'],
                    score=0,
                    quicklook=data['quicklook'],
                    source2_id=2
                )
                cnt+=1
                p.save()
            except Exception as e:
                print e
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(level=logging.INFO, filename="/home/userdev/eopen.log")
    logging.info("Sentinel 2 - Search, New Products:%d" % (cnt))


def search_spacenoa_s2(aoi):

    # get important details for hub
    sci_user, sci_passwd, lastdate, sci_url = get_details('noa','s2')

    # get date info from last time api was active
    lday, lmonth, lyear = date_details(lastdate)

    currentresults = 0

    # format last access time point
    lastime = 'T' + str(lastdate.time()) + 'Z'
    starting_date = str(lastdate.date()) + lastime

    # construct url for API
    logging.info("Start searching from %s", starting_date)
    url = sci_url
    url += '/dhus/search?q='
    # url += 'footprint:"Intersects(' + aoi + ')" '
    url += 'ingestiondate:[' + starting_date + ' TO NOW] '
    url += 'platformname:Sentinel-2 '
    url += '&format=json'

    # ready to ask for products
    retrieving_products = {}
    products = {}
    starting = -100
    max_pagination_count = 100
    logging.info("Collecting results...")
    currentresults = 0

    while max_pagination_count == 100:

        stop = 0
        while True:
            # set starting point, increasing every time by 100
            starting += max_pagination_count
            url_pagination = url + '&start=%d&rows=100' % starting
            session = requests.Session()
            session.auth = (sci_user, sci_passwd)
            session.stream = True
            resp = session.get(url_pagination)

            if resp.status_code == 200:
                # update last access time point
                h = hubs_lastaccess.objects.get(hubid_id=3, product='s2')
                h.accessdate = datetime.now(tz=timezone.utc)
                #h.save()

                response = resp.json()
                for meta in response['feed']['entry'][1]:#['title']:#['']:
                    print meta

                resp.close()
                exit()
                try:
                    max_pagination_count = len(response['feed']['entry'])
                except:
                    stop = 1
                    break
                resp.close()
                break
            else:
                logging.info('Something happened: \tStatus Code: %d, \tReason: %s,', resp.status_code,
                             resp.reason)
                logging.info('URL: %s' % url)
                stop = 1
                break

        if stop == 1:
            break

        cnt = 0
        for prod in range(len(response['feed']['entry'])):
            cnt+=1
            try:
                # get str metadata
                meta_str = {meta['name']: meta['content'] for meta in response['feed']['entry'][prod]['str']}
                # get tile object
                identifier = meta_str['identifier']

                tile = get_s2_new_naming_convention(identifier)[-2]

                meta_date = {meta['name']: meta['content'] for meta in response['feed']['entry'][prod]['date']}
                # get cloud coverage metadata
                wkt_footprint = meta_str['footprint']

                if not 'MULTI' in wkt_footprint:
                    x = GEOSGeometry(wkt_footprint, srid=4326)
                    geom_footprint = MultiPolygon(x, srid=4326)
                else:
                    geom_footprint = GEOSGeometry(wkt_footprint, srid=4326)


                selected_metadata = {
                    'uuid': meta_str['uuid'],
                    'identifier': identifier,
                    'filename': meta_str['filename'],
                    'instrument': meta_str['instrumentshortname'],
                    'product_type': meta_str['producttype'],
                    'sensing_date': meta_date['beginposition'],
                    'ingestion_date': meta_date['ingestiondate'],
                    'wkt_footprint':geom_footprint,
                    'orbit_number': response['feed']['entry'][prod]['int'][0]['content'],
                    'relative_orbit_number': response['feed']['entry'][prod]['int'][1]['content'],
                    'pass_direction': meta_str['orbitdirection'],
                    'size': meta_str['size'],
                    'tile_name': tile,
                    'geom_footprint':geom_footprint,
                    'url_download': response['feed']['entry'][prod]['link'][0]['href'],
                    'url_checksum': response['feed']['entry'][prod]['link'][0]['href'][
                                    :-6] + 'Checksum/Value/$value',
                }

                k = (tile, identifier[11:])
                products[k] = selected_metadata
            except:
                #exc_type, exc_obj, exc_tb = sys.exc_info()
                #logging.info("No problem")
                continue

    retrieving_products[1] = products

    # save the products
    for m, p in retrieving_products.items():
        for t, data in p.items():
            p = sentinel2_Products(
                uuid=data['uuid'],
                identifier=data['identifier'],
                filename=data['filename'],
                url_download=data['url_download'],
                url_checksum=data['url_checksum'],
                instrument=data['instrument'],
                product_type=data['product_type'],
                sensing_date=data['sensing_date'],
                ingestion_date=data['ingestion_date'],
                orbit_number=data['orbit_number'],
                relative_orbit_number=data['relative_orbit_number'],
                pass_direction=data['pass_direction'],
                wkt_footprint=data['wkt_footprint'],
                size=data['size'],
                tile_name=data['tile_name'],
                source = sci_url,
                score = 0,
                geom_footprint=data['geom_footprint']
            )
            p.save()

def search_finhub_s2(aoi):

    # get important details for hub
    sci_user, sci_passwd, lastdate, sci_url = get_details('finhub','s2')

    # get date info from last time api was active
    lday, lmonth, lyear = date_details(lastdate)

    currentresults = 0

    # format last access time point
    lastime = 'T' + str(lastdate.time()) + 'Z'
    starting_date = str(lastdate.date()) + lastime

    # construct url for API
    logging.info("Start searching from %s", starting_date)
    url = sci_url
    url += '/search?q='
    # url += 'footprint:"Intersects(' + aoi + ')" '
    url += 'ingestiondate:[' + starting_date + ' TO NOW] '
    url += 'platformname:Sentinel-2 '
    url += '&format=json'

    # ready to ask for products
    retrieving_products = {}
    products = {}
    starting = -100
    max_pagination_count = 100
    logging.info("Collecting results...")
    currentresults = 0


    while max_pagination_count == 100:

        stop = 0
        while True:
            # set starting point, increasing every time by 100
            starting += max_pagination_count
            url_pagination = url + '&start=%d&rows=100' % starting
            session = requests.Session()
            session.auth = (sci_user, sci_passwd)
            session.stream = True
            resp = session.get(url_pagination)
            if resp.status_code == 200:

                # update last access time point
                h = hubs_lastaccess.objects.get(hubid_id=1, product='s2')
                h.accessdate = datetime.now(tz=timezone.utc)
                h.save()

                response = resp.json()
                try:
                    max_pagination_count = len(response['feed']['entry'])
                except:
                    stop = 1
                resp.close()
                break
            else:
                logging.info('Something happened: \tStatus Code: %d, \tReason: %s,', resp.status_code,
                             resp.reason)
                logging.info('URL: %s' % url)
                stop = 1
                break

        if stop == 1:
            break

        cnt = 0
        for prod in range(len(response['feed']['entry'])):
            cnt += 1
            try:
                # get str metadata
                meta_str = {meta['name']: meta['content'] for meta in
                            response['feed']['entry'][prod]['str']}
                # get tile object
                identifier = meta_str['identifier']
                tile = get_s2_new_naming_convention(identifier)[-2]

                meta_date = {meta['name']: meta['content'] for meta in
                             response['feed']['entry'][prod]['date']}
                # get cloud coverage metadata
                wkt_footprint = meta_str['footprint']
                wkt2 = GEOSGeometry(wkt_footprint, srid=4326)
                if not 'MULTI' in wkt_footprint:
                    x = GEOSGeometry(wkt_footprint, srid=4326)
                    geom_footprint = MultiPolygon(x, srid=4326)
                else:
                    geom_footprint = GEOSGeometry(wkt_footprint, srid=4326)

                selected_metadata = {
                    'uuid': meta_str['uuid'],
                    'identifier': identifier,
                    'filename': meta_str['filename'],
                    'instrument': meta_str['instrumentshortname'],
                    'product_type': meta_str['producttype'],
                    'sensing_date': meta_date['beginposition'],
                    'ingestion_date': meta_date['ingestiondate'],
                    'wkt_footprint': wkt2,
                    'orbit_number': response['feed']['entry'][prod]['int'][0]['content'],
                    'relative_orbit_number': response['feed']['entry'][prod]['int'][1]['content'],
                    'pass_direction': meta_str['orbitdirection'],
                    'size': meta_str['size'],
                    'tile_name': tile,
                    'geom_footprint': geom_footprint,
                    'url_download': response['feed']['entry'][prod]['link'][0]['href'],
                    'url_checksum': response['feed']['entry'][prod]['link'][0]['href'][
                                    :-6] + 'Checksum/Value/$value',
                }

                k = (tile, identifier[11:])
                products[k] = selected_metadata



            except:
                # exc_type, exc_obj, exc_tb = sys.exc_info()
                # logging.info("No problem")
                continue

    retrieving_products[1] = products

    # save the products
    for m, p in retrieving_products.items():
        for t, data in p.items():
            p = sentinel2_Products(
                uuid=data['uuid'],
                identifier=data['identifier'],
                filename=data['filename'],
                url_download=data['url_download'],
                url_checksum=data['url_checksum'],
                instrument=data['instrument'],
                product_type=data['product_type'],
                sensing_date=data['sensing_date'],
                ingestion_date=data['ingestion_date'],
                orbit_number=data['orbit_number'],
                relative_orbit_number=data['relative_orbit_number'],
                pass_direction=data['pass_direction'],
                wkt_footprint=data['wkt_footprint'],
                size=data['size'],
                tile_name=data['tile_name'],
                source=sci_url,
                score=0,
                geom_footprint=data['geom_footprint']
            )
            p.save()

### Sentinel 3 search functions ###

def search_scihub_s3(aoi):
    # ready to ask for products
    retrieving_products = {}
    products = {}

    for h in hubs.objects.filter(hubname='scihub'):
        sci_url = h.hublink
        for hc in hubs_credentials.objects.filter(hub_id=h.id):
            sci_user=hc.username
            sci_passwd = hc.password
            break

    cday, cmonth, cyear = current_time()
    for month in range(12, 13):
        if month == 2:
            day = 28
        elif (month % 2 == 0 and month <= 7) or (month % 2 == 1 and month > 7):
            day = 30
        else:
            day = 31
        if month == cmonth:
            day = cday
        fist_day = date(2018, month, 1).strftime('%Y-%m-%d')
        last_day = date(2018, month, day).strftime('%Y-%m-%d')
        print "Searching from ", fist_day, " to ", last_day
        url = sci_url
        url += '/dhus/search?q='
        #url += '*34SFJ* AND '
        #url += 'footprint:"Intersects(' + aoi + ')" '
        url += 'beginPosition:[' + fist_day + 'T00:00:00.000Z TO ' + last_day + 'T23:59:59.999Z] '
        url += 'AND endPosition:[' + fist_day + 'T00:00:00.000Z TO ' + last_day + 'T23:59:59.999Z] '
        url += 'platformname:Sentinel-3 '
        url += '&format=json'

        starting = -100
        max_pagination_count = 100
        currentresults = 0
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
                    try:
                        max_pagination_count = len(response['feed']['entry'])
                        goon = 1
                        total_results = response['feed']['opensearch:totalResults']
                        currentresults+=max_pagination_count
                    except:
                        goon = 0
                    if goon == 0:
                        x = 1
                        break
                    # reset max_pagination_count variable, in order to exit from loop or not
                    #total_results = response['feed']['opensearch:totalResults']
                    #logger.info('Search request for the %s month has been successfully submitted -- URL: %s',
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
            print round(currentresults / float(total_results) * 100, 2), "%"
            print total_results
            for prod in range(len(response['feed']['entry'])):

                try:
                    # get str metadata

                    meta_str = {meta['name']: meta['content'] for meta in response['feed']['entry'][prod]['str']}

                    #print response['feed']['entry'][prod]
                    quicklook = response['feed']['entry'][prod]['link'][2]['href']
                    identifier = meta_str['identifier']

                    try:
                        wkt_footprint = meta_str['footprint']


                        # geom_footprint = GEOSGeometry(wkt_footprint, srid=4326)

                        if not 'MULTI' in wkt_footprint:
                            x = GEOSGeometry(wkt_footprint, srid=4326)
                            geom_footprint = MultiPolygon(x, srid=4326)
                        else:
                            geom_footprint = GEOSGeometry(wkt_footprint, srid=4326)
                    except Exception as e:
                        wkt_footprint = None
                        geom_footprint = None


                    #tile = get_s2_new_naming_convention(identifier)[-2]
                    meta_date = {meta['name']: meta['content'] for meta in response['feed']['entry'][prod]['date']}
                    selected_metadata = {
                        'uuid': meta_str['uuid'],
                        'identifier': identifier,
                        'filename': meta_str['filename'],
                        'instrument': meta_str['instrumentshortname'],
                        'product_type': meta_str['producttype'],
                        'product_class':meta_str['productlevel'],
                        'sensing_date': meta_date['beginposition'],
                        'ingestion_date': meta_date['ingestiondate'],
                        'wkt_footprint': wkt_footprint,
                        'orbit_number': response['feed']['entry'][prod]['int'][0]['content'],
                        'relative_orbit_number': response['feed']['entry'][prod]['int'][1]['content'],
                        'pass_direction': meta_str['orbitdirection'],
                        'size': meta_str['size'],
                        'url_download': response['feed']['entry'][prod]['link'][0]['href'],
                        'url_checksum': response['feed']['entry'][prod]['link'][0]['href'][
                                        :-6] + 'Checksum/Value/$value',
                        'sensor_operational_mode': meta_str['sensoroperationalmode'],
                        'timeliness': meta_str['timeliness'],
                        'procfacilityname': meta_str['procfacilityname'],
                        'procfacilityorg': meta_str['procfacilityorg'],
                        'quicklook':quicklook,
                        'geom_footprint':geom_footprint
                    }
                    k = (identifier[11:])
                    products[k] = selected_metadata

                except Exception as e:
                    #exc_type, exc_obj, exc_tb = sys.exc_info()
                    print e
                    continue

        retrieving_products[month] = products
    cnt = 0
    # save the products
    for m, p in retrieving_products.items():
        for t, data in p.items():
            cnt+=1
            p = sentinel3_Products(
                uuid=data['uuid'],
                identifier=data['identifier'],
                filename=data['filename'],
                url_download=data['url_download'],
                url_checksum=data['url_checksum'],
                instrument=data['instrument'],
                product_type=data['product_type'],
                sensing_date=data['sensing_date'],
                ingestion_date=data['ingestion_date'],
                orbit_number=data['orbit_number'],
                relative_orbit_number=data['relative_orbit_number'],
                pass_direction=data['pass_direction'],
                wkt_footprint=data['wkt_footprint'],
                size=data['size'],
                source=sci_url,
                source2_id = 2,
                score=0,
                sensor_operational_mode=data['sensor_operational_mode'],
                timeliness=data['timeliness'],
                procfacilityname=data['procfacilityname'],
                procfacilityorg=data['procfacilityorg'],
                quicklook=data['quicklook'],
                product_class=data['product_class'],
                geom_footprint=data['geom_footprint']
            )
            #if not sentinel3_Products.objects.filter(filename=data['filename'], source=sci_url).exists():
            p.save()
    logdate = str(datetime.now())+'.log'
    logging.info("Scihub - Sentinel 3: Added %s/%s products from %s to %s" %(cnt,total_results,fist_day,last_day))

def search_finhub_s3(aoi):
    for h in hubs.objects.filter(hubname='finhub'):
        sci_url = h.hublink
        for hc in hubs_credentials.objects.filter(hub_id=h.id):
            sci_user=hc.username
            sci_passwd = hc.password
            break
    retrieving_products = {}
    cday, cmonth, cyear = current_time()
    for month in range(12, 13):
        products = {}
        if month == 2:
            day = 28
        elif (month % 2 == 0 and month <= 7) or (month % 2 == 1 and month > 7):
            day = 30
        else:
            day = 31
        if month == cmonth:
            day = cday
        fist_day = date(2019, 1, 1).strftime('%Y-%m-%d')
        last_day = date(2019, 1, 8).strftime('%Y-%m-%d')
        print "Searching from ", fist_day, " to ", last_day
        url = sci_url
        url += '/search?q='
        #url += '*34SFJ* AND '
        #url += 'footprint:"Intersects(' + aoi + ')" '
        url += 'beginPosition:[' + fist_day + 'T00:00:00.000Z TO ' + last_day + 'T23:59:59.999Z] '
        url += 'AND endPosition:[' + fist_day + 'T00:00:00.000Z TO ' + last_day + 'T23:59:59.999Z] '
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
                    try:
                        max_pagination_count = len(response['feed']['entry'])
                        goon = 1
                    except:
                        goon = 0
                    if goon == 0:
                        x = 1
                        break
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
                try:
                    # get str metadata
                    meta_str = {meta['name']: meta['content'] for meta in response['feed']['entry'][prod]['str']}

                    # get tile object
                    identifier = meta_str['identifier']

                    meta_date = {meta['name']: meta['content'] for meta in response['feed']['entry'][prod]['date']}
                    wkt_footprint = meta_str['footprint']
                    #geom_footprint = GEOSGeometry(wkt_footprint, srid=4326)
                    #geom_footprint.transform(3857)


                    selected_metadata = {
                        'uuid': meta_str['uuid'],
                        'identifier': identifier,
                        'filename': meta_str['filename'],
                        'instrument': meta_str['instrumentshortname'],
                        'product_type': meta_str['producttype'],
                        'sensing_date': meta_date['beginposition'],
                        'ingestion_date': meta_date['ingestiondate'],
                        'wkt_footprint':wkt_footprint,
                        'orbit_number': response['feed']['entry'][prod]['int'][0]['content'],
                        'relative_orbit_number': response['feed']['entry'][prod]['int'][1]['content'],
                        'pass_direction': meta_str['orbitdirection'],
                        'size': meta_str['size'],
                        'url_download': response['feed']['entry'][prod]['link'][0]['href'],
                        'url_checksum': response['feed']['entry'][prod]['link'][0]['href'][
                                        :-6] + 'Checksum/Value/$value',
                        'sensor_operational_mode': meta_str['sensoroperationalmode'],
                        'timeliness':meta_str['timeliness'],
                        'procfacilityname':meta_str['procfacilityname'],
                        'procfacilityorg':meta_str['procfacilityorg'],
                    }

                    k = identifier[11:]
                    products[k] = selected_metadata



                except:
                    #exc_type, exc_obj, exc_tb = sys.exc_info()
                    #logging.info("No problem")
                    continue

        retrieving_products[month] = products

    # save the products
    for m, p in retrieving_products.items():
        for t, data in p.items():
            p = sentinel3_Products(
                uuid=data['uuid'],
                identifier=data['identifier'],
                filename=data['filename'],
                url_download=data['url_download'],
                url_checksum=data['url_checksum'],
                instrument=data['instrument'],
                product_type=data['product_type'],
                sensing_date=data['sensing_date'],
                ingestion_date=data['ingestion_date'],
                orbit_number=data['orbit_number'],
                relative_orbit_number=data['relative_orbit_number'],
                pass_direction=data['pass_direction'],
                wkt_footprint=data['wkt_footprint'],
                size=data['size'],
                source = sci_url,
                score = 0,
                sensor_operational_mode = data['sensor_operational_mode'],
                timeliness=data['timeliness'],
                procfacilityname=data['procfacilityname'],
                procfacilityorg=data['procfacilityorg']
            )
            if not sentinel3_Products.objects.filter(filename=data['filename'],source=sci_url).exists():
                p.save()

def search_spacenoa_s3(aoi):
    for h in hubs.objects.filter(hubname='noa'):
        sci_url = h.hublink
        for hc in hubs_credentials.objects.filter(hub_id=h.id):
            sci_user = hc.username
            sci_passwd = hc.password
            break
    retrieving_products = {}
    cday, cmonth, cyear = current_time()
    for month in range(12, 13):
        products = {}
        if month == 2:
            day = 28
        elif (month % 2 == 0 and month <= 7) or (month % 2 == 1 and month > 7):
            day = 30
        else:
            day = 31
        if month == cmonth:
            day = cday
        fist_day = date(2019, 1, 1).strftime('%Y-%m-%d')
        last_day = date(2019, 1, 9).strftime('%Y-%m-%d')
        print "Searching from ", fist_day, " to ", last_day
        url = sci_url
        url += '/dhus/search?q='
        # url += '*34SFJ* AND '
        # url += 'footprint:"Intersects(' + aoi + ')" '
        url += 'beginPosition:[' + fist_day + 'T00:00:00.000Z TO ' + last_day + 'T23:59:59.999Z] '
        url += 'AND endPosition:[' + fist_day + 'T00:00:00.000Z TO ' + last_day + 'T23:59:59.999Z] '
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
                    try:
                        max_pagination_count = len(response['feed']['entry'])
                        goon = 1
                    except:
                        goon = 0
                    if goon == 0:
                        x = 1
                        break
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
                cnt += 1
                try:
                    # get str metadata
                    meta_str = {meta['name']: meta['content'] for meta in
                                response['feed']['entry'][prod]['str']}

                    # get tile object
                    identifier = meta_str['identifier']

                    meta_date = {meta['name']: meta['content'] for meta in
                                 response['feed']['entry'][prod]['date']}
                    wkt_footprint = meta_str['footprint']
                    # geom_footprint = GEOSGeometry(wkt_footprint, srid=4326)
                    # geom_footprint.transform(3857)


                    selected_metadata = {
                        'uuid': meta_str['uuid'],
                        'identifier': identifier,
                        'filename': meta_str['filename'],
                        'instrument': meta_str['instrumentshortname'],
                        'product_type': meta_str['producttype'],
                        'sensing_date': meta_date['beginposition'],
                        'ingestion_date': meta_date['ingestiondate'],
                        'wkt_footprint': wkt_footprint,
                        'orbit_number': response['feed']['entry'][prod]['int'][0]['content'],
                        'relative_orbit_number': response['feed']['entry'][prod]['int'][1]['content'],
                        'pass_direction': meta_str['orbitdirection'],
                        'size': meta_str['size'],
                        'url_download': response['feed']['entry'][prod]['link'][0]['href'],
                        'url_checksum': response['feed']['entry'][prod]['link'][0]['href'][
                                        :-6] + 'Checksum/Value/$value',
                        'sensor_operational_mode': meta_str['sensoroperationalmode'],
                        'timeliness': meta_str['timeliness'],
                        'procfacilityname': meta_str['procfacilityname'],
                        'procfacilityorg': meta_str['procfacilityorg'],
                    }

                    k = identifier[11:]
                    products[k] = selected_metadata



                except:
                    # exc_type, exc_obj, exc_tb = sys.exc_info()
                    # logging.info("No problem")
                    continue

        retrieving_products[month] = products

    # save the products
    for m, p in retrieving_products.items():
        for t, data in p.items():
            p = sentinel3_Products(
                uuid=data['uuid'],
                identifier=data['identifier'],
                filename=data['filename'],
                url_download=data['url_download'],
                url_checksum=data['url_checksum'],
                instrument=data['instrument'],
                product_type=data['product_type'],
                sensing_date=data['sensing_date'],
                ingestion_date=data['ingestion_date'],
                orbit_number=data['orbit_number'],
                relative_orbit_number=data['relative_orbit_number'],
                pass_direction=data['pass_direction'],
                wkt_footprint=data['wkt_footprint'],
                size=data['size'],
                source=sci_url,
                score=0,
                sensor_operational_mode=data['sensor_operational_mode'],
                timeliness=data['timeliness'],
                procfacilityname=data['procfacilityname'],
                procfacilityorg=data['procfacilityorg']
            )
            if not sentinel3_Products.objects.filter(filename=data['filename'], source=sci_url).exists():
                p.save()

### Sentinel 5 search functions ###


### Other helpful functions ###

def get_s2_new_naming_convention(in_name):
    '''Get the NEW format naming convention of Sentinel-2 L1C products - returns list'''

    mission = in_name[0:3]
    product_level = in_name[4:10]
    sensing_timestamp = in_name[11:26]
    processing_baseline_number = in_name[27:32]
    orbit_number = in_name[33:37]
    tile_number_field = in_name[39:44]
    product_discriminator = in_name[45:59]

    return [mission, product_level, sensing_timestamp, processing_baseline_number, orbit_number, tile_number_field,
            product_discriminator]

def current_time():
    tod = date.today()
    month = tod.month
    day = tod.day
    year = tod.year
    return day,month,year

def download_speed(url,user,password):
    try:
        for p in sentinel1_Products.objects.filter(source=url)[:10]:
            test_url = p.url_download
            c = 1
            break
        session = requests.Session()
        session.auth = (user, password)
        session.stream = True
        resp = session.get(test_url)

        CHUNK_SIZE = 2 ** 12  # Bytes
        TIME_EXPIRE = time.time() + 5  # Seconds

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
        return len(data)
    except:
        return 0
    #print "Read %s bytes out of %s expected." % (len(data), resp.headers.get('content-length'))

def delete_scihub(satellite,hub_url,username,password):

    url = hub_url
    url += '/dhus/odata/v1/DeletedProducts?$inlinecount=allpages&$select=Id&$filter=startswith(Name,%27'+satellite+'%27) and year(IngestionDate) ge 2018&$format=json'  # /search?q='

    products = {}
    starting = -1000
    max_pagination_count = 1000
    cnt = 0
    delete = []
    while max_pagination_count == 1000:
        while True:
            # set starting point, increasing every time by 100
            starting += max_pagination_count
            url_pagination = url + '&$skip=%d&$top=1000' % starting
            session = requests.Session()
            session.auth = (username, password)
            session.stream = True
            resp = session.get(url_pagination)
            if resp.status_code == 200:
                response = resp.json()
                total = response['d']['__count']
                max_pagination_count = len(response['d']['results'])
                cnt += len(response['d']['results'])
                for item in response['d']['results']:
                    delete.append(item['Id'])
                resp.close()
                break

    #save ids for delete in numpy array
    todelete = np.array(delete)

    #get all the ids from db
    if satellite=="S1":
        qs = sentinel1_Products.objects.filter(source=hub_url).values_list('uuid')
    elif satellite=="S2":
        qs = sentinel2_Products.objects.filter(source=hub_url).values_list('uuid')
    elif satellite == "S3":
        qs = sentinel3_Products.objects.filter(source=hub_url).values_list('uuid')

    #convert list to numpy arrays
    myids = np.array(qs)

    #get the common ids
    x = np.intersect1d(myids, todelete).tolist()

    #delete from db these ids
    if satellite == "S1":
        sentinel1_Products.objects.filter(uuid__in=x,source=hub_url).delete()
    elif satellite == "S2":
        sentinel2_Products.objects.filter(uuid__in=x,source=hub_url).delete()
    elif satellite == "S3":
        sentinel3_Products.objects.filter(uuid__in=x,source=hub_url).delete()

def delete_hub(satellite,hub_url,username,password):
    if satellite=='S1':
        sat = "Sentinel-1 "
    elif satellite=='S2':
        sat = "Sentinel-2 "
    elif satellite=='S3':
        sat = "Sentinel-3 "

    # construct url for API
    url = hub_url
    if 'noa' in hub_url:
        url += '/dhus/search?q='
    else:
        url += '/search?q='
    url += 'platformname:'+sat
    url += '&format=json'

    # ready to ask for products
    starting = -100
    max_pagination_count = 100
    logging.info("Collecting results...")
    delete = []
    current_results = 0
    while max_pagination_count == 100:
        stop = 0
        while True:
            # set starting point, increasing every time by 100
            starting += max_pagination_count
            url_pagination = url + '&start=%d&rows=100' % starting
            session = requests.Session()
            session.auth = (username, password)
            session.stream = True
            resp = session.get(url_pagination)

            if resp.status_code == 200:
                response = resp.json()
                try:
                    max_pagination_count = len(response['feed']['entry'])
                    current_results += max_pagination_count
                    if starting == 0:
                        total_results = response['feed']['opensearch:totalResults']
                except:
                    stop = 1
                resp.close()
                break
            else:
                logging.info('Something happened: \tStatus Code: %d, \tReason: %s,', resp.status_code,
                             resp.reason)
                logging.info('URL: %s' % url)
                stop = 1
                break

        if stop == 1:
            break
        print current_results,"/",total_results
        #progress = round(current_results/(float(total_results)*100.0),2)
        #print "Progress:",progress
        cnt = 0
        for prod in range(len(response['feed']['entry'])):
            try:
                # get str metadata
                meta_str = {meta['name']: meta['content'] for meta in response['feed']['entry'][prod]['str']}
                uuid = meta_str['uuid']
                delete.append(uuid)
            except:
                #exc_type, exc_obj, exc_tb = sys.exc_info()
                continue

    # save ids to keep in numpy array
    tokeep = np.array(delete)

    # get all the ids from db
    if satellite == "S1":
        qs = sentinel1_Products.objects.filter(source=hub_url).values_list('uuid')
    elif satellite == "S2":
        qs = sentinel2_Products.objects.filter(source=hub_url).values_list('uuid')
    elif satellite == "S3":
        qs = sentinel3_Products.objects.filter(source=hub_url).values_list('uuid')

    # convert list to numpy arrays
    myids = np.array(qs)

    # get the common ids
    x = np.setdiff1d(myids, tokeep).tolist()

    # delete from db these ids
    if satellite == "S1":
        sentinel1_Products.objects.filter(uuid__in=x, source=hub_url).delete()
    elif satellite == "S2":
        sentinel2_Products.objects.filter(uuid__in=x, source=hub_url).delete()
    elif satellite == "S3":
        sentinel3_Products.objects.filter(uuid__in=x, source=hub_url).delete()




'''
def delete_products(satellite,hub_url,username,password):
    ### delete process ###
    import numpy as np
    s = np.empty((100000,1),dtype='object')
    cnt = 0
    for p in satellite.objects.filter(source=hub_url).values('uuid'):
        s[cnt] = p['uuid']
        cnt+=1
        if cnt==100000:
            break
    print "Start"
    s2 = np.empty((100000,1),dtype='object')
    cnt = 0
    for p in satellite.objects.filter(source=hub_url).values('uuid'):
        s2[cnt] = p['uuid']
        cnt += 1
        print cnt
        if cnt==100000:
            break
    print  np.setdiff1d(s2,s)


    #for p in satellite.objects.filter(source=hub_url).values('url_download'):
        #session = requests.Session()
        #session.auth = (username, password)
        #session.stream = True
        #resp = session.get(p['url_download'])
        #if not resp.status_code == 200:
            #print "must be deleted"
            #p.delete()
        #cnt+=1
        #print cnt
        #resp.close()


def delete_test(satellite,hub_url,username,password):
    ### delete process ###
    todelete = [str(x) for x in range(0,9000)]
    print "STart"
    start_time = time.time()
    sentinel1_Products.objects.filter(identifier=x).delete()
    print x
    elapsed = time.time() - start_time
    print elapsed

'''