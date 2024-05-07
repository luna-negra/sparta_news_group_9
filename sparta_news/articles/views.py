from rest_framework.request.ForcedAuthentication import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import AccessToken
from .models import Articles
from .serializers import ArticlesSerializer


# Create your views here.

class ArticlesDetailAPIView(APIView):
    def get_object(self, pk):
        return get_object_or_404(Articles, pk=pk)

    def get(self, request):

        user = authenticate(username=request.data['username'], password=request.data['password'])
        if user is not None:
            access_token = AccessToken.for_user(user)
            return Response({'access_token': str(access_token)}, status=200)
        else:
            return Response({'error': 'Invalid credentials'}, status=400)

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
