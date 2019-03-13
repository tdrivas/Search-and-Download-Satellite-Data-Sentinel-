from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from serializers import Sentinel1Serializer,Sentinel2Serializer,Sentinel3Serializer
from django_filters import rest_framework as filters
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from harvest.models import sentinel1_Products,sentinel2_Products,sentinel3_Products
#from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from rest_framework import generics
from rest_framework.filters import OrderingFilter
from rest_framework.decorators import api_view
from django.views import View
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.geos import MultiPolygon
from url_filter.integrations.drf import DjangoFilterBackend
from rest_framework_gis.filters import InBBOXFilter,GeometryFilter
from rest_framework_gis.filterset import GeoFilterSet





'''
  @property
  def getwkt(self):
      if 'wkt_footprint' in self.request.GET:
          return self.request.get['wkt_footprint']
      else:
          return None
  '''

class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """

    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)




#class sentinel1_list(viewsets.ModelViewSet):
class sentinel1_list(generics.ListCreateAPIView):


    model = sentinel1_Products
    serializer_class = Sentinel1Serializer
    '''
    if getwkt is not None:
        print getwkt
        wkt = 'POLYGON ((-21.4453125 49.724479188712984,-10.1953125 35.746512259918504,34.62890625 33.578014746143985, 43.59375 67.67608458198097, 28.4765625 72.01972876525514, -26.71875 65.87472467098549, -21.4453125 49.724479188712984))'
        geom_multipolygon = GEOSGeometry(wkt, srid=4326)
        #geom_multipolygon = MultiPolygon(geometry, srid=4326)
        queryset = sentinel1_Products.objects.filter(geom_footprint__intersects=geom_multipolygon).order_by('-sensing_date', 'filename')
    else:
        queryset = sentinel1_Products.objects.all().order_by('-sensing_date', 'filename')[:5]
    '''

    wkt = 'POLYGON ((-21.4453125 49.724479188712984,-10.1953125 35.746512259918504,34.62890625 33.578014746143985, 43.59375 67.67608458198097, 28.4765625 72.01972876525514, -26.71875 65.87472467098549, -21.4453125 49.724479188712984))'
    geom_multipolygon = GEOSGeometry(wkt, srid=4326)
    x = MultiPolygon(geom_multipolygon, srid=4326)
    #queryset = sentinel1_Products.objects.filter(source__hubs_hublink).order_by('-hubscore')


    queryset = sentinel1_Products.objects.all().order_by('identifier','-source2_id__hubscore').distinct('identifier')
    #queryset = queryset.filter(geom_footprint__intersects=wkt)

    # new and commented
    filter_backends = (DjangoFilterBackend,)
    filter_fields = ('filename','sensing_date','product_type','wkt_footprint')






    '''
    def get_queryset(self):

        if 'wkt_footprint' in self.request.GET:
            wkt = self.request.GET['wkt_footprint']
            queryset = sentinel1_Products.objects.all().order_by('-sensing_date', 'filename')
        else:
            queryset = sentinel1_Products.objects.all().order_by('-sensing_date', 'filename')
            wkt = False
        return queryset
    '''

    #filter_fields = ('filename', 'sensing_date', 'instrument', 'polarization' ,'source', 'url_download','product_type',)

    #pagination_class = None
    # lookup_field = 'recap_id'

    # def retrieve(self, request, *args, **kwargs):
    # recap_id = kwargs.get('recap_id', None)
    # raster = Rasters.objects.get(id=recap_id)
    # self.queryset = Rasters.objects.filter(recap_id = recap_id)
    # return super(product_list, self).retrieve(request, *args, **kwargs)


class IntersectionFilter(GeoFilterSet):
    geometry = GeometryFilter(name='geometry',lookup_expr='intersects')
    class Meta:
        model = sentinel2_Products
        fields = '__all__'
        exclude = ('geom_footprint',)

class sentinel2_list(generics.ListCreateAPIView):
    model = sentinel2_Products
    serializer_class = Sentinel2Serializer

    wkt = 'POLYGON ((-21.4453125 49.724479188712984,-10.1953125 35.746512259918504,34.62890625 33.578014746143985, 43.59375 67.67608458198097, 28.4765625 72.01972876525514, -26.71875 65.87472467098549, -21.4453125 49.724479188712984))'
    geom_multipolygon = GEOSGeometry(wkt, srid=4326)
    x = MultiPolygon(geom_multipolygon, srid=4326)
    # queryset = sentinel1_Products.objects.filter(source__hubs_hublink).order_by('-hubscore')

    queryset = sentinel2_Products.objects.all().order_by('identifier', '-source2_id__hubscore').distinct('identifier')
    # queryset = queryset.filter(geom_footprint__intersects=wkt)

    bbox_filter_field = 'geom_footprint'

    # new and commented
    filter_backends = (DjangoFilterBackend,InBBOXFilter)
    filter_fields = ('filename', 'sensing_date', 'product_type', 'wkt_footprint','geom_footprint')
    bbox_filter_include_overlapping = True

class sentinel3_list(generics.ListCreateAPIView):
    # queryset = Rasters.objects.all()

    queryset = sentinel3_Products.objects.all().order_by('-sensing_date', 'filename')
    serializer_class = Sentinel3Serializer