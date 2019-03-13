from rest_framework.routers import DefaultRouter, SimpleRouter
# from rest_framework_nested import routers as nested_routers

class SharedAPIRootRouter(SimpleRouter):
    shared_router = DefaultRouter()

    def register(self, *args, **kwargs):
        self.shared_router.register(*args, **kwargs)
        super(SharedAPIRootRouter, self).register(*args,**kwargs)


class SharedAPIRootRouter_v1(SimpleRouter):
    # shared_router = nested_routers.SimpleRouter()
    shared_router = DefaultRouter()

    def register(self, *args, **kwargs):
        self.shared_router.register(*args, **kwargs)
        super(SharedAPIRootRouter_v1, self).register(*args, **kwargs)


class SharedAPIRootRouter_v2(SimpleRouter):
    shared_router = DefaultRouter()

    def register(self, *args, **kwargs):
        self.shared_router.register(*args, **kwargs)
        super(SharedAPIRootRouter_v2, self).register(*args, **kwargs)

