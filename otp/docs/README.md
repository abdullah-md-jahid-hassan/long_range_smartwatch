# OTP Module

## Table of Contents

1. [Overview](#1-overview)
2. [How It Works](#2-how-it-works)
3. [API Endpoints](#3-api-endpoints)
4. [OTP Purposes](#4-otp-purposes)
5. [OTP Policies](#5-otp-policies)
6. [OTPService Reference](#6-otpservice-reference)
7. [Configuration](#7-configuration)
8. [Security Design](#8-security-design)
9. [Integration Guide](#9-integration-guide)

---

## 1. Overview

The `otp` app provides a complete one-time password (OTP) system for any scenario that requires secondary verification. It is used across the application for registration email verification, password reset flows, and other sensitive operations.

Key characteristics:

- **Redis-backed** — OTPs are stored in Redis with automatic TTL-based expiry. No database table is required.
- **Purpose-driven** — Each OTP is tied to a specific purpose (e.g., `REGISTRATION`, `PASSWORD_RESET`), ensuring that an OTP issued for one flow cannot be used in another.
- **Hashed storage** — OTP values are hashed with SHA-256 before storage; raw values are never persisted.
- **Constant-time comparison** — Verification uses HMAC comparison to prevent timing attacks.
- **Per-purpose policies** — Authentication requirements, user existence checks, and delivery channels are configurable per purpose.

### File Structure

```
otp/
├── migrations/
├── docs/
│   └── README.md           # This file
├── apps.py
├── choices.py              # Enums for purpose and channel
├── policies.py             # Per-purpose OTP rules
├── serializers.py          # OtpVerifySerializer
├── services.py             # OTPService class
├── throttles.py            # GetOtpRateThrottle
├── urls.py
└── views.py                # GetOtpView
```

---

## 2. How It Works

### Generation Flow

```
Client → POST /otp/get-otp/  →  OTPService.generate()
                                    │
                                    ├─ Validate purpose policy
                                    ├─ Check user existence (if required by policy)
                                    ├─ Enforce max active OTP limit
                                    ├─ Generate N-digit random OTP
                                    ├─ Hash the OTP (SHA-256)
                                    ├─ Store hash in Redis with TTL
                                    └─ Send via configured channel (email)
```

### Verification Flow

```
Client sends OTP in another endpoint (e.g., /auth/register/)
                                    │
                            OtpVerifySerializer
                                    │
                            OTPService.verify()
                                    │
                                    ├─ Look up stored hashes for (identifier, purpose)
                                    ├─ Hash the provided OTP
                                    ├─ HMAC compare against stored hashes
                                    ├─ If match → delete from Redis (one-time use)
                                    └─ Return True / raise ValidationError
```

---

## 3. API Endpoints

Base path: `/otp/`

---

### POST `/otp/get-otp/`

Request an OTP for a given purpose and delivery channel.

**Authentication:** Conditional — depends on the policy of the requested `purpose` (see [OTP Policies](#5-otp-policies)).

**Request Body:**

```json
{
  "email": "user@example.com",
  "purpose": "REGISTRATION",
  "channel": "EMAIL"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `email` | string | Yes | The recipient's email address |
| `purpose` | string | Yes | The reason for the OTP (see [OTP Purposes](#4-otp-purposes)) |
| `channel` | string | No | Delivery channel. Defaults to `EMAIL`. |

**Success Response — `200 OK`:**

```json
{
  "success": true,
  "message": "OTP sent successfully",
  "data": null
}
```

**Error Responses:**

| Status | Scenario |
|---|---|
| `400 Bad Request` | Invalid purpose, user does not exist (when required), or max OTP limit reached |
| `401 Unauthorized` | Authentication required for this purpose but token not provided |
| `429 Too Many Requests` | Daily OTP throttle limit exceeded |

---

## 4. OTP Purposes

Defined in `otp/choices.py` as `OtpPurpose`.

| Value | Description |
|---|---|
| `REGISTRATION` | Verify email address during new account registration |
| `LOGIN` | Two-factor login verification |
| `PASSWORD_CHANGE` | Verify identity before changing a known password |
| `PASSWORD_RESET` | Recover access when the password is forgotten |
| `VERIFICATION` | General-purpose identity verification |
| `CHANGE_EMAIL` | Verify ownership of a new email address |
| `CHANGE_PHONE` | Verify ownership of a new phone number |
| `CHANGE_USERNAME` | Confirm username change |
| `OTHER` | Custom or miscellaneous use cases |

### OTP Channels

Defined in `otp/choices.py` as `OtpChannel`.

| Value | Description |
|---|---|
| `EMAIL` | Deliver OTP via email (fully implemented) |
| `PHONE` | Deliver OTP via SMS (not yet implemented) |
| `ALL` | Deliver via all available channels |

---

## 5. OTP Policies

Each purpose has a policy defined in `otp/policies.py` via the `OTPPolicy` dataclass. Policies control the behavior of OTP generation for each use case.

### `OTPPolicy` Fields

| Field | Type | Description |
|---|---|---|
| `enabled` | `bool` | Whether this purpose is active |
| `requires_auth` | `bool` | Whether the requester must be authenticated |
| `user_must_exist` | `bool` | Whether the email must belong to an existing user |
| `default_channel` | `OtpChannel` | The default delivery channel |

### Default Policies

| Purpose | `requires_auth` | `user_must_exist` |
|---|---|---|
| `REGISTRATION` | No | No (user is being created) |
| `PASSWORD_RESET` | No | Yes |
| `PASSWORD_CHANGE` | Yes | Yes |
| `LOGIN` | No | Yes |
| `VERIFICATION` | No | Conditional |
| `CHANGE_EMAIL` | Yes | Yes |
| `CHANGE_PHONE` | Yes | Yes |
| `CHANGE_USERNAME` | Yes | Yes |

> Policies can be modified in `otp/policies.py` to match project-specific requirements without changing the underlying service logic.

---

## 6. OTPService Reference

**Module:** `otp.services.OTPService`

### Class Methods

#### `OTPService.generate(identifier, purpose, channel)`

Generates and dispatches an OTP.

| Parameter | Type | Description |
|---|---|---|
| `identifier` | `str` | Unique identifier (email address or phone number) |
| `purpose` | `OtpPurpose` | The use case for this OTP |
| `channel` | `OtpChannel` | Delivery channel |

**Raises:** `ValidationError` if the max active OTP limit is reached.

#### `OTPService.verify(identifier, purpose, otp_value)`

Verifies a submitted OTP.

| Parameter | Type | Description |
|---|---|---|
| `identifier` | `str` | The identifier the OTP was issued for |
| `purpose` | `OtpPurpose` | The purpose to verify against |
| `otp_value` | `str` | The raw OTP submitted by the user |

**Returns:** `True` on success.  
**Raises:** `ValidationError` if the OTP is invalid or expired.

**Side effect:** The verified OTP is deleted from Redis immediately (one-time use).

### Redis Key Structure

OTPs are stored under a namespaced key pattern:

```
otp:{purpose}:{identifier}:{index}
```

Multiple OTPs can exist concurrently for the same identifier/purpose pair (up to `MAX_ACTIVE_OTPS`). Each has an independent TTL.

---

## 7. Configuration

All OTP settings are loaded from environment variables.

| Environment Variable | Description | Default |
|---|---|---|
| `OTP_LENGTH` | Number of digits in the generated OTP | `6` |
| `OTP_EXPIRY_MINUTES` | Time-to-live for each OTP in minutes | `5` |
| `OTP_ALLOW_NUMBER` | If `True`, use numeric digits only | `True` |
| `MAX_ACTIVE_OTPS` | Maximum number of active OTPs per identifier per purpose | `5` |
| `GET_OTP_THROTTLE_RATE_PER_DAY` | Maximum OTP requests per day per client | `25` |

---

## 8. Security Design

### Hashed Storage

The raw OTP value is **never stored**. Before persisting to Redis, the OTP is hashed using SHA-256:

```
stored_value = SHA256(raw_otp)
```

If Redis is compromised, attackers cannot recover OTP values from the hashes.

### Constant-Time Comparison

Verification uses `hmac.compare_digest()` to compare the hash of the submitted OTP against the stored hash. This eliminates timing-based side-channel attacks that could be used to enumerate valid OTPs.

### One-Time Use

Upon successful verification, the matching Redis key is deleted immediately. The OTP cannot be reused even within its TTL window.

### Rate Limiting

The `GetOtpRateThrottle` applies a daily cap (default: 25 requests per day) on OTP generation requests, scoped per client IP or authenticated user. This prevents automated OTP flooding.

### Purpose Isolation

An OTP generated for `REGISTRATION` cannot be used to verify a `PASSWORD_RESET` flow. The purpose is embedded in the Redis key, and verification always checks the stored purpose.

---

## 9. Integration Guide

### Using OTP in a Custom Flow

**Step 1 — Request OTP:**

```
POST /otp/get-otp/
{
  "email": "user@example.com",
  "purpose": "PASSWORD_RESET"
}
```

**Step 2 — Accept OTP in your endpoint and verify:**

```python
from otp.serializers import OtpVerifySerializer

# In your serializer or view:
otp_serializer = OtpVerifySerializer(data={
    "email": request.data["email"],
    "otp":   request.data["otp"],
    "purpose": "PASSWORD_RESET",
})
otp_serializer.is_valid(raise_exception=True)
# Verification passed — proceed with the business logic
```

### Adding a New Purpose

1. Add the new value to `OtpPurpose` in `otp/choices.py`.
2. Add a corresponding policy entry in `get_otp_rules()` inside `otp/policies.py`.
3. (Optional) Add a dedicated email template or delivery handler in the `emails` app.
