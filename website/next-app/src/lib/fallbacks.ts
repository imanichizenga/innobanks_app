import { getImgPath } from "@/utils/pathUtils";

export const fallbackImages = {
  hero: getImgPath("/images/hero/hero-image.jpg"),
  heroAlt: getImgPath("/images/hero/hero-image.png"),
  gallery: getImgPath("/images/tabbar/tab-1.jpg"),
  card: getImgPath("/images/properties/prop-1.jpg"),
  event: getImgPath("/images/blog/blog-image.jpg"),
  avatar: getImgPath("/images/avatar/avatar_1.jpg"),
  logo: getImgPath("/images/logo/logo.svg"),
};

export const fallbackText = {
  schoolName: "BRITISH OPENING SCHOOLS",
  heroTitle: "Nurturing Excellence Through Learning, Leadership, and Character",
  heroDescription:
    "We provide a student-centered education that prepares learners to thrive academically and socially in a changing world.",
};
