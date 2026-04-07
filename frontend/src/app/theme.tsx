import CssBaseline from "@mui/material/CssBaseline";
import GlobalStyles from "@mui/material/GlobalStyles";
import { alpha, createTheme, responsiveFontSizes, ThemeProvider, type PaletteMode } from "@mui/material/styles";
import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";

const COLOR_MODE_STORAGE_KEY = "character-battle-color-mode";

type ColorModeContextValue = {
  mode: PaletteMode;
  toggleMode: () => void;
};

const ColorModeContext = createContext<ColorModeContextValue | null>(null);

type AppThemeProviderProps = {
  children: ReactNode;
};

export function AppThemeProvider({ children }: AppThemeProviderProps) {
  const [mode, setMode] = useState<PaletteMode>(getInitialMode);
  const theme = buildTheme(mode);

  useEffect(() => {
    window.localStorage.setItem(COLOR_MODE_STORAGE_KEY, mode);
  }, [mode]);

  return (
    <ColorModeContext.Provider
      value={{
        mode,
        toggleMode: () => setMode((prevMode) => (prevMode === "dark" ? "light" : "dark")),
      }}
    >
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <GlobalStyles
          styles={{
            a: {
              color: "inherit",
              textDecoration: "none",
            },
            "*, *::before, *::after": {
              boxSizing: "border-box",
            },
            "#root": {
              minHeight: "100vh",
            },
            body: {
              WebkitFontSmoothing: "antialiased",
              MozOsxFontSmoothing: "grayscale",
              overflowX: "hidden",
              wordBreak: "keep-all",
            },
            "button, input, textarea": {
              font: "inherit",
            },
            code: {
              fontFamily: '"IBM Plex Mono", monospace',
            },
          }}
        />
        {children}
      </ThemeProvider>
    </ColorModeContext.Provider>
  );
}

export function useAppColorMode() {
  const context = useContext(ColorModeContext);

  if (!context) {
    throw new Error("useAppColorMode must be used inside AppThemeProvider.");
  }

  return context;
}

function getInitialMode(): PaletteMode {
  if (typeof window === "undefined") {
    return "dark";
  }

  const storedMode = window.localStorage.getItem(COLOR_MODE_STORAGE_KEY);
  if (storedMode === "dark" || storedMode === "light") {
    return storedMode;
  }

  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function buildTheme(mode: PaletteMode) {
  const isDark = mode === "dark";
  const shadowColor = isDark ? "rgba(5, 10, 20, 0.26)" : "rgba(18, 29, 58, 0.08)";

  let theme = createTheme({
    palette: {
      mode,
      primary: {
        main: "#4263eb",
        light: isDark ? "#8fa3ff" : "#2f55ef",
        dark: "#2847c7",
        contrastText: "#ffffff",
      },
      secondary: {
        main: "#ff6b3d",
        light: isDark ? "#ff9d80" : "#ff845d",
        dark: "#d55127",
      },
      background: {
        default: isDark ? "#0b111b" : "#f4f7fb",
        paper: isDark ? alpha("#121a26", 0.92) : alpha("#ffffff", 0.96),
      },
      text: {
        primary: isDark ? "#eef3ff" : "#172133",
        secondary: isDark ? alpha("#eef3ff", 0.72) : alpha("#172133", 0.66),
      },
      divider: isDark ? alpha("#d7e0ff", 0.12) : alpha("#223253", 0.1),
      error: {
        main: "#ef5a5a",
      },
      success: {
        main: isDark ? "#62cc89" : "#2d9b62",
      },
    },
    shape: {
      borderRadius: 4,
    },
    typography: {
      fontFamily: '"Inter", "Noto Sans KR", "Apple SD Gothic Neo", "Malgun Gothic", sans-serif',
      h1: {
        fontFamily: '"Inter", "Noto Sans KR", "Apple SD Gothic Neo", "Malgun Gothic", sans-serif',
        fontWeight: 700,
        letterSpacing: "-0.03em",
        lineHeight: 1.18,
      },
      h2: {
        fontFamily: '"Inter", "Noto Sans KR", "Apple SD Gothic Neo", "Malgun Gothic", sans-serif',
        fontWeight: 700,
        letterSpacing: "-0.03em",
        lineHeight: 1.22,
      },
      h3: {
        fontFamily: '"Inter", "Noto Sans KR", "Apple SD Gothic Neo", "Malgun Gothic", sans-serif',
        fontWeight: 700,
        letterSpacing: "-0.03em",
        lineHeight: 1.24,
      },
      h4: {
        fontFamily: '"Inter", "Noto Sans KR", "Apple SD Gothic Neo", "Malgun Gothic", sans-serif',
        fontWeight: 700,
        letterSpacing: "-0.02em",
        lineHeight: 1.28,
      },
      h5: {
        fontFamily: '"Inter", "Noto Sans KR", "Apple SD Gothic Neo", "Malgun Gothic", sans-serif',
        fontWeight: 700,
        lineHeight: 1.32,
      },
      h6: {
        fontFamily: '"Inter", "Noto Sans KR", "Apple SD Gothic Neo", "Malgun Gothic", sans-serif',
        fontWeight: 700,
        lineHeight: 1.34,
      },
      button: {
        fontWeight: 700,
        textTransform: "none",
        letterSpacing: "-0.01em",
      },
      body1: {
        lineHeight: 1.7,
      },
      body2: {
        lineHeight: 1.58,
      },
    },
    components: {
      MuiCssBaseline: {
        styleOverrides: {
          ":root": {
            colorScheme: mode,
          },
          body: {
            background: isDark
              ? "radial-gradient(circle at 12% 10%, rgba(66, 99, 235, 0.12), transparent 22%), radial-gradient(circle at 88% 14%, rgba(255, 107, 61, 0.08), transparent 16%), linear-gradient(180deg, #0f1623 0%, #09111a 100%)"
              : "radial-gradient(circle at 14% 12%, rgba(66, 99, 235, 0.05), transparent 18%), radial-gradient(circle at 88% 12%, rgba(255, 107, 61, 0.04), transparent 16%), linear-gradient(180deg, #fbfcff 0%, #f2f5fa 100%)",
            backgroundAttachment: "fixed",
          },
          "*::-webkit-scrollbar": {
            height: 10,
            width: 10,
          },
          "*::-webkit-scrollbar-thumb": {
            backgroundColor: isDark ? alpha("#8fa3ff", 0.22) : alpha("#31415f", 0.18),
            borderRadius: 999,
          },
          "*::-webkit-scrollbar-track": {
            backgroundColor: "transparent",
          },
          "::selection": {
            backgroundColor: alpha("#4263eb", 0.24),
          },
        },
      },
      MuiPaper: {
        styleOverrides: {
          root: {
            backgroundImage: "none",
            border: `1px solid ${isDark ? alpha("#d7e0ff", 0.1) : alpha("#223253", 0.08)}`,
            backdropFilter: "blur(10px)",
            boxShadow: `0 12px 32px ${shadowColor}`,
          },
        },
      },
      MuiButton: {
        defaultProps: {
          disableElevation: true,
        },
        styleOverrides: {
          root: {
            borderRadius: 12,
            paddingInline: 18,
            minHeight: 42,
            transition: "transform 160ms ease, border-color 160ms ease, background-color 160ms ease",
            "&:hover": {
              transform: "translateY(-1px)",
            },
          },
          containedPrimary: {
            background: isDark
              ? "linear-gradient(135deg, #6280ff 0%, #3d63f5 100%)"
              : "linear-gradient(135deg, #4b6bff 0%, #3456eb 100%)",
          },
          outlined: {
            borderColor: isDark ? alpha("#d7e0ff", 0.16) : alpha("#223253", 0.12),
          },
        },
      },
      MuiCard: {
        styleOverrides: {
          root: {
            borderRadius: 18,
            border: `1px solid ${isDark ? alpha("#d7e0ff", 0.1) : alpha("#223253", 0.08)}`,
            background: isDark ? alpha("#121924", 0.86) : alpha("#ffffff", 0.98),
            boxShadow: `0 10px 26px ${shadowColor}`,
            transition: "transform 180ms ease, border-color 180ms ease, box-shadow 180ms ease",
            "&:hover": {
              borderColor: isDark ? alpha("#8fa3ff", 0.2) : alpha("#4263eb", 0.18),
              boxShadow: `0 14px 30px ${shadowColor}`,
              transform: "translateY(-2px)",
            },
          },
        },
      },
      MuiOutlinedInput: {
        styleOverrides: {
          root: {
            borderRadius: 14,
            background: isDark ? alpha("#0d1420", 0.74) : alpha("#fbfcff", 0.92),
          },
        },
      },
      MuiChip: {
        styleOverrides: {
          root: {
            borderRadius: 999,
            backdropFilter: "blur(10px)",
            fontWeight: 600,
            minHeight: 28,
            maxWidth: "100%",
          },
        },
      },
      MuiAlert: {
        styleOverrides: {
          root: {
            borderRadius: 18,
            border: `1px solid ${isDark ? alpha("#ffffff", 0.08) : alpha("#223253", 0.08)}`,
          },
        },
      },
      MuiTableCell: {
        styleOverrides: {
          root: {
            borderBottomColor: isDark ? alpha("#ffffff", 0.08) : alpha("#223253", 0.08),
          },
          head: {
            color: isDark ? alpha("#eef3ff", 0.62) : alpha("#172133", 0.58),
            textTransform: "uppercase",
            letterSpacing: "0.12em",
            fontSize: "0.74rem",
          },
        },
      },
      MuiTableRow: {
        styleOverrides: {
          root: {
            transition: "background-color 140ms ease",
            "&:hover": {
              backgroundColor: isDark ? alpha("#ffffff", 0.03) : alpha("#4263eb", 0.03),
            },
          },
        },
      },
    },
  });

  theme = responsiveFontSizes(theme);
  return theme;
}
