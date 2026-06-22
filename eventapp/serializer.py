from .models import *
from rest_framework import serializers
from django.contrib.auth import authenticate


class EventAddSerializer(serializers.ModelSerializer):
    is_favorite = serializers.SerializerMethodField()

    class Meta:
        model = EventAdd
        fields = [
            "id",
            "title",
            "description",
            "date",
            "date_end",
            "location",
            "price",
            "capacity",
            "image",
            "type",
            "is_favorite",
        ]

    def get_is_favorite(self, obj):
        request = self.context.get("request")

        if request and request.user.is_authenticated:
            return FavouriteEvent.objects.filter(
                user=request.user,
                event=obj
            ).exists()

        return False

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id","username","ph_number","email"]

        password = serializers.CharField(write_only=True, required=False)

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
    

class FavouriteEventSerializer(serializers.ModelSerializer):
    event = EventAddSerializer(read_only = True)

    class Meta:
        model = FavouriteEvent
        fields = ["id", "event"]


class BookingSerializer(serializers.ModelSerializer):
    event = EventAddSerializer(read_only=True)
    event_id = serializers.PrimaryKeyRelatedField(
        queryset=EventAdd.objects.all(),
        source='event',
        write_only=True
    )
    available_tickets = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = ["id", "event", "event_id", "quantity", "total_price", "available_tickets"]
        read_only_fields = ['total_price']
        

    def get_available_tickets(self, obj):
        total_booked = Booking.objects.filter(event=obj.event).aggregate(
            total=models.Sum('quantity')
        )['total'] or 0
        return obj.event.capacity - total_booked
    

    def validate(self, data):
        event = data['event']
        quantity = data['quantity']

        if quantity > event.capacity:
            raise serializers.ValidationError("Not enough tickets available")

        return data



class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        user = authenticate(username=username, password=password)

        if not user:
            raise serializers.ValidationError("invalid username or password")
        
        if not user.is_active:
            raise serializers.ValidationError("user account is disabled")
        
        attrs ['user'] = user
        return attrs