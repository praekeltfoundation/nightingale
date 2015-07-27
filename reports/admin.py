from django.contrib import admin

from .models import Category, ProjectCategory, Report

admin.site.register(Category)
admin.site.register(ProjectCategory)
admin.site.register(Report)
