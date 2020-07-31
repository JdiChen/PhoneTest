# PhoneTest
# 1.整体概述

本篇以android原生phone应用调用google contact应用新建联系人为例

有描述不清及错误的地方，请指正，有更优的处理方式，请评论交流，谢谢

## 1.1 目录结构

```python
├─config
│  │  depend.py #依赖相关，logging,adb等封装
│          
├─data
│      test_data.yaml #所有数据，元素定位等
│      
├─page #PO模式封装页面
│  │  all_phone_page.py 
│  │  base_page.py  #页面基类
│  │  home_page.py
│            
└─testcase #测试用例
    │  conftest.py
    │  test_phone.py
```

## 1.2 运行方法

```shell
#--sn=device 需要自己向pytest中添加参数
pytest script_path --sn=device
```

## 1.3 主要流程

1. 命令行启动
2. pytest hook函数读取从命令行传入的设备号，并返回给base_page.SN
3. 执行set_up，初始化driver,driver通过u2.connet(SN)连接
4. driver初始化过程中会初始化logger
5. 执行测试
6. 测试报告

# 2.使用PO模式搭建粗略框架

## 2.1 testcase目录

这里面存放测试用例，PO模式中，所有的操作细节都不能暴露到测试用例中，代码如下

```python
# test_phone.py
class TestPhone:

    def setup(self):
        # 实例化封闭的页面类
        self.home = Home()
   
    def test_create_contact(self):
        """
        1.桌面点击phone
        2.点击contacts
        3.点击创建联系人
        4.输入联系人信息
        5.保存
        :return:
        """
        creat_page = self.home.goto_phone_recents() \
            .goto_phone_contacts() \
            .goto_create_contact()
        creat_page.input_mesg('test', 'contact', '10086')
        creat_page.save()
```

此目录还会存放conftest.py文件，用来自定义命令行参数，后面会讲到

## 2.2 config目录

此目录用来存放一些项目中的依赖函数，方法比较杂，log模块等也可以放到这个目录中，看个人意愿

```python
# depend.py


def read_yaml(file):
    """
    读取数据文件
    :param file:文件绝对路径
    :return:
    """
    with open(file, 'r', encoding='utf8') as f:
        return yaml.safe_load(f.read())

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
    
```

## 2.3 page目录

存放所有页面类，需要创建一个页面基类，用来封闭所有的公共方法，公共方法的封闭后面会描述，所有的页面类都需要继承基类，方便调用封装的方法和属性

一个页面做一个类。可以一个文件一个类，或者一个文件多个类，这里因为系统测试涉及到多个APP，我选择将一个应用的页面封装到一个文件内，其它主界面的一个文件一个类

```python
# base_page.py
class BasePage:
    #基类
    pass

# all_phone_page.py
class PhoneRecents(BasePage):
    # 通话记录界面
    
    pass
class PhoneContact(BasePage):
    # 联系人列表界面
    def goto_create_contact(self):
        """
        点击创建联系人
        :return: 创建联系人界面
        """
        # 元素操作封装到页面类中
        self.click(元素定位)
        #返回页面类，传入当前的driver,避免实例多个driver，后面会有driver初始化的代码
        return PhoneCreateContact(self._driver)    
    pass
class PhoneCreateContact(BasePage):
    # 创建联系人界面
    pass

# home_page.py
class Home(BasePage):
    """
    手机主页面
    """
    def goto_phone_recents(self):
        """
        主页面点击电话图标，进入电话应用界面
        :return: 电话通话记录界面
        """
        self._driver.press('home')
        self.click(self._config['Home']['phone_bt'])
        return PhoneRecents(self._driver)


```

## 2.4 data目录

存放数据,使用Yaml，在depend.py中有read_ymal函数读取此文件

```yaml
PhoneRecents:
  contacts_bt: 'Contacts'

PhoneContact:
#  create_bt: 'CREATE NEW CONTACT'
  create_bt: 'Create new contact'

PhoneCreateContact:
  save: 'Save'
  first: 'First name'
  last: 'Last name'
  phone: 'Phone'

Home:
  phone_bt: 'Phone'
```

到这里粗略的框架就搭建完成了，下面看具体的实现

# 3.方法封装

## 3.1 设备初始化（单例driver）

这里主要是需要复用driver和config，防止重复新建实例

config的复用采用直接定义类变量的方式，在测试运行前就直接读取，这里如果放到init中会重复读取，如果采用driver的方式会增加代码量

driver复用，目前采用的方式是在首个子类实例化时，传入一个driver，在构造函数中判断是否有driver传入，如果有传入，则将传入的driver赋值给构造函数中的driver,如果未传入，则初始化一个driver

```python
# base_page.py
# 设备号，通过conftest.py文件读取来自命令行的参数
SN = None


class BasePage:
    # 设备
    _driver = None
    # 配置文件    
    _config = read_yaml(os.path.join(os.getcwd(), 'data', 'test_data.yaml'))
    # log
    _log: logging = None

    def __init__(self, driver=None):
        """
        初始化driver,运行时进入homepage，当实例化时未传入driver
        则会新建一个driver，否则就使用传入的driver
        """
        if driver is None:
            # 初始化log，这里在第二次调用时，会实例不到
            self._log = get_logger(SN)
            self._driver = u2.connect(SN)
            self._log.info('connect done')
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
```

在po的使用中，当reture页面时，需要传入driver

```python
# home_page.py
class Home(BasePage):
    """
    手机主页面
    """
    def goto_phone_recents(self):
        """
        主页面点击电话图标，进入电话应用界面
        :return: 电话通话记录界面
        """
        self._driver.press('home')
        self.click(self._config['Home']['phone_bt'])
        return PhoneRecents(self._driver)
```

### 3.1.1 优化设备初始化

参考单例模式，将实例化driver的操作单独放入一个类中，在basepage基类中实例化，以此来实现复用，代码如下

```python
class _Driver:
    """
    单独将drvier建立一个类，
    """
    _log: logging = None
    _driver: u2.Device = None
    _instancn = None
    _isinit = False

    def __init__(self):
        if not self._isinit:
            self._log = get_logger(SN)
            self._driver = u2.connect(SN)
            self._log.info('connect done')
            self._log.info(f'devices info:{self._driver.device_info}\n{self._driver.info}')
            # 获取设备属性，如果是灭屏状态，则亮屏解锁
            if not self._driver.info['screenOn']:
                # 解锁
                self._driver.unlock()
                self._log.info('device is unlock')
            else:
                self._log.info('device is screen on')
            self._isinit = True

    def get_driver_and_log(self):
        #返回此类的driver和log实例
        return self._driver, self._log

    def __new__(cls, *args, **kwargs):
        if cls._instancn is None:
            cls._instancn = super().__new__(cls, *args, **kwargs)
        return cls._instancn
```

BasePage中获取driver

```python
class BasePage:
    # 设备
    _driver: u2.Device = None
    # log
    _log: logging = None
    def __init__(self, driver=None):
        """
        初始化driver,运行时进入homepage,使用driver类，单例出driver和log
        """
        # _Driver类为单例类，所以每次实例化时会返回以前的属性
        self._driver, self._log = _Driver().get_driver_and_log()     
```

页面类调用

```python
class Home(BasePage):
    """
    手机主页面
    """
    def goto_phone_recents(self):
        """
        主页面点击电话图标，进入电话应用界面
        :return: 电话通话记录界面
        """
        with allure.step('桌面点击电话图标'):
            self._driver.press('home')
            self.click(self._config['Home']['phone_bt'])
         # 这里所有页面类就可以少传入一个self._driver减少代码量
        return PhoneRecents()
```



## 3.2 log封装及打印

使用logging模块封装,在base_page中初始化

logging 为单例模式，全局直接通过base_page的log变量使用即可实现全局的log记录

log的打印根据个人情况在需要的位置调用基类中实例化的logger打印即可

```python
# depend.py
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
    #设置logger显示的级别
    logger.setLevel(logging.DEBUG)

    fmat = logging.Formatter("%(asctime)s,%(name)s,%(levelname)s : %(message)s")
    consore = logging.StreamHandler()
    consore.setFormatter(fmat)
    consore.setLevel(logging.INFO)
	# logfile是自己创建的函数，返回以sn_time.txt的绝对路径
    file = logging.FileHandler(log_file(sn), 'w+')
    file.setLevel(logging.DEBUG)
    file.setFormatter(fmat)
	# 输出至控制台
    logger.addHandler(consore)
    # 输出至文件
    logger.addHandler(file)
    return logger
```

## 3.3 元素查找封装（弹框异常处理）

处理步骤

1. 创建一个列表，用于存放点击弹框中元素的定位方式
2. 定义最大弹框处理次数和初始弹框次数
3. 执行元素查找，使用try..except捕获异常
4. 处理捕获的异常

```python
# 封装在BasePage基本类中 
    def __find_ele(self, locator: str):
        """
        查找元素，自动判断元素属性，调用driver查找， 不供子类调用
        返回查找到的对象，这里由于uiautomator2不管是否有找到元素都会返回一个对象
        需要通过判断对象长度才能决断是否找到元素
        :param locator:
        :return:
        """

        ele = []
        # 查找元素前等待，使页面加载完成，防止执行太快而定位不到元素或者过早的定位到元素
        time.sleep(3)
        # 查找元素，返回找到的对象
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
		返回一个元素，有弹框处理机制，供子类及外部类调用
        :param locator:
        :param index:
        :return:
        """
        try:
            # 返回指定的元素
            # 找到后设置异常处理次数为默认0
            ele = self.__find_ele(locator)
            if len(ele) == 0:
                # 抛出异常
                raise ValueError('not find ele')
            else:
                self._error_count = 0
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
                    # 这里一定要写在if里面，不然会造成
                    return self.find(locator, index)
            self._log.info('no black text in this page')
            # 如果列表中也没找到，则报错,并截图
            self.screenshot()
            raise e
```

## 3.4 操作封装

主要示例click和sendkeys的封装,这样我们在子类调用时，就不需要多次self.driver.click()了

直接使用self.click(元素)调用

```python
# 封装在BasePage基本类中     
    def click(self, name, index=0):
        """
        封装点击
        :param name: 定位的字符串
        :param index: 定位下标，当有多个相同元素时使用
        :return:
        """
        self.find(name, index).click()

    def sendkey(self, name, mesg, index=0):
        """
        封装输入字符
        :param name: 定位的字符串
        :param mesg: 需要输入的文本
        :param index: 定位下标，当有多个相同元素时使用
        :return:
        """
        self.find(name, index).send_keys(mesg)
```

## 3.5 页面类的封装

以首页为例，除了此方法，还可以封装更多的方法，比如进入设置界面，进入相机界面等，均可以新建一个方法调用

```python
# 主界面的页面类
class Home(BasePage):
    """
    手机主页面
   
    """
    # 封装进入通话记录界面的方法，这样就可以在测试用例中实例化后
    # 直接调用此方法就可以完成操作，无需传值，后续维护也只需要维护这个方法
    # 无需要改动测试用例    
    def goto_phone_recents(self):
        """
        主页面点击电话图标，进入电话应用界面
        :return: 电话通话记录界面
        """
        self._driver.press('home')
        self.click(self._config['Home']['phone_bt'])
        return PhoneRecents(self._driver)

```



## 3.6 pytest中自定义命令行参数

整体思路是新建参数后，使用fixture自动调用并设置调用时间为session开始的方式来获取命令行参数并返值给base_page,这样就不会影响到其它测试用例

```python
#  conftest.py
# 这是hook函数，pytest规定只能使用此名重写
def pytest_addoption(parser):
    """
    向pytest命令行添加自定义参数
    :param parser:
    :return:
    """
    parser.addoption("--sn",
                     help='test device')

# 这里需要加autouse，直接在会话开始时调用，后续就不用在测试用例中加fixture了
@pytest.fixture(scope='session', autouse=True)
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
    # SN为base_page的全局变量，接收测试的设备号
    return base_page.SN
```

## 3.7 截图方法

在BasePage基类中封装

```python
def screenshot(self):
    """
    截图并附加到测试报告中
    :return:
    """
    picture_file = os.path.join(os.getcwd(), 'tmp_picture.png')
    try:
        # 截图
        self._driver.screenshot(picture_file)
        # 将生成的截图附加到测试报告中，这里一定文件读取方式一定要为 rb
        # 否则会造成测试报告中图片无法打开的错误
        allure.attach(open(picture_file, 'rb').read(),
                      'Fail Screenshot',
                      attachment_type=allure.attachment_type.PNG)
        self._log.info('screenshot success')
        os.remove(picture_file)
    except Exception as e:
        self._log.exception('screenshot fail')
        raise e
```



# 4.报告输出

使用allure作为报告处理插件，这部分主要是要了解allure的feature，使用allure Features装饰测试用例，来美化报告，这里列一些常用的，官方有更详细的介绍

```http
https://docs.qameta.io/allure/#_pytest
```

## 4.1 step输出测试步骤

使用with allure的方式可以装一些操作封装到一个步骤内

```python
    def goto_phone_recents(self):
        """
        主页面点击电话图标，进入电话应用界面
        :return: 电话通话记录界面
        """
        # step(描述)，描述为显示到报告页的内容
        with allure.step('桌面点击电话图标'):
            self._driver.press('home')
            self.click(self._config['Home']['phone_bt'])
        return PhoneRecents()
    
# 另一种方式
@allure.step(str)
def test():
    pass
```

## 4.2 Description输出测试用例的描述

测试用例的文档描述就是allure里的Description

```python
    def test_create_contact(self):
        """
        #这里就是显示在allure里的Description
        1.桌面点击phone
        2.点击contacts
        3.点击创建联系人
        4.输入联系人信息
        5.保存
        :return:
        """
```

## 4.3 title输出测试用例名称

默认输入的是测试方法的名称，使用title装饰后可以修改显示的名称

```python
    @allure.title('新建联系人')
    def test_create_contact(self):
    	pass
```

## 4.4 severity标记测试用例的严重等级

当出现bug时的应该按照此提示提交相应等级的bug,也可以用于测试类，则表示整个测试类是严重等级

```python
"""
#等级设置有如下值 
BLOCKER = 'blocker'
CRITICAL = 'critical'
NORMAL = 'normal'
MINOR = 'minor'
TRIVIAL = 'trivial'
"""
	@allure.severity(allure.severity_level.TRIVIAL)
    def test_create_contact(self):
    	pass
```

## 4.5 suite,parent_suite,sub_suite输出测试用例模块的名称

```python
@allure.suite("测试电话应用") #测试用例模块（文件）名
@allure.parent_suite('测试用例') #测试用例目录名
@allure.sub_suite('测试电话类') # 测试用例类名
def test():
	pass
```

