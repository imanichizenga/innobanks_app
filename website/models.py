from django.db import models
from django.conf import settings
# Create your models here.
import re
class Host(models.Model):
    school_name = models.CharField(max_length=100,null=True,blank=True)
    host_name = models.CharField(max_length=30,null=True,blank=True)

    def __str__(self):
        return f'{self.host_name}'
    
    class Meta:
        verbose_name = "Register"
        verbose_name_plural = "Register Host"


class Contact(models.Model):
    host_required = models.ForeignKey(Host,on_delete=models.CASCADE)
    school_contact = models.CharField(max_length=100)
    def __str__(self):
        return self.school_contact

    class Meta:
        verbose_name = "School Contacts"
        verbose_name_plural = "School Contact"

class Top(models.Model):
    school_name = models.CharField(max_length=100,null=True,blank=True)
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    host_required = models.ForeignKey(Host,on_delete=models.CASCADE)
    question=models.CharField(max_length=30,null=True,blank=False)
    contact = models.CharField(max_length=30,null=True,blank=False)
    email=models.EmailField()
    icon_required = models.ImageField(upload_to='icon_shown/',help_text='Upload Brand Icon',null=True,blank=True)

    def __str__(self):
        return f'{self.question}'
    class Meta:
        verbose_name = "Top Section Content"
        verbose_name_plural = "Modify Top Sections"



class UserEmailSettings(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='email_settings')
    
    host_required = models.ForeignKey(Host,on_delete=models.CASCADE)
    email_backend = models.CharField(max_length=255, default='django.core.mail.backends.smtp.EmailBackend')
    email_host = models.CharField(max_length=255, default='smtp.gmail.com')
    email_port = models.IntegerField(default=587)
    email_use_tls = models.BooleanField(default=True)
    email_host_user = models.CharField(max_length=255, default='britishschooltz9@gmail.com')
    email_host_password = models.CharField(max_length=255, default='asck jcua lrxe yshb')
    default_from_email = models.CharField(max_length=255, default='britishschooltz9@gmail.com')

    def __str__(self):
        return f"Email settings for {self.user.username}-CUSTOMER"

    class Meta:
        verbose_name = "User Email Setting"
        verbose_name_plural = "User Email Settings"


from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        abstract = True


class HomePage(TimeStampedModel):
    # Hero / Banner
    hero_title = models.CharField(max_length=255, null=True, blank=True)
    hero_subtitle = models.TextField(null=True, blank=True)
    hero_description = models.TextField(null=True, blank=True)
    hero_image = models.ImageField(upload_to='homepage/hero/', null=True, blank=True)

    # CTA buttons
    hero_button_text = models.CharField(max_length=150, null=True, blank=True)
    hero_button_link = models.CharField(max_length=255, null=True, blank=True)

    hero_second_button_text = models.CharField(max_length=150, null=True, blank=True)
    hero_second_button_link = models.CharField(max_length=255, null=True, blank=True)

    # Welcome / Intro
    welcome_title = models.CharField(max_length=255, null=True, blank=True)
    welcome_description = models.TextField(null=True, blank=True)
    welcome_image = models.ImageField(upload_to='homepage/welcome/', null=True, blank=True)

    # Video / Tour section
    tour_title = models.CharField(max_length=255, null=True, blank=True)
    tour_description = models.TextField(null=True, blank=True)
    tour_thumbnail = models.ImageField(upload_to='homepage/tour/', null=True, blank=True)
    tour_video_url = models.URLField(null=True, blank=True)

    # Stats section
    stats_title = models.CharField(max_length=255, null=True, blank=True)

    # SEO/basic metadata
    meta_title = models.CharField(max_length=255, null=True, blank=True)
    meta_description = models.TextField(null=True, blank=True)

    is_active = models.BooleanField(default=True, null=True, blank=True)

    def __str__(self):
        return self.hero_title or "Home Page"


class HomeSlider(TimeStampedModel):
    home_page = models.ForeignKey(
        HomePage,
        on_delete=models.CASCADE,
        related_name='sliders',
        null=True,
        blank=True
    )
    title = models.CharField(max_length=255, null=True, blank=True)
    subtitle = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='homepage/sliders/', null=True, blank=True)
    button_text = models.CharField(max_length=150, null=True, blank=True)
    button_link = models.CharField(max_length=255, null=True, blank=True)
    order = models.PositiveIntegerField(default=0, null=True, blank=True)
    is_active = models.BooleanField(default=True, null=True, blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title or "Home Slider"


class HomeFeature(TimeStampedModel):
    home_page = models.ForeignKey(
        HomePage,
        on_delete=models.CASCADE,
        related_name='features',
        null=True,
        blank=True
    )
    title = models.CharField(max_length=255, null=True, blank=True)
    short_description = models.TextField(null=True, blank=True)
    icon_image = models.ImageField(upload_to='homepage/features/', null=True, blank=True)
    order = models.PositiveIntegerField(default=0, null=True, blank=True)
    is_active = models.BooleanField(default=True, null=True, blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title or "Home Feature"


class HomeStatistic(TimeStampedModel):
    home_page = models.ForeignKey(
        HomePage,
        on_delete=models.CASCADE,
        related_name='statistics',
        null=True,
        blank=True
    )
    label = models.CharField(max_length=255, null=True, blank=True)
    value = models.CharField(max_length=100, null=True, blank=True)
    icon_image = models.ImageField(upload_to='homepage/statistics/', null=True, blank=True)
    order = models.PositiveIntegerField(default=0, null=True, blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.label} - {self.value}"


class HomeGallery(TimeStampedModel):
    home_page = models.ForeignKey(
        HomePage,
        on_delete=models.CASCADE,
        related_name='gallery',
        null=True,
        blank=True
    )
    title = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to='homepage/gallery/', null=True, blank=True)
    caption = models.TextField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0, null=True, blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title or "Home Gallery"


class HomeVideo(TimeStampedModel):
    home_page = models.ForeignKey(
        HomePage,
        on_delete=models.CASCADE,
        related_name='videos',
        null=True,
        blank=True,
        help_text="Optional relation to the active home page record.",
    )
    title = models.CharField(max_length=255, null=True, blank=True, help_text="Video title shown on homepage.")
    description = models.TextField(null=True, blank=True, help_text="Short description for this video slide.")
    video = models.FileField(upload_to='homepage/videos/', null=True, blank=True, help_text="Upload homepage video file.")
    thumbnail = models.ImageField(
        upload_to='homepage/videos/thumbnails/',
        null=True,
        blank=True,
        help_text="Optional thumbnail before visitor plays video.",
    )
    order = models.PositiveIntegerField(default=0, null=True, blank=True, help_text="Controls display ordering.")
    is_active = models.BooleanField(default=True, null=True, blank=True, help_text="Show or hide this video.")

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title or "Home Video"


class HomeNotice(TimeStampedModel):
    title = models.CharField(max_length=255, null=True, blank=True)
    subtitle = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    button_text = models.CharField(max_length=120, null=True, blank=True)
    badge_label = models.CharField(max_length=100, null=True, blank=True)
    background_image = models.ImageField(upload_to='homepage/notice/', null=True, blank=True)
    is_active = models.BooleanField(default=True, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title or "Home Notice"


class HomeEnquirySubmission(TimeStampedModel):
    full_name = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    is_contacted = models.BooleanField(default=False)
    contacted_at = models.DateTimeField(null=True, blank=True)
    contacted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contacted_home_enquiries"
    )
    contact_notes = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.full_name or self.email or "Home Enquiry Submission"




class HomeTestimonial(TimeStampedModel):
    full_name = models.CharField(max_length=255, null=True, blank=True, help_text="Name of the person submitting the story.")
    message = models.TextField(null=True, blank=True, help_text="Story, comment, or testimonial message.")
    rating = models.PositiveIntegerField(null=True, blank=True, help_text="Rating value, for example 1 to 5.")
    role = models.CharField(max_length=100, null=True, blank=True, help_text="Role such as Student, Parent, Alumni, Guardian.")
    image = models.ImageField(upload_to='homepage/testimonials/', null=True, blank=True, help_text="Optional profile image.")
    is_approved = models.BooleanField(default=False, null=True, blank=True, help_text="Whether this testimonial is approved for public display.")
    order = models.PositiveIntegerField(default=0, null=True, blank=True, help_text="Display order for approved testimonials.")

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.full_name or "Home Testimonial"

class CourseCategory(TimeStampedModel):
    name = models.CharField(max_length=255, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='courses/categories/', null=True, blank=True)
    is_active = models.BooleanField(default=True, null=True, blank=True)

    def __str__(self):
        return self.name or "Course Category"


class Course(TimeStampedModel):
    category = models.ForeignKey(
        CourseCategory,
        on_delete=models.SET_NULL,
        related_name='courses',
        null=True,
        blank=True
    )

    title = models.CharField(max_length=255, null=True, blank=True)
    slug = models.SlugField(unique=True, null=True, blank=True)
    short_description = models.TextField(null=True, blank=True)
    full_description = models.TextField(null=True, blank=True)

    thumbnail = models.ImageField(upload_to='courses/thumbnails/', null=True, blank=True)
    banner_image = models.ImageField(upload_to='courses/banners/', null=True, blank=True)

    duration = models.CharField(max_length=100, null=True, blank=True)
    level = models.CharField(max_length=100, null=True, blank=True)
    department = models.CharField(max_length=255, null=True, blank=True)
    course_code = models.CharField(max_length=100, null=True, blank=True)

    application_link = models.CharField(max_length=255, null=True, blank=True)
    brochure_file = models.FileField(upload_to='courses/brochures/', null=True, blank=True)

    is_featured = models.BooleanField(default=False, null=True, blank=True)
    is_active = models.BooleanField(default=True, null=True, blank=True)
    order = models.PositiveIntegerField(default=0, null=True, blank=True)

    meta_title = models.CharField(max_length=255, null=True, blank=True)
    meta_description = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['order', 'title']

    def __str__(self):
        return self.title or "Course"


class CourseDetail(TimeStampedModel):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='details',
        null=True,
        blank=True
    )
    heading = models.CharField(max_length=255, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='courses/details/', null=True, blank=True)
    order = models.PositiveIntegerField(default=0, null=True, blank=True)
    is_active = models.BooleanField(default=True, null=True, blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.heading or "Course Detail"


class CourseRequirement(TimeStampedModel):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='requirements',
        null=True,
        blank=True
    )
    requirement = models.TextField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0, null=True, blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.requirement[:50] if self.requirement else "Requirement"


class CourseOutcome(TimeStampedModel):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='outcomes',
        null=True,
        blank=True
    )
    outcome = models.TextField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0, null=True, blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.outcome[:50] if self.outcome else "Outcome"


class CourseGallery(TimeStampedModel):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='gallery',
        null=True,
        blank=True
    )
    title = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to='courses/gallery/', null=True, blank=True)
    caption = models.TextField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0, null=True, blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title or "Course Gallery"


class CourseFAQ(TimeStampedModel):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='faqs',
        null=True,
        blank=True
    )
    question = models.CharField(max_length=255, null=True, blank=True)
    answer = models.TextField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0, null=True, blank=True)
    is_active = models.BooleanField(default=True, null=True, blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.question or "Course FAQ"



# =========================
# ACADEMICS
# =========================

class AcademicPage(TimeStampedModel):
    title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Main title for the academics page."
    )
    subtitle = models.TextField(
        null=True,
        blank=True,
        help_text="Short subtitle or summary shown below the academics title."
    )
    description = models.TextField(
        null=True,
        blank=True,
        help_text="Main introduction content for the academics page."
    )
    hero_image = models.ImageField(
        upload_to='academics/hero/',
        null=True,
        blank=True,
        help_text="Main banner image for the academics page."
    )
    banner_title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Optional title displayed on the hero/banner section."
    )
    banner_description = models.TextField(
        null=True,
        blank=True,
        help_text="Optional text displayed in the hero/banner section."
    )
    meta_title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="SEO title for the academics page."
    )
    meta_description = models.TextField(
        null=True,
        blank=True,
        help_text="SEO description for the academics page."
    )
    is_active = models.BooleanField(
        default=True,
        null=True,
        blank=True,
        help_text="Controls whether this academics page is active."
    )

    def __str__(self):
        return self.title or "Academics Page"


class AcademicMenuItem(TimeStampedModel):
    page = models.ForeignKey(
        AcademicPage,
        on_delete=models.CASCADE,
        related_name='menu_items',
        null=True,
        blank=True,
        help_text="Academics page this menu item belongs to."
    )
    title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Menu title, for example Results, Course, or Course Details."
    )
    slug = models.SlugField(
        unique=True,
        null=True,
        blank=True,
        help_text="Unique slug for this academics menu item."
    )
    short_description = models.TextField(
        null=True,
        blank=True,
        help_text="Short explanation for this academics menu item."
    )
    image = models.ImageField(
        upload_to='academics/menu_items/',
        null=True,
        blank=True,
        help_text="Image representing this academics menu item."
    )
    order = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True,
        help_text="Display order of the academics dropdown item."
    )
    is_active = models.BooleanField(
        default=True,
        null=True,
        blank=True,
        help_text="Controls whether this menu item is visible."
    )

    class Meta:
        ordering = ['order', 'title']

    def __str__(self):
        return self.title or "Academic Menu Item"


class AcademicSection(TimeStampedModel):
    menu_item = models.ForeignKey(
        AcademicMenuItem,
        on_delete=models.CASCADE,
        related_name='sections',
        null=True,
        blank=True,
        help_text="Academics menu item this section belongs to."
    )
    title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Section title under the academics menu item."
    )
    subtitle = models.TextField(
        null=True,
        blank=True,
        help_text="Optional subtitle for this section."
    )
    content = models.TextField(
        null=True,
        blank=True,
        help_text="Main body content for this section."
    )
    image = models.ImageField(
        upload_to='academics/sections/',
        null=True,
        blank=True,
        help_text="Image for this academics section."
    )
    file = models.FileField(
        upload_to='academics/files/',
        null=True,
        blank=True,
        help_text="Optional downloadable file for this section."
    )
    button_text = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        help_text="Optional button text for this section."
    )
    button_link = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Optional button or redirect link for this section."
    )
    order = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True,
        help_text="Display order of sections under the menu item."
    )
    is_active = models.BooleanField(
        default=True,
        null=True,
        blank=True,
        help_text="Controls whether this section is visible."
    )

    class Meta:
        ordering = ['order', 'title']

    def __str__(self):
        return self.title or "Academic Section"


class AcademicGallery(TimeStampedModel):
    menu_item = models.ForeignKey(
        AcademicMenuItem,
        on_delete=models.CASCADE,
        related_name='gallery',
        null=True,
        blank=True,
        help_text="Academics menu item this gallery image belongs to."
    )
    title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Title of the gallery image."
    )
    image = models.ImageField(
        upload_to='academics/gallery/',
        null=True,
        blank=True,
        help_text="Gallery image for academics content."
    )
    caption = models.TextField(
        null=True,
        blank=True,
        help_text="Short caption for the gallery image."
    )
    order = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True,
        help_text="Display order of gallery items."
    )

    class Meta:
        ordering = ['order', 'title']

    def __str__(self):
        return self.title or "Academic Gallery"


class AcademicFAQ(TimeStampedModel):
    menu_item = models.ForeignKey(
        AcademicMenuItem,
        on_delete=models.CASCADE,
        related_name='faqs',
        null=True,
        blank=True,
        help_text="Academics menu item this FAQ belongs to."
    )
    question = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Question shown in the academics FAQ section."
    )
    answer = models.TextField(
        null=True,
        blank=True,
        help_text="Answer for the academics FAQ question."
    )
    order = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True,
        help_text="Display order of FAQ items."
    )
    is_active = models.BooleanField(
        default=True,
        null=True,
        blank=True,
        help_text="Controls whether this FAQ is visible."
    )

    class Meta:
        ordering = ['order', 'question']

    def __str__(self):
        return self.question or "Academic FAQ"


# =========================
# ADMISSION
# =========================

class AdmissionPage(TimeStampedModel):
    title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Main title for the admission page."
    )
    subtitle = models.TextField(
        null=True,
        blank=True,
        help_text="Short subtitle or summary shown below the admission title."
    )
    description = models.TextField(
        null=True,
        blank=True,
        help_text="Main introduction content for the admission page."
    )
    hero_image = models.ImageField(
        upload_to='admission/hero/',
        null=True,
        blank=True,
        help_text="Main banner image for the admission page."
    )
    banner_title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Optional title displayed in the admission hero section."
    )
    banner_description = models.TextField(
        null=True,
        blank=True,
        help_text="Optional text displayed in the admission hero section."
    )
    application_notice = models.TextField(
        null=True,
        blank=True,
        help_text="General notice shown to applicants on the admission page."
    )
    meta_title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="SEO title for the admission page."
    )
    meta_description = models.TextField(
        null=True,
        blank=True,
        help_text="SEO description for the admission page."
    )
    is_active = models.BooleanField(
        default=True,
        null=True,
        blank=True,
        help_text="Controls whether this admission page is active."
    )

    def __str__(self):
        return self.title or "Admission Page"


class AdmissionCategory(TimeStampedModel):
    page = models.ForeignKey(
        AdmissionPage,
        on_delete=models.CASCADE,
        related_name='categories',
        null=True,
        blank=True,
        help_text="Admission page this category belongs to."
    )
    title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Admission category title, for example FTNA, CSEE, Form 1, Form 2, Form 3, Form 5, or Form 6."
    )
    slug = models.SlugField(
        unique=True,
        null=True,
        blank=True,
        help_text="Unique slug for this admission category."
    )
    short_description = models.TextField(
        null=True,
        blank=True,
        help_text="Short explanation for this admission category."
    )
    image = models.ImageField(
        upload_to='admission/categories/',
        null=True,
        blank=True,
        help_text="Representative image for this admission category."
    )
    form_type = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Optional type or class name, such as Form 1 or FTNA."
    )
    order = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True,
        help_text="Display order of this category in the admission dropdown."
    )
    is_active = models.BooleanField(
        default=True,
        null=True,
        blank=True,
        help_text="Controls whether this admission category is visible."
    )

    class Meta:
        ordering = ['order', 'title']

    def __str__(self):
        return self.title or "Admission Category"


class AdmissionSection(TimeStampedModel):
    category = models.ForeignKey(
        AdmissionCategory,
        on_delete=models.CASCADE,
        related_name='sections',
        null=True,
        blank=True,
        help_text="Admission category this section belongs to."
    )
    title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Title of the admission section."
    )
    subtitle = models.TextField(
        null=True,
        blank=True,
        help_text="Optional subtitle for this admission section."
    )
    content = models.TextField(
        null=True,
        blank=True,
        help_text="Main description or instructions for this admission section."
    )
    image = models.ImageField(
        upload_to='admission/sections/',
        null=True,
        blank=True,
        help_text="Image for this admission section."
    )
    file = models.FileField(
        upload_to='admission/files/',
        null=True,
        blank=True,
        help_text="Optional downloadable file such as a form, PDF, or guide."
    )
    external_link = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Optional link to external application or information page."
    )
    button_text = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        help_text="Optional button text for this section."
    )
    deadline = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        help_text="Optional admission deadline text."
    )
    order = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True,
        help_text="Display order of sections under this admission category."
    )
    is_active = models.BooleanField(
        default=True,
        null=True,
        blank=True,
        help_text="Controls whether this section is visible."
    )

    class Meta:
        ordering = ['order', 'title']

    def __str__(self):
        return self.title or "Admission Section"


class AdmissionRequirement(TimeStampedModel):
    category = models.ForeignKey(
        AdmissionCategory,
        on_delete=models.CASCADE,
        related_name='requirements',
        null=True,
        blank=True,
        help_text="Admission category this requirement belongs to."
    )
    requirement = models.TextField(
        null=True,
        blank=True,
        help_text="Single admission requirement item."
    )
    order = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True,
        help_text="Display order of the requirement."
    )
    is_active = models.BooleanField(
        default=True,
        null=True,
        blank=True,
        help_text="Controls whether this requirement is visible."
    )

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.requirement[:60] if self.requirement else "Admission Requirement"


class AdmissionFAQ(TimeStampedModel):
    category = models.ForeignKey(
        AdmissionCategory,
        on_delete=models.CASCADE,
        related_name='faqs',
        null=True,
        blank=True,
        help_text="Admission category this FAQ belongs to."
    )
    question = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Question shown in the admission FAQ section."
    )
    answer = models.TextField(
        null=True,
        blank=True,
        help_text="Answer for the admission FAQ question."
    )
    order = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True,
        help_text="Display order of FAQ items."
    )
    is_active = models.BooleanField(
        default=True,
        null=True,
        blank=True,
        help_text="Controls whether this FAQ is visible."
    )

    class Meta:
        ordering = ['order', 'question']

    def __str__(self):
        return self.question or "Admission FAQ"


class AdmissionGallery(TimeStampedModel):
    category = models.ForeignKey(
        AdmissionCategory,
        on_delete=models.CASCADE,
        related_name='gallery',
        null=True,
        blank=True,
        help_text="Admission category this gallery image belongs to."
    )
    title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Title of the gallery image."
    )
    image = models.ImageField(
        upload_to='admission/gallery/',
        null=True,
        blank=True,
        help_text="Gallery image for admission content."
    )
    caption = models.TextField(
        null=True,
        blank=True,
        help_text="Short caption for the gallery image."
    )
    order = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True,
        help_text="Display order of gallery items."
    )

    class Meta:
        ordering = ['order', 'title']

    def __str__(self):
        return self.title or "Admission Gallery"





# =====================================================
# CONTACT US
# =====================================================

class ContactPage(TimeStampedModel):
    title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Main title for the contact us page."
    )
    subtitle = models.TextField(
        null=True,
        blank=True,
        help_text="Short subtitle shown below the contact page title."
    )
    description = models.TextField(
        null=True,
        blank=True,
        help_text="Introductory text for the contact us page."
    )
    hero_image = models.ImageField(
        upload_to='contact/hero/',
        null=True,
        blank=True,
        help_text="Banner or hero image for the contact us page."
    )
    banner_title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Optional title shown in the contact page hero section."
    )
    banner_description = models.TextField(
        null=True,
        blank=True,
        help_text="Optional description shown in the contact page hero section."
    )
    office_hours = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="General office working hours text."
    )
    map_embed_link = models.TextField(
        null=True,
        blank=True,
        help_text="Google Maps embed link or iframe source for the main location."
    )
    meta_title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="SEO title for the contact us page."
    )
    meta_description = models.TextField(
        null=True,
        blank=True,
        help_text="SEO description for the contact us page."
    )
    is_active = models.BooleanField(
        default=True,
        null=True,
        blank=True,
        help_text="Controls whether this contact page is active."
    )

    def __str__(self):
        return self.title or "Contact Page"


class ContactInfoCard(TimeStampedModel):
    page = models.ForeignKey(
        ContactPage,
        on_delete=models.CASCADE,
        related_name='info_cards',
        null=True,
        blank=True,
        help_text="Contact page this info card belongs to."
    )
    title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Title of the contact card, for example Phone, Email, Address."
    )
    value = models.TextField(
        null=True,
        blank=True,
        help_text="Main value shown in the contact card."
    )
    icon_image = models.ImageField(
        upload_to='contact/cards/',
        null=True,
        blank=True,
        help_text="Optional icon or image for this contact card."
    )
    order = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True,
        help_text="Display order of the contact info card."
    )
    is_active = models.BooleanField(
        default=True,
        null=True,
        blank=True,
        help_text="Controls whether this contact info card is visible."
    )

    class Meta:
        ordering = ['order', 'title']

    def __str__(self):
        return self.title or "Contact Info Card"


class ContactOffice(TimeStampedModel):
    page = models.ForeignKey(
        ContactPage,
        on_delete=models.CASCADE,
        related_name='offices',
        null=True,
        blank=True,
        help_text="Contact page this office belongs to."
    )
    name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Office or branch name."
    )
    address = models.TextField(
        null=True,
        blank=True,
        help_text="Physical address of the office or branch."
    )
    phone = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Phone number for the office."
    )
    email = models.EmailField(
        null=True,
        blank=True,
        help_text="Email address for the office."
    )
    office_hours = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Working hours for this office."
    )
    map_embed_link = models.TextField(
        null=True,
        blank=True,
        help_text="Map embed link for this office location."
    )
    image = models.ImageField(
        upload_to='contact/offices/',
        null=True,
        blank=True,
        help_text="Image representing this office or branch."
    )
    order = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True,
        help_text="Display order of office records."
    )
    is_active = models.BooleanField(
        default=True,
        null=True,
        blank=True,
        help_text="Controls whether this office is visible."
    )

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name or "Contact Office"


class SocialLink(TimeStampedModel):
    page = models.ForeignKey(
        ContactPage,
        on_delete=models.CASCADE,
        related_name='social_links',
        null=True,
        blank=True,
        help_text="Contact page this social link belongs to."
    )
    name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Name of the social platform, for example Facebook, Instagram, X, YouTube."
    )
    url = models.URLField(
        null=True,
        blank=True,
        help_text="URL to the social media page."
    )
    icon_image = models.ImageField(
        upload_to='contact/socials/',
        null=True,
        blank=True,
        help_text="Optional icon image for the social media link."
    )
    order = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True,
        help_text="Display order of social links."
    )
    is_active = models.BooleanField(
        default=True,
        null=True,
        blank=True,
        help_text="Controls whether this social link is visible."
    )

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name or "Social Link"


# =====================================================
# NEWS AND EVENTS
# =====================================================

class NewsEventPage(TimeStampedModel):
    title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Main title for the news and events page."
    )
    subtitle = models.TextField(
        null=True,
        blank=True,
        help_text="Short subtitle shown below the page title."
    )
    description = models.TextField(
        null=True,
        blank=True,
        help_text="Introductory text for the news and events page."
    )
    hero_image = models.ImageField(
        upload_to='news_events/hero/',
        null=True,
        blank=True,
        help_text="Banner or hero image for the news and events page."
    )
    meta_title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="SEO title for the news and events page."
    )
    meta_description = models.TextField(
        null=True,
        blank=True,
        help_text="SEO description for the news and events page."
    )
    is_active = models.BooleanField(
        default=True,
        null=True,
        blank=True,
        help_text="Controls whether this page is active."
    )

    def __str__(self):
        return self.title or "News and Events Page"


class NewsEventCategory(TimeStampedModel):
    page = models.ForeignKey(
        NewsEventPage,
        on_delete=models.CASCADE,
        related_name='categories',
        null=True,
        blank=True,
        help_text="News and events page this category belongs to."
    )
    title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Category title, for example Student Events, Staff Events, Students and Staff Events, News."
    )
    slug = models.SlugField(
        unique=True,
        null=True,
        blank=True,
        help_text="Unique slug for this category."
    )
    description = models.TextField(
        null=True,
        blank=True,
        help_text="Short description of this category."
    )
    image = models.ImageField(
        upload_to='news_events/categories/',
        null=True,
        blank=True,
        help_text="Representative image for this category."
    )
    order = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True,
        help_text="Display order of this category."
    )
    is_active = models.BooleanField(
        default=True,
        null=True,
        blank=True,
        help_text="Controls whether this category is visible."
    )

    class Meta:
        ordering = ['order', 'title']

    def __str__(self):
        return self.title or "News/Event Category"


class NewsItem(TimeStampedModel):
    category = models.ForeignKey(
        NewsEventCategory,
        on_delete=models.SET_NULL,
        related_name='news_items',
        null=True,
        blank=True,
        help_text="Category this news item belongs to."
    )
    title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Title of the news item."
    )
    slug = models.SlugField(
        unique=True,
        null=True,
        blank=True,
        help_text="Unique slug for the news details page."
    )
    short_description = models.TextField(
        null=True,
        blank=True,
        help_text="Short summary shown in news cards or listing pages."
    )
    content = models.TextField(
        null=True,
        blank=True,
        help_text="Full content of the news item."
    )
    featured_image = models.ImageField(
        upload_to='news_events/news/',
        null=True,
        blank=True,
        help_text="Main image for the news item."
    )
    publish_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date the news item was published."
    )
    author_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Name of the author or publisher."
    )
    is_featured = models.BooleanField(
        default=False,
        null=True,
        blank=True,
        help_text="Controls whether this news item is featured."
    )
    is_active = models.BooleanField(
        default=True,
        null=True,
        blank=True,
        help_text="Controls whether this news item is visible."
    )

    class Meta:
        ordering = ['-publish_date', '-created_at']

    def __str__(self):
        return self.title or "News Item"


class EventItem(TimeStampedModel):
    category = models.ForeignKey(
        NewsEventCategory,
        on_delete=models.SET_NULL,
        related_name='event_items',
        null=True,
        blank=True,
        help_text="Category this event belongs to."
    )
    title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Title of the event."
    )
    slug = models.SlugField(
        unique=True,
        null=True,
        blank=True,
        help_text="Unique slug for the event details page."
    )
    short_description = models.TextField(
        null=True,
        blank=True,
        help_text="Short summary shown in event cards or listing pages."
    )
    content = models.TextField(
        null=True,
        blank=True,
        help_text="Full content or details of the event."
    )
    featured_image = models.ImageField(
        upload_to='news_events/events/',
        null=True,
        blank=True,
        help_text="Main image for the event."
    )
    event_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date of the event."
    )
    start_time = models.TimeField(
        null=True,
        blank=True,
        help_text="Event start time."
    )
    end_time = models.TimeField(
        null=True,
        blank=True,
        help_text="Event end time."
    )
    venue = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Venue or location of the event."
    )
    organizer = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Name of the event organizer."
    )
    registration_link = models.URLField(
        null=True,
        blank=True,
        help_text="Optional registration or RSVP link for the event."
    )
    is_featured = models.BooleanField(
        default=False,
        null=True,
        blank=True,
        help_text="Controls whether this event is featured."
    )
    is_active = models.BooleanField(
        default=True,
        null=True,
        blank=True,
        help_text="Controls whether this event is visible."
    )

    class Meta:
        ordering = ['-event_date', '-created_at']

    def __str__(self):
        return self.title or "Event Item"


class EventFAQ(TimeStampedModel):
    event_item = models.ForeignKey(
        EventItem,
        on_delete=models.CASCADE,
        related_name='faqs',
        null=True,
        blank=True,
        help_text="Event item this FAQ belongs to."
    )
    question = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Question shown in the event FAQ section."
    )
    answer = models.TextField(
        null=True,
        blank=True,
        help_text="Answer for the event FAQ question."
    )
    order = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True,
        help_text="Display order of event FAQ items."
    )
    is_active = models.BooleanField(
        default=True,
        null=True,
        blank=True,
        help_text="Controls whether this event FAQ is visible."
    )

    class Meta:
        ordering = ['order', 'question']

    def __str__(self):
        return self.question or "Event FAQ"


class NewsEventGallery(TimeStampedModel):
    news_item = models.ForeignKey(
        NewsItem,
        on_delete=models.CASCADE,
        related_name='gallery',
        null=True,
        blank=True,
        help_text="News item this gallery image belongs to."
    )
    event_item = models.ForeignKey(
        EventItem,
        on_delete=models.CASCADE,
        related_name='gallery',
        null=True,
        blank=True,
        help_text="Event item this gallery image belongs to."
    )
    title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Title of the gallery image."
    )
    image = models.ImageField(
        upload_to='news_events/gallery/',
        null=True,
        blank=True,
        help_text="Gallery image for the news item or event."
    )
    caption = models.TextField(
        null=True,
        blank=True,
        help_text="Short caption for the gallery image."
    )
    order = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True,
        help_text="Display order of gallery images."
    )

    class Meta:
        ordering = ['order', 'title']

    def __str__(self):
        return self.title or "News/Event Gallery"


# =====================================================
# ABOUT US
# =====================================================

class AboutPage(TimeStampedModel):
    title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Main title for the about us page."
    )
    subtitle = models.TextField(
        null=True,
        blank=True,
        help_text="Short subtitle shown below the about us title."
    )
    description = models.TextField(
        null=True,
        blank=True,
        help_text="Main introduction content for the about us page."
    )
    hero_image = models.ImageField(
        upload_to='about/hero/',
        null=True,
        blank=True,
        help_text="Banner or hero image for the about us page."
    )
    mission = models.TextField(
        null=True,
        blank=True,
        help_text="School or institution mission statement."
    )
    vision = models.TextField(
        null=True,
        blank=True,
        help_text="School or institution vision statement."
    )
    core_values = models.TextField(
        null=True,
        blank=True,
        help_text="Core values text for the institution."
    )
    meta_title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="SEO title for the about us page."
    )
    meta_description = models.TextField(
        null=True,
        blank=True,
        help_text="SEO description for the about us page."
    )
    is_active = models.BooleanField(
        default=True,
        null=True,
        blank=True,
        help_text="Controls whether this page is active."
    )

    def __str__(self):
        return self.title or "About Page"


class AboutMenuItem(TimeStampedModel):
    page = models.ForeignKey(
        AboutPage,
        on_delete=models.CASCADE,
        related_name='menu_items',
        null=True,
        blank=True,
        help_text="About us page this menu item belongs to."
    )
    title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Dropdown item title, for example Community or Parents and Teacher Association."
    )
    slug = models.SlugField(
        unique=True,
        null=True,
        blank=True,
        help_text="Unique slug for the about us dropdown item."
    )
    short_description = models.TextField(
        null=True,
        blank=True,
        help_text="Short summary for this about us menu item."
    )
    image = models.ImageField(
        upload_to='about/menu_items/',
        null=True,
        blank=True,
        help_text="Image representing this about us menu item."
    )
    order = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True,
        help_text="Display order of the about us dropdown item."
    )
    is_active = models.BooleanField(
        default=True,
        null=True,
        blank=True,
        help_text="Controls whether this menu item is visible."
    )

    class Meta:
        ordering = ['order', 'title']

    def __str__(self):
        return self.title or "About Menu Item"


class AboutSection(TimeStampedModel):
    menu_item = models.ForeignKey(
        AboutMenuItem,
        on_delete=models.CASCADE,
        related_name='sections',
        null=True,
        blank=True,
        help_text="About us menu item this section belongs to."
    )
    title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Title of the section."
    )
    subtitle = models.TextField(
        null=True,
        blank=True,
        help_text="Optional subtitle for the section."
    )
    content = models.TextField(
        null=True,
        blank=True,
        help_text="Main body content for this section."
    )
    image = models.ImageField(
        upload_to='about/sections/',
        null=True,
        blank=True,
        help_text="Image for this about us section."
    )
    file = models.FileField(
        upload_to='about/files/',
        null=True,
        blank=True,
        help_text="Optional downloadable file for this section."
    )
    order = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True,
        help_text="Display order of sections."
    )
    is_active = models.BooleanField(
        default=True,
        null=True,
        blank=True,
        help_text="Controls whether this section is visible."
    )

    class Meta:
        ordering = ['order', 'title']

    def __str__(self):
        return self.title or "About Section"



class AboutFAQ(TimeStampedModel):
    menu_item = models.ForeignKey(
        AboutMenuItem,
        on_delete=models.CASCADE,
        related_name='faqs',
        null=True,
        blank=True,
        help_text="About us menu item this FAQ belongs to."
    )
    question = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Question shown in the about us FAQ section."
    )
    answer = models.TextField(
        null=True,
        blank=True,
        help_text="Answer for the about us FAQ question."
    )
    order = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True,
        help_text="Display order of FAQ items."
    )
    is_active = models.BooleanField(
        default=True,
        null=True,
        blank=True,
        help_text="Controls whether this FAQ is visible."
    )

    class Meta:
        ordering = ['order', 'question']

    def __str__(self):
        return self.question or "About FAQ"


class LeadershipMember(TimeStampedModel):
    page = models.ForeignKey(
        AboutPage,
        on_delete=models.CASCADE,
        related_name='leadership_members',
        null=True,
        blank=True,
        help_text="About us page this leadership member belongs to."
    )
    full_name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Full name of the leader or staff member."
    )
    role = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Position or role, for example Principal, Director, Head Teacher."
    )
    bio = models.TextField(
        null=True,
        blank=True,
        help_text="Short biography or profile description."
    )
    image = models.ImageField(
        upload_to='about/leadership/',
        null=True,
        blank=True,
        help_text="Profile image of the leader or staff member."
    )
    email = models.EmailField(
        null=True,
        blank=True,
        help_text="Optional email address of the member."
    )
    phone = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Optional phone number of the member."
    )
    order = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True,
        help_text="Display order of leadership members."
    )
    is_active = models.BooleanField(
        default=True,
        null=True,
        blank=True,
        help_text="Controls whether this leadership member is visible."
    )

    class Meta:
        ordering = ['order', 'full_name']

    def __str__(self):
        return self.full_name or "Leadership Member"


# =====================================================
# STUDENT LIFE
# =====================================================

class StudentLifePage(TimeStampedModel):
    title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Main title for the student life page."
    )
    subtitle = models.TextField(
        null=True,
        blank=True,
        help_text="Short subtitle shown below the student life title."
    )
    description = models.TextField(
        null=True,
        blank=True,
        help_text="Introductory text for the student life page."
    )
    hero_image = models.ImageField(
        upload_to='student_life/hero/',
        null=True,
        blank=True,
        help_text="Banner or hero image for the student life page."
    )
    meta_title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="SEO title for the student life page."
    )
    meta_description = models.TextField(
        null=True,
        blank=True,
        help_text="SEO description for the student life page."
    )
    is_active = models.BooleanField(
        default=True,
        null=True,
        blank=True,
        help_text="Controls whether this page is active."
    )

    def __str__(self):
        return self.title or "Student Life Page"


class StudentLifeMenuItem(TimeStampedModel):
    page = models.ForeignKey(
        StudentLifePage,
        on_delete=models.CASCADE,
        related_name='menu_items',
        null=True,
        blank=True,
        help_text="Student life page this menu item belongs to."
    )
    title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Dropdown item title, for example Studies or Learning Environment."
    )
    slug = models.SlugField(
        unique=True,
        null=True,
        blank=True,
        help_text="Unique slug for this student life menu item."
    )
    short_description = models.TextField(
        null=True,
        blank=True,
        help_text="Short summary for this student life menu item."
    )
    image = models.ImageField(
        upload_to='student_life/menu_items/',
        null=True,
        blank=True,
        help_text="Image representing this student life menu item."
    )
    order = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True,
        help_text="Display order of the student life dropdown item."
    )
    is_active = models.BooleanField(
        default=True,
        null=True,
        blank=True,
        help_text="Controls whether this menu item is visible."
    )

    class Meta:
        ordering = ['order', 'title']

    def __str__(self):
        return self.title or "Student Life Menu Item"


class StudentLifeSection(TimeStampedModel):
    menu_item = models.ForeignKey(
        StudentLifeMenuItem,
        on_delete=models.CASCADE,
        related_name='sections',
        null=True,
        blank=True,
        help_text="Student life menu item this section belongs to."
    )
    title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Title of this student life section."
    )
    subtitle = models.TextField(
        null=True,
        blank=True,
        help_text="Optional subtitle for the section."
    )
    content = models.TextField(
        null=True,
        blank=True,
        help_text="Main body content for the section."
    )
    image = models.ImageField(
        upload_to='student_life/sections/',
        null=True,
        blank=True,
        help_text="Image for this student life section."
    )
    file = models.FileField(
        upload_to='student_life/files/',
        null=True,
        blank=True,
        help_text="Optional downloadable file for this section."
    )
    button_text = models.CharField(
        max_length=150,
        null=True,
        blank=True,
        help_text="Optional button text shown in this section."
    )
    button_link = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Optional button link for this section."
    )
    order = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True,
        help_text="Display order of this section."
    )
    is_active = models.BooleanField(
        default=True,
        null=True,
        blank=True,
        help_text="Controls whether this section is visible."
    )

    class Meta:
        ordering = ['order', 'title']

    def __str__(self):
        return self.title or "Student Life Section"


class StudentLifeGallery(TimeStampedModel):
    menu_item = models.ForeignKey(
        StudentLifeMenuItem,
        on_delete=models.CASCADE,
        related_name='gallery',
        null=True,
        blank=True,
        help_text="Student life menu item this gallery image belongs to."
    )
    title = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Title of the gallery image."
    )
    image = models.ImageField(
        upload_to='student_life/gallery/',
        null=True,
        blank=True,
        help_text="Gallery image for this student life content."
    )
    caption = models.TextField(
        null=True,
        blank=True,
        help_text="Short caption for the gallery image."
    )
    order = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True,
        help_text="Display order of gallery items."
    )

    class Meta:
        ordering = ['order', 'title']

    def __str__(self):
        return self.title or "Student Life Gallery"


class StudentLifeFAQ(TimeStampedModel):
    menu_item = models.ForeignKey(
        StudentLifeMenuItem,
        on_delete=models.CASCADE,
        related_name='faqs',
        null=True,
        blank=True,
        help_text="Student life menu item this FAQ belongs to."
    )
    question = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Question shown in the student life FAQ section."
    )
    answer = models.TextField(
        null=True,
        blank=True,
        help_text="Answer for the question."
    )
    order = models.PositiveIntegerField(
        default=0,
        null=True,
        blank=True,
        help_text="Display order of FAQ items."
    )
    is_active = models.BooleanField(
        default=True,
        null=True,
        blank=True,
        help_text="Controls whether this FAQ is visible."
    )

    class Meta:
        ordering = ['order', 'question']

    def __str__(self):
        return self.question or "Student Life FAQ"
