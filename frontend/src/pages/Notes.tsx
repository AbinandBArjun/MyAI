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


  const updateNote = async () => {
  if (!title || !content || editingId === null) return;

  try {
    await axios.put(`${API_URL}/${editingId}`, {
      title,
      content,
    });

    setTitle("");
    setContent("");
    setEditingId(null);

    fetchNotes();
  } catch (error) {
    console.error(error);
  }
  };
  const editNote = (note: Note) => {
  setTitle(note.title);
  setContent(note.content);
  setEditingId(note.id);
  };

  const deleteNote = async (id: number) => {
  try {
    await axios.delete(`${API_URL}/${id}`);

    if (editingId === id) {
      setEditingId(null);
      setTitle("");
      setContent("");
    }

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
          onClick={
            editingId === null
              ? createNote
              : updateNote
            }
            className="rounded-lg bg-blue-600 px-5 py-2"
          >
            {editingId === null
              ? "Create Note"
              : "Update Note"}
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

            <div className="mt-4 flex gap-3">
      <button
        onClick={() => editNote(note)}
          className="rounded bg-yellow-600 px-4 py-2"
        >
          Edit
      </button>

  <button
    onClick={() => deleteNote(note.id)}
    className="rounded bg-red-600 px-4 py-2"
  >
    Delete
  </button>
</div>
          </div>
        ))}
      </div>
    </div>
  );
}