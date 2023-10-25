from celery import shared_task

from habits import services


@shared_task
def task_send_scheduled_reminder() -> None:
    """Отправка напоминаний о привычке в соответствии с недельным расписанием пользователям в telegram"""

    services.send_scheduled_reminder()


@shared_task
def task_send_interval_reminder() -> None:
    """Отправка напоминаний о привычке с заданным интервалом пользователям в telegram"""

    services.send_interval_reminder()
