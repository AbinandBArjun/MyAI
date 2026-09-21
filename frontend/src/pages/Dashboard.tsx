import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

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
    const fetchDashboardData = async () => {
      try {
        const [articlesResponse, notesResponse] = await Promise.all([
          fetch("http://127.0.0.1:8000/articles/"),
          fetch("http://127.0.0.1:8000/notes/"),
        ]);

        const articlesData = await articlesResponse.json();
        const notesData = await notesResponse.json();

        setArticles(articlesData);
        setNotes(notesData);
      } catch (error) {
        console.error("Failed to load dashboard data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <p className="text-sm text-slate-500">
          Loading your knowledge space...
        </p>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-7xl space-y-8">
      {/* Welcome Section */}
      <section>
        <p className="mb-2 text-sm font-medium text-blue-400">
          YOUR PERSONAL KNOWLEDGE SPACE
        </p>

        <h1 className="text-3xl font-bold tracking-tight text-white">
          Welcome back, Abinand.
        </h1>

        <p className="mt-2 max-w-2xl text-slate-400">
          Discover ideas, organize your thoughts, and connect what you learn.
        </p>
      </section>

      {/* Statistics */}
      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5">
          <p className="text-sm text-slate-500">Articles</p>

          <p className="mt-3 text-3xl font-semibold text-white">
            {articles.length}
          </p>

          <p className="mt-2 text-xs text-slate-500">
            Saved knowledge sources
          </p>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5">
          <p className="text-sm text-slate-500">Notes</p>

          <p className="mt-3 text-3xl font-semibold text-white">
            {notes.length}
          </p>

          <p className="mt-2 text-xs text-slate-500">
            Ideas captured by you
          </p>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5">
          <p className="text-sm text-slate-500">Topics</p>

          <p className="mt-3 text-3xl font-semibold text-white">3</p>

          <p className="mt-2 text-xs text-slate-500">
            Areas of exploration
          </p>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5">
          <p className="text-sm text-slate-500">AI Assistant</p>

          <p className="mt-3 text-3xl font-semibold text-emerald-400">
            Ready
          </p>

          <p className="mt-2 text-xs text-slate-500">
            Ask questions about your knowledge
          </p>
        </div>
      </section>

      {/* Main Content */}
      <section className="grid gap-8 lg:grid-cols-[1.5fr_1fr]">
        {/* Recent Articles */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/40 p-6">
          <div className="mb-6 flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-white">
                Recent Articles
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                The latest knowledge added to your space.
              </p>
            </div>

            <Link
              to="/news"
              className="text-sm font-medium text-blue-400 transition hover:text-blue-300"
            >
              View all →
            </Link>
          </div>

          <div className="space-y-4">
            {articles.slice(0, 5).map((article) => (
              <article
                key={article.id}
                className="rounded-xl border border-slate-800 bg-slate-950/50 p-4 transition hover:border-slate-700"
              >
                <div className="mb-2 flex items-center gap-2 text-xs text-slate-500">
                  <span>{article.source}</span>
                </div>

                <h3 className="font-medium leading-relaxed text-slate-200">
                  {article.title}
                </h3>

                <p className="mt-2 line-clamp-2 text-sm leading-relaxed text-slate-500">
                  {article.summary}
                </p>
              </article>
            ))}

            {articles.length === 0 && (
              <p className="text-sm text-slate-500">
                No articles available yet.
              </p>
            )}
          </div>
        </div>

        {/* Notes and Quick Actions */}
        <div className="space-y-8">
          {/* Quick Actions */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/40 p-6">
            <h2 className="text-lg font-semibold text-white">
              Quick Actions
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Continue exploring and organizing your knowledge.
            </p>

            <div className="mt-5 grid gap-3">
              <Link
                to="/notes"
                className="group flex items-center justify-between rounded-xl border border-slate-800 bg-slate-950/50 p-4 transition hover:border-blue-500/50 hover:bg-slate-800/60"
              >
                <div>
                  <p className="font-medium text-slate-200">
                    Create a Note
                  </p>

                  <p className="mt-1 text-xs text-slate-500">
                    Capture an idea or thought.
                  </p>
                </div>

                <span className="text-slate-500 transition group-hover:translate-x-1 group-hover:text-blue-400">
                  →
                </span>
              </Link>

              <Link
                to="/news"
                className="group flex items-center justify-between rounded-xl border border-slate-800 bg-slate-950/50 p-4 transition hover:border-blue-500/50 hover:bg-slate-800/60"
              >
                <div>
                  <p className="font-medium text-slate-200">
                    Discover News
                  </p>

                  <p className="mt-1 text-xs text-slate-500">
                    Explore the latest articles.
                  </p>
                </div>

                <span className="text-slate-500 transition group-hover:translate-x-1 group-hover:text-blue-400">
                  →
                </span>
              </Link>

              <Link
                to="/chat"
                className="group flex items-center justify-between rounded-xl border border-slate-800 bg-slate-950/50 p-4 transition hover:border-blue-500/50 hover:bg-slate-800/60"
              >
                <div>
                  <p className="font-medium text-slate-200">
                    Ask AI Assistant
                  </p>

                  <p className="mt-1 text-xs text-slate-500">
                    Ask questions about your knowledge.
                  </p>
                </div>

                <span className="text-slate-500 transition group-hover:translate-x-1 group-hover:text-blue-400">
                  →
                </span>
              </Link>
            </div>
          </div>

          {/* Recent Notes */}
          <div className="rounded-2xl border border-slate-800 bg-slate-900/40 p-6">
            <h2 className="text-lg font-semibold text-white">
              Recent Notes
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Your latest thoughts and ideas.
            </p>

            <div className="mt-5 space-y-3">
              {notes.slice(0, 4).map((note) => (
                <div
                  key={note.id}
                  className="rounded-xl border border-slate-800 bg-slate-950/50 p-4"
                >
                  <h3 className="font-medium text-slate-200">
                    {note.title}
                  </h3>

                  <p className="mt-1 line-clamp-2 text-sm text-slate-500">
                    {note.content}
                  </p>
                </div>
              ))}

              {notes.length === 0 && (
                <p className="text-sm text-slate-500">
                  No notes created yet.
                </p>
              )}
            </div>
          </div>

          {/* Explore Your Knowledge */}
          <div className="rounded-2xl border border-blue-500/20 bg-blue-500/5 p-6">
            <h2 className="text-lg font-semibold text-white">
              Explore Your Knowledge
            </h2>

            <p className="mt-2 text-sm leading-relaxed text-slate-400">
              Use the AI assistant to find connections, understand concepts,
              and ask questions about your saved knowledge.
            </p>

            <Link
              to="/chat"
              className="mt-5 inline-flex rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-blue-500"
            >
              Ask AI Assistant →
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}