import { useEffect, useState } from 'react';

const PIPELINE_STEPS = [
  { label: 'Searching court opinions', icon: '🔍', durationMs: 8_000 },
  { label: 'Analyzing legal issues', icon: '📋', durationMs: 12_000 },
  { label: 'Drafting case brief', icon: '✍️', durationMs: 12_000 },
  { label: 'Reviewing & verifying citations', icon: '✅', durationMs: 10_000 },
];

interface LoadingStateProps {
  query: string;
}

export default function LoadingState({ query }: LoadingStateProps) {
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    const timers: ReturnType<typeof setTimeout>[] = [];
    let elapsed = 0;

    for (let i = 1; i < PIPELINE_STEPS.length; i++) {
      elapsed += PIPELINE_STEPS[i - 1].durationMs;
      const step = i;
      timers.push(setTimeout(() => setCurrentStep(step), elapsed));
    }

    return () => timers.forEach(clearTimeout);
  }, []);

  return (
    <div className="flex-1 flex items-center justify-center px-4 sm:px-6 py-16">
      <div className="max-w-lg w-full">
        <div className="bg-white rounded-2xl shadow-lg p-6 sm:p-8">
          {/* Query echo */}
          <div className="mb-8 text-center">
            <p className="text-sm text-slate-500 mb-1">Generating brief for</p>
            <p className="font-medium text-slate-900 italic truncate px-4">
              &ldquo;{query}&rdquo;
            </p>
          </div>

          {/* Pipeline Steps */}
          <div className="space-y-3">
            {PIPELINE_STEPS.map((step, index) => {
              const isActive = index === currentStep;
              const isDone = index < currentStep;

              return (
                <div
                  key={step.label}
                  className={`flex items-center gap-4 p-3 rounded-lg transition-all duration-500 ${
                    isActive
                      ? 'bg-indigo-50 border border-indigo-200'
                      : isDone
                        ? 'bg-green-50 border border-green-200'
                        : 'bg-slate-50 border border-transparent'
                  }`}
                >
                  {/* Status icon */}
                  <div className="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center text-lg">
                    {isDone ? (
                      <svg
                        className="w-5 h-5 text-green-600"
                        fill="none"
                        viewBox="0 0 24 24"
                        strokeWidth={2.5}
                        stroke="currentColor"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          d="M4.5 12.75l6 6 9-13.5"
                        />
                      </svg>
                    ) : (
                      <span className={isActive ? 'animate-pulse' : 'opacity-30'}>
                        {step.icon}
                      </span>
                    )}
                  </div>

                  {/* Label */}
                  <span
                    className={`text-sm font-medium transition-colors duration-300 ${
                      isActive
                        ? 'text-indigo-700'
                        : isDone
                          ? 'text-green-700'
                          : 'text-slate-400'
                    }`}
                  >
                    {step.label}
                  </span>

                  {/* Spinner for active step */}
                  {isActive && (
                    <div className="ml-auto">
                      <div className="w-5 h-5 border-2 border-indigo-200 border-t-indigo-600 rounded-full animate-spin" />
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Timing hint */}
          <p className="text-center text-xs text-slate-400 mt-6">
            This typically takes 30–60 seconds
          </p>
        </div>
      </div>
    </div>
  );
}
