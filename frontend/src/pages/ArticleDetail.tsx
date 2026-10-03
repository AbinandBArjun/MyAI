import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import axios from "axios";

interface Article {
  id: number;
  title: string;
  summary: string;
  source: string;
  url: string;
}

export default function ArticleDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [article, setArticle] = useState<Article | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    const fetchArticle = async () => {
      if (!id) {
        setError(true);
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(false);

        const response = await axios.get(
          `http://localhost:8000/articles/${id}`
        );

        setArticle(response.data);
      } catch (error) {
        console.error("Failed to fetch article:", error);
        setError(true);
      } finally {
        setLoading(false);
      }
    };

    fetchArticle();
  }, [id]);

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="text-center">
          <div className="mx-auto h-8 w-8 animate-spin rounded-full border-2 border-slate-600 border-t-blue-400" />

          <p className="mt-4 text-gray-400">
            Loading article...
          </p>
        </div>
      </div>
    );
  }

  if (error || !article) {
    return (
      <div className="rounded-2xl border border-red-900/50 bg-red-950/20 p-10 text-center">
        <h1 className="text-xl font-semibold text-red-300">
          Article not found
        </h1>

        <p className="mt-2 text-sm text-red-200/70">
          The requested article could not be loaded.
        </p>

        <button
          onClick={() => navigate("/news")}
          className="mt-5 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-500"
        >
          Back to News
        </button>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl space-y-8">
      <button
        onClick={() => navigate("/news")}
        className="text-sm font-medium text-blue-400 transition hover:text-blue-300"
      >
        ← Back to News
      </button>

      <article className="rounded-2xl border border-slate-800 bg-slate-900/70 p-6 shadow-lg sm:p-8">
        <div className="flex flex-wrap items-center gap-3">
          <span className="rounded-full bg-blue-500/10 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-blue-400">
            {article.source}
          </span>

          <span className="text-xs text-slate-500">
            Article #{article.id}
          </span>
        </div>

        <h1 className="mt-5 text-3xl font-bold leading-tight tracking-tight text-white sm:text-4xl">
          {article.title}
        </h1>

        <div className="mt-8 border-t border-slate-800 pt-6">
          <p className="text-base leading-8 text-gray-300">
            {article.summary}
          </p>
        </div>

        <div className="mt-8 border-t border-slate-800 pt-6">
          <a
            href={article.url}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-blue-500"
          >
            Read Original Article
            <span>↗</span>
          </a>
        </div>
      </article>
    </div>
  );
}