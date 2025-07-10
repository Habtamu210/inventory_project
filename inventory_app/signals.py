from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Request, AuditLog, Notification, Item
from django.contrib.auth import get_user_model
from django.utils.timezone import now

User = get_user_model()

# 1. ✅ Send Notification on Request status change
@receiver(post_save, sender=Request)
def notify_on_request_change(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            recipient=instance.employee,
            message=f"Your request for {instance.item} has been submitted.",
        )
        if instance.item.business_unit.director:
            Notification.objects.create(
                recipient=instance.item.business_unit.director,
                message=f"New request from {instance.employee.username} needs your approval.",
            )
    else:
        if instance.status == 'PENDING_OFFICER':
            officers = User.objects.filter(role='INVENTORY_OFFICER')
            for officer in officers:
                Notification.objects.create(
                    recipient=officer,
                    message=f"Request #{instance.pk} is pending your approval.",
                )
        elif instance.status == 'APPROVED':
            Notification.objects.create(
                recipient=instance.employee,
                message=f"Your request for {instance.item} has been approved.",
            )
        elif "REJECTED" in instance.status:
            Notification.objects.create(
                recipient=instance.employee,
                message=f"Your request for {instance.item} was rejected.",
            )


# 2. ✅ Audit Log on create/update for Item
@receiver(post_save, sender=Item)
def log_item_changes(sender, instance, created, **kwargs):
    if created:
        AuditLog.objects.create(
            user=instance.assigned_to or User.objects.filter(role='ADMIN').first(),
            action_type="Created",
            object_type="Item",
            object_id=instance.pk,
            description=f"Item {instance} created.",
        )
    else:
        AuditLog.objects.create(
            user=instance.assigned_to or User.objects.filter(role='ADMIN').first(),
            action_type="Updated",
            object_type="Item",
            object_id=instance.pk,
            description=f"Item {instance} updated.",
        )


# 3. ✅ Audit Log on delete
@receiver(pre_delete, sender=Item)
def log_item_delete(sender, instance, **kwargs):
    AuditLog.objects.create(
        user=instance.assigned_to or User.objects.filter(role='ADMIN').first(),
        action_type="Deleted",
        object_type="Item",
        object_id=instance.pk,
        description=f"Item {instance} deleted.",
    )
