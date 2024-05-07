
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
        
        comment = Comments.objects.create(content=content,user=user,article=article)
        serializer = CommentSerializer(comment)
        return Response(serializer.data,status=status.HTTP_201_CREATED)
    

class CommentDetailView(generics.ListAPIView):
    
    """
    HTTP 프로토콜 수정 제안 사항
    
    1. 보통 새 데이터의 추가는 POST()를 사용하고 - 블로그 글을 포스팅한다 -,
    기존에 존재하는 데이터의 수정은 PUT()을 사용합니다. 
    
    PUT()이 댓글 수정인지 확실하지가 않은데, 만약 새 댓글을 작성하는 것이라면
    API 사용 기준을 따르려면 PUT이 아닌 POST를 사용하는 것이 좋을 듯 합니다. :)
    
    2. user 조회하는 코드의 pk 값도 request.user의 id값을 참조하도록 수정부탁드립니다. :)
    """
       
    
    # permission_classes = [IsAuthenticated]
    serializer_class = CommentSerializer

    def put(self,request,comment_id):
        user = get_object_or_404(Accounts, pk=1)
        comment = get_object_or_404(Comments,pk=comment_id)
        content = request.data.get("content")
        if not content:
            return Response({"error":"댓글 내용 입력이 없습니다"})
        
        if len(content) < 5:
            return Response({"error":"댓글의 내용을 5글자 이상 작성해주세요"})
        
        #if request.user == comment.user:
        if user == comment.user:
            comment.content = content
            comment.save()
            serializer = CommentSerializer(comment)
            return Response(serializer.data)
        return Response({"error":"권한 없는 사용자입니다."},status=status.HTTP_403_FORBIDDEN)


    def delete(self,request,comment_id):
        user = get_object_or_404(Accounts, pk=1)
        comment = get_object_or_404(Comments, pk=comment_id)
        #if request.user == comment.user:
        if user == comment.user:
            comment.delete()
            return Response({"message":"댓글이 삭제 되었습니다."},status=status.HTTP_204_NO_CONTENT)
        return Response({"error":"권한 없는 사용자입니다."},status=status.HTTP_403_FORBIDDEN)


class ArticleListView(APIView):

    '''
    permission_classes = [IsAuthenticatedOrReadOnly] - get으로는 읽기 기능만 가능
    
    post에 있던 기능 중복되는 코드 지웠습니다.
    self.permission_classes = [IsAuthenticated]
    '''

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

    """
    반드시 수정이 필요한 부분에 대한 요청

    1. 수정을 진행하는 put()과 삭제를 진행하는 delete()는 다른 사용자가 내 글을 수정/삭제하거나
       내가 다른 사용자의 글을 수정/삭제할 수 있도록 현재 코드가 작성되어 있습니다.
       get()은 상관없지만 put()과 delete()는 내가 작성한 글만 수정과 삭제 가능하도록 수정 부탁드립니다 :)

    2. 계정 테스트로 넣어두신 주석처리된 get()은 삭제하셔도 됩니다 :)
    """


    def get_object(self, article_pk):
        try:
            return Articles.objects.get(pk=article_pk)
        except Articles.DoesNotExist:
            return Response({"error": "Article not found"}, status=status.HTTP_404_NOT_FOUND)

    # 게시글 조회(detail)
    def get(self, request, article_pk):
        get_obj = self.get_object(article_pk)
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
