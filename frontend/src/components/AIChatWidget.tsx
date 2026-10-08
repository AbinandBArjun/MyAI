import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
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

interface AIChatContext {
  type: "NOTE" | "ARTICLE";
  id: number;
  title?: string;
}

interface AIChatWidgetProps {
  context?: AIChatContext;
}

type ContextMode = "AUTO" | "NOTE" | "ARTICLE" | "GLOBAL";

export default function AIChatWidget({
  context,
}: AIChatWidgetProps) {
  const navigate = useNavigate();

  const [isOpen, setIsOpen] = useState(false);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);

  const [contextMode, setContextMode] =
    useState<ContextMode>("AUTO");

  const messagesEndRef =
    useRef<HTMLDivElement | null>(null);

  const inputRef =
    useRef<HTMLInputElement | null>(null);

  /*
   * When the current page changes:
   *
   * Note #12 → Note #15
   * Note #12 → Article #1
   * Article #1 → Notes list
   *
   * reset the context and conversation so that
   * messages from the previous document are not
   * incorrectly associated with the new document.
   */
  useEffect(() => {
    setContextMode("AUTO");
    setMessages([]);
    setInput("");
  }, [context?.type, context?.id]);

  /*
   * Scroll to the newest message.
   */
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, loading]);

  /*
   * Focus the input whenever the widget opens.
   */
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => {
        inputRef.current?.focus();
      }, 100);
    }
  }, [isOpen]);

  /*
   * Determine which context is actually active.
   */
  const activeContext =
    contextMode === "GLOBAL"
      ? undefined
      : context;

  const isUsingSpecificContext =
    activeContext !== undefined;

  /*
   * Human-readable context name.
   */
  const getContextLabel = () => {
    if (contextMode === "GLOBAL") {
      return "Entire Knowledge Base";
    }

    if (activeContext) {
      return (
        activeContext.title ||
        `${activeContext.type} #${activeContext.id}`
      );
    }

    return "Entire Knowledge Base";
  };

  /*
   * Short context type shown in the header.
   */
  const getContextTypeLabel = () => {
    if (contextMode === "GLOBAL") {
      return "GLOBAL";
    }

    if (activeContext) {
      return activeContext.type;
    }

    return "GLOBAL";
  };

  /*
   * Send a message to the backend.
   */
  const sendMessage = async () => {
    const trimmedMessage = input.trim();

    if (!trimmedMessage || loading) {
      return;
    }

    const userMessage: Message = {
      role: "user",
      content: trimmedMessage,
    };

    setMessages((previous) => [
      ...previous,
      userMessage,
    ]);

    setInput("");
    setLoading(true);

    try {
      const requestBody = {
        message: trimmedMessage,

        /*
         * When a specific note/article is active,
         * send its type and ID.
         *
         * When GLOBAL is selected, no context is
         * sent and the backend performs normal RAG.
         */
        ...(isUsingSpecificContext && activeContext
          ? {
              context: {
                type: activeContext.type,
                id: activeContext.id,
              },
            }
          : {}),
      };

      const response = await axios.post(
        "http://localhost:8000/chat/",
        requestBody
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
      console.error(
        "Chat request failed:",
        error
      );

      const errorMessage: Message = {
        role: "assistant",
        content:
          "Sorry, I couldn't process your request. Please make sure the backend server is running and try again.",
        sources: [],
      };

      setMessages((previous) => [
        ...previous,
        errorMessage,
      ]);
    } finally {
      setLoading(false);
    }
  };

  /*
   * Enter sends the message.
   */
  const handleKeyDown = (
    event: React.KeyboardEvent<HTMLInputElement>
  ) => {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault();
      sendMessage();
    }
  };

  /*
   * Open a source from an AI response.
   */
  const openSource = (source: Source) => {
    if (source.type === "NOTE") {
      navigate(`/notes/${source.id}`);
    } else {
      navigate(`/news/${source.id}`);
    }

    setIsOpen(false);
  };

  /*
   * Manually clear the conversation.
   */
  const clearChat = () => {
    setMessages([]);
    setInput("");
  };

  /*
   * Changing context starts a fresh conversation.
   */
  const handleContextChange = (
    event: React.ChangeEvent<HTMLSelectElement>
  ) => {
    const newMode =
      event.target.value as ContextMode;

    setContextMode(newMode);

    /*
     * Do not carry a conversation from one
     * context into another.
     */
    setMessages([]);
    setInput("");
  };

  return (
    <>
      {/* Floating Button */}
      {!isOpen && (
        <button
          type="button"
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 z-50 flex h-14 w-14 items-center justify-center rounded-full bg-blue-600 text-white shadow-lg shadow-blue-900/30 transition hover:scale-105 hover:bg-blue-500"
          aria-label="Open AI assistant"
        >
          <span className="text-xl">
            ✦
          </span>
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 z-50 flex h-[650px] w-[390px] max-w-[calc(100vw-2rem)] flex-col overflow-hidden rounded-2xl border border-slate-700 bg-slate-950 shadow-2xl shadow-black/40">

          {/* Header */}
          <div className="border-b border-slate-800 bg-slate-900 px-4 py-3">

            <div className="flex items-center justify-between">

              <div className="flex min-w-0 items-center gap-2">

                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-blue-600/20 text-blue-400">
                  ✦
                </div>

                <div className="min-w-0">
                  <h2 className="text-sm font-semibold text-white">
                    Mypedia AI
                  </h2>

                  <p className="text-[11px] text-slate-500">
                    Knowledge assistant
                  </p>
                </div>

              </div>

              <div className="flex items-center gap-1">

                {messages.length > 0 && (
                  <button
                    type="button"
                    onClick={clearChat}
                    className="rounded-lg px-2 py-1.5 text-xs text-slate-500 transition hover:bg-slate-800 hover:text-slate-300"
                    title="Clear chat"
                  >
                    Clear
                  </button>
                )}

                <button
                  type="button"
                  onClick={() =>
                    setIsOpen(false)
                  }
                  className="rounded-lg px-2 py-1 text-lg text-slate-500 transition hover:bg-slate-800 hover:text-white"
                  aria-label="Close AI assistant"
                >
                  ×
                </button>

              </div>

            </div>

            {/* Context Selector */}
            <div className="mt-3">

              <div className="mb-1.5 flex items-center justify-between">

                <label
                  htmlFor="ai-context"
                  className="text-[10px] font-semibold uppercase tracking-wide text-slate-500"
                >
                  Context
                </label>

                <span className="text-[10px] text-slate-600">
                  {getContextTypeLabel()}
                </span>

              </div>

              <select
                id="ai-context"
                value={contextMode}
                onChange={handleContextChange}
                className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-xs text-slate-300 outline-none transition focus:border-blue-500"
              >

                <option value="AUTO">
                  Current Page
                </option>

                {context?.type === "NOTE" && (
                  <option value="NOTE">
                    Current Note
                  </option>
                )}

                {context?.type === "ARTICLE" && (
                  <option value="ARTICLE">
                    Current Article
                  </option>
                )}

                <option value="GLOBAL">
                  Entire Knowledge Base
                </option>

              </select>

              <div className="mt-1.5 truncate text-[10px] text-slate-600">
                {getContextLabel()}
              </div>

            </div>

          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-4 py-4">

            {messages.length === 0 && (
              <div className="flex h-full items-center justify-center">

                <div className="max-w-[290px] text-center">

                  <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-500/10 text-2xl text-blue-400">
                    ✦
                  </div>

                  <h3 className="mt-4 text-sm font-semibold text-white">
                    Ask Mypedia AI
                  </h3>

                  <p className="mt-2 text-xs leading-5 text-slate-500">
                    Ask questions about your
                    notes, articles, or knowledge
                    base. Relevant sources will be
                    shown with each answer.
                  </p>

                  <div className="mt-4 rounded-xl border border-blue-500/20 bg-blue-500/5 px-3 py-2.5 text-left">

                    <p className="text-[10px] font-semibold uppercase tracking-wide text-blue-400">
                      Current Context
                    </p>

                    <p className="mt-1 truncate text-xs text-slate-300">
                      {getContextLabel()}
                    </p>

                  </div>

                </div>

              </div>
            )}

            <div className="space-y-4">

              {messages.map(
                (item, index) => (
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
                          ? "rounded-br-sm bg-blue-600 text-white"
                          : "rounded-bl-sm bg-slate-800 text-gray-200"
                      }`}
                    >

                      <div className="whitespace-pre-wrap">
                        {item.content}
                      </div>

                      {/* Sources */}
                      {item.role ===
                        "assistant" &&
                        item.sources &&
                        item.sources.length >
                          0 && (
                          <div className="mt-3 border-t border-slate-700 pt-3">

                            <p className="mb-2 text-[11px] font-semibold uppercase tracking-wide text-slate-400">
                              Sources
                            </p>

                            <div className="space-y-1.5">

                              {item.sources.map(
                                (source) => (
                                  <button
                                    key={`${source.type}-${source.id}`}
                                    type="button"
                                    onClick={() =>
                                      openSource(
                                        source
                                      )
                                    }
                                    className="w-full rounded-lg bg-slate-900/70 px-2.5 py-2 text-left transition hover:bg-slate-700/80"
                                  >

                                    <div className="flex items-center gap-2">

                                      <span className="shrink-0 text-[10px] font-semibold text-blue-400">
                                        {
                                          source.type
                                        }
                                      </span>

                                      <span
                                        className="truncate text-xs text-slate-300"
                                        title={
                                          source.title
                                        }
                                      >
                                        {
                                          source.title
                                        }
                                      </span>

                                      <span className="ml-auto shrink-0 text-xs text-slate-500">
                                        →
                                      </span>

                                    </div>

                                    {typeof source.score === "number" ? (
                                      <div className="mt-1 text-[10px] text-slate-600">
                                        Relevance:{" "}
                                        {(source.score * 100).toFixed(1)}%
                                      </div>  
                                    ) : (
                                      <div className="mt-1 text-[10px] text-blue-400/70">
                                        Current context
                                      </div>
                                      )}
                                      
                                      
                                    

                                  </button>
                                )
                              )}

                            </div>

                          </div>
                        )}

                    </div>

                  </div>
                )
              )}

              {/* Loading Indicator */}
              {loading && (
                <div className="flex justify-start">

                  <div className="rounded-2xl rounded-bl-sm bg-slate-800 px-4 py-3">

                    <div className="flex items-center gap-1.5">

                      <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-500" />

                      <span
                        className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-500"
                        style={{
                          animationDelay:
                            "120ms",
                        }}
                      />

                      <span
                        className="h-1.5 w-1.5 animate-bounce rounded-full bg-slate-500"
                        style={{
                          animationDelay:
                            "240ms",
                        }}
                      />

                    </div>

                  </div>

                </div>
              )}

              <div ref={messagesEndRef} />

            </div>

          </div>

          {/* Input */}
          <div className="border-t border-slate-800 bg-slate-900 p-3">

            <div className="flex items-center gap-2 rounded-xl border border-slate-700 bg-slate-950 px-3 py-2 focus-within:border-blue-500">

              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={(event) =>
                  setInput(event.target.value)
                }
                onKeyDown={handleKeyDown}
                disabled={loading}
                placeholder={
                  contextMode === "GLOBAL"
                    ? "Ask Mypedia AI..."
                    : activeContext
                    ? `Ask about this ${activeContext.type.toLowerCase()}...`
                    : "Ask Mypedia AI..."
                }
                className="min-w-0 flex-1 bg-transparent text-sm text-white outline-none placeholder:text-slate-600 disabled:cursor-not-allowed disabled:opacity-50"
              />

              <button
                type="button"
                onClick={sendMessage}
                disabled={
                  loading ||
                  !input.trim()
                }
                className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-blue-600 text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-30"
                aria-label="Send message"
              >
                ↑
              </button>

            </div>

            <p className="mt-2 text-center text-[10px] text-slate-600">
              Press Enter to send
            </p>

          </div>

        </div>
      )}
    </>
  );
}