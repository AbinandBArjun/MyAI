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
      <h1 className="text-4xl font-bold">
        AI News
      </h1>

      {articles.map((article, index) => (
        <div
          key={index}
          className="bg-slate-800 p-5 rounded-xl"
        >
          <h2 className="text-xl font-semibold">
            {article.title}
          </h2>

          <a
            href={article.link}
            target="_blank"
            rel="noreferrer"
            className="inline-block mt-3 text-blue-400"
          >
            Read Article →
          </a>
        </div>
      ))}
    </div>
  );
}