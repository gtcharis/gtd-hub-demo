import { createContext, useContext, useEffect, useMemo, useState } from "react";
import App from "./App";

type RouterValue = { pathname: string; navigate: (path: string) => void };
const RouterContext = createContext<RouterValue | null>(null);

function currentPath() {
  const hash = window.location.hash.replace(/^#/, "");
  return hash.startsWith("/") ? hash : "/welcome";
}

export function useAppRouter() {
  const value = useContext(RouterContext);
  if (!value) throw new Error("useAppRouter must be used inside AppRouter");
  return value;
}

export default function AppRouter() {
  const [pathname, setPathname] = useState(currentPath);
  useEffect(() => {
    const sync = () => setPathname(currentPath());
    window.addEventListener("hashchange", sync);
    if (!window.location.hash) window.location.hash = "/welcome";
    return () => window.removeEventListener("hashchange", sync);
  }, []);
  const value = useMemo<RouterValue>(
    () => ({
      pathname,
      navigate: (path) => {
        if (currentPath() === path) return;
        window.location.hash = path;
      },
    }),
    [pathname],
  );
  return (
    <RouterContext.Provider value={value}>
      <App />
    </RouterContext.Provider>
  );
}
