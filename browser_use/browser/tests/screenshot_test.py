import base64
import pytest
from browser_use.browser.browser import Browser, BrowserConfig
import datetime
import os

@pytest.fixture
async def browser():
    browser_service = Browser(config=BrowserConfig(headless=True))
    yield browser_service
    await browser_service.close()

@pytest.mark.asyncio
async def test_take_full_page_screenshot(browser):
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

    async with browser:
        await browser.go_to_url('https://google.com')

        screenshot_b64 = await browser.take_screenshot(full_page=True)
        assert screenshot_b64 is not None
        assert isinstance(screenshot_b64, str)
        assert len(screenshot_b64) > 0

        try:
            base64.b64decode(screenshot_b64)
        except Exception as e:
            pytest.fail(f'Failed to decode base64 screenshot: {str(e)}')

        screenshot_filename = f'full_page_screenshot_{timestamp}.png'
        screenshot_path = os.path.join('/Users/tomolds/first-agent/browser-use/screenshots', screenshot_filename)

        with open(screenshot_path, 'wb') as f:
            f.write(base64.b64decode(screenshot_b64))

        print(f'Screenshot saved to {screenshot_path}')

if __name__ == '__main__':
    pytest.main([__file__])


#import base64

#import pytest

#from browser_use.browser.browser import Browser, BrowserConfig

#import datetime
#import os

#@pytest.fixture
#async def browser():
#	browser_service = Browser(config=BrowserConfig(headless=True))
#	yield browser_service

#	await browser_service.close()


## @pytest.mark.skip(reason='takes too long')
#def test_take_full_page_screenshot(browser):
#	# Go to a test page
#	timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
	
#	browser.go_to_url('https://google.com')

#	# Take full page screenshot
#	screenshot_b64 = browser.take_screenshot(full_page=True)

#	# Verify screenshot is not empty and is valid base64
#	assert screenshot_b64 is not None
#	assert isinstance(screenshot_b64, str)
#	assert len(screenshot_b64) > 0

#	# Test we can decode the base64 string
#	try:
#		base64.b64decode(screenshot_b64)
#	except Exception as e:
#		pytest.fail(f'Failed to decode base64 screenshot: {str(e)}')
	
	
#	screenshot_filename = f'full_page_screenshot_{timestamp}.png'
#	screenshot_path = os.path.join('/Users/tomolds/first-agent/browser-use/screenshots', screenshot_filename)
	

#	# Decode the base64 screenshot and save it as an image file
#	with open(screenshot_path, 'wb') as f:
#		f.write(base64.b64decode(screenshot_b64))

#	print(f'Screenshot saved to {screenshot_path}')


#if __name__ == '__main__':
#	test_take_full_page_screenshot(Browser(config=BrowserConfig(headless=False)))


