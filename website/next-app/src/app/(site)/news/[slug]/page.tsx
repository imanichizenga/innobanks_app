import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { asArray, fetchAPI, getMediaUrl, toSlug } from "@/lib/api";
import ImageGallery from "@/app/components/school/ImageGallery";
import EmptyState from "@/app/components/school/EmptyState";
import { fallbackImages } from "@/lib/fallbacks";
import { notFound } from "next/navigation";
import { buildMetadata, breadcrumbJsonLd, toAbsoluteUrl } from "@/lib/seo";

interface NewsItemData {
  id?: number;
  title?: string;
  slug?: string;
  short_description?: string;
  content?: string;
  featured_image?: string;
  publish_date?: string;
  author_name?: string;
  is_featured?: boolean;
  is_active?: boolean;
}

interface GalleryItemData {
  id?: number;
  title?: string;
  image?: string;
  caption?: string;
  news_item?: number;
}

const formatDate = (value?: string) => {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  return new Intl.DateTimeFormat("en-US", { month: "long", day: "numeric", year: "numeric" }).format(date);
};

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const newsPayload = await fetchAPI<unknown>("/news-items/");
  const item = asArray<NewsItemData>(newsPayload).find((entry) => entry.slug === slug || toSlug(entry.title) === slug);
  return buildMetadata({
    title: item?.title?.trim() || "News",
    description: item?.short_description?.trim() || item?.content?.trim()?.slice(0, 160) || "Latest school news.",
    path: `/news/${item?.slug || slug}`,
    image: getMediaUrl(item?.featured_image, fallbackImages.card),
  });
}

export default async function NewsDetail({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const [newsPayload, galleryPayload] = await Promise.all([fetchAPI<unknown>("/news-items/"), fetchAPI<unknown>("/news-event-gallery/")]);

  const item = asArray<NewsItemData>(newsPayload).find((entry) => entry.slug === slug || toSlug(entry.title) === slug) || null;

  if (!item) {
    notFound();
  }

  const gallery = asArray<GalleryItemData>(galleryPayload).filter((entry) => !entry.news_item || entry.news_item === item.id);
  const publishDate = formatDate(item.publish_date);
  const canonicalPath = `/news/${item.slug || slug}`;
  const breadcrumb = breadcrumbJsonLd([
    { name: "Home", path: "/" },
    { name: "News", path: "/news" },
    { name: item.title || "News", path: canonicalPath },
  ]);
  const newsArticleJsonLd = {
    "@context": "https://schema.org",
    "@type": "NewsArticle",
    headline: item.title || "News",
    description: item.short_description || item.content || "Latest school updates",
    datePublished: item.publish_date || undefined,
    author: item.author_name ? { "@type": "Person", name: item.author_name } : undefined,
    image: getMediaUrl(item.featured_image, fallbackImages.card),
    mainEntityOfPage: toAbsoluteUrl(canonicalPath),
  };

  return (
    <main>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumb) }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(newsArticleJsonLd) }} />
      <section className="relative !py-0">
        <div className="relative h-[40vh] min-h-[260px] overflow-hidden">
          <Image src={getMediaUrl(item.featured_image, fallbackImages.heroAlt)} alt={item.title || "News banner"} fill priority className="object-cover" />
          <div className="absolute inset-0 bg-[#102d47]/60" />
          <div className="container relative z-10 mx-auto flex h-full max-w-screen-xl items-end px-4 pb-8"><div><p className="mb-2 text-xs uppercase tracking-[0.18em] text-white/90">News</p><h1 className="!text-white">{item.title || "School News"}</h1></div></div>
        </div>
      </section>

      <section>
        <div className="container mx-auto max-w-screen-xl space-y-8 px-4">
          <div className="rounded-xl border border-blue-100 bg-white p-5">
            <div className="mb-3 flex flex-wrap items-center gap-2 text-xs text-gray">
              {item.is_featured ? <span className="rounded-full bg-amber-50 px-2.5 py-1 font-semibold text-amber-700">Featured</span> : null}
              {publishDate ? <span>Published on {publishDate}</span> : null}
              {item.author_name?.trim() ? <span>By {item.author_name}</span> : null}
            </div>
            {item.short_description?.trim() ? <p className="mb-4 text-base text-gray">{item.short_description}</p> : null}
            <div className="space-y-3 text-sm text-gray">{item.content?.trim() ? item.content.split(/\n\n+/).map((paragraph, index) => <p key={`paragraph-${index}-${paragraph.slice(0, 24)}`}>{paragraph}</p>) : <p>Full article content will be available soon.</p>}</div>
          </div>

          <div className="rounded-xl border border-blue-100 bg-section p-5">
            <div className="mb-4 flex items-center justify-between gap-3"><h3 className="!text-xl !text-midnight_text">Related Gallery</h3><Link href="/news" className="text-sm font-semibold text-primary">Back to News →</Link></div>
            {gallery.length ? <ImageGallery items={gallery} /> : <EmptyState message="No gallery images available for this news post yet." />}
          </div>
        </div>
      </section>
    </main>
  );
}
