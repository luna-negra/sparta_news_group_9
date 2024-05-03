from django.shortcuts import render, get_object_or_404
from rest_framework.status import *
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenBlacklistSerializer
from rest_framework_simplejwt.exceptions import TokenError
from .serializers import *

# Create your views here.


# CONSTANT VARIABLES
ACCOUNTS_MODEL = AccountSerializers.Meta.model
ACCOUNTS_MNG = ACCOUNTS_MODEL.objects


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

        # 데이터 추출 / 계정 검증 및 token 반환
        data = super().post(request, *args, **kwargs)

        # refresh 토큰 추출
        r_token = data.data.get("refresh")

        # 로그인 계정 last_date 및 r_token 업데이트
        update_last_login(username=request.data.get("username"),
                          r_token = r_token)

        # 발급된 access_token 반환
        data = {
            "result": True,
            "access_token": data.data.get("access")
        }
        return Response(data=data,
                        status=HTTP_200_OK)


#회원 로그아웃
@api_view(["POST"])
def signout(request):

    token = request.auth
    status_code = HTTP_401_UNAUTHORIZED
    result = {
        "result": False,
        "msg": "사용자 정보가 유효하지 않습니다.",
    }

    if token is not None:

        r_token = request.user.r_token
        request.data["refresh"] = r_token
        serializer = TokenBlacklistSerializer(data=request.data)

        try:
            serializer.is_valid()
            result["result"] = True
            result.pop("msg")

        except TokenError:
            result["msg"] = "이미 로그아웃 된 계정입니다."
            status_code = HTTP_400_BAD_REQUEST

    return Response(data=result,
                    status=status_code)


class AccountsDetailView(APIView):

    permission_classes = [IsAuthenticated]

    # 회원 정보 조회
    def get(self, request, account_id: int):

        result = {
            "result": False,
            "msg": "계정이 존재하지 않습니다."
        }
        status_code = HTTP_400_BAD_REQUEST

        try:
            user = ACCOUNTS_MNG.get(id=account_id)

        except ACCOUNTS_MODEL.DoesNotExist:
            pass

        else:
            serializer = AccountSerializers(instance=user, many=False)
            result["result"] = True
            result["user"] = serializer.get_data()
            result.pop("msg")
            status_code = HTTP_200_OK

        return Response(data=result,
                        status=status_code)


    # 회원 정보 수정
    def put(self, request, account_id: int):
        return Response(data={"title": "회원정보수정"})


    # 회원 비밀번호 변경
    def patch(self, request, account_id: int):
        return Response(data={"title": "비밀번호 변경"})


    # 회원 탈퇴
    def delete(self, request, account_id: int):
        return Response(data={"title": "회원탈퇴"})

