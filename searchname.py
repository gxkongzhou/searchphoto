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
import mytools
from datetime import datetime
from logging.handlers import RotatingFileHandler as RF
# '
from pathlib import Path

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

# Dir constant parameter
root = r"\\tencent.com\tfs\跨部门项目\HRC"
photo_p = r'{}\photo'.format(root)
photo_ser_p = r'{}\photo_service'.format(root)
cust_dir = r'{}\custom'.format(photo_ser_p)


# log config
LOGFORMAT = '%(asctime)s - %(thread)s - %(levelname)s : %(message)s'
LOGFILE = 'c:\date\searchlog'
LOGERROR = 'c:\date\searcherr'
Path('c:\date').mkdir(parents=True, exist_ok=True)

searchlog = logging.getLogger('searchlog')
searchlog.propagate = False
searchhandler = RF(LOGFILE, mode='a', maxBytes=30 * 1024 * 1024, backupCount=3)
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
            if re.match(r'[a-zA-Z]', char) or '\u4e00' <= char <= '\u9fff':
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
    searchlog.debug("Start del !!!")
    for cfile in cust_path.rglob('*.png'):
        if cfile.stem in finally_name:
            cfile.unlink()
            if not cfile.exists():
                searchlog.warning('Delect {} 成功'.format(cfile))
            else:
                searchlog.warning('Delect {} 失败！！'.format(cfile))

def cleancustom():
    starttime = time.perf_counter()

    #photo_today = photo_p + r"\原始工卡照\20200831补录"
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
    time.sleep(60)
    alljpgfile = [x for x in source_path.rglob('*.jpg') if x.is_file()]
    all_name2 = []
    find_all_name(all_name2, alljpgfile)
    finally_name = all_name1 if all_name1 == all_name2 else list(set(all_name2 + all_name1))

    searchlog.debug('The number of files today is : {}'.format(len(finally_name)))
    searchlog.debug('#'*120)
    grouping_f = mytools.grouping(finally_name,10)
    str_group = [str(g) for g in grouping_f]
    searchlog.debug('\n'.join(str_group))
    searchlog.debug('#'*120)

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
            for n in check_name(file.stem):
                namel.pop(n)
            correctname = "".join(namel)
            # newPath_object = Path/'string'
            record = {'old':file.stem, 'new':correctname}
            searchlog.warning(" Rename <{old}> to <{new}>".format(**record))
            file.rename(file.with_name(correctname + file.suffix))
            finally_name.append(correctname)
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
        searchlog.debug("There's been some trouble")
