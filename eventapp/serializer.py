from .models import *
from rest_framework import serializers
from django.contrib.auth import authenticate


class EventAddSerializer(serializers.ModelSerializer):
    is_favorite = serializers.SerializerMethodField()
    image = serializers.ImageField(use_url=True)

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
        fields = ["id", "username", "ph_number", "email", "password"]

        password = serializers.CharField(write_only=True)


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



User = get_user_model()

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        print("Username:", username)
        print("Password:", password)

        try:
            user = User.objects.get(username=username)
            print("User exists:", user.username)
            print("Password correct:", user.check_password(password))
        except User.DoesNotExist:
            print("User does not exist")

        user = authenticate(username=username, password=password)
        print("Authenticate result:", user)

        if not user:
            raise serializers.ValidationError("invalid username or password")

        attrs["user"] = user
        return attrs