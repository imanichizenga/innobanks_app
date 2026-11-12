import type { Metadata } from "next";
import { asArray, fetchAPI, toSlug } from "@/lib/api";
import DetailLayout from "@/app/components/school/DetailLayout";
import { notFound } from "next/navigation";
import { buildMetadata, breadcrumbJsonLd } from "@/lib/seo";

interface AdmissionRequirement {
  id?: number;
  requirement?: string;
  order?: number;
  is_active?: boolean;
  category?: number;
  admission_category?: number;
}

interface AdmissionCategory {
  id?: number;
  title?: string;
  slug?: string;
  short_description?: string;
  image?: string;
  form_type?: string;
  requirements?: AdmissionRequirement[];
  order?: number;
  is_active?: boolean;
  meta_title?: string;
  meta_description?: string;
}

const byOrder = <T extends { order?: number }>(items: T[]) =>
  [...items].sort((a, b) => (a?.order ?? Number.MAX_SAFE_INTEGER) - (b?.order ?? Number.MAX_SAFE_INTEGER));

const scopedToCategory = (value: Record<string, any>, categoryId?: number) => {
  if (!categoryId) return true;
  const relationKeys = ["category", "admission_category", "menu_item"];
  const rawRelation = relationKeys.find((key) => value[key] !== undefined && value[key] !== null);
  if (!rawRelation) return true;
  return Number(value[rawRelation]) === Number(categoryId);
};

async function getAdmissionItem(slug: string) {
  const [categoriesPayload, sectionsPayload, requirementsPayload, faqsPayload, galleryPayload] = await Promise.all([
    fetchAPI<unknown>("/admission-categories/"),
    fetchAPI<unknown>("/admission-sections/"),
    fetchAPI<unknown>("/admission-requirements/"),
    fetchAPI<unknown>("/admission-faqs/"),
    fetchAPI<unknown>("/admission-gallery/"),
  ]);

  const categoryItems = asArray<AdmissionCategory>(categoriesPayload).filter((item) => item?.is_active !== false);
  const item =
    categoryItems.find((x) => x.slug === slug || toSlug(x.title) === slug) ||
    asArray<AdmissionCategory>(categoriesPayload).find((x) => x.slug === slug || toSlug(x.title) === slug) ||
    {};

  const sections = byOrder(
    asArray<any>(sectionsPayload)
      .filter((entry) => entry?.is_active !== false)
      .filter((entry) => scopedToCategory(entry, item?.id)),
  );

  const nestedRequirements = asArray<AdmissionRequirement>(item?.requirements).filter((entry) => entry?.is_active !== false);
  const endpointRequirements = asArray<AdmissionRequirement>(requirementsPayload)
    .filter((entry) => entry?.is_active !== false)
    .filter((entry) => scopedToCategory(entry as unknown as Record<string, any>, item?.id));

  const requirementsSource = nestedRequirements.length ? nestedRequirements : endpointRequirements;
  const requirements = byOrder(requirementsSource).filter((entry) => entry?.requirement?.trim());

  const faqs = byOrder(
    asArray<any>(faqsPayload)
      .filter((entry) => entry?.is_active !== false)
      .filter((entry) => scopedToCategory(entry, item?.id)),
  );

  const gallery = byOrder(asArray<any>(galleryPayload).filter((entry) => scopedToCategory(entry, item?.id)));
  return { item, sections, requirements, faqs, gallery };
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const { item } = await getAdmissionItem(slug);
  if (!item?.id) notFound();
  return buildMetadata({
    title: item.meta_title?.trim() || item.title?.trim() || "Admission",
    description: item.meta_description?.trim() || item.short_description?.trim() || "Admission details",
    path: `/admission/${item.slug || slug}`,
  });
}

export default async function AdmissionDetail({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const { item, sections, requirements, faqs, gallery } = await getAdmissionItem(slug);
  if (!item?.id) notFound();

  const breadcrumb = breadcrumbJsonLd([
    { name: "Home", path: "/" },
    { name: "Admission", path: "/admission" },
    { name: item.title || "Details", path: `/admission/${item.slug || slug}` },
  ]);

  return (
    <>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumb) }} />
      <DetailLayout item={item} sections={sections} faqs={faqs} gallery={gallery} requirements={requirements} />
    </>
  );
}
