import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { asArray, fetchAPI, getMediaUrl, toSlug } from "@/lib/api";
import SectionHeading from "@/app/components/school/SectionHeading";
import EmptyState from "@/app/components/school/EmptyState";
import { fallbackImages } from "@/lib/fallbacks";
import { buildMetadata } from "@/lib/seo";

interface EventItemData {
  id?: number;
  slug?: string;
  title?: string;
  short_description?: string;
  content?: string;
  featured_image?: string;
  event_date?: string;
  start_time?: string;
  end_time?: string;
  venue?: string;
  organizer?: string;
  registration_link?: string;
  is_featured?: boolean;
  is_active?: boolean;
  created_at?: string;
  updated_at?: string;
}

const defaultTitle = "Events";
const defaultSubtitle = "Student, staff, and community events.";

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
  return new Intl.DateTimeFormat("en-US", { hour: "numeric", minute: "2-digit", hour12: true }).format(
    new Date(2000, 0, 1, hours, minutes),
  );
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

async function getEventData() {
  const payload = await fetchAPI<unknown>("/event-items/");
  const items = asArray<EventItemData>(payload).filter((item) => item?.is_active !== false);
  return items;
}

export async function generateMetadata(): Promise<Metadata> {
  const items = await getEventData();
  const featured = items.find((item) => item?.is_featured);

  return buildMetadata({
    title: defaultTitle,
    description: featured?.short_description?.trim() || defaultSubtitle,
    path: "/events",
    image: getMediaUrl(featured?.featured_image, fallbackImages.heroAlt),
  });
}

export default async function EventsPage() {
  const items = await getEventData();

  return (
    <main>
      <section>
        <div className="container mx-auto max-w-screen-xl space-y-8 px-4">
          <SectionHeading title={defaultTitle} subtitle={defaultSubtitle} />

          {items.length ? (
            <div className="grid gap-5 md:grid-cols-2">
              {items.map((item) => {
                const slug = item.slug || toSlug(item.title) || String(item.id || "event-item");
                const eventDate = formatDate(item.event_date);
                const createdAt = formatDate(item.created_at);
                const updatedAt = formatDate(item.updated_at);
                const timeRange = formatTimeRange(item.start_time, item.end_time);
                const status = getEventStatus(item.event_date);

                return (
                  <article
                    key={item.id || slug}
                    className="overflow-hidden rounded-xl border border-blue-100 bg-white shadow-sm transition hover:-translate-y-1 hover:shadow-property"
                  >
                    <Image
                      src={getMediaUrl(item.featured_image, fallbackImages.event)}
                      alt={item.title || "Event image"}
                      width={700}
                      height={320}
                      className="h-56 w-full object-cover"
                    />
                    <div className="space-y-3 p-5">
                      <div className="flex flex-wrap items-center gap-2 text-xs text-gray">
                        {item.is_featured ? <span className="rounded-full bg-amber-50 px-2.5 py-1 font-semibold text-amber-700">Featured</span> : null}
                        {eventDate ? <span>{eventDate}</span> : null}
                        {timeRange ? <span>{timeRange}</span> : null}
                        {status ? <span className={`rounded-full px-2.5 py-1 font-semibold ${status === "Upcoming" ? "bg-emerald-50 text-emerald-700" : "bg-slate-100 text-slate-600"}`}>{status}</span> : null}
                      </div>
                      <h3 className="!text-xl !text-midnight_text">{item.title || "Upcoming Event"}</h3>
                      <p className="line-clamp-3 text-sm text-gray">
                        {item.short_description?.trim() || item.content?.trim() || "Event details will be published soon."}
                      </p>

                      <div className="grid gap-2 text-sm text-gray sm:grid-cols-2">
                        {item.venue?.trim() ? <p><span className="font-semibold text-midnight_text">Venue:</span> {item.venue}</p> : null}
                        {item.organizer?.trim() ? <p><span className="font-semibold text-midnight_text">Organizer:</span> {item.organizer}</p> : null}
                        {createdAt ? <p><span className="font-semibold text-midnight_text">Created:</span> {createdAt}</p> : null}
                        {updatedAt ? <p><span className="font-semibold text-midnight_text">Updated:</span> {updatedAt}</p> : null}
                      </div>

                      <div className="flex flex-wrap items-center gap-3 pt-1">
                        <Link className="text-sm font-semibold text-primary" href={`/events/${slug}`}>
                          View details →
                        </Link>
                        {item.registration_link?.trim() ? (
                          <a
                            href={item.registration_link}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center rounded-lg bg-primary px-3 py-2 text-xs font-semibold text-white transition hover:bg-blue-700"
                          >
                            Register now
                          </a>
                        ) : null}
                      </div>
                    </div>
                  </article>
                );
              })}
            </div>
          ) : (
            <EmptyState message="No events are available right now." />
          )}
        </div>
      </section>
    </main>
  );
}
