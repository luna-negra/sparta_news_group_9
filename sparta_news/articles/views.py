from django.shortcuts import render, get_object_or_404
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from .models import Comments, Articles, Accounts
from .serializers import CommentSerializer, ArticlesSerializer
from rest_framework_simplejwt.tokens import AccessToken


# from rest_framework.request.ForcedAuthentication import authenticate

class CommentListCreatAPIView(generics.ListAPIView):
  
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = CommentSerializer
    
    def get(self,request,article_pk):
        article = get_object_or_404(Articles,pk=article_pk) #id나 pk나
        comments = article.comments.all()
        serializer = CommentSerializer(comments,many=True)
        return Response(serializer.data)
      
    def post(self,request,article_pk):
        user = request.user
        article = get_object_or_404(Articles, pk=article_pk)
        content = request.data.get("content")
        if not content:
            return Response({"error":"댓글 내용 입력이 없습니다"})
        comment = Comments.objects.create(content=content,user=user,article=article)
        serializer = CommentSerializer(comment)
        return Response(serializer.data,status=status.HTTP_201_CREATED)
      
      
class CommentDetailAPIView(generics.ListAPIView):
  
    permission_classes = [IsAuthenticated]
    serializer_class = CommentSerializer
    
    def put(self,request,comment_pk):
        comment = get_object_or_404(Comments,pk=comment_pk)
        content = request.data.get("content")
        
        #사용자가 수정한 comment내용을 받음 -> comment밖에 항목 없음
        if not content:
            return Response({"error":"댓글 내용 입력이 없습니다"})
          
        if request.user == comment.user:
            comment.content = content   #수정내용 업데이트
            comment.save()
            serializer = CommentSerializer(comment)
            return Response(serializer.data)
          
        return Response({"error":"권한 없는 사용자입니다."},status=status.HTTP_403_FORBIDDEN)
      
    def delete(self,request,comment_pk):
        comment = get_object_or_404(Comments, pk=comment_pk)
        if request.user == comment.user:
            comment.delete()
            return Response({"message":"댓글이 삭제 되었습니다."},status=status.HTTP_204_NO_CONTENT)
        return Response({"error":"권한 없는 사용자입니다."},status=status.HTTP_403_FORBIDDEN)


class ArticleListView(APIView):
    """
    확인 필요 사항

    게시글 조회 -> 등록 후 다시 게시글 조회 할 때, 일반 사용자가 아무 문제 없이 게시글을 볼 수 있는지
    확인을 한 번 해봐야 할 듯 합니다.

    self.permission_classes = [IsAuthenticated]로 인해서
    클래스 상단에 선언한 permission_classes값이 [IsAuthenticatedOrReadOnly]가
    [IsAuthenticated]로 변경되기 때문입니다. :)
    """

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
    """
    반드시 수정이 필요한 부분에 대한 요청

    1. 수정을 진행하는 put()과 삭제를 진행하는 delete()는 다른 사용자가 내 글을 수정/삭제하거나
       내가 다른 사용자의 글을 수정/삭제할 수 있도록 현재 코드가 작성되어 있습니다.
       get()은 상관없지만 put()과 delete()는 내가 작성한 글만 수정과 삭제 가능하도록 수정 부탁드립니다 :)

    2. 계정 테스트로 넣어두신 주석처리된 get()은 삭제하셔도 됩니다 :)
    """

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

    def put(self, request, article_pk):
        article = self.get_object(pk=article_pk)

        if not request.user == article.author:
            return Response({"error": "권한 없는 사용자입니다."}, status=status.HTTP_403_FORBIDDEN)

        serializer = ArticlesSerializer(article, data=request.data, partial=True)

        if serializer.is_valid(raise_exception=True):
            serializer.save()  # 유효한 경우 저장
            return Response(serializer.data, status=200)
        else:
            # 유효하지 않은 경우 에러 응답
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, article_pk):
        article = self.get_object(pk=article_pk)
        if not request.user == article.author:
            return Response({"error": "권한 없는 사용자입니다."}, status=status.HTTP_403_FORBIDDEN)

        article.delete()
        data = {"pk": f"{article_pk} is deleted."}
        return Response(data, status=200)
