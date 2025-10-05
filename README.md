# Early Burnout Detection Chatbot

A full-stack web application with user authentication system, built with Django backend and React frontend, paving the way for an AI-powered burnout detection chatbot.

##  Features

### Implemented Features
- **User Authentication System**
  - Secure user registration and login
  - Multi-Factor Authentication (MFA/2FA)
  - Gmail OTP (One-Time Password) delivery
  - Password reset functionality
  - Session management

### Planned Features
- **AI Chatbot Integration** - Burnout detection through conversational AI
- **Mental Health Assessment** - Automated burnout risk evaluation
- **Personalized Recommendations** - Customized well-being suggestions

## 🛠 Tech Stack

### Backend
- **Python** 
- **Django** - Web framework
- **Django REST Framework** - API development
- **PostgreSQL** - Database (default, configurable)
- **JWT Authentication** - Secure token-based auth

### Frontend
- **React** - User interface
- **React Router** - Navigation
- **Axios** - API communication
- **Context API** - State management

### Services
- **Gmail API** - OTP delivery
- **2FA/MFA** - Multi-factor authentication

## Installation

### Prerequisites
- Python 3.8+
- Node.js 14+
- PostgreSQL (optional)

### Backend Setup
```bash
# Clone repository
git clone https://github.com/rogitoms/early-burnout-detection-system.git
cd early-burnout-detection-system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure your database and Gmail credentials in .env

# Database setup
python manage.py migrate
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Configure API endpoints in .env

# Start development server
npm start
```

## Configuration

### Environment Variables

#### Backend (.env)
```env
SECRET_KEY=your-django-secret-key
DEBUG=True
DATABASE_URL=postgres://user:pass@localhost:5432/burnout_db
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

#### Frontend (.env)
```env
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_WS_URL=ws://localhost:8000/ws
```

## Usage

### Authentication Flow
1. **Registration**: Users create account with email verification
2. **Login**: Secure login with credentials
3. **MFA/2FA**: OTP sent via Gmail for additional security
4. **Password Reset**: Secure password recovery process

### API Endpoints
```http
POST /api/auth/register/          # User registration
POST /api/auth/login/             # User login
POST /api/auth/verify-otp/        # MFA verification
POST /api/auth/reset-password/    # Password reset request
POST /api/auth/reset-confirm/     # Password reset confirmation
GET  /api/user/profile/           # User profile
```

## Project Structure

```
early-burnout-detection-system/
├── backend/                 # Django project
│   ├── __pycache__/        # Python cache
│   ├── middleware.py       # Custom middleware
│   ├── settings.py         # Django settings
│   ├── urls.py            # URL routing
│   ├── asgi.py            # ASGI config
│   └── wsgi.py            # WSGI config
├── frontend/               # React Vite application
│   ├── public/
│   │   └── vite.svg       # Vite assets
│   ├── src/
│   │   ├── assets/        # Static assets
│   │   ├── components/    # React components
│   │   ├── contexts/      # React contexts (Auth, etc.)
│   │   ├── App.css        # Main styles
│   │   ├── App.jsx        # Main App component
│   │   ├── index.css      # Global styles
│   │   └── main.jsx       # Entry point
│   ├── index.html         # HTML template
│   ├── package.json       # Dependencies
│   ├── vite.config.js     # Vite configuration
│   └── eslint.config.js   # ESLint rules
├── venv/                  # Python virtual environment
├── .gitignore            # Git ignore rules
└── README.md             # Project documentation
```

## Security Features

- **Password Hashing**: BCrypt password encryption
- **JWT Tokens**: Secure authentication tokens
- **MFA/2FA**: Two-factor authentication via Gmail OTP
- **CORS Protection**: Configured CORS policies
- **SQL Injection Protection**: Django ORM security
- **XSS Protection**: Built-in Django security

##  Development Roadmap

### Phase 1: Complete
- [x] User authentication system
- [x] MFA/2FA with Gmail OTP
- [x] Password reset functionality
- [x] React frontend integration

### Phase 2: In Progress
- [ ] Chatbot interface components
- [ ] Burnout assessment algorithms
- [ ] Conversation data models

### Phase 3: Planned
- [ ] AI/ML integration for burnout detection
- [ ] Advanced analytics dashboard
- [ ] Mobile application
- [ ] Admin reporting tools

