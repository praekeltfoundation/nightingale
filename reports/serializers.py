from rest_framework import serializers

from .models import Category, ProjectCategory


class CategorySerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Category
        fields = ('url', 'id', 'name', 'order', 'metadata')


class ProjectCategorySerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = ProjectCategory
        fields = ('url', 'id', 'project', 'categories')


class CategorySimpleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('id', 'name')


class ProjectCategoryListSerializer(serializers.ModelSerializer):

    """
        Only used for get views, because relational serializer is not
        something that works nicely with posts
    """
    categories = CategorySimpleSerializer(many=True, read_only=True)

    class Meta:
        model = ProjectCategory
        fields = ('id', 'project', 'categories')
