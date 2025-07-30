from django.urls import path
from .views import (
    CategoryListView, CategoryDetailView, CategoryCreateView,
    CategoryUpdateView, CategoryDeleteView,
    TagListView, TagDetailView, TagCreateView,
    TagUpdateView, TagDeleteView
)

app_name = 'categories'

urlpatterns = [
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('categories/<slug:slug>/', CategoryDetailView.as_view(), name='category_detail'),
    path('categories/create/', CategoryCreateView.as_view(), name='category_create'),
    path('categories/<slug:slug>/update/', CategoryUpdateView.as_view(), name='category_update'),
    path('categories/<slug:slug>/delete/', CategoryDeleteView.as_view(), name='category_delete'),
    
    path('tags/', TagListView.as_view(), name='tag_list'),
    path('tags/<slug:slug>/', TagDetailView.as_view(), name='tag_detail'),
    path('tags/create/', TagCreateView.as_view(), name='tag_create'),
    path('tags/<slug:slug>/update/', TagUpdateView.as_view(), name='tag_update'),
    path('tags/<slug:slug>/delete/', TagDeleteView.as_view(), name='tag_delete'),
]