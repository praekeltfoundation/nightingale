from .models import Category, ProjectCategory, Report
from accounts.models import UserProject
from rest_framework import viewsets, generics, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .serializers import (CategorySerializer,
                          CategorySimpleSerializer,
                          ProjectCategorySerializer,
                          ProjectCategoryListSerializer,
                          ReportSerializer,
                          ReportUserSerializer)


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


class ReportViewSet(viewsets.ModelViewSet):

    """
    API endpoint that allows reports to be viewed or edited.
    """
    permission_classes = (IsAdminUser,)
    queryset = Report.objects.all()
    serializer_class = ReportSerializer


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


class CategoryItemViewSet(generics.RetrieveAPIView):

    """
    API endpoint that allows individual categories (access controlled)
    to be viewed and used as references in POSTS
    """
    permission_classes = (IsAuthenticated,)
    queryset = Category.objects.all()
    serializer_class = CategorySimpleSerializer


class ReportPost(mixins.CreateModelMixin,  generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Report.objects.all()
    serializer_class = ReportUserSerializer

    def post(self, request, *args, **kwargs):
        # load the users project - posting users should only have one project
        userprojects = UserProject.objects.get(user=self.request.user)
        project = userprojects.projects.all()[0]
        request.data["project"] = project.id
        return self.create(request, *args, **kwargs)


class ReportPatch(mixins.UpdateModelMixin,  generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Report.objects.all()
    serializer_class = ReportUserSerializer

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)
