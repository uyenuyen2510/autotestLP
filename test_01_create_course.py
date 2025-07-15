import unittest
import time
import random
import string
import os
import datetime
import tempfile
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

class LearnPressCreateCourseTest(unittest.TestCase):
    # Thư mục lưu ảnh chụp màn hình
    SCREENSHOT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "screenshots")
    BASE_URL = "http://wp.local"
    LOGIN_PATH = "/wp-login.php"
    ADMIN_PATH = "/wp-admin"
    COURSES_PATH = "/wp-admin/edit.php?post_type=lp_course"
    USERNAME = "admin"
    PASSWORD = "admin"
    
    @classmethod
    def setUpClass(cls):
        """Khởi tạo trình duyệt và đăng nhập một lần duy nhất cho tất cả các test"""
        # Tạo thư mục screenshots nếu chưa tồn tại
        if not os.path.exists(cls.SCREENSHOT_DIR):
            os.makedirs(cls.SCREENSHOT_DIR)
            
        # Khởi tạo trình duyệt
        cls.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        cls.driver.maximize_window()
        cls.driver.implicitly_wait(10)
        
        # Đăng nhập vào WordPress
        cls.login(cls)
    
    @classmethod
    def tearDownClass(cls):
        """Đóng trình duyệt sau khi hoàn thành tất cả các test"""
        cls.driver.quit()
    
    def login(self):
        """Đăng nhập vào trang quản trị WordPress"""
        login_url = f"{self.BASE_URL}{self.LOGIN_PATH}"
        self.driver.get(login_url)
        print(f"Đang truy cập trang đăng nhập: {login_url}")
        
        # Nhập username
        username_input = self.driver.find_element(By.ID, "user_login")
        username_input.clear()
        username_input.send_keys(self.USERNAME)
        
        # Nhập password
        password_input = self.driver.find_element(By.ID, "user_pass")
        password_input.clear()
        password_input.send_keys(self.PASSWORD)
        
        # Nhấn nút đăng nhập
        login_btn = self.driver.find_element(By.ID, "wp-submit")
        login_btn.click()
        
        # Chờ trang quản trị tải
        wait = WebDriverWait(self.driver, 20)
        try:
            wait.until(EC.presence_of_element_located((By.ID, "wpadminbar")))
            
            # Kiểm tra đăng nhập thành công
            if "Bảng tin" in self.driver.page_source or "Dashboard" in self.driver.page_source:
                print("✅ Đăng nhập thành công")
                return True
            else:
                print("❌ Đăng nhập thất bại: Không tìm thấy text Dashboard")
                self.take_screenshot("login_failed_no_dashboard")
                return False
        except TimeoutException:
            print("❌ Đăng nhập thất bại: Timeout khi chờ admin bar")
            self.take_screenshot("login_failed_timeout")
            return False
    
    def take_screenshot(self, test_name):
        """Chụp ảnh màn hình khi test thất bại"""
        # Tạo tên file ảnh chụp với timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{test_name}.png"
        filepath = os.path.join(self.SCREENSHOT_DIR, filename)
        
        # Chụp ảnh màn hình
        try:
            self.driver.save_screenshot(filepath)
            print(f"📸 Đã chụp ảnh màn hình: {filepath}")
            return filepath
        except Exception as e:
            print(f"❌ Không thể chụp ảnh màn hình: {str(e)}")
            return None
    
    def download_image_from_url(self, url):
        """Download image from URL and save it to a temporary file"""
        try:
            # Create a temporary file with .jpg extension
            temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
            temp_path = temp_file.name
            temp_file.close()
            
            # Download the image
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            with open(temp_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            
            print(f"✅ Đã tải ảnh thành công từ {url} vào {temp_path}")
            return temp_path
        except Exception as e:
            print(f"❌ Không thể tải ảnh từ {url}: {str(e)}")
            return None
            
    def step_demo(self, msg, delay=1.5):
        print(f"[DEMO] {msg}")
        time.sleep(delay)

    def test_01_create_new_course(self):
        """Test Case 1: Tạo khóa học mới"""
        try:
            # Bước 1: Truy cập trang quản trị khóa học
            courses_url = f"{self.BASE_URL}{self.COURSES_PATH}"
            self.driver.get(courses_url)
            self.step_demo(f"Truy cập trang quản trị khóa học: {courses_url}")
            
            # Chờ trang tải xong
            wait = WebDriverWait(self.driver, 15)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.wp-heading-inline, .page-title-action")))
            
            # Kiểm tra tiêu đề trang
            page_title = self.driver.find_element(By.CLASS_NAME, "wp-heading-inline").text
            self.assertTrue("Courses" in page_title or "Khóa học" in page_title, 
                            "Không thể điều hướng đến trang quản lý khóa học")
            print("✅ Đã điều hướng thành công đến trang quản lý khóa học")
            
            # Bước 2: Nhấn nút Add New để tạo khóa học mới
            add_new_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "a.page-title-action")))
            self.step_demo("Tìm thấy và chuẩn bị nhấn nút Add New để tạo khóa học mới")
            add_new_btn.click()
            self.step_demo("Đã nhấn nút Add New để tạo khóa học mới")
            
            # Chờ trang tải xong
            wait = WebDriverWait(self.driver, 15)
            wait.until(EC.presence_of_element_located((By.ID, "title")))
            print("Đã tải trang thêm khóa học mới")
            
            # Bước 3: Tạo tiêu đề khóa học với timestamp
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            course_title = f"Test course {timestamp}"
            
            # Bước 3: Nhập tiêu đề khóa học
            title_input = wait.until(EC.presence_of_element_located((By.ID, "title")))
            course_title = f"Test Course {datetime.datetime.now().strftime('%H%M%S')}"
            self.step_demo(f"Nhập tiêu đề khóa học: {course_title}")
            title_input.clear()
            title_input.send_keys(course_title)
            print(f"✅ Đã nhập tiêu đề khóa học: {course_title}")
            
            # Bước 4: Thêm mô tả khóa học
            # Chuyển đến iframe của trình soạn thảo nếu có
            try:
                # Nếu có iframe, chuyển đến iframe
                iframe = self.driver.find_element(By.ID, "content_ifr")
                self.driver.switch_to.frame(iframe)
                editor_body = self.driver.find_element(By.ID, "tinymce")
                editor_body.clear()
                editor_body.send_keys(f"This is an automated test description for {course_title}. Created by Selenium test.")
                # Chuyển về trang chính
                self.driver.switch_to.default_content()
            except NoSuchElementException:
                # Nếu không có iframe, sử dụng textarea trực tiếp
                content_area = self.driver.find_element(By.ID, "content")
                content_area.clear()
                content_area.send_keys(f"This is an automated test description for {course_title}. Created by Selenium test.")
            
            self.step_demo("Đã thêm mô tả khóa học")
            
            # Bước 5: Xuất bản khóa học
            # Đảm bảo không có cửa sổ modal nào đang mở
            try:
                modals = self.driver.find_elements(By.CSS_SELECTOR, ".media-modal")
                if modals:
                    close_button = self.driver.find_element(By.CSS_SELECTOR, ".media-modal-close")
                    close_button.click()
                    time.sleep(1)
            except:
                pass
            
            # Cuộn lên đầu trang để đảm bảo có thể nhìn thấy nút Publish
            self.driver.execute_script("window.scrollTo(0, 0);")
            self.step_demo("Cuộn lên đầu trang để chuẩn bị nhấn Publish")
            
            # Tìm và nhấn nút Publish
            publish_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "publish"))
            )
            self.step_demo("Tìm thấy nút Publish và chuẩn bị nhấn")
            publish_button.click()
            self.step_demo("Đã nhấn nút xuất bản khóa học")
            
            # Chờ thông báo xuất bản thành công
            wait = WebDriverWait(self.driver, 10)
            success_notice = wait.until(EC.presence_of_element_located((By.ID, "message")))
            
            # Kiểm tra thông báo thành công
            self.assertTrue("Post published" in success_notice.text or "Bài viết đã được xuất bản" in success_notice.text, 
                          "Xuất bản khóa học không thành công")
            print("✅ Đã xuất bản khóa học thành công")
            
            # Chụp ảnh màn hình để xác nhận
            self.step_demo("Chụp ảnh màn hình xác nhận đã xuất bản thành công")
            self.take_screenshot("course_published")
            
            # Bước 6: Xem khóa học đã xuất bản
            view_post_link = self.driver.find_element(By.CSS_SELECTOR, "#message a")
            view_post_url = view_post_link.get_attribute("href")
            self.step_demo(f"Nhấn vào liên kết xem khóa học: {view_post_url}")
            view_post_link.click()
            
            # Chờ trang khóa học tải xong
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "body.single-lp_course")))
            
            # Kiểm tra tiêu đề khóa học trên trang
            page_title = self.driver.title
            self.assertTrue(course_title in page_title, f"Tiêu đề khóa học không xuất hiện trên trang: {page_title}")
            print(f"✅ Đã xem khóa học thành công: {page_title}")
            
            # Chụp ảnh màn hình cuối cùng
            self.step_demo("Chụp ảnh màn hình cuối cùng xác nhận xem được khóa học")
            self.take_screenshot("view_course")
            
        except Exception as e:
            self.take_screenshot("create_new_course_failed")
            self.fail(f"Tạo khóa học mới thất bại: {str(e)}")
