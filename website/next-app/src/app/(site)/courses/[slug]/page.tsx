import type { Metadata } from "next";
import { asArray, fetchAPI, getMediaUrl, toSlug } from "@/lib/api";
import DetailLayout from "@/app/components/school/DetailLayout";
import { notFound } from "next/navigation";
import { buildMetadata, breadcrumbJsonLd, toAbsoluteUrl } from "@/lib/seo";
import { fallbackImages } from "@/lib/fallbacks";

type CourseSection = {
  id?: number;
  course?: number;
  title?: string;
  slug?: string;
  subtitle?: string;
  description?: string;
  content?: string;
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

type CourseRequirement = {
  id?: number;
  course?: number;
  requirement?: string;
  description?: string;
  order?: number;
  is_active?: boolean;
};

const byOrder = <T extends { order?: number }>(items: T[]) =>
  [...items].sort((a, b) => (a?.order ?? Number.MAX_SAFE_INTEGER) - (b?.order ?? Number.MAX_SAFE_INTEGER));

const normalizeToken = (value?: string | number | null) =>
  `${value ?? ""}`
    .trim()
    .toLowerCase()
    .replace(/\s+/g, "-")
    .replace(/[^a-z0-9-]/g, "")
    .slice(0, 40);

const toKeyedSections = ({
  items,
  source,
  courseId,
}: {
  items: CourseSection[];
  source: "detail" | "outcome";
  courseId?: number;
}) => {
  const scoped = byOrder(items.filter((entry) => entry?.is_active !== false).filter((entry) => !entry.course || entry.course === courseId));
  const seen = new Map<string, number>();

  return scoped.map((entry, index) => {
    const baseSignature = [
      source,
      courseId ?? "course",
      entry.id ?? "id",
      entry.order ?? "order",
      normalizeToken(entry.slug || entry.title),
      normalizeToken(entry.subtitle),
      normalizeToken(entry.deadline),
      normalizeToken(entry.file),
    ].join("|");

    const duplicateCount = seen.get(baseSignature) ?? 0;
    seen.set(baseSignature, duplicateCount + 1);

    return {
      ...entry,
      section_key: `course-${baseSignature}|dup-${duplicateCount}|idx-${index}`,
    };
  });
};

async function getCourse(slug: string) {
  const [courses, details, requirements, outcomes, gallery, faqs] = await Promise.all([
    fetchAPI<unknown>("/courses/"),
    fetchAPI<unknown>("/course-details/"),
    fetchAPI<unknown>("/course-requirements/"),
    fetchAPI<unknown>("/course-outcomes/"),
    fetchAPI<unknown>("/course-gallery/"),
    fetchAPI<unknown>("/course-faqs/"),
  ]);

  const item = asArray<any>(courses).find((x) => x.slug === slug || toSlug(x.title || x.name) === slug) || {};

  const detailSections = toKeyedSections({ items: asArray<CourseSection>(details), source: "detail", courseId: item.id });
  const outcomeSections = toKeyedSections({ items: asArray<CourseSection>(outcomes), source: "outcome", courseId: item.id });

  const sections = [...detailSections, ...outcomeSections].filter((entry) => entry.title || entry.subtitle || entry.content || entry.description);

  const scopedRequirements = byOrder(
    asArray<CourseRequirement>(requirements)
      .filter((entry) => entry?.is_active !== false)
      .filter((entry) => !entry.course || entry.course === item.id),
  )
    .map((entry) => ({ ...entry, requirement: entry.requirement || entry.description }))
    .filter((entry) => entry.requirement?.trim());

  return {
    item,
    sections,
    requirements: scopedRequirements,
    faqs: byOrder(asArray<any>(faqs).filter((x) => !x.course || x.course === item.id)),
    gallery: byOrder(asArray<any>(gallery).filter((x) => !x.course || x.course === item.id)),
  };
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const { item } = await getCourse(slug);
  if (!item?.id) notFound();

  const title = item.meta_title?.trim() || item.title?.trim() || "Course";
  const description = item.meta_description?.trim() || item.short_description?.trim() || "Course details and learning outcomes.";

  return buildMetadata({
    title,
    description,
    path: `/courses/${item.slug || slug}`,
    image: getMediaUrl(item.banner_image || item.thumbnail, fallbackImages.card),
  });
}

export default async function CourseDetail({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const { item, sections, requirements, faqs, gallery } = await getCourse(slug);
  if (!item?.id) notFound();

  const breadcrumb = breadcrumbJsonLd([
    { name: "Home", path: "/" },
    { name: "Courses", path: "/courses" },
    { name: item.title || "Course", path: `/courses/${item.slug || slug}` },
  ]);

  const courseJsonLd = {
    "@context": "https://schema.org",
    "@type": "Course",
    name: item.title || "Course",
    description: item.short_description || item.full_description || "Course information",
    provider: {
      "@type": "EducationalOrganization",
      name: "British Opening Schools",
      url: toAbsoluteUrl("/"),
    },
    image: getMediaUrl(item.banner_image || item.thumbnail, fallbackImages.card),
    url: toAbsoluteUrl(`/courses/${item.slug || slug}`),
  };

  return (
    <>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumb) }} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(courseJsonLd) }} />
      <DetailLayout item={item} sections={sections} faqs={faqs} gallery={gallery} requirements={requirements} />
    </>
  );
}
