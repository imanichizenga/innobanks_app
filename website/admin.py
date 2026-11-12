from django.contrib import admin
from django.utils.html import format_html
from django.http import Http404
from .models import (

     Top, Host
)
from django.contrib.auth import get_user_model

from django.contrib import admin

# Set the overall title for the admin site
admin.site.site_header = "School Administration Panel"
admin.site.site_title = "Admin Portal"
admin.site.index_title = "Welcome to the School Admin Portal"

# Helper function to get Host object based on hostname
def get_host_object(request):
    hostname = request.get_host()
    try:
        return Host.objects.get(host_name=hostname)
    except Host.DoesNotExist:
        raise Http404("Host does not exist")

# Base Admin class to filter by host_required
class HostFilteredAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if not request.user.is_superuser:  # Allow superusers to see all records
            host = get_host_object(request)
            return queryset.filter(host_required=host)
        return queryset

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'host_required' and not request.user.is_superuser:
            host = get_host_object(request)
            kwargs['queryset'] = Host.objects.filter(pk=host.pk)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

# @admin.register(Staff)
# class StaffAdmin(HostFilteredAdmin):
#     """Customizes the admin interface for the Staff model."""
#     list_display = ('heading', 'button', 'description','host_required')
#     search_fields = ('heading', 'description')
#     list_filter = ('host_required',)

# @admin.register(Slide)
# class SlideAdmin(HostFilteredAdmin):
#     """Customizes the admin interface for the Slide model with image previews."""
#     list_display = ('name', 'description', 'image_preview','host_required')
#     search_fields = ('name', 'description')
#     readonly_fields = ('image_preview',)
#     list_filter = ('host_required',)

#     def image_preview(self, obj):
#         if obj.image:
#             return format_html('<img src="{}" width="150" style="border-radius: 5px;" />', obj.image.url)
#         return "No Image"
#     image_preview.short_description = 'Image'

# @admin.register(Footer)
# class FooterAdmin(HostFilteredAdmin):
#     """Organizes the Footer model admin using fieldsets and adds filters."""
#     list_display = ('teacher_name', 'teacher_subject', 'teacher_image_preview')
#     search_fields = ('teacher_name', 'teacher_subject')
#     list_filter = ('teacher_subject', 'host_required')
#     readonly_fields = ('teacher_image_preview',)

#     fieldsets = (
#         ('Teacher Information', {
#             'fields': ('host_required', 'teacher_picture', 'teacher_image_preview', 'teacher_name', 'teacher_subject', 'teacher_description')
#         }),
#         ('Social Media Links (Optional)', {
#             'classes': ('collapse',),
#             'fields': ('fb_link', 'x_link', 'linked_in'),
#         }),
#     )

#     def teacher_image_preview(self, obj):
#         if obj.teacher_picture:
#             return format_html('<img src="{}" width="80" style="border-radius: 50%;" />', obj.teacher_picture.url)
#         return "No Image"
#     teacher_image_preview.short_description = 'Picture'

# @admin.register(Service)
# class ServiceAdmin(HostFilteredAdmin):
#     """Customizes the admin interface for the Service model."""
#     list_display = ('service_name', 'host_required')
#     search_fields = ('service_name',)
#     list_filter = ('host_required',)

# @admin.register(Contact)
# class ContactAdmin(HostFilteredAdmin):
#     """Customizes the admin interface for the Contact model."""
#     list_display = ('school_contact', 'host_required')
#     search_fields = ('school_contact',)
#     list_filter = ('host_required',)

# @admin.register(Gallery)
# class GalleryAdmin(HostFilteredAdmin):
#     """Customizes the admin for Gallery, showing image previews."""
#     list_display = ('gallery_image_preview', 'host_required')
#     readonly_fields = ('gallery_image_preview',)
#     list_filter = ('host_required',)

#     def gallery_image_preview(self, obj):
#         if obj.all_gallery:
#             return format_html('<img src="{}" width="150" style="border-radius: 5px;" />', obj.all_gallery.url)
#         return "No Image"
#     gallery_image_preview.short_description = 'Image'

# @admin.register(About)
# class AboutAdmin(HostFilteredAdmin):
#     """Customizes the admin for the About model to show a preview of the description."""
#     list_display = ('description_preview', 'host_required')
#     search_fields = ('about_us_description',)
#     list_filter = ('host_required',)

#     def description_preview(self, obj):
#         if len(obj.about_us_description) > 100:
#             return f'{obj.about_us_description[:100]}...'
#         return obj.about_us_description
#     description_preview.short_description = 'About Us (Preview)'

# @admin.register(BottomDescription)
# class BottomDescriptionAdmin(HostFilteredAdmin):
#     """Customizes the admin interface for the BottomDescription model."""
#     list_display = ('description', 'host_required')
#     search_fields = ('description',)
#     list_filter = ('host_required',)

# @admin.register(Gallary_Tab2)
# class GallaryTab2Admin(HostFilteredAdmin):
#     list_display = ('heading', 'description', 'button', 'host_required')
#     search_fields = ('heading',)
#     list_filter = ('heading', 'host_required')

# @admin.register(Image_Tab2)
# class ImageTab2Admin(HostFilteredAdmin):
#     list_display = ('heading', 'description', 'image', 'host_required')
#     search_fields = ('heading',)
#     list_filter = ('heading', 'host_required')

# @admin.register(BottomImage_Tab2)
# class BottomImageTab2Admin(HostFilteredAdmin):
#     list_display = ('title', 'image', 'host_required')
#     search_fields = ('title',)
#     list_filter = ('title', 'host_required')

# @admin.register(Instructor)
# class InstructorAdmin(HostFilteredAdmin):
#     list_display = ('heading', 'button', 'image_heading', 'host_required')
#     search_fields = ('heading', 'image_heading')
#     list_filter = ('heading', 'host_required')
#     ordering = ('heading',)

# @admin.register(AllList)
# class AllListAdmin(HostFilteredAdmin):
#     list_display = ('list_required', 'host_required')
#     search_fields = ('list_required',)
#     list_filter = ('host_required',)

@admin.register(Top)
class TopAdmin(admin.ModelAdmin):  # Not using HostFilteredAdmin since it has user-specific logic
    list_display = ('user', 'question', 'contact', 'email', 'host_required','icon_required','school_name')
    search_fields = ('user__username', 'email')
    list_filter = ('user__is_superuser', 'host_required')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        User = get_user_model()
        if db_field.name == 'user':
            kwargs['queryset'] = User.objects.filter(is_teacher=True)
        if db_field.name == 'host_required' and not request.user.is_superuser:
            host = get_host_object(request)
            kwargs['queryset'] = Host.objects.filter(pk=host.pk)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Host)
class HostAdmin(admin.ModelAdmin):
    list_display = ('host_name',)
    search_fields = ('host_name',)


# @admin.register(Video)
# class VideoAdmin(admin.ModelAdmin):
#     list_display = ('title', 'uploaded_by', 'uploaded_at', 'like_count')
#     list_filter = ('uploaded_at', 'uploaded_by')
#     search_fields = ('title', 'uploaded_by__username')
#     readonly_fields = ('uploaded_at', 'like_count')
#     date_hierarchy = 'uploaded_at'
#     ordering = ('-uploaded_at',)

#     def like_count(self, obj):
#         return obj.like_count()
#     like_count.short_description = 'Number of Likes'


# from django.contrib import admin
# from .models import AboutBottom

# @admin.register(AboutBottom)
# class AboutBottomAdmin(admin.ModelAdmin):
#     list_display = ('heading', 'host_required', 'list_display')
#     search_fields = ('heading', 'description', 'list_display')
#     list_filter = ('host_required',)
#     fieldsets = (
#         (None, {
#             'fields': ('host_required', 'heading', 'description', 'list_display')
#         }),
#         ('Images', {
#             'fields': ('single_image', 'image'),
#             'description': 'Upload images displayed in the Gallery Tab.'
#         }),
#     )

#     def __str__(self, obj):
#         return obj.heading if obj.heading else 'No Heading'


# from django.contrib import admin
# from django.contrib import admin
# from django.utils.safestring import mark_safe
# from .models import FeaturedClass

# @admin.register(FeaturedClass)
# class FeaturedClassAdmin(admin.ModelAdmin):
#     list_display = ('display_image', 'title', 'host_required', 'created_at')
#     list_filter = ('host_required', 'created_at')
#     search_fields = ('title', 'description')
#     ordering = ('-created_at',)
#     date_hierarchy = 'created_at'
#     list_per_page = 20

#     fieldsets = (
#         (None, {
#             'fields': ('host_required', 'title', 'image', 'description')
#         }),
#     )

#     def display_image(self, obj):
#         if obj.image:
#             return mark_safe(f'<img src="{obj.image.url}" style="max-width: 50px; max-height: 50px;" alt="{obj.title}" />')
#         return 'No Image'
#     display_image.short_description = 'Image'




from website.models import UserEmailSettings

@admin.register(UserEmailSettings)
class UserEmailSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_host', 'email_port', 'email_host_user', 'default_from_email')
    search_fields = ('user__username', 'email_host_user', 'default_from_email')
    list_filter = ('email_host', 'email_use_tls')

    def get_queryset(self, request):
        # Filter the queryset to show only UserEmailSettings for superusers
        queryset = super().get_queryset(request)
        return queryset.filter(user__is_superuser=True)

    def has_add_permission(self, request):
        # Optional: Restrict adding new settings to superusers only
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        # Optional: Restrict editing to superusers only
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        # Optional: Restrict deletion to superusers only
        return request.user.is_superuser


from django.contrib import admin
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
# COMMON MIXIN
# =========================================================

class TimeStampedAdmin(admin.ModelAdmin):
    readonly_fields = ("created_at", "updated_at")


# =========================================================
# HOME
# =========================================================

class HomeSliderInline(admin.TabularInline):
    model = HomeSlider
    extra = 1


class HomeFeatureInline(admin.TabularInline):
    model = HomeFeature
    extra = 1


class HomeStatisticInline(admin.TabularInline):
    model = HomeStatistic
    extra = 1


class HomeGalleryInline(admin.TabularInline):
    model = HomeGallery
    extra = 1


class HomeVideoInline(admin.TabularInline):
    model = HomeVideo
    extra = 1


@admin.register(HomePage)
class HomePageAdmin(TimeStampedAdmin):
    list_display = ("hero_title", "welcome_title", "is_active", "created_at", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("hero_title", "welcome_title", "meta_title")
    inlines = [HomeSliderInline, HomeFeatureInline, HomeStatisticInline, HomeGalleryInline, HomeVideoInline]


@admin.register(HomeSlider)
class HomeSliderAdmin(TimeStampedAdmin):
    list_display = ("title", "home_page", "order", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("title", "subtitle")
    ordering = ("order",)


@admin.register(HomeFeature)
class HomeFeatureAdmin(TimeStampedAdmin):
    list_display = ("title", "home_page", "order", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("title", "short_description")
    ordering = ("order",)


@admin.register(HomeStatistic)
class HomeStatisticAdmin(TimeStampedAdmin):
    list_display = ("label", "value", "home_page", "order", "created_at")
    search_fields = ("label", "value")
    ordering = ("order",)


@admin.register(HomeGallery)
class HomeGalleryAdmin(TimeStampedAdmin):
    list_display = ("title", "home_page", "order", "created_at")
    search_fields = ("title", "caption")
    ordering = ("order",)


@admin.register(HomeVideo)
class HomeVideoAdmin(TimeStampedAdmin):
    list_display = ("title", "home_page", "order", "is_active", "created_at")
    list_filter = ("is_active", "home_page")
    search_fields = ("title", "description")
    ordering = ("order", "-created_at")


@admin.register(HomeNotice)
class HomeNoticeAdmin(TimeStampedAdmin):
    list_display = ("title", "button_text", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("title", "subtitle", "description", "button_text", "badge_label")
    ordering = ("-created_at",)


@admin.register(HomeEnquirySubmission)
class HomeEnquirySubmissionAdmin(TimeStampedAdmin):
    list_display = ("full_name", "email", "phone_number", "location", "is_contacted", "contacted_at", "contacted_by", "created_at")
    list_filter = ("is_contacted", "contacted_at", "created_at")
    search_fields = ("full_name", "email", "phone_number", "location", "description", "contact_notes")
    ordering = ("-created_at",)


@admin.register(HomeTestimonial)
class HomeTestimonialAdmin(TimeStampedAdmin):
    list_display = ("thumbnail_preview", "full_name", "role", "rating", "is_approved", "order", "created_at")
    list_filter = ("is_approved", "rating", "created_at")
    search_fields = ("full_name", "role", "message")
    readonly_fields = ("thumbnail_preview",)
    ordering = ("order", "-created_at")

    def thumbnail_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" alt="{}" style="width:40px;height:40px;object-fit:cover;border-radius:8px;" />', obj.image.url, obj.full_name or "Testimonial")
        return "—"

    thumbnail_preview.short_description = "Image"


# =========================================================
# COURSES
# =========================================================

class CourseDetailInline(admin.TabularInline):
    model = CourseDetail
    extra = 1


class CourseRequirementInline(admin.TabularInline):
    model = CourseRequirement
    extra = 1


class CourseOutcomeInline(admin.TabularInline):
    model = CourseOutcome
    extra = 1


class CourseGalleryInline(admin.TabularInline):
    model = CourseGallery
    extra = 1


class CourseFAQInline(admin.TabularInline):
    model = CourseFAQ
    extra = 1


@admin.register(CourseCategory)
class CourseCategoryAdmin(TimeStampedAdmin):
    list_display = ("name", "slug", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Course)
class CourseAdmin(TimeStampedAdmin):
    list_display = (
        "title",
        "category",
        "level",
        "department",
        "is_featured",
        "is_active",
        "order",
        "created_at",
    )
    list_filter = ("is_active", "is_featured", "category", "level", "department")
    search_fields = ("title", "short_description", "full_description", "course_code", "department")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("order", "title")
    inlines = [
        CourseDetailInline,
        CourseRequirementInline,
        CourseOutcomeInline,
        CourseGalleryInline,
        CourseFAQInline,
    ]


@admin.register(CourseDetail)
class CourseDetailAdmin(TimeStampedAdmin):
    list_display = ("heading", "course", "order", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("heading", "content")
    ordering = ("order",)


@admin.register(CourseRequirement)
class CourseRequirementAdmin(TimeStampedAdmin):
    list_display = ("course", "requirement", "order", "created_at")
    search_fields = ("requirement",)
    ordering = ("order",)


@admin.register(CourseOutcome)
class CourseOutcomeAdmin(TimeStampedAdmin):
    list_display = ("course", "outcome", "order", "created_at")
    search_fields = ("outcome",)
    ordering = ("order",)


@admin.register(CourseGallery)
class CourseGalleryAdmin(TimeStampedAdmin):
    list_display = ("title", "course", "order", "created_at")
    search_fields = ("title", "caption")
    ordering = ("order",)


@admin.register(CourseFAQ)
class CourseFAQAdmin(TimeStampedAdmin):
    list_display = ("question", "course", "order", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("question", "answer")
    ordering = ("order",)


# =========================================================
# ACADEMICS
# =========================================================

class AcademicSectionInline(admin.TabularInline):
    model = AcademicSection
    extra = 1


class AcademicGalleryInline(admin.TabularInline):
    model = AcademicGallery
    extra = 1


class AcademicFAQInline(admin.TabularInline):
    model = AcademicFAQ
    extra = 1


class AcademicMenuItemInline(admin.TabularInline):
    model = AcademicMenuItem
    extra = 1


@admin.register(AcademicPage)
class AcademicPageAdmin(TimeStampedAdmin):
    list_display = ("title", "is_active", "created_at", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("title", "subtitle", "description", "meta_title")
    inlines = [AcademicMenuItemInline]


@admin.register(AcademicMenuItem)
class AcademicMenuItemAdmin(TimeStampedAdmin):
    list_display = ("title", "page", "order", "is_active", "created_at")
    list_filter = ("is_active", "page")
    search_fields = ("title", "short_description")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("order", "title")
    inlines = [AcademicSectionInline, AcademicGalleryInline, AcademicFAQInline]


@admin.register(AcademicSection)
class AcademicSectionAdmin(TimeStampedAdmin):
    list_display = ("title", "menu_item", "order", "is_active", "created_at")
    list_filter = ("is_active", "menu_item")
    search_fields = ("title", "subtitle", "content")
    ordering = ("order", "title")


@admin.register(AcademicGallery)
class AcademicGalleryAdmin(TimeStampedAdmin):
    list_display = ("title", "menu_item", "order", "created_at")
    search_fields = ("title", "caption")
    ordering = ("order", "title")


@admin.register(AcademicFAQ)
class AcademicFAQAdmin(TimeStampedAdmin):
    list_display = ("question", "menu_item", "order", "is_active", "created_at")
    list_filter = ("is_active", "menu_item")
    search_fields = ("question", "answer")
    ordering = ("order", "question")


# =========================================================
# ADMISSION
# =========================================================

class AdmissionCategoryInline(admin.TabularInline):
    model = AdmissionCategory
    extra = 1


class AdmissionSectionInline(admin.TabularInline):
    model = AdmissionSection
    extra = 1


class AdmissionRequirementInline(admin.TabularInline):
    model = AdmissionRequirement
    extra = 1


class AdmissionFAQInline(admin.TabularInline):
    model = AdmissionFAQ
    extra = 1


class AdmissionGalleryInline(admin.TabularInline):
    model = AdmissionGallery
    extra = 1


@admin.register(AdmissionPage)
class AdmissionPageAdmin(TimeStampedAdmin):
    list_display = ("title", "is_active", "created_at", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("title", "subtitle", "description", "meta_title")
    inlines = [AdmissionCategoryInline]


@admin.register(AdmissionCategory)
class AdmissionCategoryAdmin(TimeStampedAdmin):
    list_display = ("title", "page", "form_type", "order", "is_active", "created_at")
    list_filter = ("is_active", "page", "form_type")
    search_fields = ("title", "short_description", "form_type")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("order", "title")
    inlines = [
        AdmissionSectionInline,
        AdmissionRequirementInline,
        AdmissionFAQInline,
        AdmissionGalleryInline,
    ]


@admin.register(AdmissionSection)
class AdmissionSectionAdmin(TimeStampedAdmin):
    list_display = ("title", "category", "deadline", "order", "is_active", "created_at")
    list_filter = ("is_active", "category")
    search_fields = ("title", "subtitle", "content", "deadline")
    ordering = ("order", "title")


@admin.register(AdmissionRequirement)
class AdmissionRequirementAdmin(TimeStampedAdmin):
    list_display = ("category", "requirement", "order", "is_active", "created_at")
    list_filter = ("is_active", "category")
    search_fields = ("requirement",)
    ordering = ("order",)


@admin.register(AdmissionFAQ)
class AdmissionFAQAdmin(TimeStampedAdmin):
    list_display = ("question", "category", "order", "is_active", "created_at")
    list_filter = ("is_active", "category")
    search_fields = ("question", "answer")
    ordering = ("order", "question")


@admin.register(AdmissionGallery)
class AdmissionGalleryAdmin(TimeStampedAdmin):
    list_display = ("title", "category", "order", "created_at")
    search_fields = ("title", "caption")
    ordering = ("order", "title")


# =========================================================
# CONTACT US
# =========================================================

class ContactInfoCardInline(admin.TabularInline):
    model = ContactInfoCard
    extra = 1


class ContactOfficeInline(admin.TabularInline):
    model = ContactOffice
    extra = 1


class SocialLinkInline(admin.TabularInline):
    model = SocialLink
    extra = 1


@admin.register(ContactPage)
class ContactPageAdmin(TimeStampedAdmin):
    list_display = ("title", "office_hours", "is_active", "created_at", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("title", "subtitle", "description", "office_hours", "meta_title")
    inlines = [ContactInfoCardInline, ContactOfficeInline, SocialLinkInline]


@admin.register(ContactInfoCard)
class ContactInfoCardAdmin(TimeStampedAdmin):
    list_display = ("title", "page", "order", "is_active", "created_at")
    list_filter = ("is_active", "page")
    search_fields = ("title", "value")
    ordering = ("order", "title")


@admin.register(ContactOffice)
class ContactOfficeAdmin(TimeStampedAdmin):
    list_display = ("name", "page", "phone", "email", "order", "is_active", "created_at")
    list_filter = ("is_active", "page")
    search_fields = ("name", "address", "phone", "email", "office_hours")
    ordering = ("order", "name")


@admin.register(SocialLink)
class SocialLinkAdmin(TimeStampedAdmin):
    list_display = ("name", "page", "url", "order", "is_active", "created_at")
    list_filter = ("is_active", "page")
    search_fields = ("name", "url")
    ordering = ("order", "name")


# =========================================================
# NEWS AND EVENTS
# =========================================================

class NewsEventCategoryInline(admin.TabularInline):
    model = NewsEventCategory
    extra = 1


class NewsEventGalleryInline(admin.TabularInline):
    model = NewsEventGallery
    extra = 1
    fk_name = "news_item"

class EventGalleryInline(admin.TabularInline):
    model = NewsEventGallery
    extra = 1
    fk_name = "event_item"


class EventFAQInline(admin.TabularInline):
    model = EventFAQ
    extra = 1


@admin.register(NewsEventPage)
class NewsEventPageAdmin(TimeStampedAdmin):
    list_display = ("title", "is_active", "created_at", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("title", "subtitle", "description", "meta_title")
    inlines = [NewsEventCategoryInline]


@admin.register(NewsEventCategory)
class NewsEventCategoryAdmin(TimeStampedAdmin):
    list_display = ("title", "page", "order", "is_active", "created_at")
    list_filter = ("is_active", "page")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("order", "title")


@admin.register(NewsItem)
class NewsItemAdmin(TimeStampedAdmin):
    list_display = ("title", "category", "publish_date", "author_name", "is_featured", "is_active", "created_at")
    list_filter = ("is_active", "is_featured", "category", "publish_date")
    search_fields = ("title", "short_description", "content", "author_name")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [NewsEventGalleryInline]


@admin.register(EventItem)
class EventItemAdmin(TimeStampedAdmin):
    list_display = ("title", "category", "event_date", "venue", "organizer", "is_featured", "is_active", "created_at")
    list_filter = ("is_active", "is_featured", "category", "event_date")
    search_fields = ("title", "short_description", "content", "venue", "organizer")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [EventGalleryInline, EventFAQInline]


@admin.register(EventFAQ)
class EventFAQAdmin(TimeStampedAdmin):
    list_display = ("question", "event_item", "order", "is_active", "created_at")
    list_filter = ("is_active", "event_item")
    search_fields = ("question", "answer")
    ordering = ("order", "question")


@admin.register(NewsEventGallery)
class NewsEventGalleryAdmin(TimeStampedAdmin):
    list_display = ("title", "news_item", "event_item", "order", "created_at")
    search_fields = ("title", "caption")
    ordering = ("order", "title")


# =========================================================
# ABOUT US
# =========================================================

class AboutMenuItemInline(admin.TabularInline):
    model = AboutMenuItem
    extra = 1


class AboutSectionInline(admin.TabularInline):
    model = AboutSection
    extra = 1


class LeadershipMemberInline(admin.TabularInline):
    model = LeadershipMember
    extra = 1


class AboutFAQInline(admin.TabularInline):
    model = AboutFAQ
    extra = 1


@admin.register(AboutPage)
class AboutPageAdmin(TimeStampedAdmin):
    list_display = ("title", "is_active", "created_at", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("title", "subtitle", "description", "mission", "vision", "meta_title")
    inlines = [AboutMenuItemInline, LeadershipMemberInline]


@admin.register(AboutMenuItem)
class AboutMenuItemAdmin(TimeStampedAdmin):
    list_display = ("title", "page", "order", "is_active", "created_at")
    list_filter = ("is_active", "page")
    search_fields = ("title", "short_description")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("order", "title")
    inlines = [AboutSectionInline, AboutFAQInline]


@admin.register(AboutSection)
class AboutSectionAdmin(TimeStampedAdmin):
    list_display = ("title", "menu_item", "order", "is_active", "created_at")
    list_filter = ("is_active", "menu_item")
    search_fields = ("title", "subtitle", "content")
    ordering = ("order", "title")


@admin.register(AboutFAQ)
class AboutFAQAdmin(TimeStampedAdmin):
    list_display = ("question", "menu_item", "order", "is_active", "created_at")
    list_filter = ("is_active", "menu_item")
    search_fields = ("question", "answer")
    ordering = ("order", "question")


@admin.register(LeadershipMember)
class LeadershipMemberAdmin(TimeStampedAdmin):
    list_display = ("full_name", "page", "role", "email", "phone", "order", "is_active", "created_at")
    list_filter = ("is_active", "page", "role")
    search_fields = ("full_name", "role", "bio", "email", "phone")
    ordering = ("order", "full_name")


# =========================================================
# STUDENT LIFE
# =========================================================

class StudentLifeMenuItemInline(admin.TabularInline):
    model = StudentLifeMenuItem
    extra = 1


class StudentLifeSectionInline(admin.TabularInline):
    model = StudentLifeSection
    extra = 1


class StudentLifeGalleryInline(admin.TabularInline):
    model = StudentLifeGallery
    extra = 1


class StudentLifeFAQInline(admin.TabularInline):
    model = StudentLifeFAQ
    extra = 1


@admin.register(StudentLifePage)
class StudentLifePageAdmin(TimeStampedAdmin):
    list_display = ("title", "is_active", "created_at", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("title", "subtitle", "description", "meta_title")
    inlines = [StudentLifeMenuItemInline]


@admin.register(StudentLifeMenuItem)
class StudentLifeMenuItemAdmin(TimeStampedAdmin):
    list_display = ("title", "page", "order", "is_active", "created_at")
    list_filter = ("is_active", "page")
    search_fields = ("title", "short_description")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("order", "title")
    inlines = [StudentLifeSectionInline, StudentLifeGalleryInline, StudentLifeFAQInline]


@admin.register(StudentLifeSection)
class StudentLifeSectionAdmin(TimeStampedAdmin):
    list_display = ("title", "menu_item", "order", "is_active", "created_at")
    list_filter = ("is_active", "menu_item")
    search_fields = ("title", "subtitle", "content")
    ordering = ("order", "title")


@admin.register(StudentLifeGallery)
class StudentLifeGalleryAdmin(TimeStampedAdmin):
    list_display = ("title", "menu_item", "order", "created_at")
    search_fields = ("title", "caption")
    ordering = ("order", "title")


@admin.register(StudentLifeFAQ)
class StudentLifeFAQAdmin(TimeStampedAdmin):
    list_display = ("question", "menu_item", "order", "is_active", "created_at")
    list_filter = ("is_active", "menu_item")
    search_fields = ("question", "answer")
    ordering = ("order", "question")
