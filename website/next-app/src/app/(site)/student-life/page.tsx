import type { Metadata } from "next";
import Image from "next/image";
import { asArray, fetchAPI, getMediaUrl } from "@/lib/api";
import SectionHeading from "@/app/components/school/SectionHeading";
import { GenericCard } from "@/app/components/school/cards";
import { buildMetadata } from "@/lib/seo";
import { fallbackImages } from "@/lib/fallbacks";

async function getStudentLifeData() {
  const [pages, menus] = await Promise.all([fetchAPI<unknown>("/student-life-pages/"), fetchAPI<unknown>("/student-life-menu-items/")]);
  const page = asArray<any>(pages).find((item) => item?.is_active !== false) || asArray<any>(pages)[0] || {};
  const menuItems = asArray<any>(menus).filter((item) => item?.is_active !== false);
  return { page, menuItems };
}

export async function generateMetadata(): Promise<Metadata> {
  const { page } = await getStudentLifeData();
  return buildMetadata({
    title: page.meta_title?.trim() || page.title?.trim() || "Student Life",
    description: page.meta_description?.trim() || page.description?.trim() || "Studies, activities, and a supportive learning environment.",
    path: "/student-life",
    image: getMediaUrl(page.hero_image, fallbackImages.heroAlt),
  });
}

export default async function StudentLifePage() {
  const { page, menuItems } = await getStudentLifeData();
  const pageTitle = page.title?.trim() || "Student Life";
  const pageSubtitle = page.subtitle?.trim();
  const pageDescription =
    page.description?.trim() || "Discover clubs, mentorship, leadership opportunities, and a nurturing environment beyond the classroom.";

  return (
    <main>
      <section className="!py-0">
        <div className="relative h-[44vh] min-h-[280px] overflow-hidden md:h-[52vh]">
          <Image src={getMediaUrl(page.hero_image, fallbackImages.heroAlt)} alt={pageTitle} fill priority className="object-cover" />
          <div className="absolute inset-0 bg-[#0f2c52]/60" />
          <div className="container relative z-10 mx-auto flex h-full max-w-screen-xl items-end px-4 pb-8 md:pb-12">
            <div className="max-w-3xl">
              {pageSubtitle ? <p className="mb-2 text-sm font-medium tracking-[0.08em] text-blue-100">{pageSubtitle}</p> : null}
              <h1 className="!text-white">{pageTitle}</h1>
              <p className="mt-3 text-sm text-blue-50 md:text-base">{pageDescription}</p>
            </div>
          </div>
        </div>
      </section>

      <section>
        <div className="container mx-auto max-w-screen-xl px-4">
          <SectionHeading title="Explore Student Life" subtitle={pageDescription} />
          <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
            {menuItems.map((item: any) => (
              <GenericCard key={item.id} item={item} hrefBase="/student-life" />
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}
