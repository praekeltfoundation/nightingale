from .models import Category, ProjectCategory
from accounts.models import UserProject
from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .serializers import (CategorySerializer,
                          ProjectCategorySerializer,
                          ProjectCategoryListSerializer)


class CategoryViewSet(viewsets.ModelViewSet):

    """
    API endpoint that allows categories to be viewed or edited.
    """
    permission_classes = (IsAdminUser,)
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProjectCategoryViewSet(viewsets.ModelViewSet):

    """
    API endpoint that allows project categories to be viewed or edited.
    """
    permission_classes = (IsAdminUser,)
    queryset = ProjectCategory.objects.all()
    serializer_class = ProjectCategorySerializer


class FilteredCategoriesList(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ProjectCategoryListSerializer

    def get_queryset(self):
        userprojects = UserProject.objects.get(user=self.request.user)
        queryset = ProjectCategory.objects.filter(
            project__in=userprojects.projects.all())
        return queryset

    def list(self, request):
        queryset = self.get_queryset()
        serializer = ProjectCategoryListSerializer(queryset, many=True)
        return Response(serializer.data)
