import logging

logger = logging.getLogger(__name__)
formatter = logging.Formatter(u'[%(asctime)s] %(filename)s [LINE:%(lineno)d] #%(levelname)-8s  %(message)s\n')

sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
sh.setFormatter(formatter)

fh = logging.FileHandler("bot.log")
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)

logger.addHandler(sh)
logger.addHandler(fh)

logger.setLevel(logging.DEBUG)

logger.info("Logging initialized!")
