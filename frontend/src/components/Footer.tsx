export default function Footer() {
  return (
    <footer className="bg-white border-t border-slate-200 py-4 mt-auto">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 text-center">
        <p className="text-xs text-slate-400">
          Powered by{' '}
          <a
            href="https://www.courtlistener.com"
            target="_blank"
            rel="noopener noreferrer"
            className="text-slate-500 hover:text-indigo-600 underline decoration-slate-300 underline-offset-2 transition-colors"
          >
            CourtListener
          </a>
          {' '}&amp;{' '}
          <a
            href="https://deepmind.google/technologies/gemini/"
            target="_blank"
            rel="noopener noreferrer"
            className="text-slate-500 hover:text-indigo-600 underline decoration-slate-300 underline-offset-2 transition-colors"
          >
            Google Gemini
          </a>
          .{' '}
          <span className="text-slate-400">Not legal advice.</span>
        </p>
        <p className="text-xs text-slate-500 mt-2 font-medium">
          Built with <span className="text-red-500">❤️</span> by Rish
        </p>
      </div>
    </footer>
  );
}
