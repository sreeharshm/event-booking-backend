from django.shortcuts import render
from rest_framework import permissions, authentication
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import portrait
from reportlab.lib.utils import ImageReader
from io import BytesIO

from .utilis.send_email_otp import *
from .utilis.otp_generate import *

from .models import *
from .serializer import *
from django.contrib.auth import get_user_model


class CheckAdmin(APIView):
    permission_classes = []

    def get(self, request):
        try:
            user = User.objects.get(username="admin")
            return Response({
                "exists": True,
                "is_active": user.is_active,
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
            })
        except User.DoesNotExist:
            return Response({"exists": False})



User = get_user_model()

class CreateAdmin(APIView):
    permission_classes = []

    def get(self, request):
        try:
            user = User.objects.get(username="admin")

            user.set_password("admin")
            user.is_active = True
            user.is_staff = True
            user.is_superuser = True
            user.save()

            return Response({
                "message": "Admin password reset successfully"
            })

        except User.DoesNotExist:
            user = User.objects.create_superuser(
                username="admin",
                password="admin",
                email="admin@example.com"
            )

            return Response({
                "message": "Admin created successfully"
            })
    


class UserView(APIView):
    def get(self, request):
        user = User.objects.all()
        serializer = UserSerializer(user, many=True)
        return Response(data=serializer.data)
    
    def post(self, request):
        serializer = UserSerializer(data= request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UserEditView(APIView):
    permission_classes=[permissions.IsAuthenticated]
    authentication_classes=[JWTAuthentication]

    def get(self, request, *args, **kw):
        uid = kw.get('id')
        user = User.objects.get(id=uid)
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
    def put(self, request, *args, **kw):
        uid = kw.get('id')
        user = User.objects.get(id=uid)
        serializer = UserSerializer(user, data = request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data)
        return Response(serializer.data, status=400)
    
    def delete(self, request, *args, **kw):
        uid = kw.get('id')
        user = User.objects.get(id=uid).delete()
        return Response(status=204)
    


class CurrentUserView(APIView):
    permission_classes=[permissions.IsAuthenticated]
    authentication_classes=[JWTAuthentication]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    


class GetAllUserView(APIView):
    permission_classes=[permissions.IsAuthenticated]
    authentication_classes=[JWTAuthentication]

    def get(self, request):
        user = User.objects.all()
        serializer = UserSerializer(user, many=True)
        return Response(data=serializer.data)
    


class EventView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        event = EventAdd.objects.all()
        serializer = EventAddSerializer(
            event,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)


class EventDetailView(APIView):
    def get(self, request, *args, **kwargs):
        event_id = kwargs.get("id")
        event = get_object_or_404(EventAdd, id=event_id)
        # FIX: Also add context here for consistency when viewing a single event card
        serializer = EventAddSerializer(event, context={'request': request})
        return Response(serializer.data)
    
    

class EventAddView(APIView):
    permission_classes = [permissions.IsAdminUser]
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        serializer = EventAddSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class EventEditView(APIView):
    permission_classes = [permissions.IsAdminUser]
    authentication_classes = [JWTAuthentication]

    def put(self, request, *args, **kwargs):
        event_id = kwargs.get('id')
        event = get_object_or_404(EventAdd, id=event_id)
        serializer = EventAddSerializer(event, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        event_id = kwargs.get('id')
        event = get_object_or_404(EventAdd, id=event_id)
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    

class FavouriteEventView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]


    def post(self, request, id):  
        user = request.user
        
        event = get_object_or_404(EventAdd, id=id)
        fav_exists = FavouriteEvent.objects.filter(user=user, event=event).first()

        if fav_exists:
            fav_exists.delete()
            return Response({"message": "Removed from favorites", "is_favorited": False}, status=200)
        
        FavouriteEvent.objects.create(user=user, event=event)
        return Response({"message": "Added to favorites", "is_favorited": True}, status=201)
    


class RemoveFavEvent(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def delete(self, request, id):
        event = get_object_or_404(EventAdd, id=id)

        FavouriteEvent.objects.filter(
            user=request.user,
            event=event
        ).delete()

        return Response(
            {"message": "Removed from favorites"},
            status=status.HTTP_200_OK
        )
    


class GetFavEvent(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        fav_events = FavouriteEvent.objects.filter(
            user_id=request.user.id
        )

        serializer = FavouriteEventSerializer(
            fav_events,
            many=True
        )

        return Response(serializer.data)

    
class BookingView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        user = request.user
        booking = Booking.objects.filter(user=user)
        serializer = BookingSerializer(booking, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        user = request.user
        serializer = BookingSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    

class LoginView(APIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        print(request.data)

        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)

        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "username": user.username,
                "email": user.email,
                "ph_number": user.ph_number,
                "is_staff": user.is_staff,
                "is_superuser": user.is_superuser,
            }
        })



class SendPasswordResetOTP(APIView):
    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response(
                {"error": "Email is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.filter(email=email).first()
        if not user:
            return Response(
                {"error": "No account found with this email."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Optional: delete old OTPs to prevent multiple valid OTPs
        OTP.objects.filter(email=email, otp_type="password_reset").delete()

        # Generate OTP
        otp_code = generate_otp()

        # Create OTP record
        OTP.objects.create(
            email=email,
            otp=otp_code,
            otp_type="password_reset"
        )

        # Send email
        send_password_reset_email(email, otp_code)

        return Response(
            {"message": "A password reset OTP has been sent to your email."},
            status=status.HTTP_200_OK
        )
    


class VerifyPasswordResetOTP(APIView):

    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')

        if not email or not otp:
            return Response(
                {"error": "Email and OTP required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        otp_record = OTP.objects.filter(
            email=email,
            otp=otp,
            otp_type='password_reset'
        ).first()

        if not otp_record:
            return Response(
                {"error": "Invalid OTP"},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {"message": "OTP verified successfully"},
            status=status.HTTP_200_OK
        )



class ResetPasswordView(APIView):

    def post(self, request):
        email = request.data.get('email')
        new_password = request.data.get('new_password')

        if not email or not new_password:
            return Response(
                {"error": "Email and new password required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.filter(email=email).first()
        if not user:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        user.set_password(new_password)
        user.save()

        OTP.objects.filter(email=email, otp_type='password_reset').delete()

        return Response(
            {"message": "Password reset successfully"},
            status=status.HTTP_200_OK
        )
    


class DownloadTicket(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, id):
        booking = get_object_or_404(Booking, id=id, user=request.user)

        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename=ticket_{id}.pdf'

        # Modern Ticket Size (Portrait)
        w, h = 300
        pdf = canvas.Canvas(response, pagesize=(w, h))

        # --- BACKGROUND & BORDER ---
        pdf.setStrokeColor(colors.lightgrey)
        pdf.roundRect(10, 10, w-20, h-20, 15, stroke=1, fill=0)

        # --- HEADER SECTION (Branding) ---
        pdf.setFillColor(colors.HexColor("#F84464")) # Match your UI Red/Pink
        pdf.roundRect(10, h-70, w-20, 60, 10, stroke=0, fill=1)
        
        pdf.setFillColor(colors.white)
        pdf.setFont("Helvetica-Bold", 18)
        pdf.drawCentredString(w/2, h-45, "ADMIT ONE")
        
        pdf.setFont("Helvetica", 9)
        pdf.drawCentredString(w/2, h-58, "OFFICIAL EVENT PASS")

        # --- MAIN CONTENT ---
        pdf.setFillColor(colors.black)
        
        # Event Title (Large)
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawCentredString(w/2, h-110, booking.event.title.upper())

        # Vertical Divider Line
        pdf.setStrokeColor(colors.HexColor("#EEEEEE"))
        pdf.line(20, h-130, w-20, h-130)

        # Labels & Values Helper
        def draw_field(label, value, y_pos):
            pdf.setFont("Helvetica-Bold", 8)
            pdf.setFillColor(colors.grey)
            pdf.drawString(30, y_pos, label.upper())
            pdf.setFont("Helvetica", 11)
            pdf.setFillColor(colors.black)
            pdf.drawString(30, y_pos - 15, str(value))

        # Fields
        draw_field("Attendee", booking.user.username, h-160)
        draw_field("Date & Time", booking.event.date.strftime('%d %b %Y, %I:%M %p'), h-210)
        draw_field("Location", booking.event.location, h-260)
        draw_field("Booking ID", f"#{booking.id:06d}", h-310)
        draw_field("Quantity", booking.quantity, h-360)

        # --- TEAR-OFF SECTION ---
        # Dashed line
        pdf.setDash(3, 3)
        pdf.setStrokeColor(colors.grey)
        pdf.line(10, 100, w-10, 100)
        pdf.setDash(1, 0) # Reset dash

        # Price Info in Tear-off
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawCentredString(w/2, 65, f"TOTAL: ₹{booking.quantity * booking.event.price}")
        
        pdf.setFont("Helvetica", 8)
        pdf.setFillColor(colors.grey)
        pdf.drawCentredString(w/2, 45, "Non-Transferable | Present at Entrance")

        # --- FOOTER ---
        pdf.setFont("Helvetica-Oblique", 7)
        pdf.drawCentredString(w/2, 25, "Generated by Your Event Platform")

        pdf.showPage()
        pdf.save()

        return response