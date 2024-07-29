from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.mail import send_mail
from djoser.serializers import PasswordResetConfirmRetypeSerializer
from rest_framework import serializers

from poker_elite.settings import EMAIL_HOST_USER

User = get_user_model()


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    refferalcode = serializers.CharField(required=False)
    nikname = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ['email', 'password', 'refferalcode', 'nikname']

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            refferalcode=validated_data.get('refferalcode', None),
            nikname=validated_data.get('nikname', None)
        )
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'nikname', 'avatar_id', 'balance', 'FA', 'refferalcode']
        read_only_fields = ['email']

    def update(self, instance, validated_data):
        instance.nikname = validated_data.get('nikname', instance.nikname)
        instance.avatar_id = validated_data.get('avatar_id', instance.avatar_id)
        instance.balance = validated_data.get('balance', instance.balance)
        instance.FA = validated_data.get('FA', instance.FA)
        instance.refferalcode = validated_data.get('refferalcode', instance.refferalcode)
        instance.save()
        return instance


class UserActivationSerializer(serializers.Serializer):
    activation_code = serializers.CharField(max_length=4)

    def validate_activation_code(self, value):
        try:
            user = User.objects.get(activation_code=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid activation code.")
        return value


class CustomActivationSerializer(serializers.Serializer):
    activation_code = serializers.CharField(max_length=4)

    default_error_messages = {
        "invalid_code": "Invalid activation code."
    }

    def validate(self, attrs):
        activation_code = attrs.get('activation_code')

        try:
            self.user = User.objects.get(activation_code=activation_code)
        except User.DoesNotExist:
            self.user = None

        if not self.user or not self.user.activation_code == activation_code:
            self.fail('invalid_code')

        if self.user.is_active:
            self.fail('stale_token')

        return attrs


class CustomUserPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Пользователь с таким email не найден.")
        return value

    def update(self, instance, validated_data):
        instance.is_active = False
        instance.generate_activation_code()
        instance.save()
        return instance

    def get_user(self):
        email = self.validated_data.get('email')
        return User.objects.get(email=email)


class CustomPasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    activation_code = serializers.CharField(max_length=4)
    new_password = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    def validate(self, attrs):
        try:
            user = User.objects.get(email=attrs['email'], activation_code=attrs['activation_code'])
        except User.DoesNotExist:
            raise serializers.ValidationError({"activation_code": "Неверный код активации или email."})

        validate_password(attrs['new_password'], user)

        self.user = user
        return attrs

    def save(self):
        user = self.user
        user.set_password(self.validated_data['new_password'])
        user.is_active = True  # Устанавливаем is_active в True
        user.activation_code = None  # Опционально: сбросить код активации после использования
        user.save()
        return user