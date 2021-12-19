import traceback
from waitress import serve

from libs.logger import logger, LOG_FILE
logger = logger.getChild('run')

import webapp

if __name__ == '__main__':
    try:
        app = webapp.create_app()
        logger.info("Starting web conosole at 0.0.0.0:5005")
        serve(app, host="0.0.0.0", port=5005)
    except (KeyboardInterrupt, SystemExit):
        exit
    except Exception:
        logger.info("Error executing Azure auth operation.", exc_info=True)

# import traceback
# import libs.console as console
# if __name__ == '__main__':
#     try:
#         con = console.QEMUConsole()
#         con._is_vm_process_running('manjaro')
#     except Exception as e:
#         traceback.print_exc()