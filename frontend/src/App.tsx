import { useState, useCallback } from 'react';
import type { CaseBrief, AppState } from './types';
import { generateBrief } from './api/client';
import Header from './components/Header';
import SearchForm from './components/SearchForm';
import BriefResult from './components/BriefResult';
import LoadingState from './components/LoadingState';
import Footer from './components/Footer';

function App() {
  const [state, setState] = useState<AppState>('idle');
  const [brief, setBrief] = useState<CaseBrief | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [query, setQuery] = useState('');

  const handleSubmit = useCallback(async (searchQuery: string) => {
    setState('loading');
    setError(null);
    setBrief(null);
    setQuery(searchQuery);

    try {
      const result = await generateBrief({ query: searchQuery });
      setBrief(result);
      setState('success');
    } catch (err) {
      const message =
        err instanceof Error ? err.message : 'An unexpected error occurred';
      setError(message);
      setState('error');
    }
  }, []);

  const handleNewSearch = useCallback(() => {
    setState('idle');
    setBrief(null);
    setError(null);
    setQuery('');
  }, []);

  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      <main className="flex-1 flex flex-col">
        {state === 'idle' && <SearchForm onSubmit={handleSubmit} />}

        {state === 'loading' && <LoadingState query={query} />}

        {state === 'success' && brief && (
          <BriefResult
            brief={brief}
            query={query}
            onNewSearch={handleNewSearch}
          />
        )}

        {state === 'error' && (
          <div className="flex-1 flex items-center justify-center px-4 sm:px-6">
            <div className="max-w-lg w-full bg-white rounded-2xl shadow-lg p-8 text-center">
              {/* Error icon */}
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-red-100 flex items-center justify-center">
                <svg
                  className="w-8 h-8 text-red-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={1.5}
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z"
                  />
                </svg>
              </div>

              <h3 className="text-xl font-semibold text-slate-900 mb-2">
                Something went wrong
              </h3>
              <p className="text-slate-600 mb-6">{error}</p>
              <button
                onClick={handleNewSearch}
                className="px-6 py-2.5 bg-indigo-600 text-white rounded-lg
                           hover:bg-indigo-700 transition-colors font-medium"
              >
                Try Again
              </button>
            </div>
          </div>
        )}
      </main>

      <Footer />
    </div>
  );
}

export default App;
