"""accounts/views.py"""
import base64
import io
import pyotp
import qrcode

from django.contrib.auth import get_user_model, authenticate
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    LoginSerializer,
    TOTPVerifySerializer,
    TOTPSetupConfirmSerializer,
    TOTPDisableSerializer,
)

User = get_user_model()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _tokens_for_user(user):
    """Return access + refresh tokens for a user."""
    refresh = RefreshToken.for_user(user)
    return {
        'access':  str(refresh.access_token),
        'refresh': str(refresh),
    }


def _qr_base64(user):
    """Generate QR code PNG as base64 string."""
    uri = user.get_totp_uri()
    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return base64.b64encode(buf.getvalue()).decode()


# ── Login ─────────────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Step 1 of login.
    - If 2FA disabled: returns JWT tokens immediately.
    - If 2FA enabled: returns {totp_required: true, uid: <user_pk>}.
      Frontend must call /api/auth/totp/verify/ with the code.
    """
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    email    = serializer.validated_data['email']
    password = serializer.validated_data['password']

    user = authenticate(request, username=email, password=password)

    if user is None:
        return Response(
            {'detail': 'Invalid email or password.'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    if not user.is_active:
        return Response(
            {'detail': 'Your account is awaiting activation. Please contact staff.'},
            status=status.HTTP_403_FORBIDDEN
        )

    if user.totp_enabled:
        # Store user pk in session for the TOTP verify step
        request.session['pending_user_pk'] = str(user.pk)
        return Response({
            'totp_required': True,
            'uid': str(user.pk),
        })

    return Response(_tokens_for_user(user))


# ── TOTP — complete login ─────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
def totp_verify(request):
    """
    Step 2 of login when 2FA is enabled.
    Receives the 6-digit TOTP code and issues JWT if valid.
    """
    serializer = TOTPVerifySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    uid = request.session.get('pending_user_pk')
    if not uid:
        return Response(
            {'detail': 'No login in progress. Please log in again.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.get(pk=uid)
    except User.DoesNotExist:
        return Response(
            {'detail': 'Session expired. Please log in again.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not user.verify_totp(serializer.validated_data['code']):
        return Response(
            {'detail': 'Invalid or expired code. Please try again.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Clear the session
    del request.session['pending_user_pk']

    return Response(_tokens_for_user(user))


# ── TOTP — setup ──────────────────────────────────────────────────────────────

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def totp_setup(request):
    """
    GET  — generate a new TOTP secret and return QR code.
    POST — confirm by submitting the first code (enables 2FA).
    """
    user = request.user

    if request.method == 'GET':
        if user.totp_enabled:
            return Response(
                {'detail': '2FA is already enabled.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Generate a new secret (not saved yet — only saved on POST confirmation)
        secret = pyotp.random_base32()
        request.session['pending_totp_secret'] = secret

        # Temporarily set so get_totp_uri() works
        user.totp_secret = secret
        return Response({
            'qr_code': _qr_base64(user),
            'secret':  secret,   # for manual entry in authenticator app
        })

    # POST — confirm
    serializer = TOTPSetupConfirmSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    secret = request.session.get('pending_totp_secret')
    if not secret:
        return Response(
            {'detail': 'Setup session expired. Please start again.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Verify the code against the pending secret
    totp = pyotp.TOTP(secret)
    if not totp.verify(serializer.validated_data['code'], valid_window=1):
        return Response(
            {'detail': 'Invalid code. Please try again.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Save and enable
    user.totp_secret  = secret
    user.totp_enabled = True
    user.save(update_fields=['totp_secret', 'totp_enabled'])

    del request.session['pending_totp_secret']

    return Response({'detail': '2FA enabled successfully.'})


# ── TOTP — disable ────────────────────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def totp_disable(request):
    """Disable 2FA. Requires current TOTP code to confirm."""
    user = request.user

    if not user.totp_enabled:
        return Response(
            {'detail': '2FA is not enabled.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer = TOTPDisableSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    if not user.verify_totp(serializer.validated_data['code']):
        return Response(
            {'detail': 'Invalid code.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user.totp_enabled = False
    user.totp_secret  = ''
    user.save(update_fields=['totp_enabled', 'totp_secret'])

    return Response({'detail': '2FA disabled.'})


# ── Current user ──────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    """Return current user details."""
    from .serializers import UserSerializer
    return Response(UserSerializer(request.user).data)
