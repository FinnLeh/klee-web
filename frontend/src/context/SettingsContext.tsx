import { createContext, useContext, useEffect, useState, type ReactNode } from "react"

type Theme = "system" | "dark" | "light"
type ResultsPosition = "right" | "below"

type SettingsValue = {
  theme: Theme
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

  useEffect(() => {
    const mql = window.matchMedia("(prefers-color-scheme: dark)")
    const apply = () => {
      const shouldBeDark =
        theme === "dark" || (theme === "system" && mql.matches)
      document.documentElement.classList.toggle("dark", shouldBeDark)
    }
    apply()
    if (theme === "system") {
      mql.addEventListener("change", apply)
      return () => mql.removeEventListener("change", apply)
    }
  }, [theme])

  useEffect(() => {
    localStorage.setItem(THEME_KEY, theme)
  }, [theme])

  useEffect(() => {
    localStorage.setItem(RESULTS_POSITION_KEY, resultsPosition)
  }, [resultsPosition])

  return (
    <SettingsContext.Provider
      value={{ theme, resultsPosition, setTheme, setResultsPosition }}
    >
      {children}
    </SettingsContext.Provider>
  )
}

export function useSettings() {
  const ctx = useContext(SettingsContext)
  if (ctx === null) throw new Error("useSettings must be used within SettingsProvider")
  return ctx
}
