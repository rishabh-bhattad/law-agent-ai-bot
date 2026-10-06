import { useState } from 'react';
import type { CaseBrief } from '../types';

interface BriefResultProps {
  brief: CaseBrief;
  query: string;
  onNewSearch: () => void;
}

export default function BriefResult({ brief, query, onNewSearch }: BriefResultProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    const text = [
      'CASE BRIEF',
      '',
      `Case Name: ${brief.caseName}`,
      '',
      'Holding:',
      brief.holding,
      '',
      'Reasoning:',
      brief.reasoning,
      '',
      'Citations:',
      ...brief.citation.map((c, i) => `  ${i + 1}. ${c}`),
    ].join('\n');

    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Clipboard API not available — silent fallback
    }
  };

  return (
    <div className="flex-1 px-4 sm:px-6 py-8 sm:py-10">
      <div className="max-w-3xl mx-auto">
        {/* Top bar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
          <div className="min-w-0">
            <p className="text-sm text-slate-500">Brief generated for</p>
            <p className="text-sm font-medium text-slate-700 italic truncate">
              &ldquo;{query}&rdquo;
            </p>
          </div>
          <button
            onClick={onNewSearch}
            className="self-start sm:self-auto flex-shrink-0 px-4 py-2 text-sm bg-white border border-slate-200
                       rounded-lg hover:bg-slate-50 hover:border-slate-300 transition-all
                       text-slate-700 flex items-center gap-2"
          >
            <svg
              className="w-4 h-4"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1.5}
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z"
              />
            </svg>
            New Search
          </button>
        </div>

        {/* Brief Card */}
        <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
          {/* Case Name banner */}
          <div className="bg-slate-900 px-6 sm:px-8 py-6">
            <p className="text-[11px] uppercase tracking-widest text-slate-400 mb-2 font-medium">
              Case Name
            </p>
            <h2 className="font-serif text-xl sm:text-2xl font-bold text-white leading-snug">
              {brief.caseName}
            </h2>
          </div>

          <div className="divide-y divide-slate-100">
            {/* Holding */}
            <section className="px-6 sm:px-8 py-6">
              <div className="flex items-center gap-2 mb-3">
                <div className="w-1 h-5 bg-indigo-500 rounded-full" />
                <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Holding
                </h3>
              </div>
              <p className="text-slate-800 leading-relaxed">{brief.holding}</p>
            </section>

            {/* Reasoning */}
            <section className="px-6 sm:px-8 py-6">
              <div className="flex items-center gap-2 mb-3">
                <div className="w-1 h-5 bg-amber-500 rounded-full" />
                <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Reasoning
                </h3>
              </div>
              <p className="text-slate-800 leading-relaxed whitespace-pre-line">
                {brief.reasoning}
              </p>
            </section>

            {/* Citations */}
            <section className="px-6 sm:px-8 py-6">
              <div className="flex items-center gap-2 mb-3">
                <div className="w-1 h-5 bg-green-500 rounded-full" />
                <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Citations ({brief.citation.length})
                </h3>
              </div>
              <ul className="space-y-2">
                {brief.citation.map((cite, index) => (
                  <li key={index} className="flex items-start gap-3">
                    <span
                      className="flex-shrink-0 w-6 h-6 rounded-full bg-slate-100 text-slate-500
                                 text-xs flex items-center justify-center font-medium mt-0.5"
                    >
                      {index + 1}
                    </span>
                    <span className="text-slate-700 leading-relaxed">{cite}</span>
                  </li>
                ))}
              </ul>
            </section>
          </div>
        </div>

        {/* Copy action */}
        <div className="mt-6 flex justify-center">
          <button
            onClick={handleCopy}
            className="px-5 py-2.5 text-sm bg-slate-100 text-slate-700 rounded-lg
                       hover:bg-slate-200 transition-all flex items-center gap-2"
          >
            {copied ? (
              <>
                <svg
                  className="w-4 h-4 text-green-600"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={2}
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M4.5 12.75l6 6 9-13.5"
                  />
                </svg>
                <span className="text-green-700">Copied!</span>
              </>
            ) : (
              <>
                <svg
                  className="w-4 h-4"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={1.5}
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M15.666 3.888A2.25 2.25 0 0013.5 2.25h-3c-1.03 0-1.9.693-2.166 1.638m7.332 0c.055.194.084.4.084.612v0a.75.75 0 01-.75.75H9.75a.75.75 0 01-.75-.75v0c0-.212.03-.418.084-.612m7.332 0c.646.049 1.288.11 1.927.184 1.1.128 1.907 1.077 1.907 2.185V19.5a2.25 2.25 0 01-2.25 2.25H6.75A2.25 2.25 0 014.5 19.5V6.257c0-1.108.806-2.057 1.907-2.185a48.208 48.208 0 011.927-.184"
                  />
                </svg>
                Copy to Clipboard
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
