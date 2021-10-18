import covid19step1_5
import covid19step2_5
import schedule
import time


schedule.every().day.at("00:05").do(covid19step1_5.step1_5,'Updating KGPLVariable for'
                                                           'the value of latest 14 days.')
schedule.every().day.at("00:10").do(covid19step2_5.step2_5,'Updating KGPLVariable for'
                                                           'the prediction for tomorrow.')


while True:
    schedule.run_pending()
    time.sleep(60) # wait