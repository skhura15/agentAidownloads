import { useState } from 'react'

interface SessionExpiryWarningProps {
  /** Seconds remaining before the session expires */
  secondsRemaining: number
  /** Called when user clicks "Continue Session" */
  onContinue: () => Promise<void>
  /** Called when user dismisses the banner without continuing */
  onDismiss: () => void
}

export default function SessionExpiryWarning({
  secondsRemaining,
  onContinue,
  onDismiss,
}: SessionExpiryWarningProps) {
  const [isKeepingAlive, setIsKeepingAlive] = useState(false)

  const minutes = Math.floor(secondsRemaining / 60)
  const seconds = secondsRemaining % 60
  const timeLabel =
    minutes > 0
      ? `${minutes}m ${seconds}s`
      : `${seconds}s`

  const handleContinue = async () => {
    setIsKeepingAlive(true)
    try {
      await onContinue()
    } finally {
      setIsKeepingAlive(false)
    }
  }

  return (
    <div className="absolute top-0 left-0 right-0 z-40 animate-slide-down">
      <div className="mx-4 mt-3 rounded-lg border border-amber-300 dark:border-amber-600 bg-amber-50 dark:bg-amber-900/60 shadow-lg px-4 py-3 flex items-center justify-between gap-4">
        {/* Icon + message */}
        <div className="flex items-center gap-3 min-w-0">
          <div className="flex-shrink-0">
            <svg
              className="h-5 w-5 text-amber-500 dark:text-amber-400"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth="2"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z"
              />
            </svg>
          </div>
          <p className="text-sm font-medium text-amber-800 dark:text-amber-200 truncate">
            Your session will expire due to inactivity in{' '}
            <span className="font-bold tabular-nums">{timeLabel}</span>
          </p>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-2 flex-shrink-0">
          <button
            onClick={handleContinue}
            disabled={isKeepingAlive}
            className="inline-flex items-center gap-1.5 rounded-md bg-amber-600 hover:bg-amber-700 disabled:bg-amber-400 px-3 py-1.5 text-sm font-semibold text-white shadow-sm transition-colors"
          >
            {isKeepingAlive ? (
              <>
                <svg
                  className="animate-spin h-4 w-4"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                  />
                </svg>
                Extending...
              </>
            ) : (
              'Continue Session'
            )}
          </button>
          <button
            onClick={onDismiss}
            className="rounded-md p-1 text-amber-600 hover:text-amber-800 dark:text-amber-400 dark:hover:text-amber-200 transition-colors"
            aria-label="Dismiss"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" strokeWidth="2" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  )
}
