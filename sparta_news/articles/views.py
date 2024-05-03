from django.shortcuts import render
from rest_framework import generics

def test(request):
    pass

class CommentListCreatView(generics.ListAPIView):
    def get(self,request):
        pass

    def post(self,request):
        pass