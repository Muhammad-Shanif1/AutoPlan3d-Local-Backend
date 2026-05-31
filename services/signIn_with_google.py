import httpx
from fastapi import HTTPException, status
from schema.user import ContinueWithGoogleSchema
import services.controller as controller
from services.settings import settings

GOOGLE_CLIENT_ID = getattr(settings, "GOOGLE_CLIENT_ID", None)

async def login_with_google(body: ContinueWithGoogleSchema, db):
    """Verify Google ID token using Google's tokeninfo endpoint and return or create local user.

    Expects `body.id_token` to be provided by the client (recommended flow).
    """
    if not body.id_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="id_token is required"
        )

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                "https://oauth2.googleapis.com/tokeninfo",
                params={"id_token": body.id_token},
                timeout=10.0,
            )
        # Catch network/timeout issues safely instead of crashing with 500
        except httpx.RequestError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication server temporarily unreachable"
            )

    if resp.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid Google ID token"
        )

    data = resp.json()

    # CRITICAL SECURITY FIX: Google tokens can contain 'aud' or 'azp'. Check both.
    aud = data.get("aud")
    azp = data.get("azp")
    if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_ID not in [aud, azp]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid token audience"
        )

    email = data.get("email")
    # Normalize string booleans safely
    email_verified = str(data.get("email_verified", "")).lower() in ("true", "1")
    
    if not email or not email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email not available or not verified by Google"
        )

    name = data.get("name") or body.name
    google_id = data.get("sub")

    payload = ContinueWithGoogleSchema(
        id_token=None,
        email=email,
        name=name,
        google_id=google_id,
    )

    return controller.continue_with_google(payload, db)
