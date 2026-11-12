import Image from "next/image";
import Link from "next/link";
import { getMediaUrl, toSlug } from "@/lib/api";
import { fallbackImages } from "@/lib/fallbacks";
import { BaseEntity } from "@/lib/types";

const formatDate = (value?: string) => {
  if (!value) return "";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return "";
  return new Intl.DateTimeFormat("en-US", { month: "short", day: "numeric", year: "numeric" }).format(parsed);
};

const eventStatus = (value?: string) => {
  if (!value) return "";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return "";
  return parsed.getTime() >= Date.now() ? "Upcoming" : "Past";
};

export function GenericCard({ item, hrefBase }: { item: BaseEntity & Record<string, any>; hrefBase: string }) {
  const slug = item.slug || toSlug(item.title || item.name) || String(item.id || "details");
  const dateLabel = formatDate(item.event_date || item.publish_date || item.created_at);
  const status = hrefBase.includes("events") ? eventStatus(item.event_date) : "";

  return (
    <article className="overflow-hidden rounded-xl border border-blue-100 bg-white shadow-sm transition hover:-translate-y-1 hover:shadow-property">
      <div className="relative">
        <Image src={getMediaUrl(item.image || item.banner_image || item.featured_image, fallbackImages.card)} alt={item.title || "image"} width={500} height={300} className="h-48 w-full object-cover" />
        {dateLabel ? <span className="absolute left-3 top-3 rounded-full bg-white/95 px-2.5 py-1 text-[11px] font-semibold text-midnight_text">{dateLabel}</span> : null}
      </div>
      <div className="p-5">
        <div className="mb-2 flex flex-wrap items-center gap-2 text-xs">
          {item.is_featured ? <span className="rounded-full bg-amber-50 px-2 py-1 font-semibold text-amber-700">Featured</span> : null}
          {status ? <span className={`rounded-full px-2 py-1 font-semibold ${status === "Upcoming" ? "bg-emerald-50 text-emerald-700" : "bg-slate-100 text-slate-600"}`}>{status}</span> : null}
        </div>
        <h3 className="mb-2 !text-lg !text-midnight_text">{item.title || item.name || "School content"}</h3>
        <p className="mb-4 line-clamp-3 text-sm text-gray">{item.short_description || item.description || "More information will be published soon."}</p>
        <Link className="text-sm font-semibold text-primary" href={`${hrefBase}/${slug}`}>{hrefBase.includes("events") ? "View event" : "Read more"} →</Link>
      </div>
    </article>
  );
}
