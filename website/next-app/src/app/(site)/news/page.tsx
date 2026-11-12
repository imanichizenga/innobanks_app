import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { asArray, fetchAPI, getMediaUrl, toSlug } from "@/lib/api";
import SectionHeading from "@/app/components/school/SectionHeading";
import EmptyState from "@/app/components/school/EmptyState";
import { fallbackImages } from "@/lib/fallbacks";
import { buildMetadata } from "@/lib/seo";

interface NewsEventPageData {
  id?: number;
  title?: string;
  subtitle?: string;
  description?: string;
  hero_image?: string;
  meta_title?: string;
  meta_description?: string;
  is_active?: boolean;
}

interface NewsEventCategoryData {
  id?: number;
  title?: string;
  slug?: string;
  description?: string;
  image?: string;
  order?: number;
  is_active?: boolean;
}

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

interface EventItemData {
  id?: number;
  title?: string;
  slug?: string;
  short_description?: string;
  featured_image?: string;
  event_date?: string;
  start_time?: string;
  end_time?: string;
  venue?: string;
  organizer?: string;
  registration_link?: string;
  is_featured?: boolean;
  is_active?: boolean;
}

const defaultTitle = "News & Events";
const defaultSubtitle = "Latest announcements, stories, and upcoming activities from our school community.";

const byOrder = <T extends { order?: number }>(items: T[]) =>
  [...items].sort((a, b) => (a?.order ?? Number.MAX_SAFE_INTEGER) - (b?.order ?? Number.MAX_SAFE_INTEGER));

const formatDate = (value?: string) => {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  return new Intl.DateTimeFormat("en-US", { month: "short", day: "numeric", year: "numeric" }).format(date);
};

const formatTime = (value?: string) => {
  if (!value) return "";
  const [hoursRaw, minsRaw] = value.split(":");
  const hours = Number(hoursRaw);
  const minutes = Number(minsRaw);
  if (Number.isNaN(hours) || Number.isNaN(minutes)) return "";
  return new Intl.DateTimeFormat("en-US", {
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  }).format(new Date(2000, 0, 1, hours, minutes));
};

const formatTimeRange = (start?: string, end?: string) => {
  const startLabel = formatTime(start);
  const endLabel = formatTime(end);
  if (startLabel && endLabel) return `${startLabel} - ${endLabel}`;
  return startLabel || endLabel;
};

const getEventStatus = (value?: string) => {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  return date.getTime() >= Date.now() ? "Upcoming" : "Past";
};

async function getNewsEventsData() {
  const [pagesPayload, categoriesPayload, newsPayload, eventsPayload] = await Promise.all([
    fetchAPI<unknown>("/news-event-pages/"),
    fetchAPI<unknown>("/news-event-categories/"),
    fetchAPI<unknown>("/news-items/"),
    fetchAPI<unknown>("/event-items/"),
  ]);

  const page =
    asArray<NewsEventPageData>(pagesPayload).find((item) => item?.is_active !== false) ||
    asArray<NewsEventPageData>(pagesPayload)[0] ||
    null;

  const categories = byOrder(asArray<NewsEventCategoryData>(categoriesPayload).filter((item) => item?.is_active !== false));
  const newsItems = asArray<NewsItemData>(newsPayload).filter((item) => item?.is_active !== false).slice(0, 6);
  const eventItems = asArray<EventItemData>(eventsPayload).filter((item) => item?.is_active !== false).slice(0, 4);

  return { page, categories, newsItems, eventItems };
}

export async function generateMetadata(): Promise<Metadata> {
  const { page } = await getNewsEventsData();

  return buildMetadata({
    title: page?.meta_title?.trim() || page?.title?.trim() || defaultTitle,
    description: page?.meta_description?.trim() || page?.description?.trim() || defaultSubtitle,
    path: "/news",
    image: getMediaUrl(page?.hero_image, fallbackImages.heroAlt),
  });
}

export default async function NewsPage() {
  const { page, categories, newsItems, eventItems } = await getNewsEventsData();

  return (
    <main>
      <section className="relative !py-0">
        <div className="relative h-[38vh] min-h-[260px] overflow-hidden">
          <Image src={getMediaUrl(page?.hero_image, fallbackImages.heroAlt)} alt={page?.title || defaultTitle} fill priority className="object-cover" />
          <div className="absolute inset-0 bg-[#102d47]/55" />
          <div className="container relative z-10 mx-auto flex h-full max-w-screen-xl items-end px-4 pb-8">
            <div>
              <h1 className="!text-white">{page?.title?.trim() || defaultTitle}</h1>
              {page?.subtitle?.trim() ? <p className="mt-2 max-w-2xl text-white/90">{page.subtitle}</p> : null}
            </div>
          </div>
        </div>
      </section>

      <section>
        <div className="container mx-auto max-w-screen-xl space-y-10 px-4">
          <SectionHeading title={page?.title?.trim() || defaultTitle} subtitle={page?.description?.trim() || defaultSubtitle} />

          <div>
            <div className="mb-4 flex items-center justify-between gap-3">
              <h3 className="!text-2xl !text-midnight_text">Categories</h3>
            </div>
            {categories.length ? (
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                {categories.map((category) => (
                  <article key={category.id || category.slug || category.title} className="rounded-xl border border-blue-100 bg-white p-4 shadow-sm">
                    <div className="mb-3 flex items-center gap-3">
                      <Image
                        src={getMediaUrl(category.image, fallbackImages.card)}
                        alt={category.title || "Category image"}
                        width={52}
                        height={52}
                        className="h-12 w-12 rounded-lg object-cover"
                      />
                      <h4 className="!text-base !font-semibold !text-midnight_text">{category.title || "General"}</h4>
                    </div>
                    <p className="line-clamp-3 text-sm text-gray">{category.description?.trim() || "Category updates and highlights."}</p>
                  </article>
                ))}
              </div>
            ) : (
              <EmptyState message="News and event categories are not available yet." />
            )}
          </div>

          <div>
            <div className="mb-4 flex items-center justify-between gap-3">
              <h3 className="!text-2xl !text-midnight_text">Latest News</h3>
              <Link href="/news" className="text-sm font-semibold text-primary">
                View all news →
              </Link>
            </div>
            {newsItems.length ? (
              <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
                {newsItems.map((item) => {
                  const slug = item.slug || toSlug(item.title) || String(item.id || "news-item");
                  const publishDate = formatDate(item.publish_date);
                  return (
                    <article key={item.id || slug} className="overflow-hidden rounded-xl border border-blue-100 bg-white shadow-sm transition hover:-translate-y-1 hover:shadow-property">
                      <Image
                        src={getMediaUrl(item.featured_image, fallbackImages.card)}
                        alt={item.title || "News image"}
                        width={500}
                        height={300}
                        className="h-48 w-full object-cover"
                      />
                      <div className="space-y-3 p-5">
                        <div className="flex flex-wrap items-center gap-2 text-xs text-gray">
                          {item.is_featured ? <span className="rounded-full bg-amber-50 px-2.5 py-1 font-semibold text-amber-700">Featured</span> : null}
                          {publishDate ? <span>{publishDate}</span> : null}
                          {item.author_name?.trim() ? <span>By {item.author_name}</span> : null}
                        </div>
                        <h4 className="!text-lg !text-midnight_text">{item.title || "School News"}</h4>
                        <p className="line-clamp-3 text-sm text-gray">
                          {item.short_description?.trim() || item.content?.trim() || "Full details will be published soon."}
                        </p>
                        <Link href={`/news/${slug}`} className="text-sm font-semibold text-primary">
                          Read more →
                        </Link>
                      </div>
                    </article>
                  );
                })}
              </div>
            ) : (
              <EmptyState message="No news has been published yet." />
            )}
          </div>

          <div>
            <div className="mb-4 flex items-center justify-between gap-3">
              <h3 className="!text-2xl !text-midnight_text">Upcoming Events</h3>
              <Link href="/events" className="text-sm font-semibold text-primary">
                View all events →
              </Link>
            </div>
            {eventItems.length ? (
              <div className="grid gap-5 md:grid-cols-2">
                {eventItems.map((event) => {
                  const slug = event.slug || toSlug(event.title) || String(event.id || "event-item");
                  const dateLabel = formatDate(event.event_date);
                  const timeLabel = formatTimeRange(event.start_time, event.end_time);
                  const status = getEventStatus(event.event_date);
                  return (
                    <article key={event.id || slug} className="rounded-xl border border-blue-100 bg-white p-4 shadow-sm">
                      <div className="flex gap-4">
                        <Image
                          src={getMediaUrl(event.featured_image, fallbackImages.event)}
                          alt={event.title || "Event image"}
                          width={140}
                          height={120}
                          className="h-24 w-28 rounded-lg object-cover sm:h-28 sm:w-32"
                        />
                        <div className="min-w-0 flex-1 space-y-2">
                          <div className="flex flex-wrap items-center gap-2 text-xs text-gray">
                            {event.is_featured ? <span className="rounded-full bg-amber-50 px-2.5 py-1 font-semibold text-amber-700">Featured</span> : null}
                            {dateLabel ? <span>{dateLabel}</span> : null}
                            {timeLabel ? <span>{timeLabel}</span> : null}
                            {status ? <span className={`rounded-full px-2.5 py-1 font-semibold ${status === "Upcoming" ? "bg-emerald-50 text-emerald-700" : "bg-slate-100 text-slate-600"}`}>{status}</span> : null}
                          </div>
                          <h4 className="!text-lg !text-midnight_text">{event.title || "School Event"}</h4>
                          <p className="line-clamp-2 text-sm text-gray">
                            {event.short_description?.trim() || "Event details will be updated soon."}
                          </p>
                          <div className="flex flex-wrap gap-x-4 gap-y-1 text-xs text-gray">
                            {event.venue?.trim() ? <span>Venue: {event.venue}</span> : null}
                            {event.organizer?.trim() ? <span>Organizer: {event.organizer}</span> : null}
                          </div>
                          <div className="flex flex-wrap items-center gap-2">
                            <Link href={`/events/${slug}`} className="text-sm font-semibold text-primary">
                              View event →
                            </Link>
                            {event.registration_link?.trim() ? <a href={event.registration_link} target="_blank" rel="noopener noreferrer" className="rounded-md bg-primary px-2.5 py-1.5 text-xs font-semibold text-white">Register</a> : null}
                          </div>
                        </div>
                      </div>
                    </article>
                  );
                })}
              </div>
            ) : (
              <EmptyState message="No events are scheduled right now." />
            )}
          </div>
        </div>
      </section>
    </main>
  );
}
