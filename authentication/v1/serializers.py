from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from otp.v1.serializers import OtpVerifySerializer
from otp.choices import OtpPurpose

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    otp_data = serializers.DictField(write_only=True)

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "password", "otp_data")

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        otp_data = validated_data.pop("otp_data")
        otp_data["purpose"] = OtpPurpose.REGISTRATION
        otp_verifier = OtpVerifySerializer(data=otp_data)
        otp_verifier.is_valid(raise_exception=True)

        if not otp_verifier.verify():
            raise serializers.ValidationError("Invalid OTP")

        return User.objects.create_user(**validated_data)


class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = {
            "id": self.user.id,
            "email": self.user.email,
        }
        return data
