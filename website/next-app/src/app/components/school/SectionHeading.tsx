interface Props { title: string; subtitle?: string; center?: boolean }

export default function SectionHeading({ title, subtitle, center }: Props) {
  return (
    <div className={center ? "mx-auto mb-8 max-w-2xl text-center" : "mb-8"}>
      <h2 className="mb-3 text-midnight_text">{title}</h2>
      {subtitle && <p className="text-gray">{subtitle}</p>}
    </div>
  );
}
