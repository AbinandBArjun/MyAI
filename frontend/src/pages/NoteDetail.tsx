import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import axios from "axios";

interface Note {
  id: number;
  title: string;
  content: string;
}

export default function NoteDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [note, setNote] = useState<Note | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    const fetchNote = async () => {
      if (!id) {
        setError(true);
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(false);

        const response = await axios.get(
          `http://localhost:8000/notes/${id}`
        );

        setNote(response.data);
      } catch (error) {
        console.error("Failed to fetch note:", error);
        setError(true);
      } finally {
        setLoading(false);
      }
    };

    fetchNote();
  }, [id]);

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="text-center">
          <div className="mx-auto h-8 w-8 animate-spin rounded-full border-2 border-slate-600 border-t-blue-400" />

          <p className="mt-4 text-gray-400">
            Loading note...
          </p>
        </div>
      </div>
    );
  }

  if (error || !note) {
    return (
      <div className="rounded-2xl border border-red-900/50 bg-red-950/20 p-10 text-center">
        <h1 className="text-xl font-semibold text-red-300">
          Note not found
        </h1>

        <p className="mt-2 text-sm text-red-200/70">
          The requested note could not be loaded.
        </p>

        <button
          onClick={() => navigate("/notes")}
          className="mt-5 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-blue-500"
        >
          Back to Notes
        </button>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-4xl space-y-8">
      <button
        onClick={() => navigate("/notes")}
        className="text-sm font-medium text-blue-400 transition hover:text-blue-300"
      >
        ← Back to Notes
      </button>

      <article className="rounded-2xl border border-slate-800 bg-slate-900/70 p-6 shadow-lg sm:p-8">
        <div className="mb-6">
          <p className="text-sm font-medium uppercase tracking-[0.2em] text-blue-400">
            Personal Note
          </p>

          <h1 className="mt-3 text-3xl font-bold tracking-tight text-white sm:text-4xl">
            {note.title}
          </h1>
        </div>

        <div className="border-t border-slate-800 pt-6">
          <p className="whitespace-pre-wrap text-base leading-8 text-gray-300">
            {note.content}
          </p>
        </div>
      </article>
    </div>
  );
}