from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='post_list'),
    path('post/new/', views.PostCreateView.as_view(), name='post_create'),
    path('post/<slug:slug>/', views.PostDetailView.as_view(), name='post_detail'),
    path('post/<slug:slug>/edit/', views.PostUpdateView.as_view(), name='post_edit'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
