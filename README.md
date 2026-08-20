# AutoPlan Backend 🚀

AutoPlan is an advanced AI-powered architectural platform designed for automated floorplan generation and project management. This repository contains the FastAPI-based backend that orchestrates user workflows, database management, and deep learning model integrations.

## 🌟 Key Features

- **User Authentication & Management**: 
  - Secure JWT-based authentication.
  - Google OAuth2 integration for seamless login.
  - OTP-based password recovery.
  - Tiered subscription and credit system (40 free credits on signup).
- **AI-Powered Floorplan Generation**:
  - Integration with **Graph2Plan** for graph-based layouts.
  - **CSP (Constraint Satisfaction Problem)** engine for optimized floorplans.
  - **DiffPlanner** integration for generative refinements.
- **Project Management**:
  - CRUD operations for architectural projects.
  - Flexible data storage using PostgreSQL **JSONB**.
  - Cloud-based image storage via **ImageKit**.
- **Asynchronous Workflows**:
  - Background tasks for email notifications (OTP, Support requests).
  - High-performance asynchronous API endpoints.

## 🛠️ Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **ORM**: [SQLAlchemy 2.0](https://www.sqlalchemy.org/)
- **Database**: [PostgreSQL](https://www.postgresql.org/)
- **AI/ML**: PyTorch, OpenCV, Shapely, Scipy
- **Cloud Storage**: ImageKit.io
- **Mailing**: FastAPI-Mail, Resend/Brevo APIs
- **Deployment**: Docker ready

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL
- Docker (optional)

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/AutoPlan-Backend.git
   cd AutoPlan-Backend
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**:
   Create a `.env` file in the root directory and add the following:
   ```env
   DB_CONNECTION=postgresql://user:password@localhost:5432/autoplan
   SECRET_KEY=your_super_secret_key
   ALGORITHM=HS256
   EXPIRE_MINUTES=60
   
   # Optional: Integrations
   GOOGLE_CLIENT_ID=...
   IMAGEKIT_PUBLIC_KEY=...
   IMAGEKIT_PRIVATE_KEY=...
   IMAGEKIT_URL_ENDPOINT=...
   ```

5. **Initialize Database**:
   ```bash
   python create_tables.py
   ```

6. **Run the application**:
   ```bash
   uvicorn main:app --reload
   ```

## 📂 Project Structure

```text
├── services/           # Core business logic & controllers
├── schema/             # Pydantic models for request/response validation
├── Graph2Plan/         # AI Model specific logic
├── diffplanner/        # Generative refinement logic
├── tests/              # Unit and integration tests
├── main.py             # Application entry point & router wiring
├── Dockerfile          # Containerization config
└── requirements.txt    # Project dependencies
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📧 Contact

For support or inquiries, please contact [autoplan3d@gmail.com](mailto:autoplan3d@gmail.com).
