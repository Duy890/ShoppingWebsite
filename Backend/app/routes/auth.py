"""Auth routes: register, login, refresh, logout, MFA, password, email change, login history."""

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models, repositories, schemas
from ..services import auth_service, session_service
from ..core.admin_security import check_account_locked, record_failed_login, reset_failed_login_count
from ..core.config import get_settings
from ..core.database import get_db
from ..core.rate_limit import limiter
from ..core.security import (
    create_access_token,
    decode_refresh_token,
    generate_totp_secret,
    hash_token,
    hash_password,
    verify_password,
)
from ..deps import get_current_user, require_admin

router = APIRouter(tags=["auth"])


@router.post("/auth/register", response_model=schemas.TokenWithUser)
@limiter.limit("3/minute")
def register_user(payload: schemas.UserCreate, request: Request, db: Session = Depends(get_db)):
    try:
        user = auth_service.register_user(db, payload.email, payload.password, payload.full_name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    access_token = create_access_token(user.id)
    refresh_raw, _ = session_service.create_refresh_token_for_user(
        db, user.id,
        device_info=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_raw,
        "token_type": "bearer",
        "user": user,
    }


@router.post("/auth/login", response_model=schemas.LoginResponse)
@limiter.limit("5/minute")
def login(payload: schemas.UserCreate, request: Request, db: Session = Depends(get_db)):
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    try:
        user = auth_service.authenticate_user(db, payload.email, payload.password)
    except ValueError as exc:
        user_by_email = db.query(models.User).filter(
            func.lower(models.User.email) == payload.email.strip().lower()
        ).first()
        if user_by_email:
            record_failed_login(db, user_by_email, ip_address)
            auth_service.record_login_attempt(
                db, user_by_email.id, False, ip_address, user_agent, "Invalid password"
            )
        raise HTTPException(status_code=401, detail=str(exc))

    check_account_locked(user)
    reset_failed_login_count(db, user)
    auth_service.record_login_attempt(db, user.id, True, ip_address, user_agent)

    if user.mfa_enabled:
        challenge_token = auth_service.create_mfa_challenge(db, user)
        return {
            "access_token": "",
            "refresh_token": "",
            "token_type": "bearer",
            "user": user,
            "mfa_required": True,
            "mfa_challenge_token": challenge_token,
        }

    access_token = create_access_token(user.id)
    refresh_raw, _ = session_service.create_refresh_token_for_user(
        db, user.id, device_info=user_agent, ip_address=ip_address,
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_raw,
        "token_type": "bearer",
        "user": user,
        "mfa_required": False,
        "mfa_challenge_token": "",
    }


@router.post("/auth/refresh", response_model=schemas.Token)
def refresh_access_token(payload: schemas.RefreshTokenRequest, request: Request, db: Session = Depends(get_db)):
    token_hash = hash_token(payload.refresh_token)
    stored = repositories.get_refresh_token_by_hash(db, token_hash)
    if not stored:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    user = auth_service.get_user(db, stored.user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    repositories.revoke_refresh_token(db, stored.id)

    new_access = create_access_token(user.id)
    new_refresh_raw, _ = session_service.create_refresh_token_for_user(
        db, user.id,
        device_info=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )

    return {
        "access_token": new_access,
        "refresh_token": new_refresh_raw,
        "token_type": "bearer",
    }


@router.post("/auth/logout")
def logout(payload: schemas.RefreshTokenRequest, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    token_hash = hash_token(payload.refresh_token)
    stored = repositories.get_refresh_token_by_hash(db, token_hash)
    if stored and stored.user_id == current_user.id:
        repositories.revoke_refresh_token(db, stored.id)
    return {"ok": True}


@router.post("/auth/logout-all")
def logout_all_sessions(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    repositories.revoke_all_user_refresh_tokens(db, current_user.id)
    return {"ok": True}


@router.get("/auth/me", response_model=schemas.UserResponse)
def read_current_user(current_user: models.User = Depends(get_current_user)):
    return current_user


# ── MFA ──


@router.post("/auth/mfa/challenge/verify", response_model=schemas.TokenWithUser)
@limiter.limit("5/minute")
def mfa_challenge_verify(payload: schemas.MFAChallengeVerifyRequest, request: Request, db: Session = Depends(get_db)):
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    try:
        user, access_token, refresh_token = auth_service.verify_mfa_challenge_and_login(
            db, payload.challenge_token, payload.code,
            device_info=user_agent, ip_address=ip_address,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": user,
    }


@router.get("/auth/mfa/status", response_model=schemas.MFAStatusResponse)
def mfa_status(current_user: models.User = Depends(get_current_user)):
    return {"mfa_enabled": current_user.mfa_enabled or False}


@router.post("/auth/mfa/setup", response_model=schemas.MFASetupResponse)
def mfa_setup(payload: schemas.MFAEnableRequest, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.mfa_enabled:
        raise HTTPException(status_code=400, detail="MFA already enabled")
    if not verify_password(payload.password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid password")

    secret = generate_totp_secret()
    current_user.mfa_secret = secret
    db.commit()

    issuer = get_settings().SITE_NAME or "Electronics Store"
    qr_url = f"otpauth://totp/{issuer}:{current_user.email}?secret={secret}&issuer={issuer}"
    return {"secret": secret, "qr_code_url": qr_url}


@router.post("/auth/mfa/verify")
def mfa_verify(payload: schemas.MFAVerifyRequest, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        import pyotp
    except ImportError:
        raise HTTPException(status_code=501, detail="MFA not available (pyotp not installed)")
    if not current_user.mfa_secret:
        raise HTTPException(status_code=400, detail="MFA not set up")

    totp = pyotp.TOTP(current_user.mfa_secret)
    if not totp.verify(payload.code):
        raise HTTPException(status_code=400, detail="Invalid verification code")

    current_user.mfa_enabled = True
    db.commit()
    return {"ok": True, "message": "MFA enabled successfully"}


@router.post("/auth/mfa/disable")
def mfa_disable(payload: schemas.MFADisableRequest, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user.mfa_enabled:
        raise HTTPException(status_code=400, detail="MFA not enabled")
    if not verify_password(payload.password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid password")

    try:
        import pyotp
    except ImportError:
        raise HTTPException(status_code=501, detail="MFA not available (pyotp not installed)")
    totp = pyotp.TOTP(current_user.mfa_secret)
    if not totp.verify(payload.code):
        raise HTTPException(status_code=400, detail="Invalid verification code")

    current_user.mfa_secret = None
    current_user.mfa_enabled = False
    db.commit()
    return {"ok": True, "message": "MFA disabled successfully"}


# ── Login History ──


@router.get("/auth/login-history", response_model=list[schemas.LoginHistoryRead])
def login_history(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return auth_service.get_login_history_for_user(db, current_user.id, limit=20)


# ── Password ──


@router.post("/auth/forgot-password")
@limiter.limit("3/minute")
async def forgot_password(payload: schemas.ForgotPasswordRequest, request: Request, db: Session = Depends(get_db)):
    try:
        await auth_service.create_reset_token_and_send_email(db, payload.email)
    except ValueError:
        pass
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email sending failed: {str(e)}")
    return {"message": "If this email is registered, a reset link has been sent."}


@router.post("/auth/reset-password")
def reset_password(payload: schemas.ResetPasswordRequest, db: Session = Depends(get_db)):
    try:
        auth_service.reset_password(db, payload.token, payload.new_password)
        return {"message": "Password reset successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ── Email Change ──


@router.post("/auth/request-email-change")
async def request_email_change(
    payload: schemas.EmailChangeRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        await auth_service.create_email_change_token_and_send(db, current_user, payload.new_email)
        return {"message": "Verification email sent to the new address."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email sending failed: {str(e)}")


@router.get("/auth/verify-email-change")
def verify_email_change(token: str, db: Session = Depends(get_db)):
    try:
        auth_service.confirm_email_change(db, token)
        return RedirectResponse(url=f"{get_settings().FRONTEND_URL}/profile?email_changed=1")
    except ValueError:
        return RedirectResponse(url=f"{get_settings().FRONTEND_URL}/profile?email_error=1")


@router.post("/auth/change-password")
def change_password(
    payload: schemas.ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    current_user.hashed_password = hash_password(payload.new_password)
    db.commit()
    return {"message": "Password changed successfully"}
