"""
Supabase JWT Authentication Middleware.
Validates Authorization: Bearer <token> on every request.
Attaches user_id and email to request object.
"""
import jwt
from django.conf import settings
from django.http import JsonResponse


class SupabaseJWTMiddleware:
    """
    Middleware that reads the Supabase JWT from the Authorization header,
    validates it, and populates request.user_id / request.user_email.
    Views that require auth should check for request.user_id.
    """

    # Paths that do NOT require authentication
    PUBLIC_PATHS = []

    def __init__(self, get_response):
        self.get_response = get_response
        self.jwks_client = None
        if settings.SUPABASE_URL:
            # Construct JWKS URL for Supabase
            jwks_url = f"{settings.SUPABASE_URL.rstrip('/')}/auth/v1/.well-known/jwks.json"
            self.jwks_client = jwt.PyJWKClient(jwks_url)

    def __call__(self, request):
        request.user_id = None
        request.user_email = None

        # Only enforce auth for /api/ paths
        if not request.path.startswith("/api/"):
            return self.get_response(request)

        # Skip auth for explicit public paths
        if request.path in self.PUBLIC_PATHS:
            return self.get_response(request)

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JsonResponse(
                {"error": "Authentication required. Provide Authorization: Bearer <token>"},
                status=401,
            )

        token = auth_header.split(" ", 1)[1]

        try:
            # 1. Determine signing key
            try:
                header = jwt.get_unverified_header(token)
                alg = header.get("alg")
            except Exception:
                return JsonResponse({"error": "Invalid token header format"}, status=401)

            # 2. Decode using either JWKS (Asymmetric) or Secret (Symmetric)
            if alg == "ES256" and self.jwks_client:
                signing_key = self.jwks_client.get_signing_key_from_jwt(token)
                key = signing_key.key
                allowed_algs = ["ES256"]
            else:
                key = settings.SUPABASE_JWT_SECRET
                allowed_algs = ["HS256", "HS384", "HS512"]
                if key == "your-supabase-jwt-secret":
                     return JsonResponse({"error": "Backend misconfiguration: SUPABASE_JWT_SECRET is still the placeholder."}, status=500)

            payload = jwt.decode(
                token,
                key,
                algorithms=allowed_algs,
                audience="authenticated",
            )
            request.user_id = payload.get("sub")
            request.user_email = payload.get("email")

        except jwt.ExpiredSignatureError:
            return JsonResponse({"error": "Token has expired."}, status=401)
        except Exception as exc:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"JWT Validation failed: {exc}. alg={alg}")
            return JsonResponse({"error": f"Authentication failed: {exc}"}, status=401)

        return self.get_response(request)
