import logging
import os
import time
import types
import requests
from utils import delete_hub,delete_scihub,search_finhub_s2,search_finhub_s1,search_spacenoa_s1,search_finhub_s3,search_spacenoa_s3,search_scihub_s3,search_scihub_s1,download_speed,search_scihub_s2,search_spacenoa_s2,get_s2_new_naming_convention
os.environ.setdefault("DJANGO_SETTINGS_MODULE","eopen.settings")
import django
django.setup()
import harvest.models
from harvest.models import hubs,hubs_credentials,sentinel2_Products,sentinel1_Products,sentinel3_Products
#aoi ='POLYGON ((-1.984891597597141 42.9448387446552, -1.367038590164367 42.93539924782252, -1.363815009256022 42.55505005702414, -1.984891597597141 42.56454765255964, -1.984891597597141 42.9448387446552))'
aoi_europe = 'POLYGON ((-21.4453125 49.724479188712984,-10.1953125 35.746512259918504,34.62890625 33.578014746143985, 43.59375 67.67608458198097, 28.4765625 72.01972876525514, -26.71875 65.87472467098549, -21.4453125 49.724479188712984))'




#products = {1:sentinel1_Products,2:sentinel2_Products,3:sentinel3_Products}

start_time = time.time()


start_time = time.time()

#initialize dictionaries for grading hubs
scores = {}
speed = {}

#check each hub if it is active
for hub in hubs.objects.all():
    logging.info("Checking hub %s" %(hub.hublink))
    scores[hub.hublink] = 0
    speed[hub.hublink] = 0

    #get credentials from db
    hub_password = hubs_credentials.objects.get(hub_id=hub.id).password
    hub_url = hub.hublink
    hub_username = hubs_credentials.objects.get(hub_id=hub.id).username

    #start connection to hub
    session = requests.Session()
    session.auth = (hub_username, hub_password)
    session.stream = True

    #ask for response
    resp = session.get(hub.hublink)

    #check if response is ok or not. if not, score = 0, otherwise 1
    if not resp.status_code == 200:
        continue

    scores[hub_url] += 1
    resp.close()

    #delete process of not available products
    if 'sci' in hub.hubname:
        logging.info("Deleting sentinel-1 products...")
        delete_scihub("S1", hub.hublink, hub_username, hub_password)
        #logging.info("Deleting sentinel-2 products...")
        #delete_scihub("S2", hub.hublink, hub_username, hub_password)
        #logging.info("Deleting sentinel-3 products...")
        #delete_scihub("S3", hub.hublink, hub_username, hub_password)
    else:
        logging.info("Deleting sentinel-1 products...")
        delete_hub("S1", hub.hublink, hub_username, hub_password)
        #logging.info("Deleting sentinel-2 products...")
        #delete_hub("S2", hub.hublink, hub_username, hub_password)
        #logging.info("Deleting sentinel-3 products...")
        #delete_hub("S3", hub.hublink, hub_username, hub_password)

    #measure download speed of hub
    logging.info("Check download speed...")
    speed[hub.hublink] = download_speed(hub_url, hub_username, hub_password)


    if 'sci' in hub.hubname:
        search_scihub_s1(aoi_europe)
        search_scihub_s2(aoi_europe)
        search_scihub_s3(aoi_europe)

    elif 'fin' in hub.hublink:
        search_finhub_s1(aoi_europe)
        search_finhub_s2(aoi_europe)
        search_finhub_s3(aoi_europe)
    else:
        search_spacenoa_s1(aoi_europe)
        search_spacenoa_s2(aoi_europe)
        search_spacenoa_s3(aoi_europe)

elap = time.time()-start_time


grades = len(scores)
for w in sorted(speed,key=speed.get,reverse=True):
    scores[w] += grades
    grades-=1

logging.info("Update score on each product")
for hub in hubs.objects.all():
    	logging.info("Updating score on %s" %(hub.hublink))
	    
	hub.hubscore = scores[hub.hublink]
	hub.save()










