from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from .models import Comments
from .serializers import CommentSerializer


def test(request):
    pass

class CommentListCreatView(generics.ListAPIView):

    # permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = CommentSerializer

    def get(self,request,article_id):
        comments = Comments.objects.filter(article_id=article_id)
        serializer = CommentSerializer(comments,many=True)
        return Response(serializer.data)


    def post(self,request,article_id): 
        pass