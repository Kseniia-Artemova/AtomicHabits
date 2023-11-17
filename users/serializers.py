from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'telegram_username', 'password', 'password2')
        extra_kwargs = {
            'password': {'write_only': True},
        }
        
    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({'password2': 'Введенные пароли не совпадают.'})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

