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

  const API_URL = "http://localhost:8000/notes";

  const fetchNotes = async () => {
    try {
      const response = await axios.get(API_URL);
      setNotes(response.data);
    } catch (error) {
      console.error(error);
    }
  };

  const createNote = async () => {
    if (!title || !content) return;

    try {
      await axios.post(API_URL, {
        title,
        content,
      });

      setTitle("");
      setContent("");

      fetchNotes();
    } catch (error) {
      console.error(error);
    }
  };

  const deleteNote = async (id: number) => {
    try {
      await axios.delete(`${API_URL}/${id}`);
      fetchNotes();
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    fetchNotes();
  }, []);

  return (
    <div className="space-y-6">
      <h1 className="text-4xl font-bold">My Notes</h1>

      <div className="rounded-xl bg-slate-800 p-6 space-y-4">
        <input
          type="text"
          placeholder="Note Title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="w-full rounded-lg bg-slate-700 p-3"
        />

        <textarea
          placeholder="Note Content"
          value={content}
          onChange={(e) => setContent(e.target.value)}
          className="w-full rounded-lg bg-slate-700 p-3"
          rows={4}
        />

        <button
          onClick={createNote}
          className="rounded-lg bg-blue-600 px-5 py-2"
        >
          Create Note
        </button>
      </div>

      <div className="space-y-4">
        {notes.map((note) => (
          <div
            key={note.id}
            className="rounded-xl bg-slate-800 p-5"
          >
            <h2 className="text-xl font-semibold">
              {note.title}
            </h2>

            <p className="mt-2 text-gray-300">
              {note.content}
            </p>

            <button
              onClick={() => deleteNote(note.id)}
              className="mt-4 rounded bg-red-600 px-4 py-2"
            >
              Delete
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}