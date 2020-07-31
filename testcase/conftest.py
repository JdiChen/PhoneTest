import pytest
from _pytest import config
# 此处在导入的时候就会新建base_page模块中的全局变量
from page import base_page
from config.depend import get_all_adb_devices


def pytest_addoption(parser):
    """
    会话前调用
    向pytest命令行添加自定义参数
    :param parser:
    :return:
    """
    parser.addoption("--sn",
                     help='test device')

@pytest.fixture(scope='session',
                autouse=True
                )
def get_cmd_device(request):
    """
    从命令行取得参数
    :param request:
    :return:
    """
    # 获取命令行参数
    base_page.SN = request.config.getoption('--sn')
    deivces = get_all_adb_devices()
    # 多设备判断
    if base_page.SN is None and len(deivces) > 1:
        raise RuntimeError('more than one device/emulator, '
                           'please specify the serial number by --sn=device')
    elif base_page.SN is None and len(deivces) == 1:
        base_page.SN = deivces[0]
    # return SN
