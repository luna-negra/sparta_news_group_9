from django.shortcuts import render, get_object_or_404
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from .models import Comments, Articles, Accounts
from .serializers import CommentSerializer, ArticlesSerializer
from rest_framework_simplejwt.tokens import AccessToken

# 임현경 Import 추가
from rest_framework.decorators import api_view


## 임현경 Import 추가 완료##


# from rest_framework.request.ForcedAuthentication import authenticate

class CommentListCreateAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = CommentSerializer

    def get(self, request, article_pk):
        article = get_object_or_404(Articles, pk=article_pk)
        comments = article.comments.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, article_pk):
        user = request.user
        article = get_object_or_404(Articles, pk=article_pk)
        content = request.data.get("content")
        if not content:
            return Response({"error": "댓글 내용 입력이 없습니다"})
        comment = Comments.objects.create(content=content, user=user, article=article)
        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommentDetailAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CommentSerializer

    def put(self, request, comment_pk):
        comment = get_object_or_404(Comments, pk=comment_pk)
        content = request.data.get("content")

        if not content:
            return Response({"error": "댓글 내용 입력이 없습니다"})

        if request.user == comment.user:
            comment.content = content
            comment.save()
            serializer = CommentSerializer(comment)
            return Response(serializer.data)

        return Response({"error": "권한 없는 사용자입니다."}, status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, comment_pk):
        comment = get_object_or_404(Comments, pk=comment_pk)
        if request.user == comment.user:
            comment.delete()
            return Response({"message": "댓글이 삭제 되었습니다."}, status=status.HTTP_204_NO_CONTENT)
        return Response({"error": "권한 없는 사용자입니다."}, status=status.HTTP_403_FORBIDDEN)


class ArticleListView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    # 게시글 조회 (list)
    def get(self, request):
        article = Articles.objects.all()
        serializer = ArticlesSerializer(article, many=True)
        return Response(serializer.data)

    # 게시글 등록
    def post(self, request):
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
    def get(self, request, article_pk):
        get_obj = self.get_object(article_pk)

        if isinstance(get_obj, ArticlesSerializer.Meta.model):
            serializer = ArticlesSerializer(get_obj)
            return Response(serializer.data)

        else:
            return get_obj

    def put(self, request, article_pk):
        article = self.get_object(pk=article_pk)

        if not isinstance(article, ArticlesSerializer.Meta.model):
            return article

        if not request.user == article.user:
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
        if not request.user == article.user:
            return Response({"error": "권한 없는 사용자입니다."}, status=status.HTTP_403_FORBIDDEN)

        article.delete()
        data = {"pk": f"{article_pk} is deleted."}
        return Response(data, status=200)


@api_view(["POST"])
def scrap_article(request, article_pk: int):
    result = {
        "result": False,
        "msg": "사용자 정보가 유효하지 않습니다."
    }
    status_code = status.HTTP_401_UNAUTHORIZED

    if request.auth is not None:
        try:
            article = Articles.objects.get(id=article_pk)
            like_user = article.like_user.all()

        except Articles.DoesNotExist:
            result["msg"] = f"article id '{article_pk}'번이 존재하지 않습니다."

        else:
            if request.user not in like_user:
                request.user.like_article.add(article)
                result["result"] = True
                result.pop("msg")
                status_code = status.HTTP_204_NO_CONTENT

            else:
                result["msg"] = "이미 관심 기사로 등록되었습니다."
                status_code = status.HTTP_400_BAD_REQUEST

    return Response(data=result,
                    status=status_code)


@api_view(["POST"])
def unscrap_article(request, article_pk: int):
    result = {
        "result": False,
        "msg": "사용자 정보가 유효하지 않습니다."
    }
    status_code = status.HTTP_401_UNAUTHORIZED

    if request.auth is not None:
        try:
            article = Articles.objects.get(id=article_pk)
            like_user = article.like_user.all()

        except Articles.DoesNotExist:
            result["msg"] = f"article id '{article_pk}'번이 존재하지 않습니다."

        else:
            if request.user in like_user:
                request.user.like_article.remove(article)
                result["result"] = True
                result.pop("msg")
                status_code = status.HTTP_204_NO_CONTENT

            else:
                result["msg"] = "이미 관심 기사에서 해제되었습니다."

    return Response(data=result,
                    status=status_code)
