from django.conf.urls import url, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'submissions', views.SubmissionViewSet)


# Wire up our API using automatic URL routing.
urlpatterns = [
    url(r'^sys/', include(router.urls)),
    url(r'^onasubmission/', views.OnaSubmissionPost.as_view()),
]
