from apscheduler.schedulers.blocking import BlockingScheduler
import requests

sched = BlockingScheduler()

@sched.scheduled_job('cron', day_of_week='mon-sun', minute='*/20')
def scheduled_job():
    url = "https://linebot-account-book.herokuapp.com/"
    conn = requests.get(url)
    # print('This job is run every weekday at 5pm.')
    print(conn.status_code)

sched.start()