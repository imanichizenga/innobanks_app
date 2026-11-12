import { fallbackImages } from "./fallbacks";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "https://britishschool.ac.tz/api";

const stripSlashes = (value: string) => value.replace(/^\/+|\/+$/g, "");

const API_ORIGIN = API_BASE_URL.replace(/\/api\/?$/, "");

// The former API/media hostname is retained in existing database records. Rewrite
// it at render time so old records remain usable if that hostname's DNS is down.
const LEGACY_MEDIA_HOSTS = new Set([
  "british.schoolsoft.online",
  "www.british.schoolsoft.online",
]);

const MEDIA_KEYS = ["url", "image", "icon_image", "src", "path", "file"];

export const extractMediaPath = (value: unknown): string | null => {
  if (typeof value === "string") {
    const trimmed = value.trim();
    return trimmed.length ? trimmed : null;
  }

  if (!value || typeof value !== "object") return null;

  for (const key of MEDIA_KEYS) {
    const candidate = (value as Record<string, unknown>)[key];
    const extracted = extractMediaPath(candidate);
    if (extracted) return extracted;
  }

  return null;
};

export const getMediaUrl = (url?: unknown, fallback = fallbackImages.card) => {
  const parsedUrl = extractMediaPath(url);
  if (!parsedUrl) return fallback;
  const normalized = parsedUrl.replace(/\\/g, "/").trim();
  if (!normalized) return fallback;
  if (normalized.startsWith("http://") || normalized.startsWith("https://")) {
    try {
      const absoluteUrl = new URL(normalized);
      if (LEGACY_MEDIA_HOSTS.has(absoluteUrl.hostname)) {
        return new URL(`${absoluteUrl.pathname}${absoluteUrl.search}${absoluteUrl.hash}`, `${API_ORIGIN}/`).toString();
      }
      return absoluteUrl.toString();
    } catch {
      return fallback;
    }
  }
  if (normalized.startsWith("//")) return `https:${normalized}`;
  if (normalized.startsWith("data:")) return normalized;

  try {
    return new URL(normalized, `${API_ORIGIN}/`).toString();
  } catch {
    return `${API_ORIGIN}/${stripSlashes(normalized)}`;
  }
};

export const toSlug = (value?: string | null) =>
  (value || "")
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9\s-]/g, "")
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-");

export async function fetchAPI<T>(endpoint: string, revalidate = 120): Promise<T | null> {
  const normalizedEndpoint = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;
  const url = `${API_BASE_URL}${normalizedEndpoint}`;

  try {
    const res = await fetch(url, {
      next: { revalidate },
      headers: { "Content-Type": "application/json" },
    });

    if (!res.ok) return null;
    return (await res.json()) as T;
  } catch {
    return null;
  }
}

export function asArray<T>(payload: unknown): T[] {
  if (Array.isArray(payload)) return payload as T[];
  if (payload && typeof payload === "object") {
    const p = payload as Record<string, unknown>;
    if (Array.isArray(p.results)) return p.results as T[];
    if (Array.isArray(p.data)) return p.data as T[];
  }
  return [];
}
