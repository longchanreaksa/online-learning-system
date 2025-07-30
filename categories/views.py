from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from .models import Category, Tag
from .forms import CategoryForm, TagForm

class CategoryListView(ListView):
    model = Category
    template_name = 'categories/category_list.html'
    context_object_name = 'categories'

class CategoryDetailView(DetailView):
    model = Category
    template_name = 'categories/category_detail.html'

class CategoryCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'categories/category_form.html'
    success_message = "Category created successfully!"
    success_url = reverse_lazy('categories:category_list')

class CategoryUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'categories/category_form.html'
    success_message = "Category updated successfully!"

class CategoryDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Category
    template_name = 'categories/category_confirm_delete.html'
    success_url = reverse_lazy('categories:category_list')
    success_message = "Category deleted successfully!"

class TagListView(ListView):
    model = Tag
    template_name = 'categories/tag_list.html'
    context_object_name = 'tags'

class TagDetailView(DetailView):
    model = Tag
    template_name = 'categories/tag_detail.html'

class TagCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Tag
    form_class = TagForm
    template_name = 'categories/tag_form.html'
    success_message = "Tag created successfully!"
    success_url = reverse_lazy('categories:tag_list')

class TagUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Tag
    form_class = TagForm
    template_name = 'categories/tag_form.html'
    success_message = "Tag updated successfully!"

class TagDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Tag
    template_name = 'categories/tag_confirm_delete.html'
    success_url = reverse_lazy('categories:tag_list')
    success_message = "Tag deleted successfully!"