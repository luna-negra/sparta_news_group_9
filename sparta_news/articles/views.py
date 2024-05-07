from rest_framework.views import APIView
from articles.models import Articles
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from articles.serializers import ArticleSerializer
from rest_framework.response import Response
from django.shortcuts import get_list_or_404
from rest_framework import status


class ArticleListView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    # 게시글 조회 (list)
    def get(self, request):
        article = Articles.objects.all()
        serializer = ArticleSerializer(article, many=True)
        return Response(serializer.data)

    # 게시글 등록
    def post(self, request):
        self.permission_classes = [IsAuthenticated]
        serializer = ArticleSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class ArticleDetailView(APIView):
    def get_object(self, pk):
        try:
            return Articles.objects.get(pk=pk)
        except Articles.DoesNotExist:
            return Response({"error": "Article not found"}, status=status.HTTP_404_NOT_FOUND)

    # 게시글 조회(detail)
    def get(self, request, pk):
        get_obj = self.get_object(pk)
        serializer = ArticleSerializer(get_obj)
        return Response(serializer.data)