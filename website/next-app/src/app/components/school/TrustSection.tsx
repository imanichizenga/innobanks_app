interface TrustItem {
  title: string;
  value: string;
  description: string;
}

export default function TrustSection({ items }: { items: TrustItem[] }) {
  if (!items.length) return null;

  return (
    <section className="bg-section">
      <div className="container mx-auto max-w-screen-xl px-4">
        <h3 className="!text-2xl !text-midnight_text">Trust & Credibility</h3>
        <p className="mt-2 max-w-3xl text-sm text-gray">Institutional strengths that matter to students, families, and education partners.</p>
        <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {items.map((item) => (
            <article key={`${item.title}-${item.value}`} className="rounded-xl border border-blue-100 bg-white p-5 shadow-sm">
              <p className="text-3xl font-bold text-primary">{item.value}</p>
              <h4 className="mt-2 !text-lg !text-midnight_text">{item.title}</h4>
              <p className="mt-1 text-sm text-gray">{item.description}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
