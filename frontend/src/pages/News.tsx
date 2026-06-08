import { useEffect, useState } from "react";
import axios from "axios";

interface Article {
  id: number;
  title: string;
  summary: string;
  source: string;
  url: string;
}

export default function News() {
  const [articles, setArticles] = useState<Article[]>([]);

  const fetchArticles = async () => {
    try {
      const response = await axios.get(
        "http://localhost:8000/articles"
      );

      setArticles(response.data);
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    fetchArticles();
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-4xl font-bold">
          AI News Archive
        </h1>

        <p className="mt-2 text-gray-400">
          Articles stored inside Mypedia.
        </p>
      </div>

      {articles.map((article) => (
        <div
          key={article.id}
          className="rounded-xl bg-slate-800 p-5"
        >
          <div className="mb-2 text-sm text-blue-400">
            {article.source}
          </div>

          <h2 className="text-xl font-semibold">
            {article.title}
          </h2>

          <p className="mt-3 text-gray-300">
            {article.summary}
          </p>

          <a
            href={article.url}
            target="_blank"
            rel="noreferrer"
            className="mt-4 inline-block text-blue-400"
          >
            Read Full Article →
          </a>
        </div>
      ))}
    </div>
  );
}