import time

from rest_framework import serializers

from django.contrib.auth import get_user_model

User = get_user_model() # References settings.AUTH_USER_MODEL directly

class UserSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "password"]

    def create(self, validated_data):
        print(f"Saving user: {validated_data['username']}")
        start_time = time.time()
        created_user = User.objects.create_user(**validated_data)
        elapsed_time = time.time() - start_time
        print(f"Created user {validated_data['username']} in {elapsed_time} seconds")
        return created_user
