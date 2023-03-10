# coding=utf-8 
import logging
import time
from logging.handlers import TimedRotatingFileHandler

max_day = 5  # 最多保留的日志数量
# 第一步，创建一个logger  
logger = logging.getLogger()
logger.setLevel(logging.INFO)  # Log等级总开关  

# 第二步，创建一个handler，用于写入日志文件   
fh = TimedRotatingFileHandler('/underdog/fsmlog/main_all.log',
                              when="D",
                              interval=1,
                              backupCount=1)
fh.setLevel(logging.CRITICAL)  # 输出到file的log等级的开关  

efh = TimedRotatingFileHandler('/underdog/fsmlog/main_error.log',
                               when="D",
                               interval=1,
                               backupCount=max_day)
efh.setLevel(logging.ERROR)

ifh = TimedRotatingFileHandler('/underdog/fsmlog/main_info.log',
                               when="D",
                               interval=1,
                               backupCount=max_day)
ifh.setLevel(logging.INFO)

# 第三步，再创建一个handler，用于输出到控制台  
ch = logging.StreamHandler()
ch.setLevel(logging.CRITICAL)  # 输出到console的log等级的开关  

# 第四步，定义handler的输出格式  
formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
fh.setFormatter(formatter)
ch.setFormatter(formatter)
efh.setFormatter(formatter)
ifh.setFormatter(formatter)

# 第五步，将logger添加到handler里面  
logger.addHandler(fh)
logger.addHandler(ch)
logger.addHandler(efh)
logger.addHandler(ifh)

# if __name__ == "__main__":
#    for i in range(10):
#        logger.info("This is a info test!")
#        logger.debug("This is a debug test!")
#        logger.error("This is a error test!")
#        time.sleep(51)
