import React, { createContext, useEffect, useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Dashboard from "layouts/Dashboard";

export const AlertsContext = createContext([]);

function App() {
  const [alerts, setAlerts] = useState<any[]>([]);

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/realtime/ws/alerts");
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setAlerts((prev) => [...prev, data]);
    };
    return () => ws.close();
  }, []);

  return (
    <AlertsContext.Provider value={alerts}>
      <BrowserRouter>
        <Routes>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="*" element={<Navigate to="/dashboard" />} />
        </Routes>
      </BrowserRouter>
    </AlertsContext.Provider>
  );
}

export default App;
