import type { Metadata } from "next";
import { asArray, fetchAPI, toSlug } from "@/lib/api";
import DetailLayout from "@/app/components/school/DetailLayout";
import { notFound } from "next/navigation";
import { buildMetadata, breadcrumbJsonLd } from "@/lib/seo";

async function getAcademicItem(slug: string) {
  const [menu, sections, faqs, gallery] = await Promise.all([
    fetchAPI<unknown>("/academic-menu-items/"),
    fetchAPI<unknown>("/academic-sections/"),
    fetchAPI<unknown>("/academic-faqs/"),
    fetchAPI<unknown>("/academic-gallery/"),
  ]);

  const menuItems = asArray<any>(menu).filter((x) => x?.is_active !== false);
  const item = menuItems.find((x) => x.slug === slug || toSlug(x.title || x.name) === slug) || {};
  const filteredSections = asArray<any>(sections)
    .filter((x) => x?.is_active !== false)
    .filter((x) => !x.menu_item || x.menu_item === item.id)
    .sort((a, b) => (a?.order ?? Number.MAX_SAFE_INTEGER) - (b?.order ?? Number.MAX_SAFE_INTEGER));
  const filteredFaqs = asArray<any>(faqs)
    .filter((x) => x?.is_active !== false)
    .filter((x) => !x.menu_item || x.menu_item === item.id)
    .sort((a, b) => (a?.order ?? Number.MAX_SAFE_INTEGER) - (b?.order ?? Number.MAX_SAFE_INTEGER));
  const filteredGallery = asArray<any>(gallery)
    .filter((x) => !x.menu_item || x.menu_item === item.id)
    .sort((a, b) => (a?.order ?? Number.MAX_SAFE_INTEGER) - (b?.order ?? Number.MAX_SAFE_INTEGER));

  return { item, filteredSections, filteredFaqs, filteredGallery };
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const { item } = await getAcademicItem(slug);
  if (!item?.id) notFound();
  return buildMetadata({
    title: item.meta_title?.trim() || item.title?.trim() || "Academics",
    description: item.meta_description?.trim() || item.short_description?.trim() || "Academic details",
    path: `/academics/${item.slug || slug}`,
  });
}

export default async function AcademicDetail({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const { item, filteredSections, filteredFaqs, filteredGallery } = await getAcademicItem(slug);
  if (!item?.id) notFound();

  const breadcrumb = breadcrumbJsonLd([
    { name: "Home", path: "/" },
    { name: "Academics", path: "/academics" },
    { name: item.title || "Details", path: `/academics/${item.slug || slug}` },
  ]);

  return (
    <>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumb) }} />
      <DetailLayout item={item} sections={filteredSections} faqs={filteredFaqs} gallery={filteredGallery} />
    </>
  );
}
