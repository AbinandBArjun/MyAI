import { useState } from "react";
import axios from "axios";

export default function Chat() {
  const [message, setMessage] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
  if (!message) return;

  setLoading(true);

  try {
    const res = await axios.post(
      "http://localhost:8000/chat/",
      {
        message,
      }
    );

    setResponse(res.data.response);
  } catch (error) {
    console.error(error);
  } finally {
    setLoading(false);
  }
};

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-4xl font-bold">
          AI Chat
        </h1>

        <p className="mt-2 text-gray-400">
          Chat with your local AI assistant.
        </p>
      </div>

      <div className="rounded-xl bg-slate-800 p-6 space-y-4">
        <textarea
          value={message}
          onChange={(e) =>
            setMessage(e.target.value)
          }
          placeholder="Ask anything..."
          rows={4}
          className="w-full rounded-lg bg-slate-700 p-3"
        />

        <button
            onClick={sendMessage}
            disabled={loading}
            className="rounded-lg bg-blue-600 px-5 py-2 disabled:opacity-50"
          >
            {loading ? "Thinking..." : "Send"}
</button>
      </div>

      {response && (
        <div className="rounded-xl bg-slate-800 p-6">
          <h2 className="mb-3 text-xl font-semibold">
            Response
          </h2>

          <p className="whitespace-pre-wrap">
            {response}
          </p>
        </div>
      )}
    </div>
  );
}