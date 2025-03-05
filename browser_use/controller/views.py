from typing import Literal, Optional

from pydantic import BaseModel


# Action Input Models
class CreateFileAction(BaseModel):
    file_path: Optional[str] = None

class AppendToFileAction(BaseModel):
    file_path: Optional[str] = None
    text: str

class SaveFileToLocalAction(BaseModel):
    source_path: str
    dest_path: str

class TakeAndSaveScreenshotAction(BaseModel):
    file_path: Optional[str] = None  # Optional; if not provided, use default from env vars
    full_page: Optional[bool] = False  # Option to capture the full page


#class ExtractEmailAction(BaseModel):
#	text: str


class ExtractEmailAction(BaseModel):
    text: str = ""         # if needed for additional instructions
    n_emails: int = 30     # default value, which can be overwritten by the agent
	
class OutlookEmailScrollAction(BaseModel):
    n_emails: int = 30       # The expected number of emails (default: 30)
    scroll_amount: int = 500   # Number of pixels to scroll per action
    delay: int = 1000          # Delay after scrolling in milliseconds


class SearchGoogleAction(BaseModel):
	query: str


class GoToUrlAction(BaseModel):
	url: str


class ClickElementAction(BaseModel):
	index: int
	xpath: Optional[str] = None


class InputTextAction(BaseModel):
	index: int
	text: str
	xpath: Optional[str] = None


class DoneAction(BaseModel):
	text: str


class SwitchTabAction(BaseModel):
	page_id: int


class OpenTabAction(BaseModel):
	url: str


class ExtractPageContentAction(BaseModel):
	include_links: bool


class ScrollAction(BaseModel):
	amount: Optional[int] = None  # The number of pixels to scroll. If None, scroll down/up one page


class SendKeysAction(BaseModel):
	keys: str
