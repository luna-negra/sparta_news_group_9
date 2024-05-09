from smtplib import SMTPException
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Q, F, Count, ExpressionWrapper, IntegerField
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import (IsAuthenticated, IsAuthenticatedOrReadOnly)
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.serializers import TokenVerifySerializer
from .models import Comments, Articles, Accounts
from .serializers import CommentSerializer, ArticlesSerializer


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
            return Response({"error": "댓글 내용 입력이 없습니다"}, status=status.HTTP_400_BAD_REQUEST)

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
        current_time = timezone.now()

        articles = Articles.objects.annotate(
            comments_count=Count('comments'),
            like_count=Count('like_user'),
            days_passed=ExpressionWrapper(current_time - F('created'), output_field=IntegerField())
        ).annotate(
            comments_point=F('comments_count') * 3,
            like_point=F('like_count') * 1,
            days_point=ExpressionWrapper(F('days_passed') / timedelta(days=1) * -5, output_field=IntegerField()),
            total_point=F('comments_point') + F('like_point') + F('days_point')
        ).order_by('-total_point')

        serializer = ArticlesSerializer(articles, many=True)
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

        if not isinstance(article, ArticlesSerializer.Meta.model):
            return article

        if not request.user == article.user:
            return Response({"error": "권한 없는 사용자입니다."}, status=status.HTTP_403_FORBIDDEN)

        article.delete()
        data = {"pk": f"{article_pk} is deleted."}
        return Response(data, status=200)


class ArticlesSearchAPIView(generics.ListAPIView):
    #게시글 검색 (title, content, username)
    serializer_class = ArticlesSerializer

    def get_queryset(self):

        query_params = self.request.query_params
        title = query_params.get("title")
        content = query_params.get("content")
        username = query_params.get("username")

        q = Q()

        if title:
            q &= Q(title__icontains=title)
        if content:
            q &= Q(content__icontains=content)
        if username:
            user = Accounts.objects.filter(username=username).first()
            if user:
                q &= Q(user=user)

        return Articles.objects.filter(q)


@api_view(["POST"])
def scrap_article(request, article_pk: int):
    result = {
        "result": False,
        "msg": "사용자 정보가 유효하지 않습니다."
    }
    status_code = status.HTTP_401_UNAUTHORIZED

    try:
        r_token_verify = TokenVerifySerializer(data={"token": request.user.r_token})

    except AttributeError:
        pass

    else:
        if request.auth is not None and r_token_verify.is_valid():
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

    try:
        r_token_verify = TokenVerifySerializer(data={"token": request.user.r_token})

    except AttributeError:
        pass

    else:

        if request.auth is not None and r_token_verify.is_valid():
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


@api_view(["POST"])
def email_article(request, article_pk):
    result = {
        "result": False,
        "msg": "사용자 정보가 유효하지 않습니다."
    }
    status_code = status.HTTP_401_UNAUTHORIZED

    try:
        r_token_verify = TokenVerifySerializer(data={"token": request.user.r_token})

    except AttributeError:
        pass

    else:

        if request.auth is not None and r_token_verify.is_valid():
            try:
                article = Articles.objects.get(id=article_pk)

            except Articles.DoesNotExist:
                result["msg"] = f"article id '{article_pk}'번이 존재하지 않습니다."

            else:
                subject = f"[Sparta News] {article.title}"
                from_email = settings.EMAIL_HOST
                recipient_list = [request.user.email]
                message = \
                    f"""
    안녕하세요. '{request.user.username}' 님.
    메일 전송 요청하신 기사를 아래와 같이 전달드립니다.
    --
    
    제목: {article.title}
    작성자: {article.user.username}
    등록일: {article.created}
    --------------------------------------------------
    {article.content}
    --------------------------------------------------
    
    스파르타 마켓.
    
    """

                try:
                    sending_result = send_mail(subject=subject,
                                               message=message,
                                               from_email=from_email,
                                               recipient_list=recipient_list,
                                               fail_silently=False)

                except SMTPException:
                    result["msg"] = "App Password 인증 실패"
                    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

                else:
                    if sending_result:
                        result["result"] = True,
                        result.pop("msg")
                        status_code = status.HTTP_204_NO_CONTENT

                    else:
                        result["msg"] = "App Password 인증 실패"
                        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    return Response(data=result,
                    status=status_code)
