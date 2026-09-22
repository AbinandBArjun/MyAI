import { Routes, Route } from "react-router-dom";

import Sidebar from "./components/Sidebar";
import Navbar from "./components/Navbar";
import AIChatWidget from "./components/AIChatWidget";

import Dashboard from "./pages/Dashboard";
import News from "./pages/News";
import Notes from "./pages/Notes";
import Trends from "./pages/Trends";

function App() {
  return (
    <div className="flex min-h-screen bg-slate-950 text-white">
      <Sidebar />

      <div className="flex min-w-0 flex-1 flex-col">
        <Navbar />

        <main className="flex-1 px-8 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/news" element={<News />} />
            <Route path="/notes" element={<Notes />} />
            <Route path="/trends" element={<Trends />} />
          </Routes>
        </main>
      </div>

      <AIChatWidget />
    </div>
  );
}

export default App;