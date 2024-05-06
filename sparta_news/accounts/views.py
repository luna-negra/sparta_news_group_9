from rest_framework.status import *
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
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

    result = {
        "result": False,
        "msg": None
    }
    status_code = HTTP_400_BAD_REQUEST

    # POST 입력 데이터 Serialization
    serializer = AccountSerializers(data=request.data,
                                    many=False)

    # POST 입력값 검증
    if serializer.is_valid():
        # 새 가입 계정 생성
        data = serializer.save()
        result.pop("msg")
        result["user"] = data
        status_code = HTTP_200_OK

    else:
        result["msg"] = serializer.errors

    # API 처리 결과 반환
    return Response(data=result,
                    status=status_code)


# 회원 로그인
class AccountSignInView(TokenObtainPairView):

    def post(self, request, *args, **kwargs):

        result = {
            "result": False,
            "msg": None
        }
        status_code = HTTP_401_UNAUTHORIZED

        # 데이터 추출 / 계정 검증 및 token 반환
        try:
            data = super().post(request, *args, **kwargs)

        except AuthenticationFailed as e:
            result["msg"] = "계정 정보가 일치하지 않습니다."

        else:
            # refresh 토큰 추출
            r_token = data.data.get("refresh")

            # 로그인 계정 last_date 및 r_token 업데이트
            update_last_login(username=request.data.get("username"),
                              r_token = r_token)

            # 발급된 access_token 반환
            result["result"] = True
            result["access_token"] = data.data.get("access")
            result.pop("msg")
            status_code = HTTP_200_OK

        return Response(data=result,
                        status=status_code)


# 회원 로그아웃
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

    def check_token(self, request) -> bool:
        if request.auth is None:
            return False

        return True

    # 회원 정보 조회
    def get(self, request, account_id: int):

        result = {
            "result": False,
            "msg": None
        }
        status_code = HTTP_401_UNAUTHORIZED

        if not self.check_token(request=request):
            result["msg"] = "로그인 사용자의 유효한 토큰이 입력되지 않았습니다."

        else:
            try:
                user = ACCOUNTS_MNG.get(id=account_id)

            except ACCOUNTS_MODEL.DoesNotExist:
                result["msg"] = "사용자가 존재하지 않습니다."

            else:
                serializer = AccountSerializers(instance=user, many=False)
                result["result"] = True
                result["user"] = serializer.get_data()
                result.pop("msg")
                status_code = HTTP_200_OK

        return Response(data=result,
                        status=status_code)

    # 회원 정보 변경
    def put(self, request, account_id: int):

        result = {
            "result": False,
            "msg": None
        }
        status_code = HTTP_401_UNAUTHORIZED

        if not self.check_token(request=request):
            result["msg"] = "로그인 사용자의 유효한 토큰이 입력되지 않았습니다."

        else:
            if request.user.id == account_id:
                serializer = AccountsModifySerializers(data=request.data,
                                                       instance=ACCOUNTS_MNG.get(id=account_id),
                                                       many=False,
                                                       partial=True)

                if serializer.is_valid():
                    serializer.save()

                    result["result"] = True
                    result["user"] = AccountSerializers(instance=ACCOUNTS_MNG.get(id=account_id),
                                                        many=False).get_data()
                    result.pop("msg")
                    status_code = HTTP_200_OK

                else:
                    result["msg"] = serializer.errors
                    status_code = HTTP_400_BAD_REQUEST

            else:
                result["msg"] = "다른 계정의 변경을 시도했습니다."

        return Response(data=result,
                        status=status_code)

    # 회원 비밀번호 변경
    def patch(self, request, account_id: int):

        result = {
            "result": False,
            "msg": None
        }
        status_code = HTTP_401_UNAUTHORIZED

        if not self.check_token(request=request):
            result["msg"] = "로그인 사용자의 유효한 토큰이 입력되지 않았습니다."

        else:
            if request.user.id == account_id:
                serializer = AccountsPasswordChangeSerializer(data=request.data,
                                                              instance=ACCOUNTS_MNG.get(id=account_id),
                                                              many=False)

                if serializer.is_valid():
                    user = just_authenticate(request=request,
                                             username=request.user.username,
                                             password=request.data.get("pre_password"))

                    if user is not None and serializer.save(request=request):
                        result["result"] = True
                        result.pop("msg")
                        status_code = HTTP_204_NO_CONTENT

                    else:
                        result["msg"] = "비밀번호가 일치하지 않습니다."

                else:
                    result["msg"] = serializer.errors

            else:
                result["msg"] = "다른 계정의 비밀번호 변경을 시도했습니다."

        return Response(data=result,
                        status=status_code)

    # 회원 탈퇴
    def delete(self, request, account_id: int):

        result = {
            "result": False,
            "msg": None
        }
        status_code = HTTP_401_UNAUTHORIZED

        if not self.check_token(request=request):
            result["msg"] = "로그인 사용자의 유효한 토큰이 입력되지 않았습니다."

        else:
            if request.user.id == account_id:

                user = ACCOUNTS_MNG.get(id=account_id)
                input_pw = request.data.get("password")

                if input_pw is not None:
                    if just_authenticate(request=request,
                                         username=user.username,
                                         password=input_pw):

                        user.delete()
                        result["result"] = True
                        result.pop("msg")
                        status_code = HTTP_204_NO_CONTENT

                    else:
                        result["msg"] = "계정 정보가 일치하지 않습니다."

                else:
                    result["msg"] = "탈퇴할 계정의 비밀번호를 입력해야합니다. (key: password)"

            else:
                result["msg"] = "다른 계정의 탈퇴를 시도했습니다."

        return Response(data=result,
                        status=status_code)
