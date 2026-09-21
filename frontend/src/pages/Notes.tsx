import { useEffect, useState } from "react";
import axios from "axios";

interface Note {
  id: number;
  title: string;
  content: string;
}

export default function Notes() {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [notes, setNotes] = useState<Note[]>([]);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(false);

  const API_URL = "http://localhost:8000/notes";

  const fetchNotes = async () => {
    try {
      setLoading(true);
      setError(false);

      const response = await axios.get(API_URL);
      setNotes(response.data);
    } catch (error) {
      console.error("Failed to fetch notes:", error);
      setError(true);
    } finally {
      setLoading(false);
    }
  };

  const clearForm = () => {
    setTitle("");
    setContent("");
    setEditingId(null);
  };

  const createNote = async () => {
    if (!title.trim() || !content.trim()) return;

    try {
      setSaving(true);

      await axios.post(API_URL, {
        title: title.trim(),
        content: content.trim(),
      });

      clearForm();
      await fetchNotes();
    } catch (error) {
      console.error("Failed to create note:", error);
    } finally {
      setSaving(false);
    }
  };

  const updateNote = async () => {
    if (!title.trim() || !content.trim() || editingId === null) return;

    try {
      setSaving(true);

      await axios.put(`${API_URL}/${editingId}`, {
        title: title.trim(),
        content: content.trim(),
      });

      clearForm();
      await fetchNotes();
    } catch (error) {
      console.error("Failed to update note:", error);
    } finally {
      setSaving(false);
    }
  };

  const editNote = (note: Note) => {
    setTitle(note.title);
    setContent(note.content);
    setEditingId(note.id);

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

  const deleteNote = async (id: number) => {
    const confirmed = window.confirm(
      "Are you sure you want to delete this note?"
    );

    if (!confirmed) return;

    try {
      await axios.delete(`${API_URL}/${id}`);

      if (editingId === id) {
        clearForm();
      }

      await fetchNotes();
    } catch (error) {
      console.error("Failed to delete note:", error);
    }
  };

  useEffect(() => {
    fetchNotes();
  }, []);

  const isEditing = editingId !== null;

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <section>
        <p className="text-sm font-medium uppercase tracking-[0.2em] text-blue-400">
          Personal Knowledge
        </p>

        <div className="mt-3 flex flex-col justify-between gap-4 md:flex-row md:items-end">
          <div>
            <h1 className="text-4xl font-bold tracking-tight text-white">
              My Notes
            </h1>

            <p className="mt-3 max-w-2xl text-gray-400">
              Capture ideas, organize thoughts, and build your personal
              knowledge base.
            </p>
          </div>

          <div className="rounded-full border border-slate-700 bg-slate-900 px-4 py-2 text-sm text-gray-300">
            {notes.length} {notes.length === 1 ? "note" : "notes"}
          </div>
        </div>
      </section>

      {/* Note Editor */}
      <section className="rounded-2xl border border-slate-800 bg-slate-900/70 p-6 shadow-lg">
        <div className="mb-5 flex items-center justify-between gap-3">
          <div>
            <h2 className="text-xl font-semibold text-white">
              {isEditing ? "Edit Note" : "Create a New Note"}
            </h2>

            <p className="mt-1 text-sm text-gray-500">
              {isEditing
                ? "Update your existing note."
                : "Write down something worth remembering."}
            </p>
          </div>

          {isEditing && (
            <button
              onClick={clearForm}
              className="text-sm text-gray-400 transition hover:text-white"
            >
              Cancel
            </button>
          )}
        </div>

        <div className="space-y-4">
          <input
            type="text"
            placeholder="Give your note a title..."
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition placeholder:text-slate-600 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
          />

          <textarea
            placeholder="Start writing your thoughts..."
            value={content}
            onChange={(e) => setContent(e.target.value)}
            rows={6}
            className="w-full resize-y rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 leading-7 text-white outline-none transition placeholder:text-slate-600 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
          />

          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={isEditing ? updateNote : createNote}
              disabled={
                saving || !title.trim() || !content.trim()
              }
              className="rounded-xl bg-blue-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-40"
            >
              {saving
                ? "Saving..."
                : isEditing
                  ? "Update Note"
                  : "Create Note"}
            </button>

            {(title || content || isEditing) && (
              <button
                onClick={clearForm}
                className="rounded-xl border border-slate-700 px-5 py-3 text-sm font-medium text-gray-400 transition hover:border-slate-600 hover:text-white"
              >
                Clear
              </button>
            )}
          </div>
        </div>
      </section>

      {/* Loading State */}
      {loading && (
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-10 text-center">
          <div className="mx-auto h-8 w-8 animate-spin rounded-full border-2 border-slate-600 border-t-blue-400" />

          <p className="mt-4 text-gray-400">
            Loading your notes...
          </p>
        </div>
      )}

      {/* Error State */}
      {!loading && error && (
        <div className="rounded-2xl border border-red-900/50 bg-red-950/20 p-8 text-center">
          <h2 className="text-lg font-semibold text-red-300">
            Unable to load notes
          </h2>

          <p className="mt-2 text-sm text-red-200/70">
            Make sure the backend server is running and try again.
          </p>

          <button
            onClick={fetchNotes}
            className="mt-5 rounded-lg bg-red-500 px-4 py-2 text-sm font-medium text-white transition hover:bg-red-400"
          >
            Try Again
          </button>
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && notes.length === 0 && (
        <div className="rounded-2xl border border-dashed border-slate-700 bg-slate-900/40 p-12 text-center">
          <div className="text-4xl">📝</div>

          <h2 className="mt-4 text-xl font-semibold text-white">
            Your notes will appear here
          </h2>

          <p className="mt-2 text-gray-400">
            Create your first note using the editor above.
          </p>
        </div>
      )}

      {/* Notes Grid */}
      {!loading && !error && notes.length > 0 && (
        <section>
          <div className="mb-5 flex items-center justify-between">
            <h2 className="text-xl font-semibold text-white">
              Saved Notes
            </h2>

            <span className="text-sm text-gray-500">
              Your personal collection
            </span>
          </div>

          <div className="grid gap-5 md:grid-cols-2">
            {notes.map((note) => (
              <article
                key={note.id}
                className="group flex h-full flex-col rounded-2xl border border-slate-800 bg-slate-900/70 p-6 transition duration-300 hover:-translate-y-1 hover:border-slate-700 hover:bg-slate-800/80"
              >
                <div className="flex items-start justify-between gap-3">
                  <span className="rounded-full bg-emerald-500/10 px-3 py-1 text-xs font-semibold uppercase tracking-wider text-emerald-400">
                    Note
                  </span>

                  <span className="text-xs text-slate-600">
                    #{note.id}
                  </span>
                </div>

                <h3 className="mt-5 text-xl font-semibold leading-snug text-white transition group-hover:text-blue-300">
                  {note.title}
                </h3>

                <p className="mt-3 flex-1 whitespace-pre-wrap break-words text-sm leading-7 text-gray-400">
                  {note.content}
                </p>

                <div className="mt-6 flex gap-3 border-t border-slate-800 pt-4">
                  <button
                    onClick={() => editNote(note)}
                    className="rounded-lg border border-amber-500/30 bg-amber-500/10 px-4 py-2 text-sm font-medium text-amber-300 transition hover:bg-amber-500/20"
                  >
                    Edit
                  </button>

                  <button
                    onClick={() => deleteNote(note.id)}
                    className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-2 text-sm font-medium text-red-300 transition hover:bg-red-500/20"
                  >
                    Delete
                  </button>
                </div>
              </article>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}