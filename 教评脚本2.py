import time
import threading
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class TeachingEvaluationBot:
    def __init__(self):
        # 设置Chrome选项
        self.chrome_options = Options()
        # 忽略SSL证书错误
        self.chrome_options.add_argument('--ignore-certificate-errors')
        self.chrome_options.add_argument('--ignore-ssl-errors')
        # 可选：无头模式，如果需要可视化可以注释掉
        # self.chrome_options.add_argument('--headless')

        self.main_driver = webdriver.Chrome(options=self.chrome_options)
        self.wait = WebDriverWait(self.main_driver, 10)
        self.course_dict = {}
        self.student_id = ""
        self.password = ""

        # 并行执行相关变量
        self.thread_pool = ThreadPoolExecutor(max_workers=10)  # 增加并发数
        self.completed_evaluations = 0  # 完成的评估数量
        self.lock = threading.Lock()  # 线程锁

    def login_main(self):
        """主会话登录系统"""
        print("正在打开网站...")
        self.main_driver.get("http://jwcxk2.aufe.edu.cn/index.jsp")
        try:
            # 等待用户名输入框
            username_input = self.wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            password_input = self.main_driver.find_element(By.ID, "passwordOld")

            # 输入用户名和密码
            username_input.clear()
            username_input.send_keys(self.student_id)
            password_input.clear()
            password_input.send_keys(self.password)
            print("已输入用户名和密码")

            # 点击登录按钮
            login_btn = self.main_driver.find_element(By.ID, "J-login-btn")
            login_btn.click()
            print("已点击登录按钮")

            # 等待登录完成
            time.sleep(3)
            return True
        except Exception as e:
            print(f"登录过程中出错: {e}")
            return False

    def login_evaluation_session(self, driver, session_num):
        """评估会话登录系统"""
        print(f"正在为评估会话 {session_num} 登录...")
        driver.get("http://jwcxk2.aufe.edu.cn/index.jsp")
        try:
            # 等待用户名输入框
            wait = WebDriverWait(driver, 10)
            username_input = wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            password_input = driver.find_element(By.ID, "passwordOld")

            # 输入用户名和密码
            username_input.clear()
            username_input.send_keys(self.student_id)
            password_input.clear()
            password_input.send_keys(self.password)
            print(f"评估会话 {session_num}: 已输入用户名和密码")

            # 点击登录按钮
            login_btn = driver.find_element(By.ID, "J-login-btn")
            login_btn.click()
            print(f"评估会话 {session_num}: 已点击登录按钮")

            # 等待登录完成
            time.sleep(3)
            return True
        except Exception as e:
            print(f"评估会话 {session_num} 登录过程中出错: {e}")
            return False

    def navigate_to_evaluation_main(self):
        """主会话导航到教学评估页面"""
        try:
            # 点击教学评估菜单
            evaluation_menu = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//li[contains(@class, 'click-item') and contains(text(), '教学评估')]"))
            )
            evaluation_menu.click()
            print("已点击教学评估菜单")

            # 等待页面跳转
            time.sleep(3)
            return True
        except Exception as e:
            print(f"导航到评估页面时出错: {e}")
            return False

    def navigate_to_evaluation_session(self, driver, session_num):
        """评估会话导航到教学评估页面"""
        try:
            # 点击教学评估菜单
            wait = WebDriverWait(driver, 10)
            evaluation_menu = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//li[contains(@class, 'click-item') and contains(text(), '教学评估')]"))
            )
            evaluation_menu.click()
            print(f"评估会话 {session_num}: 已点击教学评估菜单")

            # 等待页面跳转
            time.sleep(3)
            return True
        except Exception as e:
            print(f"评估会话 {session_num} 导航到评估页面时出错: {e}")
            return False

    def parse_course_table(self):
        """解析课程表格并创建课程字典"""
        try:
            # 等待表格加载
            table = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//*[@id='page_div']/table"))
            )

            # 获取所有课程行
            course_rows = self.main_driver.find_elements(By.XPATH, "//tbody[@id='jxpgtbody']/tr")
            print(f"\n找到 {len(course_rows)} 门需要评估的课程:")
            print("-" * 80)
            print(f"{'序号':<4} {'课程名称':<20} {'教师':<10} {'评估内容':<20} {'状态':<8}")
            print("-" * 80)

            # 解析每门课程信息
            for i, row in enumerate(course_rows, 1):
                try:
                    # 获取课程信息
                    course_name = row.find_element(By.XPATH, "./td[4]").text  # 评估内容列
                    teacher_name = row.find_element(By.XPATH, "./td[3]").text  # 被评人列
                    status = row.find_element(By.XPATH, "./td[5]").text.strip()  # 是否已评估列

                    # 获取评估按钮
                    eval_button = row.find_element(By.XPATH, "./td[1]/button")

                    # 添加到课程字典
                    course_key = f"{course_name}_{teacher_name}"
                    self.course_dict[course_key] = {
                        'index': i,
                        'course_name': course_name,
                        'teacher': teacher_name,
                        'status': status,
                        'button': eval_button,
                        'evaluated': False,
                        'evaluation_completed': False,  # 标记评估是否已完成
                        'submitted': False  # 标记是否已提交
                    }

                    print(f"{i:<4} {course_name:<20} {teacher_name:<10} {course_name:<20} {status:<8}")
                except Exception as e:
                    print(f"解析第 {i} 门课程时出错: {e}")
                    continue

            print("-" * 80)
            return True
        except Exception as e:
            print(f"解析课程表格时出错: {e}")
            return False

    def evaluate_single_course(self, course_info, session_num):
        """单个课程的完整评估流程"""
        driver = None
        try:
            print(f"\n评估会话 {session_num}: 开始处理课程 {course_info['course_name']}")

            # 创建新的driver
            driver = webdriver.Chrome(options=self.chrome_options)

            # 在新会话中登录
            if not self.login_evaluation_session(driver, session_num):
                print(f"评估会话 {session_num}: 登录失败")
                return

            # 导航到评估页面
            if not self.navigate_to_evaluation_session(driver, session_num):
                print(f"评估会话 {session_num}: 导航到评估页面失败")
                return

            # 直接访问评估页面URL
            driver.get("http://jwcxk2.aufe.edu.cn/student/teachingEvaluation/evaluation/index")
            time.sleep(3)

            # 点击对应的评估按钮
            course_rows = driver.find_elements(By.XPATH, "//tbody[@id='jxpgtbody']/tr")
            button_clicked = False

            for row in course_rows:
                try:
                    row_course_name = row.find_element(By.XPATH, "./td[4]").text
                    row_teacher_name = row.find_element(By.XPATH, "./td[3]").text
                    if (row_course_name == course_info['course_name'] and
                            row_teacher_name == course_info['teacher']):
                        eval_button = row.find_element(By.XPATH, "./td[1]/button")
                        eval_button.click()
                        print(f"评估会话 {session_num}: 已点击课程 {course_info['course_name']} 的评估按钮")
                        time.sleep(3)
                        button_clicked = True
                        break
                except Exception:
                    continue

            if not button_clicked:
                print(f"评估会话 {session_num}: 未找到课程 {course_info['course_name']} 的评估按钮")
                return

            # 填写评估表单
            print(f"评估会话 {session_num}: 开始填写课程 {course_info['course_name']} 的评估表单...")

            # 选择满意度选项
            if not self.select_satisfaction(driver, session_num):
                print(f"评估会话 {session_num}: 选择满意度选项失败")
                return

            # 填写评价文本
            if not self.fill_evaluation_text(driver, session_num):
                print(f"评估会话 {session_num}: 填写评价文本失败")
                return

            print(f"评估会话 {session_num}: ✓ 已完成课程 {course_info['course_name']} 的表单填写")

            # 标记评估完成
            with self.lock:
                course_info['evaluation_completed'] = True
                self.completed_evaluations += 1

            # 记录填写完成时间
            completion_time = time.time()
            print(
                f"评估会话 {session_num}: 表单填写完成时间: {time.strftime('%H:%M:%S', time.localtime(completion_time))}")

            # 独立等待120秒
            print(f"评估会话 {session_num}: 开始独立等待120秒...")
            self.wait_with_progress_independent(session_num, 120)

            # 提交评估
            print(f"评估会话 {session_num}: 正在提交课程 {course_info['course_name']} 的评估...")
            if self.submit_evaluation(driver, session_num):
                with self.lock:
                    course_info['evaluated'] = True
                    course_info['submitted'] = True
                print(f"评估会话 {session_num}: ✓ 已成功提交课程 {course_info['course_name']} 的评估")
            else:
                print(f"评估会话 {session_num}: ✗ 提交课程 {course_info['course_name']} 的评估失败")

        except Exception as e:
            print(f"评估会话 {session_num} 处理课程 {course_info['course_name']} 时出错: {e}")
        finally:
            # 关闭driver
            if driver:
                try:
                    driver.quit()
                    print(f"评估会话 {session_num}: 已关闭浏览器")
                except:
                    pass

    def wait_with_progress_independent(self, session_num, wait_time):
        """独立会话的带进度显示的等待"""
        start_time = time.time()
        while time.time() - start_time < wait_time:
            elapsed = time.time() - start_time
            remaining = wait_time - elapsed
            if remaining % 30 == 0 or remaining <= 10:
                print(f"评估会话 {session_num}: 剩余等待时间: {int(remaining)} 秒")
            time.sleep(1)
        print(f"评估会话 {session_num}: 等待完成，准备提交")

    def evaluate_all_courses_independent_timing(self):
        """独立计时的并行评估"""
        print("\n开始独立计时的并行评估...")

        # 获取需要评估的课程列表
        courses_to_evaluate = [course for course in self.course_dict.values()
                               if course['status'] == '否' and not course['evaluated']]
        print(f"需要评估的课程数量: {len(courses_to_evaluate)}")

        if not courses_to_evaluate:
            print("没有需要评估的课程")
            return

        # 使用线程池并行处理所有课程
        futures = []
        for i, course_info in enumerate(courses_to_evaluate):
            # 每6秒创建一个新的线程
            if i > 0:
                time.sleep(6)
                print(f"等待6秒后创建下一个评估会话... ({i + 1}/{len(courses_to_evaluate)})")

            # 提交任务到线程池
            future = self.thread_pool.submit(self.evaluate_single_course, course_info, i + 1)
            futures.append(future)
            print(f"已创建评估会话 {i + 1} 用于课程 {course_info['course_name']}")

        # 等待所有任务完成
        print("\n所有评估会话已创建，等待所有评估完成...")
        for future in futures:
            future.result()

        # 打印评估总结
        self.print_evaluation_summary()

    def select_satisfaction(self, driver, session_num):
        """选择满意度选项"""
        try:
            # 等待页面完全加载
            time.sleep(3)

            # 查找所有单选按钮组
            radio_inputs = driver.find_elements(By.XPATH, "//input[@type='radio']")

            # 按name属性分组
            radio_groups = {}
            for radio in radio_inputs:
                name = radio.get_attribute('name')
                if name not in radio_groups:
                    radio_groups[name] = []
                radio_groups[name].append(radio)

            print(f"评估会话 {session_num}: 找到 {len(radio_groups)} 个问题组")

            # 对每个组选择最满意的选项
            for name, radios in radio_groups.items():
                best_option = None
                best_option_radio = None

                for radio in radios:
                    try:
                        # 查找标签
                        label = radio.find_element(By.XPATH,
                                                   "./following-sibling::span[contains(@class, 'lbl')]/following-sibling::span")
                        label_text = label.text

                        # 如果是"非常满意"，直接选择
                        if "非常满意" in label_text:
                            best_option = "非常满意"
                            best_option_radio = radio
                            break
                        # 如果是"满意"且还没有找到更好的选项
                        elif "满意" in label_text and "非常" not in label_text and best_option != "非常满意":
                            best_option = "满意"
                            best_option_radio = radio
                    except:
                        continue

                # 选择最佳选项
                if best_option_radio:
                    driver.execute_script("arguments[0].click();", best_option_radio)
                    # print(f"评估会话 {session_num}: 组 {name}: 已选择 {best_option}")
                else:
                    # 如果没有找到满意的选项，选择第一个
                    driver.execute_script("arguments[0].click();", radios[0])
                    # print(f"评估会话 {session_num}: 组 {name}: 已选择第一个选项")

            # 添加验证步骤
            # self.verify_selections(driver, session_num)
            # print(f"评估会话 {session_num}: 所有满意度选项已选择")
            return True

        except Exception as e:
            print(f"评估会话 {session_num} 选择满意度选项时出错: {e}")
            return False

    def verify_selections(self, driver, session_num):
        """验证选择结果"""
        try:
            # 查找所有单选按钮组
            radio_groups = driver.find_elements(By.XPATH, "//input[@type='radio']")
            group_names = set()
            for radio in radio_groups:
                name = radio.get_attribute('name')
                if name:
                    group_names.add(name)

            # 检查每个组是否有选中的选项
            selected_count = 0
            for name in group_names:
                checked_radio = driver.find_elements(By.XPATH,
                                                     f"//input[@type='radio' and @name='{name}' and @checked]")
                if checked_radio:
                    selected_count += 1
                else:
                    print(f"评估会话 {session_num}: 警告: 组 {name} 没有选中的选项")

            print(f"评估会话 {session_num}: 验证: 已选中 {selected_count}/{len(group_names)} 个问题的选项")
        except Exception as e:
            print(f"评估会话 {session_num} 验证选择结果时出错: {e}")

    def fill_evaluation_text(self, driver, session_num):
        """填写评价文本"""
        try:
            # 查找评价文本框
            textarea = driver.find_element(By.XPATH, "//textarea[@name='zgpj']")
            textarea.clear()
            textarea.send_keys("老师教学认真负责，课程内容充实，受益匪浅。")
            print(f"评估会话 {session_num}: 已填写评价文本")
            return True
        except Exception as e:
            print(f"评估会话 {session_num} 填写评价文本时出错: {e}")
            return False

    def submit_evaluation(self, driver, session_num):
        """提交评估"""
        try:
            submit_btn = driver.find_element(By.ID, "buttonSubmit")
            submit_btn.click()
            print(f"评估会话 {session_num}: 已点击提交按钮")

            # 等待确认对话框出现
            time.sleep(2)

            # 处理确认对话框
            if self.handle_confirmation_dialog(driver, session_num):
                # 等待提交完成
                time.sleep(3)
                return True
            else:
                return False
        except Exception as e:
            print(f"评估会话 {session_num} 提交评估时出错: {e}")
            return False

    def handle_confirmation_dialog(self, driver, session_num):
        """处理确认对话框"""
        try:
            # 等待对话框出现
            wait = WebDriverWait(driver, 5)
            dialog = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "layui-layer-dialog"))
            )

            # 获取对话框文本内容
            content = dialog.find_element(By.CLASS_NAME, "layui-layer-content").text
            print(f"评估会话 {session_num}: 对话框内容: {content}")

            # 点击"是"按钮
            confirm_btn = dialog.find_element(By.CLASS_NAME, "layui-layer-btn0")
            confirm_btn.click()
            print(f"评估会话 {session_num}: 已点击确认按钮")

            # 等待对话框关闭
            time.sleep(2)
            return True
        except TimeoutException:
            print(f"评估会话 {session_num}: 未找到确认对话框，可能已经自动处理")
            return True
        except Exception as e:
            print(f"评估会话 {session_num} 处理确认对话框时出错: {e}")
            return False

    def print_evaluation_summary(self):
        """打印评估总结"""
        evaluated_count = sum(1 for course in self.course_dict.values() if course['evaluated'])
        total_courses = len(self.course_dict)
        print(f"\n评估完成! 总共评估了 {evaluated_count}/{total_courses} 门课程")
        print("\n评估总结:")
        for course_key, course_info in self.course_dict.items():
            status = "✓ 已评估" if course_info['evaluated'] else "✗ 未评估"
            print(
                f"{course_info['index']:>2}. {course_info['course_name']:<20} - {course_info['teacher']:<10} [{status}]")

    def close_all_sessions(self):
        """关闭所有会话"""
        print("\n正在关闭所有会话...")

        # 关闭线程池
        self.thread_pool.shutdown(wait=True)

        # 关闭主会话
        try:
            self.main_driver.quit()
        except:
            pass

        print("所有会话已关闭")

    def run(self, student_id, password):
        """运行主流程"""
        start_time = time.time()
        self.student_id = student_id
        self.password = password

        try:
            # 1. 主会话登录
            if not self.login_main():
                print("主会话登录失败，程序退出")
                return

            # 2. 主会话导航到评估页面
            if not self.navigate_to_evaluation_main():
                print("主会话导航到评估页面失败")
                return

            # 3. 解析课程表格
            if not self.parse_course_table():
                print("解析课程表格失败")
                return

            # 4. 独立计时的并行评估
            self.evaluate_all_courses_independent_timing()

        except Exception as e:
            print(f"程序运行出错: {e}")
        finally:
            # 关闭所有浏览器会话
            end_time = time.time()
            run_time = end_time - start_time
            print(f"\n程序总运行时间: {run_time:.2f} 秒")
            self.close_all_sessions()


# 使用示例
if __name__ == "__main__":
    # 在这里输入你的学号和密码
    STUDENT_ID = ""  # 请替换为你的学号
    PASSWORD = ""  # 请替换为你的密码

    if not STUDENT_ID or not PASSWORD:
        print("请先在代码内填写你的学号和密码")
    else:
        bot = TeachingEvaluationBot()
        bot.run(STUDENT_ID, PASSWORD)

# 这是一个针对安徽财经大学教学评估系统的自动化脚本，可以自动完成所有未评估课程的评价填写和提交。
#
# 功能特点
# ✅ 并行处理：支持多课程同时评估，大幅缩短总耗时
# ⏱️ 独立计时：每个课程评估会话独立等待2分钟，互不干扰
# 🎯 智能选择：自动选择"非常满意"选项
# 📝 自动填写：预设文本1项，自动填写评语
# 🔒 安全可靠：使用官方浏览器驱动，模拟真实操作
# 📊 进度显示：实时显示评估进度和状态

# 系统要求
# Python 3.12+
# Google Chrome 浏览器
# ChromeDriver 驱动

# 安装步骤
# 1. 安装Selenium包：在 cmd 中使用 pip install selenium
# 2. 下载ChromeDriver：访问https://googlechromelabs.github.io/chrome-for-testing/
# 下载与你的Chrome浏览器版本完全匹配的ChromeDriver
# 解压后将 chromedriver.exe 放到 python.exe 同一目录下
# 3. 配置账号信息
# 在 main 函数中修改以下变量：STUDENT_ID 、 PASSWORD

# 使用方法
# 完成上述安装步骤后直接运行。

# 注意事项
# ⚠️ 请勿在评估期间进行其他操作，以免干扰脚本运行
# ⚠️ 确保校园网连接稳定，避免评估过程中断
# ⚠️ ChromeDriver版本必须与Chrome浏览器版本完全匹配
# ⚠️ 脚本仅用于学习交流，请合理使用

# 免责声明
# 本脚本仅供学习和研究使用，请遵守学校相关规定，合理使用自动化工具。使用者需对使用本脚本产生的一切后果负责。