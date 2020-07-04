import logging

from publisher.publisher import main, datetime

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        msg = "The System Ecnountered an Exception on"
        date = datetime.now().strftime('%d %b %Y %H:%M')
        logging.basicConfig(filename='publisher.log')
        logging.exception("%s %s", msg, date)
