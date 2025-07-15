import unittest
import time
import os
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class LearnPressEnrollCourseTest(unittest.TestCase):
    BASE_URL = "http://wp.local"
    USERNAME = "admin"
    PASSWORD = "admin"
    SCREENSHOT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "screenshots")

    @classmethod
    def setUpClass(cls):
        if not os.path.exists(cls.SCREENSHOT_DIR):
            os.makedirs(cls.SCREENSHOT_DIR)
        cls.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        cls.driver.maximize_window()
        cls.driver.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def take_screenshot(self, test_name):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{test_name}.png"
        filepath = os.path.join(self.SCREENSHOT_DIR, filename)
        try:
            self.driver.save_screenshot(filepath)
            print(f"📸 Đã chụp ảnh màn hình: {filepath}")
            return filepath
        except Exception as e:
            print(f"❌ Không thể chụp ảnh màn hình: {str(e)}")
            return None


    def step_demo(self, msg, delay=1.5):
        print(f"[DEMO] {msg}")
        time.sleep(delay)

    def test_01_enroll_first_course(self):
        """Test Case: Enroll the first course on /courses/ page"""
        try:
            # Truy cập trang /courses/
            courses_url = f"{self.BASE_URL}/courses/"
            self.driver.get(courses_url)
            self.step_demo(f"Truy cập trang danh sách khoá học: {courses_url}")
            wait = WebDriverWait(self.driver, 10)
            # Tìm ul chứa danh sách khoá học (dùng selector đơn giản cho mọi theme)
            course_list = wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR, "ul.learn-press-courses"
            )))
            # Tìm li đầu tiên
            first_li = course_list.find_element(By.TAG_NAME, "li")
            # Tìm nút Read more trong li đầu tiên
            read_more_btn = first_li.find_element(By.CSS_SELECTOR, "div.course-button-read-more a")
            course_detail_url = read_more_btn.get_attribute("href")
            self.step_demo(f"Nhấn Read more để vào trang chi tiết: {course_detail_url}")
            read_more_btn.click()
            self.step_demo("Đã nhấn Read more, vào trang chi tiết khoá học")
            # Đợi trang detail load
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "body.single-lp_course")))
            # Tìm form enroll và click Start Now
            enroll_form = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "form.enroll-course")))
            start_now_btn = enroll_form.find_element(By.CSS_SELECTOR, "button[type='submit']")
            self.step_demo("Tìm thấy nút Start Now, chuẩn bị nhấn để bắt đầu học khoá học")
            start_now_btn.click()
            self.step_demo("Đã nhấn Start Now để bắt đầu học khoá học!")
            
            # Sau khi click, kiểm tra nếu xuất hiện form checkout yêu cầu đăng nhập
            try:
                checkout_form = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "form#learn-press-checkout-form.lp-checkout-form")))
                self.step_demo("Phát hiện form checkout, tiến hành đăng nhập...")
                # Điền username và password
                username_input = checkout_form.find_element(By.ID, "username")
                password_input = checkout_form.find_element(By.ID, "password")
                username_input.clear()
                username_input.send_keys(self.USERNAME)
                password_input.clear()
                password_input.send_keys(self.PASSWORD)
                self.step_demo("Đã nhập username và password, chuẩn bị nhấn Place order")
                # Click Place order
                place_order_btn = checkout_form.find_element(By.ID, "learn-press-checkout-place-order")
                place_order_btn.click()
                self.step_demo(f"Đã đăng nhập thành công với user: {self.USERNAME} trên trang checkout!")
                self.take_screenshot("checkout_login_success")
            except Exception as ce:
                print("Không xuất hiện form checkout hoặc không cần đăng nhập tiếp.")
            
            # Sau khi checkout, kiểm tra trang nhận order
            try:
                # Đợi chuyển trang sang /lp-checkout/lp-order-received/
                wait.until(EC.url_contains("lp-order-received"))
                self.step_demo("Đã chuyển sang trang order received.")
                # Tìm <tr class="item">
                item_row = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "tr.item")))
                course_link = item_row.find_element(By.TAG_NAME, "a")
                course_url = course_link.get_attribute("href")
                self.step_demo(f"Click vào link khoá học: {course_url}")
                course_link.click()
                self.step_demo("Đã vào lại trang chi tiết khoá học sau khi order")
                # Đợi trang detail load
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "body.single-lp_course")))
                # Kiểm tra nút trạng thái khoá học
                try:
                    finish_btn = self.driver.find_element(By.CSS_SELECTOR, "button.wp-block-learnpress-course-button.lp-button.btn-finish-course")
                    btn_text = finish_btn.text.strip().lower()
                    self.step_demo(f"Đã kiểm tra trạng thái khoá học sau khi enroll. Nút trạng thái: '{btn_text}'")
                    self.take_screenshot("course_status_button")
                    if btn_text in ["finish", "continue"]:
                        self.step_demo(f"✅ Thành công: Trạng thái khoá học là '{btn_text}'. Đã đăng ký và truy cập khoá học thành công!")
                    elif btn_text == "start now":
                        self.fail("❌ Thất bại: Sau khi enroll, trạng thái vẫn là 'Start Now'!")
                    else:
                        print(f"Nút trạng thái không xác định ('{btn_text}'), cần kiểm tra lại.")
                except Exception as btn_e:
                    self.fail(f"Không tìm thấy nút trạng thái khoá học: {str(btn_e)}")
            except Exception as order_e:
                self.fail(f"Không kiểm tra được trạng thái khoá học sau khi checkout: {str(order_e)}")
            
        except Exception as e:
            self.take_screenshot("enroll_course_failed")
            self.fail(f"Không thể enroll khoá học: {str(e)}")

if __name__ == "__main__":
    unittest.main()
