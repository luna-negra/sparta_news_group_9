from django.shortcuts import render
from rest_framework.status import *
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import *

# Create your views here.


# 회원 가입
@api_view(["POST"])
def signup(request):

    # POST 입력 데이터 Serialization
    serializer = AccountSerializers(data=request.data,
                                    many=False)

    # POST 입력값 검증
    serializer.is_valid(raise_exception=True)

    # 새 가입 계정 생성
    data = serializer.save()

    # API 처리 결과 반환
    return Response(data={"result": True, "user": data})



# 회원 로그인
class AccountSignInView(TokenObtainPairView):

    def post(self, request, *args, **kwargs):
        pass


#회원 로그아웃
@api_view(["POST"])
def signout(request):
    return Response(data={"title": "회원로그아웃"})



class AccountsDetailView(APIView):

    # 회원 정보 조회
    def get(self, request, account_id: int):
        return Response(data={"title": "회원정보조회"})


    # 회원 정보 수정
    def put(self, request, account_id: int):
        return Response(data={"title": "회원정보수정"})


    # 회원 비밀번호 변경
    def patch(self, request, account_id: int):
        return Response(data={"title": "비밀번호 변경"})


    # 회원 탈퇴
    def delete(self, request, account_id: int):
        return Response(data={"title": "회원탈퇴"})

