import { Routes, Route, useLocation } from "react-router-dom";

import Sidebar from "./components/Sidebar";
import Navbar from "./components/Navbar";
import AIChatWidget from "./components/AIChatWidget";

import Dashboard from "./pages/Dashboard";
import News from "./pages/News";
import Notes from "./pages/Notes";
import Trends from "./pages/Trends";
import Chat from "./pages/Chat";
import ArticleDetail from "./pages/ArticleDetail";
import NoteDetail from "./pages/NoteDetail";

interface ChatContext {
  type: "NOTE" | "ARTICLE";
  id: number;
  title?: string;
}

function AppContent() {
  const location = useLocation();

  let context: ChatContext | undefined;

  const noteMatch = location.pathname.match(/^\/notes\/(\d+)$/);
  const articleMatch = location.pathname.match(/^\/news\/(\d+)$/);

  if (noteMatch) {
    context = {
      type: "NOTE",
      id: Number(noteMatch[1]),
    };
  } else if (articleMatch) {
    context = {
      type: "ARTICLE",
      id: Number(articleMatch[1]),
    };
  }

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

      <AIChatWidget context={context} />
    </div>
  );
}

export default function App() {
  return <AppContent />;
}