# 🐾 Animal Shelter API

A **FastAPI-based multi-tenant backend** for managing animal shelters, adoptions, staff, and analytics.  
This MVP supports both **public endpoints** (for adopters) and **internal/ endpoints** (for organizations).

---

## 🚀 Features

### 👥 Multi-Tenant Architecture
- Each **organization** (animal welfare NGO) can manage multiple **shelters**.
- Role-based access control with `org_admin`, `staff`, and `adopter` roles.

### 🐕 Animal Management
- Create, update, and list animals within shelters.
- Track vaccination and medical records.
- Expose public endpoints for available animals.

### 💌 Adoption Requests
- Users can submit and track adoption requests.
- Admins can review and approve/reject requests.
- Analytics provide adoption success rates and top adopted breeds.

### 📊 Analytics
- Shelter-level adoption success rates.
- Top 3 adopted breeds per organization.

## 🏗️ Project Structure
app/
├── api/routers/ # Routers (users, animals, shelters, analytics, etc.)
├── core/ # Security, config, dependencies
├── schemas/ # SQLModel + Pydantic models
├── main.py # App entry point
└── alembic/ # DB migrations

## 🔑 Roles and Access Control
| Role          | Permissions                                                                 |
|---------------|-----------------------------------------------------------------------------|
| `org_admin`   | Manage organization, shelters, staff, and view analytics                    |
| `staff`       | Manage animals, medical records, and vaccinations within assigned shelters  |
| `adopter`     | View animals and submit adoption requests   

## 🧭 API Overview

### **Public Routes**
Accessible to everyone (no authentication).

#### `GET /api/public/animals/`
List available animals with filters (breed, name, sterilized) and pagination.

#### `GET /api/public/animals/{animal_id}`
Get detailed public profile for a specific animal including medical & vaccination records.

### **Internal (Authenticated) Routes**

#### `GET /api/internal/analytics/`
Requires role: `org_admin`  
Returns adoption success rates per shelter and top 3 adopted breeds for the organization.

Example response:
```json
{
  "success_rate_per_shelter": [
    {"shelter_name": "Happy Paws", "success_rate": 75.0}
  ],
  "top_breeds": [
    {"breed": "Labrador", "adopted_count": 12}
  ]
}
```
#### 🧪 Setup Instructions
1️- Clone the repository
git clone https://github.com/Waadhmd/pawbase-api.git
2️- Create and configure .env
 DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/pawbase
 SECRET_KEY=your_secret_key
3️- Install dependencies
4️- Run database migrations
 alembic upgrade head
5️- Start the application
 uvicorn app.main:app --reload

####  Future Roadmap (v2)
| Feature                | Description                                                  |
| ---------------------- | ------------------------------------------------------------ |
| 🐳 **Dockerization**   | Containerize backend for easier scaling & deployment         |
| ☁️ **AWS Integration** | Deploy on ECS/Fargate, use RDS for production DB             |
| 📊 **React Dashboard** | Admin/staff dashboards with data visualization               |
| 🤖 **AI Integration**  | Automatic animal photo tagging, medical report summarization |
| 📬 **Notifications**   | Email or SMS adoption updates                                |
| 🧩 **API Gateway**     | Introduce rate limiting, logging, and API key management     |








