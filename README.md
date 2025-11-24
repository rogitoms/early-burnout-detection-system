# Burnout Detection System

A comprehensive full-stack application for detecting and managing workplace burnout through AI-powered assessments and personalized recommendations.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![React](https://img.shields.io/badge/react-18+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)

## Features

### Authentication & Security
- **Two-Factor Authentication (2FA)** with email verification
- **Role-based access control** (Admin/Employee)
- **Secure session management**
- **Password reset functionality**

### AI-Powered Assessment
- **Machine Learning Model** using DistilBERT for burnout prediction
- **Conversational Chatbot** for natural assessment experience
- **Personalized Recommendations** via Groq LLM API
- **Real-time burnout scoring** and analysis

### User Management
- **Admin Dashboard** for employee management
- **Employee role assignment** and tracking
- **Assessment history** and progress monitoring
- **Department and employee ID** management

### Smart Chatbot
- **Progressive question flow** (6 key questions)
- **Context-aware responses**
- **Session persistence**
- **Assessment completion tracking**

## Tech Stack

### Backend
- **Django** with Django REST Framework
- **Django-OTP** for 2FA
- **SQLite** database (production-ready PostgreSQL compatible)
- **Transformers** (Hugging Face) for ML model
- **PyTorch** for model inference

### Frontend
- **React** with modern hooks
- **React Router** for navigation
- **Axios** for API communication
- **CSS3** with custom design system

### AI/ML
- **DistilBERT** base model for text classification
- **Custom neural network** architecture
- **Groq API** (Llama 3.1) for recommendations
- **Real-time text processing** and analysis

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Groq API key

### Backend Setup

```bash
# Clone repository
git clone <repository-url>
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver
```

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Environment Variables

Create `.env` file in backend directory:

```env
GROQ_API_KEY=your_groq_api_key_here
EMAIL_HOST_PASSWORD=your_email_app_password
```

## Project Structure

```
burnout-detection-system/
├── backend/                              
│   ├── api/                              
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── two_factor_serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── tests.py
│   │   └── migrations/
│
│   ├── chatbot/                          # Chatbot App
│   │   ├── __init__.py                   # Added (clean version)
│   │   ├── admin.py                      # Added (clean version)
│   │   ├── apps.py
│   │   ├── conversation_flow.py          # Uploaded file
│   │   ├── models.py                     # Uploaded file
│   │   ├── serializers.py                # Uploaded file
│   │   ├── views.py                      # Uploaded file
│   │   ├── urls.py                       # Uploaded file
│   │   └── tests.py
│
│   ├── ml_model/
│   │   ├── __init__.py
│   │   ├── apps.py
│   │   ├── model_architecture.py
│   │   ├── model_service.py
│   │   ├── data_processing.py
│   │   ├── prediction_utils.py
│   │   ├── training_pipeline.py
│   │   ├── llm_api_recommender.py
│   │   ├── assessment_logic.py
│   │   └── ultimate_burnout_model.pth
│   │
│   ├── backend/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   ├── asgi.py
│   │   └── middleware.py
│   │
│   ├── manage.py
│   ├── requirements.txt
│   └── db.sqlite3
│
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/
│   │   │   ├── App.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Dashboard.css
│   │   │   ├── Login.jsx
│   │   │   ├── Signup.jsx
│   │   │   ├── TwoFactorVerify.jsx
│   │   │   ├── PasswordResetRequest.jsx
│   │   │   ├── PasswordResetConfirm.jsx
│   │   │   ├── ProtectedRoute.jsx
│   │   │   ├── AuthRouteGuard.jsx
│   │   │   ├── AdminEmployeeManagement.jsx
│   │   │   └── chatbot/
│   │   │       ├──Chatbot.css
│   │   │       └── Chatbot.jsx
│   │   ├── contexts/
│   │   │   └── AuthContext.jsx
│   │   ├── services/
│   │   │   ├── api.js
│   │   │   ├── auth.js
│   │   │   └── chatbot.js
│   │   ├── hooks/
│   │   │   └── useChatbot.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   └── yarn.lock / package-lock.json
│
├── .gitignore
├── README.md
└── manage.py

```

## API Endpoints

### Authentication
- `POST /api/auth/signup/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `POST /api/auth/2fa/verify/` - 2FA verification

### Chatbot & Assessment
- `POST /chatbot/start-session/` - Start new assessment
- `POST /chatbot/submit-answer/` - Submit answer
- `GET /chatbot/history/` - Get assessment history
- `DELETE /chatbot/session/{id}/delete/` - Delete session

### Admin
- `GET /api/auth/admin/employees/` - List employees
- `POST /api/auth/admin/employees/create/` - Create employee
- `PUT /api/auth/admin/employees/{id}/update/` - Update employee
- `DELETE /api/auth/admin/employees/{id}/delete/` - Delete employee

## ML Model Details

### Architecture
- **Base Model**: DistilBERT (uncased)
- **Custom Head**: Multi-layer perceptron with GELU activation
- **Output**: Sigmoid activation for burnout probability (0-1)

### Training Features
- Text preprocessing and cleaning
- Strategic layer freezing for efficiency
- Advanced dropout for regularization
- Optimized for burnout-specific language patterns

## User Roles

### Employee
- Complete burnout assessments
- View personal assessment history
- Receive personalized recommendations
- Update profile information

### Admin
- Manage employee accounts
- View system analytics
- Monitor assessment completion
- Generate reports

## Security Features

- **2FA Enforcement**: All users require email verification
- **Session Management**: Secure cookie-based sessions
- **CSRF Protection**: Cross-site request forgery protection
- **CORS Configuration**: Controlled cross-origin requests
- **Password Validation**: Strong password requirements

## Assessment Flow

1. **Welcome** → Introduction and consent
2. **Q1-6** → Progressive questions about work experience
3. **ML Analysis** → Real-time burnout scoring
4. **LLM Recommendations** → Personalized advice generation
5. **Results** → Comprehensive report with actionable insights

## UI/UX Features

- **Responsive Design**: Mobile-first approach
- **Dark/Light Mode**: CSS variable support
- **Accessibility**: WCAG compliant components
- **Loading States**: Smooth user experience
- **Error Handling**: User-friendly error messages

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Check existing issues on GitHub
- Create new issue with detailed description
- Contact development team

---

**Built with ❤️ for better workplace wellbeing**
