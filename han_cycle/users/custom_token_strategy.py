# custom_token_strategy.py
from allauth.headless.tokens.base import AbstractTokenStrategy
from allauth.socialaccount.models import SocialToken, SocialAccount

class CustomTokenStrategy(AbstractTokenStrategy):
    def __init__(self, provider):
        self.provider = provider

    def get_token(self, user):
        try:
            social_account = SocialAccount.objects.get(user=user, provider=self.provider)
            social_token = SocialToken.objects.get(account=social_account)
            return social_token.token
        except SocialAccount.DoesNotExist:
            return None
        except SocialToken.DoesNotExist:
            return None
