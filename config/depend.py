import os,logging,time,yaml
import uiautomator2 as u2



def run_cmd(cmd):
    """
    运行非阻塞型命令，返回str
    :param cmd: run command
    :return: str
    """
    return os.popen(cmd).read()


def get_all_adb_devices():
    """
    返回当前系统所有已连接的adb设备列表
    :return:list
    """
    devices = list()
    devices_str = run_cmd("adb devices").split('\n')
    for i in range(1, len(devices_str) - 2):
        devices.append(devices_str[i].split('\t')[0])
    assert len(devices) != 0, "devices is None,Plese connect device"
    return devices


def get_logger(sn):
    """
    供外部调用的log接口
    :param sn: 设备号，也是显示在log里面的用户名
    :return:
    """
    return _get_device_log(sn)


def _get_device_log(sn):
    """
    设置全局logger
    :param sn: 设备号，也是显示在log里面的用户名
    :return: logger
    """
    logger = logging.getLogger(sn)
    logger.setLevel(logging.DEBUG)

    fmat = logging.Formatter("%(asctime)s,%(name)s,%(levelname)s : %(message)s")
    consore = logging.StreamHandler()
    consore.setFormatter(fmat)
    consore.setLevel(logging.NOTSET)

    file = logging.FileHandler(log_file(sn), 'w+')
    file.setLevel(logging.DEBUG)
    file.setFormatter(fmat)

    logger.addHandler(consore)
    logger.addHandler(file)
    u2.logger.addHandler(file)
    return logger


def get_local_time():
    """
    取得当前时间
    :return: str
    """
    tformat = '%Y%m%d_%H%M%S'
    mytime = time.strftime(tformat, time.localtime())
    return mytime


def log_file(sn):
    """
    以设备名新建log文件
    :param sn: 设备名
    :return:
    """
    log_dir = os.path.join(os.getcwd(), 'Test_Log')
    file_name = f'{sn}_{get_local_time()}.txt'
    file_path = os.path.join(log_dir, file_name)
    if not os.path.isdir(log_dir):
        os.mkdir(log_dir)
    return file_path


def read_yaml(file):
    """
    读取数据文件
    :param file:文件绝对路径
    :return:
    """
    with open(file, 'r', encoding='utf8') as f:
        return yaml.safe_load(f.read())
