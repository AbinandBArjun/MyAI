import { useMemo } from "react";
import { Routes, Route, useLocation } from "react-router-dom";

import Sidebar from "./components/Sidebar";
import Navbar from "./components/Navbar";
import AIChatWidget from "./components/AIChatWidget";

import Dashboard from "./pages/Dashboard";
import News from "./pages/News";
import Notes from "./pages/Notes";
import Trends from "./pages/Trends";
import Chat from "./pages/Chat";
import NoteDetail from "./pages/NoteDetail";
import ArticleDetail from "./pages/ArticleDetail";

function App() {
  const location = useLocation();

  const chatContext = useMemo(() => {
    const noteMatch = location.pathname.match(/^\/notes\/(\d+)$/);

    if (noteMatch) {
      return {
        type: "NOTE" as const,
        id: Number(noteMatch[1]),
      };
    }

    const articleMatch = location.pathname.match(/^\/news\/(\d+)$/);

    if (articleMatch) {
      return {
        type: "ARTICLE" as const,
        id: Number(articleMatch[1]),
      };
    }

    return undefined;
  }, [location.pathname]);

  return (
    <div className="flex min-h-screen bg-slate-950 text-white">
      <Sidebar />

      <div className="flex min-w-0 flex-1 flex-col">
        <Navbar />

        <main className="flex-1 px-8 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />

            <Route path="/news" element={<News />} />
            <Route path="/news/:id" element={<ArticleDetail />} />

            <Route path="/notes" element={<Notes />} />
            <Route path="/notes/:id" element={<NoteDetail />} />

            <Route path="/chat" element={<Chat />} />

            <Route path="/trends" element={<Trends />} />
          </Routes>
        </main>
      </div>

      <AIChatWidget context={chatContext} />
    </div>
  );
}

export default App;