import re
from django.contrib.auth import (get_user_model,
                                 authenticate)
from django.contrib.auth.hashers import make_password
from rest_framework.serializers import (ModelSerializer,
                                        ValidationError,
                                        CharField)
from .models import datetime, DATETIME_FORMAT


class AccountSerializer(ModelSerializer):
    
    """
    AccountSerializer: 사용자 기본 정보 직렬화 클래슨
    """
    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "username",
            "password",
            "email",
            "introduction",
            "created",
            "last_login"
        ]
        error_messages = {
            "username": {
                "min_length": "계정 길이는 최소 5자 이상이어야 합니다."
            },
            "password": {
                "invalid_length": "비밀번호의 최소 길이는 8자입니다.",
                "non_upper": "하나 이상의 대문자가 포함되어야 합니다.",
                "non_lower": "하나 이상의 소문자가 포함되어야 합니다.",
                "non_number": "하나 이상의 숫자가 포함되어야 합니다.",
                "non_special": "하나 이상의 특수문자가 포함되어야 합니다.",
                "same_password": "변경하려는 비밀번호는 이전 비밀번호와 다르게 지정해야 합니다."
            }
        }

    def validate_username(self, username) -> str | None:

        """
        valiate_username: 사용자가 입력한 username 검증을 위한 seriailizer 매서드
        """

        len_username = len(username)

        # Username 최소값 검증
        if len_username < 5:
            raise ValidationError(self.Meta.error_messages.get("username").get("min_length"))

        return username

    def validate_password(self, password):

        """
        valiate_password: 사용자가 입력한 password 검증을 위한 seriailizer 매서드
        """

        len_password = len(password)
        regex_lower = re.compile(pattern=r"[a-z]")
        regex_upper = re.compile(pattern=r"[A-Z]")
        regex_int = re.compile(pattern=r"\d")
        regex_special = re.compile(pattern=r"[!#\$%\^&*\(\)\\\-\_\?=\+|:;\"\'@`~]")
        err_msg = self.Meta.error_messages.get("password")

        # 비밀번호 길이 확인 (최소 8자 이상, 최대 256자 이하)
        if len_password < 8:
            raise ValidationError(err_msg.get("invalid_length"))

        # 소문자 포함 확인
        elif regex_lower.search(password) is None:
            raise ValidationError(err_msg.get("non_lower"))

        # 대문자 포함 확인
        elif regex_upper.search(password) is None:
            raise ValidationError(err_msg.get("non_upper"))

        # 숫자 포함 확인
        elif regex_int.search(password) is None:
            raise ValidationError(err_msg.get("non_number"))

        # 특수문자 포함 확인
        elif regex_special.search(password) is None:
            raise ValidationError(err_msg.get("non_special"))

        return password

    def save(self,):
        
        """
        save: 회원 가입 입력값의 DB 저장 매서드
        """
        
        new_user = self.Meta.model(**self.data)
        new_user.password = make_password(self.data.get("password"))
        new_user.save()

        result = self.data.copy()
        result.pop("password")
        result["created"] = new_user.created.strftime(DATETIME_FORMAT)
        result["last_login"] = new_user.last_login.strftime(DATETIME_FORMAT)
        return result

    def get_data(self):
        
        """
        get_data: 회원 정보 중 password를 제외한 데이터의 반환을 위한 매서드
        """
        
        result = self.data.copy()
        result["like_articles"] = [article.id for article in self.instance.like_article.all()]
        result.pop("password")
        return result


class AccountsModifySerializer(AccountSerializer):
    
    """
    AccountModifySerializer: 회원 정보 수정 관련 입력값 및 결과 직렬화를 위한 클래스
                             AccountSerializer 클래스 상속
    """

    class Meta:
        model = AccountSerializer.Meta.model
        fields = [
            "email",
            "introduction"
        ]

    def save(self):
        
        """
        save: 회원 정보 수정 시 데이터 저장을 진행하는 매서드
        """
        
        edit_user = self.instance
        for field_name in self.initial_data:
            if field_name in self.Meta.fields:
                setattr(edit_user, field_name, self.initial_data.get(field_name))

        edit_user.save()
        return None


class AccountsPasswordChangeSerializer(AccountSerializer):

    """
    AccountsPasswordChangeSerializer: 계정 비밀번호 변경 관련 입력값 및 결과 직렬화를 위한 클래스
                                      AccountSerializer 클래스 상속
    """

    # 계정의 기존 password 입력을 위한 Field 추가
    pre_password = CharField(max_length=25,
                             required=True)

    class Meta:
        model = AccountSerializer.Meta.model
        fields = [
            "pre_password",
            "password"
        ]
        error_messages = AccountSerializer.Meta.error_messages

    def validate_password(self, n_pw):
        
        """
        validate_password: 새 비밀번호 입력값(password)에 대한 검증 진행
        """
        
        # 입력한 기존 비밀번호 추출
        p_pw = self.initial_data.get("pre_password")

        # 새 비밀번호 및 기존 비밀번호의 동일 여부 확인
        if p_pw == n_pw:
            raise ValidationError(self.Meta.error_messages.get("password").get("same_password"))

        return super().validate_password(password=n_pw)

    def save(self, request) -> bool:
        
        """
        save: 회원 비밀번호 변경 시 데이터 저장을 진행하는 매서드
        """
        
        user = self.instance
        new_password = self.initial_data.get("password")
        
        # Password Encryption 진행
        user.password = make_password(password=new_password)
        user.save()

        return True if just_authenticate(request=request,
                                         username=user.username,
                                         password=new_password) else False


def update_last_login(username, r_token) -> None:

    """
    update_last_login: 로그인 성공 사용자 DB 데이터의 last_login 및 r_token 필드 업데이트

    :param username: 로그인 사용자 계정명
    :param r_token: 로그인 성공 시 반환받은 refresh_token 값
    :return: None
    """

    user_model = AccountSerializer.Meta.model
    login_user = user_model.objects.get(username=username)
    login_user.last_login = datetime.now()
    login_user.r_token = r_token
    login_user.save()
    return None


def just_authenticate(request, username, password) -> AccountSerializer.Meta.model | None:

    """
    just_authenticate: 현재 로그인 한 사용자의 계정명 및 비밀번호의 인증 결과 반환 매서드
    
    :param request: request 객체 
    :param username: 로그인 사용자 계정명
    :param password: 검증을 진행할 사용자 비밀번호(plain text) 입력
    :return: bool. 검증 성공 시 Account 객체를, 검증 실패 시 None 반환
    """

    return authenticate(request=request, username=username, password=password)
