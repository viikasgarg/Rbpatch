from django.conf.urls import url
import views

urlpatterns = [
    url(r'^$',
        views.home,
        name='home'),
    url(r'^gitlog$',
        views.gitlogs,
        name='git_logs'),
    url(r'^patch/(?P<pk>[0-9]+)/$',
        views.PatchDetail.as_view(),
        name='patch_detail'),
    url(r'^patches/$',
        views.PatchList.as_view(),
        name='patch_list'),
]
