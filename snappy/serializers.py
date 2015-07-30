from rest_framework import serializers

from .models import Category, ProjectCategory, Report, Location


class CategorySerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Category
        fields = ('url', 'id', 'name', 'order', 'metadata')


class ProjectCategorySerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = ProjectCategory
        fields = ('url', 'id', 'project', 'categories')


class LocationSerializer(serializers.ModelSerializer):

    """ A class to serialize locations as GeoJSON compatible data """

    class Meta:
        model = Location
        geo_field = "point"
        fields = ('id', 'point')


class ReportSerializer(serializers.HyperlinkedModelSerializer):
    location = LocationSerializer(many=False, read_only=False)

    class Meta:
        model = Report
        fields = ('url', 'id', 'contact_key', 'to_addr', 'category', 'project',
                  'location', 'description', 'incident_at', 'metadata')

    def create(self, validated_data):
        location_data = validated_data.pop('location')
        loc = Location.objects.create(**location_data)
        report = Report.objects.create(location=loc, **validated_data)
        return report


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


class ReportUserSerializer(serializers.ModelSerializer):
    """
        Only used for posting from normal users
    """
    location = LocationSerializer(many=False, read_only=False)

    class Meta:
        model = Report
        fields = ('id', 'contact_key', 'to_addr', 'category', 'project',
                  'location', 'description', 'incident_at', 'metadata')

    def create(self, validated_data):
        location_data = validated_data.pop('location')
        loc = Location.objects.create(**location_data)
        report = Report.objects.create(location=loc, **validated_data)
        return report
