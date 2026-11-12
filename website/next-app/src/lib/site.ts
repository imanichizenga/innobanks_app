export const SITE_NAME = "British Opening Schools";

const toAbsoluteSiteUrl = (value?: string | null) => {
  const raw = value?.trim();
  if (!raw) return null;
  const withProtocol = /^https?:\/\//i.test(raw) ? raw : `https://${raw}`;

  try {
    const normalized = new URL(withProtocol);
    const pathname = normalized.pathname.replace(/\/+$/, "");
    normalized.pathname = pathname || "/";
    return normalized.toString().replace(/\/$/, "");
  } catch {
    return null;
  }
};

export const SITE_URL =
  toAbsoluteSiteUrl(process.env.NEXT_PUBLIC_SITE_URL) ||
  "https://britishschool.ac.tz";

export const DEFAULT_OG_IMAGE = "/favicon.ico";