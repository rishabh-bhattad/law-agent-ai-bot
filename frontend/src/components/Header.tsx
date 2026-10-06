export default function Header() {
  return (
    <header className="bg-slate-900 text-white">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-4 flex items-center gap-3">
        <span className="text-2xl" role="img" aria-label="scales of justice">
          ⚖️
        </span>
        <div>
          <h1 className="text-lg font-bold tracking-tight leading-tight">
            CaseBrief AI
          </h1>
          <p className="text-xs text-slate-400 hidden sm:block">
            AI-Powered Legal Case Briefing
          </p>
        </div>
      </div>
    </header>
  );
}
