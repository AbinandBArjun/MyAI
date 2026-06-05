export default function Dashboard() {
  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-5xl font-bold text-blue-400">
          Mypedia Dashboard
        </h1>

        <p className="mt-2 text-gray-400">
          Your AI knowledge and research hub.
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4">
        <div className="rounded-xl bg-slate-800 p-6">
          <h3 className="text-gray-400">Articles</h3>
          <p className="mt-2 text-3xl font-bold">0</p>
        </div>

        <div className="rounded-xl bg-slate-800 p-6">
          <h3 className="text-gray-400">Notes</h3>
          <p className="mt-2 text-3xl font-bold">0</p>
        </div>

        <div className="rounded-xl bg-slate-800 p-6">
          <h3 className="text-gray-400">Bookmarks</h3>
          <p className="mt-2 text-3xl font-bold">0</p>
        </div>

        <div className="rounded-xl bg-slate-800 p-6">
          <h3 className="text-gray-400">Topics</h3>
          <p className="mt-2 text-3xl font-bold">0</p>
        </div>
      </div>

      {/* Latest News */}
      <div className="rounded-xl bg-slate-800 p-6">
        <h2 className="mb-4 text-2xl font-semibold">
          Latest AI News
        </h2>

        <div className="rounded-lg border border-slate-700 p-4">
          No articles available yet.
        </div>
      </div>

      {/* Trends */}
      <div className="rounded-xl bg-slate-800 p-6">
        <h2 className="mb-4 text-2xl font-semibold">
          Trending Topics
        </h2>

        <div className="flex gap-3">
          <span className="rounded-full bg-blue-600 px-4 py-2">
            GPT
          </span>

          <span className="rounded-full bg-purple-600 px-4 py-2">
            Agents
          </span>

          <span className="rounded-full bg-green-600 px-4 py-2">
            MCP
          </span>
        </div>
      </div>
    </div>
  );
}