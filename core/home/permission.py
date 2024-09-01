from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group
from .models import *

def create_permissions_and_groups():
    user_type = ContentType.objects.get_for_model(User)
    clerk_type=ContentType.objects.get_for_model(Clerk)
    colonel_type=ContentType.objects.get_for_model(Colonel)
    brigadier_type=ContentType.objects.get_for_model(Brigadier)
    director_general_type=ContentType.objects.get_for_model(Director_General)

    student_type = ContentType.objects.get_for_model(Student)
    can_edit_student_details = Permission.objects.get_or_create(
        codename="can_edit_student_details",
        name="Can Edit Student Details",
        content_type=student_type
    )

    can_approve_admit_card = Permission.objects.get_or_create(
        codename="can_approve_admit_card",
        name="Can approve Admit Card",
        content_type=student_type
    )

    can_reject_admit_card = Permission.objects.get_or_create(
        codename="can_reject_admit_card",
        name="Can Reject Admit Card",
        content_type=student_type
    )

    can_view_rejected_applications = Permission.objects.get_or_create(
        codename="can_view_rejected_applications",
        name="Can View Rejected Applications",
        content_type=student_type
    )
        
    can_create_new_candidates = Permission.objects.get_or_create(
        codename="can_create_new_candidates",
        name="Can Create New Candidates",
        content_type=student_type
    )

    can_create_new_users = Permission.objects.get_or_create(
        codename="can_create_new_users",
        name="Can Create New Users",
        content_type=student_type
    )

    can_send_admit_card_for_approval = Permission.objects.get_or_create(
        codename="can_send_admit_card_for_approval",
        name="Can Send Admit Card For Approval",
        content_type=student_type
    )

    can_preview_admit_card = Permission.objects.get_or_create(
        codename="can_preview_admit_card",
        name="Can Preview Admit Card",
        content_type=student_type
    )

    can_print_admit_card = Permission.objects.get_or_create(
        codename="can_print_admit_card",
        name="Can Print Admit Card",
        content_type=student_type
    )

    can_view_student_details = Permission.objects.get_or_create(
        codename="can_view_student_details",
        name="Can View Student Details",
        content_type=student_type
    )

    can_add_student_results = Permission.objects.get_or_create(
        codename="can_add_student_results",
        name="Can Add Student Results",
        content_type=student_type
    )

    can_generate_certificate = Permission.objects.get_or_create(
        codename="can_generate_certificate",
        name="Can Generate Certificate",
        content_type=student_type
    )

    can_send_certificate_for_approval = Permission.objects.get_or_create(
        codename="can_send_certificate_for_approval",
        name="Can Send Certificate For Approval",
        content_type=student_type
    )

    can_approve_certificate = Permission.objects.get_or_create(
        codename="can_approve_certificate",
        name="Can Approve Certificate",
        content_type=student_type
    )

    can_view_student_results = Permission.objects.get_or_create(
        codename="can_view_student_results",
        name="Can View Student Results",
        content_type=student_type
    )


