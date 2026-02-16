# API Standards

## Overview

This document defines API design standards for the Airis project (Open WebUI fork). All API endpoints must follow these conventions for consistency, maintainability, and developer experience.

---

## Naming Conventions

### Endpoints

- Use lowercase with underscores for multi-word resources
- Resource-based URLs, not action-based
- Plural nouns for collections: `/api/v1/billing/plans`, `/api/v1/billing/transactions`
- Singular for specific resources: `/api/v1/billing/subscription`

### Examples

```
Good:
  GET  /api/v1/billing/plans                  - List all plans
  GET  /api/v1/billing/plans/{plan_id}        - Get specific plan
  POST /api/v1/billing/payment                - Create payment
  GET  /api/v1/billing/subscription           - Get user's subscription

Bad:
  GET  /api/v1/billing/getPlan                - Action-based (avoid)
  GET  /api/v1/billing/plan-list              - Inconsistent casing
  POST /api/v1/billing/createNewPayment       - Too verbose
```

---

## FastAPI Router Organization

### Router Structure

```python
from fastapi import APIRouter, Depends, HTTPException, status
from open_webui.utils.auth import get_verified_user, get_admin_user
from pydantic import BaseModel

# User-facing API
router = APIRouter(prefix="/api/v1/billing", tags=["billing"])

# Admin API
admin_router = APIRouter(prefix="/api/v1/admin/billing", tags=["admin", "billing"])

@router.get("/plans")
async def get_plans(user=Depends(get_verified_user)):
    """Get all active billing plans"""
    pass

@admin_router.post("/plans")
async def create_plan(
    request: CreatePlanRequest,
    user=Depends(get_admin_user)
):
    """Create a new billing plan (admin only)"""
    pass
```

### Router Grouping

```
/api/v1/billing/*          - User billing operations
/api/v1/admin/billing/*    - Admin billing management
/api/auths/*            - Authentication
/api/users/*            - User management
/api/chats/*            - Chat operations
/api/models/*           - AI model configuration
```

---

## Request/Response Format

### Content Type

- All requests/responses use `application/json`
- File uploads use `multipart/form-data`

### Date Formats

- ISO 8601: `2025-12-11T10:30:00Z`
- All timestamps in UTC
- Python: `datetime.datetime.utcnow().isoformat() + 'Z'`
- TypeScript: `new Date().toISOString()`

### Currency

- Store amounts as `Decimal` or `float` (in smallest unit or standard unit)
- Currency code: ISO 4217 (`RUB`, `USD`, `EUR`)
- Example: `{"amount": 1000.00, "currency": "RUB"}`

---

## Pydantic Request/Response Models

### Request Models

```python
from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class CreatePlanRequest(BaseModel):
    """Request to create a billing plan"""
    name: str = Field(..., min_length=1, max_length=100, description="Plan name (EN)")
    name_ru: str = Field(..., min_length=1, max_length=100, description="Plan name (RU)")
    price: float = Field(..., gt=0, description="Price in RUB")
    currency: str = Field(default="RUB", regex="^(RUB|USD|EUR)$")
    interval: str = Field(..., regex="^(day|week|month|year)$")
    quotas: Dict[str, int] = Field(..., description="Quota limits")
    features: List[str] = Field(default_factory=list, description="Feature list")
    is_active: bool = Field(default=True)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Professional",
                "name_ru": "Профессиональный",
                "price": 990.0,
                "currency": "RUB",
                "interval": "month",
                "quotas": {
                    "tokens_input": 100000,
                    "tokens_output": 100000,
                    "requests": 1000
                },
                "features": ["gpt4", "claude", "api_access"]
            }
        }
```

### Response Models

```python
from datetime import datetime

class PlanResponse(BaseModel):
    """Billing plan response"""
    id: str
    name: str
    name_ru: str
    price: float
    currency: str
    interval: str
    quotas: Dict[str, int]
    features: List[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # For ORM models
```

### Validation Example

```python
from pydantic import validator

class CreatePaymentRequest(BaseModel):
    plan_id: str
    return_url: str = Field(..., regex="^https?://")

    @validator('return_url')
    def validate_return_url(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('Return URL must be HTTP/HTTPS')
        return v
```

---

## HTTP Status Codes

### Success Codes

- `200 OK` - Successful GET, PUT, DELETE
- `201 Created` - Successful POST with resource creation
- `204 No Content` - Successful DELETE with no response body

### Client Error Codes

- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Not authenticated
- `403 Forbidden` - Authenticated but not authorized
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource conflict (e.g., duplicate)
- `422 Unprocessable Entity` - Validation error
- `429 Too Many Requests` - Rate limit exceeded

### Server Error Codes

- `500 Internal Server Error` - Unexpected server error
- `502 Bad Gateway` - External API failure (YooKassa, OpenAI)
- `503 Service Unavailable` - Service temporarily down

### Usage Examples

```python
from fastapi import HTTPException, status

# Not found
if not plan:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Plan not found"
    )

# Validation error
if price <= 0:
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="Price must be positive"
    )

# Quota exceeded
if usage >= quota:
    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail="Quota exceeded"
    )

# External API error
try:
    payment = await yookassa_client.create_payment(...)
except YooKassaError as e:
    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail="Payment gateway error"
    )
```

---

## Authentication & Authorization

### JWT Token Authentication

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Extract user from JWT token"""
    try:
        payload = jwt.decode(
            credentials.credentials,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        return Users.get_user_by_id(user_id)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### Authorization Dependencies

```python
from open_webui.utils.auth import get_verified_user, get_admin_user

# Requires authenticated user
@router.get("/subscription")
async def get_subscription(user=Depends(get_verified_user)):
    return Subscriptions.get_subscription_by_user_id(user.id)

# Requires admin role
@admin_router.post("/plans")
async def create_plan(
    request: CreatePlanRequest,
    admin_user=Depends(get_admin_user)
):
    # Only admins can create plans
    pass
```

---

## External API Integration Standards

### YooKassa Pattern

```python
import httpx
from loguru import logger

class YooKassaClient:
    """YooKassa payment gateway client"""

    def __init__(self, shop_id: str, secret_key: str):
        self.shop_id = shop_id
        self.secret_key = secret_key
        self.base_url = "https://api.yookassa.ru/v3"

    async def create_payment(
        self,
        amount: float,
        currency: str,
        return_url: str,
        description: str
    ) -> dict[str, object]:
        """Create payment in YooKassa"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/payments",
                    auth=(self.shop_id, self.secret_key),
                    json={
                        "amount": {"value": str(amount), "currency": currency},
                        "confirmation": {"type": "redirect", "return_url": return_url},
                        "description": description,
                        "capture": True
                    },
                    headers={"Idempotence-Key": str(uuid.uuid4())},
                    timeout=10.0
                )
                response.raise_for_status()
                return response.json()

            except httpx.HTTPStatusError as e:
                logger.error(f"YooKassa HTTP error: {e.response.status_code}")
                raise YooKassaError(f"Payment creation failed: {e}")
            except httpx.TimeoutException:
                logger.error("YooKassa timeout")
                raise YooKassaError("Payment gateway timeout")

    def verify_webhook_signature(
        self,
        body: bytes,
        signature: str
    ) -> bool:
        """Verify YooKassa webhook signature"""
        import hmac
        import hashlib

        computed = hmac.new(
            self.secret_key.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(computed, signature)
```

### OpenAI/Anthropic Pattern

```python
import openai
from anthropic import AsyncAnthropic

async def call_openai(prompt: str, model: str = "gpt-4") -> str:
    """Call OpenAI API with error handling"""
    try:
        response = await openai.ChatCompletion.acreate(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            timeout=30.0
        )
        return response.choices[0].message.content
    except openai.error.RateLimitError:
        raise HTTPException(status_code=429, detail="OpenAI rate limit")
    except openai.error.APIError as e:
        logger.error(f"OpenAI error: {e}")
        raise HTTPException(status_code=502, detail="AI service error")
```

---

## Rate Limiting

### Implementation with Redis

```python
from datetime import timedelta
import redis.asyncio as redis

async def check_rate_limit(user_id: str, limit: int = 100, window: int = 60):
    """Check if user exceeded rate limit"""
    key = f"rate_limit:{user_id}"
    async with redis.from_url(REDIS_URL) as r:
        count = await r.incr(key)
        if count == 1:
            await r.expire(key, window)
        if count > limit:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Try again in {window}s"
            )
```

### Quota Enforcement

```python
from open_webui.utils.billing import BillingService

async def check_and_enforce_quota(
    user_id: str,
    metric: str,
    amount: int = 1
):
    """Check quota before processing request"""
    billing_service = BillingService()

    # Check if user has quota
    has_quota = await billing_service.check_quota(user_id, metric, amount)

    if not has_quota:
        raise HTTPException(
            status_code=429,
            detail=f"Quota exceeded for {metric}"
        )

    # Deduct quota
    await billing_service.track_usage(user_id, metric, amount)
```

---

## Webhooks

### YooKassa Webhook Handler

```python
from fastapi import Request, HTTPException

@router.post("/webhook/yookassa")
async def yookassa_webhook(request: Request):
    """Handle YooKassa payment webhook"""
    # Verify signature
    body = await request.body()
    signature = request.headers.get("X-Webhook-Signature")

    if not yookassa_client.verify_webhook_signature(body, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Process webhook
    data = await request.json()
    payment_id = data["object"]["id"]
    status = data["object"]["status"]

    # Update subscription based on payment status
    if status == "succeeded":
        await activate_subscription(payment_id)
    elif status == "canceled":
        await cancel_subscription(payment_id)

    return {"status": "ok"}
```

---

## Logging Standards

### Structured Logging with Loguru

```python
from loguru import logger

# Configure logger
logger.add(
    "logs/billing_{time}.log",
    rotation="1 day",
    retention="30 days",
    level="INFO",
    format="{time} | {level} | {message} | {extra}"
)

# Log with context
logger.info(
    "Payment created",
    user_id=user.id,
    plan_id=plan_id,
    amount=amount,
    payment_id=payment_id
)

logger.error(
    "Payment failed",
    user_id=user.id,
    error=str(e),
    exc_info=True
)
```

### What NOT to Log

- API keys, secrets, passwords
- Full payment card numbers
- Personal data (unless necessary and anonymized)
- Full request/response bodies (may contain sensitive data)

---

## Pagination

### Standard Pagination Pattern

```python
from typing import Optional
from pydantic import BaseModel

class PaginatedResponse(BaseModel):
    """Paginated response wrapper"""
    items: list[object]
    total: int
    page: int
    page_size: int
    has_more: bool

@router.get("/transactions")
async def get_transactions(
    user=Depends(get_verified_user),
    page: int = 1,
    page_size: int = 20
):
    """Get user transactions with pagination"""
    offset = (page - 1) * page_size
    transactions = Transactions.get_by_user_id(
        user.id,
        limit=page_size,
        offset=offset
    )
    total = Transactions.count_by_user_id(user.id)

    return PaginatedResponse(
        items=transactions,
        total=total,
        page=page,
        page_size=page_size,
        has_more=(offset + page_size) < total
    )
```

---

## Versioning

### URL-Based Versioning (Not currently used, but reserved)

```python
# Future versioning strategy
router_v1 = APIRouter(prefix="/api/v1/billing")
router_v2 = APIRouter(prefix="/api/v2/billing")
```

---

## CORS Configuration

### FastAPI CORS Middleware

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # From env config
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Documentation

### OpenAPI/Swagger

- FastAPI automatically generates OpenAPI docs at `/docs`
- Ensure all endpoints have:
  - Clear descriptions
  - Request/response examples
  - Proper tags for grouping

### Example with Full Documentation

```python
@router.post(
    "/payment",
    response_model=CreatePaymentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create payment for subscription",
    description="Creates a new payment in YooKassa for subscribing to a plan",
    responses={
        201: {"description": "Payment created successfully"},
        404: {"description": "Plan not found"},
        502: {"description": "Payment gateway error"}
    }
)
async def create_payment(
    request: CreatePaymentRequest,
    user=Depends(get_verified_user)
):
    """
    Create a payment for subscription.

    This endpoint creates a payment in YooKassa and returns a confirmation URL
    where the user should be redirected to complete the payment.
    """
    pass
```

---

**Last Updated**: 2026-02-05
**Framework**: FastAPI 0.128.0
**API Version**: v1 (explicit via `/api/v1/*` routes)
