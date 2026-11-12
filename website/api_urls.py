from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    HomePageViewSet,
    HomeSliderViewSet,
    HomeFeatureViewSet,
    HomeStatisticViewSet,
    HomeGalleryViewSet,
    HomeVideoViewSet,
    HomeNoticeViewSet,
    HomeEnquirySubmissionViewSet,
    HomeTestimonialViewSet,

    CourseCategoryViewSet,
    CourseViewSet,
    CourseDetailViewSet,
    CourseRequirementViewSet,
    CourseOutcomeViewSet,
    CourseGalleryViewSet,
    CourseFAQViewSet,

    AcademicPageViewSet,
    AcademicMenuItemViewSet,
    AcademicSectionViewSet,
    AcademicGalleryViewSet,
    AcademicFAQViewSet,

    AdmissionPageViewSet,
    AdmissionCategoryViewSet,
    AdmissionSectionViewSet,
    AdmissionRequirementViewSet,
    AdmissionFAQViewSet,
    AdmissionGalleryViewSet,

    ContactPageViewSet,
    ContactInfoCardViewSet,
    ContactOfficeViewSet,
    SocialLinkViewSet,

    NewsEventPageViewSet,
    NewsEventCategoryViewSet,
    NewsItemViewSet,
    EventItemViewSet,
    EventFAQViewSet,
    NewsEventGalleryViewSet,

    AboutPageViewSet,
    AboutMenuItemViewSet,
    AboutSectionViewSet,
    AboutFAQViewSet,
    LeadershipMemberViewSet,

    StudentLifePageViewSet,
    StudentLifeMenuItemViewSet,
    StudentLifeSectionViewSet,
    StudentLifeGalleryViewSet,
    StudentLifeFAQViewSet,
)

router = DefaultRouter()

# HOME
router.register(r'home-pages', HomePageViewSet, basename='home-page')
router.register(r'home-sliders', HomeSliderViewSet, basename='home-slider')
router.register(r'home-features', HomeFeatureViewSet, basename='home-feature')
router.register(r'home-statistics', HomeStatisticViewSet, basename='home-statistic')
router.register(r'home-gallery', HomeGalleryViewSet, basename='home-gallery')
router.register(r'home-videos', HomeVideoViewSet, basename='home-video')
router.register(r'home-notices', HomeNoticeViewSet, basename='home-notice')
router.register(r'home-enquiry-submissions', HomeEnquirySubmissionViewSet, basename='home-enquiry-submission')
router.register(r'home-testimonials', HomeTestimonialViewSet, basename='home-testimonial')

# COURSES
router.register(r'course-categories', CourseCategoryViewSet, basename='course-category')
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'course-details', CourseDetailViewSet, basename='course-detail')
router.register(r'course-requirements', CourseRequirementViewSet, basename='course-requirement')
router.register(r'course-outcomes', CourseOutcomeViewSet, basename='course-outcome')
router.register(r'course-gallery', CourseGalleryViewSet, basename='course-gallery')
router.register(r'course-faqs', CourseFAQViewSet, basename='course-faq')

# ACADEMICS
router.register(r'academic-pages', AcademicPageViewSet, basename='academic-page')
router.register(r'academic-menu-items', AcademicMenuItemViewSet, basename='academic-menu-item')
router.register(r'academic-sections', AcademicSectionViewSet, basename='academic-section')
router.register(r'academic-gallery', AcademicGalleryViewSet, basename='academic-gallery')
router.register(r'academic-faqs', AcademicFAQViewSet, basename='academic-faq')

# ADMISSION
router.register(r'admission-pages', AdmissionPageViewSet, basename='admission-page')
router.register(r'admission-categories', AdmissionCategoryViewSet, basename='admission-category')
router.register(r'admission-sections', AdmissionSectionViewSet, basename='admission-section')
router.register(r'admission-requirements', AdmissionRequirementViewSet, basename='admission-requirement')
router.register(r'admission-faqs', AdmissionFAQViewSet, basename='admission-faq')
router.register(r'admission-gallery', AdmissionGalleryViewSet, basename='admission-gallery')

# CONTACT
router.register(r'contact-pages', ContactPageViewSet, basename='contact-page')
router.register(r'contact-info-cards', ContactInfoCardViewSet, basename='contact-info-card')
router.register(r'contact-offices', ContactOfficeViewSet, basename='contact-office')
router.register(r'social-links', SocialLinkViewSet, basename='social-link')

# NEWS & EVENTS
router.register(r'news-event-pages', NewsEventPageViewSet, basename='news-event-page')
router.register(r'news-event-categories', NewsEventCategoryViewSet, basename='news-event-category')
router.register(r'news-items', NewsItemViewSet, basename='news-item')
router.register(r'event-items', EventItemViewSet, basename='event-item')
router.register(r'event-faqs', EventFAQViewSet, basename='event-faq')
router.register(r'news-event-gallery', NewsEventGalleryViewSet, basename='news-event-gallery')

# ABOUT
router.register(r'about-pages', AboutPageViewSet, basename='about-page')
router.register(r'about-menu-items', AboutMenuItemViewSet, basename='about-menu-item')
router.register(r'about-sections', AboutSectionViewSet, basename='about-section')
router.register(r'about-faqs', AboutFAQViewSet, basename='about-faq')
router.register(r'leadership-members', LeadershipMemberViewSet, basename='leadership-member')

# STUDENT LIFE
router.register(r'student-life-pages', StudentLifePageViewSet, basename='student-life-page')
router.register(r'student-life-menu-items', StudentLifeMenuItemViewSet, basename='student-life-menu-item')
router.register(r'student-life-sections', StudentLifeSectionViewSet, basename='student-life-section')
router.register(r'student-life-gallery', StudentLifeGalleryViewSet, basename='student-life-gallery')
router.register(r'student-life-faqs', StudentLifeFAQViewSet, basename='student-life-faq')

urlpatterns = [
    path('', include(router.urls)),
]

