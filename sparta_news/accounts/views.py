from rest_framework.status import *
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenBlacklistSerializer, TokenVerifySerializer
from rest_framework_simplejwt.exceptions import TokenError
from .serializers import *


# Create your views here.


# CONSTANT VARIABLES
ACCOUNTS_MODEL = AccountSerializer.Meta.model
ACCOUNTS_MNG = ACCOUNTS_MODEL.objects


@api_view(["POST"])
def signup(request):

    """
    signup: 회원 가입 FBV
    """

    # 반환값 및 status_code 초기값 설정
    result = {
        "result": False,
        "msg": None
    }
    status_code = HTTP_400_BAD_REQUEST

    # POST 입력 데이터 Serialization
    serializer = AccountSerializer(data=request.data,
                                   many=False)

    # POST 입력값 검증
    if serializer.is_valid():
        # 새 가입 계정 생성
        data = serializer.save()

        # 반환값 내용 및 status_code 수정
        result.pop("msg")
        result["user"] = data
        result["result"] = True
        status_code = HTTP_200_OK

    else:
        # 입력값 검증 실패 시, 입력값 이상 내역 반환
        result["msg"] = serializer.errors

    # API 처리 결과 반환
    return Response(data=result,
                    status=status_code)


class AccountSignInView(TokenObtainPairView):

    """
    AccountSignView: 회원 로그인 CBV
    """

    def post(self, request, *args, **kwargs):
        # 반환값 및 status_code 초기값 설정
        result = {
            "result": False,
            "msg": None
        }
        status_code = HTTP_401_UNAUTHORIZED

        # 데이터 추출 / 계정 검증 및 token 반환
        try:
            data = super().post(request, *args, **kwargs)

        # 로그인 계정 정보 불일치 시, result["msg"] 값 처리를 위한 AuthenticationFailed 예외처리.
        except AuthenticationFailed:
            result["msg"] = "계정 정보가 일치하지 않습니다."

        # 계정 정보 일치 시,
        else:
            # refresh 토큰 추출
            r_token = data.data.get("refresh")

            # 로그인 계정 last_date 및 발급받은 refresh token을 DB r_token 필드에 업데이트
            update_last_login(username=request.data.get("username"),
                              r_token=r_token)

            # 발급된 access_token을 반환값에 포함
            result["result"] = True
            result["access_token"] = data.data.get("access")
            result.pop("msg")
            status_code = HTTP_200_OK

        return Response(data=result,
                        status=status_code)


@api_view(["POST"])
def signout(request):

    """
    signout: 회원 탈퇴 FBV
    """

    # 로그인 사용자 토큰 추출 및 반환값/status_code 초기값 설정
    token = request.auth
    status_code = HTTP_401_UNAUTHORIZED
    result = {
        "result": False,
        "msg": "사용자 정보가 유효하지 않습니다.",
    }

    # 토큰이 존재하는 경우,
    if token is not None:

        # 사용자의 로그인 시 유효한 Refresh Token 값을 DB에서 추출
        r_token = request.user.r_token

        # 사용자 요청 정보 내 refresh token 정보를 추가
        request.data["refresh"] = r_token

        # 사용자 요청 정보를 TokenBlacklistSerializer로 전달하여 현재 token의 무효화 진행
        serializer = TokenBlacklistSerializer(data=request.data)

        try:
            # refresh 토큰 유효 여부 확인
            serializer.is_valid()

            result["result"] = True
            result.pop("msg")
            status_code=HTTP_204_NO_CONTENT

        except TokenError:
            # 사용자가 이미 유효하지 않은 token을 가지고 있는 경우(로그아웃 또는 lifetime 만료)
            result["msg"] = "이미 로그아웃 된 계정입니다."
            status_code = HTTP_400_BAD_REQUEST

    return Response(data=result,
                    status=status_code)


class AccountDetailView(APIView):

    """
    AccountsDetailView: 특정 Account 작업 관련 CBV
    - 회원 정보 조회 (get)
    - 회원 정보 수정 (put)
    - 회원 비밀번호 수정(patch)
    - 회원 탈퇴 (delete)
    """

    def check_token(self, request) -> bool:
        # 로그인 사용자 토큰 확인을 위한 매서드
        # IsAuthenticated 클래스 사용 대신 매서드 구현
        # -> Token 관련 ValidationError 발생 시, API 결과 내에 result 키 생성 불가로 인해 매서드 구현
        # 사용자 access_token 입력 여부 및 refresh_token 유효 여부에 따라 True/False 반환

        r_token_verify = TokenVerifySerializer(data={"token": request.user.r_token})
        if request.auth is None or not r_token_verify.is_valid():
            return False
        
        return True

    def get(self, request, account_id: int):
        # 반환값 및 status_code 초기값 설정
        result = {
            "result": False,
            "msg": None
        }
        status_code = HTTP_401_UNAUTHORIZED

        # 로그인 사용자 토큰 확인
        if not self.check_token(request=request):
            result["msg"] = "로그인 사용자의 유효한 토큰이 입력되지 않았습니다."

        else:
            try:
                # account_id 사용자 정보 추출
                user = ACCOUNTS_MNG.get(id=account_id)

            except ACCOUNTS_MODEL.DoesNotExist:
                # account_id 사용자가 존재하지 않는 경우,
                result["msg"] = "사용자가 존재하지 않습니다."

            else:
                # 사용자 존재 시, Serializer로 계정 정보 직렬화 및 반환.
                serializer = AccountSerializer(instance=user, many=False)
                result["result"] = True
                result["user"] = serializer.get_data()
                result.pop("msg")
                status_code = HTTP_200_OK

        return Response(data=result,
                        status=status_code)

    def put(self, request, account_id: int):
        # 반환값 및 status_code 초기값 설정
        result = {
            "result": False,
            "msg": None
        }
        status_code = HTTP_401_UNAUTHORIZED

        # 로그인 사용자 토큰 확인
        if not self.check_token(request=request):
            result["msg"] = "로그인 사용자의 유효한 토큰이 입력되지 않았습니다."

        else:
            # 로그인 사용자 id와 account_id 일치 여부 확인
            if request.user.id == account_id:

                # 회원 정보 변경 내역 및 기존 account_id 이전 정보 직렬화
                serializer = AccountsModifySerializer(data=request.data,
                                                      instance=ACCOUNTS_MNG.get(id=account_id),
                                                      many=False,
                                                      partial=True)

                # 회원 정보 변경 내역 입력값 검증 진행
                if serializer.is_valid():
                    # 입력값 검증 완료 시, 입력 데이터 및 기존 회원 정보 중 변경되지 않은 내용 저장.
                    serializer.save()

                    # 반환 데이터 처리. Password 제외한 정보 반환을 위해 AccountSerializer 사용
                    result["result"] = True
                    result["user"] = AccountSerializer(instance=ACCOUNTS_MNG.get(id=account_id),
                                                       many=False).get_data()
                    result.pop("msg")
                    status_code = HTTP_200_OK

                else:
                    # 입력값 검증에 이상이 있는 경우,
                    result["msg"] = serializer.errors
                    status_code = HTTP_400_BAD_REQUEST

            else:
                result["msg"] = "다른 계정의 변경을 시도했습니다."

        return Response(data=result,
                        status=status_code)

    def patch(self, request, account_id: int):
        # 반환값 및 status_code 초기값 설정
        result = {
            "result": False,
            "msg": None
        }
        status_code = HTTP_401_UNAUTHORIZED

        # 로그인 사용자 토큰 확인
        if not self.check_token(request=request):
            result["msg"] = "로그인 사용자의 유효한 토큰이 입력되지 않았습니다."

        else:
            # 로그인 사용자 id와 account_id 일치 여부 확인
            if request.user.id == account_id:

                # 회원 정보 변경 내역 및 기존 account_id 이전 정보 직렬화
                serializer = AccountsPasswordChangeSerializer(data=request.data,
                                                              instance=ACCOUNTS_MNG.get(id=account_id),
                                                              many=False)

                # 비밀번호 변경 관련 사용자 입력값 검증 진행
                if serializer.is_valid():

                    # 사용자 계정의 이전 비밀번호 인증 성공 시, 반환되는 Account 객체 저장
                    user = just_authenticate(request=request,
                                             username=request.user.username,
                                             password=request.data.get("pre_password"))

                    # 이전 비밀번호로 인증 성공 시, 새 비밀번호 정보를 DB password 필드에 업데이트
                    # 업데이트 성공 시 True 값 반환
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

    def delete(self, request, account_id: int):
        # 반환값 및 status_code 초기값 설정
        result = {
            "result": False,
            "msg": None
        }
        status_code = HTTP_401_UNAUTHORIZED

        # 로그인 사용자 토큰 확인
        if not self.check_token(request=request):
            result["msg"] = "로그인 사용자의 유효한 토큰이 입력되지 않았습니다."

        else:
            # 로그인 사용자 id와 account_id 일치 여부 확인
            if request.user.id == account_id:

                # account_id 사용자 정보를 user에 저장
                user = ACCOUNTS_MNG.get(id=account_id)

                # 사용자가 request body에 입력한 password 값 추출
                input_pw = request.data.get("password")

                # request body 내 password 필드 존재 시
                if input_pw is not None:
                    # 입력한 password 값에 대한 사용자 인증 진행. 성공 시, Account 객체 반환
                    if just_authenticate(request=request,
                                         username=user.username,
                                         password=input_pw):

                        # 사용자 계정 비밀번호 인증 성공 시 계정 삭제 진행.
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
