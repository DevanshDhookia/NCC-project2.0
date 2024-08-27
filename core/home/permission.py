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
    edit_student_permission = Permission.objects.get_or_create(
        codename="edit_student",
        name="Can Edit Rejected Students",
        content_type=student_type
    )

    can_approve_certs = Permission.objects.get_or_create(
        codename="can_approve_certs",
        name="Can approve Certificates",
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


    # clerk_group, created = Group.objects.get_or_create(
    #     name="clerk_group"
    # )
    # print(can_create_new_candidates)
    # clerk_group.permissions.add(32)
    # clerk_group.permissions.add(31)
    # clerk_group.permissions.add(29)

    # colonel_group, created = Group.objects.get_or_create(
    #     name="colonel_group"
    # )
    # colonel_group.permissions.add(31)
    # colonel_group.permissions.add(33)

    # senior_1_group, created = Group.objects.get_or_create(
    #     name="senior_1_group"
    # )
    # senior_1_group.permissions.add(31)
    # senior_1_group.permissions.add(33)

    # senior_2_group, created = Group.objects.get_or_create(
    #     name="senior_2_group"
    # )
    # senior_2_group.permissions.add(31)
    # senior_2_group.permissions.add(33)

