from django.conf.urls.static import static
from django.conf.urls import patterns, url, include
from django.conf import settings

from django.contrib import admin


urlpatterns = patterns('',
	(r'', include('core.urls')),
)
