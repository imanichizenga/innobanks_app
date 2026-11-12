import { SkeletonCardGrid, SkeletonHero, SkeletonSectionHeading } from "@/app/components/shared/skeletons";

export default function Loading() {
  return (
    <main>
      <SkeletonHero compact />
      <section>
        <div className="container mx-auto max-w-screen-xl space-y-8 px-4">
          <SkeletonSectionHeading />
          <SkeletonCardGrid count={6} />
        </div>
      </section>
    </main>
  );
}
