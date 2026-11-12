export function SkeletonBlock({ className }: { className?: string }) {
  return <div className={`animate-pulse rounded-lg bg-slate-200/80 ${className || ""}`} aria-hidden="true" />;
}

export function SkeletonSectionHeading() {
  return (
    <div className="space-y-3">
      <SkeletonBlock className="h-9 w-56 max-w-full" />
      <SkeletonBlock className="h-4 w-full max-w-2xl" />
      <SkeletonBlock className="h-4 w-4/5 max-w-xl" />
    </div>
  );
}

export function SkeletonHero({ compact = false }: { compact?: boolean }) {
  return (
    <section className="relative !py-0">
      <div className={`overflow-hidden ${compact ? "h-[34vh] min-h-[220px]" : "h-[48vh] min-h-[320px]"}`}>
        <SkeletonBlock className="h-full w-full rounded-none" />
        <div className="container relative z-10 mx-auto flex h-full max-w-screen-xl items-end px-4 pb-8">
          <div className="w-full max-w-3xl space-y-3 rounded-2xl border border-white/50 bg-white/70 p-6 backdrop-blur-sm">
            <SkeletonBlock className="h-4 w-28" />
            <SkeletonBlock className="h-9 w-4/5" />
            <SkeletonBlock className="h-4 w-full" />
            <SkeletonBlock className="h-4 w-11/12" />
            <div className="pt-2">
              <SkeletonBlock className="h-10 w-36" />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export function SkeletonCardGrid({ count = 6 }: { count?: number }) {
  return (
    <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
      {Array.from({ length: count }).map((_, index) => (
        <article key={`skeleton-card-${index}`} className="overflow-hidden rounded-xl border border-blue-100 bg-white shadow-sm">
          <SkeletonBlock className="h-48 w-full rounded-none" />
          <div className="space-y-3 p-5">
            <SkeletonBlock className="h-3 w-2/5" />
            <SkeletonBlock className="h-6 w-4/5" />
            <SkeletonBlock className="h-4 w-full" />
            <SkeletonBlock className="h-4 w-11/12" />
            <SkeletonBlock className="h-4 w-2/5" />
          </div>
        </article>
      ))}
    </div>
  );
}

export function SkeletonListRows({ count = 4 }: { count?: number }) {
  return (
    <div className="space-y-4">
      {Array.from({ length: count }).map((_, index) => (
        <article key={`skeleton-row-${index}`} className="rounded-xl border border-blue-100 bg-white p-4 shadow-sm sm:p-5">
          <div className="flex flex-col gap-4 sm:flex-row">
            <SkeletonBlock className="h-24 w-full sm:h-28 sm:w-32" />
            <div className="flex-1 space-y-3">
              <SkeletonBlock className="h-3 w-2/5" />
              <SkeletonBlock className="h-6 w-4/5" />
              <SkeletonBlock className="h-4 w-full" />
              <SkeletonBlock className="h-4 w-3/4" />
            </div>
          </div>
        </article>
      ))}
    </div>
  );
}

export function SkeletonDetail() {
  return (
    <main>
      <SkeletonHero compact />
      <section>
        <div className="container mx-auto grid max-w-screen-xl gap-8 px-4 lg:grid-cols-12">
          <div className="space-y-6 lg:col-span-8">
            <article className="rounded-xl border border-blue-100 bg-white p-6 shadow-sm">
              <SkeletonBlock className="mb-4 h-7 w-1/2" />
              <div className="space-y-3">
                <SkeletonBlock className="h-4 w-full" />
                <SkeletonBlock className="h-4 w-11/12" />
                <SkeletonBlock className="h-4 w-4/5" />
              </div>
            </article>
            <article className="rounded-xl border border-blue-100 bg-section p-5">
              <SkeletonBlock className="mb-4 h-6 w-44" />
              <SkeletonCardGrid count={3} />
            </article>
          </div>
          <aside className="space-y-6 lg:col-span-4">
            <article className="rounded-xl border border-blue-100 bg-white p-5 shadow-sm">
              <SkeletonBlock className="mb-4 h-6 w-40" />
              <div className="space-y-3">
                <SkeletonBlock className="h-4 w-full" />
                <SkeletonBlock className="h-4 w-5/6" />
                <SkeletonBlock className="h-4 w-2/3" />
              </div>
            </article>
            <article className="rounded-xl border border-blue-100 bg-white p-5 shadow-sm">
              <SkeletonBlock className="mb-4 h-6 w-24" />
              <div className="space-y-3">
                <SkeletonBlock className="h-12 w-full" />
                <SkeletonBlock className="h-12 w-full" />
              </div>
            </article>
          </aside>
        </div>
      </section>
    </main>
  );
}

export function SkeletonHomePage() {
  return (
    <main>
      <SkeletonHero />
      <section>
        <div className="container mx-auto max-w-screen-xl space-y-8 px-4">
          <SkeletonSectionHeading />
          <div className="grid gap-5 md:grid-cols-3">
            <SkeletonBlock className="h-28" />
            <SkeletonBlock className="h-28" />
            <SkeletonBlock className="h-28" />
          </div>
          <SkeletonCardGrid count={6} />
          <SkeletonListRows count={3} />
        </div>
      </section>
    </main>
  );
}
