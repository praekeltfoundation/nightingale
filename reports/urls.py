from django.conf.urls import url, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'projectcategories', views.ProjectCategoryViewSet)


# Wire up our API using automatic URL routing.
urlpatterns = [
    url(r'^sys/', include(router.urls)),
    url('^categories/$',
        views.FilteredCategoriesList.as_view()),
]
