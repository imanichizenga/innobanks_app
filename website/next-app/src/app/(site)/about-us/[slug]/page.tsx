import type { Metadata } from "next";
import { asArray, fetchAPI, toSlug } from "@/lib/api";
import DetailLayout from "@/app/components/school/DetailLayout";
import { notFound } from "next/navigation";
import { buildMetadata, breadcrumbJsonLd } from "@/lib/seo";

const byOrder = <T extends { order?: number }>(items: T[]) =>
  [...items].sort((a, b) => (a?.order ?? Number.MAX_SAFE_INTEGER) - (b?.order ?? Number.MAX_SAFE_INTEGER));

async function getAboutItem(slug: string) {
  const [menusPayload, sectionsPayload, faqsPayload] = await Promise.all([
    fetchAPI<unknown>("/about-menu-items/"),
    fetchAPI<unknown>("/about-sections/"),
    fetchAPI<unknown>("/about-faqs/"),
  ]);

  const menuItems = asArray<any>(menusPayload).filter((item) => item?.is_active !== false);
  const item =
    menuItems.find((entry) => entry.slug === slug || toSlug(entry.title || entry.name) === slug) ||
    asArray<any>(menusPayload).find((entry) => entry.slug === slug || toSlug(entry.title || entry.name) === slug) ||
    {};

  const sections = byOrder(
    asArray<any>(sectionsPayload)
      .filter((entry) => entry?.is_active !== false)
      .filter((entry) => !entry.menu_item || entry.menu_item === item.id),
  );

  const nestedFaqs = asArray<any>(item?.faqs)
    .filter((entry) => entry?.is_active !== false)
    .filter((entry) => !entry.menu_item || entry.menu_item === item.id);

  const endpointFaqs = asArray<any>(faqsPayload)
    .filter((entry) => entry?.is_active !== false)
    .filter((entry) => !entry.menu_item || entry.menu_item === item.id);

  const faqs = byOrder(nestedFaqs.length ? nestedFaqs : endpointFaqs);

  return { item, sections, faqs };
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const { item } = await getAboutItem(slug);
  if (!item?.id) notFound();

  return buildMetadata({
    title: item.meta_title?.trim() || item.title?.trim() || "About",
    description: item.meta_description?.trim() || item.short_description?.trim() || "About details",
    path: `/about-us/${item.slug || slug}`,
  });
}

export default async function AboutDetail({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const { item, sections, faqs } = await getAboutItem(slug);
  if (!item?.id) notFound();

  const breadcrumb = breadcrumbJsonLd([
    { name: "Home", path: "/" },
    { name: "About Us", path: "/about-us" },
    { name: item.title || "Details", path: `/about-us/${item.slug || slug}` },
  ]);

  return (
    <>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumb) }} />
      <DetailLayout item={item} sections={sections} faqs={faqs} gallery={[]} />
    </>
  );
}
