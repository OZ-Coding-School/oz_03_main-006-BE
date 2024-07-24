from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):

    def get_login_redirect_url(self, request):
        return '/users/accounts/profile/'


    def populate_user(self, request, sociallogin, data):
        user = super().populate_user(request, sociallogin, data)
        if sociallogin.account.provider == 'naver':
            naver_data = sociallogin.account.extra_data
            full_name = naver_data.get('name', '')  # Get the full name from Naver's data
            if full_name:
                user.last_name = full_name[0]  # First letter as first name
                user.first_name = full_name[1:] if len(full_name) > 1 else ''  # Rest as last name
        return user
