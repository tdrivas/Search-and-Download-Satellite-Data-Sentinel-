from __future__ import unicode_literals

from datetime import datetime
#from django.db import models
from django.contrib.gis.db import models
from django.contrib.gis.geos import MultiPolygon
from django.contrib.gis import geos

# Create your models here.
# Create your models here.


class hubs(models.Model):
    hubname = models.CharField(max_length=250, blank=True, null=True)
    hublink = models.CharField(max_length=250, blank=True, null=True)
    hubscore = models.IntegerField(blank=True, null=True)



class sentinel2_Products(models.Model):
    uuid = models.CharField(max_length=500)
    identifier = models.CharField(max_length=500)
    filename = models.CharField(max_length=500)
    url_download = models.CharField(max_length=500, blank=True, null=True)
    url_checksum = models.CharField(max_length=500, blank=True, null=True)
    instrument = models.CharField(max_length=250, blank=True, null=True)
    product_type = models.CharField(max_length=250, blank=True, null=True)
    cloud_coverage = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    sensing_date = models.DateTimeField(null=True)
    ingestion_date = models.DateTimeField(null=True)
    orbit_number = models.CharField(max_length=250, blank=True, null=True)
    relative_orbit_number = models.CharField(max_length=250, blank=True, null=True)
    pass_direction = models.CharField(max_length=250, blank=True, null=True)
    wkt_footprint = models.CharField(max_length=10000, blank=True, null=True)
    size = models.CharField(max_length=250, blank=True, null=True)
    #received = models.NullBooleanField()
    source = models.CharField(max_length=250,blank=True,null=True)
    score = models.IntegerField(null=True)
    tile_name = models.CharField(max_length=250,null=True)
    #geom_footprint = models.PolygonField(srid=4326,null=True,blank=True)
    geom_footprint = models.MultiPolygonField(srid=4326,null=True,blank=True)
    #('geom_footprint', django.contrib.gis.db.models.fields.MultiPolygonField(blank=True, null=True, srid=4326)),
    source2 = models.ForeignKey(hubs)
    quicklook = models.CharField(max_length=500, blank=True, null=True)



class sentinel1_Products(models.Model):
    uuid = models.CharField(max_length=500)
    identifier = models.CharField(max_length=500)
    filename = models.CharField(max_length=500)
    url_download = models.CharField(max_length=500, blank=True, null=True)
    url_checksum = models.CharField(max_length=500, blank=True, null=True)
    instrument = models.CharField(max_length=250, blank=True, null=True)
    product_type = models.CharField(max_length=250, blank=True, null=True)
    sensor_operational_mode = models.CharField(max_length=250, blank=True, null=True)
    sensing_date = models.DateTimeField(null=True)
    ingestion_date = models.DateTimeField(null=True)
    orbit_number = models.CharField(max_length=250, blank=True, null=True)
    relative_orbit_number = models.CharField(max_length=250, blank=True, null=True)
    pass_direction = models.CharField(max_length=250, blank=True, null=True)
    wkt_footprint = models.CharField(max_length=10000, blank=True, null=True)
    size = models.CharField(max_length=250, blank=True, null=True)
    polarization = models.CharField(max_length=250, blank=True, null=True)
    swath = models.CharField(max_length=250, blank=True, null=True)
    #received = models.NullBooleanField()
    source = models.CharField(max_length=250,blank=True,null=True)
    source2 = models.ForeignKey(hubs)
    score = models.IntegerField(null=True)
    #geom_footprint2 = models.PolygonField(srid=4326,null=True,blank=True)
    geom_footprint = models.MultiPolygonField(srid=4326,null=True,blank=True)
    quicklook = models.CharField(max_length=500, blank=True, null=True)







class sentinel3_Products(models.Model):
    uuid = models.CharField(max_length=500)
    identifier = models.CharField(max_length=500)
    filename = models.CharField(max_length=500)
    url_download = models.CharField(max_length=500, blank=True, null=True)
    url_checksum = models.CharField(max_length=500, blank=True, null=True)
    instrument = models.CharField(max_length=250, blank=True, null=True)
    product_type = models.CharField(max_length=250, blank=True, null=True)
    product_class = models.CharField(max_length=250, blank=True, null=True)
    sensor_operational_mode = models.CharField(max_length=250, blank=True, null=True)
    sensing_date = models.DateTimeField(null=True)
    ingestion_date = models.DateTimeField(null=True)
    timeliness = models.CharField(max_length=200,blank=True,null=True)
    procfacilityname = models.CharField(max_length=250,blank=True,null=True)
    procfacilityorg =  models.CharField(max_length=200, blank=True, null=True)
    orbit_number = models.CharField(max_length=250, blank=True, null=True)
    relative_orbit_number = models.CharField(max_length=250, blank=True, null=True)
    pass_direction = models.CharField(max_length=250, blank=True, null=True)
    wkt_footprint = models.CharField(max_length=10000, blank=True, null=True)
    size = models.CharField(max_length=250, blank=True, null=True)
    #received = models.NullBooleanField()
    source = models.CharField(max_length=250,blank=True,null=True)
    score = models.IntegerField(null=True)
    geom_footprint = models.MultiPolygonField(srid=4326,null=True,blank=True)
    quicklook = models.CharField(max_length=500, blank=True, null=True)
    source2 = models.ForeignKey(hubs,default=2)





class hubs_credentials(models.Model):
    hub = models.ForeignKey(hubs)
    username = models.CharField(max_length=250, blank=True, null=True)
    password  = models.CharField(max_length=250, blank=True, null=True)


class hubs_lastaccess(models.Model):
    hubid = models.ForeignKey(hubs)
    accessdate = models.DateTimeField(blank=True,null=True)
    product = models.CharField(max_length=10,blank=True,null=True)
