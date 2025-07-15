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
from selenium.webdriver.common.action_chains import ActionChains

class LearnPressCoursesPerPageTest(unittest.TestCase):
    BASE_URL = "http://wp.local"
    LOGIN_PATH = "/wp-login.php"
    ADMIN_PATH = "/wp-admin"
    LP_COURSES_PATH = "/wp-admin/edit.php?post_type=lp_course"
    SETTINGS_PATH = "/admin.php?page=learn-press-settings"
    COURSES_PATH = "/courses/"
    THEME_NAME = "Twenty Twenty-One"

    def activate_theme(self, theme_name=None):
        """Tự động active theme cho WordPress qua giao diện admin."""
        if theme_name is None:
            theme_name = self.THEME_NAME
        self.step_demo(f"Bắt đầu kiểm tra và kích hoạt theme: {theme_name}")
        # Truy cập trang quản lý theme
        themes_url = f"{self.BASE_URL}/wp-admin/themes.php"
        self.driver.get(themes_url)
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, "wpbody-content")))
        time.sleep(1)
        # Kiểm tra theme đã active chưa
        try:
            active_theme = self.driver.find_element(By.CSS_SELECTOR, "div.theme.active")
            active_theme_name = active_theme.find_element(By.CLASS_NAME, "theme-name").text.strip()
            if theme_name.lower() in active_theme_name.lower():
                self.step_demo(f"Theme '{theme_name}' đã được kích hoạt.")
                return
        except Exception:
            pass
        # Nếu chưa active thì tìm theme và click Activate
        themes = self.driver.find_elements(By.CSS_SELECTOR, "div.theme")
        found = False
        for theme in themes:
            try:
                name = theme.find_element(By.CLASS_NAME, "theme-name").text.strip()
                if theme_name.lower() in name.lower():
                    found = True
                    # Nếu có nút Activate hoặc Kích hoạt thì click
                    try:
                        activate_btn = theme.find_element(By.CSS_SELECTOR, "a.activate, button.activate")
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", activate_btn)
                        time.sleep(0.5)
                        activate_btn.click()
                        self.step_demo(f"Đã nhấn nút Activate cho theme '{theme_name}'")
                        # Đợi theme được active
                        wait.until(lambda d: "active" in theme.get_attribute("class"))
                        self.step_demo(f"Theme '{theme_name}' đã được kích hoạt thành công!")
                        return
                    except Exception as e:
                        self.take_screenshot("cannot_activate_theme")
                        raise Exception(f"Không thể kích hoạt theme: {theme_name}. Lỗi: {str(e)}")
            except Exception:
                continue
        if not found:
            self.take_screenshot("theme_not_found")
            raise Exception(f"Không tìm thấy theme: {theme_name} trong danh sách themes.")
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

    def step_demo(self, msg, delay=1.5):
        """In thông báo và tạm dừng để demo"""
        print(f"[DEMO] {msg}")
        time.sleep(delay)

    def test_01_courses_per_page_setting(self):
        """Test Case: Kiểm tra cài đặt "Courses per page" của LearnPress"""
        try:
            # Đăng nhập vào WordPress admin
            self.login()
            self.step_demo("Đã đăng nhập thành công vào trang quản trị")
            # Kích hoạt theme Twenty Twenty-One trước khi test
            self.activate_theme("Twenty Twenty-One")
            
            # Truy cập trang LearnPress Courses trước
            lp_courses_url = f"{self.BASE_URL}{self.LP_COURSES_PATH}"
            self.driver.get(lp_courses_url)
            self.step_demo(f"Truy cập trang LearnPress Courses: {lp_courses_url}")
            
            # Chờ trang courses admin tải xong
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "body.post-type-lp_course")))
            self.take_screenshot("learnpress_courses_admin")
            
            # Tìm và click vào menu Settings
            try:
                # Tìm link Settings trong menu LearnPress
                settings_link = self.driver.find_element(By.CSS_SELECTOR, "a[href='admin.php?page=learn-press-settings']")
                self.step_demo("Tìm thấy link Settings, chuẩn bị nhấn vào")
            except NoSuchElementException:
                # Tìm theo text
                links = self.driver.find_elements(By.TAG_NAME, "a")
                settings_link = None
                for link in links:
                    if "Settings" in link.text and "learn-press" in link.get_attribute("href"):
                        settings_link = link
                        break
                if not settings_link:
                    self.take_screenshot("cannot_find_settings_link")
                    raise Exception("Không thể tìm thấy link Settings")
            
            # Click vào link Settings
            settings_link.click()
            self.step_demo("Đã nhấn vào link Settings")
            
            # Chờ trang settings tải xong
            wait = WebDriverWait(self.driver, 10)
            self.step_demo(f"Đã chuyển đến trang LearnPress Settings")
            self.take_screenshot("learnpress_settings_page")
            
            # Chờ trang settings tải xong (thử nhiều selector khác nhau)
            wait = WebDriverWait(self.driver, 10)
            try:
                wait.until(lambda driver: any([
                    len(driver.find_elements(By.CSS_SELECTOR, "div.learn-press-settings-wrap")) > 0,
                    len(driver.find_elements(By.CSS_SELECTOR, "form.learn-press-settings")) > 0,
                    len(driver.find_elements(By.CSS_SELECTOR, "#learn-press-settings")) > 0,
                    len(driver.find_elements(By.CSS_SELECTOR, ".learn-press-settings-page")) > 0
                ]))
                self.step_demo("Trang LearnPress Settings đã tải xong")
                self.take_screenshot("learnpress_settings_loaded")
            except TimeoutException:
                print("Không tìm thấy trang settings với các selector thông thường, thử tìm tab Courses trực tiếp")
            
            # Click vào tab Courses - thử nhiều cách khác nhau
            try:
                # Cách 1: Tìm theo CSS selector
                courses_tab = self.driver.find_element(By.CSS_SELECTOR, "a.nav-tab[href*='tab=courses']")
                self.step_demo("Tìm thấy tab Courses (cách 1), chuẩn bị nhấn vào")
            except NoSuchElementException:
                try:
                    # Cách 2: Tìm theo text
                    tabs = self.driver.find_elements(By.CSS_SELECTOR, "a.nav-tab")
                    courses_tab = None
                    for tab in tabs:
                        if "Courses" in tab.text:
                            courses_tab = tab
                            break
                    if courses_tab:
                        self.step_demo("Tìm thấy tab Courses (cách 2), chuẩn bị nhấn vào")
                    else:
                        raise NoSuchElementException("Không tìm thấy tab Courses")
                except NoSuchElementException:
                    # Cách 3: Tìm theo href chứa courses
                    links = self.driver.find_elements(By.TAG_NAME, "a")
                    courses_tab = None
                    for link in links:
                        href = link.get_attribute("href")
                        if href and "tab=courses" in href:
                            courses_tab = link
                            break
                    if courses_tab:
                        self.step_demo("Tìm thấy tab Courses (cách 3), chuẩn bị nhấn vào")
                    else:
                        self.take_screenshot("cannot_find_courses_tab")
                        raise Exception("Không thể tìm thấy tab Courses bằng bất kỳ phương pháp nào")
            
            # Click vào tab Courses
            courses_tab.click()
            self.step_demo("Đã nhấn vào tab Courses")
            self.take_screenshot("courses_tab_clicked")
            
            # Thử với giá trị 1
            self.check_courses_per_page_value(1)
            
            # Thử với giá trị 4
            self.check_courses_per_page_value(4)
            
        except Exception as e:
            self.take_screenshot("courses_per_page_test_failed")
            self.fail(f"Test cài đặt Courses per page thất bại: {str(e)}")

    def check_courses_per_page_value(self, value):
        """Kiểm tra cài đặt Courses per page với một giá trị cụ thể"""
        try:
            # Tìm input field "Courses per page"
            try:
                self.driver.execute_script("window.scrollBy(0, 300);")
                time.sleep(1)
                courses_per_page_input = self.driver.find_element(By.ID, "learn_press_archive_course_limit")
                self.step_demo("Tìm thấy input field theo ID")
            except NoSuchElementException:
                courses_per_page_input = self.driver.find_element(By.NAME, "learn_press_archive_course_limit")
                self.step_demo("Tìm thấy input field theo name attribute")
            self.take_screenshot(f"before_change_value_{value}")
            courses_per_page_input.clear()
            courses_per_page_input.send_keys(str(value))
            self.step_demo(f"Đã nhập giá trị {value} vào trường Courses per page")
            # Nhấn nút Save settings (không cần kiểm tra reload hay thông báo thành công)
            try:
                save_button = self.driver.find_element(By.CSS_SELECTOR, "p.lp-admin-settings-buttons > button.button.button-primary")
            except NoSuchElementException:
                buttons = self.driver.find_elements(By.TAG_NAME, "button")
                save_button = None
                for button in buttons:
                    if "Save settings" in button.text:
                        save_button = button
                        break
                if not save_button:
                    self.take_screenshot("cannot_find_save_button")
                    raise Exception("Không thể tìm thấy nút Save settings")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", save_button)
            time.sleep(1)
            save_button.click()
            self.step_demo("Đã nhấn nút Save settings (không kiểm tra reload hay thông báo thành công)")
            
            # Truy cập trang /courses/ để kiểm tra
            courses_url = f"{self.BASE_URL}{self.COURSES_PATH}"
            self.driver.get(courses_url)
            self.step_demo(f"Truy cập trang danh sách khóa học: {courses_url}")
            
            # Chờ trang courses tải xong
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "ul.learn-press-courses")))
            course_list = self.driver.find_element(By.CSS_SELECTOR, "ul.learn-press-courses")
            course_items = course_list.find_elements(By.TAG_NAME, "li")
            course_count = len(course_items)
            # In ra HTML của danh sách khóa học để debug
            print(f"HTML của danh sách khóa học:\n{course_list.get_attribute('outerHTML')}")
            
            # Chụp ảnh màn hình kết quả
            self.take_screenshot(f"courses_per_page_{value}")
            
            # Kiểm tra số lượng khóa học hiển thị có đúng với giá trị đã cài đặt không
            print(f"Số lượng khóa học hiển thị: {course_count}, Giá trị cài đặt: {value}")
            
            if course_count == value:
                print(f"✅ Test PASS: Số lượng khóa học hiển thị ({course_count}) đúng với giá trị cài đặt ({value})")
            else:
                print(f"❌ Test FAILED: Số lượng khóa học hiển thị ({course_count}) không khớp với giá trị cài đặt ({value})")
                self.fail(f"Số lượng khóa học hiển thị ({course_count}) không khớp với giá trị cài đặt ({value})")
            
            # Quay lại trang cài đặt để thử giá trị tiếp theo
            settings_url = f"{self.BASE_URL}{self.SETTINGS_PATH}&tab=courses"
            self.driver.get(settings_url)
            self.step_demo("Quay lại trang cài đặt LearnPress")
            
        except Exception as e:
            self.take_screenshot(f"courses_per_page_{value}_failed")
            self.fail(f"Kiểm tra với giá trị {value} thất bại: {str(e)}")

if __name__ == "__main__":
    unittest.main()
