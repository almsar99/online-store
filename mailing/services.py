from django.core.mail import send_mail
from django.utils import timezone

from mailing.models import Attempt


def send_mailing(mailing):
    now = timezone.now()

    if not mailing.start_time <= now <= mailing.end_time:
        raise ValueError(
            'Рассылку можно запускать только между датой начала и датой окончания.'
        )

    attempts = []

    for recipient in mailing.recipients.all():
        try:
            send_mail(
                subject=mailing.message.subject,
                message=mailing.message.body,
                from_email=None,
                recipient_list=[recipient.email],
                fail_silently=False,
            )

            attempts.append(
                Attempt(
                    mailing=mailing,
                    status=Attempt.STATUS_SUCCESS,
                    server_response='Письмо успешно отправлено',
                )
            )

        except Exception as error:
            attempts.append(
                Attempt(
                    mailing=mailing,
                    status=Attempt.STATUS_FAILED,
                    server_response=str(error),
                )
            )

    Attempt.objects.bulk_create(attempts)

    return attempts
