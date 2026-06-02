"use client";

import { createContext, useContext, useState, type ReactNode } from "react";

type Theme = "light";

const ThemeContext = createContext<Theme>("light");

export function ThemeProvider({ children }: { children: ReactNode }) {
  // Only "light" is supported today; there is no toggle yet.
  const [theme] = useState<Theme>("light");
  return <ThemeContext.Provider value={theme}>{children}</ThemeContext.Provider>;
}

export const useTheme = () => useContext(ThemeContext);
