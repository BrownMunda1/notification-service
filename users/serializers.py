from rest_framework import serializers

from django.contrib.auth import get_user_model

User = get_user_model() # References settings.AUTH_USER_MODEL directly

class UserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "password"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
