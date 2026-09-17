import { useEffect, useState } from "react";

const API_URL = "http://127.0.0.1:8000";

interface Article {
  id: number;
  title: string;
  summary: string;
  source: string;
  url: string;
}

interface Note {
  id: number;
  title: string;
  content: string;
}

export default function Dashboard() {
  const [articles, setArticles] = useState<Article[]>([]);
  const [notes, setNotes] = useState<Note[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadDashboard() {
      try {
        const [articlesResponse, notesResponse] = await Promise.all([
          fetch(`${API_URL}/articles/`),
          fetch(`${API_URL}/notes/`),
        ]);

        if (!articlesResponse.ok || !notesResponse.ok) {
          throw new Error("Failed to load dashboard data");
        }

        const articlesData = await articlesResponse.json();
        const notesData = await notesResponse.json();

        setArticles(articlesData);
        setNotes(notesData);
      } catch (error) {
        console.error("Dashboard loading error:", error);
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
  }, []);

  const latestArticles = articles.slice(0, 5);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-5xl font-bold text-blue-400">
          Mypedia Dashboard
        </h1>

        <p className="mt-2 text-gray-400">
          Your AI knowledge and research hub.
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4">
        <div className="rounded-xl bg-slate-800 p-6">
          <h3 className="text-gray-400">Articles</h3>
          <p className="mt-2 text-3xl font-bold">
            {loading ? "..." : articles.length}
          </p>
        </div>

        <div className="rounded-xl bg-slate-800 p-6">
          <h3 className="text-gray-400">Notes</h3>
          <p className="mt-2 text-3xl font-bold">
            {loading ? "..." : notes.length}
          </p>
        </div>

        <div className="rounded-xl bg-slate-800 p-6">
          <h3 className="text-gray-400">Bookmarks</h3>
          <p className="mt-2 text-3xl font-bold">0</p>
        </div>

        <div className="rounded-xl bg-slate-800 p-6">
          <h3 className="text-gray-400">Topics</h3>
          <p className="mt-2 text-3xl font-bold">3</p>
        </div>
      </div>

      {/* Latest News */}
      <div className="rounded-xl bg-slate-800 p-6">
        <h2 className="mb-4 text-2xl font-semibold">
          Latest AI News
        </h2>

        {loading ? (
          <div className="rounded-lg border border-slate-700 p-4">
            Loading articles...
          </div>
        ) : latestArticles.length === 0 ? (
          <div className="rounded-lg border border-slate-700 p-4">
            No articles available yet.
          </div>
        ) : (
          <div className="space-y-3">
            {latestArticles.map((article) => (
              <div
                key={article.id}
                className="rounded-lg border border-slate-700 p-4"
              >
                <h3 className="text-lg font-semibold">
                  {article.title}
                </h3>

                <p className="mt-2 text-gray-400">
                  {article.summary}
                </p>

                <a
                  href={article.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="mt-2 inline-block text-blue-400 hover:underline"
                >
                  Read article →
                </a>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Trends */}
      <div className="rounded-xl bg-slate-800 p-6">
        <h2 className="mb-4 text-2xl font-semibold">
          Trending Topics
        </h2>

        <div className="flex gap-3">
          <span className="rounded-full bg-blue-600 px-4 py-2">
            GPT
          </span>

          <span className="rounded-full bg-purple-600 px-4 py-2">
            Agents
          </span>

          <span className="rounded-full bg-green-600 px-4 py-2">
            MCP
          </span>
        </div>
      </div>
    </div>
  );
}