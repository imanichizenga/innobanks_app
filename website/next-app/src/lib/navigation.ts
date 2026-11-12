import { NavItem } from "./types";

export const schoolNav: NavItem[] = [
  { label: "Home", href: "/" },
  {
    label: "Academics",
    href: "/academics",
    children: [
      { label: "Results", href: "/academics/results" },
      { label: "Course", href: "/academics/course" },
      { label: "Course Details", href: "/academics/course-details" },
    ],
  },
  {
    label: "Admission",
    href: "/admission",
    children: ["ftna", "csee", "acsee", "computer-course","childhood-education", "english-course"].map((slug) => ({
      label: slug.toUpperCase().replace("-", " "),
      href: `/admission/${slug}`,
    })),
  },
  {
    label: "Student Life",
    href: "/student-life",
    children: [
      { label: "Studies", href: "/student-life/studies" },
      { label: "Learning Environment", href: "/student-life/learning-environment" },
    ],
  },
  {
    label: "About Us",
    href: "/about-us",
    children: [
      { label: "Community", href: "/about-us/community" },
      { label: "Parents and Teacher Association", href: "/about-us/parents-and-teacher-association" },
    ],
  },
  {
    label: "News and Events",
    href: "/news",
    children: [
      { label: "Student Events", href: "/events?category=student-events" },
      { label: "Staff Events", href: "/events?category=staff-events" },
      { label: "Students and Staff Events", href: "/events?category=students-and-staff-events" },
    ],
  },
  { label: "Contact Us", href: "/contact-us" },
];
