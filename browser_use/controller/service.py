from pathlib import Path
import os
import pdb
import asyncio
import json
import logging
from typing import Optional, Type

from main_content_extractor import MainContentExtractor
from playwright.async_api import Page
from pydantic import BaseModel

from browser_use.agent.views import ActionModel, ActionResult
from browser_use.browser.context import BrowserContext
from browser_use.controller.registry.service import Registry
from browser_use.controller.views import (
	ClickElementAction,
	DoneAction,
	ExtractPageContentAction,
	GoToUrlAction,
	InputTextAction,
	OpenTabAction,
	ScrollAction,
	SearchGoogleAction,
	SendKeysAction,
	SwitchTabAction,
	CreateFileAction,
	AppendToFileAction,
	SaveFileToLocalAction,
	TakeAndSaveScreenshotAction,
	ExtractEmailAction,
	OutlookEmailScrollAction,

)
from browser_use.utils import time_execution_async, time_execution_sync

logger = logging.getLogger(__name__)



#class CreateFileParams(BaseModel):
#    file_path: Optional[str] = None

#class AppendToFileParams(BaseModel):
#    file_path: Optional[str] = None
#    text: str

#class SaveFileToLocalParams(BaseModel):
#    source_path: str
#    dest_path: str



class Controller:
	def __init__(
		self,
		exclude_actions: list[str] = [],
		output_model: Optional[Type[BaseModel]] = None,
	):
		self.exclude_actions = exclude_actions
		self.output_model = output_model
		self.registry = Registry(exclude_actions)
		self._register_default_actions()

	def _register_default_actions(self):
		"""Register all default browser actions"""

		if self.output_model is not None:

			@self.registry.action('Complete task', param_model=self.output_model)
			async def done(params: BaseModel):
				return ActionResult(is_done=True, extracted_content=params.model_dump_json())
		else:

			@self.registry.action('Complete task', param_model=DoneAction)
			async def done(params: DoneAction):
				return ActionResult(is_done=True, extracted_content=params.text)

		######  ADDED BY TOM OLDS  2/16/2025
			

		#@self.registry.action('Extract Email Texts', requires_browser=True)
		#async def extract_email_texts(params: ExtractEmailAction, browser: BrowserContext):
		#	"""
		#	Extracts the innerText of all elements whose aria-label attribute indicates email content.
		#	For example, this action finds elements where aria-label contains "Re:".
		#	Adjust the CSS selector as needed.
		#	"""
		#	page: Page = await browser.get_current_page()
			
		#	# Adjust the selector to match the email elements you are interested in.
		#	# This example finds any element with an aria-label containing "Re:".
		#	email_texts = await page.eval_on_selector_all(
		#		'[aria-label]',
		#		"""
		#		elements => {
		#			return elements
		#				.filter(el => el.getAttribute('aria-label') && el.getAttribute('aria-label').includes('Re:'))
		#				.map(el => el.innerText)
		#		}
		#		"""
		#	)
			
		#	if email_texts is None:
		#		email_texts = []
			
		#	msg = f"Extracted {len(email_texts)} email texts."
		#	logger.info(msg)
		#	# Return an ActionResult with both a summary message and the concatenated email texts.
		#	return ActionResult(
		#		extracted_content=msg + "\n" + "\n\n".join(email_texts),
		#		include_in_memory=True
		#	)
		
		# In your controller/service.py, register the action:
		@self.registry.action('Outlook Email Scroll', requires_browser=True)
		async def outlook_email_scroll(params: OutlookEmailScrollAction, browser: BrowserContext):
			page: Page = await browser.get_current_page()

			# Convert params to a dict to safely access the values.
			params_data = params.dict()  # or use params.model_dump() if using Pydantic v2
			scroll_amount = params_data.get("scroll_amount", 500)
			delay = params_data.get("delay", 1000)

			# Scroll down the page by the specified amount.
			await page.evaluate(f"window.scrollBy(0, {scroll_amount})")
			# Wait for the specified delay to allow content to load.
			await page.wait_for_timeout(delay)

			msg = f"Scrolled down {scroll_amount} pixels and waited {delay} ms."
			logger.info(msg)
			
			return ActionResult(
				extracted_content=msg,
				include_in_memory=True
			)
				
		
		@self.registry.action('Extract Email Texts', requires_browser=True)
		async def extract_email_texts(params: ExtractEmailAction, browser: BrowserContext):
			"""
			Extracts the full email content by:
			1. Clicking a "Read more" button if present to expand content.
			2. Scrolling the email container into view.
			3. Using a broad CSS selector to capture the complete email text.
			4. Continuously scrolling down until the number of extracted emails meets
			the target count (params.n_emails, defaults to 30) or no new emails are loaded.
			"""
			page: Page = await browser.get_current_page()
			
			# Step 1: Click "Read more" if the button exists.
			read_more_button = await page.query_selector("button[aria-label*='Read more']")
			if read_more_button:
				await read_more_button.click()
				await page.wait_for_timeout(1000)
			
			# Step 2: Define a broad selector for the email container.
			# Adjust this selector as needed for your page's structure.
			email_container_selector = "div[role='document'], div.email-content"
			
			# Scroll the container into view.
			email_container = await page.query_selector(email_container_selector)
			if email_container:
				await email_container.scroll_into_view_if_needed()
				await page.wait_for_timeout(500)
			
			# Step 3: Initial extraction of email texts.
			email_texts = await page.eval_on_selector_all(
				email_container_selector,
				"elements => elements.map(el => el.innerText)"
			) or []
			
			# Step 4: Determine target count.
			target_count = params.n_emails if hasattr(params, "n_emails") else 30
			current_count = len(email_texts)
			
			# Step 5: Scroll down repeatedly until we meet the target or no new emails load.
			max_attempts = 10  # To avoid an infinite loop.
			attempts = 0
			while current_count < target_count and attempts < max_attempts:
				# Scroll down the window by 500 pixels.
				await page.evaluate("window.scrollBy(0, 500)")
				await page.wait_for_timeout(1000)
				
				# Re-extract email texts after scrolling.
				new_texts = await page.eval_on_selector_all(
					email_container_selector,
					"elements => elements.map(el => el.innerText)"
				) or []
				
				# Deduplicate by combining the old and new texts.
				combined_texts = list(set(email_texts + new_texts))
				if len(combined_texts) == current_count:
					# No new emails were found.
					break
				
				email_texts = combined_texts
				current_count = len(email_texts)
				attempts += 1

			msg = f"Extracted {current_count} email texts."
			logger.info(msg)
			
			return ActionResult(
				extracted_content=msg + "\n" + "\n\n".join(email_texts),
				include_in_memory=True
			)

	# Create File Action
		@self.registry.action('Create File', param_model=CreateFileAction)
		async def create_file(params: CreateFileAction, browser: BrowserContext = None):
			"""
			Creates a new file if it doesn't exist.
			If file_path is not provided, defaults will be used from environment variables.
			"""
			default_dir = os.getenv("DEFAULT_FILE_DIR", "/Users/tomolds/first-agent/browser-use/screenshots")
			default_name = os.getenv("DEFAULT_FILE_NAME", "agent_output.txt")
			file_path = params.file_path or os.path.join(default_dir, default_name)
			try:
				# Ensure directory exists
				Path(os.path.dirname(file_path)).mkdir(parents=True, exist_ok=True)
				# Create file if it doesn't exist
				if not os.path.exists(file_path):
					with open(file_path, "w", encoding="utf-8") as f:
						f.write("")
				msg = f"File created at {file_path}"
				logger.info(msg)
				return ActionResult(extracted_content=msg, include_in_memory=True)
			except Exception as e:
				err_msg = f"Error in Create File: {str(e)}"
				logger.error(err_msg)
				return ActionResult(error=err_msg)

		# Append to File Action
		@self.registry.action('Append to File', param_model=AppendToFileAction)
		async def append_to_file(params: AppendToFileAction, browser: BrowserContext = None):
			"""
			Appends text to an existing file.
			If file_path is not provided, defaults will be used from environment variables.
			"""
			default_dir = os.getenv("DEFAULT_FILE_DIR", "/Users/tomolds/first-agent/browser-use/screenshots")
			default_name = os.getenv("DEFAULT_FILE_NAME", "agent_output.txt")
			file_path = params.file_path or os.path.join(default_dir, default_name)
			try:
				with open(file_path, "a", encoding="utf-8") as f:
					f.write(params.text + "\n")
				msg = f"Appended text to {file_path}"
				logger.info(msg)
				return ActionResult(extracted_content=msg, include_in_memory=True)
			except Exception as e:
				err_msg = f"Error in Append to File: {str(e)}"
				logger.error(err_msg)
				return ActionResult(error=err_msg)

		# Save File To Local Action
		@self.registry.action('Save File To Local', param_model=SaveFileToLocalAction)
		async def save_file_to_local(params: SaveFileToLocalAction, browser: BrowserContext = None):
			"""
			Copies a file from a source path to a destination path.
			"""
			source_path = params.source_path
			dest_path = params.dest_path
			try:
				# Ensure destination directory exists
				Path(os.path.dirname(dest_path)).mkdir(parents=True, exist_ok=True)
				with open(source_path, "r", encoding="utf-8") as src:
					content = src.read()
				with open(dest_path, "w", encoding="utf-8") as dst:
					dst.write(content)
				msg = f"Copied file from {source_path} to {dest_path}"
				logger.info(msg)
				return ActionResult(extracted_content=msg, include_in_memory=True)
			except Exception as e:
				err_msg = f"Error in Save File To Local: {str(e)}"
				logger.error(err_msg)
				return ActionResult(error=err_msg)	
					
		@self.registry.action('Take and Save Screenshot', param_model=TakeAndSaveScreenshotAction, requires_browser=True)
		async def take_and_save_screenshot(params: TakeAndSaveScreenshotAction, browser: BrowserContext):
			"""
			Takes a screenshot of the current page and saves it to a file.
			If file_path is not provided, uses the default directory and file name from environment variables.
			"""
			# Get defaults from environment variables
			default_dir = os.getenv("DEFAULT_FILE_DIR", "/Users/tomolds/first-agent/browser-use/screenshots")
			default_name = os.getenv("DEFAULT_SCREENSHOT_NAME", "screenshot.png")
			file_path = params.file_path or os.path.join(default_dir, default_name)
			
			try:
				# Ensure directory exists
				Path(os.path.dirname(file_path)).mkdir(parents=True, exist_ok=True)
				
				# Get the current page and take a screenshot.
				page = await browser.get_current_page()
				screenshot_options = {"path": file_path}
				if params.full_page:
					screenshot_options["full_page"] = True
				
				await page.screenshot(**screenshot_options)
				
				msg = f"Screenshot taken and saved at {file_path}"
				logger.info(msg)
				return ActionResult(extracted_content=msg, include_in_memory=True)
			except Exception as e:
				err_msg = f"Error in Take and Save Screenshot: {str(e)}"
				logger.error(err_msg)
				return ActionResult(error=err_msg)	
				
		#############################	
			
			
			# Basic Navigation Actions
		@self.registry.action(
			'Search Google in the current tab',
			param_model=SearchGoogleAction,
			requires_browser=True,
		)
		async def search_google(params: SearchGoogleAction, browser: BrowserContext):
			page = await browser.get_current_page()
			await page.goto(f'https://www.google.com/search?q={params.query}&udm=14')
			await page.wait_for_load_state()
			msg = f'🔍  Searched for "{params.query}" in Google'
			logger.info(msg)
			return ActionResult(extracted_content=msg, include_in_memory=True)

		@self.registry.action('Navigate to URL in the current tab', param_model=GoToUrlAction, requires_browser=True)
		async def go_to_url(params: GoToUrlAction, browser: BrowserContext):
			page = await browser.get_current_page()
			await page.goto(params.url)
			await page.wait_for_load_state()
			msg = f'🔗  Navigated to {params.url}'
			logger.info(msg)
			return ActionResult(extracted_content=msg, include_in_memory=True)

		@self.registry.action('Go back', requires_browser=True)
		async def go_back(browser: BrowserContext):
			await browser.go_back()
			msg = '🔙  Navigated back'
			logger.info(msg)
			return ActionResult(extracted_content=msg, include_in_memory=True)

		# Element Interaction Actions
		@self.registry.action('Click element', param_model=ClickElementAction, requires_browser=True)
		async def click_element(params: ClickElementAction, browser: BrowserContext):
			session = await browser.get_session()
			state = session.cached_state

			if params.index not in state.selector_map:
				raise Exception(f'Element with index {params.index} does not exist - retry or use alternative actions')

			element_node = state.selector_map[params.index]
			initial_pages = len(session.context.pages)

			# if element has file uploader then dont click
			if await browser.is_file_uploader(element_node):
				msg = f'Index {params.index} - has an element which opens file upload dialog. To upload files please use a specific function to upload files '
				logger.info(msg)
				return ActionResult(extracted_content=msg, include_in_memory=True)

			msg = None

			try:
				await browser._click_element_node(element_node)
				msg = f'🖱️  Clicked button with index {params.index}: {element_node.get_all_text_till_next_clickable_element(max_depth=2)}'

				logger.info(msg)
				logger.debug(f'Element xpath: {element_node.xpath}')
				if len(session.context.pages) > initial_pages:
					new_tab_msg = 'New tab opened - switching to it'
					msg += f' - {new_tab_msg}'
					logger.info(new_tab_msg)
					await browser.switch_to_tab(-1)
				return ActionResult(extracted_content=msg, include_in_memory=True)
			except Exception as e:
				logger.warning(f'Element not clickable with index {params.index} - most likely the page changed')
				return ActionResult(error=str(e))

		@self.registry.action(
			'Input text into a input interactive element',
			param_model=InputTextAction,
			requires_browser=True,
		)
		async def input_text(params: InputTextAction, browser: BrowserContext):
			session = await browser.get_session()
			state = session.cached_state

			if params.index not in state.selector_map:
				raise Exception(f'Element index {params.index} does not exist - retry or use alternative actions')

			element_node = state.selector_map[params.index]
			await browser._input_text_element_node(element_node, params.text)
			msg = f'⌨️  Input "{params.text}" into index {params.index}'
			logger.info(msg)
			logger.debug(f'Element xpath: {element_node.xpath}')
			return ActionResult(extracted_content=msg, include_in_memory=True)

		# Tab Management Actions
		@self.registry.action('Switch tab', param_model=SwitchTabAction, requires_browser=True)
		async def switch_tab(params: SwitchTabAction, browser: BrowserContext):
			await browser.switch_to_tab(params.page_id)
			# Wait for tab to be ready
			page = await browser.get_current_page()
			await page.wait_for_load_state()
			msg = f'🔄  Switched to tab {params.page_id}'
			logger.info(msg)
			return ActionResult(extracted_content=msg, include_in_memory=True)

		@self.registry.action('Open url in new tab', param_model=OpenTabAction, requires_browser=True)
		async def open_tab(params: OpenTabAction, browser: BrowserContext):
			await browser.create_new_tab(params.url)
			msg = f'🔗  Opened new tab with {params.url}'
			logger.info(msg)
			return ActionResult(extracted_content=msg, include_in_memory=True)

		# Content Actions
		@self.registry.action(
			'Extract page content to get the pure text or markdown with links if include_links is set to true',
			param_model=ExtractPageContentAction,
			requires_browser=True,
		)
		async def extract_content(params: ExtractPageContentAction, browser: BrowserContext):
			page = await browser.get_current_page()
			output_format = 'markdown' if params.include_links else 'text'
			content = MainContentExtractor.extract(  # type: ignore
				html=await page.content(),
				output_format=output_format,
			)
			msg = f'📄  Extracted page as {output_format}\n: {content}\n'
			logger.info(msg)
			return ActionResult(extracted_content=msg)

		@self.registry.action(
			'Scroll down the page by pixel amount - if no amount is specified, scroll down one page',
			param_model=ScrollAction,
			requires_browser=True,
		)
		async def scroll_down(params: ScrollAction, browser: BrowserContext):
			page = await browser.get_current_page()
			if params.amount is not None:
				await page.evaluate(f'window.scrollBy(0, {params.amount});')
			else:
				await page.keyboard.press('PageDown')

			amount = f'{params.amount} pixels' if params.amount is not None else 'one page'
			msg = f'🔍  Scrolled down the page by {amount}'
			logger.info(msg)
			return ActionResult(
				extracted_content=msg,
				include_in_memory=True,
			)

		# scroll up
		@self.registry.action(
			'Scroll up the page by pixel amount - if no amount is specified, scroll up one page',
			param_model=ScrollAction,
			requires_browser=True,
		)
		async def scroll_up(params: ScrollAction, browser: BrowserContext):
			page = await browser.get_current_page()
			if params.amount is not None:
				await page.evaluate(f'window.scrollBy(0, -{params.amount});')
			else:
				await page.keyboard.press('PageUp')

			amount = f'{params.amount} pixels' if params.amount is not None else 'one page'
			msg = f'🔍  Scrolled up the page by {amount}'
			logger.info(msg)
			return ActionResult(
				extracted_content=msg,
				include_in_memory=True,
			)

		# send keys
		@self.registry.action(
			'Send strings of special keys like Backspace, Insert, PageDown, Delete, Enter, Shortcuts such as `Control+o`, `Control+Shift+T` are supported as well. This gets used in keyboard.press. Be aware of different operating systems and their shortcuts',
			param_model=SendKeysAction,
			requires_browser=True,
		)
		async def send_keys(params: SendKeysAction, browser: BrowserContext):
			page = await browser.get_current_page()

			await page.keyboard.press(params.keys)
			msg = f'⌨️  Sent keys: {params.keys}'
			logger.info(msg)
			#pdb.set_trace()
			return ActionResult(extracted_content=msg, include_in_memory=True)

		@self.registry.action(
			description='If you dont find something which you want to interact with, scroll to it',
			requires_browser=True,
		)
		async def scroll_to_text(text: str, browser: BrowserContext):  # type: ignore
			page = await browser.get_current_page()
			try:
				# Try different locator strategies
				locators = [
					page.get_by_text(text, exact=False),
					page.locator(f'text={text}'),
					page.locator(f"//*[contains(text(), '{text}')]"),
				]

				for locator in locators:
					try:
						# First check if element exists and is visible
						if await locator.count() > 0 and await locator.first.is_visible():
							await locator.first.scroll_into_view_if_needed()
							await asyncio.sleep(0.5)  # Wait for scroll to complete
							msg = f'🔍  Scrolled to text: {text}'
							logger.info(msg)
							return ActionResult(extracted_content=msg, include_in_memory=True)
					except Exception as e:
						logger.debug(f'Locator attempt failed: {str(e)}')
						continue

				msg = f"Text '{text}' not found or not visible on page"
				logger.info(msg)
				return ActionResult(extracted_content=msg, include_in_memory=True)

			except Exception as e:
				msg = f"Failed to scroll to text '{text}': {str(e)}"
				logger.error(msg)
				return ActionResult(error=msg, include_in_memory=True)

		@self.registry.action(
			description='Get all options from a native dropdown',
			requires_browser=True,
		)
		async def get_dropdown_options(index: int, browser: BrowserContext) -> ActionResult:
			"""Get all options from a native dropdown"""
			page = await browser.get_current_page()
			selector_map = await browser.get_selector_map()
			dom_element = selector_map[index]

			try:
				# Frame-aware approach since we know it works
				all_options = []
				frame_index = 0

				for frame in page.frames:
					try:
						options = await frame.evaluate(
							"""
							(xpath) => {
								const select = document.evaluate(xpath, document, null,
									XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
								if (!select) return null;

								return {
									options: Array.from(select.options).map(opt => ({
										text: opt.text, //do not trim, because we are doing exact match in select_dropdown_option
										value: opt.value,
										index: opt.index
									})),
									id: select.id,
									name: select.name
								};
							}
						""",
							dom_element.xpath,
						)

						if options:
							logger.debug(f'Found dropdown in frame {frame_index}')
							logger.debug(f'Dropdown ID: {options["id"]}, Name: {options["name"]}')

							formatted_options = []
							for opt in options['options']:
								# encoding ensures AI uses the exact string in select_dropdown_option
								encoded_text = json.dumps(opt['text'])
								formatted_options.append(f'{opt["index"]}: text={encoded_text}')

							all_options.extend(formatted_options)

					except Exception as frame_e:
						logger.debug(f'Frame {frame_index} evaluation failed: {str(frame_e)}')

					frame_index += 1

				if all_options:
					msg = '\n'.join(all_options)
					msg += '\nUse the exact text string in select_dropdown_option'
					logger.info(msg)
					return ActionResult(extracted_content=msg, include_in_memory=True)
				else:
					msg = 'No options found in any frame for dropdown'
					logger.info(msg)
					return ActionResult(extracted_content=msg, include_in_memory=True)

			except Exception as e:
				logger.error(f'Failed to get dropdown options: {str(e)}')
				msg = f'Error getting options: {str(e)}'
				logger.info(msg)
				return ActionResult(extracted_content=msg, include_in_memory=True)

		@self.registry.action(
			description='Select dropdown option for interactive element index by the text of the option you want to select',
			requires_browser=True,
		)
		async def select_dropdown_option(
			index: int,
			text: str,
			browser: BrowserContext,
		) -> ActionResult:
			"""Select dropdown option by the text of the option you want to select"""
			page = await browser.get_current_page()
			selector_map = await browser.get_selector_map()
			dom_element = selector_map[index]

			# Validate that we're working with a select element
			if dom_element.tag_name != 'select':
				logger.error(f'Element is not a select! Tag: {dom_element.tag_name}, Attributes: {dom_element.attributes}')
				msg = f'Cannot select option: Element with index {index} is a {dom_element.tag_name}, not a select'
				return ActionResult(extracted_content=msg, include_in_memory=True)

			logger.debug(f"Attempting to select '{text}' using xpath: {dom_element.xpath}")
			logger.debug(f'Element attributes: {dom_element.attributes}')
			logger.debug(f'Element tag: {dom_element.tag_name}')

			xpath = '//' + dom_element.xpath

			try:
				frame_index = 0
				for frame in page.frames:
					try:
						logger.debug(f'Trying frame {frame_index} URL: {frame.url}')

						# First verify we can find the dropdown in this frame
						find_dropdown_js = """
							(xpath) => {
								try {
									const select = document.evaluate(xpath, document, null,
										XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
									if (!select) return null;
									if (select.tagName.toLowerCase() !== 'select') {
										return {
											error: `Found element but it's a ${select.tagName}, not a SELECT`,
											found: false
										};
									}
									return {
										id: select.id,
										name: select.name,
										found: true,
										tagName: select.tagName,
										optionCount: select.options.length,
										currentValue: select.value,
										availableOptions: Array.from(select.options).map(o => o.text.trim())
									};
								} catch (e) {
									return {error: e.toString(), found: false};
								}
							}
						"""

						dropdown_info = await frame.evaluate(find_dropdown_js, dom_element.xpath)

						if dropdown_info:
							if not dropdown_info.get('found'):
								logger.error(f'Frame {frame_index} error: {dropdown_info.get("error")}')
								continue

							logger.debug(f'Found dropdown in frame {frame_index}: {dropdown_info}')

							# "label" because we are selecting by text
							# nth(0) to disable error thrown by strict mode
							# timeout=1000 because we are already waiting for all network events, therefore ideally we don't need to wait a lot here (default 30s)
							selected_option_values = (
								await frame.locator('//' + dom_element.xpath).nth(0).select_option(label=text, timeout=1000)
							)

							msg = f'selected option {text} with value {selected_option_values}'
							logger.info(msg + f' in frame {frame_index}')

							return ActionResult(extracted_content=msg, include_in_memory=True)

					except Exception as frame_e:
						logger.error(f'Frame {frame_index} attempt failed: {str(frame_e)}')
						logger.error(f'Frame type: {type(frame)}')
						logger.error(f'Frame URL: {frame.url}')

					frame_index += 1

				msg = f"Could not select option '{text}' in any frame"
				logger.info(msg)
				return ActionResult(extracted_content=msg, include_in_memory=True)

			except Exception as e:
				msg = f'Selection failed: {str(e)}'
				logger.error(msg)
				return ActionResult(error=msg, include_in_memory=True)

	def action(self, description: str, **kwargs):
		"""Decorator for registering custom actions

		@param description: Describe the LLM what the function does (better description == better function calling)
		"""
		return self.registry.action(description, **kwargs)

	@time_execution_async('--multi-act')
	async def multi_act(
		self, actions: list[ActionModel], browser_context: BrowserContext, check_for_new_elements: bool = True
	) -> list[ActionResult]:
		"""Execute multiple actions"""
		results = []

		session = await browser_context.get_session()
		cached_selector_map = session.cached_state.selector_map
		cached_path_hashes = set(e.hash.branch_path_hash for e in cached_selector_map.values())
		await browser_context.remove_highlights()

		for i, action in enumerate(actions):
			if action.get_index() is not None and i != 0:
				new_state = await browser_context.get_state()
				new_path_hashes = set(e.hash.branch_path_hash for e in new_state.selector_map.values())
				if check_for_new_elements and not new_path_hashes.issubset(cached_path_hashes):
					# next action requires index but there are new elements on the page
					logger.info(f'Something new appeared after action {i} / {len(actions)}')
					break

			results.append(await self.act(action, browser_context))

			logger.debug(f'Executed action {i + 1} / {len(actions)}')
			#pdb.set_trace()
			if results[-1].is_done or results[-1].error or i == len(actions) - 1:
				
				break

			await asyncio.sleep(browser_context.config.wait_between_actions)
			# hash all elements. if it is a subset of cached_state its fine - else break (new elements on page)
		#pdb.set_trace()
		return results

	@time_execution_sync('--act')
	async def act(self, action: ActionModel, browser_context: BrowserContext) -> ActionResult:
		"""Execute an action"""
		try:
			for action_name, params in action.model_dump(exclude_unset=True).items():
				if params is not None:
					# remove highlights
					result = await self.registry.execute_action(action_name, params, browser=browser_context)
					#pdb.set_trace()
					if isinstance(result, str):
						return ActionResult(extracted_content=result)
					elif isinstance(result, ActionResult):
						return result
					elif result is None:
						return ActionResult()
					else:
						raise ValueError(f'Invalid action result type: {type(result)} of {result}')
			return ActionResult()
		except Exception as e:
			raise e
