from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.views.generic import TemplateView

from django.contrib import admin
import patch.urls

urlpatterns = [
    url(r"^admin/", include(admin.site.urls)),
    url(r"^accounts/", include("account.urls")),
    url(r"^",  include(patch.urls)),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
