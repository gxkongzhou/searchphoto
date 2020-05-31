r"""Find the user name of the photo stored in the warehouse the day before and
clean up the personal photos.Add get specific photo object.
Actually returns the photo object

    This exports:
    e.g.
"""

import logging
import re
import sys
import time
from datetime import datetime
from logging.handlers import RotatingFileHandler
# '
from pathlib import Path

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

# Dir constant parameter
cust_dir = r'X:'
photo_ser_p = 'Y:'
photo_p = 'Z:'

# log config
LOGFORMAT = '%(asctime)s - %(thread)s - %(levelname)s : %(message)s'
LOGFILE = 'c:\date\searchlog'
LOGERROR = 'c:\date\searcherr'
Path('c:\date').mkdir(parents=True, exist_ok=True)

searchlog = logging.getLogger('searchlog')
searchlog.propagate = False
searchhandler = RotatingFileHandler(LOGFILE, mode='a', maxBytes=30 * 1024 * 1024, backupCount=3)
searchformat = logging.Formatter(LOGFORMAT)

searchlog.setLevel(logging.DEBUG)
searchhandler.setLevel(logging.DEBUG)
searchhandler.setFormatter(searchformat)
searchlog.addHandler(searchhandler)


# Only English characters and Chinese characters are allowed
def check_name(name):
    errornum = []
    for num, char in enumerate(name):
        if num == 0:
            if re.match(r'[a-zA-Z]]', char) or '\u4e00' <= char <= '\u9fff':
                continue
            else:
                errornum.append(num)
        elif re.match(r'[a-zA-Z_]', char) or '\u4e00' <= char <= '\u9fff':
            continue
        else:
            errornum.append(num)
    if len(errornum) == 0:
        return True
    else:
        # searchlog.error("File <{}> name is illegal".format(file.stem))
        return errornum

    # searchlog.error("File <{}> name is illegal".format(file.stem))


def del_cust(finally_name, cust_path):
    print("start del")
    for cfile in cust_path.rglob('*.png'):
        if cfile.stem in finally_name:
            searchlog.warning('Delect {}'.format(cfile))
            cfile.unlink()


def cleancustom():
    starttime = time.perf_counter()

    # photo_today = r"Z:\原始工卡照\20200313补录"
    today = datetime.now().strftime('%Y%m%d')
    photo_today = "".join([photo_p, "\原始工卡照", '\{}'.format(today), "补录"])

    # search photo source file
    try:
        source_path = Path(photo_today)
        if source_path.exists():
            searchlog.warning("Enter the directory {}".format(photo_today))
        else:
            raise FileNotFoundError('The path {} not fount'.format(photo_today))
    except FileNotFoundError as fileer:
        searchlog.error("{0} {1}".format(fileer.strerror, fileer.filename))
        raise

    allfile = [x for x in source_path.rglob('*') if x.is_file()]
    # Record an incorrectly formatted file
    for file in allfile:
        if re.search(r'png$', file.suffix, re.I, ):
            searchlog.warning('The file <{}> is not correct format'.format(file.name))
        if re.search(r'jpeg$', file.suffix, re.I, ):
            searchlog.warning('The file <{}> is not correct format'.format(file.name))

    # Double check all files in directory to avoid omissions caused by network delays
    alljpgfile = [x for x in source_path.rglob('*.jpg') if x.is_file()]
    all_name1 = []
    find_all_name(all_name1, alljpgfile)
    time.sleep(300)
    alljpgfile = [x for x in source_path.rglob('*.jpg') if x.is_file()]
    all_name2 = []
    find_all_name(all_name2, alljpgfile)
    finally_name = all_name1 if all_name1 == all_name2 else list(set(all_name2+all_name1))

    searchlog.debug('The number of files today is : {}'.format(len(finally_name)))

    # search custom file
    try:
        cust_path = Path(cust_dir)
        if cust_path.exists():
            searchlog.warning("Enter the directory {}".format(cust_dir))
        else:
            raise FileNotFoundError('The path {} not fount'.format(cust_dir))
    except FileNotFoundError as fileer:
        searchlog.error("{0} {1}".format(fileer.strerror, fileer.filename))
        raise
    else:
        del_cust(finally_name, cust_path)
        usetime = time.perf_counter() - starttime
        searchlog.debug('Time used : {}'.format(usetime))


def find_all_name(finally_name, alljpgfile):
    for file in alljpgfile:
        if check_name(file.stem) != True:
            # Clear the illegal
            namel = [n for n in file.stem]
            for n in check_name(file):
                namel.pop(n)
            correctname = "".join(namel)
            # newPath_object = Path/'string'
            searchlog.warning(" Rename {}".format(correctname))
            file.rename(file.parent / correctname)
            finally_name.append(file.stem)
        else:
            finally_name.append(file.stem)


if __name__ == "__main__":
    mysched = BlockingScheduler()
    # 22 points every day
    mytrigger = CronTrigger(hour='23', minute=30)
    mysched.add_job(cleancustom, mytrigger, misfire_grace_time=300)
    fstd = open(LOGERROR, 'a')
    sys.stdout = fstd
    sys.stderr = fstd
    try:
        mysched.start()
    except:
        searchlog.error("There's been some trouble")
