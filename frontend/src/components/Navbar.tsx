export default function Navbar() {
  return (
    <div className="flex items-center justify-between border-b border-slate-700 p-5">
      <h2 className="text-xl font-semibold">
        Mypedia
      </h2>

      <input
        type="text"
        placeholder="Search..."
        className="rounded-lg bg-slate-800 px-4 py-2 outline-none"
      />
    </div>
  );
}