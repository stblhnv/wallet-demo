from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from wallet.services import update_exchange_rates


list_jobs = (
    {
        'func': update_exchange_rates,
        'trigger': CronTrigger.from_crontab('*/3 * * * *'),
        'replace_existing': True,
    },
)


def init_scheduler():
    scheduler = BlockingScheduler()
    for job_args in list_jobs:
        scheduler.add_job(**job_args)

    return scheduler


def run_scheduler():
    scheduler = init_scheduler()
    try:
        scheduler.start()
    except KeyboardInterrupt:
        scheduler.shutdown()
