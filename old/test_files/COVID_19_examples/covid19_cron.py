from apscheduler.schedulers.background import BlockingScheduler
import covid19step1_5
import schedule
import time

scheduler = BlockingScheduler()


# Schedules the job_function to be executed Monday through Friday at 20:00 (8pm)
scheduler.add_job(covid19step1_5, 'cron', day_of_week='mon-fri', hour=20, minute=00)

# Start the scheduler
scheduler.start()