import covid19step1_5
import covid19step2
import schedule
import time


# schedule.every().day.at("01:00").do(job,'It is 01:00')
schedule.every().day.at("23:16").do(covid19step1_5.step1_5,'Updating KGPLVariable for'
                                                           'the value of latest 14 days.')
schedule.every().day.at("23:20").do(covid19step2.step2,'Updating KGPLVariable for'
                                                           'the prediction for tomorrow.')


while True:
    schedule.run_pending()
    time.sleep(60) # wait