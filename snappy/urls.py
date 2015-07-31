from django.conf.urls import url, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'messages', views.MessageViewSet)


# Wire up our API using automatic URL routing.
urlpatterns = [
    url(r'^sys/', include(router.urls)),
    url(r'^snappymessage/', views.SnappyMessagePost.as_view()),
]
