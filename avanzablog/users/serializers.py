from rest_framework import serializers
from django.contrib.auth.models import User, Group
from django.db import IntegrityError
from .models import Profile

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    team = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['username', 'password', 'confirm_password', 'team']

    def validate(self, data):
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError("User already exists.")
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        team_name = validated_data.pop('team', 'Default Team')
        
        try:
            user = User.objects.create_user(
                username=validated_data['username'],
                password=validated_data['password']
            )
            # Create or get the team (group)
            team, created = Group.objects.get_or_create(name=team_name)
            user.groups.add(team)

            # Create the Profile instance
            Profile.objects.create(user=user, team=team_name)
        except IntegrityError as e:
            raise serializers.ValidationError(f"Database error: {str(e)}")

        return user
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        if not User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError("User does not exist.")
        return data