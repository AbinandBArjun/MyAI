import { useLocation } from "react-router-dom";

const pageTitles: Record<string, string> = {
  "/": "Dashboard",
  "/news": "Discover News",
  "/notes": "My Notes",
  "/chat": "AI Assistant",
  "/trends": "AI Trends",
};

export default function Navbar() {
  const location = useLocation();

  const pageTitle = pageTitles[location.pathname] || "Mypedia";

  return (
    <header className="flex items-center justify-between border-b border-slate-800 bg-slate-950/80 px-8 py-5 backdrop-blur">
      <div>
        <h2 className="text-xl font-semibold text-white">
          {pageTitle}
        </h2>

        <p className="mt-1 text-sm text-slate-500">
          Discover, understand, and connect knowledge.
        </p>
      </div>

      <div className="flex items-center gap-4">
        <div className="hidden items-center gap-2 rounded-xl border border-slate-800 bg-slate-900 px-4 py-2.5 md:flex">
          <span className="text-slate-500">⌕</span>

          <input
            type="text"
            placeholder="Search your knowledge..."
            className="w-56 bg-transparent text-sm text-white outline-none placeholder:text-slate-500"
          />
        </div>

        <div className="flex h-10 w-10 items-center justify-center rounded-full border border-slate-700 bg-slate-800 text-sm font-semibold text-blue-400">
          A
        </div>
      </div>
    </header>
  );
}