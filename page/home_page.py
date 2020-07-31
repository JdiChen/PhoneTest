import allure

from page.all_phone_page import PhoneRecents
from page.base_page import BasePage


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
        return PhoneRecents()

