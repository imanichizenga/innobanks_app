export interface ApiListResponse<T> {
  results?: T[];
  data?: T[];
}

export interface BaseEntity {
  id?: number;
  slug?: string;
  title?: string;
  name?: string;
  description?: string;
  short_description?: string;
  image?: string;
  banner_image?: string;
  featured_image?: string;
  is_featured?: boolean;
  created_at?: string;
}

export interface NavItem {
  label: string;
  href?: string;
  children?: { label: string; href: string }[];
}

export interface FAQItem extends BaseEntity {
  question?: string;
  answer?: string;
}
