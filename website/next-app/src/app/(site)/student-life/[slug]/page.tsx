import type { Metadata } from "next";
import { asArray, fetchAPI, toSlug } from "@/lib/api";
import DetailLayout from "@/app/components/school/DetailLayout";
import { notFound } from "next/navigation";
import { buildMetadata, breadcrumbJsonLd } from "@/lib/seo";

async function getStudentLifeItem(slug: string) {
  const [menus, sections, faqs, gallery] = await Promise.all([
    fetchAPI<unknown>("/student-life-menu-items/"),
    fetchAPI<unknown>("/student-life-sections/"),
    fetchAPI<unknown>("/student-life-faqs/"),
    fetchAPI<unknown>("/student-life-gallery/"),
  ]);
  const item = asArray<any>(menus).find((x) => x.slug === slug || toSlug(x.title || x.name) === slug) || {};
  return {
    item,
    sections: asArray<any>(sections).filter((x) => !x.menu_item || x.menu_item === item.id),
    faqs: asArray<any>(faqs).filter((x) => !x.menu_item || x.menu_item === item.id),
    gallery: asArray<any>(gallery).filter((x) => !x.menu_item || x.menu_item === item.id),
  };
}

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const { item } = await getStudentLifeItem(slug);
  if (!item?.id) notFound();
  return buildMetadata({
    title: item.meta_title?.trim() || item.title?.trim() || "Student Life",
    description: item.meta_description?.trim() || item.short_description?.trim() || "Student life details.",
    path: `/student-life/${item.slug || slug}`,
  });
}

export default async function StudentLifeDetail({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const { item, sections, faqs, gallery } = await getStudentLifeItem(slug);
  if (!item?.id) notFound();
  const breadcrumb = breadcrumbJsonLd([
    { name: "Home", path: "/" },
    { name: "Student Life", path: "/student-life" },
    { name: item.title || "Details", path: `/student-life/${item.slug || slug}` },
  ]);

  return (
    <>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumb) }} />
      <DetailLayout item={item} sections={sections} faqs={faqs} gallery={gallery} />
    </>
  );
}
