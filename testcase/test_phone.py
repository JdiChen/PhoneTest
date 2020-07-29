import sys

sys.path.append('..')
from page.home_page import Home

import pytest


class TestPhone:

    def setup(self):
        self.home = Home()

    @pytest.mark.skip()
    def test_create_contact(self):
        """
        1.桌面点击phone
        2.点击contacts
        3。点击创建联系人
        4。输入联系人信息
        5。保存
        :return:
        """
        creat_page = self.home.goto_phone_recents() \
            .goto_phone_contacts() \
            .goto_create_contact()
        creat_page.input_mesg('test', 'contact', '10086')
        creat_page.save()


if __name__ == '__main__':
    pytest.main(['-v', '-s', r'E:\PythonProject\Learn\po_test\test_case\test_phone.py'])
