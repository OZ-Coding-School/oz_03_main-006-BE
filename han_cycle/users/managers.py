from django.contrib.auth.models import BaseUserManager


# CustomUserManager는 사용자(User)와 슈퍼유저(Superuser)를 생성하는 매니저 클래스입니다.
class CustomUserManager(BaseUserManager):

    # 일반 사용자를 생성하는 메서드입니다.
    # nickname: 사용자의 닉네임을 설정합니다.
    # email: 사용자의 이메일 주소입니다. 이메일 필드는 필수입니다.
    # password: 사용자의 비밀번호를 설정합니다. 기본값은 None입니다.
    # **extra_fields: 추가적인 필드들(예: first_name, last_name 등)을 받아서 사용자 객체에 저장합니다.
    def create_user(self, nickname, email, password=None, **extra_fields):

        # 이메일 필드가 설정되지 않은 경우, 오류를 발생시킵니다.
        if not email:
            raise ValueError("The Email field must be set")

        # 이메일 주소를 정규화합니다 (모두 소문자로 변환하는 등의 작업).
        email = self.normalize_email(email)

        # 주어진 필드들로 새로운 사용자 객체를 생성합니다.
        user = self.model(nickname=nickname, email=email, **extra_fields)

        # 사용자의 비밀번호를 해싱하여 설정합니다.
        user.set_password(password)

        # 데이터베이스에 사용자 객체를 저장합니다.
        user.save(using=self._db)

        # 생성된 사용자 객체를 반환합니다.
        return user

    # 슈퍼유저를 생성하는 메서드입니다.
    # nickname: 슈퍼유저의 닉네임을 설정합니다.
    # email: 슈퍼유저의 이메일 주소입니다.
    # password: 슈퍼유저의 비밀번호를 설정합니다. 기본값은 None입니다.
    # **extra_fields: 추가적인 필드들(예: is_staff, is_superuser 등)을 받아서 슈퍼유저 객체에 저장합니다.
    def create_superuser(self, nickname, email, password=None, **extra_fields):

        # 슈퍼유저에게 is_staff와 is_superuser 필드를 기본으로 True로 설정합니다.
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        # is_staff 필드가 True가 아닌 경우, 오류를 발생시킵니다.
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        # is_superuser 필드가 True가 아닌 경우, 오류를 발생시킵니다.
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        # 주어진 필드들로 새로운 슈퍼유저 객체를 생성하고 반환합니다.
        return self.create_user(nickname, email, password, **extra_fields)
