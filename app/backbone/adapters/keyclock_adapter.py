# # اخرین کاری که در این فایل کردیم میخواستیم otp را هندل کنیم که نشد


# from dataclasses import asdict, dataclass
# from datetime import datetime, timedelta, timezone
# import secrets
# from uuid import UUID
# from typing import Dict, Any, Optional
# from keycloak import KeycloakAdmin  # type: ignore
# from keycloak import KeycloakOpenID
# from keycloak.exceptions import KeycloakPostError  # type: ignore
# from typing import List
# from pydantic import BaseModel

# from backbone.devlog import devlog


# class Credential(BaseModel):
# type: str = "password"
#     value: Optional[str] = None
#     temporary: bool = False

#     id: Optional[str] = None
#     createdDate: Optional[int] = None
#     userLabel: Optional[str] = None
#     secretData: Optional[Dict[str, Any]] = None
#     credentialData: Optional[Dict[str, Any]] = None

#     expire_at: Optional[datetime] = None  # همیشه datetime باشه

#     def to_payload(self) -> Dict[str, Any]:
#         payload: Dict[str, Any] = {
#             "type": self.type,
#             "temporary": self.temporary,
#         }
#         if self.value is not None:
#             payload["value"] = self.value
#         if self.userLabel:
#             payload["userLabel"] = self.userLabel
#         if self.credentialData:
#             payload["credentialData"] = self.credentialData

#         # expire_at → string
#         if self.expire_at:
#             payload.setdefault("credentialData", {})
#             payload["credentialData"]["expire_at"] = self.expire_at.isoformat()

#         return payload

#     @classmethod
#     def otp(cls, otp: str, expire_seconds: int = 120) -> "Credential":
#         expire_at = datetime.now(timezone.utc) + timedelta(seconds=expire_seconds)
#         return cls(
#             value=otp, userLabel=f"OTP valid {expire_seconds}s", expire_at=expire_at
#         )


# class UserKeycloak(BaseModel):
#     id: Optional[str] = None
#     username: str
#     enabled: bool = True

#     email: Optional[str] = None
#     firstName: Optional[str] = None
#     lastName: Optional[str] = None

#     credentials: Optional[List[Credential]] = None
#     requiredActions: Optional[List[str]] = None

#     attributes: Optional[Dict[str, Any]] = None

#     phone_number: Optional[str] = None
#     national_id: Optional[str] = None
#     roles: Optional[List[str]] = None4l.,t      kk1
#     groups: Optional[List[str]] = None

#     def to_payload(self) -> Dict[str, Any]:
#         payload: Dict[str, Any] = self.model_dump(
#             by_alias=True,  # استفاده از camelCase
#             exclude={"id", "phone_number", "national_id", "roles", "groups"},
#             exclude_none=True,
#         )

#         if self.credentials:
#             payload["credentials"] = [c.to_payload() for c in self.credentials]

#         attrs = self.attributes.copy() if self.attributes else {}
#         if self.phone_number:
#             attrs["phone_number"] = self.phone_number
#         if self.national_id:
#             attrs["national_id"] = self.national_id
#         if attrs:
#             payload["attributes"] = attrs

#         return payload


# @dataclass
# class Token:
#     access_token: str
#     refresh_token: str
#     token_type: str
#     expires_in: int
#     refresh_expires_in: int

#     def to_dict(self) -> dict:
#         """Return token fields as a dict."""
#         return asdict(self)


# class KeycloakClient:
#     """
#     Adapter / client for Keycloak.
#     Use this class anywhere in your application to interact with Keycloak admin and OpenID endpoints.
#     """

#     def __init__(
#         self,
#         realm_name: str = "master",
#         server_url: str = "http://localhost:8080/",
#         client_id: str = "admin-cli",
#         client_secret_key: str | None = None,
#         admin_user: str = "admin",
#         admin_password: str = "admin",
#     ) -> None:
#         """
#         Initialize Keycloak admin and OpenID clients.
#         Use this when you need to perform admin tasks (users/roles/groups) or obtain/validate tokens.
#         """
#         # OpenID client: used for token operations (login, refresh, introspect)
#         self.openid = KeycloakOpenID(
#             server_url=server_url,
#             client_id=client_id,
#             realm_name=realm_name,
#             client_secret_key=client_secret_key,
#         )

#         # Admin client: used for realm admin actions (create/update/delete users, roles, groups, sessions)
#         self.admin = KeycloakAdmin(
#             server_url=server_url,
#             realm_name=realm_name,
#             client_id=client_id,
#             client_secret_key=client_secret_key,
#             username=admin_user,
#             password=admin_password,
#         )

#     # ----------------------
#     # Utility
#     # ----------------------
#     async def get_client_id(self, token: str) -> Optional[str]:
#         """
#         Asynchronously return the client_id associated with an introspected token.
#         Use this to determine which client issued or is using a token.
#         When to use:
#           - Use in async applications (FastAPI, aiohttp, etc.) to avoid blocking.
#         """
#         info = await self.openid.a_introspect(token=token)
#         return info.get("client_id") if info else None

#     # ----------------------
#     # User Management
#     # ----------------------
#     async def _find_user_by_attribute(self, key: str, value: str) -> Optional[dict]:
#         users = await self.admin.a_get_users(query={"q": value})
#         for u in users:
#             attrs = u.get("attributes", {})
#             if attrs and attrs.get(key, [None])[0] == value:
#                 return u
#         return None

#     def _generate_otp(self, expire_seconds: int = 120, length: int = 6) -> Credential:
#         """Generate a numeric OTP of given length."""
#         return Credential.otp(
#             "".join(str(secrets.randbelow(10)) for _ in range(length)),
#             expire_seconds,
#         )

#     async def get_user_by_phone(self, phone_number: str) -> Optional[Any]:
#         return await self._find_user_by_attribute("phone_number", phone_number)

#     async def get_user_by_email(self, email: str) -> Optional[Any]:
#         """
#         Unlike attributes, email is a top-level field in Keycloak.
#         """
#         users = await self.admin.a_get_users(query={"email": email})
#         if users:
#             return users[0]
#         return None

#     async def get_user_by_username(self, username: str) -> Optional[Any]:
#         """
#         Unlike attributes, username is a top-level field in Keycloak.
#         """
#         users = await self.admin.a_get_users(query={"username": username})
#         if users:
#             return users[0]
#         return None

#     async def get_user_id_by_phone(self, phone_number: str) -> Optional[UUID]:
#         u = await self.get_user_by_phone(phone_number)
#         if u:
#             return UUID(u["id"])
#         return None

#     async def get_user_id_by_email(self, email: str) -> Optional[UUID]:
#         u = await self.get_user_by_email(email)
#         if u:
#             return UUID(u["id"])
#         return None

#     async def get_user_id_by_username(self, username: str) -> Optional[UUID]:
#         u = await self.get_user_by_username(username)
#         if u:
#             return UUID(u["id"])
#         return None

#     async def get_user_by_id(self, user_id: UUID) -> Any:
#         """
#         Get user info by UUID.
#         Returns user dict if found, otherwise None.
#         """
#         try:
#             user = await self.admin.a_get_user(str(user_id), True)
#             return user
#         except Exception:
#             return None

#     async def create_or_get_user(self, user: UserKeycloak) -> UUID:
#         """
#         Create user if not exists, otherwise return existing one.
#         Matching priority:
#           1. phone_number attribute (unique)
#           2. username fallback (only if no phone_number check is possible)
#         """
#         id = (
#             await self.get_user_id_by_phone(user.phone_number)
#             if user.phone_number
#             else None
#         )
#         if id:
#             return id
#         id = await self.get_user_id_by_email(user.email) if user.email else None
#         if id:
#             return id
#         id = await self.get_user_id_by_username(user.username)
#         if id:
#             return id

#         # --- If not found, try create user ---
#         try:
#             user_uuid = await self.admin.a_create_user(user.to_payload())

#             return UUID(user_uuid)
#         except KeycloakPostError as e:
#             error_msg = (
#                 getattr(e, "error_message", b"").decode()
#                 if getattr(e, "error_message", None)
#                 else ""
#             )
#             # username exists → just get its ID (do not trust phone_number mismatch)
#             if "User exists with same username" in error_msg:
#                 existing_id = await self.admin.a_get_user_id(username=user.username)
#                 return UUID(existing_id)
#             raise

#     async def create_or_get_user_by_phone(self, phone_number: str) -> UUID:
#         """
#         Register a new user with only phone number.
#         Safe against duplicate usernames: we always trust phone_number attribute first.
#         """
#         # --- Not found → create user ---
#         user = UserKeycloak(
#             username=phone_number,
#             attributes={"phone_number": phone_number},
#             enabled=True,
#         )
#         return await self.create_or_get_user(user)

#     async def update_user(self, user: UserKeycloak, merge: bool = True) -> UUID:
#         """
#         Asynchronously update an existing user.

#         Args:
#             user: UserKeycloak model with data to update.
#             merge:
#                 - True  → only update non-null fields (safe update).
#                 - False → overwrite all fields (even nulls will clear existing values).
#         Returns:
#             UUID of the updated user
#         """
#         if not user.id:
#             raise ValueError("User id is required for update")

#         payload = user.to_payload()

#         # اگر merge فعال باشه، فیلدهای None رو حذف می‌کنیم
#         if merge:
#             payload = {k: v for k, v in payload.items() if v is not None}

#         await self.admin.a_update_user(user_id=user.id, payload=payload)
#         return UUID(user.id)

#     async def delete_user(self, user_uuid: UUID) -> None:
#         """
#         Asynchronously delete a user from Keycloak.
#         """
#         await self.admin.a_delete_user(user_id=str(user_uuid))

#     async def set_password(self, user_uuid: UUID, credential: Credential) -> None:
#         """
#         Add a new credential (password/OTP/etc.) for the given user.
#         This does not remove previous credentials, only appends.
#         """
#         # --- دریافت کاربر ---
#         user = await self.get_user_by_id(user_uuid)

#         # --- گرفتن credentials فعلی ---
#         existing_credentials = user.get("credentials", [])

#         # --- اضافه کردن credential جدید ---
#         new_credentials = existing_credentials + [credential.to_payload()]

#         # --- بروزرسانی کاربر با credentials جدید ---
#         await self.admin.a_update_user(
#             user_id=str(user_uuid),
#             payload={"credentials": new_credentials},
#         )

#     async def generate_otp_for_user(
#         self, phone_number: str, length: int = 6
#     ) -> Credential:
#         """
#         Generate and store a one-time password (OTP) for a user identified by phone number.
#         When to use:
#           - Use this for passwordless login or 2FA via SMS.
#         """
#         otp = self._generate_otp(length)
#         id = await self.get_user_id_by_phone(phone_number)
#         if not id:
#             raise ValueError("User not found")
#         await self.set_password(
#             id,
#             otp,
#         )
#         return otp

#     async def generate_token_with_otp(self, phone_number: str, otp: str) -> dict:
#         """
#         Generate access/refresh token with username & password.
#         If the password credential has expire_at → enforce it.
#         After successful login, expired/temporary password is deleted.
#         """
#         # --- پیدا کردن کاربر بر اساس username ---
#         user = await self.get_user_by_phone(phone_number)
#         if not user:
#             raise ValueError("User not found")

#         return await self._generate_token(user, otp)

#     async def generate_token(self, username: str, password: str) -> dict:
#         user = await self.get_user_by_username(username)
#         if not user:
#             raise ValueError("User not found")

#         return await self._generate_token(user, password)

#     async def _generate_token(self, user, password: str) -> dict:
#         """
#         Generate access/refresh token with username & password.
#         If the password credential has expire_at → enforce it.
#         After successful login, expired/temporary password is deleted.
#         """
#         user_id = user["id"]

#         credentials = user.get("credentials", [])
#         target_credential = None
#         for c in credentials:
#             if c.get("type") == "password" and c.get("value") == password:
#                 target_credential = c
#                 break

#         if not target_credential:
#             raise ValueError("Invalid username/password")

#         expire_at = (
#             target_credential.get("credentialData", {}).get("expire_at")
#             if target_credential.get("credentialData")
#             else None
#         )
#         if expire_at:
#             expire_dt = datetime.fromisoformat(expire_at)
#             if expire_dt < datetime.now(timezone.utc):
#                 raise ValueError("Password expired")

#         token = await self.openid.a_token(
#             username=user["username"], password=password, grant_type="password"
#         )

#         # --- اگر temporary یا expire داشت، credential رو حذف کن ---
#         if target_credential.get("temporary") or expire_at:
#             new_credentials = [c for c in credentials if c != target_credential]
#             await self.admin.a_update_user(
#                 user_id=user_id, payload={"credentials": new_credentials}
#             )

#         return token

#     async def generate_service_token(self) -> dict:
#         """
#         Generate token for a client (service account) using client credentials grant.
#         When to use:
#           - For machine-to-machine authentication.
#         """
#         token = await self.openid.a_token(grant_type="client_credentials")
#         return token

#     async def refresh_user_token(self, refresh_token: str) -> dict:
#         """
#         Refresh user's access token using refresh_token.
#         """
#         token = await self.openid.a_refresh_token(refresh_token=refresh_token)
#         return token

#     def introspect_token(self, token: str) -> Dict[str, Any]:
#         """
#         Introspect a token to retrieve its metadata (active, scope, username, etc).
#         When to use:
#           - Use this on backend services when you need token validity and metadata.
#         Returns:
#           - Introspection response dict or empty dict if token is inactive.
#         """
#         result = self.openid.introspect(token)
#         return result if result.get("active") else {}

#     def verify_token(
#         self, token: str, options: Optional[Dict[str, Any]] = None
#     ) -> Dict[str, Any]:
#         """
#         Decode and verify a JWT access token using realm public key.
#         When to use:
#           - Use this when you need to decode token claims locally (subject, roles, exp) and verify signature.
#         Parameters:
#           - options: pass verify options to decode_token (e.g., {'verify_aud': True}).
#         Returns:
#           - Decoded token claims as dict.
#         """
#         opts = options or {"verify_aud": True}
#         return self.openid.decode_token(
#             token, key=self.openid.public_key(), options=opts
#         )

#     async def test(self):
#         # 🟢 تصحیح: مقدار 'phone_number' باید یک لیست از رشته‌ها باشد
#         payload = {
#             "username": str(self._generate_otp().value),
#             "enabled": True,
#             "attributes": {
#                 "phone_number": [
#                     "09123456781",
#                 ]
#             },
#         }

#         # ساخت کاربر
#         user_id = await self.admin.a_create_user(payload, exist_ok=True)
#         await self.admin.a_update_user(
#             user_id,
#             {
#                 "attributes": {"phone_number": ["09123456781"]},
#             },
#         )
#         # نمایش کاربر بعد از ساخت (حالا باید attributes را در خروجی داشته باشد)
#         user = await self.admin.a_get_user(user_id, True)


# if __name__ == "__main__":
#     import asyncio

#     async def main():

#         kc = KeycloakClient()
#         await kc.test()
#         # --- کاربر رو بساز (بر اساس شماره موبایل)
#         # phone_number = "0912345678133"
#         # user_id = await kc.create_or_get_user_by_phone(phone_number)
#         # devlog("user_id")
#         # devlog(user_id)
#         # user = await kc.get_user_by_id(user_id)
#         # devlog("user")
#         # devlog(user)  # {'phone_number': '09123456781'}

#         # --- OTP تولید کن
#         # otp_cred = await kc.generate_otp_for_user(phone_number, length=6)
#         # devlog(otp_cred.value)

#         # # --- تست ورود با OTP
#         # try:
#         #     token = await kc.generate_token_with_otp(phone_number, otp_cred.value)
#         #     print("Access Token:", token["access_token"][:50], "...")
#         # except Exception as e:
#         #     print("Login failed:", e)

#     asyncio.run(main())

#     # def get_client_token(self) -> str:
#     #     """
#     #     Obtain a client credentials token (access token).
#     #     When to use:
#     #       - Use this when server-to-server calls to Keycloak admin endpoints require a bearer token.
#     #     Returns:
#     #       - access_token string.
#     #     """
#     #     return self.openid.token(grant_type="client_credentials")["access_token"]

#     # # ----------------------
#     # # User Credentials management
#     # # ----------------------
#     # def remove_user_credential(self, user_id: UUID | str) -> None:
#     #     """
#     #     Remove user's stored credential(s).
#     #     When to use:
#     #       - Use this to force removal of existing credentials before setting a new password or removing password login.
#     #     """
#     #     creds = self.admin.get_credentials(user_id=str(user_id))
#     #     if creds:
#     #         # remove first credential (commonly the password credential)
#     #         self.admin.delete_credential(
#     #             user_id=str(user_id), credential_id=creds[0].get("id")
#     #         )

#     # def change_user_password(
#     #     self, user_id: UUID, password: str, temporary: bool = False
#     # ):
#     #     """
#     #     Change user's password.
#     #     When to use:
#     #       - Use this for admin-initiated password reset or when user changes password via profile.
#     #     Notes:
#     #       - temporary flag indicates if user must change password on next login.
#     #     """
#     #     self.remove_user_credential(user_id)
#     #     return self.admin.set_user_password(str(user_id), password, temporary=temporary)

#     # # ----------------------
#     # # Sessions
#     # # ----------------------
#     # def get_user_sessions(self, user_id: UUID):
#     #     """
#     #     Retrieve active sessions for a user.
#     #     When to use:
#     #       - Use this for auditing or to show active sessions in a user admin UI.
#     #     """
#     #     return self.admin.get_sessions(str(user_id))

#     # def remove_session(
#     #     self, session_id: UUID, admin_token: Optional[str] = None
#     # ) -> bool:
#     #     """
#     #     Remove a specific session by id (force logout that session).
#     #     When to use:
#     #       - Use this to terminate a single session (e.g., remote logout of a device).
#     #     Parameters:
#     #       - admin_token: optional bearer token to use; if not provided, a client token is obtained.
#     #     Returns:
#     #       - True on success, False on failure.
#     #     """
#     #     try:
#     #         token = admin_token or self.get_client_token()
#     #         url = f"{configs.KEYCLOAK_SERVER_URL}admin/realms/{configs.KEYCLOAK_REAL_NAME}/sessions/{session_id}"
#     #         headers = {"Authorization": f"Bearer {token}"}
#     #         resp = requests.delete(url, headers=headers)
#     #         resp.raise_for_status()
#     #         return True
#     #     except Exception:
#     #         return False

#     # def logout_user(self, user_id: UUID):
#     #     """
#     #     Invalidate all sessions of a user (global logout).
#     #     When to use:
#     #       - Use this to force logout a user from all devices (e.g., account disable).
#     #     """
#     #     self.admin.logout(str(user_id))

#     # # ----------------------
#     # # Roles
#     # # ----------------------
#     # def get_all_roles(self):
#     #     """
#     #     Retrieve all realm roles.
#     #     When to use:
#     #       - Use this to display available roles in admin UI or for syncing roles to a local DB.
#     #     """
#     #     return self.admin.get_realm_roles()

#     # def assign_role(self, user_id: UUID, role_name: str):
#     #     """
#     #     Assign a realm role to a user.
#     #     When to use:
#     #       - Use this when granting permissions or access levels to a user.
#     #     """
#     #     role = self.admin.get_realm_role(role_name)
#     #     self.admin.assign_realm_roles(user_id=str(user_id), roles=[role])

#     # def remove_role(self, user_id: UUID, role_name: str):
#     #     """
#     #     Remove a realm role from a user.
#     #     When to use:
#     #       - Use this when revoking a previously granted role/permission.
#     #     """
#     #     role = self.admin.get_realm_role(role_name)
#     #     self.admin.delete_realm_roles_of_user(str(user_id), [role])

#     # # ----------------------
#     # # Groups
#     # # ----------------------
#     # def create_group(self, group_name: str) -> str:
#     #     """
#     #     Create a group in the realm.
#     #     When to use:
#     #       - Use this to organize users into groups (e.g., team, organization unit).
#     #     Returns:
#     #       - group id or representation returned by Keycloak.
#     #     """
#     #     return self.admin.create_group({"name": group_name})

#     # def get_groups(self):
#     #     """
#     #     Get all groups in the realm.
#     #     When to use:
#     #       - Use this to sync groups to a local DB or show group list in admin UI.
#     #     """
#     #     return self.admin.get_groups()

#     # def add_user_to_group(self, user_id: UUID, group_id: str):
#     #     """
#     #     Add a user to a group.
#     #     When to use:
#     #       - Use this to grant group-based permissions or for organizational mapping.
#     #     """
#     #     self.admin.group_user_add(user_id=str(user_id), group_id=group_id)

#     # def remove_user_from_group(self, user_id: UUID, group_id: str):
#     #     """
#     #     Remove a user from a group.
#     #     When to use:
#     #       - Use this to revoke group membership.
#     #     """
#     #     self.admin.group_user_remove(user_id=str(user_id), group_id=group_id)

#     # # ----------------------
#     # # OTP / TOTP
#     # # ----------------------
#     # def get_user_otp_config(self, user_id: UUID):
#     #     """
#     #     Check OTP (TOTP) configuration for a user.
#     #     When to use:
#     #       - Use this to determine whether user has configured TOTP (for prompting setup or enforcing MFA).
#     #     """
#     #     return self.admin.get_totp(str(user_id))

#     # def reset_user_otp(self, user_id: UUID):
#     #     """
#     #     Remove / reset OTP configuration for a user (force re-setup).
#     #     When to use:
#     #       - Use this when suspecting compromise or when admin forces reconfiguration of 2FA.
#     #     """
#     #     return self.admin.delete_totp(str(user_id))
