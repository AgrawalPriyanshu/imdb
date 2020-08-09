from rest_framework.routers import DefaultRouter


from movies.api import MovieViewset

router = DefaultRouter()
router.register(r'movies', MovieViewset)
