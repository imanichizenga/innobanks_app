import Image from "next/image";
import Link from "next/link";
import { BaseEntity, FAQItem } from "@/lib/types";
import { fallbackImages, fallbackText } from "@/lib/fallbacks";
import { getMediaUrl } from "@/lib/api";
import FAQAccordion from "./FAQAccordion";
import ImageGallery from "./ImageGallery";
import EmptyState from "./EmptyState";

type DetailSection = BaseEntity & {
  subtitle?: string;
  content?: string;
  description?: string;
  image?: string;
  file?: string;
  external_link?: string;
  button_text?: string;
  button_link?: string;
  deadline?: string;
  order?: number;
  is_active?: boolean;
  section_key?: string;
};

type RequirementItem = {
  id?: number;
  requirement?: string;
  order?: number;
};

const isAbsoluteUrl = (value?: string) => Boolean(value && /^https?:\/\//i.test(value));

const normalizeKeyToken = (value?: string | number | null) =>
  `${value ?? ""}`
    .trim()
    .toLowerCase()
    .replace(/\s+/g, "-")
    .replace(/[^a-z0-9-]/g, "")
    .slice(0, 50);

const getSectionStableKey = (section: DetailSection, index: number, itemContext?: string | number) => {
  if (section.section_key?.trim()) return section.section_key;

  const parts = [
    "section",
    normalizeKeyToken(itemContext),
    normalizeKeyToken(section.id),
    normalizeKeyToken(section.order),
    normalizeKeyToken(section.slug),
    normalizeKeyToken(section.title),
    normalizeKeyToken(section.subtitle),
    normalizeKeyToken(section.deadline),
    index,
  ].filter(Boolean);

  return parts.join("-");
};

export default function DetailLayout({
  item,
  sections,
  faqs,
  gallery,
  requirements = [],
}: {
  item: BaseEntity & Record<string, any>;
  sections: DetailSection[];
  faqs: FAQItem[];
  gallery: BaseEntity[];
  requirements?: RequirementItem[];
}) {
  const sectionContext = item.slug || item.id || item.title;
  const overviewText = item.full_description || item.description || item.short_description;
  const hasCourseMeta = Boolean(item.duration || item.level || item.department || item.course_code);
  const ctas = [
    item.application_link
      ? {
          href: item.application_link,
          label: "Apply Now",
          primary: true,
        }
      : null,
    item.brochure_file
      ? {
          href: getMediaUrl(item.brochure_file, ""),
          label: "Download Brochure",
          primary: false,
        }
      : null,
  ].filter(Boolean) as { href: string; label: string; primary: boolean }[];

  return (
    <main>
      <section className="relative !py-0">
        <div className="relative min-h-[320px]">
          <Image
            src={getMediaUrl(item.banner_image || item.image || item.featured_image, fallbackImages.heroAlt)}
            alt={item.title || "banner"}
            fill
            className="object-cover"
            priority
          />
          <div className="absolute inset-0 bg-gradient-to-r from-[#0d2542]/90 via-[#123a62]/70 to-[#123a62]/35" />
          <div className="container relative z-10 mx-auto flex h-full max-w-screen-xl items-end px-4 pb-10 pt-28">
            <div className="w-full rounded-2xl border border-white/20 bg-white/10 p-6 backdrop-blur-sm lg:p-8">
              <h1 className="!mb-3 !text-white">{item.title || item.name || fallbackText.schoolName}</h1>
              {item.short_description ? <p className="max-w-3xl text-sm text-white/90 lg:text-base">{item.short_description}</p> : null}

              {hasCourseMeta ? (
                <div className="mt-5 flex flex-wrap gap-2">
                  {[item.duration ? `Duration: ${item.duration}` : null, item.level ? `Level: ${item.level}` : null, item.department ? `Department: ${item.department}` : null, item.course_code ? `Code: ${item.course_code}` : null]
                    .filter(Boolean)
                    .map((meta) => (
                      <span key={meta} className="rounded-full border border-white/40 bg-white/15 px-3 py-1 text-xs font-semibold text-white">
                        {meta}
                      </span>
                    ))}
                </div>
              ) : null}

              {ctas.length ? (
                <div className="mt-5 flex flex-wrap gap-3">
                  {ctas.map((cta) => (
                    <Link
                      key={`${cta.label}-${cta.href}`}
                      href={cta.href}
                      target="_blank"
                      rel="noopener noreferrer"
                      className={`inline-flex items-center rounded-lg px-4 py-2 text-sm font-semibold transition ${
                        cta.primary ? "bg-primary text-white hover:bg-blue-700" : "border border-white text-white hover:bg-white hover:text-[#123a62]"
                      }`}
                    >
                      {cta.label}
                    </Link>
                  ))}
                </div>
              ) : null}
            </div>
          </div>
        </div>
      </section>

      <section>
        <div className="container mx-auto grid max-w-screen-xl gap-8 px-4 lg:grid-cols-12">
          <div className="space-y-8 lg:col-span-8">
            <article className="rounded-xl border border-blue-100 bg-white p-6 shadow-sm">
              <h2 className="mb-3 text-2xl text-midnight_text">Course Overview</h2>
              <p className="whitespace-pre-line leading-7 text-gray">{overviewText || "Course overview will be available soon."}</p>
            </article>

            <div className="space-y-5">
              {sections.length ? (
                sections.map((section, i) => {
                  const body = section.content || section.description;
                  const sectionImage = section.image;
                  const fileUrl = section.file ? getMediaUrl(section.file, "") : "";
                  const buttonLink = section.external_link || section.button_link;
                  const hasFile = Boolean(fileUrl);
                  const hasButton = Boolean(section.button_text?.trim() && buttonLink?.trim());

                  return (
                    <article key={getSectionStableKey(section, i, sectionContext)} className="rounded-xl border border-blue-100 bg-white p-6 shadow-sm">
                      <h3 className="mb-2 !text-lg !text-midnight_text">{section.title || `Section ${i + 1}`}</h3>
                      {section.subtitle?.trim() ? <p className="mb-2 text-sm font-medium text-primary">{section.subtitle}</p> : null}
                      <p className="whitespace-pre-line text-sm leading-7 text-gray">{body || "Details for this section are coming soon."}</p>

                      {section.deadline?.trim() ? (
                        <p className="mt-4 inline-flex rounded-full bg-red-50 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-red-700">
                          Deadline: {section.deadline}
                        </p>
                      ) : null}

                      {sectionImage ? (
                        <div className="relative mt-5 h-56 overflow-hidden rounded-lg border border-blue-100">
                          <Image
                            src={getMediaUrl(sectionImage, fallbackImages.card)}
                            alt={section.title || `Section image ${i + 1}`}
                            fill
                            className="object-cover"
                          />
                        </div>
                      ) : null}

                      {(hasFile || hasButton) && (
                        <div className="mt-5 flex flex-wrap gap-3">
                          {hasFile ? (
                            <a
                              href={fileUrl}
                              target="_blank"
                              rel="noopener noreferrer"
                              download={!isAbsoluteUrl(fileUrl) ? true : undefined}
                              className="inline-flex items-center rounded-lg border border-primary px-4 py-2 text-sm font-semibold text-primary transition hover:bg-primary hover:text-white"
                            >
                              View Resource
                            </a>
                          ) : null}

                          {hasButton ? (
                            <Link
                              href={buttonLink as string}
                              target={isAbsoluteUrl(buttonLink) ? "_blank" : undefined}
                              rel={isAbsoluteUrl(buttonLink) ? "noopener noreferrer" : undefined}
                              className="inline-flex items-center rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-700"
                            >
                              {section.button_text}
                            </Link>
                          ) : null}
                        </div>
                      )}
                    </article>
                  );
                })
              ) : (
                <EmptyState message="No detailed sections available yet." />
              )}
            </div>
          </div>

          <aside className="space-y-6 lg:col-span-4">
            {requirements.length ? (
              <div className="rounded-xl border border-blue-100 bg-white p-5 shadow-sm">
                <h4 className="mb-3 text-xl text-midnight_text">Requirements</h4>
                <ul className="space-y-2">
                  {requirements.map((requirement, index) => (
                    <li
                      key={`requirement-${sectionContext}-${requirement.id ?? requirement.order ?? index}`}
                      className="flex gap-2 text-sm leading-6 text-gray"
                    >
                      <span className="mt-2 inline-block h-1.5 w-1.5 shrink-0 rounded-full bg-primary" />
                      <span>{requirement.requirement}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ) : null}

            <div className="rounded-xl border border-blue-100 bg-white p-5 shadow-sm">
              <h4 className="mb-3 text-xl text-midnight_text">FAQs</h4>
              {faqs.length ? <FAQAccordion items={faqs} /> : <EmptyState message="FAQs will appear here." />}
            </div>
          </aside>
        </div>
      </section>

      <section className="bg-section">
        <div className="container mx-auto max-w-screen-xl px-4">
          <h4 className="mb-4 text-xl">Gallery</h4>
          {gallery.length ? <ImageGallery items={gallery} /> : <EmptyState message="Gallery is currently empty." />}
        </div>
      </section>
    </main>
  );
}
