import type { MetadataRoute } from "next";
import { asArray, fetchAPI, toSlug } from "@/lib/api";
import { SITE_URL } from "@/lib/site";
import { getHomeVideos } from "@/lib/videos";

const staticRoutes = ["", "/about-us", "/academics", "/admission", "/courses", "/news", "/events", "/student-life", "/contact-us", "/videos"];

const toValidDate = (value: unknown) => {
  if (!value || typeof value !== "string") return undefined;
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? undefined : parsed;
};

const toResolvedSlug = (item: Record<string, any>) => {
  const slug = `${item?.slug || ""}`.trim() || toSlug(item?.title || item?.name || "");
  return slug.trim();
};

const mapDynamic = (items: Record<string, any>[], base: string) => {
  const unique = new Set<string>();

  return items
    .filter((item) => item?.is_active !== false)
    .map((item) => {
      const slug = toResolvedSlug(item);
      if (!slug || unique.has(slug)) return null;
      unique.add(slug);
      return {
        url: `${SITE_URL}${base}/${slug}`,
        lastModified: toValidDate(item?.updated_at || item?.created_at || item?.published_at || item?.publish_date),
      };
    })
    .filter((item): item is NonNullable<typeof item> => Boolean(item));
};

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const [courses, news, events, academics, about, admission, studentLife, videos] = await Promise.all([
    fetchAPI<unknown>("/courses/"),
    fetchAPI<unknown>("/news-items/"),
    fetchAPI<unknown>("/event-items/"),
    fetchAPI<unknown>("/academic-menu-items/"),
    fetchAPI<unknown>("/about-menu-items/"),
    fetchAPI<unknown>("/admission-categories/"),
    fetchAPI<unknown>("/student-life-menu-items/"),
    getHomeVideos(),
  ]);

  const videoUrls = videos.map((video) => ({
    url: `${SITE_URL}/videos/${video.slug}`,
    lastModified: toValidDate(video.updated_at || video.created_at),
  }));

  return [
    ...staticRoutes.map((path) => ({ url: `${SITE_URL}${path}` })),
    ...mapDynamic(asArray<Record<string, any>>(courses), "/courses"),
    ...mapDynamic(asArray<Record<string, any>>(news), "/news"),
    ...mapDynamic(asArray<Record<string, any>>(events), "/events"),
    ...mapDynamic(asArray<Record<string, any>>(academics), "/academics"),
    ...mapDynamic(asArray<Record<string, any>>(about), "/about-us"),
    ...mapDynamic(asArray<Record<string, any>>(admission), "/admission"),
    ...mapDynamic(asArray<Record<string, any>>(studentLife), "/student-life"),
    ...videoUrls,
  ];
}
