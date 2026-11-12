interface StepItem {
  key: string;
  title: string;
  description: string;
}

export default function AdmissionsJourneySection({ steps }: { steps: StepItem[] }) {
  if (!steps.length) return null;

  return (
    <section>
      <div className="container mx-auto max-w-screen-xl px-4">
        <div className="rounded-2xl border border-blue-100 bg-white p-5 shadow-sm md:p-8">
          <h3 className="!text-2xl !text-midnight_text">Admissions Journey</h3>
          <p className="mt-2 max-w-3xl text-sm text-gray">A simple step-by-step process to guide families from enquiry to enrollment.</p>
          <div className="mt-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
            {steps.map((step) => (
              <article key={step.key} className="rounded-xl border border-blue-100 bg-section p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.16em] text-primary">Step {step.key}</p>
                <h4 className="mt-2 !text-base !text-midnight_text">{step.title}</h4>
                <p className="mt-2 text-sm text-gray">{step.description}</p>
              </article>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
