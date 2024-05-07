from rest_framework import serializers
from .models import Articles

class ArticlesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Articles
        fields = '__all__'
        read_only_fields = ('user',)