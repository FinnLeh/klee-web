import { createContext, useContext, useEffect, useState, type ReactNode } from "react"

type Theme = "system" | "dark" | "light"
type ResolvedTheme = "dark" | "light"
type ResultsPosition = "right" | "below"

type SettingsValue = {
  theme: Theme
  resolvedTheme: ResolvedTheme
  resultsPosition: ResultsPosition
  setTheme: (t: Theme) => void
  setResultsPosition: (p: ResultsPosition) => void
}

const SettingsContext = createContext<SettingsValue | null>(null)

const THEME_KEY = "klee.theme"
const RESULTS_POSITION_KEY = "klee.resultsPosition"

function readTheme(): Theme {
  const stored = localStorage.getItem(THEME_KEY)
  if (stored === "system" || stored === "dark" || stored === "light") return stored
  return "system"
}

function readResultsPosition(): ResultsPosition {
  const stored = localStorage.getItem(RESULTS_POSITION_KEY)
  if (stored === "right" || stored === "below") return stored
  return "right"
}

export function SettingsProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>(readTheme)
  const [resultsPosition, setResultsPosition] = useState<ResultsPosition>(readResultsPosition)
  const [systemPrefersDark, setSystemPrefersDark] = useState<boolean>(
    () => window.matchMedia("(prefers-color-scheme: dark)").matches,
  )

  useEffect(() => {
    const mql = window.matchMedia("(prefers-color-scheme: dark)")
    const onChange = () => setSystemPrefersDark(mql.matches)
    mql.addEventListener("change", onChange)
    return () => mql.removeEventListener("change", onChange)
  }, [])

  const resolvedTheme: ResolvedTheme =
    theme === "dark" ? "dark"
    : theme === "light" ? "light"
    : systemPrefersDark ? "dark" : "light"

  useEffect(() => {
    document.documentElement.classList.toggle("dark", resolvedTheme === "dark")
  }, [resolvedTheme])

  useEffect(() => {
    localStorage.setItem(THEME_KEY, theme)
  }, [theme])

  useEffect(() => {
    localStorage.setItem(RESULTS_POSITION_KEY, resultsPosition)
  }, [resultsPosition])

  return (
    <SettingsContext.Provider
      value={{ theme, resolvedTheme, resultsPosition, setTheme, setResultsPosition }}
    >
      {children}
    </SettingsContext.Provider>
  )
}

// eslint-disable-next-line react-refresh/only-export-components
export function useSettings() {
  const ctx = useContext(SettingsContext)
  if (ctx === null) throw new Error("useSettings must be used within SettingsProvider")
  return ctx
}
