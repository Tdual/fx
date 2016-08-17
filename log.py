import logging

def debug(msg):
    logging.basicConfig(
        format='%(asctime)s %(message)s',
        datefmt='%Y/%m/%d %p %I:%M:%S',
        filename="/share/var/log/error.log",
        level=logging.DEBUG
    )
    logging.debug(msg)
