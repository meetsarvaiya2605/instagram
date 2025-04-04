from django.shortcuts import render
from datetime import datetime,timedelta
import jwt
from django.conf import settings
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from dotenv import load_dotenv
from .serializers import UserSerializer, LoginSerializer
from .models import User
from django.http import JsonResponse
from rest_framework import status


load_dotenv()

SECRET_KEY = settings.SIMPLE_JWT["SIGNING_KEY"]

# Create your views here.
def create_access_token(user):
    payload = {
        "user_id": user._id,  # Ensure _id is included
        "exp": datetime.utcnow() + timedelta(days=1),
        "iat": datetime.utcnow(),
        "type": "access",
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token


def create_refresh_token(user):
    payload = {
        "user_id": user._id,  # Ensure _id is included
        "exp": datetime.utcnow() + timedelta(days=7),
        "iat": datetime.utcnow(),
        "type": "refresh",
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token


# SignUp View
class SignUpView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            is_user_found = User.objects(email=email).first()
            if is_user_found is not None:
                return JsonResponse(
                    {"message": "User already exists."},  # JSON data must be in a dictionary
                    status=status.HTTP_400_BAD_REQUEST
                )

            user = serializer.save()
            # breakpoint()
            access_token = create_access_token(user)
            refresh_token = create_refresh_token(user)

            user_data = UserSerializer(user).data

            print("user_data : ", user_data)

            return JsonResponse(
                {
                    "message": "User created successfully.",
                    "data": {
                        "user": user_data,  
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                    }
                },
                # status=status.HTTP_201_CREATED  # HTTP 201 for "Created"
            )


        return JsonResponse(
            {"message": serializer.errors, "error": serializer.errors},  # Include error in response body
            status=status.HTTP_400_BAD_REQUEST  # ✅ Use 'status' instead of 'status_code'
        )



# SignIn View
class SignInView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]

            # Check if user exists
            user = User.objects(email=email).first()
            if user and user.check_password(password):

                # Generate a token
                access_token = create_access_token(user)
                refresh_token = create_refresh_token(user)

                # Serialize the user object to a dictionary
                user_data = UserSerializer(user).data
                return JsonResponse(
                    {"message":"Login successfully.",
                    "user": user_data,  # Use serialized user data
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    },
                    status=status.HTTP_200_OK,
                )
            return JsonResponse(
                {"message":"Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED
            )
        return JsonResponse(
            {"message":serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
            error=serializer.errors,
        )

        