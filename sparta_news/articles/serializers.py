from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Articles

class ArticleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Articles
        fields = '__all__'
        read_only_fields = ('user',)