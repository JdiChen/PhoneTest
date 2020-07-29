import os
import time

import uiautomator2 as u2
from config.depend import get_logger, read_yaml
import logging

# 设备号，在conftest.py文件中读取
SN = None


class BasePage:
    # 设备
    _driver = None
    # 配置文件
    # _config = read_yaml(r'E:\PythonProject\Learn\po_test\data\test_data.yaml')
    _config = read_yaml(os.path.join('..', 'data', 'test_data.yaml'))
    # log
    _log: logging = None
    # 异常弹框的text列表
    _black_list = ['OK', 'ALLOW ALL THE TIME', 'Keep off']
    # 最大异常处理次数
    _error_max_count = 3
    # 异常处理次数
    _error_count = 0

    def __init__(self, driver=None):
        """
        初始化driver,运行时进入homepage
        """
        if driver is None:
            self._log = get_logger(SN)
            self._driver = u2.connect(SN)
            self._log.info('connect done')
            # 隐式等待10S
            self._driver.implicitly_wait(10)
            # self._driver.click_post_delay(3)
            # self._log.info("device info:", *self._driver.info)

            # 获取设备属性，如果是灭屏状态，则亮屏解锁
            if not self._driver.info['screenOn']:
                # 解锁
                self._driver.unlock()
                self._log.info('device is unlock')
            else:
                self._log.info('device is screen on')

            self._driver.press('home')
        else:
            self._driver = driver

    def __find_ele(self, locator: str):
        """
        查找元素，自动判断元素属性，调用driver查找
        :param locator:
        :return:
        """

        ele = []
        # 查找元素前等待，使页面加载完成，防止执行太快而定位不到元素或者过早的定位到元素
        time.sleep(3)
        # 查找元素，如果找不到就捕获异常
        self._log.debug('try find element %s' % locator)
        if locator.startswith('//') and len(self._driver.xpath(locator)) > 0:
            ele = self._driver.xpath(locator)
            self._log.debug('Found ele by XPath')
            return ele
        elif ':id/' in locator and len(self._driver(resourceId=locator)) > 0:
            ele = self._driver(resourceId=locator)
            self._log.debug('Found ele by resourceId')
        elif len(self._driver(text=locator)) > 0:
            ele = self._driver(text=locator)
            self._log.debug('Found ele by text')
        elif len(self._driver(description=locator)) > 0:
            ele = self._driver(description=locator)
            self._log.debug('Found ele by description')
        elif len(self._driver(className=locator)) > 0:
            ele = self._driver(className=locator)
            self._log.debug('Found ele by className')
        return ele

    def find(self, locator: str, index=0):
        """

        :param locator:
        :param index:
        :return:
        """
        try:
            # 返回指定的元素
            # 找到后设置异常处理次数为默认0
            ele = self.__find_ele(locator)
            if len(ele) == 0:
                raise ValueError('not find ele')
            else:
                # 这里是因为在xpath中不会有下标，只会返回一个元素
                # 不判断会造成错误
                if len(ele) > 1:
                    return ele[index]
                return ele
        except Exception as e:
            self._log.debug('find ele error,try black list')
            # 判断异常处理次数是否达到最大值,达到则报错
            self._log.info(f'erorr count is {self._error_count}')
            if self._error_count > self._error_max_count:
                raise e
            self._error_count += 1
            # 到弹框处理的列表中查找，能找到就点击
            for black in self._black_list:
                # 遍历列表中的弹框
                self._log.info(f'try find {black}')
                # 查找黑名单元素
                ele = self.__find_ele(black)
                if len(ele) > 0:
                    ele.click()
                    self._log.debug('raise done')
                    # 处理完弹框后，调用自身，继续查找目标元素
                    return self.find(locator, index)
            self._log.info('no black text in this page')
            raise e

    def rool_find(self, ele):
        """
        滚动查找
        :return:element
        """
        pass

    def click(self, name):
        """
        封装点击
        :param name: 定位的字符串
        :return:
        """
        self._driver(text=name).click()

    def sendkey(self, name, mesg):
        """
        封装输入字符
        :param name: 定位的字符串
        :param mesg: 需要输入的文本
        :return:
        """
        self._driver(text=name).send_keys(mesg)
