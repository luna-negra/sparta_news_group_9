from django.shortcuts import render, get_object_or_404
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from .models import Comments, Articles, Accounts
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
        # user = request.user
        user = get_object_or_404(Accounts, pk=1)
        article = get_object_or_404(Articles, pk=article_id)

        content = request.data.get("content")

        if not content:
            return Response({"error":"댓글 내용 입력이 없습니다"})
        
        if len(content) < 10:
            return Response({"error":"댓글의 내용을 10글자 이상 작성해주세요"})
        
        comment = Comments.objects.create(content=content, user=user, article=article)
        serializer = CommentSerializer(comment)
        return Response(serializer.data,status=status.HTTP_201_CREATED)
    

class CommentDetailView(generics.ListAPIView):
    serializer_class = CommentSerializer

    def put(self,request,comment_id):
        user = get_object_or_404(Accounts, pk=1)
        comment = get_object_or_404(Comments,pk=comment_id)
        content = request.data.get("content")
        if not content:
            return Response({"error":"댓글 내용 입력이 없습니다"})
        
        if len(content) < 10:
            return Response({"error":"댓글의 내용을 10글자 이상 작성해주세요"})
        
        #if request.user == comment.user:
        if user == comment.user:
            comment.content = content
            comment.save()
            serializer = CommentSerializer(comment)
            return Response(serializer.data)
        return Response({"error":"권한 없는 사용자입니다."},status=status.HTTP_403_FORBIDDEN)


