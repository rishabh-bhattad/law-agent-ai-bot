import { useState } from 'react';

const EXAMPLE_QUERIES = [
  'Fourth Amendment search and seizure automobile exception',
  'First Amendment free speech in public schools',
  'Due process rights in criminal sentencing',
  'Equal protection clause racial discrimination',
];

interface SearchFormProps {
  onSubmit: (query: string) => void;
}

export default function SearchForm({ onSubmit }: SearchFormProps) {
  const [query, setQuery] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = query.trim();
    if (trimmed) {
      onSubmit(trimmed);
    }
  };

  return (
    <div className="flex-1 flex flex-col items-center justify-center px-4 sm:px-6 py-12 sm:py-20">
      <div className="max-w-2xl w-full text-center">
        {/* Hero */}
        <h2 className="font-serif text-3xl sm:text-4xl md:text-5xl font-bold text-slate-900 mb-4 leading-tight">
          Research Case Law
          <br />
          in Seconds
        </h2>
        <p className="text-base sm:text-lg text-slate-600 mb-10 max-w-xl mx-auto leading-relaxed">
          Enter a legal query and our AI will search court opinions, analyze the
          issues, and generate a structured case brief — complete with holdings,
          reasoning, and citations.
        </p>

        {/* Search Form */}
        <form onSubmit={handleSubmit} className="mb-8">
          <div className="flex flex-col sm:flex-row gap-3">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g., Fourth Amendment search and seizure…"
              className="flex-1 px-5 py-3.5 text-base rounded-xl border-2 border-slate-200
                         focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100
                         outline-none transition-all bg-white shadow-sm
                         placeholder:text-slate-400"
              autoFocus
            />
            <button
              type="submit"
              disabled={!query.trim()}
              className="px-8 py-3.5 bg-indigo-600 text-white font-semibold rounded-xl
                         hover:bg-indigo-700 active:bg-indigo-800 transition-all
                         disabled:bg-slate-300 disabled:cursor-not-allowed
                         shadow-sm hover:shadow-md whitespace-nowrap"
            >
              Generate Brief
            </button>
          </div>
        </form>

        {/* Example Queries */}
        <div>
          <p className="text-sm text-slate-500 mb-3">Try an example:</p>
          <div className="flex flex-wrap justify-center gap-2">
            {EXAMPLE_QUERIES.map((example) => (
              <button
                key={example}
                type="button"
                onClick={() => {
                  setQuery(example);
                  onSubmit(example);
                }}
                className="px-3 py-1.5 text-sm bg-white border border-slate-200 rounded-full
                           text-slate-600 hover:border-indigo-300 hover:text-indigo-700
                           hover:bg-indigo-50 transition-all cursor-pointer"
              >
                {example}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
