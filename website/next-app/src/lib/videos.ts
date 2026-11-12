import { asArray, extractMediaPath, fetchAPI, getMediaUrl, toSlug } from "@/lib/api";
import { fallbackImages } from "@/lib/fallbacks";

export type HomeVideoItem = {
  id?: number;
  title?: string | null;
  description?: string | null;
  video?: unknown;
  thumbnail?: unknown;
  order?: number | null;
  is_active?: boolean;
  created_at?: string | null;
  updated_at?: string | null;
};

export type NormalizedVideo = HomeVideoItem & {
  slug: string;
  videoUrl: string;
  thumbnailUrl: string;
};

const hasValidDate = (value?: string | null) => {
  if (!value) return false;
  const parsed = new Date(value);
  return !Number.isNaN(parsed.getTime());
};

const byOrder = <T extends { order?: number | null }>(items: T[]) =>
  [...items].sort((a, b) => (a.order ?? Number.MAX_SAFE_INTEGER) - (b.order ?? Number.MAX_SAFE_INTEGER));

export const getVideoSlug = (video: HomeVideoItem, index: number) => {
  const base = toSlug(video.title || "").trim();
  if (base) return base;
  if (video.id) return `video-${video.id}`;
  return `video-${index + 1}`;
};

export async function getHomeVideos(): Promise<NormalizedVideo[]> {
  const payload = await fetchAPI<unknown>("/home-videos/");
  const raw = byOrder(asArray<HomeVideoItem>(payload)).filter((video) => video?.is_active !== false);

  const normalized: NormalizedVideo[] = [];

  raw.forEach((video, index) => {
    const videoPath = extractMediaPath(video.video);
    if (!videoPath) return;

    normalized.push({
      ...video,
      slug: getVideoSlug(video, index),
      videoUrl: getMediaUrl(video.video),
      thumbnailUrl: getMediaUrl(video.thumbnail, fallbackImages.gallery),
      created_at: hasValidDate(video.created_at) ? video.created_at : null,
      updated_at: hasValidDate(video.updated_at) ? video.updated_at : null,
    });
  });

  return normalized;
}
