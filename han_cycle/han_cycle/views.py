from django.shortcuts import render

def profile_view(request):
    # Access the user object from the request
    user = request.user

    # Retrieve profile data based on the user
    # (Replace with your logic to get relevant profile data)
    profile_data = {'username': user.username, 'email': user.email}

    context = {'profile_data': profile_data}
    return render(request, 'profile.html', context)