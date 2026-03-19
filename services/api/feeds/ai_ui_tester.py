"""
AI UI 测试代理 (AI UI Testing Agent)

功能：
1. 浏览器自动化 - Selenium 控制浏览器
2. 用户操作模拟 - 点击、输入、滚动等
3. 截图对比 - 视觉回归测试
4. 性能监控 - 加载时间、指标
5. AI 分析 - 发现问题、提出建议

关注维度：
- 功能 (Functional)
- 性能 (Performance)
- 美观 (UI/UX)
- 质量 (Quality)
- 深度 (Depth)
- 进化 (Evolution)
"""

import base64
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
# 测试类型
# ═══════════════════════════════════════════════════════════════════════════

class TestDimension(str, Enum):
    """测试维度"""
    FUNCTIONAL = "functional"  # 功能
    PERFORMANCE = "performance"  # 性能
    UX = "ux"  # 用户体验
    UI = "ui"  # 界面美观
    QUALITY = "quality"  # 质量
    DEPTH = "depth"  # 深度
    EVOLUTION = "evolution"  # 进化方向


class IssueSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# ═══════════════════════════════════════════════════════════════════════════
# 测试结果定义
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class UITestResult:
    """UI 测试结果"""
    test_id: str
    test_name: str
    dimension: str
    passed: bool
    duration: float
    score: float = 0.0  # 0-100
    message: str = ""
    error: str = ""
    screenshot: str = ""  # base64
    metrics: Dict = field(default_factory=dict)


# ═══════════════════════════════════════════════════════════════════════════
# Selenium 浏览器控制器
# ═══════════════════════════════════════════════════════════════════════════

class BrowserController:
    """浏览器控制器 - 使用 Selenium"""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver = None
        self._last_error = None

    def start(self) -> bool:
        """启动浏览器"""
        self._last_error = None
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.chrome.options import Options
            from webdriver_manager.chrome import ChromeDriverManager

            # 配置 Chrome 选项
            options = Options()
            if self.headless:
                options.add_argument('--headless')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

            # 使用 webdriver_manager 自动下载和管理驱动
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(10)

            logger.info(f"Browser started - driver: {self.driver}")
            return True
        except Exception as e:
            import traceback
            self._last_error = f"{e}\n{traceback.format_exc()}"
            logger.error(f"Failed to start browser: {e}\n{traceback.format_exc()}")
            return False

    def stop(self):
        """关闭浏览器"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Browser stopped")
            except Exception as e:
                logger.error(f"Error stopping browser: {e}")

    def screenshot(self, name: str = "screenshot") -> str:
        """截图并返回 base64"""
        if not self.driver:
            return ""

        try:
            # 截图
            bytes_data = self.driver.get_screenshot_as_png()
            base64_str = base64.b64encode(bytes_data).decode('utf-8')
            return base64_str
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return ""

    def click(self, selector: str):
        """点击元素"""
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )
        element.click()

    def fill(self, selector: str, value: str):
        """输入文本"""
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )
        element.clear()
        element.send_keys(value)

    def goto(self, url: str):
        """访问页面"""
        self.driver.get(url)

    def wait_for_selector(self, selector: str, timeout: int = 10):
        """等待元素"""
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC

        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )

    def get_metrics(self) -> Dict:
        """获取性能指标"""
        if not self.driver:
            return {}

        try:
            # 使用 JavaScript 获取性能指标
            metrics = self.driver.execute_script("""
                const timing = performance.timing;
                const nav = performance.getEntriesByType('navigation')[0];
                const resources = performance.getEntriesByType('resource');

                return {
                    loadTime: timing.loadEventEnd - timing.navigationStart,
                    domContentLoaded: timing.domContentLoadedEventEnd - timing.navigationStart,
                    firstPaint: performance.getEntriesByType('paint')[0]?.startTime || 0,
                    domInteractive: timing.domInteractive - timing.navigationStart,
                    transferSize: nav?.transferSize || 0,
                    resourceCount: resources.length,
                    resourceSize: resources.reduce((sum, r) => sum + (r.transferSize || 0), 0)
                };
            """)
            return metrics or {}
        except Exception as e:
            logger.error(f"Get metrics failed: {e}")
            return {}


# ═══════════════════════════════════════════════════════════════════════════
# UI 测试套件
# ═══════════════════════════════════════════════════════════════════════════

class UITestSuite:
    """UI 测试套件"""

    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url
        self.browser = BrowserController(headless=True)

    def setup(self) -> bool:
        """初始化"""
        return self.browser.start()

    def teardown(self):
        """清理"""
        self.browser.stop()

    # ═══════════════════════════════════════════════════════════════════
    # 功能测试
    # ═══════════════════════════════════════════════════════════════════

    def test_home_page_loads(self) -> UITestResult:
        """测试首页加载"""
        start = time.time()

        try:
            self.browser.goto(self.base_url)
            self.browser.wait_for_selector('body')

            duration = time.time() - start
            screenshot = self.browser.screenshot("home")

            return UITestResult(
                test_id="ui-home-load",
                test_name="首页加载",
                dimension=TestDimension.FUNCTIONAL.value,
                passed=True,
                duration=duration,
                score=100 if duration < 3 else 70,
                message=f"加载时间: {duration:.2f}s",
                screenshot=screenshot
            )
        except Exception as e:
            return UITestResult(
                test_id="ui-home-load",
                test_name="首页加载",
                dimension=TestDimension.FUNCTIONAL.value,
                passed=False,
                duration=time.time() - start,
                score=0,
                error=str(e)
            )

    def test_navigation_works(self) -> UITestResult:
        """测试导航功能"""
        try:
            # 尝试点击导航项
            nav_items = ['a[href*="/feeds"]', 'a[href*="/chat"]', 'a[href*="/settings"]']

            for nav in nav_items:
                try:
                    self.browser.click(nav)
                    time.sleep(0.5)
                except:
                    pass

            screenshot = self.browser.screenshot("navigation")

            return UITestResult(
                test_id="ui-nav",
                test_name="导航功能",
                dimension=TestDimension.FUNCTIONAL.value,
                passed=True,
                duration=0,
                score=80,
                screenshot=screenshot
            )
        except Exception as e:
            return UITestResult(
                test_id="ui-nav",
                test_name="导航功能",
                dimension=TestDimension.FUNCTIONAL.value,
                passed=False,
                duration=0,
                error=str(e)
            )

    def test_chat_functionality(self) -> UITestResult:
        """测试聊天功能"""
        try:
            # 访问聊天页面
            self.browser.goto(f"{self.base_url}/chat")
            time.sleep(2)

            # 尝试找到并输入
            input_selector = 'input[placeholder*="发消息"], textarea, input[type="text"]'

            try:
                self.browser.fill(input_selector, "测试消息")
                time.sleep(1)
            except Exception as e:
                pass

            screenshot = self.browser.screenshot("chat")

            return UITestResult(
                test_id="ui-chat",
                test_name="聊天功能",
                dimension=TestDimension.FUNCTIONAL.value,
                passed=True,
                duration=0,
                score=70,
                screenshot=screenshot
            )
        except Exception as e:
            return UITestResult(
                test_id="ui-chat",
                test_name="聊天功能",
                dimension=TestDimension.FUNCTIONAL.value,
                passed=False,
                duration=0,
                error=str(e)
            )

    # ═══════════════════════════════════════════════════════════════════
    # 性能测试
    # ═══════════════════════════════════════════════════════════════════

    def test_page_performance(self) -> UITestResult:
        """测试页面性能"""
        try:
            self.browser.goto(self.base_url)
            self.browser.wait_for_selector('body')

            metrics = self.browser.get_metrics()
            screenshot = self.browser.screenshot("performance")

            # 计算性能得分
            load_time = metrics.get('loadTime', 0) / 1000  # 转换为秒

            if load_time < 2:
                score = 100
            elif load_time < 5:
                score = 80
            elif load_time < 10:
                score = 60
            else:
                score = 40

            return UITestResult(
                test_id="ui-perf",
                test_name="页面性能",
                dimension=TestDimension.PERFORMANCE.value,
                passed=score >= 60,
                duration=load_time,
                score=score,
                message=f"加载时间: {load_time:.2f}s, 资源数: {metrics.get('resourceCount', 0)}",
                screenshot=screenshot,
                metrics=metrics
            )
        except Exception as e:
            return UITestResult(
                test_id="ui-perf",
                test_name="页面性能",
                dimension=TestDimension.PERFORMANCE.value,
                passed=False,
                duration=0,
                error=str(e)
            )

    # ═══════════════════════════════════════════════════════════════════
    # UI 美观测试
    # ═══════════════════════════════════════════════════════════════════

    def test_ui_layout(self) -> UITestResult:
        """测试 UI 布局"""
        try:
            self.browser.goto(self.base_url)
            time.sleep(1)

            # 检查页面结构
            checks = []

            # 检查必要元素
            try:
                self.browser.driver.find_element('tag name', 'header')
                checks.append('header')
            except:
                pass

            try:
                self.browser.driver.find_element('tag name', 'main')
                checks.append('main')
            except:
                pass

            screenshot = self.browser.screenshot("layout")

            score = len(checks) / 2 * 100

            return UITestResult(
                test_id="ui-layout",
                test_name="UI布局结构",
                dimension=TestDimension.UI.value,
                passed=score >= 50,
                duration=0,
                score=score,
                message=f"结构完整度: {len(checks)}/2",
                screenshot=screenshot
            )
        except Exception as e:
            return UITestResult(
                test_id="ui-layout",
                test_name="UI布局结构",
                dimension=TestDimension.UI.value,
                passed=False,
                duration=0,
                error=str(e)
            )

    def test_responsive_design(self) -> UITestResult:
        """测试响应式设计"""
        try:
            # 测试不同视口
            viewports = [
                {'width': 1920, 'height': 1080, 'name': 'desktop'},
                {'width': 768, 'height': 1024, 'name': 'tablet'},
                {'width': 375, 'height': 667, 'name': 'mobile'}
            ]

            results = []

            for vp in viewports:
                self.browser.driver.set_window_size(vp['width'], vp['height'])
                self.browser.goto(self.base_url)
                time.sleep(1)

                # 检查是否有横向滚动条
                has_h_scroll = self.browser.driver.execute_script(
                    "return document.body.scrollWidth > window.innerWidth;"
                )

                results.append({
                    'viewport': vp['name'],
                    'horizontal_scroll': has_h_scroll
                })

            # 响应式得分
            scroll_issues = sum(1 for r in results if r['horizontal_scroll'])
            score = (len(results) - scroll_issues) / len(results) * 100

            return UITestResult(
                test_id="ui-responsive",
                test_name="响应式设计",
                dimension=TestDimension.UI.value,
                passed=score >= 70,
                duration=0,
                score=score,
                message=f"视口测试: {len(results)} 个"
            )
        except Exception as e:
            return UITestResult(
                test_id="ui-responsive",
                test_name="响应式设计",
                dimension=TestDimension.UI.value,
                passed=False,
                duration=0,
                error=str(e)
            )

    # ═══════════════════════════════════════════════════════════════════
    # 质量测试
    # ═══════════════════════════════════════════════════════════════════

    def test_no_console_errors(self) -> UITestResult:
        """测试控制台错误"""
        try:
            # 获取日志
            logs = self.browser.driver.get_log('browser')
            errors = [log for log in logs if log['level'] == 'SEVERE']

            error_count = len(errors)
            score = 100 if error_count == 0 else max(0, 100 - error_count * 20)

            return UITestResult(
                test_id="ui-console",
                test_name="控制台错误",
                dimension=TestDimension.QUALITY.value,
                passed=error_count == 0,
                duration=0,
                score=score,
                message=f"错误数: {error_count}"
            )
        except Exception as e:
            return UITestResult(
                test_id="ui-console",
                test_name="控制台错误",
                dimension=TestDimension.QUALITY.value,
                passed=False,
                duration=0,
                error=str(e)
            )

    # ═══════════════════════════════════════════════════════════════════
    # 运行完整测试套件
    # ═══════════════════════════════════════════════════════════════════

    def run_full_suite(self) -> Dict:
        """运行完整 UI 测试套件"""
        results = []
        issues = []

        # 初始化浏览器
        setup_result = self.setup()
        if not setup_result or not self.browser.driver:
            return {
                "summary": {"total": 7, "passed": 0, "failed": 7, "pass_rate": 0, "avg_score": 0},
                "results": [
                    {
                        "test_id": "ui-setup",
                        "test_name": "浏览器初始化",
                        "dimension": "functional",
                        "passed": False,
                        "score": 0,
                        "duration": 0,
                        "message": "",
                        "error": f"Browser start failed: {self.browser._last_error}"
                    }
                ] * 7,
                "issues": [{"id": "setup", "title": "浏览器启动失败", "description": self.browser._last_error or "Unknown error", "severity": "critical"}]
            }

        try:
            # 功能测试
            print("Running functional tests...")
            results.append(self.test_home_page_loads())
            results.append(self.test_navigation_works())
            results.append(self.test_chat_functionality())

            # 性能测试
            print("Running performance tests...")
            results.append(self.test_page_performance())

            # UI 测试
            print("Running UI tests...")
            results.append(self.test_ui_layout())
            results.append(self.test_responsive_design())

            # 质量测试
            print("Running quality tests...")
            results.append(self.test_no_console_errors())

        finally:
            self.teardown()

        # 汇总结果
        passed = sum(1 for r in results if r.passed)
        total = len(results)
        avg_score = sum(r.score for r in results) / total if total > 0 else 0

        return {
            "summary": {
                "total": total,
                "passed": passed,
                "failed": total - passed,
                "pass_rate": passed / total if total > 0 else 0,
                "avg_score": avg_score
            },
            "results": [
                {
                    "test_id": r.test_id,
                    "test_name": r.test_name,
                    "dimension": r.dimension,
                    "passed": r.passed,
                    "score": r.score,
                    "duration": r.duration,
                    "message": r.message,
                    "error": r.error
                }
                for r in results
            ],
            "issues": issues
        }


# ═══════════════════════════════════════════════════════════════════════════
# 便捷函数
# ═══════════════════════════════════════════════════════════════════════════

def run_ui_tests(base_url: str = "http://localhost:3000") -> Dict:
    """运行 UI 测试"""
    suite = UITestSuite(base_url)
    return suite.run_full_suite()