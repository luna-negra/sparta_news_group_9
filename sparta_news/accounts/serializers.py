import re
from django.contrib.auth import (get_user_model,
                                 authenticate,
                                 logout)
from rest_framework.serializers import (ModelSerializer,
                                        ValidationError,)
from .models import datetime, DATETIME_FORMAT


class AccountSerializers(ModelSerializer):
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
                "same_password": "이전과 동일한 비밀번호를 사용할 수 없습니다."
            }
        }

    def validate_username(self, username) -> str | None:
        len_username = len(username)

        # Username 최소값 검증
        if len_username < 5:
            raise ValidationError(self.Meta.error_messages.get("username").get("min_length"))

        return username

    def validate_password(self, password):

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

    def save(self, is_modify=False):

        if not is_modify:
            new_user = self.Meta.model(**self.data)
            new_user.set_password(self.data.get("password"))
            new_user.save()

            result = self.data.copy()
            result.pop("password")
            result["created"] = new_user.created.strftime(DATETIME_FORMAT)
            result["last_login"] = new_user.last_login.strftime(DATETIME_FORMAT)
            return result

        edit_user = self.instance
        for field_name in self.initial_data:
            setattr(edit_user, field_name, self.initial_data.get(field_name))

        edit_user.save()




    def get_data(self):
        result = self.data.copy()
        result.pop("password")
        return result


class AccountsModifySerializers(AccountSerializers):

    class Meta:
        model = get_user_model()
        fields = [
            "email",
            "introduction"
        ]





def update_last_login(username, r_token) -> None:

    user_model = AccountSerializers.Meta.model
    login_user = user_model.objects.get(username=username)
    login_user.last_login = datetime.now()
    login_user.r_token = r_token
    login_user.save()
    return None
