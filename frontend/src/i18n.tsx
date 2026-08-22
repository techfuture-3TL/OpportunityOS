import { createContext, useContext, useEffect, useState } from "react";

export type Lang = "vi" | "en";

interface I18nContextValue {
  lang: Lang;
  setLang: (lang: Lang) => void;
  t: (vi: string, en: string) => string;
}

const I18nContext = createContext<I18nContextValue>({
  lang: "vi",
  setLang: () => {},
  t: (vi) => vi,
});

export function I18nProvider({ children }: { children: React.ReactNode }) {
  const [lang, setLangState] = useState<Lang>(() => {
    const stored = window.localStorage.getItem("opp-os-lang");
    return stored === "en" ? "en" : "vi";
  });

  const setLang = (next: Lang) => {
    setLangState(next);
    window.localStorage.setItem("opp-os-lang", next);
  };

  useEffect(() => {
    document.documentElement.lang = lang;
  }, [lang]);

  const t = (vi: string, en: string) => (lang === "vi" ? vi : en);

  return (
    <I18nContext.Provider value={{ lang, setLang, t }}>
      {children}
    </I18nContext.Provider>
  );
}

export function useI18n() {
  return useContext(I18nContext);
}
