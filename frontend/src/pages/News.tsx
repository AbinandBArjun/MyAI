import { useEffect, useState } from "react";
import axios from "axios";

interface Article {
  id: number;
  title: string;
  summary: string;
  source: string;
  url: string;
}

interface Pagination {
  page: number;
  page_size: number;
  total_items: number;
  total_pages: number;
  has_next: boolean;
  has_previous: boolean;
}

export default function News() {
  const [articles, setArticles] = useState<Article[]>([]);
  const [pagination, setPagination] = useState<Pagination>({
    page: 1,
    page_size: 20,
    total_items: 0,
    total_pages: 0,
    has_next: false,
    has_previous: false,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const fetchArticles = async (pageToFetch: number = 1) => {
    try {
      setLoading(true);
      setError(false);

      const response = await axios.get(
        "http://localhost:8000/articles",
        {
          params: {
            page: pageToFetch,
            page_size: 20,
          },
        }
      );

      setArticles(response.data.items);
      setPagination(response.data.pagination);
    } catch (error) {
      console.error("Failed to fetch articles:", error);
      setError(true);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchArticles();
  }, []);

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <section>
        <p className="text-sm font-medium uppercase tracking-[0.2em] text-blue-400">
          Knowledge Library
        </p>

        <div className="mt-3 flex flex-col justify-between gap-4 md:flex-row md:items-end">
          <div>
            <h1 className="text-4xl font-bold tracking-tight text-white">
              AI News Archive
            </h1>

            <p className="mt-3 max-w-2xl text-gray-400">
              Explore articles collected and organized inside MyAI.
            </p>
          </div>

          <div className="rounded-full border border-slate-700 bg-slate-900 px-4 py-2 text-sm text-gray-300">
            {pagination.total_items}{" "}
            {pagination.total_items === 1 ? "article" : "articles"}
          </div>
        </div>
      </section>

      {/* Loading State */}
      {loading && (
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-10 text-center">
          <div className="mx-auto h-8 w-8 animate-spin rounded-full border-2 border-slate-600 border-t-blue-400" />

          <p className="mt-4 text-gray-400">
            Loading your news archive...
          </p>
        </div>
      )}

      {/* Error State */}
      {!loading && error && (
        <div className="rounded-2xl border border-red-900/50 bg-red-950/20 p-8 text-center">
          <h2 className="text-lg font-semibold text-red-300">
            Unable to load articles
          </h2>

          <p className="mt-2 text-sm text-red-200/70">
            Make sure the backend server is running and try again.
          </p>

          <button
            onClick={() => fetchArticles(pagination.page)}
            className="mt-5 rounded-lg bg-red-500 px-4 py-2 text-sm font-medium text-white transition hover:bg-red-400"
          >
            Try Again
          </button>
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && articles.length === 0 && (
        <div className="rounded-2xl border border-dashed border-slate-700 bg-slate-900/40 p-12 text-center">
          <div className="text-4xl">📰</div>

          <h2 className="mt-4 text-xl font-semibold text-white">
            No articles yet
          </h2>

          <p className="mt-2 text-gray-400">
            Your collected articles will appear here.
          </p>
        </div>
      )}

      {/* Article Grid */}
      {!loading && !error && articles.length > 0 && (
        <section className="grid gap-6 lg:grid-cols-2">
          {articles.map((article) => (
            <article
              key={article.id}
              className="group flex h-full flex-col rounded-2xl border border-slate-800 bg-slate-900/70 p-6 transition duration-300 hover:-translate-y-1 hover:border-slate-700 hover:bg-slate-800/80"
            >
              <div className="flex items-center justify-between gap-3">
                <span className="rounded-full bg-blue-500/10 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-blue-400">
                  {article.source}
                </span>

                <span className="text-xs text-slate-500">
                  Article #{article.id}
                </span>
              </div>

              <h2 className="mt-5 text-xl font-semibold leading-snug text-white transition group-hover:text-blue-300">
                {article.title}
              </h2>

              <p className="mt-4 flex-1 text-sm leading-7 text-gray-400">
                {article.summary}
              </p>

              <div className="mt-6 border-t border-slate-800 pt-4">
                <a
                  href={article.url}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-2 text-sm font-medium text-blue-400 transition hover:text-blue-300"
                >
                  Read Full Article
                  <span className="transition-transform group-hover:translate-x-1">
                    →
                  </span>
                </a>
              </div>
            </article>
          ))}
        </section>
      )}

      {/* Pagination Controls */}
      {!loading && !error && pagination.total_pages > 1 && (
        <div className="flex flex-col items-center justify-between gap-4 border-t border-slate-800 pt-6 sm:flex-row">
          <p className="text-sm text-gray-400">
            Page {pagination.page} of {pagination.total_pages}
          </p>

          <div className="flex items-center gap-3">
            <button
              onClick={() => fetchArticles(pagination.page - 1)}
              disabled={!pagination.has_previous}
              className="rounded-lg border border-slate-700 px-4 py-2 text-sm font-medium text-gray-300 transition hover:border-slate-600 hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-40"
            >
              Previous
            </button>

            <button
              onClick={() => fetchArticles(pagination.page + 1)}
              disabled={!pagination.has_next}
              className="rounded-lg border border-slate-700 px-4 py-2 text-sm font-medium text-gray-300 transition hover:border-slate-600 hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-40"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
