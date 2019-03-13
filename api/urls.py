from django.conf.urls import url
from .views import sentinel1_list,sentinel2_list,sentinel3_list
from django.conf.urls import url, include


from rest_framework_nested import routers as nested_routers


#router = nested_routers.DefaultRouter()
#router.register(r'', sentinel1_list, base_name='sentinel1')



#parcels_router = nested_routers.NestedSimpleRouter(router, r'sentinel/aoi', lookup='aoi')
#parcels_router.register(r'parcels', classify_views.ParcelViewSet , base_name='api-parcels')


urlpatterns = [
    url('products/sentinel1',sentinel1_list.as_view()),
    url('products/sentinel2',sentinel2_list.as_view()),
    url('products/sentinel3',sentinel3_list.as_view())
    #url(r'', include(router.urls)),
    #url(r'', include(parcels_router.urls)),

]
