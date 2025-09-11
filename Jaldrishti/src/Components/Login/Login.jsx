import React, { useState, useEffect } from "react";
import {
  User,
  Shield,
  BarChart3,
  AlertCircle,
  CheckCircle,
} from "lucide-react";

// Firebase imports
import { initializeApp } from "firebase/app";
import {
  getAuth,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut,
} from "firebase/auth";
import { getFirestore, doc, setDoc, getDoc } from "firebase/firestore";

// Firebase config
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);

import "./Login.css"; // external CSS

const Login = () => {
  const [selectedRole, setSelectedRole] = useState(null);
  const [showLoginForm, setShowLoginForm] = useState(false);
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [user, setUser] = useState(null);
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState("");

  const roles = [
    {
      id: "citizen",
      name: "Citizen",
      icon: User,
      description: [
        "Report hazards quickly",
        "Track your submissions",
        "Receive alerts & updates",
      ],
      color: "#3b82f6",
    },
    {
      id: "analyst",
      name: "Analyst",
      icon: BarChart3,
      description: [
        "Access hazard data",
        "Generate visual reports",
        "Identify patterns & risks",
      ],
      color: "#10b981",
    },
    {
      id: "admin",
      name: "Admin",
      icon: Shield,
      description: [
        "Manage all users",
        "Configure system settings",
        "Full access to all reports",
      ],
      color: "#ef4444",
    },
  ];

  useEffect(() => {
    const savedUser = localStorage.getItem("currentUser");
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
  }, []);

  const handleRoleSelect = (role) => {
    setSelectedRole(role);
    setShowLoginForm(true);
    setMessage("");
  };

  const showMessage = (text, type) => {
    setMessage(text);
    setMessageType(type);
    setTimeout(() => setMessage(""), 5000);
  };

  const handleAuth = async () => {
    if (!email || !password) {
      showMessage("Please fill in all fields", "error");
      return;
    }

    setLoading(true);
    try {
      let authResult;

      if (isLogin) {
        authResult = await signInWithEmailAndPassword(auth, email, password);
        const docRef = doc(db, "users", authResult.user.uid);
        const userDoc = await getDoc(docRef);
        const roleData = userDoc.exists()
          ? userDoc.data()
          : { role: selectedRole.id };

        showMessage("Login successful!", "success");

        const userData = {
          ...authResult.user,
          role: roleData.role,
          roleName: selectedRole.name,
        };

        localStorage.setItem("currentUser", JSON.stringify(userData));
        setUser(userData);
      } else {
        authResult = await createUserWithEmailAndPassword(
          auth,
          email,
          password
        );

        await setDoc(doc(db, "users", authResult.user.uid), {
          role: selectedRole.id,
          email: authResult.user.email,
          createdAt: new Date().toISOString(),
        });

        showMessage("Account created successfully!", "success");

        const userData = {
          ...authResult.user,
          role: selectedRole.id,
          roleName: selectedRole.name,
        };

        localStorage.setItem("currentUser", JSON.stringify(userData));
        setUser(userData);
      }

      setShowLoginForm(false);
      setEmail("");
      setPassword("");
    } catch (error) {
      showMessage(error.message, "error");
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await signOut(auth);
      localStorage.removeItem("currentUser");
      setUser(null);
      setSelectedRole(null);
      setShowLoginForm(false);
      showMessage("Logged out successfully", "success");
    } catch (error) {
      showMessage("Logout failed", "error");
    }
  };

  if (user) {
    return (
      <div className="container">
        <div className="card">
          <h2>Welcome!</h2>
          <p>{user.email}</p>
          <h3>Role: {user.roleName}</h3>
          <button onClick={handleLogout} className="logout-btn">
            Logout
          </button>
        </div>
      </div>
    );
  }

  if (showLoginForm) {
  const SelectedIcon = selectedRole.icon;
  return (
    <div className="container">
      <div className="card">
        <div className="form-header">
          <SelectedIcon size={48} color="#6b7280" />
          <h2>{isLogin ? "Login" : "Register"} as {selectedRole.name}</h2>
          <p className="form-subtitle">
            {selectedRole.name === "Citizen" && "Report hazards, track your submissions and get alerts."}
            {selectedRole.name === "Analyst" && "Analyze hazard data, generate reports and identify risks."}
            {selectedRole.name === "Admin" && "Manage users, configure settings and oversee reports."}
          </p>
        </div>

        {message && (
          <div className={`message ${messageType}`}>{message}</div>
        )}

        <div className="form-group">
          <label>Email</label>
          <input
            type="email"
            placeholder="Enter your email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>

        <div className="form-group">
          <label>Password</label>
          <input
            type="password"
            placeholder="Enter your password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>

        <button
          onClick={handleAuth}
          disabled={loading}
          style={{ backgroundColor: selectedRole.color }}
        >
          {loading ? "Processing..." : isLogin ? "Login" : "Register"}
        </button>

        <div className="switch-auth">
          <button onClick={() => setIsLogin(!isLogin)}>
            {isLogin
              ? "Don't have an account? Register"
              : "Already have an account? Login"}
          </button>
          <button onClick={() => setShowLoginForm(false)}>Back</button>
        </div>
      </div>
    </div>
  );
}

  return (
    <div className="container">
      <div className="large-card">
        <h1>Select Your Role</h1>
        {message && <div className={`message ${messageType}`}>{message}</div>}

        <div className="roles-grid">
          {roles.map((role) => {
            const IconComponent = role.icon;
            return (
              <div
                key={role.id}
                className="role-card"
                onClick={() => handleRoleSelect(role)}
              >
                <div className="icon-container">
                  <IconComponent size={32} color="#6b7280" />
                </div>
                <h3>{role.name}</h3>
                <ul>
                  {role.description.map((point, idx) => (
                    <li key={idx}>{point}</li>
                  ))}
                </ul>
                <button
                  style={{ backgroundColor: role.color }}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleRoleSelect(role);
                  }}
                >
                  Continue as {role.name}
                </button>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default Login;
