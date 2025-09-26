"""Custom Robot Framework library for Streamlit UI testing."""

from robot.api.deco import keyword
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class StreamlitTestLibrary:
    """Custom library for Streamlit UI automation."""

    def __init__(self):
        self.driver = None

    @keyword
    def setup_chrome_driver(self, headless: bool = True):
        """Setup Chrome WebDriver for Streamlit testing."""
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        self.driver = webdriver.Chrome(options=options)
        return self.driver

    @keyword
    def wait_for_streamlit_element(self, selector: str, timeout: int = 10):
        """Wait for Streamlit element to be present."""
        wait = WebDriverWait(self.driver, timeout)
        return wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))

    @keyword
    def get_chat_messages(self) -> list:
        """Get all chat messages from Streamlit interface."""
        messages = self.driver.find_elements(By.CSS_SELECTOR, '[data-testid="stChatMessage"]')
        return [msg.text for msg in messages]

    @keyword
    def verify_agent_status_indicator(self, expected_status: str) -> bool:
        """Verify the agent status indicator shows expected status."""
        try:
            status_element = self.wait_for_streamlit_element(
                '[data-testid="stSuccess"], [data-testid="stError"]'
            )
            return expected_status in status_element.text
        except Exception:
            return False
