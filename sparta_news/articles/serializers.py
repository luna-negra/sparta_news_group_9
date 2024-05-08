from rest_framework import serializers
from .models import Comments, Articles


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = "__all__"


class ArticlesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Articles
        fields = '__all__'
        read_only_fields = ('user',)
