# NexusChat

NexusChat-v3 is a modern, real-time chat application built with a Python (FastAPI) backend and a React (Vite) frontend. It features secure user authentication, real-time messaging using WebSockets, and a responsive, dynamic user interface.

## 🚀 Features

- **Real-time Messaging**: Instant message delivery using WebSockets.
- **Secure Authentication**: User registration and login with JWT-based authentication and Bcrypt password hashing.
- **Modern UI/UX**: Built with React, Tailwind CSS v4, and dynamic animations for a premium feel.
- **Responsive Design**: Works seamlessly across desktop and mobile devices.
- **Robust Backend**: Powered by FastAPI for high performance and scalability.
- **Database**: MongoDB for reliable message and user data storage.
- **Security**: Includes rate limiting, input validation, and secure API key handling.

## 🛠️ Technology Stack

**Frontend:**
- React (via Vite)
- Tailwind CSS v4 (for styling)
- Anime.js & Lenis (for animations and smooth scrolling)
- Native WebSockets API

**Backend:**
- Python 3.x
- FastAPI
- Uvicorn (ASGI server)
- Motor (Async MongoDB driver)
- PyJWT & Bcrypt (Security)

## 📦 Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 18+
- MongoDB instance (local or Atlas)

### Backend Setup
1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the `backend` directory. Use `.env.example` as a template and provide your MongoDB URI and a secret key for JWT:
   ```env
   MONGODB_URI=mongodb://localhost:27017
   SECRET_KEY=your_super_secret_key_here
   ```
5. Start the backend server:
   ```bash
   uvicorn server:app --reload --port 8000
   ```

### Frontend Setup
1. Navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```
2. Install the frontend dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
4. Open your browser and navigate to the URL provided by Vite (usually `http://localhost:5173`).

## 🛡️ Security Best Practices Implemented
- **Rate Limiting**: Protects public endpoints from brute-force and DDoS attacks.
- **Input Validation**: Ensures all user inputs meet strict schema requirements before processing.
- **Secure Password Storage**: Uses Bcrypt with appropriate work factors.
- **Environment Variables**: Sensitive data like DB URIs and Secret Keys are kept out of source code.

## 🤝 Contributing
Contributions, issues, and feature requests are welcome!

## 📝 License
This project is open-source and available under the MIT License.
