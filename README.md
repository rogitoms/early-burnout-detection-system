```markdown
# Burnout Detection System

A comprehensive full-stack application for detecting and managing workplace burnout through AI-powered assessments and personalized recommendations.

## 🌟 Features

### 🔐 Authentication & Security
- **Two-Factor Authentication (2FA)** with email verification
- Role-based access control (Admin/Employee)
- Secure session management
- Password reset functionality

### 🤖 AI-Powered Assessment
- **Machine Learning Model** using DistilBERT for burnout prediction
- **Conversational Chatbot** for natural assessment experience
- **Personalized Recommendations** via Groq LLM API
- Real-time burnout scoring and analysis

### 👥 User Management
- **Admin Dashboard** for employee management
- Employee role assignment and tracking
- Assessment history and progress monitoring
- Department and employee ID management

### 💬 Smart Chatbot
- Progressive question flow (6 key questions)
- Context-aware responses
- Session persistence
- Assessment completion tracking

## 🛠 Tech Stack

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
- Real-time text processing and analysis

## 🚀 Quick Start

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

## 📁 Project Structure

```
burnout-detection-system/
├── backend/                 # Django backend
│   ├── api/                # Main app with auth and user management
│   ├── chatbot/            # Chatbot and assessment logic
│   ├── ml_model/           # Machine learning components
│   └── backend/            # Project settings
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── contexts/       # React contexts (Auth)
│   │   ├── services/       # API services
│   │   └── App.jsx         # Main app component
└── README.md
```

## 🔧 API Endpoints

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

## 🧠 ML Model Details

### Architecture
- **Base Model**: DistilBERT (uncased)
- **Custom Head**: Multi-layer perceptron with GELU activation
- **Output**: Sigmoid activation for burnout probability (0-1)

### Training Features
- Text preprocessing and cleaning
- Strategic layer freezing for efficiency
- Advanced dropout for regularization
- Optimized for burnout-specific language patterns

## 👥 User Roles

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

## 🔒 Security Features

- **2FA Enforcement**: All users require email verification
- **Session Management**: Secure cookie-based sessions
- **CSRF Protection**: Cross-site request forgery protection
- **CORS Configuration**: Controlled cross-origin requests
- **Password Validation**: Strong password requirements

## 📊 Assessment Flow

1. **Welcome** → Introduction and consent
2. **Q1-6** → Progressive questions about work experience
3. **ML Analysis** → Real-time burnout scoring
4. **LLM Recommendations** → Personalized advice generation
5. **Results** → Comprehensive report with actionable insights

## 🎨 UI/UX Features

- **Responsive Design**: Mobile-first approach
- **Dark/Light Mode**: CSS variable support
- **Accessibility**: WCAG compliant components
- **Loading States**: Smooth user experience
- **Error Handling**: User-friendly error messages

## 🚀 Deployment

### Backend (Production)
```bash
# Collect static files
python manage.py collectstatic

# Use production WSGI server
gunicorn backend.wsgi:application
```

### Frontend (Production)
```bash
# Build optimized version
npm run build

# Serve with nginx or similar
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check existing issues on GitHub
- Create new issue with detailed description
- Contact development team

---

**Built with ❤️ for better workplace wellbeing**
```I NEED FORMAT OF READ ME
