from django.conf.urls import url, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'projectcategories', views.ProjectCategoryViewSet)
router.register(r'reports', views.ReportViewSet)


# Wire up our API using automatic URL routing.
urlpatterns = [
    url(r'^sys/', include(router.urls)),
    url('^category/$',
        views.FilteredCategoriesList.as_view()),
    url(r'^category/(?P<pk>.+)/', views.CategoryItemViewSet.as_view()),
    url(r'^report/(?P<pk>.+)/', views.ReportPatch.as_view()),
    url(r'^report/', views.ReportPost.as_view()),

]
