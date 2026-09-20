import { NavLink } from "react-router-dom";

const navigationItems = [
  { name: "Dashboard", path: "/", icon: "⌂", end: true },
  { name: "News", path: "/news", icon: "◈" },
  { name: "Notes", path: "/notes", icon: "▤" },
  { name: "Chat", path: "/chat", icon: "◌" },
  { name: "Trends", path: "/trends", icon: "↗" },
];

export default function Sidebar() {
  return (
    <aside className="flex min-h-screen w-64 flex-col border-r border-slate-800 bg-slate-950 px-4 py-6">
      {/* Branding */}
      <div className="mb-10 px-3">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-blue-600 text-xl font-bold">
            M
          </div>

          <div>
            <h1 className="text-xl font-bold tracking-tight text-white">
              Mypedia
            </h1>

            <p className="text-xs text-slate-500">
              Your knowledge space
            </p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex flex-1 flex-col gap-2">
        <p className="mb-2 px-3 text-xs font-semibold uppercase tracking-wider text-slate-500">
          Workspace
        </p>

        {navigationItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.end}
            className={({ isActive }) =>
              [
                "flex items-center gap-3 rounded-xl px-3 py-3 text-sm font-medium transition-all duration-200",
                isActive
                  ? "bg-blue-600/15 text-blue-400"
                  : "text-slate-400 hover:bg-slate-800 hover:text-white",
              ].join(" ")
            }
          >
            <span className="flex w-6 justify-center text-lg">
              {item.icon}
            </span>

            <span>{item.name}</span>
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="border-t border-slate-800 pt-4">
        <p className="px-3 text-xs text-slate-600">
          Mypedia · Personal Knowledge
        </p>
      </div>
    </aside>
  );
}