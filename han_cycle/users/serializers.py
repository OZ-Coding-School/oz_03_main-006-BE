from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['nickname', 'email', 'password'] #return by POST 
        extra_kwargs = {
            'password': {'write_only':True} #won't show password
        }

    #hashed password
    def create(self, validated_data):
        password = validated_data.pop('password',None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password) #password provided Django (hashed)
        instance.save()
        return instance
