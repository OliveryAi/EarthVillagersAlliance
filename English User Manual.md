# Earth Citizens Supervision Alliance - User Guide (English)

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Quick Start](#2-quick-start)
3. [Feature Modules](#3-feature-modules)
4. [API Documentation](#4-api-documentation)
5. [FAQ & Troubleshooting](#5-faq--troubleshooting)

---

## 1. System Overview

### 1.1 Project Introduction

**Earth Citizens Supervision Alliance** is a netizen-driven platform designed to monitor and document employment discrimination and labor exploitation practices. Through anonymous voting with evidence submission, the system creates transparent leaderboards that promote social accountability for corporate workplace environments.

### 1.2 Four Observation Categories

| Category | Code Name | Description |
|----------|-----------|-------------|
| Age Discrimination (35+ Employment) | `age_discrimination` | Records enterprises with age-based hiring discrimination |
| Gender Discrimination | `gender_discrimination` | Records enterprises with gender-based employment discrimination |
| Workplace PUA Despotism | `pua_despotism` | Records enterprises with psychological manipulation and authoritarian management |
| Overwork Exploitation | `overwork_exploitation` | Records enterprises with forced overtime and unpaid labor practices |

### 1.3 Core Principles

- **Anonymous Voting**: All voter information is strictly confidential; only statistical results are published
- **Evidence Priority**: Users are encouraged to upload screenshots/documents as supporting evidence
- **Anti-Fraud Mechanisms**: Limited to 3 votes per user/day, one vote per company/category combination
- **Real & Reliable**: Device fingerprinting and IP rate limiting ensure data authenticity

---

## 2. Quick Start

### 2.1 Web Access Instructions

#### Step 1: Register Account

1. Visit the system (local: `http://127.0.0.1:8000/`)
2. Click "Register" button
3. Enter your 11-digit Chinese mobile number
4. Request verification code (in test mode, it prints to console)
5. Set password (min 8 chars, must include letters and numbers)
6. Submit to complete registration

**Important Notes**:
- New registrations require admin approval
- Each phone number can only register once

#### Step 2: Login System

1. Enter your mobile number and password on the login page
2. Click "Login"
3. After first successful login, you receive a Token for subsequent API calls (Web handles this automatically)

#### Step 3: Submit Vote

1. After logging in, go to "Vote" section
2. Select target category
3. Search company name and select from results
4. Fill voting reason (max 2000 characters, recommended)
5. Upload evidence material (optional but highly encouraged):
   - Supported formats: Images (JPG/PNG), Documents (PDF/DOCX)
   - Max file size: 5MB
6. Confirm submission

**After Voting**:
- Remaining votes for today will be displayed
- Cannot vote again on same company/category combination
- Can upload evidence, but each vote allows only one upload

#### Step 4: View Leaderboards

1. After logging in, visit "Leaderboard" section
2. Choose to view:
   - **All Categories Overview**: See Top N enterprises across all categories
   - **Specific Category Details**: Click on specific category for detailed ranking

**Leaderboard Display Content**:
- Rank (sorted by total votes from highest)
- Company name, industry, and city location
- Vote count and vote rate (%)

---

## 3. Feature Modules

### 3.1 User Authentication System

#### Phone Registration & Login API

```bash
# Request verification code during registration
POST /api/auth/register/
Content-Type: application/json

{
    "phone": "13800138000",      # 11-digit Chinese mobile number
    "code": "123456",            # SMS verification code (console output in test mode)
    "password": "SecurePass123!" # Password: letters + numbers, minimum 8 characters
}

# Login to get authentication token
POST /api/auth/login/
Content-Type: application/json

{
    "username": "13800138000",   # Your registered phone number
    "password": "SecurePass123!" # Your password
}
```

**Token**:
- Returned after successful login, valid for 24 hours
- Required for all subsequent API calls requiring authentication
- Recommended to store safely locally (Web: localStorage, Mobile: Keychain)

#### Administrator Account

Pre-configured admin credentials: `11011912000 / 110119120`  
Purpose: View backend data, manage leaderboard entries

---

### 3.2 Voting Process Details

#### Enterprise Search API

```bash
GET /api/vote/companies/search/?q=Huawei

# Parameters:
- q: Search keyword (supports fuzzy matching, e.g., "Tencent" finds "Tencent Tech")
- Returns up to 50 results
```

**Search Result Format**:
```json
[
    {
        "id": 11,
        "name": "Huawei Technologies",
        "industry": "Telecommunications Equipment",
        "city": "Shenzhen"
    }
]
```

#### Detailed Voting Submission Steps

1. **Preparation Phase**:
   - Confirm target enterprise exists in system (contact admin if not found)
   - Gather evidence materials (recommended: chat screenshots, overtime notifications, pay slips, etc.)

2. **Form Filling**:
   ```json
   POST /api/vote/submit/

   {
       "category": "age_discrimination",      # Voting category (required)
       "company_id": 13,                      # Enterprise ID (obtained from search results, required)
       "reason": "The enterprise requires all job applicants under 35 years old"  # Reason description (optional but recommended)
   }
   ```

3. **Post-Submission Feedback**:
   - Success: Returns `vote_id` and remaining votes count
   - Failure possible reasons:
     - Daily vote limit reached (429 Too Many Requests)
     - Already voted on this company for this category (400 Bad Request)
     - Company not found / Invalid category

---

### 3.3 Evidence Upload Details

#### Supported File Formats

| Type | Extensions | MIME Type | Description |
|------|------------|-----------|-------------|
| Images | .jpg, .jpeg, .png | image/jpeg / image/png | Recommended for screenshots (chat logs, notifications) |
| Documents | .pdf | application/pdf | PDF scans or exported emails |
| Documents | .docx | application/vnd.openxmlformats-officedocument.wordprocessingml.document | Word documents |

#### Upload Process

1. **Obtain Vote ID**:
   - Returned immediately after successful vote submission as `vote_id`
   - Or view via "My Votes" page (future feature)

2. **Call Upload API**:
   ```python
   import requests

   s = requests.Session()
   s.headers['Authorization'] = f'Token {your_token}'

   evidence_resp = s.post(
       'http://127.0.0.1:8000/api/vote/evidence/upload/',
       data={'vote_id': 5},                      # Corresponding vote ID (required)
       files={
           'evidence_file': (                   # Required field name for file upload
               'proof.pdf',                     # Custom filename (up to you)
               open('evidence_content.pdf', 'rb'),  # Actual file content
               'application/pdf'                # MIME type
           )
       }
   )
   ```

3. **Result Verification**:
   - Success: Returns `file_url` and upload timestamp
   - Failure reasons:
     - Evidence already exists for this vote (cannot submit duplicate)
     - File format not supported
     - File too large (>5MB)

#### Evidence Management Recommendations

- **Naming Convention**: Use descriptive filenames, e.g., "2024-03-15_OvertimeNotice.png"
- **Content Requirements**: Ensure screenshots/documents contain key information (timestamp, company name, event details)
- **Privacy Protection**: Blurring/redacting personally identifiable information before upload

---

### 3.4 Leaderboard Query Details

#### Query All Categories Overview

```bash
GET /api/vote/ranking/

# Returns list format:
[
    {
        "category": "age_discrimination",
        "company_name": "某科技有限公司",
        "total_votes": 10,
        "vote_rate": 25.00,
        "industry": "Technology",
        "city": "Shenzhen"
    }
]
```

#### Query Specific Category Details

```bash
GET /api/vote/ranking/<category>

# Example:
GET /api/vote/ranking/age_discrimination/

# Return format (with rankings):
{
    "category": "age_discrimination",
    "category_name": "35+ Age Discrimination Observation List",
    "rankings": [
        {
            "rank": 1,                           # Rank position (starts from 1)
            "company_name": "某科技有限公司",
            "total_votes": 10,
            "vote_rate": 25.00,                   # Vote rate percentage
            "industry": "Technology",
            "city": "Shenzhen"
        }
    ]
}
```

#### Leaderboard Sorting Rules

- Sorted by total votes `total_votes` from **highest to lowest**
- If vote counts are equal, sorted by vote rate `vote_rate` from **highest to lowest**
- Currently displays Top 20 per category (expandable in future)

---

## 4. API Documentation

### 4.1 User Authentication APIs

#### POST `/api/auth/register/` - Register with Phone & Verification Code

**Request Headers**: None required for registration

**Request Body**:
```json
{
    "phone": "13800138000",      # Required: 11-digit Chinese mobile number
    "code": "123456",            # Required: 6-digit SMS verification code
    "password": "SecurePass123!" # Required: Min 8 characters with letters + numbers
}
```

**Response (201 Created)**:
```json
{
    "message": "Registration successful",
    "user_id": 5,
    "username": "13800138000"
}
```

#### POST `/api/auth/login/` - Login to Get Token

**Request Body**:
```json
{
    "username": "testuser",       # Your registered phone number or admin account
    "password": "TestPass123!"    # Your password
}
```

**Response (200 OK)**:
```json
{
    "message": "Login successful",
    "user_id": 4,
    "is_admin": false,
    "token": "abcdef1234567890..." # Use this token for authenticated requests
}
```

**Admin Login**:
- Username: `11011912000`
- Password: `110119120`

---

### 4.2 Voting APIs

#### POST `/api/vote/submit/` - Submit Vote

**Required Headers**:
```
Authorization: Token <your_token>
Content-Type: application/json
```

**Request Body**:
```json
{
    "category": "age_discrimination",
    "company_id": 13,
    "reason": "This enterprise exhibits age discrimination behavior in hiring"
}
```

**Valid Category Values**:
- `age_discrimination`: 35+ Age Discrimination Observation List
- `gender_discrimination`: Gender Discrimination Observation List
- `pua_despotism`: Workplace PUA Despotism Observation List
- `overwork_exploitation`: Overwork Exploitation Observation List

**Response (201 Created)**:
```json
{
    "message": "Vote submitted successfully",
    "vote_id": 6,
    "remaining_today": 0            # Remaining votes for today
}
```

#### GET `/api/vote/ranking/<category>/` - Get Category Leaderboard

**Example URL**: `GET /api/vote/ranking/age_discrimination/`

**Response (200 OK)**:
```json
{
    "category": "age_discrimination",
    "category_name": "35+ Age Discrimination Observation List",
    "rankings": [
        {
            "rank": 1,
            "company_name": "某科技有限公司",
            "total_votes": 10,
            "vote_rate": 25.00,
            "industry": "Technology",
            "city": "Shenzhen"
        }
    ]
}
```

#### GET `/api/vote/companies/search/?q=华为` - Search Enterprises

**Query Parameters**:
- `q`: Search keyword (required)

**Response (200 OK)**:
```json
[
    {
        "id": 11,
        "name": "华为技术",
        "industry": "通信设备",
        "city": "深圳"
    }
]
```

---

### 4.3 Evidence Upload API

#### POST `/api/vote/evidence/upload/` - Upload Supporting Evidence

**Required Headers**:
```
Authorization: Token <your_token>
```

**FormData Fields**:
- `vote_id`: Integer (vote ID from successful submission, required)
- `evidence_file`: File upload (image/PDF/DOCX only, max 5MB)

**Response (201 Created)**:
```json
{
    "message": "Evidence uploaded successfully",
    "vote_id": 6,
    "file_url": "/media/evidence/6/proof.pdf",
    "file_type": "document"        # 'image' or 'document'
}
```

---

## 5. FAQ & Troubleshooting

### Q1: Daily vote limit reached? What can I do?

**A**:
- **Rule**: Same user can cast max 3 votes per day (across all categories)
- **Solution**: Continue using tomorrow after midnight, or register new account (please follow fairness principles)

**Technical Details**:
```python
# IP + device fingerprint dual verification prevents vote fraud
daily_votes = Vote.objects.filter(
    voter_id=user_id,
    category=category,
    ip_address__startswith=request_ip,
    created_at__gte=today_midnight
).count()
```

### Q2: Already voted on a company for this category - can I modify or delete?

**A**:
- Current version does NOT support modifying or deleting existing votes
- If corrections are needed, contact administrator (`11011912000 / 110119120`) for manual handling

### Q3: Evidence upload fails? What should I check?

**A**:
Verify these conditions:
1. **File Format**: Only `.jpg`, `.jpeg`, `.png`, `.pdf`, `.docx` supported
2. **File Size**: Not exceeding 5MB (recommended <2MB for better compatibility)
3. **Duplicate Upload**: Each vote allows only one evidence submission

**Debug Commands**:
```bash
# Check file type
file proof.pdf

# View file size
ls -lh proof.pdf
```

### Q4: How do I confirm successful vote submission?

**A**: 
Successful response example:
```json
{
    "message": "Vote submitted successfully",
    "vote_id": 6,
    "remaining_today": 0          # Remaining votes for today
}
```

If error code `201` returned, check:
- Company exists (try searching again to confirm)
- Category is valid (see Section 4.2 Voting Process Details)

### Q5: How is data security guaranteed?

**A**:
- **Phone Number Encryption**: Fernet symmetric encryption algorithm, private key read from environment variable
- **Token Authentication**: Each API call requires Token, valid for 24 hours
- **Anti-Fraud Mechanisms**: IP + device fingerprint dual verification
- **Evidence Material Security**: Files stored independently in `media/evidence/` directory

### Q6: How can I manage backend data as administrator?

**A**:
1. Access `/admin/` (requires pre-configured admin account)
2. View/edit enterprise list
3. Audit user-submitted data
4. Check leaderboard ranking update status

---

## Appendix A: Complete Test Script Examples

### A.1 Full End-to-End Test Script (Python Requests)

```python
import requests

BASE_URL = 'http://127.0.0.1:8000'

def main():
    # Step 1: Login and get token
    login_resp = requests.post(
        f'{BASE_URL}/api/auth/login/',
        json={'username': 'testuser', 'password': 'TestPass123!'}
    )
    
    if login_resp.status_code != 200:
        print(f'Login failed: {login_resp.text}')
        return
    
    token = login_resp.json()['token']
    s = requests.Session()
    s.headers['Authorization'] = f'Token {token}'
    
    # Step 2: Search for enterprise
    comp_resp = s.get(
        f'{BASE_URL}/api/vote/companies/search/',
        params={'q': 'Huawei'}
    )
    companies = comp_resp.json()
    print(f'Found companies: {[c["name"] for c in companies]}')
    
    # Step 3: Submit vote (if company found)
    if companies:
        vote_resp = s.post(
            f'{BASE_URL}/api/vote/submit/',
            data={
                'category': 'age_discrimination',
                'company_id': companies[0]['id'],
                'reason': 'This enterprise exhibits age discrimination behavior'
            }
        )
        
        if vote_resp.status_code == 201:
            print(f"Vote submitted! ID={vote_resp.json()['vote_id']}")
            
            # Step 4: Upload evidence (if vote was successful)
            evidence_resp = s.post(
                f'{BASE_URL}/api/vote/evidence/upload/',
                data={'vote_id': vote_resp.json()['vote_id']},
                files={
                    'evidence_file': (
                        'proof.pdf',
                        b'%PDF-1.4\nEvidence Content Here',
                        'application/pdf'
                    )
                }
            )
            
            if evidence_resp.status_code == 201:
                print(f"Evidence uploaded successfully!")
                print(f"File URL: {evidence_resp.json()['file_url']}")
        else:
            print(f"Vote submission failed: {vote_resp.text}")

if __name__ == '__main__':
    main()
```

### A.2 cURL Command-Line Examples

```bash
# Login and save token to environment variable
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"TestPass123!"}' | \
  python -c "import sys,json;print(json.load(sys.stdin)['token'])")

echo "Your Token: $TOKEN"

# Search for enterprises
curl -s http://127.0.0.1:8000/api/vote/companies/search/?q=Huawei \
  | python -m json.tool

# Submit vote (assuming enterprise ID=11)
curl -s -X POST http://127.0.0.1:8000/api/vote/submit/ \
  -H "Authorization: Token $TOKEN" \
  -d "category=age_discrimination&company_id=11&reason=This enterprise exhibits age discrimination behavior"

# Upload evidence (requires vote_id from previous step)
curl -s -X POST http://127.0.0.1:8000/api/vote/evidence/upload/ \
  -H "Authorization: Token $TOKEN" \
  -F "vote_id=5" \
  -F "evidence_file=@proof.pdf"

# View leaderboard for specific category
curl -s http://127.0.0.1:8000/api/vote/ranking/age_discrimination/ | python -m json.tool
```

### A.3 JavaScript (Fetch API) Example

```javascript
const BASE_URL = 'http://127.0.0.1:8000';

// Login and get token
async function login() {
    const resp = await fetch(`${BASE_URL}/api/auth/login/`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({username: 'testuser', password: 'TestPass123!'})
    });
    
    if (!resp.ok) throw new Error('Login failed');
    const data = await resp.json();
    return data.token;
}

// Search enterprises
async function searchCompanies(keyword, token) {
    const resp = await fetch(
        `${BASE_URL}/api/vote/companies/search/?q=${keyword}`,
        {headers: {'Authorization': `Token ${token}`}}
    );
    return resp.json();
}

// Submit vote
async function submitVote(token, category, companyId, reason) {
    const resp = await fetch(`${BASE_URL}/api/vote/submit/`, {
        method: 'POST',
        headers: {'Authorization': `Token ${token}`, 'Content-Type': 'application/json'},
        body: JSON.stringify({category, company_id: companyId, reason})
    });
    return resp.json();
}

// Upload evidence
async function uploadEvidence(token, voteId, file) {
    const formData = new FormData();
    formData.append('vote_id', voteId);
    formData.append('evidence_file', file);
    
    const resp = await fetch(`${BASE_URL}/api/vote/evidence/upload/`, {
        method: 'POST',
        headers: {'Authorization': `Token ${token}`},
        body: formData
    });
    return resp.json();
}

// Complete workflow
async function main() {
    try {
        const token = await login();
        console.log('Your Token:', token);
        
        const companies = await searchCompanies('Huawei', token);
        console.log('Found Companies:', companies);
        
        if (companies.length > 0) {
            const voteResult = await submitVote(
                token,
                'age_discrimination',
                companies[0].id,
                'This enterprise exhibits age discrimination behavior'
            );
            console.log('Vote Result:', voteResult);
            
            // Upload evidence (requires frontend file input)
            // const evidence = await uploadEvidence(token, voteResult.vote_id, fileInput.files[0]);
        }
    } catch (err) {
        console.error(err);
    }
}

main();
```

---

## Appendix B: Error Codes Quick Reference

| HTTP Status | Description | Possible Cause | Solution |
|-------------|-------------|----------------|----------|
| 200 OK | Success | API returned normally | No action needed |
| 201 Created | Resource created successfully | Vote/evidence uploaded | Save returned data |
| 400 Bad Request | Request error | Missing params, invalid format, duplicate submission | Check input parameters |
| 401 Unauthorized | Unauthenticated | Token missing or invalid | Re-login to get new token |
| 403 Forbidden | Permission denied | Non-voter trying to upload others' evidence | Use the creator's account |
| 429 Too Many Requests | Rate limit exceeded | User exceeds 3 votes/day | Use again tomorrow |

---

**Document Version**: v1.0  
**Last Updated**: April 6, 2026  
**Technical Support**: Via GitHub Issues or contact administrator at `11011912000`
