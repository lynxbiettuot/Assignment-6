from django.contrib.auth.models import User
from rest_framework import serializers
from .models import CustomerProfile


# ── Registration ─────────────────────────────────────────────────────────────

class RegisterSerializer(serializers.ModelSerializer):
    password         = serializers.CharField(write_only=True, min_length=6)
    phone            = serializers.CharField(required=False, default='', allow_blank=True)
    address          = serializers.CharField(required=False, default='', allow_blank=True)
    date_of_birth    = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model  = User
        fields = ('id', 'username', 'email', 'password', 'phone', 'address', 'date_of_birth')
        extra_kwargs = {'email': {'required': False}}

    def create(self, validated_data):
        # Pop extra profile fields before creating user
        phone         = validated_data.pop('phone', '')
        address       = validated_data.pop('address', '')
        date_of_birth = validated_data.pop('date_of_birth', None)

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
        )
        CustomerProfile.objects.create(
            user=user,
            phone=phone,
            address=address,
            date_of_birth=date_of_birth,
        )
        return user

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        try:
            profile = instance.customer_profile
            rep['phone']         = profile.phone
            rep['address']       = profile.address
            rep['date_of_birth'] = str(profile.date_of_birth) if profile.date_of_birth else None
        except CustomerProfile.DoesNotExist:
            rep['phone']         = ''
            rep['address']       = ''
            rep['date_of_birth'] = None
        return rep


# ── Profile view / update ─────────────────────────────────────────────────────

class CustomerProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email    = serializers.EmailField(source='user.email', read_only=True)
    user_id  = serializers.IntegerField(source='user.id', read_only=True)

    class Meta:
        model  = CustomerProfile
        fields = ('user_id', 'username', 'email', 'phone', 'address', 'date_of_birth', 'created_at', 'updated_at')
        read_only_fields = ('user_id', 'username', 'email', 'created_at', 'updated_at')

class CustomerManagerSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(source='customer_profile.phone', required=False, allow_blank=True)
    address = serializers.CharField(source='customer_profile.address', required=False, allow_blank=True)
    date_of_birth = serializers.DateField(source='customer_profile.date_of_birth', required=False, allow_null=True)
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'phone', 'address', 'date_of_birth')

    def create(self, validated_data):
        profile_data = validated_data.pop('customer_profile', {})
        password = validated_data.pop('password', None)
        
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data.get('email', '')
        )
        if password:
            user.set_password(password)
        else:
            user.set_password('default123')
        user.save()
        
        CustomerProfile.objects.create(
            user=user,
            phone=profile_data.get('phone', ''),
            address=profile_data.get('address', ''),
            date_of_birth=profile_data.get('date_of_birth')
        )
        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('customer_profile', {})
        password = validated_data.pop('password', None)
        
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        if password:
            instance.set_password(password)
        instance.save()
        
        profile, _ = CustomerProfile.objects.get_or_create(user=instance)
        if 'phone' in profile_data:
            profile.phone = profile_data['phone']
        if 'address' in profile_data:
            profile.address = profile_data['address']
        if 'date_of_birth' in profile_data:
            profile.date_of_birth = profile_data['date_of_birth']
        profile.save()
        return instance
