from datetime import datetime, timedelta

if __name__ == "__main__":
    today = datetime.today() 
    today = today.strftime('%Y%m%d')
    print(today)