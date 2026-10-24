from pages.base import BasePage
from pages.dialog import Dialog


class AdsPage(BasePage):
    path = "/ads/"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ad = Dialog(self, 1272)
