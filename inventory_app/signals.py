from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from .models import Request, RequestApproval, Notification, AuditLog, User, BusinessUnit
import logging

logger = logging.getLogger(__name__)

# -------------------------------------------------
# Notify Director when a request is submitted
# -------------------------------------------------
@receiver(post_save, sender=Request)
def notify_director_on_request(sender, instance, created, **kwargs):
    if created and instance.status == 'PENDING_DIRECTOR':
        try:
            director = instance.employee.business_unit.director
            if director is not None:
                Notification.objects.create(
                    recipient=director,
                    message=f"New request from {instance.employee.username} for {instance.product.name}"
                )
            else:
                logger.warning(f"No director assigned to business unit '{instance.employee.business_unit}' for request {instance.id}")
        except AttributeError as e:
            logger.error(f"Missing attribute when notifying director for request {instance.id}: {e}")

# -------------------------------------------------
# Notify next approver and employee after approval
# -------------------------------------------------
@receiver(post_save, sender=RequestApproval)
def notify_after_approval(sender, instance, created, **kwargs):
    if not created:
        return

    req = instance.request
    if instance.status == 'APPROVED':
        if instance.role == 'DIRECTOR':
            try:
                officer = User.objects.filter(role='INVENTORY_OFFICER').first()
                if officer:
                    Notification.objects.create(
                        recipient=officer,
                        message=f"Request #{req.id} approved by Director. Awaiting your action."
                    )
                else:
                    logger.warning(f"No Inventory Officer found to notify for request {req.id}")
            except Exception as e:
                logger.error(f"Error notifying Inventory Officer for request {req.id}: {e}")
        elif instance.role == 'INVENTORY_OFFICER':
            Notification.objects.create(
                recipient=req.employee,
                message=f"Your request #{req.id} for {req.product.name} has been approved."
            )
    elif instance.status == 'REJECTED':
        Notification.objects.create(
            recipient=req.employee,
            message=f"Your request #{req.id} has been rejected by {instance.role.title()}."
        )

# -------------------------------------------------
# Audit log for new user creation
# -------------------------------------------------
@receiver(post_save, sender=User)
def log_user_creation(sender, instance, created, **kwargs):
    if created:
        AuditLog.objects.create(
            user=instance,
            action_type='Create',
            object_type='User',
            object_id=instance.id,
            description=f'User {instance.username} was created with role {instance.role}'
        )

# -------------------------------------------------
# Assign user to business unit if Director
# -------------------------------------------------
@receiver(post_save, sender=BusinessUnit)
def assign_director_to_unit(sender, instance, **kwargs):
    if instance.director:
        instance.director.role = 'DIRECTOR'
        instance.director.save()
        AuditLog.objects.create(
            user=instance.director,
            action_type='Assign',
            object_type='BusinessUnit',
            object_id=instance.id,
            description=f'User {instance.director.username} assigned as Director of {instance.name}'
        )
        AuditLog.objects.create(
            user=instance.director,
            action_type='Create',
            object_type='BusinessUnit',
            object_id=instance.id,
            description=f'Business Unit {instance.name} created with Director {instance.director.username}'
        )