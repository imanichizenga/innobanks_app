import type { Metadata } from "next";
import { asArray, fetchAPI } from "@/lib/api";
import SectionHeading from "@/app/components/school/SectionHeading";
import { GenericCard } from "@/app/components/school/cards";
import { buildMetadata } from "@/lib/seo";

export const metadata: Metadata = buildMetadata({
  title: "Courses",
  description: "Find the right program by level, department, and learning outcomes.",
  path: "/courses",
});

export default async function CoursesPage() {
  const [categories, courses] = await Promise.all([fetchAPI<unknown>("/course-categories/"), fetchAPI<unknown>("/courses/")]);
  return (
    <main><section><div className="container mx-auto max-w-screen-xl px-4"><SectionHeading title="Courses" subtitle="Find the right program by level, department, and learning outcomes." /><div className="mb-6 flex flex-wrap gap-2">{asArray<any>(categories).map((c:any)=><span key={c.id} className="rounded-full bg-blue-50 px-3 py-1 text-xs text-primary">{c.title || c.name}</span>)}</div><div className="grid gap-5 md:grid-cols-3">{asArray<any>(courses).map((item:any)=><GenericCard key={item.id} item={item} hrefBase="/courses" />)}</div></div></section></main>
  );
}
