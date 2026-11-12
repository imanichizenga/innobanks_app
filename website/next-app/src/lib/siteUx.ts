export type QuickActionItem = {
  key: string;
  label: string;
  href?: string | null;
  description?: string;
  icon: "apply" | "prospectus" | "fees" | "calendar" | "results" | "admissions";
  external?: boolean;
};

export const quickActions: QuickActionItem[] = [
  { key: "apply", label: "Apply Now", href: "/admission", description: "Start admissions", icon: "apply" },
  { key: "prospectus", label: "Download Prospectus", href: process.env.NEXT_PUBLIC_PROSPECTUS_URL || null, description: "Program details", icon: "prospectus", external: true },
  { key: "fees", label: "Fee Structure", href: process.env.NEXT_PUBLIC_FEE_STRUCTURE_URL || null, description: "View tuition guide", icon: "fees", external: true },
  { key: "calendar", label: "Academic Calendar", href: process.env.NEXT_PUBLIC_ACADEMIC_CALENDAR_URL || null, description: "Key dates", icon: "calendar", external: true },
  { key: "results", label: "Results", href: "/academics/results", description: "Academic outcomes", icon: "results" },
  { key: "contact", label: "Contact Admissions", href: "/contact-us", description: "Talk to our team", icon: "admissions" },
];

export const mobileActions = {
  phone: process.env.NEXT_PUBLIC_CONTACT_PHONE || "+255700000000",
  whatsapp: process.env.NEXT_PUBLIC_WHATSAPP_NUMBER || "+255700000000",
  apply: true,
};

export const admissionsJourneyFallback = [
  { title: "Choose Program", description: "Select the right level and pathway for your child.", key: "01" },
  { title: "Submit Application", description: "Complete the online or in-person application form.", key: "02" },
  { title: "Assessment & Review", description: "We review records and schedule placement where required.", key: "03" },
  { title: "Receive Confirmation", description: "Admissions office shares confirmation and onboarding steps.", key: "04" },
  { title: "Join the School", description: "Begin classes and integrate into school life with confidence.", key: "05" },
];

export const trustHighlightsFallback = [
  { title: "Exam Performance", value: "98%", description: "Students meeting or exceeding benchmark scores." },
  { title: "Accreditation", value: "Registered", description: "Fully recognized and compliant with education standards." },
  { title: "Years of Service", value: "15+", description: "Delivering quality education to the community." },
  { title: "Student Community", value: "1,200+", description: "Active learners across multiple programs and levels." },
  { title: "Qualified Staff", value: "85+", description: "Experienced teachers and student support specialists." },
  { title: "University Pathways", value: "90%", description: "Graduates progressing to higher education opportunities." },
];

export const testimonialFallback = [
  {
    quote: "The admissions process was clear and supportive from start to finish.",
    name: "Amina R.",
    role: "Parent",
    rating: 5,
  },
  {
    quote: "Teachers are approachable and genuinely focused on helping students grow.",
    name: "Daniel M.",
    role: "Student",
    rating: 5,
  },
  {
    quote: "The school balances academics, discipline, and confidence-building activities.",
    name: "Grace K.",
    role: "Alumni Parent",
    rating: 4,
  },
];
