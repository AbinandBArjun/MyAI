import { useEffect, useRef, useState } from "react";
import axios from "axios";

interface Source {
  type: "NOTE" | "ARTICLE";
  id: number;
  title: string;
  score?: number;
}

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
}

export default function AIChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading]);

  const sendMessage = async () => {
    const trimmedMessage = message.trim();

    if (!trimmedMessage || loading) return;

    const userMessage: Message = {
      role: "user",
      content: trimmedMessage,
    };

    setMessages((previous) => [...previous, userMessage]);
    setMessage("");
    setLoading(true);

    try {
      const response = await axios.post(
        "http://localhost:8000/chat/",
        {
          message: trimmedMessage,
        }
      );

      const assistantMessage: Message = {
        role: "assistant",
        content: response.data.response,
        sources: response.data.sources || [],
      };

      setMessages((previous) => [
        ...previous,
        assistantMessage,
      ]);
    } catch (error) {
      console.error("Failed to send message:", error);

      let errorMessage =
        "Something went wrong while processing your request.";
      
      if (axios.isAxiosError(error)) {
        if (!error.response) {
          errorMessage =
            "I couldn't connect to MyAI. Please make sure the backend is running.";
          } else if (error.response.status >= 500) {
            errorMessage =
              "MyAI encountered a server error while processing your request. Please try again.";
          } else if (error.response.status >= 400) {
            errorMessage =
              "MyAI couldn't process that request. Please check your message and try again.";
          }
      }
      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: errorMessage,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const clearConversation = () => {
    if (loading) return;

    setMessages([]);
  };

  return (
    <>
      {/* Floating Button */}
      <button
        onClick={() => setIsOpen((previous) => !previous)}
        className="fixed bottom-4 right-4 z-50 flex h-14 w-14 items-center justify-center rounded-full bg-blue-600 text-2xl shadow-lg transition hover:bg-blue-500 sm:bottom-6 sm:right-6"
        aria-label="Toggle AI assistant"
      >
        {isOpen ? "×" : "✦"}
      </button>

      {/* Chat Panel */}
      {isOpen && (
        <div className="fixed bottom-24 right-4 z-50 flex h-[min(520px,calc(100vh-7rem))] w-[calc(100vw-2rem)] max-w-[360px] flex-col overflow-hidden rounded-2xl border border-slate-700 bg-slate-900 shadow-2xl sm:right-6">
          {/* Header */}
          <div className="flex items-center justify-between border-b border-slate-700 bg-slate-800 px-4 py-4">
            <div>
              <h2 className="font-semibold text-white">
                MyAI
              </h2>

              <p className="text-xs text-gray-400">
                Your personal knowledge assistant
              </p>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={clearConversation}
                disabled={loading || messages.length === 0}
                className="text-xs text-gray-400 transition hover:text-white disabled:cursor-not-allowed disabled:opacity-30"
                aria-label="Clear conversation"
              >
                Clear
              </button>

              <button
                onClick={() => setIsOpen(false)}
                className="text-xl text-gray-400 transition hover:text-white"
                aria-label="Close chat"
              >
                ×
              </button>
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 space-y-4 overflow-y-auto p-4">
            {messages.length === 0 && (
              <div className="mt-12 text-center">
                <div className="text-3xl text-blue-400">
                  ✦
                </div>

                <h3 className="mt-3 font-medium text-white">
                  How can I help?
                </h3>

                <p className="mt-2 text-sm text-gray-400">
                  Ask questions about your notes and saved articles.
                </p>
              </div>
            )}

            {messages.map((item, index) => (
              <div
                key={`${item.role}-${index}`}
                className={`flex ${
                  item.role === "user"
                    ? "justify-end"
                    : "justify-start"
                }`}
              >
                <div
                  className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-6 ${
                    item.role === "user"
                      ? "whitespace-pre-wrap rounded-br-sm bg-blue-600 text-white"
                      : "rounded-bl-sm bg-slate-800 text-gray-200"
                  }`}
                >
                  <div className="whitespace-pre-wrap">
                    {item.content}
                  </div>

                  {item.role === "assistant" &&
                    item.sources &&
                    item.sources.length > 0 && (
                      <div className="mt-3 border-t border-slate-700 pt-3">
                        <p className="mb-2 text-[11px] font-semibold uppercase tracking-wide text-slate-400">
                          Sources
                        </p>

                        <div className="space-y-1.5">
                          {item.sources.map((source) => (
                            <div
                              key={`${source.type}-${source.id}`}
                              className="rounded-lg bg-slate-900/70 px-2.5 py-2"
                            >
                              <div className="flex items-center gap-2">
                                <span className="text-[10px] font-semibold text-blue-400">
                                  {source.type}
                                </span>

                                <span className="truncate text-xs text-slate-300">
                                  {source.title}
                                </span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex justify-start">
                <div className="flex items-center gap-1 rounded-2xl rounded-bl-sm bg-slate-800 px-4 py-3">
                  <span className="h-2 w-2 animate-bounce rounded-full bg-blue-400 [animation-delay:-0.3s]" />
                  <span className="h-2 w-2 animate-bounce rounded-full bg-blue-400 [animation-delay:-0.15s]" />
                  <span className="h-2 w-2 animate-bounce rounded-full bg-blue-400" />
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="border-t border-slate-700 bg-slate-800/80 p-3">
            <div className="flex items-end gap-2">
              <textarea
                value={message}
                onChange={(event) =>
                  setMessage(event.target.value)
                }
                onKeyDown={(event) => {
                  if (
                    event.key === "Enter" &&
                    !event.shiftKey
                  ) {
                    event.preventDefault();
                    sendMessage();
                  }
                }}
                placeholder="Ask your knowledge assistant..."
                rows={2}
                className="min-w-0 flex-1 resize-none rounded-xl border border-slate-600 bg-slate-950 px-3 py-2 text-sm text-white outline-none placeholder:text-slate-600 focus:border-blue-500"
              />

              <button
                onClick={sendMessage}
                disabled={loading || !message.trim()}
                className="rounded-xl bg-blue-600 px-3 py-2 text-sm font-semibold text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-40"
              >
                ↑
              </button>
            </div>

            <p className="mt-2 text-[11px] text-gray-500">
              Enter to send · Shift + Enter for a new line
            </p>
          </div>
        </div>
      )}
    </>
  );
}
