from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# 替换为你的登录信息
phone_number = '15666820414'
verification_code = 'your_verification_code'

# 设置WebDriver路径
driver = webdriver.Chrome()  # 确保你的ChromeDriver路径已经设置在系统PATH中

try:
    # 打开网页
    driver.get("https://expert.kunlungpt.cn/")

    # 等待手机号输入框元素加载完成
    phone_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "phone"))  # 假设手机号输入框的name属性为"phone"
    )

    # 输入手机号
    phone_input.send_keys(phone_number)

    # 点击获取验证码按钮，这里需要根据实际的元素属性来定位
    send_code_button = driver.find_element(By.XPATH, '//button[@type="submit"]')  # 假设获取验证码按钮的XPath
    send_code_button.click()

    # 等待验证码输入框元素加载完成
    code_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "code"))  # 假设验证码输入框的name属性为"code"
    )

    # 输入验证码
    code_input.send_keys(verification_code)

    # 点击登录按钮，这里需要根据实际的元素属性来定位
    login_button = driver.find_element(By.XPATH, '//button[@type="submit"]')  # 假设登录按钮的XPath
    login_button.click()

    # 可以添加一些代码来验证是否登录成功，例如检查某个元素是否存在

finally:
    # 关闭浏览器
    driver.quit()