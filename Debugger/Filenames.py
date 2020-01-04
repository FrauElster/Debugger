import os


class FILENAMES:
    # dirs
    LOG_DIR: str = "tracer_logs"

    # files
    LOG: str = os.path.join(LOG_DIR, 'tracer.log')
    DEBUG_LOG: str = os.path.join(LOG_DIR, 'debug.tracer.log')
