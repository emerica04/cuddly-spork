这是一个针对安徽财经大学教务系统的教学评估自动化脚本，可以自动完成所有未评估课程的评价填写和提交。喜欢就点个星星吧。

# 功能特点

✅ 并行处理：支持多课程同时评估，大幅缩短总耗时

⏱️ 独立计时：每个课程评估会话独立等待2分钟，互不干扰

🎯 自动选择：仅仅选择"非常满意"选项，你好我好大家好

📝 自动填写：预设文本1项，自动填写评语

🔒 安全可靠：使用官方浏览器驱动，模拟真实操作

📊 进度显示：实时显示评估进度和状态

# 系统要求

- Python 3.12+
- Google Chrome 浏览器
- ChromeDriver 驱动
- VS Code、PyCharm 或其他 IDE

# 安装步骤

1. 为 Python 安装 Selenium 包：在 cmd 中使用 `pip install selenium`
2. 下载 ChromeDriver：访问[友情链接](https://googlechromelabs.github.io/chrome-for-testing/)，下载与你的 Chrome 浏览器版本完全匹配的 ChromeDriver 。
3. 将下载好的 ChromeDriver 解压后将 chromedriver.exe 放到 python.exe 同一目录下
4. 下载 `教评脚本2.py`

# 使用方法

1. 确保前面的安装步骤已就位
2. 配置账号信息：在 `教评脚本2.py` 末尾的 main 函数中修改以下变量：`STUDENT_ID` 、`PASSWORD`

# 注意事项

⚠️ 请勿在评估期间进行其他操作，以免干扰脚本运行

⚠️ 确保校园网连接稳定，避免评估过程中断

⚠️ ChromeDriver版本必须与Chrome浏览器版本完全匹配

⚠️ 脚本仅用于学习交流，请合理使用

# 使用案例

室友有19门课，用时5分半就全部搞定

# 免责声明
本脚本仅供学习和研究使用，请遵守学校相关规定，合理使用自动化工具。使用者需对使用本脚本产生的一切后果负责。
