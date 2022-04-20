from drf_writable_nested.serializers import WritableNestedModelSerializer

from rest_framework import serializers
from rest_framework.authtoken.models import Token

from accounts.models import Account, Document, Interest, Location

class DocumentSerializer(serializers.ModelSerializer):
    file = serializers.FileField()
    class Meta:
        model = Document
        fields = ['id', 'file']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        file = {
            "url": representation.pop("file"),
            "name": instance.file.name.replace('documents/', ''),
        }
        representation['file'] = file
        return representation

class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = ['id', 'name']

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'latitude', 'longitude']

class AccountSerializer(WritableNestedModelSerializer, serializers.ModelSerializer):
    areas_of_interest = InterestSerializer(many=True)
    user_documents = DocumentSerializer(many=True)
    location_of_home = LocationSerializer()
    location_of_office = LocationSerializer()

    class Meta:
        model = Account
        fields = ('id', 'username', 'country', 'areas_of_interest', 'phone_number', 'user_documents', 'location_of_home', 'location_of_office', )

class AccountSignUpSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(max_length=255, write_only=True)

    class Meta:
        model = Account
        fields = ['id', 'username', 'phone_number', 'email', 'country', 'date_of_birth', 'password', 'confirm_password']
        read_only_fields = ['id', 'username',]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['phone_number'].required = True

    def validate_phone_number(self, data):
        if Account.objects.filter(phone_number=data).exists():
            raise serializers.ValidationError('User with this phone number already exists.')
        return data

    def validate_email(self, data):
        if data != None and Account.objects.filter(email=data).exists():
            raise serializers.ValidationError('User with this email already exists.')
        return data

    def validate(self, data):
        password = data.get('password')
        confirm_password=data.get('confirm_password')
        if password != confirm_password:
            raise serializers.ValidationError("Your password doesn't match")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        password = validated_data.pop('password')
        account = Account(**validated_data)
        account.set_password(password)
        account.save()
        return account

    def to_representation(self, instance):
        token = self.create_token(user=instance)
        data = {}
        data['token'] = token.key
        data['user'] = AccountSerializer(instance=instance).data
        return data

    def create_token(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        return token