from django.contrib import admin

from .models import Project, UserProject, Integration

admin.site.register(Project)
admin.site.register(UserProject)
admin.site.register(Integration)
