import sys,getopt
from time import sleep
from waitress import serve

from libs.logger import logger, LOG_FILE
logger = logger.getChild('run')

import webapp

def run_webapp():
    try:
        app = webapp.create_app()
        logger.info("Starting web conosole at 0.0.0.0:5005")
        serve(app, host="0.0.0.0", port=5005)
    except (KeyboardInterrupt, SystemExit):
        exit
    except Exception:
        logger.info("Error while running the web application", exc_info=True)


# the delay opetion was implemented to allow mount operation on mac os external drive to happen 
def main(argv):
    if len(argv) == 0:
        run_webapp()
    else:
        try:
            opts, args = getopt.getopt(argv,"hd:",["delay="])
            for opt, arg in opts:
                if opt == '-h':
                    print ("qemu-console.py without arguments starts the web app immediately")
                    print ("qemu-console.py -d <delay> starts with the specified delay in seconds")
                    sys.exit(2)
                elif opt in ("-d", "--delay"):
                    delay = int(arg)
                    sleep(delay)
                    run_webapp()
        except getopt.GetoptError:
            print("qemu-console.py -d <delay_in_sec>")


if __name__ == '__main__':
    main(sys.argv[1:])