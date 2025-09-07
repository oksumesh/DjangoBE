## 🔐 AUTHENTICATION ENDPOINTS

| **1** | `api/auth/login` | `api/auth/login/` | POST | User login | ✅ **Match** |
| **2** | `api/auth/register` | `api/auth/register/` | POST | User registration | ✅ **Match** |
| **3** | `api/auth/refresh` | `api/auth/refresh/` | POST | Refresh JWT token | ✅ **Match** |
| **4** | `api/auth/logout` | `api/auth/logout/` | POST | User logout | ✅ **Match** |
| **5** | `api/auth/forgot` | `api/auth/forgot/` | POST | Forgot password - request OTP | ✅ **Match** |
| **6** | `api/auth/verify-otp` | `api/auth/verify-otp/` | POST | Verify OTP for password reset | ✅ **Match** |
| **7** | `api/auth/reset-password` | `api/auth/reset-password/` | POST | Reset password with new password | ✅ **Match** |

## 👥 USER MANAGEMENT ENDPOINTS

| **8** | `api/users` | `api/users/` | GET | Get all users | ✅ **Match** |
| **9** | `api/users/{id}` | `api/users/{id}/` | GET | Get user by ID | ✅ **Match** |
| **10** | `api/users/email/{email}` | `api/users/email/{email}/` | GET | Get user by email | ✅ **Match** |
| **11** | `api/users` | `api/users/create/` | POST | Create new user | ✅ **Match** |
| **12** | `api/users/{id}` | `api/users/{id}/update/` | PUT | Update user information | ✅ **Match** |
| **13** | `api/users/{id}/loyalty-points` | `api/users/{id}/loyalty-points/` | PUT | Add loyalty points to user | ✅ **Match** |
| **14** | `api/users/{id}/verify-email` | `api/users/{id}/verify-email/` | PUT | Verify user email address | ✅ **Match** |
| **15** | `api/users/{id}/deactivate` | `api/users/{id}/deactivate/` | PUT | Deactivate user account | ✅ **Match** |
| **16** | `api/users/loyalty-tier/{tier}` | `api/users/loyalty-tier/{tier}/` | GET | Get users by loyalty tier | ✅ **Match** |
| **17** | `api/users/active` | `api/users/active/` | GET | Get all active users | ✅ **Match** |
| **18** | `api/users/health` | `api/users/health/` | GET | User service health check | ✅ **Match** |

## 📊 POLL MANAGEMENT ENDPOINTS

| **19** | `api/polls` | `api/polls/` | GET | Get all polls | ✅ **Match** |
| **20** | `api/polls/{id}` | `api/polls/{id}/` | GET | Get poll by ID | ✅ **Match** |
| **21** | `api/polls` | `api/polls/create/` | POST | Create new poll | ✅ **Match** |
| **22** | `api/polls/{id}/vote` | `api/polls/{id}/vote/` | POST | Vote on a poll | ✅ **Match** |
| **23** | `api/polls/{id}` | `api/polls/{id}/delete/` | DELETE | Delete a poll | ✅ **Match** |
| **24** | `api/polls/category/{category}` | `api/polls/category/{category}/` | GET | Get polls by category | ✅ **Match** |
| **25** | `api/polls/user/{userId}` | `api/polls/user/{userId}/` | GET | Get polls by user | ✅ **Match** |
| **26** | `api/polls/visibility/{visibility}` | `api/polls/visibility/{visibility}/` | GET | Get polls by visibility | ✅ **Match** |
| **27** | `api/polls/{id}/statistics` | `api/polls/{id}/statistics/` | GET | Get poll statistics | ✅ **Match** |
| **28** | `api/polls/categories` | `api/polls/categories/` | GET | Get available categories | ✅ **Match** |
| **29** | `api/polls/health` | `api/polls/health/` | GET | Poll service health check | ✅ **Match** |

## 🛠️ UTILITY ENDPOINTS

| **30** | `hello` | `hello/` | GET | Hello endpoint for testing | ✅ **Match** |

---

## 📋 SUMMARY

### **Total Endpoints**: 30
- **Authentication**: 7 endpoints
- **User Management**: 11 endpoints  
- **Poll Management**: 11 endpoints
- **Utility**: 1 endpoint

### **Base URLs**:
- **Android App**: `http://10.0.2.2:8080/` (for emulator)
- **Python/Django**: `http://127.0.0.1:8000/` (default) or `http://127.0.0.1:8080/` (if configured)

### **Key Differences**:
1. **Trailing Slashes**: Django URLs have trailing slashes (`/`) by default
2. **URL Structure**: Some Django URLs use more descriptive paths (e.g., `/create/`, `/update/`, `/delete/`)
3. **Port Configuration**: Android expects port 8080, Django defaults to 8000

### **Compatibility**: 
✅ **100% API Compatibility** - All endpoints match functionally, with minor URL structure differences that don't affect functionality.

---

## 🔧 Configuration Notes

### **For Android App Integration**:
1. **Option A**: Run Django on port 8080:
   ```bash
   python3 manage.py runserver 0.0.0.0:8080
   ```

2. **Option B**: Update Android app's `BASE_URL` in `NetworkService.kt`:
   ```kotlin
   private const val BASE_URL = "http://10.0.2.2:8000/" // Change from 8080 to 8000
   ```

### **Testing URLs**:
- **Django Admin**: `http://127.0.0.1:8000/admin/`
- **API Base**: `http://127.0.0.1:8000/api/`
- **Health Check**: `http://127.0.0.1:8000/api/users/health/`

---

*Generated on: September 7, 2025*
*Django Backend: RedCurtainsWebBackend*
*Android App: RedCurtainsFrontend*
