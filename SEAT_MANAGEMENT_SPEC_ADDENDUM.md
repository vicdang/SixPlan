# SEAT MANAGEMENT SYSTEM — SPEC ADDENDUM
**Version:** 1.0 | **Supplements:** SEAT_MANAGEMENT_SPEC.md  
**Purpose:** Concrete implementation details for Claude Code agent — no ambiguity, no decisions left open.

---

## TABLE OF CONTENTS
14. [Authentication Flow](#14-authentication-flow)
15. [Profile Page](#15-profile-page)
16. [CSV Member Import](#16-csv-member-import)
17. [CRUD Wireframes](#17-crud-wireframes)
18. [API Request/Response Examples](#18-api-requestresponse-examples)
19. [Form Validation Rules](#19-form-validation-rules)
20. [Error Response Format](#20-error-response-format)
21. [Seed Data](#21-seed-data)
22. [Project Bootstrap Commands](#22-project-bootstrap-commands)

---

## 14. AUTHENTICATION FLOW

### 14.1 Login Page Wireframe

```
┌────────────────────────────────────────────────────────┐
│                                                        │
│                                                        │
│              ┌─────────────────────────┐               │
│              │                         │               │
│              │   SEATMAP               │               │
│              │   Internal workspace    │               │
│              │   seat management       │               │
│              │                         │               │
│              │   ─────────────────     │               │
│              │                         │               │
│              │   Username or email     │               │
│              │   ┌─────────────────┐   │               │
│              │   │                 │   │               │
│              │   └─────────────────┘   │               │
│              │                         │               │
│              │   Password              │               │
│              │   ┌─────────────────┐   │               │
│              │   │            [👁] │   │               │
│              │   └─────────────────┘   │               │
│              │                         │               │
│              │   [ ] Remember me       │               │
│              │                         │               │
│              │   ┌─────────────────┐   │               │
│              │   │     Sign in     │   │               │
│              │   └─────────────────┘   │               │
│              │                         │               │
│              │   ─── or continue ───   │               │
│              │                         │               │
│              │   ┌─────────────────┐   │               │
│              │   │  G  Google      │   │  (disabled)   │
│              │   └─────────────────┘   │               │
│              │                         │               │
│              └─────────────────────────┘               │
│                                                        │
│                                                        │
└────────────────────────────────────────────────────────┘
```

**Styling:**
- Full-screen `bg-surface-base`
- Centered card: `max-w-md bg-surface-raised border border-surface-border rounded-xl p-8`
- Logo: text-only "SEATMAP" in `font-semibold tracking-tight text-2xl`
- Subtitle: `text-sm text-text-muted`
- Inputs: shadcn/ui `<Input />` component
- Button: shadcn/ui `<Button />` full width
- Google button: disabled with tooltip "Coming soon"

### 14.2 JWT Strategy

**Token Structure (access_token):**
```json
{
  "sub": "<account_id>",
  "member_id": "<member_id>",
  "role": "admin",
  "username": "vic.nguyen",
  "exp": 1735689600,
  "iat": 1735686000,
  "type": "access"
}
```

**Refresh Token:**
- Stored in `httpOnly` cookie OR in localStorage (configurable via env)
- Default for MVP: **localStorage** for simplicity (rotate to httpOnly cookie before production)
- Refresh token longer-lived (30 days), access token short-lived (60 min)

**Storage (frontend):**
```typescript
// src/lib/auth-storage.ts
const KEY_ACCESS = 'seatmap_access_token';
const KEY_REFRESH = 'seatmap_refresh_token';

export const tokenStorage = {
  getAccess: () => localStorage.getItem(KEY_ACCESS),
  setAccess: (token: string) => localStorage.setItem(KEY_ACCESS, token),
  getRefresh: () => localStorage.getItem(KEY_REFRESH),
  setRefresh: (token: string) => localStorage.setItem(KEY_REFRESH, token),
  clear: () => {
    localStorage.removeItem(KEY_ACCESS);
    localStorage.removeItem(KEY_REFRESH);
  },
};
```

### 14.3 Axios Interceptor (Auto-Refresh)

```typescript
// src/lib/axios.ts
import axios from 'axios';
import { tokenStorage } from './auth-storage';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api/v1',
});

// Inject access token
api.interceptors.request.use((config) => {
  const token = tokenStorage.getAccess();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Auto-refresh on 401
let isRefreshing = false;
let refreshQueue: Array<(token: string) => void> = [];

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve) => {
          refreshQueue.push((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            resolve(api(originalRequest));
          });
        });
      }
      originalRequest._retry = true;
      isRefreshing = true;
      try {
        const refreshToken = tokenStorage.getRefresh();
        const { data } = await axios.post('/api/v1/auth/refresh', { refresh_token: refreshToken });
        tokenStorage.setAccess(data.access_token);
        refreshQueue.forEach((cb) => cb(data.access_token));
        refreshQueue = [];
        originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
        return api(originalRequest);
      } catch (err) {
        tokenStorage.clear();
        window.location.href = '/login';
        return Promise.reject(err);
      } finally {
        isRefreshing = false;
      }
    }
    return Promise.reject(error);
  }
);

export default api;
```

### 14.4 Logout Flow

1. User clicks "Logout" in avatar dropdown
2. Frontend: POST `/auth/logout` with current access_token in header
3. Backend: Add `jti` (JWT ID) to Redis blacklist with TTL = remaining token lifetime
4. Frontend: `tokenStorage.clear()` → redirect to `/login`
5. Show toast: "Signed out"

### 14.5 Protected Route Component

```typescript
// src/components/auth/RequireAuth.tsx
import { Navigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '@/store/authStore';
import type { UserRole } from '@/types/auth';

interface Props {
  children: React.ReactNode;
  roles?: UserRole[];
}

export function RequireAuth({ children, roles }: Props) {
  const { account, isHydrated } = useAuthStore();
  const location = useLocation();

  if (!isHydrated) return <LoadingSpinner />;
  if (!account) return <Navigate to="/login" state={{ from: location }} replace />;
  if (roles && !roles.includes(account.role)) return <Navigate to="/forbidden" replace />;

  return <>{children}</>;
}
```

### 14.6 Auth Backend Logic

```python
# app/services/auth_service.py
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    async def authenticate(self, identifier: str, password: str) -> Account:
        # identifier can be username or email
        account = await self._find_by_identifier(identifier)
        if not account or not account.is_active:
            raise InvalidCredentialsError()
        if not pwd_context.verify(password, account.password_hash):
            raise InvalidCredentialsError()
        account.last_login_at = datetime.utcnow()
        await self.db.commit()
        return account

    def create_access_token(self, account: Account) -> str:
        payload = {
            "sub": str(account.id),
            "member_id": str(account.member_id),
            "role": account.role.value,
            "username": account.member.username,
            "exp": datetime.utcnow() + timedelta(minutes=60),
            "iat": datetime.utcnow(),
            "type": "access",
            "jti": str(uuid4()),
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")

    def create_refresh_token(self, account: Account) -> str:
        payload = {
            "sub": str(account.id),
            "exp": datetime.utcnow() + timedelta(days=30),
            "iat": datetime.utcnow(),
            "type": "refresh",
            "jti": str(uuid4()),
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")

    async def blacklist_token(self, jti: str, ttl_seconds: int):
        await redis.setex(f"jwt_blacklist:{jti}", ttl_seconds, "1")

    async def is_blacklisted(self, jti: str) -> bool:
        return await redis.exists(f"jwt_blacklist:{jti}") > 0
```

---

## 15. PROFILE PAGE

### 15.1 Page Layout

**Route:** `/profile`  
**Access:** All authenticated users

```
┌──────────────────────────────────────────────────────────────────┐
│ PageHeader: "My Profile"                                          │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│ ┌─── Personal Information ──────────────────────────────────┐    │
│ │                                                            │    │
│ │  [Avatar]   Vic Nguyen                                     │    │
│ │   80×80     Project Manager / Business Analyst             │    │
│ │             IT Department                                  │    │
│ │             [Edit profile]                                 │    │
│ │                                                            │    │
│ │  ─────────────────────────────────────────────────────     │    │
│ │                                                            │    │
│ │  Username        vic.nguyen          (read-only)           │    │
│ │  Employee ID     EMP12345            (read-only)           │    │
│ │  Email           vic@company.com     (read-only)           │    │
│ │  Phone           +84 901 234 567     [editable]            │    │
│ │  Gender          Male                (read-only)           │    │
│ │  Department      IT                  (read-only)           │    │
│ │  Role            Admin               (read-only)           │    │
│ │                                                            │    │
│ └────────────────────────────────────────────────────────────┘    │
│                                                                   │
│ ┌─── Security ──────────────────────────────────────────────┐    │
│ │                                                            │    │
│ │  Password        ●●●●●●●●           [Change password]      │    │
│ │  Last login      Jun 22, 2026 14:23                        │    │
│ │                                                            │    │
│ └────────────────────────────────────────────────────────────┘    │
│                                                                   │
│ ┌─── My Seat Assignments ───────────────────────────────────┐    │
│ │                                                            │    │
│ │  Primary seat                                              │    │
│ │  ┌──────────────────────────────────────────────────┐      │    │
│ │  │ C703-A01           [Status: Occupied]             │      │    │
│ │  │ Block C / Floor 7 / Room 03                       │      │    │
│ │  │ Project: Team Alpha                               │      │    │
│ │  │ Since Jun 1, 2026                  [View on map] │      │    │
│ │  └──────────────────────────────────────────────────┘      │    │
│ │                                                            │    │
│ │  Secondary slots (2)                                       │    │
│ │  ┌──────────────────────────────────────────────────┐      │    │
│ │  │ C302-B05           hostname: VIC-LAB-01           │      │    │
│ │  │ Block C / Floor 3 / Room 02                       │      │    │
│ │  │ IP: 10.0.5.123     MAC: AA:BB:CC:DD:EE:FF         │      │    │
│ │  │                                    [View on map] │      │    │
│ │  └──────────────────────────────────────────────────┘      │    │
│ │                                                            │    │
│ └────────────────────────────────────────────────────────────┘    │
│                                                                   │
│ ┌─── My Pending Requests ───────────────────────────────────┐    │
│ │                                                            │    │
│ │  [Empty state if none, otherwise table]                    │    │
│ │                                                            │    │
│ └────────────────────────────────────────────────────────────┘    │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

### 15.2 Edit Profile Modal

```
┌─────────────────────────────────────────────┐
│  Edit profile                          [X]  │
├─────────────────────────────────────────────┤
│                                             │
│  Phone                                      │
│  ┌─────────────────────────────────────┐    │
│  │ +84 901 234 567                     │    │
│  └─────────────────────────────────────┘    │
│                                             │
│  Avatar                                     │
│  ┌─────────────────────────────────────┐    │
│  │ [Upload image] or [Use initials]    │    │
│  └─────────────────────────────────────┘    │
│                                             │
│              [Cancel]      [Save changes]   │
│                                             │
└─────────────────────────────────────────────┘
```

### 15.3 Change Password Modal

```
┌─────────────────────────────────────────────┐
│  Change password                       [X]  │
├─────────────────────────────────────────────┤
│                                             │
│  Current password                           │
│  ┌─────────────────────────────────────┐    │
│  │                                  👁  │    │
│  └─────────────────────────────────────┘    │
│                                             │
│  New password                               │
│  ┌─────────────────────────────────────┐    │
│  │                                  👁  │    │
│  └─────────────────────────────────────┘    │
│  Min 8 chars, 1 uppercase, 1 number         │
│                                             │
│  Confirm new password                       │
│  ┌─────────────────────────────────────┐    │
│  │                                  👁  │    │
│  └─────────────────────────────────────┘    │
│                                             │
│           [Cancel]   [Update password]      │
│                                             │
└─────────────────────────────────────────────┘
```

### 15.4 Profile API Endpoints

```
GET    /profile                 → ProfileDetail (current user)
PUT    /profile                 → ProfileDetail (update phone, avatar)
POST   /profile/avatar          → { avatar_url } (multipart upload)
POST   /profile/change-password → 200 (current_password, new_password)
GET    /profile/assignments     → { primary: Assignment, secondary: Assignment[] }
GET    /profile/requests        → PaginatedList[SeatRequest] (own only)
```

---

## 16. CSV MEMBER IMPORT

### 16.1 File Format Specification

**Encoding:** UTF-8 with BOM (Excel-compatible)  
**Format:** CSV or Excel (.xlsx, .xls)  
**Max file size:** 5 MB  
**Max rows:** 5,000 per import

### 16.2 Column Schema

| Column | Required | Type | Validation | Example |
|---|:---:|---|---|---|
| `employee_id` | ✓ | string | 1–50 chars, unique | `EMP12345` |
| `username` | ✓ | string | 3–100 chars, unique, lowercase alphanumeric + dot/underscore | `vic.nguyen` |
| `full_name` | ✓ | string | 1–200 chars | `Nguyen Van Vic` |
| `email` | ✓ | string | Valid email, unique | `vic@company.com` |
| `gender` | ✗ | enum | `male` / `female` / `other` | `male` |
| `phone` | ✗ | string | 7–30 chars | `+84901234567` |
| `title` | ✗ | string | 1–100 chars | `Project Manager` |
| `department_code` | ✓ | string | Must exist in `departments.code` | `IT` |
| `role` | ✗ | enum | `viewer`/`user`/`manager`/`admin`, default `user` | `user` |
| `initial_password` | ✗ | string | If empty, system generates random 12-char password | `Welcome123!` |

### 16.3 Sample CSV Template

```csv
employee_id,username,full_name,email,gender,phone,title,department_code,role,initial_password
EMP12345,vic.nguyen,Nguyen Van Vic,vic@company.com,male,+84901234567,Project Manager,IT,admin,
EMP12346,linh.tran,Tran Thi Linh,linh@company.com,female,+84901234568,QA Engineer,QA,user,
EMP12347,minh.pham,Pham Quang Minh,minh@company.com,male,,Developer,DEV,user,Welcome2026
```

### 16.4 Import Workflow

**Step 1: Upload**
```
┌──────────────────────────────────────────────────────┐
│  Import members                                  [X] │
├──────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────────────────────────────────────┐    │
│  │                                              │    │
│  │     Drop CSV or Excel file here              │    │
│  │     or click to browse                       │    │
│  │                                              │    │
│  │     Max 5 MB · UTF-8 encoding                │    │
│  └──────────────────────────────────────────────┘    │
│                                                      │
│  [Download template CSV]                             │
│                                                      │
│                       [Cancel]   [Upload & preview]  │
└──────────────────────────────────────────────────────┘
```

**Step 2: Preview & Validate**
```
┌──────────────────────────────────────────────────────────────┐
│  Import preview                                          [X] │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  members.csv  ·  52 rows  ·  47 valid  ·  5 errors           │
│                                                              │
│  Mode: ○ Create new only   ● Create or update                │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐    │
│  │ Row │ Status │ employee_id │ username    │ Error    │    │
│  ├─────┼────────┼─────────────┼─────────────┼──────────┤    │
│  │ 1   │ NEW    │ EMP12345    │ vic.nguyen  │ —        │    │
│  │ 2   │ UPDATE │ EMP12346    │ linh.tran   │ —        │    │
│  │ 3   │ ERROR  │ EMP12347    │ minh.pham   │ Dept     │    │
│  │     │        │             │             │ code     │    │
│  │     │        │             │             │ ITX not  │    │
│  │     │        │             │             │ found    │    │
│  │ 4   │ ERROR  │ (empty)     │ —           │ Required │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                              │
│  [ ] Send welcome email to new members (placeholder)         │
│                                                              │
│                       [Cancel]   [Import 47 valid rows]      │
└──────────────────────────────────────────────────────────────┘
```

**Step 3: Result Summary**
- Toast: "Imported 47 members successfully. 5 rows skipped (see report)."
- Generated random passwords downloadable as CSV (`employee_id, generated_password`).

### 16.5 Import Service Pseudocode

```python
# app/services/import_service.py

class ImportResult(BaseModel):
    total_rows: int
    created: int
    updated: int
    errors: list[ImportError]
    generated_passwords: list[dict]  # if any

class ImportError(BaseModel):
    row_number: int
    employee_id: str | None
    field: str | None
    message: str

class MemberImportService:
    async def parse_file(self, file: UploadFile) -> list[dict]:
        # Detect CSV vs Excel by extension
        # Read with pandas, normalize column names, return list of dicts
        ...

    async def validate_rows(self, rows: list[dict]) -> tuple[list[dict], list[ImportError]]:
        valid = []
        errors = []
        # For each row:
        # - check required fields
        # - validate email format
        # - validate department_code exists (cache departments dict)
        # - validate role enum
        # - check uniqueness within file (employee_id, username, email)
        # - check uniqueness against DB
        return valid, errors

    async def execute_import(
        self, valid_rows: list[dict], mode: Literal["create_only", "upsert"]
    ) -> ImportResult:
        # Bulk insert/update inside a single transaction
        # Generate password if initial_password empty
        # Hash all passwords with bcrypt
        # Create account row for each member
        # Return ImportResult
        ...
```

### 16.6 API

```
GET    /members/import/template      → text/csv (download template)
POST   /members/import/preview       → ImportPreview (no DB changes)
POST   /members/import/execute       → ImportResult (commits)
```

---

## 17. CRUD WIREFRAMES

### 17.1 Member List Page (Admin)

```
┌──────────────────────────────────────────────────────────────────────┐
│ PageHeader: Members                                                   │
│                                  [Import CSV]  [+ Add member]         │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                │
│  │ Search...    │  │ Dept     ▼  │  │ Role     ▼  │                │
│  └──────────────┘  └──────────────┘  └──────────────┘                │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │ Employee ID │ Name        │ Email           │ Dept │ Role │     │ │
│  ├─────────────┼─────────────┼─────────────────┼──────┼──────┼─────┤ │
│  │ EMP12345    │ Vic Nguyen  │ vic@company.com │ IT   │ Admin│ ⋮   │ │
│  │ EMP12346    │ Linh Tran   │ linh@…          │ QA   │ User │ ⋮   │ │
│  │ EMP12347    │ Minh Pham   │ minh@…          │ DEV  │ User │ ⋮   │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                                                       │
│  Showing 1–10 of 247                  [< 1 2 3 ... 25 >]  [10 ▼]    │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

**Row actions menu (⋮):**
- View detail
- Edit
- Reset password
- Deactivate / Activate
- Delete (soft)

### 17.2 Member Add/Edit Modal (Slide-over)

```
┌────────────────────────────────────────────────┐
│                                                │
│  Add member                            [X]    │
│  Create a new member record                    │
│                                                │
│  ──────────────────────────────────────────    │
│                                                │
│  Employee ID *                                 │
│  ┌──────────────────────────────────────────┐  │
│  │                                          │  │
│  └──────────────────────────────────────────┘  │
│                                                │
│  Username *                                    │
│  ┌──────────────────────────────────────────┐  │
│  │                                          │  │
│  └──────────────────────────────────────────┘  │
│                                                │
│  Full name *                                   │
│  ┌──────────────────────────────────────────┐  │
│  │                                          │  │
│  └──────────────────────────────────────────┘  │
│                                                │
│  Email *                                       │
│  ┌──────────────────────────────────────────┐  │
│  │                                          │  │
│  └──────────────────────────────────────────┘  │
│                                                │
│  Gender                                        │
│  ┌──────────────────────────────────────────┐  │
│  │ Select                              ▼   │  │
│  └──────────────────────────────────────────┘  │
│                                                │
│  Phone                                         │
│  ┌──────────────────────────────────────────┐  │
│  │                                          │  │
│  └──────────────────────────────────────────┘  │
│                                                │
│  Title                                         │
│  ┌──────────────────────────────────────────┐  │
│  │                                          │  │
│  └──────────────────────────────────────────┘  │
│                                                │
│  Department *                                  │
│  ┌──────────────────────────────────────────┐  │
│  │ Select                              ▼   │  │
│  └──────────────────────────────────────────┘  │
│                                                │
│  Role *                                        │
│  ┌──────────────────────────────────────────┐  │
│  │ User                                ▼   │  │
│  └──────────────────────────────────────────┘  │
│                                                │
│  Initial password                              │
│  ┌──────────────────────────────────────────┐  │
│  │ Leave empty to auto-generate         👁  │  │
│  └──────────────────────────────────────────┘  │
│                                                │
│  [x] Account active                            │
│                                                │
│  ──────────────────────────────────────────    │
│                                                │
│                    [Cancel]    [Create member] │
│                                                │
└────────────────────────────────────────────────┘
```

**Implementation:** shadcn/ui `<Sheet />` component, slides from right, width `w-96` on mobile, `w-[480px]` on desktop.

### 17.3 Room List Page (Admin)

```
┌──────────────────────────────────────────────────────────────────────┐
│ PageHeader: Rooms                                                     │
│                                                  [+ Create room]      │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  Tabs: [All] [Draft] [Pending] [Warehouse] [Published] [Locked]      │
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐                                  │
│  │ Search code  │  │ Sort: Recent ▼│                                 │
│  └──────────────┘  └──────────────┘                                  │
│                                                                       │
│  Grid (3 columns):                                                    │
│                                                                       │
│  ┌────────────────────┐  ┌────────────────────┐  ┌────────────────┐  │
│  │ C703               │  │ C302               │  │ B401           │  │
│  │ Block C Floor 7    │  │ Block C Floor 3    │  │ Block B Floor 4│  │
│  │ ────────────────   │  │ ────────────────   │  │ ─────────────  │  │
│  │ 32 seats           │  │ 28 seats           │  │ 24 seats       │  │
│  │ 18 occupied (56%)  │  │ 5 occupied (18%)   │  │ 22 occupied    │  │
│  │ ●●●●●●●○○○         │  │ ●●○○○○○○○○         │  │ ●●●●●●●●●●     │  │
│  │                    │  │                    │  │                │  │
│  │ [Published v3]     │  │ [Draft]            │  │ [Locked]       │  │
│  │                    │  │                    │  │                │  │
│  │ [Open] [Edit] [⋮]  │  │ [Edit] [⋮]         │  │ [Open] [⋮]     │  │
│  └────────────────────┘  └────────────────────┘  └────────────────┘  │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

**Card actions menu (⋮):**
- View floor plan
- Edit (requires lock)
- View version history
- Comments
- Delete (draft only, with confirmation)

### 17.4 Room Create Modal

```
┌────────────────────────────────────────────────┐
│  Create room                            [X]    │
├────────────────────────────────────────────────┤
│                                                │
│  Room code *                                   │
│  ┌──────────────────────────────────────────┐  │
│  │ e.g. C703                                │  │
│  └──────────────────────────────────────────┘  │
│  Format: <Block><Floor><Number>                │
│                                                │
│  Room name *                                   │
│  ┌──────────────────────────────────────────┐  │
│  │                                          │  │
│  └──────────────────────────────────────────┘  │
│                                                │
│  Description                                   │
│  ┌──────────────────────────────────────────┐  │
│  │                                          │  │
│  │                                          │  │
│  └──────────────────────────────────────────┘  │
│                                                │
│  Capacity (estimated seats)                    │
│  ┌──────────────────────────────────────────┐  │
│  │ 0                                        │  │
│  └──────────────────────────────────────────┘  │
│  Updated automatically when you design layout  │
│                                                │
│              [Cancel]    [Create and design]   │
│                                                │
└────────────────────────────────────────────────┘
```

**Behavior:** "Create and design" → POST `/rooms` → redirect to `/rooms/{id}/edit` (editor).

### 17.5 Seat CRUD

Seat CRUD happens **inside the Floor Plan Editor**, not as a separate page. When a seat is selected on canvas, the right Properties Panel shows:

```
┌──────────────────────────────────┐
│  Selected seat                   │
├──────────────────────────────────┤
│                                  │
│  Seat code *                     │
│  ┌────────────────────────────┐  │
│  │ C703-A01                   │  │
│  └────────────────────────────┘  │
│                                  │
│  Display label                   │
│  ┌────────────────────────────┐  │
│  │ A01                        │  │
│  └────────────────────────────┘  │
│                                  │
│  Seat type                       │
│  ┌────────────────────────────┐  │
│  │ Single desk            ▼   │  │
│  └────────────────────────────┘  │
│                                  │
│  Status                          │
│  ┌────────────────────────────┐  │
│  │ Available              ▼   │  │
│  └────────────────────────────┘  │
│                                  │
│  Project                         │
│  ┌────────────────────────────┐  │
│  │ — None —               ▼   │  │
│  └────────────────────────────┘  │
│                                  │
│  Description                     │
│  ┌────────────────────────────┐  │
│  │                            │  │
│  └────────────────────────────┘  │
│                                  │
│  Facilities                      │
│  [x] Monitor                     │
│  [x] LAN Port                    │
│  [ ] Standing Desk               │
│  [ ] Near Window                 │
│  [x] Near AC                     │
│  [ ] Power Outlet                │
│  [ ] Locker                      │
│                                  │
│  Max secondary slots             │
│  ┌────────────────────────────┐  │
│  │ Unlimited              ▼   │  │
│  └────────────────────────────┘  │
│                                  │
│  ─── Position & Size ────        │
│  X: 320   Y: 200                 │
│  W: 60    H: 60                  │
│  Rotation: 0°                    │
│                                  │
│  [Delete seat]                   │
│                                  │
└──────────────────────────────────┘
```

Changes are buffered locally (Zustand) until "Save Draft" or auto-save kicks in.

### 17.6 Project CRUD Page

```
┌──────────────────────────────────────────────────────────────────────┐
│ PageHeader: Projects                              [+ Add project]    │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │ Color │ Code         │ Name              │ Seats │ Active │     │ │
│  ├───────┼──────────────┼───────────────────┼───────┼────────┼─────┤ │
│  │ ●     │ TEAM-ALPHA   │ Team Alpha        │ 12    │ Yes    │ ⋮   │ │
│  │ ●     │ TEAM-BETA    │ Team Beta         │ 8     │ Yes    │ ⋮   │ │
│  │ ●     │ INFRA-2026   │ Infrastructure    │ 4     │ No     │ ⋮   │ │
│  └─────────────────────────────────────────────────────────────────┘ │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

### 17.7 Project Add/Edit Modal

```
┌────────────────────────────────────────────────┐
│  Add project                            [X]    │
├────────────────────────────────────────────────┤
│                                                │
│  Project code *                                │
│  ┌──────────────────────────────────────────┐  │
│  │                                          │  │
│  └──────────────────────────────────────────┘  │
│                                                │
│  Project name *                                │
│  ┌──────────────────────────────────────────┐  │
│  │                                          │  │
│  └──────────────────────────────────────────┘  │
│                                                │
│  Color                                         │
│  ┌──────────────────────────────────────────┐  │
│  │ ● Indigo  ● Emerald  ● Rose  ● Amber     │  │
│  │ ● Cyan    ● Violet   ● Lime  ● Pink      │  │
│  │ ── or custom ──   #6366f1                │  │
│  └──────────────────────────────────────────┘  │
│                                                │
│  Description                                   │
│  ┌──────────────────────────────────────────┐  │
│  │                                          │  │
│  └──────────────────────────────────────────┘  │
│                                                │
│  [x] Active                                    │
│                                                │
│              [Cancel]    [Create project]      │
│                                                │
└────────────────────────────────────────────────┘
```

---

## 18. API REQUEST/RESPONSE EXAMPLES

### 18.1 POST /auth/login

**Request:**
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "identifier": "vic.nguyen",
  "password": "MyPass123!"
}
```

**Response 200:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiI...",
  "refresh_token": "eyJhbGciOiJIUzI1NiI...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "account_id": "8f3a...",
    "member_id": "9a1b...",
    "username": "vic.nguyen",
    "full_name": "Nguyen Van Vic",
    "email": "vic@company.com",
    "role": "admin",
    "department": { "id": "...", "code": "IT", "name": "IT" },
    "avatar_url": null
  }
}
```

**Response 401:**
```json
{
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Username or password is incorrect"
  }
}
```

### 18.2 GET /members?page=1&size=10

**Response 200:**
```json
{
  "data": [
    {
      "id": "9a1b...",
      "employee_id": "EMP12345",
      "username": "vic.nguyen",
      "full_name": "Nguyen Van Vic",
      "email": "vic@company.com",
      "department": { "id": "...", "code": "IT", "name": "IT" },
      "title": "Project Manager",
      "is_active": true,
      "has_account": true,
      "role": "admin"
    }
  ],
  "pagination": {
    "page": 1,
    "size": 10,
    "total": 247,
    "total_pages": 25
  }
}
```

### 18.3 POST /rooms

**Request:**
```json
{
  "code": "C703",
  "name": "Block C Floor 7 Room 03",
  "description": "Main engineering room",
  "capacity": 32
}
```

**Response 201:**
```json
{
  "id": "...",
  "code": "C703",
  "name": "Block C Floor 7 Room 03",
  "description": "Main engineering room",
  "capacity": 32,
  "status": "draft",
  "version": 0,
  "layout_data": null,
  "locked_at": null,
  "locked_by": null,
  "created_by": { "id": "...", "username": "vic.nguyen" },
  "created_at": "2026-06-22T07:30:00Z",
  "updated_at": "2026-06-22T07:30:00Z"
}
```

### 18.4 PUT /rooms/{id}/layout

**Request:**
```json
{
  "layout_data": {
    "canvas": { "width": 1200, "height": 800, "background": "#1e1e2e" },
    "elements": [
      {
        "id": "elem_1",
        "type": "door",
        "x": 100, "y": 0, "width": 60, "height": 10,
        "rotation": 0,
        "label": "Main entrance"
      }
    ],
    "seats": [
      {
        "id": "tmp_seat_1",
        "code": "C703-A01",
        "type": "single",
        "x": 200, "y": 150,
        "width": 60, "height": 60,
        "rotation": 0,
        "project_id": null,
        "facilities": ["uuid1", "uuid2"]
      }
    ]
  }
}
```

**Response 200:**
```json
{
  "id": "...",
  "status": "draft",
  "version": 0,
  "seats_created": 1,
  "seats_updated": 0,
  "seats_deleted": 0,
  "layout_data": { "...synced data with real seat IDs..." }
}
```

### 18.5 POST /seat-requests

**Request:**
```json
{
  "seat_id": "...",
  "request_type": "register",
  "requester_note": "Moving to Team Alpha next week"
}
```

**Response 201:**
```json
{
  "id": "...",
  "seat": { "id": "...", "code": "C703-A01", "room_code": "C703" },
  "member": { "id": "...", "full_name": "Nguyen Van Vic" },
  "request_type": "register",
  "status": "pending",
  "requester_note": "Moving to Team Alpha next week",
  "created_at": "2026-06-22T07:30:00Z"
}
```

### 18.6 POST /members/import/preview

**Request:** `multipart/form-data` with `file`

**Response 200:**
```json
{
  "total_rows": 52,
  "valid_count": 47,
  "error_count": 5,
  "preview": [
    {
      "row_number": 1,
      "status": "new",
      "data": { "employee_id": "EMP12345", "username": "vic.nguyen", "...": "..." },
      "errors": []
    },
    {
      "row_number": 3,
      "status": "error",
      "data": { "employee_id": "EMP12347", "username": "minh.pham" },
      "errors": [
        { "field": "department_code", "message": "Department 'ITX' does not exist" }
      ]
    }
  ]
}
```

### 18.7 POST /members/import/execute

**Request:**
```json
{
  "preview_id": "tmp_upload_abc123",
  "mode": "upsert"
}
```

**Response 200:**
```json
{
  "total_rows": 52,
  "created": 42,
  "updated": 5,
  "skipped": 5,
  "errors": [
    { "row_number": 3, "employee_id": "EMP12347", "message": "Department 'ITX' not found" }
  ],
  "generated_passwords_url": "/api/v1/members/import/passwords/abc123.csv"
}
```

---

## 19. FORM VALIDATION RULES

### 19.1 Frontend (Zod)

```typescript
// src/lib/schemas.ts
import { z } from 'zod';

export const loginSchema = z.object({
  identifier: z.string().min(1, 'Required'),
  password: z.string().min(1, 'Required'),
});

export const memberSchema = z.object({
  employee_id: z.string().min(1).max(50),
  username: z.string().min(3).max(100).regex(/^[a-z0-9._]+$/, 'lowercase letters, numbers, dot, underscore only'),
  full_name: z.string().min(1).max(200),
  email: z.string().email().max(200),
  gender: z.enum(['male', 'female', 'other']).optional(),
  phone: z.string().min(7).max(30).optional().or(z.literal('')),
  title: z.string().max(100).optional(),
  department_id: z.string().uuid(),
  role: z.enum(['viewer', 'user', 'manager', 'admin']).default('user'),
  initial_password: z.string().min(8).max(100).optional().or(z.literal('')),
  is_active: z.boolean().default(true),
});

export const roomSchema = z.object({
  code: z.string().min(1).max(20).regex(/^[A-Z][0-9]{3,4}$/, 'Format: <Block><Floor><Number>, e.g. C703'),
  name: z.string().min(1).max(200),
  description: z.string().max(1000).optional(),
  capacity: z.number().int().min(0).max(10000),
});

export const seatSchema = z.object({
  code: z.string().min(1).max(50),
  label: z.string().max(100).optional(),
  seat_type: z.enum(['single', 'double', 'double_facing', 'meeting_round', 'executive']),
  status: z.enum(['available', 'occupied', 'reserved', 'disabled', 'maintenance']),
  project_id: z.string().uuid().nullable().optional(),
  description: z.string().max(500).optional(),
  facility_ids: z.array(z.string().uuid()).default([]),
  max_secondary: z.number().int().min(0).max(100).nullable().optional(),
});

export const projectSchema = z.object({
  code: z.string().min(1).max(50),
  name: z.string().min(1).max(200),
  color: z.string().regex(/^#[0-9a-fA-F]{6}$/, 'Must be hex color #RRGGBB'),
  description: z.string().max(500).optional(),
  is_active: z.boolean().default(true),
});

export const changePasswordSchema = z.object({
  current_password: z.string().min(1),
  new_password: z.string()
    .min(8, 'Min 8 characters')
    .regex(/[A-Z]/, 'Must contain uppercase letter')
    .regex(/[0-9]/, 'Must contain number'),
  confirm_password: z.string(),
}).refine((d) => d.new_password === d.confirm_password, {
  message: 'Passwords do not match',
  path: ['confirm_password'],
});

export const secondaryAssignmentSchema = z.object({
  member_id: z.string().uuid(),
  hostname: z.string().min(1).max(200),
  ip_address: z.string().ip(),
  mac_address: z.string().regex(/^([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}$/, 'Invalid MAC address'),
  device_note: z.string().max(500).optional(),
  start_date: z.string().date().optional(),
  end_date: z.string().date().optional(),
});
```

### 19.2 Backend (Pydantic)

Mirror the same rules in Pydantic schemas under `app/schemas/`. Pydantic validation is the source of truth — frontend Zod is a UX layer only.

---

## 20. ERROR RESPONSE FORMAT

### 20.1 Standard Envelope

All error responses follow this shape:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": [
      { "field": "email", "message": "Email is required" }
    ]
  }
}
```

### 20.2 Standard Error Codes

| HTTP | Code | Use case |
|---|---|---|
| 400 | `VALIDATION_ERROR` | Request body fails validation |
| 401 | `INVALID_CREDENTIALS` | Login failed |
| 401 | `TOKEN_EXPIRED` | Access token expired |
| 401 | `TOKEN_INVALID` | Malformed or blacklisted token |
| 403 | `FORBIDDEN` | Authenticated but lacks role |
| 404 | `NOT_FOUND` | Entity not found |
| 409 | `CONFLICT` | Unique constraint violation |
| 409 | `ROOM_LOCKED` | Cannot edit, room is locked |
| 409 | `SEAT_ALREADY_ASSIGNED` | Primary seat conflict |
| 422 | `BUSINESS_RULE_VIOLATION` | E.g. max secondary slots exceeded |
| 500 | `INTERNAL_ERROR` | Unexpected server error |

### 20.3 FastAPI Exception Handler

```python
# app/main.py
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

class AppError(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400, details: list = None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or []

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.message, "details": exc.details}},
    )

@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    details = [
        {"field": ".".join(str(x) for x in e["loc"][1:]), "message": e["msg"]}
        for e in exc.errors()
    ]
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": details,
            }
        },
    )
```

### 20.4 Frontend Error Handling

```typescript
// src/lib/error-handler.ts
import { toast } from 'sonner';
import { AxiosError } from 'axios';

interface ApiError {
  error: { code: string; message: string; details?: Array<{ field: string; message: string }> };
}

export function handleApiError(error: unknown, fallback = 'Something went wrong') {
  if (error instanceof AxiosError && error.response?.data) {
    const apiError = error.response.data as ApiError;
    toast.error(apiError.error.message || fallback);
    return apiError;
  }
  toast.error(fallback);
  return null;
}
```

---

## 21. SEED DATA

### 21.1 Initial Admin Account

Created via Alembic data migration on first deploy:

```python
# alembic/versions/xxx_seed_initial_admin.py

def upgrade():
    # 1. Default department
    op.execute("""
        INSERT INTO departments (id, code, name, description)
        VALUES (gen_random_uuid(), 'SYS', 'System', 'System default department')
    """)

    # 2. Default member (admin)
    op.execute("""
        INSERT INTO members (id, employee_id, username, full_name, email, gender, department_id, is_active)
        SELECT gen_random_uuid(), 'EMP00001', 'admin', 'System Administrator',
               'admin@company.local', 'other', id, TRUE
        FROM departments WHERE code = 'SYS'
    """)

    # 3. Admin account (password: ChangeMe@2026 — bcrypt hashed)
    op.execute("""
        INSERT INTO accounts (id, member_id, password_hash, role, is_active)
        SELECT gen_random_uuid(), m.id,
               '$2b$12$xxxxxxxxxxxxxxxxxxxxxxxxxx',  -- replace with actual bcrypt of "ChangeMe@2026"
               'admin', TRUE
        FROM members m WHERE m.username = 'admin'
    """)
```

**On first login, the system prompts admin to change password.**

### 21.2 Default Facilities

```python
DEFAULT_FACILITIES = [
    ("Monitor", "monitor", 1),
    ("Standing Desk", "armchair", 2),
    ("Near Window", "panels-top-left", 3),
    ("Near AC", "snowflake", 4),
    ("Near Door", "door-open", 5),
    ("Power Outlet", "plug", 6),
    ("LAN Port", "ethernet-port", 7),
    ("Locker", "lock", 8),
    ("Whiteboard", "presentation", 9),
    ("Phone", "phone", 10),
]
# Insert all with is_default=TRUE, is_active=TRUE
```

### 21.3 Sample Departments (Optional Dev Seed)

```python
DEV_DEPARTMENTS = [
    ("IT", "Information Technology"),
    ("DEV", "Development"),
    ("QA", "Quality Assurance"),
    ("HR", "Human Resources"),
    ("BA", "Business Analyst"),
    ("PM", "Project Management"),
]
```

---

## 22. PROJECT BOOTSTRAP COMMANDS

Claude Code should execute these commands in order:

### 22.1 Initial Setup

```bash
# Repo root
mkdir seat-management && cd seat-management
git init

# Create .env from example
cp .env.example .env
# Edit DB_PASSWORD and JWT_SECRET_KEY

# Backend scaffold
mkdir -p backend/app/{models,schemas,routers,services,utils}
mkdir -p backend/alembic/versions
touch backend/{Dockerfile,requirements.txt}
cd backend
python -m venv venv && source venv/bin/activate
pip install fastapi[all] uvicorn sqlalchemy[asyncio] asyncpg alembic \
            python-jose[cryptography] passlib[bcrypt] pydantic-settings \
            pandas openpyxl python-multipart redis pytest pytest-asyncio httpx
pip freeze > requirements.txt
alembic init alembic
cd ..

# Frontend scaffold
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install
npm install -D tailwindcss postcss autoprefixer @types/node
npm install react-router-dom@6 zustand @tanstack/react-query axios \
            react-hook-form @hookform/resolvers zod \
            konva react-konva use-image \
            lucide-react sonner date-fns clsx tailwind-merge \
            class-variance-authority
npx tailwindcss init -p
npx shadcn@latest init -d
# Add shadcn components:
npx shadcn@latest add button input label dialog sheet dropdown-menu \
            select table tabs toast tooltip avatar badge card \
            form checkbox radio-group separator skeleton textarea
cd ..

# Docker
docker-compose up -d db redis
cd backend && alembic upgrade head
docker-compose up
```

### 22.2 Development Workflow

```bash
# Backend
cd backend
uvicorn app.main:app --reload --port 8000
# Visit http://localhost:8000/docs for Swagger UI

# Frontend
cd frontend
npm run dev
# Visit http://localhost:3000

# Run migrations after model change
cd backend
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

### 22.3 Initial Login

After first deploy:
1. Visit http://localhost
2. Login with `admin / ChangeMe@2026`
3. Profile → Change password (forced)
4. Admin → Departments → Create your real departments
5. Admin → Members → Import CSV (use template)
6. Admin → Rooms → Create first room → Design floor plan
7. Admin → Projects → Add projects with colors

---

## 23. CLAUDE CODE AGENT — IMPLEMENTATION ORDER

This is the authoritative build order. Each step compiles and runs before moving on.

### Sprint 1: Foundation (Day 1)
1. `docker-compose.yml`, `.env.example`, `nginx.conf`
2. Backend skeleton: `main.py`, `config.py`, `database.py`, `dependencies.py`
3. All SQLAlchemy models from Section 4
4. Initial Alembic migration + seed (Section 21)
5. Verify DB up, models created, admin seeded
6. Frontend scaffold: Vite + Tailwind config + shadcn init
7. Tailwind config with design tokens from Section 7.2
8. AppShell layout (Sidebar + Topbar empty stubs)

### Sprint 2: Auth + Profile (Day 2)
1. Backend: `auth_service.py`, `/auth` router (login/logout/refresh/me)
2. Frontend: `LoginPage`, `authStore`, axios interceptor, `RequireAuth`
3. Frontend: Topbar with avatar dropdown (logout)
4. Profile page (read-only first), then edit + change password
5. End-to-end test: login → see profile → logout

### Sprint 3: Member Management (Day 3-4)
1. Backend: `/departments` CRUD, `/members` CRUD, `/accounts` CRUD
2. Backend: `/members/import` (preview + execute)
3. Frontend: `DepartmentsPage`, `MemberListPage`, member add/edit Sheet
4. Frontend: CSV import modal (3-step flow)
5. Frontend: `AccountsPage` (role management)

### Sprint 4: Projects + Facilities (Day 5)
1. Backend: `/projects` CRUD, `/facilities` CRUD
2. Frontend: `ProjectsPage`, `FacilitiesPage`

### Sprint 5: Rooms + Seats (basic) (Day 6-7)
1. Backend: `/rooms` CRUD (no layout yet), `/seats` CRUD
2. Backend: Room status workflow (`/submit`, `/approve`, `/publish`, `/lock`)
3. Frontend: `RoomListPage` with status tabs
4. Frontend: Room create modal
5. Frontend: `RoomEditorPage` stub (placeholder canvas)
6. Frontend: `RoomViewPage` stub

### Sprint 6: Floor Plan Editor (Day 8-10)
1. Editor canvas: react-konva Stage + Layers
2. Drag-drop room elements (door, window, pillar, etc.)
3. Drag-drop seat shapes (all 5 types)
4. Transformer for resize/rotate
5. Properties panel binding
6. Undo/redo via Zustand history
7. Auto-save layout to API
8. Seat sync logic (backend diff on save)

### Sprint 7: Viewer + Search (Day 11-12)
1. `RoomViewPage` with read-only Konva
2. Seat click → slide-in info panel
3. Project color rendering on seats
4. Search page (member → list)
5. Map navigation: `?highlight=seat_id` → pan + glow seat

### Sprint 8: Requests + Assignments (Day 13-14)
1. Backend: `/seat-requests` flow + `/assignments`
2. Frontend: `RequestsPage` (manager view + user view)
3. Frontend: "Register" button on seat panel
4. Frontend: Direct assign modal (manager/admin)
5. Secondary assignment form (hostname/IP/MAC/note)

### Sprint 9: Notifications + Audit (Day 15)
1. Backend: notification service with InApp channel
2. Backend: audit log decorator on all mutation endpoints
3. Frontend: notification bell in topbar
4. Frontend: `AuditLogPage` (admin)

### Sprint 10: Polish (Day 16-17)
1. Dashboard with metrics
2. Empty states across all pages
3. Loading skeletons
4. Mobile responsive pass
5. Final E2E smoke test

---

## 24. ACCEPTANCE CRITERIA SUMMARY

The system is ready for production handoff when:

- [ ] Admin can log in with seeded credentials and is forced to change password
- [ ] Admin can import members via CSV, see preview, fix errors, execute
- [ ] Admin can create a room, design layout with seats and elements
- [ ] Admin can submit → approve → publish a room (workflow)
- [ ] Manager sees pending requests and can approve/reject
- [ ] User can browse published rooms, see seat info, submit registration request
- [ ] User is notified when request is approved/rejected
- [ ] Search by member name returns clickable result that navigates to seat on map
- [ ] Secondary slot can be created with hostname/IP/MAC for asset tracking
- [ ] Profile page shows own assignments and pending requests
- [ ] All actions are audit-logged
- [ ] UI uses only Tailwind classes — no inline styles, no emoji
- [ ] System runs locally via `docker-compose up` with single command
- [ ] All forms have client + server validation
- [ ] Error responses follow standard envelope
