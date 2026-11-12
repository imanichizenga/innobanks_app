from django.shortcuts import render
from django.http import Http404,HttpResponse
import re
# Helper function to get Host object based on hostname
from django.http import Http404
from .models import Host
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from website.models import Host

def get_host_object(request):
    hostname = request.get_host().split(':')[0]  # e.g., 'localhost'
    print(f"Hostname: {hostname}")  # Debugging
    try:
        return Host.objects.get(host_name=hostname)
    except Host.DoesNotExist:
        default_host, created = Host.objects.get_or_create(
            host_name='localhost',
            defaults={'host_name': 'localhost'}  # Add other default values as needed
        )
        if created:
            print(f"Created default Host object for 'localhost'")
        return default_host
    
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, BasePermission
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser

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

from .serializers import (
    HomePageSerializer,
    HomeSliderSerializer,
    HomeFeatureSerializer,
    HomeStatisticSerializer,
    HomeGallerySerializer,
    HomeVideoSerializer,
    HomeNoticeSerializer,
    HomeEnquirySubmissionSerializer,
    HomeTestimonialSerializer,

    CourseCategorySerializer,
    CourseSerializer,
    CourseDetailSerializer,
    CourseRequirementSerializer,
    CourseOutcomeSerializer,
    CourseGallerySerializer,
    CourseFAQSerializer,

    AcademicPageSerializer,
    AcademicMenuItemSerializer,
    AcademicSectionSerializer,
    AcademicGallerySerializer,
    AcademicFAQSerializer,

    AdmissionPageSerializer,
    AdmissionCategorySerializer,
    AdmissionSectionSerializer,
    AdmissionRequirementSerializer,
    AdmissionFAQSerializer,
    AdmissionGallerySerializer,

    ContactPageSerializer,
    ContactInfoCardSerializer,
    ContactOfficeSerializer,
    SocialLinkSerializer,

    NewsEventPageSerializer,
    NewsEventCategorySerializer,
    NewsItemSerializer,
    EventItemSerializer,
    EventFAQSerializer,
    NewsEventGallerySerializer,

    AboutPageSerializer,
    AboutMenuItemSerializer,
    AboutSectionSerializer,
    AboutFAQSerializer,
    LeadershipMemberSerializer,

    StudentLifePageSerializer,
    StudentLifeMenuItemSerializer,
    StudentLifeSectionSerializer,
    StudentLifeGallerySerializer,
    StudentLifeFAQSerializer,
)


class BaseModelViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]


def user_can_manage_home_enquiries(user):
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True

    teacher = user.teacher_profile.select_related("userpermission").first()
    if not teacher:
        return False

    permission = getattr(teacher, "userpermission", None)
    return bool(permission and permission.can_manage_home_enquiries)


class HomeEnquirySubmissionPermission(BasePermission):
    def has_permission(self, request, view):
        if getattr(view, "action", None) == "create":
            return True
        return user_can_manage_home_enquiries(request.user)


# =========================================================
# HOME
# =========================================================

class HomePageViewSet(BaseModelViewSet):
    queryset = HomePage.objects.all().order_by("-created_at")
    serializer_class = HomePageSerializer


class HomeSliderViewSet(BaseModelViewSet):
    queryset = HomeSlider.objects.all().order_by("order")
    serializer_class = HomeSliderSerializer


class HomeFeatureViewSet(BaseModelViewSet):
    queryset = HomeFeature.objects.all().order_by("order")
    serializer_class = HomeFeatureSerializer


class HomeStatisticViewSet(BaseModelViewSet):
    queryset = HomeStatistic.objects.all().order_by("order")
    serializer_class = HomeStatisticSerializer


class HomeGalleryViewSet(BaseModelViewSet):
    queryset = HomeGallery.objects.all().order_by("order")
    serializer_class = HomeGallerySerializer


class HomeVideoViewSet(BaseModelViewSet):
    queryset = HomeVideo.objects.all().order_by("order", "-created_at")
    serializer_class = HomeVideoSerializer


class HomeNoticeViewSet(BaseModelViewSet):
    queryset = HomeNotice.objects.all().order_by("-created_at")
    serializer_class = HomeNoticeSerializer


class HomeEnquirySubmissionViewSet(BaseModelViewSet):
    queryset = HomeEnquirySubmission.objects.all().order_by("-created_at")
    serializer_class = HomeEnquirySubmissionSerializer
    permission_classes = [HomeEnquirySubmissionPermission]

    def perform_create(self, serializer):
        serializer.save(
            is_contacted=False,
            contacted_at=None,
            contacted_by=None,
            contact_notes=None,
        )


class HomeTestimonialViewSet(BaseModelViewSet):
    serializer_class = HomeTestimonialSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        base = HomeTestimonial.objects.all().order_by("order", "-created_at")
        if self.action == "list":
            return base.filter(is_approved=True)
        return base

    def perform_create(self, serializer):
        serializer.save(is_approved=False)


# =========================================================
# COURSES
# =========================================================

class CourseCategoryViewSet(BaseModelViewSet):
    queryset = CourseCategory.objects.all().order_by("name")
    serializer_class = CourseCategorySerializer


class CourseViewSet(BaseModelViewSet):
    queryset = Course.objects.select_related("category").prefetch_related(
        "details", "requirements", "outcomes", "gallery", "faqs"
    ).all().order_by("order", "title")
    serializer_class = CourseSerializer


class CourseDetailViewSet(BaseModelViewSet):
    queryset = CourseDetail.objects.all().order_by("order")
    serializer_class = CourseDetailSerializer


class CourseRequirementViewSet(BaseModelViewSet):
    queryset = CourseRequirement.objects.all().order_by("order")
    serializer_class = CourseRequirementSerializer


class CourseOutcomeViewSet(BaseModelViewSet):
    queryset = CourseOutcome.objects.all().order_by("order")
    serializer_class = CourseOutcomeSerializer


class CourseGalleryViewSet(BaseModelViewSet):
    queryset = CourseGallery.objects.all().order_by("order")
    serializer_class = CourseGallerySerializer


class CourseFAQViewSet(BaseModelViewSet):
    queryset = CourseFAQ.objects.all().order_by("order")
    serializer_class = CourseFAQSerializer


# =========================================================
# ACADEMICS
# =========================================================

class AcademicPageViewSet(BaseModelViewSet):
    queryset = AcademicPage.objects.prefetch_related("menu_items__sections", "menu_items__gallery", "menu_items__faqs").all().order_by("-created_at")
    serializer_class = AcademicPageSerializer


class AcademicMenuItemViewSet(BaseModelViewSet):
    queryset = AcademicMenuItem.objects.prefetch_related("sections", "gallery", "faqs").all().order_by("order", "title")
    serializer_class = AcademicMenuItemSerializer


class AcademicSectionViewSet(BaseModelViewSet):
    queryset = AcademicSection.objects.all().order_by("order", "title")
    serializer_class = AcademicSectionSerializer


class AcademicGalleryViewSet(BaseModelViewSet):
    queryset = AcademicGallery.objects.all().order_by("order", "title")
    serializer_class = AcademicGallerySerializer


class AcademicFAQViewSet(BaseModelViewSet):
    queryset = AcademicFAQ.objects.all().order_by("order", "question")
    serializer_class = AcademicFAQSerializer


# =========================================================
# ADMISSION
# =========================================================

class AdmissionPageViewSet(BaseModelViewSet):
    queryset = AdmissionPage.objects.prefetch_related(
        "categories__sections",
        "categories__requirements",
        "categories__faqs",
        "categories__gallery"
    ).all().order_by("-created_at")
    serializer_class = AdmissionPageSerializer


class AdmissionCategoryViewSet(BaseModelViewSet):
    queryset = AdmissionCategory.objects.prefetch_related(
        "sections", "requirements", "faqs", "gallery"
    ).all().order_by("order", "title")
    serializer_class = AdmissionCategorySerializer


class AdmissionSectionViewSet(BaseModelViewSet):
    queryset = AdmissionSection.objects.all().order_by("order", "title")
    serializer_class = AdmissionSectionSerializer


class AdmissionRequirementViewSet(BaseModelViewSet):
    queryset = AdmissionRequirement.objects.all().order_by("order")
    serializer_class = AdmissionRequirementSerializer


class AdmissionFAQViewSet(BaseModelViewSet):
    queryset = AdmissionFAQ.objects.all().order_by("order", "question")
    serializer_class = AdmissionFAQSerializer


class AdmissionGalleryViewSet(BaseModelViewSet):
    queryset = AdmissionGallery.objects.all().order_by("order", "title")
    serializer_class = AdmissionGallerySerializer


# =========================================================
# CONTACT
# =========================================================

class ContactPageViewSet(BaseModelViewSet):
    queryset = ContactPage.objects.prefetch_related("info_cards", "offices", "social_links").all().order_by("-created_at")
    serializer_class = ContactPageSerializer


class ContactInfoCardViewSet(BaseModelViewSet):
    queryset = ContactInfoCard.objects.all().order_by("order", "title")
    serializer_class = ContactInfoCardSerializer


class ContactOfficeViewSet(BaseModelViewSet):
    queryset = ContactOffice.objects.all().order_by("order", "name")
    serializer_class = ContactOfficeSerializer


class SocialLinkViewSet(BaseModelViewSet):
    queryset = SocialLink.objects.all().order_by("order", "name")
    serializer_class = SocialLinkSerializer


# =========================================================
# NEWS & EVENTS
# =========================================================

class NewsEventPageViewSet(BaseModelViewSet):
    queryset = NewsEventPage.objects.prefetch_related(
        "categories__news_items__gallery",
        "categories__event_items__gallery"
    ).all().order_by("-created_at")
    serializer_class = NewsEventPageSerializer


class NewsEventCategoryViewSet(BaseModelViewSet):
    queryset = NewsEventCategory.objects.prefetch_related("news_items__gallery", "event_items__gallery").all().order_by("order", "title")
    serializer_class = NewsEventCategorySerializer


class NewsItemViewSet(BaseModelViewSet):
    queryset = NewsItem.objects.select_related("category").prefetch_related("gallery").all().order_by("-publish_date", "-created_at")
    serializer_class = NewsItemSerializer


class EventItemViewSet(BaseModelViewSet):
    queryset = EventItem.objects.select_related("category").prefetch_related("gallery", "faqs").all().order_by("-event_date", "-created_at")
    serializer_class = EventItemSerializer


class EventFAQViewSet(BaseModelViewSet):
    queryset = EventFAQ.objects.select_related("event_item").all().order_by("order", "question")
    serializer_class = EventFAQSerializer


class NewsEventGalleryViewSet(BaseModelViewSet):
    queryset = NewsEventGallery.objects.all().order_by("order", "title")
    serializer_class = NewsEventGallerySerializer


# =========================================================
# ABOUT
# =========================================================

class AboutPageViewSet(BaseModelViewSet):
    queryset = AboutPage.objects.prefetch_related("menu_items__sections", "menu_items__faqs", "leadership_members").all().order_by("-created_at")
    serializer_class = AboutPageSerializer


class AboutMenuItemViewSet(BaseModelViewSet):
    queryset = AboutMenuItem.objects.prefetch_related("sections", "faqs").all().order_by("order", "title")
    serializer_class = AboutMenuItemSerializer


class AboutSectionViewSet(BaseModelViewSet):
    queryset = AboutSection.objects.all().order_by("order", "title")
    serializer_class = AboutSectionSerializer


class AboutFAQViewSet(BaseModelViewSet):
    queryset = AboutFAQ.objects.all().order_by("order", "question")
    serializer_class = AboutFAQSerializer


class LeadershipMemberViewSet(BaseModelViewSet):
    queryset = LeadershipMember.objects.all().order_by("order", "full_name")
    serializer_class = LeadershipMemberSerializer


# =========================================================
# STUDENT LIFE
# =========================================================

class StudentLifePageViewSet(BaseModelViewSet):
    queryset = StudentLifePage.objects.prefetch_related(
        "menu_items__sections",
        "menu_items__gallery",
        "menu_items__faqs"
    ).all().order_by("-created_at")
    serializer_class = StudentLifePageSerializer


class StudentLifeMenuItemViewSet(BaseModelViewSet):
    queryset = StudentLifeMenuItem.objects.prefetch_related("sections", "gallery", "faqs").all().order_by("order", "title")
    serializer_class = StudentLifeMenuItemSerializer


class StudentLifeSectionViewSet(BaseModelViewSet):
    queryset = StudentLifeSection.objects.all().order_by("order", "title")
    serializer_class = StudentLifeSectionSerializer


class StudentLifeGalleryViewSet(BaseModelViewSet):
    queryset = StudentLifeGallery.objects.all().order_by("order", "title")
    serializer_class = StudentLifeGallerySerializer


class StudentLifeFAQViewSet(BaseModelViewSet):
    queryset = StudentLifeFAQ.objects.all().order_by("order", "question")
    serializer_class = StudentLifeFAQSerializer
