# Coding Standards

## General Principles

- Code readability over cleverness
- Self-documenting code with minimal but meaningful comments
- Follow DRY (Don't Repeat Yourself)
- KISS (Keep It Simple, Stupid)
- YAGNI (You Aren't Gonna Need It)
- Explicit is better than implicit (The Zen of Python)
- Type safety: Use TypeScript and Python type hints everywhere

---

## Python Backend Standards (FastAPI)

### Naming Conventions

#### Variables and Functions

- Use descriptive names: `get_user_subscription()` not `getSub()`
- Snake_case for variables and functions: `user_id`, `fetch_plans()`
- Boolean variables: `is_active`, `has_permission`, `can_access`
- Constants: `UPPER_SNAKE_CASE`: `MAX_RETRIES`, `API_TIMEOUT`

#### Classes

- PascalCase for class names: `BillingService`, `YooKassaClient`
- Private methods start with underscore: `_internal_method()`
- Dunder methods for special Python methods: `__init__()`, `__str__()`

#### Files and Directories

- Modules: `snake_case.py`: `billing.py`, `admin_billing.py`
- Packages: lowercase, no underscores if possible: `routers/`, `models/`
- Tests: `test_module_name.py`: `test_billing.py`

### Type Hints (MANDATORY)

All functions, methods, and variables must have type hints:

```python
from typing import Optional
from pydantic import BaseModel

async def get_user_subscription(
    user_id: str,
    include_usage: bool = False
) -> Optional[dict[str, object]]:
    """Get user subscription data"""
    pass

# Type hints for variables
plans: list[Plan] = []
config: dict[str, object] = {}
subscription: Optional[Subscription] = None
```

### Docstrings (Google Style)

```python
async def create_payment(
    user_id: str,
    plan_id: str,
    return_url: str
) -> dict[str, str]:
    """Create a payment for subscription.

    Args:
        user_id: User ID from auth system
        plan_id: Billing plan ID to subscribe to
        return_url: URL to redirect after payment

    Returns:
        Dictionary with payment_id and confirmation_url

    Raises:
        HTTPException: If plan not found or user already subscribed
        YooKassaError: If payment creation fails

    Example:
        >>> payment = await create_payment("user_123", "plan_pro", "https://...")
        >>> print(payment["confirmation_url"])
    """
    pass
```

### FastAPI Router Structure

```python
from fastapi import APIRouter, Depends, HTTPException
from open_webui.utils.auth import get_verified_user, get_admin_user
from open_webui.models.users import Users

router = APIRouter(prefix="/api/v1/billing", tags=["billing"])

@router.get("/plans")
async def get_plans(user=Depends(get_verified_user)):
    """Get all active billing plans"""
    try:
        plans = Plans.get_active_plans()
        return plans
    except Exception as e:
        log.exception(f"Error fetching plans: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch plans")

@router.post("/subscription")
async def create_subscription(
    request: CreateSubscriptionRequest,
    user=Depends(get_verified_user)
):
    """Create new subscription"""
    # Implementation
    pass
```

### Pydantic Models for Request/Response

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CreatePaymentRequest(BaseModel):
    """Request to create payment"""
    plan_id: str = Field(..., description="Billing plan ID")
    return_url: str = Field(..., description="Return URL after payment")

class CreatePaymentResponse(BaseModel):
    """Payment creation response"""
    transaction_id: str
    confirmation_url: str
    status: str

class PlanResponse(BaseModel):
    """Billing plan response"""
    id: str
    name: str
    price: float
    currency: str
    interval: str
    quotas: Dict[str, int]
    features: List[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True  # For SQLAlchemy models
```

### Async/Await Best Practices

```python
# Good - async for all I/O operations
async def fetch_payment_status(payment_id: str) -> dict[str, object]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{YOOKASSA_API}/payments/{payment_id}")
        response.raise_for_status()
        return response.json()

# Bad - blocking I/O in async function
async def fetch_payment_status_bad(payment_id: str) -> dict[str, object]:
    response = requests.get(f"{YOOKASSA_API}/payments/{payment_id}")  # BLOCKS!
    return response.json()
```

### Database Access Patterns

```python
# Using Peewee models (singleton pattern in project)
from open_webui.models.billing import Plans, Subscriptions

# Get all active plans
plans = Plans.get_active_plans()

# Get user subscription
subscription = Subscriptions.get_subscription_by_user_id(user_id)

# Create new subscription
subscription = Subscriptions.insert_new_subscription(
    user_id=user_id,
    plan_id=plan_id,
    status="active"
)

# Update subscription
Subscriptions.update_subscription_by_id(
    subscription_id,
    {"status": "canceled"}
)
```

### Error Handling in FastAPI

```python
from fastapi import HTTPException
from loguru import logger

# Good - specific error handling with logging
@router.post("/payment")
async def create_payment(request: CreatePaymentRequest, user=Depends(get_verified_user)):
    try:
        # Check if plan exists
        plan = Plans.get_plan_by_id(request.plan_id)
        if not plan:
            raise HTTPException(status_code=404, detail="Plan not found")

        # Create payment
        payment = await yookassa_client.create_payment(
            amount=plan.price,
            currency=plan.currency,
            return_url=request.return_url
        )
        return payment

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except YooKassaError as e:
        logger.error(f"YooKassa error: {e}")
        raise HTTPException(status_code=502, detail="Payment gateway error")
    except Exception as e:
        logger.exception(f"Unexpected error creating payment: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

### Logging Standards

```python
from loguru import logger

# Use structured logging with context
logger.info("Creating payment", user_id=user.id, plan_id=plan_id, amount=amount)
logger.error("Payment failed", user_id=user.id, error=str(e), exc_info=True)

# Log levels:
# DEBUG - detailed diagnostic information
# INFO - general operational messages
# WARNING - unexpected but handled situations
# ERROR - errors that affect functionality
# CRITICAL - critical system failures
```

---

## TypeScript/Svelte Frontend Standards

### Naming Conventions

#### Variables and Functions

- camelCase for variables and functions: `userId`, `fetchPlans()`
- Boolean variables: `isActive`, `hasPermission`, `canAccess`
- Constants: `UPPER_SNAKE_CASE` or `SCREAMING_SNAKE_CASE`: `API_BASE_URL`, `MAX_RETRIES`

#### Interfaces and Types

- PascalCase: `Plan`, `Subscription`, `BillingInfo`
- Prefix interfaces with `I` only if ambiguous: `IConfig` (rare)

#### Components

- PascalCase for Svelte components: `PlanCard.svelte`, `BillingDashboard.svelte`

#### Files and Directories

- Routes: `+page.svelte`, `+layout.svelte`, `+server.ts`
- Components: `PascalCase.svelte`
- Utilities: `camelCase.ts`: `billing.ts`, `formatters.ts`

### TypeScript Type Safety

```typescript
// Define interfaces for all data structures
export interface Plan {
	id: string;
	name: string;
	price: number;
	currency: string;
	interval: string;
	quotas: Record<string, number>;
	features: string[];
	is_active: boolean;
	created_at: string;
}

export interface Subscription {
	id: string;
	user_id: string;
	plan_id: string;
	status: 'active' | 'canceled' | 'past_due' | 'trialing';
	current_period_start: string;
	current_period_end: string;
}

// Type all function parameters and return values
export const getPlans = async (token: string): Promise<Plan[] | null> => {
	try {
		const res = await fetch(`${API_BASE_URL}/api/v1/billing/plans`, {
			method: 'GET',
			headers: {
				Authorization: `Bearer ${token}`,
				'Content-Type': 'application/json'
			}
		});

		if (!res.ok) {
			throw new Error(`HTTP ${res.status}: ${await res.text()}`);
		}

		return (await res.json()) as Plan[];
	} catch (error) {
		console.error('Error fetching plans:', error);
		return null;
	}
};
```

### Svelte Component Structure

```svelte
<script lang="ts">
	// Imports first
	import { onMount } from 'svelte';
	import { toast } from 'svelte-sonner';
	import type { Plan } from '$lib/types/billing';

	// Props
	export let userId: string;
	export let onSelect: (plan: Plan) => void = () => {};

	// State variables
	let plans: Plan[] = [];
	let loading = false;
	let error: string | null = null;

	// Reactive declarations
	$: activePlans = plans.filter((p) => p.is_active);

	// Lifecycle
	onMount(async () => {
		await loadPlans();
	});

	// Functions
	async function loadPlans() {
		loading = true;
		error = null;

		try {
			const response = await fetch('/api/v1/billing/plans');
			if (!response.ok) throw new Error('Failed to load plans');
			plans = await response.json();
		} catch (e) {
			error = e instanceof Error ? e.message : 'Unknown error';
			toast.error('Failed to load plans');
		} finally {
			loading = false;
		}
	}

	function handleSelectPlan(plan: Plan) {
		onSelect(plan);
	}
</script>

<!-- Template -->
{#if loading}
	<div class="loading">Loading plans...</div>
{:else if error}
	<div class="error">{error}</div>
{:else}
	<div class="plans-grid">
		{#each activePlans as plan (plan.id)}
			<button class="plan-card" on:click={() => handleSelectPlan(plan)}>
				<h3>{plan.name}</h3>
				<p class="price">{plan.price} {plan.currency}</p>
			</button>
		{/each}
	</div>
{/if}

<style>
	.plans-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
		gap: 1rem;
	}

	.plan-card {
		padding: 1.5rem;
		border: 1px solid var(--border-color);
		border-radius: 8px;
		cursor: pointer;
	}

	.plan-card:hover {
		background: var(--hover-bg);
	}
</style>
```

### API Client Patterns

```typescript
// src/lib/apis/billing/index.ts

const API_BASE_URL = 'http://localhost:8080';

// Response wrapper
type ApiResponse<T> = {
	data: T | null;
	error: string | null;
};

// Generic fetch wrapper
async function apiCall<T>(
	endpoint: string,
	token: string,
	options: RequestInit = {}
): Promise<ApiResponse<T>> {
	try {
		const res = await fetch(`${API_BASE_URL}${endpoint}`, {
			...options,
			headers: {
				Authorization: `Bearer ${token}`,
				'Content-Type': 'application/json',
				...options.headers
			}
		});

		if (!res.ok) {
			const text = await res.text();
			throw new Error(`HTTP ${res.status}: ${text}`);
		}

		const data = (await res.json()) as T;
		return { data, error: null };
	} catch (error) {
		console.error(`API call failed [${endpoint}]:`, error);
		return {
			data: null,
			error: error instanceof Error ? error.message : 'Unknown error'
		};
	}
}

// Specific API methods
export const getPlans = async (token: string): Promise<Plan[] | null> => {
	const { data } = await apiCall<Plan[]>('/api/v1/billing/plans', token);
	return data;
};

export const createPayment = async (
	token: string,
	request: CreatePaymentRequest
): Promise<CreatePaymentResponse | null> => {
	const { data } = await apiCall<CreatePaymentResponse>('/api/v1/billing/payment', token, {
		method: 'POST',
		body: JSON.stringify(request)
	});
	return data;
};
```

### Svelte Stores

```typescript
// src/lib/stores/billing.ts
import { writable, derived } from 'svelte/store';
import type { Subscription, Plan } from '$lib/types/billing';

export const subscription = writable<Subscription | null>(null);
export const plans = writable<Plan[]>([]);

// Derived store
export const hasActiveSubscription = derived(
	subscription,
	($subscription) => $subscription?.status === 'active'
);

export const currentPlan = derived([subscription, plans], ([$subscription, $plans]) => {
	if (!$subscription) return null;
	return $plans.find((p) => p.id === $subscription.plan_id) || null;
});
```

### Error Handling in Frontend

```typescript
// Use try-catch with specific error messages
async function handlePayment(planId: string) {
	try {
		loading = true;
		error = null;

		const response = await createPayment(token, {
			plan_id: planId,
			return_url: window.location.href
		});

		if (!response) {
			throw new Error('Failed to create payment');
		}

		// Redirect to payment page
		window.location.href = response.confirmation_url;
	} catch (e) {
		error = e instanceof Error ? e.message : 'Payment failed';
		toast.error(error);
		console.error('Payment error:', e);
	} finally {
		loading = false;
	}
}
```

### Tailwind CSS Standards

```svelte
<!-- Use Tailwind utility classes, avoid inline styles -->
<div class="flex flex-col gap-4 p-6 rounded-lg border border-gray-200 dark:border-gray-700">
	<h2 class="text-xl font-semibold text-gray-900 dark:text-white">Billing Plans</h2>

	<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
		{#each plans as plan}
			<div class="plan-card hover:shadow-lg transition-shadow">
				<!-- Content -->
			</div>
		{/each}
	</div>
</div>

<!-- Use custom classes only when necessary -->
<style>
	.plan-card {
		@apply p-4 rounded-lg border;
	}
</style>
```

---

## Code Organization

### File Structure Limits

- Maximum file length: 500 lines. If longer — split into modules
- Maximum function length: 50 lines. If longer — decompose

### Function Responsibility

One function = one responsibility (Single Responsibility Principle)

```python
# Good - single responsibility
async def get_user_subscription(user_id: str) -> Optional[Subscription]:
    """Get user subscription"""
    return Subscriptions.get_subscription_by_user_id(user_id)

async def check_quota(user_id: str, metric: str) -> bool:
    """Check if user has quota available"""
    usage = get_current_usage(user_id, metric)
    limit = get_quota_limit(user_id, metric)
    return usage < limit

# Bad - multiple responsibilities
async def get_user_data_and_check_quota(user_id: str) -> Dict:
    """Do too many things"""
    subscription = get_subscription(user_id)
    usage = get_usage(user_id)
    quota_ok = check_quota(user_id)
    return {"subscription": subscription, "usage": usage, "quota_ok": quota_ok}
```

---

## Comments and Documentation

### When to Comment

```python
# Good - explaining WHY, not WHAT
def calculate_proration(old_price: float, new_price: float, days_left: int) -> float:
    # YooKassa requires prorated amount to be calculated using
    # calendar days, not billing periods (per their API docs v3.0)
    return (new_price - old_price) * (days_left / 30)

# Bad - stating the obvious
def add_numbers(a: int, b: int) -> int:
    # Add a and b together
    return a + b  # return the sum
```

### TODO Comments

```python
# TODO(username): Add caching for frequently requested plans
# FIXME(username): Race condition when processing concurrent subscriptions
# NOTE: Temporary workaround until YooKassa adds webhook retry
```

---

## Formatting

### Python

- Maximum line length: 100 characters
- Use Black formatter (configured in project)
- Configure in `pyproject.toml` or run: `black .`

### TypeScript

- Maximum line length: 100 characters
- Use Prettier (configured in project)
- Configure in `.prettierrc` or run: `npm run format`

### Imports Organization

#### Python

```python
# Standard library imports
import asyncio
import logging
from typing import Optional

# Third-party imports
import httpx
from fastapi import APIRouter, Depends
from pydantic import BaseModel

# Local application imports
from open_webui.models.billing import Plans, Subscriptions
from open_webui.utils.auth import get_verified_user
```

#### TypeScript

```typescript
// Svelte imports
import { onMount } from 'svelte';

// External libraries
import { toast } from 'svelte-sonner';

// Types
import type { Plan, Subscription } from '$lib/types/billing';

// Local modules
import { getPlans, createPayment } from '$lib/apis/billing';
import { formatCurrency } from '$lib/utils/formatters';
```

---

## Testing Considerations

### Write Testable Code

```python
# Good - easy to test (dependency injection)
async def fetch_payment_data(client: httpx.AsyncClient, payment_id: str):
    response = await client.get(f"/payments/{payment_id}")
    return response.json()

# Bad - hard to test (creates own dependencies)
async def fetch_payment_data_bad(payment_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"/payments/{payment_id}")
        return response.json()
```

### Dependency Injection in FastAPI

```python
# Dependencies are explicit and easily mockable
from fastapi import Depends

def get_billing_service() -> BillingService:
    return BillingService()

@router.post("/subscription")
async def create_subscription(
    request: CreateSubscriptionRequest,
    user=Depends(get_verified_user),
    billing_service: BillingService = Depends(get_billing_service)
):
    return await billing_service.create_subscription(user.id, request.plan_id)
```

---

## Security Best Practices

### Never Store Secrets in Code

```python
# Good - from environment variables
import os

# Good - from environment variables (this repo uses env parsing in backend/open_webui/env.py)
YOOKASSA_SHOP_ID = os.environ.get("YOOKASSA_SHOP_ID", "")
YOOKASSA_SECRET_KEY = os.environ.get("YOOKASSA_SECRET_KEY", "")
DATABASE_URL = os.environ.get("DATABASE_URL", "")
```

### Input Validation

```python
# Always validate user input with Pydantic
from pydantic import BaseModel, Field, validator

class CreatePlanRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0, description="Price must be positive")
    interval: str = Field(..., regex='^(day|week|month|year)$')

    @validator('price')
    def price_must_be_reasonable(cls, v):
        if v > 1000000:
            raise ValueError('Price too high')
        return v
```

### SQL Injection Prevention

```python
# Good - use ORM or parameterized queries
subscription = Subscriptions.get_subscription_by_user_id(user_id)

# Bad - string interpolation (SQL injection risk!)
query = f"SELECT * FROM subscriptions WHERE user_id = '{user_id}'"
```

### XSS Prevention (Frontend)

```typescript
// Use DOMPurify for user-generated HTML
import DOMPurify from 'dompurify';

const sanitizedHTML = DOMPurify.sanitize(userInput);
```

---

## Code Review Checklist

### Python Backend

- [ ] All functions have type hints
- [ ] Public functions have docstrings
- [ ] FastAPI dependencies used correctly
- [ ] Pydantic models for request/response
- [ ] Async/await used for all I/O
- [ ] Proper exception handling with logging
- [ ] No secrets in code
- [ ] Code formatted with Black

### TypeScript Frontend

- [ ] All functions have TypeScript types
- [ ] Interfaces defined for all data structures
- [ ] API calls handle errors gracefully
- [ ] Loading and error states in UI
- [ ] Tailwind CSS used (no inline styles)
- [ ] Code formatted with Prettier
- [ ] Svelte component structure followed

### General

- [ ] No overly long functions (>50 lines)
- [ ] No overly long files (>500 lines)
- [ ] Tests written for new functionality
- [ ] Meaningful variable and function names
- [ ] Comments explain WHY, not WHAT

---

## Project-Specific Patterns

### Billing System

```python
# Always use BillingService for business logic
from open_webui.utils.billing import BillingService

billing_service = BillingService()

# Get user subscription with usage
billing_info = await billing_service.get_user_billing_info(user_id)

# Check and enforce quota
await billing_service.enforce_quota(user_id, "requests", amount=1)

# Track usage
await billing_service.track_usage(
    user_id=user_id,
    metric="tokens_input",
    amount=token_count
)
```

### Audit Logging (Admin Actions)

```python
from open_webui.models.audit import AuditLog, AuditAction

# Log all admin actions
AuditLog.log_action(
    user_id=admin_user.id,
    action=AuditAction.PLAN_UPDATED,
    entity_type="plan",
    entity_id=plan.id,
    description=f"Updated plan: {plan.name}",
    changes={"price": {"old": old_price, "new": new_price}}
)
```

### WebSocket Events

```python
from open_webui.socket.main import get_event_emitter

emitter = get_event_emitter()

# Emit events to connected clients
await emitter.emit("subscription_updated", {
    "user_id": user_id,
    "status": "active"
})
```

---

**Last Updated**: 2026-02-05
**Python Version**: 3.11+
**Node Version**: 18.13.0 - 22.x.x
