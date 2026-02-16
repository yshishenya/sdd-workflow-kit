# Error Handling Patterns

## Philosophy

- Fail fast and explicitly
- Always log errors with context
- User-facing errors should be actionable
- Never expose internal implementation details to users
- Use structured error responses
- Graceful degradation for non-critical features

---

## Error Categories

### 1. Client Errors (4xx)

**User input issues, authentication failures, authorization problems**

- 400 Bad Request - Malformed request
- 401 Unauthorized - Missing or invalid authentication
- 403 Forbidden - Insufficient permissions
- 404 Not Found - Resource doesn't exist
- 409 Conflict - Resource state conflict
- 422 Unprocessable Entity - Validation errors
- 429 Too Many Requests - Rate limit / quota exceeded

### 2. Server Errors (5xx)

**Internal failures, service unavailability**

- 500 Internal Server Error - Unexpected server error
- 502 Bad Gateway - External service failure
- 503 Service Unavailable - Temporary service downtime
- 504 Gateway Timeout - External service timeout

### 3. Business Logic Errors

**Application-specific rule violations**

- Quota exceeded
- Subscription inactive
- Invalid plan state
- Payment processing failures

### 4. External Integration Errors

**Third-party API failures**

- YooKassa payment gateway errors
- OpenAI/Anthropic API failures
- Database connection errors
- Redis cache errors

---

## FastAPI Exception Handling

### HTTPException Usage

```python
from fastapi import HTTPException, status

# Not found
if not plan:
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Plan not found"
    )

# Unauthorized
if not user:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
        headers={"WWW-Authenticate": "Bearer"}
    )

# Forbidden
if user.role != "admin":
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Admin access required"
    )

# Validation error
from pydantic import ValidationError
try:
    plan = CreatePlanRequest(**data)
except ValidationError as e:
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=e.errors()
    )

# Quota exceeded
if usage >= quota:
    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail={"error": "Quota exceeded", "metric": metric, "limit": quota}
    )
```

### Custom Exception Classes

```python
class AirisException(Exception):
    """Base exception for Airis application"""
    def __init__(self, message: str, code: str, details: dict = None):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)

class BillingError(AirisException):
    """Billing-related errors"""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message, "BILLING_ERROR", details)

class QuotaExceededError(BillingError):
    """User quota exceeded"""
    def __init__(self, metric: str, limit: int):
        super().__init__(
            f"Quota exceeded for {metric}",
            details={"metric": metric, "limit": limit}
        )

class YooKassaError(AirisException):
    """YooKassa API errors"""
    def __init__(self, message: str, original_error: Exception = None):
        super().__init__(
            message,
            "YOOKASSA_ERROR",
            {"original_error": str(original_error)} if original_error else {}
        )

class AIProviderError(AirisException):
    """AI provider API errors"""
    def __init__(self, provider: str, message: str, original_error: Exception = None):
        super().__init__(
            message,
            "AI_PROVIDER_ERROR",
            {"provider": provider, "original_error": str(original_error)}
        )
```

### Global Exception Handler

```python
from fastapi import Request, status
from fastapi.responses import JSONResponse
from loguru import logger

@app.exception_handler(AirisException)
async def airis_exception_handler(request: Request, exc: AirisException):
    """Handle custom Airis exceptions"""
    logger.error(
        f"Airis exception: {exc.code}",
        message=exc.message,
        details=exc.details,
        path=request.url.path,
        method=request.method
    )

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details
            }
        }
    )

@app.exception_handler(QuotaExceededError)
async def quota_exceeded_handler(request: Request, exc: QuotaExceededError):
    """Handle quota exceeded errors"""
    logger.warning(
        "Quota exceeded",
        metric=exc.details["metric"],
        limit=exc.details["limit"],
        user_id=getattr(request.state, "user_id", None)
    )

    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "error": {
                "code": "QUOTA_EXCEEDED",
                "message": exc.message,
                "details": exc.details
            }
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions"""
    logger.exception(
        "Unexpected exception",
        exc_info=exc,
        path=request.url.path,
        method=request.method
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred"
            }
        }
    )
```

---

## Error Handling Patterns

### Pattern 1: Try-Except with Specific Exceptions

```python
from loguru import logger

@router.post("/payment")
async def create_payment(
    request: CreatePaymentRequest,
    user=Depends(get_verified_user)
):
    """Create payment with comprehensive error handling"""
    try:
        # Validate plan exists
        plan = Plans.get_plan_by_id(request.plan_id)
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan not found"
            )

        # Check if user already has subscription
        existing_sub = Subscriptions.get_subscription_by_user_id(user.id)
        if existing_sub and existing_sub.status == "active":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already has active subscription"
            )

        # Create payment via YooKassa
        payment = await yookassa_client.create_payment(
            amount=plan.price,
            currency=plan.currency,
            return_url=request.return_url,
            description=f"Subscription: {plan.name}"
        )

        # Store transaction
        transaction = Transactions.create_transaction(
            user_id=user.id,
            plan_id=plan.id,
            amount=plan.price,
            currency=plan.currency,
            yookassa_payment_id=payment["id"],
            status="pending"
        )

        logger.info(
            "Payment created",
            user_id=user.id,
            plan_id=plan.id,
            payment_id=payment["id"]
        )

        return {
            "transaction_id": transaction.id,
            "confirmation_url": payment["confirmation"]["confirmation_url"],
            "status": "pending"
        }

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise

    except YooKassaError as e:
        logger.error(
            "YooKassa error",
            user_id=user.id,
            plan_id=request.plan_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Payment gateway error. Please try again later."
        )

    except Exception as e:
        logger.exception(
            "Unexpected error creating payment",
            user_id=user.id,
            plan_id=request.plan_id
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
```

### Pattern 2: Service Layer with Error Propagation

```python
# utils/billing.py
class BillingService:
    """Billing business logic with error handling"""

    async def create_subscription(
        self,
        user_id: str,
        plan_id: str
    ) -> dict:
        """Create subscription with error handling"""
        try:
            # Get plan
            plan = Plans.get_plan_by_id(plan_id)
            if not plan:
                raise BillingError(f"Plan {plan_id} not found")

            # Check for existing subscription
            existing = Subscriptions.get_subscription_by_user_id(user_id)
            if existing and existing.status == "active":
                raise BillingError(
                    "User already has active subscription",
                    details={"subscription_id": existing.id}
                )

            # Create subscription
            subscription = Subscriptions.create_subscription(
                user_id=user_id,
                plan_id=plan_id,
                status="active"
            )

            logger.info(
                "Subscription created",
                user_id=user_id,
                subscription_id=subscription.id
            )

            return subscription

        except BillingError:
            # Re-raise billing errors
            raise
        except Exception as e:
            logger.exception(
                "Error creating subscription",
                user_id=user_id,
                plan_id=plan_id
            )
            raise BillingError(
                "Failed to create subscription",
                details={"original_error": str(e)}
            )

# routers/billing.py
@router.post("/subscription")
async def create_subscription(
    request: CreateSubscriptionRequest,
    user=Depends(get_verified_user)
):
    """Create subscription endpoint"""
    try:
        billing_service = BillingService()
        subscription = await billing_service.create_subscription(
            user.id,
            request.plan_id
        )
        return subscription

    except BillingError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
```

### Pattern 3: Retry with Exponential Backoff

```python
import asyncio
from typing import TypeVar, Callable

T = TypeVar('T')

async def retry_with_backoff(
    func: Callable[[], T],
    max_attempts: int = 3,
    backoff_multiplier: float = 1.0,
    max_backoff: float = 10.0
) -> T:
    """Retry function with exponential backoff"""
    for attempt in range(max_attempts):
        try:
            return await func()
        except Exception as e:
            if attempt == max_attempts - 1:
                logger.error(f"Failed after {max_attempts} attempts: {e}")
                raise

            wait_time = min(backoff_multiplier * (2 ** attempt), max_backoff)
            logger.warning(
                f"Attempt {attempt + 1} failed, retrying in {wait_time}s",
                error=str(e)
            )
            await asyncio.sleep(wait_time)

# Usage
async def fetch_payment_status(payment_id: str):
    """Fetch payment status with retry"""
    return await retry_with_backoff(
        lambda: yookassa_client.get_payment(payment_id),
        max_attempts=3,
        backoff_multiplier=1.0
    )
```

### Pattern 4: Graceful Degradation

```python
@router.get("/me")
async def get_billing_info(user=Depends(get_verified_user)):
    """Get billing info with graceful degradation"""
    result = {
        "subscription": None,
        "usage": {},
        "transactions": [],
        "errors": []
    }

    # Try to get subscription (critical)
    try:
        result["subscription"] = Subscriptions.get_subscription_by_user_id(user.id)
    except Exception as e:
        logger.exception("Error fetching subscription", user_id=user.id)
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch subscription"
        )

    # Try to get usage (non-critical)
    try:
        result["usage"] = UsageTracking.get_current_period_usage(user.id)
    except Exception as e:
        logger.error("Error fetching usage", user_id=user.id, error=str(e))
        result["errors"].append("usage_unavailable")

    # Try to get transactions (non-critical)
    try:
        result["transactions"] = Transactions.get_by_user_id(user.id, limit=10)
    except Exception as e:
        logger.error("Error fetching transactions", user_id=user.id, error=str(e))
        result["errors"].append("transactions_unavailable")

    return result
```

---

## Logging Standards

### Structured Logging with Context

```python
from loguru import logger

# Configure logger
logger.add(
    "logs/app_{time}.log",
    rotation="1 day",
    retention="30 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message} | {extra}",
    serialize=True  # JSON format
)

# Log with context
logger.info(
    "Payment processed",
    user_id=user.id,
    plan_id=plan.id,
    amount=amount,
    payment_id=payment_id,
    status="success"
)

logger.error(
    "Payment failed",
    user_id=user.id,
    plan_id=plan.id,
    error=str(e),
    exc_info=True  # Include stack trace
)
```

### Log Levels Usage

- **DEBUG**: Detailed diagnostic information (SQL queries, API payloads)
- **INFO**: General operational messages (payment created, user logged in)
- **WARNING**: Unexpected but handled situations (quota approaching limit, slow query)
- **ERROR**: Errors affecting functionality (payment failed, API error)
- **CRITICAL**: Critical system failures (database down, all AI providers unavailable)

### What NOT to Log

- API keys, secrets, passwords
- Full payment card numbers (only last 4 digits)
- Personal data (unless necessary and anonymized)
- Full request/response bodies (may contain sensitive data)
- JWT tokens

```python
# Good
logger.info("API call to YooKassa", endpoint="/payments", method="POST")

# Bad - exposes secret
logger.info(f"YooKassa API key: {api_key}")  # NEVER!

# Good
logger.info("Card charged", last4=card_number[-4:])

# Bad - exposes full card number
logger.info(f"Card charged: {card_number}")  # NEVER!
```

---

## Error Recovery Strategies

### Circuit Breaker Pattern

```python
from datetime import datetime, timedelta

class CircuitBreaker:
    """Simple circuit breaker implementation"""

    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open

    async def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker"""
        if self.state == "open":
            if datetime.utcnow() - self.last_failure_time > timedelta(seconds=self.timeout):
                self.state = "half-open"
                logger.info("Circuit breaker: half-open state")
            else:
                raise Exception("Circuit breaker is open")

        try:
            result = await func(*args, **kwargs)
            if self.state == "half-open":
                self.state = "closed"
                self.failures = 0
                logger.info("Circuit breaker: closed state")
            return result

        except Exception as e:
            self.failures += 1
            self.last_failure_time = datetime.utcnow()

            if self.failures >= self.failure_threshold:
                self.state = "open"
                logger.warning(
                    f"Circuit breaker opened after {self.failures} failures"
                )

            raise

# Usage
yookassa_breaker = CircuitBreaker(failure_threshold=5, timeout=60)

async def create_payment_with_breaker(...):
    return await yookassa_breaker.call(
        yookassa_client.create_payment,
        amount=amount,
        currency=currency
    )
```

### Fallback Strategies

```python
async def get_ai_response(prompt: str, model: str = "gpt-4"):
    """Get AI response with fallback to alternative models"""
    try:
        # Try primary model
        return await openai.ChatCompletion.acreate(model=model, messages=[...])
    except openai.error.RateLimitError:
        logger.warning("OpenAI rate limit, trying Anthropic")
        try:
            # Fallback to Claude
            return await anthropic_client.messages.create(model="claude-3-sonnet", ...)
        except Exception as e:
            logger.error("All AI providers failed", error=str(e))
            raise HTTPException(
                status_code=503,
                detail="AI services temporarily unavailable"
            )
```

---

## Error Monitoring & Alerting

### Sentry Integration (Optional)

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastAPIIntegration

sentry_sdk.init(
    dsn=SENTRY_DSN,
    integrations=[FastAPIIntegration()],
    traces_sample_rate=0.1,
    environment="production"
)

# Sentry will automatically capture unhandled exceptions
```

### Custom Error Metrics

```python
from prometheus_client import Counter, Histogram

error_counter = Counter(
    'airis_errors_total',
    'Total errors by type',
    ['error_type', 'endpoint']
)

@app.middleware("http")
async def error_metrics_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except HTTPException as e:
        error_counter.labels(
            error_type=f"http_{e.status_code}",
            endpoint=request.url.path
        ).inc()
        raise
    except Exception as e:
        error_counter.labels(
            error_type=type(e).__name__,
            endpoint=request.url.path
        ).inc()
        raise
```

---

## Testing Error Handling

### Unit Tests for Error Cases

```python
import pytest
from fastapi.testclient import TestClient

def test_create_payment_plan_not_found():
    """Test payment creation with non-existent plan"""
    response = client.post(
        "/api/v1/billing/payment",
        json={"plan_id": "nonexistent", "return_url": "https://example.com"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_create_payment_quota_exceeded():
    """Test payment creation with exceeded quota"""
    # Setup: User with exceeded quota
    # ...

    response = client.post("/api/v1/billing/payment", ...)
    assert response.status_code == 429
    assert "quota exceeded" in response.json()["detail"].lower()
```

---

**Last Updated**: 2025-12-11
**Framework**: FastAPI 0.128.0
**Logging**: Standard `logging` routed into Loguru via `backend/open_webui/utils/logger.py`
