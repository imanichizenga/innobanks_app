import type { Metadata } from "next";
import { DEFAULT_OG_IMAGE, SITE_NAME, SITE_URL } from "./site";

export const toAbsoluteUrl = (path = "/") => {
  if (/^https?:\/\//i.test(path)) return path;
  const safePath = path.startsWith("/") ? path : `/${path}`;
  return `${SITE_URL}${safePath}`;
};

type BuildMetadataInput = {
  title: string;
  description: string;
  path: string;
  image?: string;
  noIndex?: boolean;
};

export function buildMetadata({ title, description, path, image, noIndex = false }: BuildMetadataInput): Metadata {
  const canonical = toAbsoluteUrl(path);
  const ogImage = image || toAbsoluteUrl(DEFAULT_OG_IMAGE);

  return {
    title,
    description,
    alternates: { canonical },
    openGraph: {
      title,
      description,
      url: canonical,
      siteName: SITE_NAME,
      type: "website",
      images: [{ url: ogImage }],
    },
    twitter: {
      card: "summary_large_image",
      title,
      description,
      images: [ogImage],
    },
    robots: noIndex
      ? { index: false, follow: false }
      : { index: true, follow: true, googleBot: { index: true, follow: true } },
  };
}

export function breadcrumbJsonLd(items: Array<{ name: string; path: string }>) {
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: items.map((item, index) => ({
      "@type": "ListItem",
      position: index + 1,
      name: item.name,
      item: toAbsoluteUrl(item.path),
    })),
  };
}
