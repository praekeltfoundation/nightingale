from django.conf.urls import patterns, include, url
from django.contrib import admin


urlpatterns = patterns(
    '',
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/',  include(admin.site.urls)),
    url(r'^api/auth/',
        include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/token-auth/',
        'rest_framework.authtoken.views.obtain_auth_token'),
    url(r'^api/v1/', include('accounts.urls')),
    url(r'^api/v1/', include('reports.urls')),
    url(r'^api/v1/', include('snappy.urls')),
)
