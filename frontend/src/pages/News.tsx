import { useEffect, useState } from "react";
import axios from "axios";

interface Article {
  title: string;
  link: string;
}

export default function News() {
  const [articles, setArticles] = useState<Article[]>([]);

  const fetchNews = async () => {
    try {
      const response = await axios.get(
        "http://localhost:8000/news"
      );

      setArticles(response.data);
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    fetchNews();
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-4xl font-bold">
          AI News Feed
        </h1>

        <p className="mt-2 text-gray-400">
          Latest AI and technology news from TechCrunch.
        </p>
      </div>

      {articles.map((article, index) => (
        <div
          key={index}
          className="rounded-xl bg-slate-800 p-5"
        >
          <h2 className="text-xl font-semibold">
            {article.title}
          </h2>

          <a
            href={article.link}
            target="_blank"
            rel="noreferrer"
            className="mt-3 inline-block text-blue-400"
          >
            Read Article →
          </a>
        </div>
      ))}
    </div>
  );
}