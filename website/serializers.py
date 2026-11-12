from rest_framework import serializers
from .models import (
    HomePage,
    HomeSlider,
    HomeFeature,
    HomeStatistic,
    HomeGallery,
    HomeVideo,
    HomeNotice,
    HomeEnquirySubmission,
    HomeTestimonial,

    CourseCategory,
    Course,
    CourseDetail,
    CourseRequirement,
    CourseOutcome,
    CourseGallery,
    CourseFAQ,

    AcademicPage,
    AcademicMenuItem,
    AcademicSection,
    AcademicGallery,
    AcademicFAQ,

    AdmissionPage,
    AdmissionCategory,
    AdmissionSection,
    AdmissionRequirement,
    AdmissionFAQ,
    AdmissionGallery,

    ContactPage,
    ContactInfoCard,
    ContactOffice,
    SocialLink,

    NewsEventPage,
    NewsEventCategory,
    NewsItem,
    EventItem,
    EventFAQ,
    NewsEventGallery,

    AboutPage,
    AboutMenuItem,
    AboutSection,
    AboutFAQ,
    LeadershipMember,

    StudentLifePage,
    StudentLifeMenuItem,
    StudentLifeSection,
    StudentLifeGallery,
    StudentLifeFAQ,
)


# =========================================================
# HOME
# =========================================================

class HomeSliderSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeSlider
        fields = "__all__"


class HomeFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeFeature
        fields = "__all__"


class HomeStatisticSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeStatistic
        fields = "__all__"


class HomeGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeGallery
        fields = "__all__"


class HomeVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeVideo
        fields = "__all__"


class HomeNoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeNotice
        fields = "__all__"


class HomeEnquirySubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeEnquirySubmission
        fields = "__all__"


class HomeTestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeTestimonial
        fields = "__all__"
        read_only_fields = ("is_approved", "order", "created_at", "updated_at")


class HomePageSerializer(serializers.ModelSerializer):
    sliders = HomeSliderSerializer(many=True, read_only=True)
    features = HomeFeatureSerializer(many=True, read_only=True)
    statistics = HomeStatisticSerializer(many=True, read_only=True)
    gallery = HomeGallerySerializer(many=True, read_only=True)
    videos = HomeVideoSerializer(many=True, read_only=True)

    class Meta:
        model = HomePage
        fields = "__all__"


# =========================================================
# COURSES
# =========================================================

class CourseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseCategory
        fields = "__all__"


class CourseDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseDetail
        fields = "__all__"


class CourseRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseRequirement
        fields = "__all__"


class CourseOutcomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseOutcome
        fields = "__all__"


class CourseGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseGallery
        fields = "__all__"


class CourseFAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseFAQ
        fields = "__all__"


class CourseSerializer(serializers.ModelSerializer):
    category_detail = CourseCategorySerializer(source="category", read_only=True)
    details = CourseDetailSerializer(many=True, read_only=True)
    requirements = CourseRequirementSerializer(many=True, read_only=True)
    outcomes = CourseOutcomeSerializer(many=True, read_only=True)
    gallery = CourseGallerySerializer(many=True, read_only=True)
    faqs = CourseFAQSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = "__all__"


# =========================================================
# ACADEMICS
# =========================================================

class AcademicSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicSection
        fields = "__all__"


class AcademicGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicGallery
        fields = "__all__"


class AcademicFAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicFAQ
        fields = "__all__"


class AcademicMenuItemSerializer(serializers.ModelSerializer):
    sections = AcademicSectionSerializer(many=True, read_only=True)
    gallery = AcademicGallerySerializer(many=True, read_only=True)
    faqs = AcademicFAQSerializer(many=True, read_only=True)

    class Meta:
        model = AcademicMenuItem
        fields = "__all__"


class AcademicPageSerializer(serializers.ModelSerializer):
    menu_items = AcademicMenuItemSerializer(many=True, read_only=True)

    class Meta:
        model = AcademicPage
        fields = "__all__"


# =========================================================
# ADMISSION
# =========================================================

class AdmissionSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdmissionSection
        fields = "__all__"


class AdmissionRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdmissionRequirement
        fields = "__all__"


class AdmissionFAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdmissionFAQ
        fields = "__all__"


class AdmissionGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = AdmissionGallery
        fields = "__all__"


class AdmissionCategorySerializer(serializers.ModelSerializer):
    sections = AdmissionSectionSerializer(many=True, read_only=True)
    requirements = AdmissionRequirementSerializer(many=True, read_only=True)
    faqs = AdmissionFAQSerializer(many=True, read_only=True)
    gallery = AdmissionGallerySerializer(many=True, read_only=True)

    class Meta:
        model = AdmissionCategory
        fields = "__all__"


class AdmissionPageSerializer(serializers.ModelSerializer):
    categories = AdmissionCategorySerializer(many=True, read_only=True)

    class Meta:
        model = AdmissionPage
        fields = "__all__"


# =========================================================
# CONTACT
# =========================================================

class ContactInfoCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactInfoCard
        fields = "__all__"


class ContactOfficeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactOffice
        fields = "__all__"


class SocialLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialLink
        fields = "__all__"


class ContactPageSerializer(serializers.ModelSerializer):
    info_cards = ContactInfoCardSerializer(many=True, read_only=True)
    offices = ContactOfficeSerializer(many=True, read_only=True)
    social_links = SocialLinkSerializer(many=True, read_only=True)

    class Meta:
        model = ContactPage
        fields = "__all__"


# =========================================================
# NEWS & EVENTS
# =========================================================

class NewsEventGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsEventGallery
        fields = "__all__"


class NewsEventCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsEventCategory
        fields = "__all__"


class NewsItemSerializer(serializers.ModelSerializer):
    category_detail = NewsEventCategorySerializer(source="category", read_only=True)
    gallery = NewsEventGallerySerializer(many=True, read_only=True)

    class Meta:
        model = NewsItem
        fields = "__all__"


class EventFAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventFAQ
        fields = "__all__"


class EventItemSerializer(serializers.ModelSerializer):
    category_detail = NewsEventCategorySerializer(source="category", read_only=True)
    gallery = NewsEventGallerySerializer(many=True, read_only=True)
    faqs = EventFAQSerializer(many=True, read_only=True)

    class Meta:
        model = EventItem
        fields = "__all__"


class NewsEventCategoryDetailSerializer(serializers.ModelSerializer):
    news_items = NewsItemSerializer(many=True, read_only=True)
    event_items = EventItemSerializer(many=True, read_only=True)

    class Meta:
        model = NewsEventCategory
        fields = "__all__"


class NewsEventPageSerializer(serializers.ModelSerializer):
    categories = NewsEventCategoryDetailSerializer(many=True, read_only=True)

    class Meta:
        model = NewsEventPage
        fields = "__all__"


# =========================================================
# ABOUT
# =========================================================

class AboutSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutSection
        fields = "__all__"


class AboutFAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutFAQ
        fields = "__all__"


class AboutMenuItemSerializer(serializers.ModelSerializer):
    sections = AboutSectionSerializer(many=True, read_only=True)
    faqs = AboutFAQSerializer(many=True, read_only=True)

    class Meta:
        model = AboutMenuItem
        fields = "__all__"


class LeadershipMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadershipMember
        fields = "__all__"


class AboutPageSerializer(serializers.ModelSerializer):
    menu_items = AboutMenuItemSerializer(many=True, read_only=True)
    leadership_members = LeadershipMemberSerializer(many=True, read_only=True)

    class Meta:
        model = AboutPage
        fields = "__all__"


# =========================================================
# STUDENT LIFE
# =========================================================

class StudentLifeSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentLifeSection
        fields = "__all__"


class StudentLifeGallerySerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentLifeGallery
        fields = "__all__"


class StudentLifeFAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentLifeFAQ
        fields = "__all__"


class StudentLifeMenuItemSerializer(serializers.ModelSerializer):
    sections = StudentLifeSectionSerializer(many=True, read_only=True)
    gallery = StudentLifeGallerySerializer(many=True, read_only=True)
    faqs = StudentLifeFAQSerializer(many=True, read_only=True)

    class Meta:
        model = StudentLifeMenuItem
        fields = "__all__"


class StudentLifePageSerializer(serializers.ModelSerializer):
    menu_items = StudentLifeMenuItemSerializer(many=True, read_only=True)

    class Meta:
        model = StudentLifePage
        fields = "__all__"
