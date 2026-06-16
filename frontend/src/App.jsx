import { useState } from "react";
import Login from "./components/Login";
import Dashboard from "./components/Dashboard";
import { getUser, clearSession } from "./api";

export default function App() {
  const [user, setUser] = useState(getUser());

  function handleLogout() {
    clearSession();
    setUser(null);
  }

  if (!user) {
    return <Login onSuccess={(data) => setUser(getUser())} />;
  }
  return <Dashboard user={user} onLogout={handleLogout} />;
}
