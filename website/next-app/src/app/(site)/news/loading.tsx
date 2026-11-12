import { SkeletonBlock, SkeletonCardGrid, SkeletonHero, SkeletonListRows, SkeletonSectionHeading } from "@/app/components/shared/skeletons";

export default function Loading() {
  return (
    <main>
      <SkeletonHero compact />
      <section>
        <div className="container mx-auto max-w-screen-xl space-y-10 px-4">
          <SkeletonSectionHeading />

          <div>
            <SkeletonBlock className="mb-4 h-7 w-40" />
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {Array.from({ length: 4 }).map((_, index) => (
                <article key={`category-skeleton-${index}`} className="rounded-xl border border-blue-100 bg-white p-4 shadow-sm">
                  <div className="mb-3 flex items-center gap-3">
                    <SkeletonBlock className="h-12 w-12" />
                    <SkeletonBlock className="h-5 w-24" />
                  </div>
                  <SkeletonBlock className="h-4 w-full" />
                  <SkeletonBlock className="mt-2 h-4 w-10/12" />
                </article>
              ))}
            </div>
          </div>

          <div>
            <SkeletonBlock className="mb-4 h-7 w-40" />
            <SkeletonCardGrid count={6} />
          </div>

          <div>
            <SkeletonBlock className="mb-4 h-7 w-48" />
            <SkeletonListRows count={4} />
          </div>
        </div>
      </section>
    </main>
  );
}
