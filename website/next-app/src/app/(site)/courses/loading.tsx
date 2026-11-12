import { SkeletonBlock, SkeletonCardGrid, SkeletonSectionHeading } from "@/app/components/shared/skeletons";

export default function Loading() {
  return (
    <main>
      <section>
        <div className="container mx-auto max-w-screen-xl space-y-6 px-4">
          <SkeletonSectionHeading />
          <div className="mb-6 flex flex-wrap gap-2">
            {Array.from({ length: 6 }).map((_, index) => (
              <SkeletonBlock key={`chip-skeleton-${index}`} className="h-7 w-24 rounded-full" />
            ))}
          </div>
          <SkeletonCardGrid count={6} />
        </div>
      </section>
    </main>
  );
}
