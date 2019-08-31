"""Functional tests."""

from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from .models import Lamp


class LampsFunctionalTests(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.driver = webdriver.Firefox()

    @classmethod
    def tearDownClass(cls):
        cls.driver.close()
        super().tearDownClass()

    def test_view_list(self):
        lamp_off = Lamp.objects.create(name='lamp1')
        # TODO: open working period
        lamp_on = Lamp.objects.create(name='lamp2', is_on=True)

        self.driver.get(self.live_server_url + '/lamps/')
        self.assertIn('lamps', self.driver.title.lower())
        table = self.driver.find_element_by_tag_name('table')
        rows = table.find_elements_by_tag_name('tr')
        self.assertIn(lamp_off.name, rows[1].text)
        self.assertIn('off', rows[1].text.lower())
        self.assertIn(lamp_on.name, rows[2].text)
        self.assertIn('on', rows[2].text.lower())

    def test_view_details(self):
        lamp = Lamp.objects.create(name='lamp1')

        # following link in list view
        list_url = self.live_server_url + '/lamps/'
        self.driver.get(list_url)
        table = self.driver.find_element_by_tag_name('table')
        rows = table.find_elements_by_tag_name('tr')
        first_row = rows[1]
        lamp_link = first_row.find_element_by_tag_name('a')
        lamp_link.click()

        self.assertIn(lamp.name, self.driver.title.lower())
        table_text = self.driver.find_element_by_tag_name('table').text.lower()
        expected_header_parts = [
            'name',
            'status',
            'brightness',
            'last switch',
            'working time',
        ]
        for expected_part in expected_header_parts:
            self.assertTrue(expected_part in table_text,
                            f'"{expected_part}" not found')

        list_link = self.driver.find_element_by_link_text('Back to list')
        self.assertEqual(list_link.get_attribute('href'), list_url)

    def test_view_control_display(self):
        lamp = Lamp.objects.create(name='lamp1')

        self.driver.get(f'{self.live_server_url}/lamps/{lamp.pk}/control')
        self.assertIn(lamp.name, self.driver.page_source)
        form = self.driver.find_element_by_tag_name('form')
        brightness_input = form.find_element_by_name('brightness')
        self.assertEqual(brightness_input.get_attribute('value'),
                         str(lamp.brightness))
        switch_inputs = form.find_elements_by_name('status')
        choices = {input.get_attribute('value'): input
                   for input in switch_inputs}
        choice_values = set(choices.keys())
        self.assertEqual(choice_values, {'on', 'off'})
        off_is_checked = choices['off'].get_attribute('checked')
        self.assertTrue(off_is_checked)

    def test_view_control_apply(self):
        lamp = Lamp.objects.create(name='lamp1')

        self.driver.get(f'{self.live_server_url}/lamps/{lamp.pk}/control')

        brightness_input = self.driver.find_element_by_id('id_brightness')
        brightness_input.send_keys(Keys.ENTER)
