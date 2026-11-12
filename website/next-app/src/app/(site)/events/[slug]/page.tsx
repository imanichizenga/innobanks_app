import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { asArray, fetchAPI, getMediaUrl, toSlug } from "@/lib/api";
import FAQAccordion from "@/app/components/school/FAQAccordion";
import ImageGallery from "@/app/components/school/ImageGallery";
import EmptyState from "@/app/components/school/EmptyState";
import { fallbackImages } from "@/lib/fallbacks";
import { notFound } from "next/navigation";
import { buildMetadata, breadcrumbJsonLd, toAbsoluteUrl } from "@/lib/seo";

interface EventFAQData { id?: number; question?: string; answer?: string; order?: number; is_active?: boolean; }
interface EventItemData {
  id?: number; title?: string; slug?: string; short_description?: string; content?: string; featured_image?: string;
  event_date?: string; start_time?: string; end_time?: string; venue?: string; organizer?: string; registration_link?: string;
  is_featured?: boolean; is_active?: boolean; created_at?: string; updated_at?: string; faqs?: EventFAQData[];
}
interface GalleryItemData { id?: number; title?: string; image?: string; caption?: string; event_item?: number; }

const formatDate = (value?: string) => value ? new Intl.DateTimeFormat("en-US", { month: "long", day: "numeric", year: "numeric" }).format(new Date(value)) : "";
const formatTime = (value?: string) => value ? new Intl.DateTimeFormat("en-US", { hour: "numeric", minute: "2-digit", hour12: true }).format(new Date(2000, 0, 1, Number(value.split(":")[0]), Number(value.split(":")[1]))) : "";
const formatTimeRange = (start?: string, end?: string) => [formatTime(start), formatTime(end)].filter(Boolean).join(" - ");

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const eventsPayload = await fetchAPI<unknown>("/event-items/");
  const item = asArray<EventItemData>(eventsPayload).find((entry) => entry.slug === slug || toSlug(entry.title) === slug);
  return buildMetadata({
    title: item?.title?.trim() || "Event",
    description: item?.short_description?.trim() || item?.content?.trim()?.slice(0, 160) || "Upcoming school event.",
    path: `/events/${item?.slug || slug}`,
    image: getMediaUrl(item?.featured_image, fallbackImages.event),
  });
}

export default async function EventDetail({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const [eventsPayload, galleryPayload] = await Promise.all([fetchAPI<unknown>("/event-items/"), fetchAPI<unknown>("/news-event-gallery/")]);
  const item = asArray<EventItemData>(eventsPayload).find((entry) => entry.slug === slug || toSlug(entry.title) === slug) || null;

  if (!item) {
    notFound();
  }

  const gallery = asArray<GalleryItemData>(galleryPayload).filter((entry) => !entry.event_item || entry.event_item === item.id);
  const faqs = [...(item.faqs || [])].filter((faq) => faq?.is_active !== false).sort((a, b) => (a?.order ?? 0) - (b?.order ?? 0));
  const eventDate = formatDate(item.event_date);
  const timeRange = formatTimeRange(item.start_time, item.end_time);
  const canonicalPath = `/events/${item.slug || slug}`;
  const breadcrumb = breadcrumbJsonLd([{ name: "Home", path: "/" }, { name: "Events", path: "/events" }, { name: item.title || "Event", path: canonicalPath }]);
  const eventJsonLd = { "@context": "https://schema.org", "@type": "Event", name: item.title || "School Event", description: item.short_description || item.content || "Event details", startDate: item.event_date, location: item.venue ? { "@type": "Place", name: item.venue } : undefined, organizer: item.organizer ? { "@type": "Organization", name: item.organizer } : undefined, image: getMediaUrl(item.featured_image, fallbackImages.event), url: toAbsoluteUrl(canonicalPath) };

  return (
    <main>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumb) }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(eventJsonLd) }} />
      <section className="relative !py-0"><div className="relative h-[40vh] min-h-[260px] overflow-hidden"><Image src={getMediaUrl(item.featured_image, fallbackImages.heroAlt)} alt={item.title || "Event banner"} fill priority className="object-cover" /><div className="absolute inset-0 bg-[#102d47]/60" /><div className="container relative z-10 mx-auto flex h-full max-w-screen-xl items-end px-4 pb-8"><div><p className="mb-2 text-xs uppercase tracking-[0.18em] text-white/90">Event Details</p><h1 className="!text-white">{item.title || "School Event"}</h1></div></div></div></section>
      <section><div className="container mx-auto grid max-w-screen-xl gap-8 px-4 lg:grid-cols-3"><div className="space-y-6 lg:col-span-2"><article className="rounded-xl border border-blue-100 bg-white p-5"><div className="mb-4 flex flex-wrap items-center gap-2 text-xs text-gray">{eventDate ? <span>{eventDate}</span> : null}{timeRange ? <span>{timeRange}</span> : null}{item.venue?.trim() ? <span>{item.venue}</span> : null}</div><p className="text-sm text-gray">{item.short_description?.trim() || item.content?.trim() || "Detailed event information will be available soon."}</p></article><article className="rounded-xl border border-blue-100 bg-section p-5"><h3 className="mb-4 !text-xl !text-midnight_text">Event Gallery</h3>{gallery.length ? <ImageGallery items={gallery} /> : <EmptyState message="No gallery images are available for this event yet." />}</article></div><aside className="space-y-6"><article className="rounded-xl border border-blue-100 bg-white p-5"><h3 className="mb-3 !text-lg !text-midnight_text">Event Information</h3><div className="space-y-2 text-sm text-gray">{item.organizer?.trim() ? <p><span className="font-semibold text-midnight_text">Organizer:</span> {item.organizer}</p> : null}</div><div className="pt-4"><Link href="/events" className="text-sm font-semibold text-primary">← Back to all events</Link></div></article>{faqs.length ? <article className="rounded-xl border border-blue-100 bg-white p-5"><h3 className="mb-3 !text-lg !text-midnight_text">Event FAQs</h3><FAQAccordion items={faqs} /></article> : null}</aside></div></section>
    </main>
  );
}
