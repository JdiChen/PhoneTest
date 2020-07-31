import allure

from page.base_page import BasePage


class PhoneRecents(BasePage):
    """
    通话记录界面
    """

    def goto_phone_contacts(self):
        """
        点击联系人图标
        :return: 联系人列表界面
        """
        with allure.step('点击联系人图标,进入联系人列表界面'):
            self.click(self._config['PhoneRecents']['contacts_bt'])
        return PhoneContact()


class PhoneContact(BasePage):
    """
    联系人列表界面
    """

    def goto_create_contact(self):
        """
        点击创建联系人
        :return: 创建联系人界面
        """
        # print('---------------self.sn is %s-----------------'% self.sn)
        with allure.step("点击创建联系人，进入创建联系人界面"):
            self.click(self._config['PhoneContact']['create_bt'])
        return PhoneCreateContact()


class PhoneCreateContact(BasePage):
    """
    创建联系人界面
    """

    def save(self):
        """
        点击保存按钮
        :return:
        """
        with allure.step('保存联系人'):
            self.click(self._config['PhoneCreateContact']['save'])

    def input_mesg(self, first_name, last_name, number):
        """
        输入联系人信息
        :param first_name: 名称
        :param last_name: 姓氏
        :param number: 电话号码
        :return:
        """
        with allure.step('输入联系人信息'):
            self.sendkey(self._config['PhoneCreateContact']['first'], first_name)
            self.sendkey(self._config['PhoneCreateContact']['last'], last_name)
            self.sendkey(self._config['PhoneCreateContact']['phone'], number)
