from functional_tests import FunctionalTest, ROOT
class TestHomePage (FunctionalTest):
	def setUp(self):
		self.url = ROOT + '/HCIQSoftware'
		get_browser=self.browser.get(self.url)

	def test_can_view_home_page(self):
		response_code = self.get_response_code(self.url)
		self.assertEqual(200, response_code)

	def test_has_right_title(self):
		title = self.browser.find_element_by_tag_name('title')
		self.assertEqual('HCI-Q Software', title.text)

	def test_has_right_headings(self):
		body = self.browser.find_element_by_tag_name('body')
		self.assertIn('This software is used to perform HCI-Q research', body.text)

