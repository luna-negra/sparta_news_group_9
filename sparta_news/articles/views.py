# from rest_framework.request.ForcedAuthentication import authenticate

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import AccessToken
from .models import Articles
from .serializers import ArticlesSerializer
from rest_framework import status



class ArticleListView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    # 게시글 조회 (list)
    def get(self, request):
        article = Articles.objects.all()
        serializer = ArticlesSerializer(article, many=True)
        return Response(serializer.data)

    # 게시글 등록
    def post(self, request):
        self.permission_classes = [IsAuthenticated]
        serializer = ArticlesSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
          
          
class ArticlesDetailAPIView(APIView):
    def get_object(self, pk):
        try:
            return Articles.objects.get(pk=pk)
        except Articles.DoesNotExist:
            return Response({"error": "Article not found"}, status=status.HTTP_404_NOT_FOUND)

              # 게시글 조회(detail)
    def get(self, request, pk):
        get_obj = self.get_object(pk)
        serializer = ArticlesSerializer(get_obj)
        return Response(serializer.data)
      
#    def get(self, request):
#        user = authenticate(username=request.data['username'], password=request.data['password'])
#        if user is not None:
#            access_token = AccessToken.for_user(user)
#            return Response({'access_token': str(access_token)}, status=200)
#        else:
#            return Response({'error': 'Invalid credentials'}, status=400)

    def put(self, request, pk):
        article = self.get_object(pk=pk)
        serializer = ArticlesSerializer(article, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=200)

    def delete(self, request, pk):
        article = self.get_object(pk=pk)
        article.delete()
        data = {"pk": f"{pk} is deleted."}
        return Response(data, status=200)

