from django.contrib.auth.models import User
from rest_framework import serializers
from harvest.models import sentinel1_Products,sentinel2_Products,sentinel3_Products


class Sentinel1Serializer(serializers.ModelSerializer):

    # monthnumb = serializers.SerializerMethodField()

    class Meta:
        model = sentinel1_Products
        fields = ('filename', 'sensing_date', 'instrument', 'polarization' ,'source', 'url_download','product_type','wkt_footprint')
        #fields = ('filename')

class Sentinel2Serializer(serializers.ModelSerializer):

    class Meta:
        model = sentinel2_Products
        fields = ('filename', 'sensing_date', 'tile_name', 'product_type','instrument','source', 'url_download',)


class Sentinel3Serializer(serializers.ModelSerializer):

    class Meta:
        model = sentinel3_Products
        fields = ('filename', 'sensing_date', 'instrument', 'sensor_operational_mode','product_type' ,'source', 'url_download',)



