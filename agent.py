from langchain_openai import ChatOpenAI
from browser_use import Agent
from dotenv import load_dotenv
load_dotenv()
import pdb
import os
import asyncio
import datetime
import json
import logging

#from datetime import datetime

#print("OPENAI_API_KEY from environment is:", os.getenv("OPENAI_API_KEY"))

#pdb.set_trace()
log_folder = "/Users/tomolds/first-agent/browser-use/logs"  # e.g., "/Users/tomolds/first-agent/browser-use/logs"
os.makedirs(log_folder, exist_ok=True)

timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')


log_filename = os.path.join(log_folder, f"agent_task_{timestamp}.log")


# Create a dedicated logger
agent_logger = logging.getLogger("agent_logger")
agent_logger.setLevel(logging.INFO)

# Create file handler
fh = logging.FileHandler(log_filename)
fh.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
fh.setFormatter(formatter)
agent_logger.addHandler(fh)

# Optionally add a stream handler for console output
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
sh.setFormatter(formatter)
agent_logger.addHandler(sh)

# Prevent propagation to the root logger if desired
agent_logger.propagate = False

agent_logger.info("Starting agent task...")


#logging.basicConfig(
#    level=logging.INFO,
#    format='%(asctime)s %(levelname)s: %(message)s',
#    handlers=[
#        logging.FileHandler(log_filename),
#        logging.StreamHandler()
#    ]
#)

logger = logging.getLogger(__name__)

os.environ["DEFAULT_FILE_DIR"] = '/Users/tomolds/first-agent/browser-use/screenshots'
os.environ["DEFAULT_FILE_NAME"] = 'agent_output.txt'



OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

 #Ensure the key is set before using it
if OPENAI_API_KEY is None:
    raise ValueError("Error: OPENAI_API_KEY is not set. Please check your environment variables.")



llm = ChatOpenAI(model="gpt-4o")



#llm = ChatOpenAI(model="gpt-4.5-preview-2025-02-27")



class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "dict"):
            return obj.dict()
        try:
            return obj.__dict__
        except AttributeError:
            return str(obj)


#task_text="Compare the price of gpt-4o and DeepSeek-V3"
#task_text="please tell me the temperature in New York City right now.  also tell me what date is today."

task_text = """Please navigate to https://amazon.com , wait three seconds and take a screenshot.
and save it to the following folder on the local machine this code is running on : '/Users/tomolds/first-agent/browser-use/screenshots'.
then wait more seconds and consider the task completed"""


#I want you to OPEN THE FIRST EMAIL FROM {search_person} BY CLICKING ON ITS subject line which should be visible in the middle pane of the email view. 
# then click inside this email then copy the contents and display those contents in the console via a print() statement. also please save a text file version of the contents to the following folder on the local machine this code is running on : '/Users/tomolds/first-agent/browser-use/screenshots'. 



search_person= "Lynn Gadue"
n_emails = 30
task_text = f"""Please navigate to https://outlook.office.com and try to log in.
if you need help logging in, please ask user for credentials then proceed. username is tolds@3clife.info. password is annuiTy2024!
I will be prompted to execute MFA on my phone. Please wait at least 10 seconds for me to complete the MFA before proceeding.once inside the outlook application
 please take a screenshot and save it to the following folder on the local machine this code is running on : '/Users/tomolds/first-agent/browser-use/screenshots'.
please locate the search box at the top of the outlook window and type in the search box: From:{search_person}
then MAKE SURE TO search the email inbox by typing in the search box: From:{search_person}", BUT PLEASE MAKE SURE YOU ARE TYPING IN THE OUTLOOK MAIL SEARCH BOX, NOT A MORE GLOBAL BROWSER SEARCH.
 take and save another screenshot of the sorted email inbox, immediately after playwright has indexed each item on the screen and numerically labeled those items on the screen also please make sure to tell me the name of the screenshot an printout the path where this is save so I can find it.
I really need to be able to find these screenshots in '/Users/tomolds/first-agent/browser-use/screenshots' so please make sure to save them there.
please do not exit the process until you have allowed enough time to complete these steps.  but note I think 20 seconds should be enough time to complete these steps once you have entered outlook. 
Once you have taken and saved this sreenshot,
 In sequence, I would like you to do the following for the first {n_emails} emails in the list of emails from LYNNNE GADUE.  If there are less than {n_emails} emails from {search_person}, then please do this for all emails from LYNN GADUE.
  sending screenshots immediately after playwright has indexed each item on the screen and numerically labeled those items on the screen, to the llm, to see if modifications to instruction steps are necessary, that show the indexing labels of each page generated by playwright before clicking anything at each step should help ensure we are always clicking the right thing and make sure we are on the right track.
 Please make sure you are working with and scrolling through the "All Results" list of emails from {search_person} and not the "Focused" or "Top Results" list of emails.
It is likely that we will need to scroll down the inbox in order to be able to click on additional emails if it is not possible to see 15 emails on the first displayed page.
 
 I would like you to extract the contents of the email using the extract_email_email_text action save a text file version of the contents to the following folder on the local machine this code is running on : '/Users/tomolds/first-agent/browser-use/screenshots'. 
 also, between each email text saved to the file, please write a line of text telling what date the email arrived on, and what number of the {n_emails} this email is.
 note once you have clicked on an email, and you go back to the email inbox, we need to be sure we are still in the searched list, and we need to be sure we are stepping down the list of searched emails so we are not just capturing the same content over and over again.
 again, sending screenshots that show the indexing labels of each page generated by playwright before clicking anything at each step should help ensure we are always clicking the right thing
 It may be necessary to scroll down the inbox in order to be able to click on additional emails if it is not possible to see 15 emails on the first displayed page
 please be sure to capture all of the content of each email and save it to the file.  this likely requires clicking into the which will perhaps open another window. also, please record and save the actual date the email
 was received and the actual subject of the email rather than placeholders. as well as saving the entire orignal content.and recall we are meant to be saving this email content all to the same iteratively updated file
 one way to be sure we are still in the searched list is to look at the screen and make sure we are looking at a list of emails from {search_person}. If not, then we need to resort the list
 Under no circumstances do I want you to delete any emails as a part of this process.  again, sending screenshots to the llm, to see if modifications to instruction steps are necessary, that show the indexing labels of each page generated by playwright before clicking anything at each step should help ensure we are always clicking the right thing. never click a delete button or icon.

  """
task_text = f"""Please navigate to https://outlook.office.com and try to log in.
If you need help logging in, please ask the user for credentials then proceed. The username is tolds@3clife.info and the password is annuiTy2024!
You will be prompted to execute MFA on your phone; please wait at least 10 seconds for MFA completion before proceeding.

Once inside the Outlook application:
1. Take a screenshot and save it to the folder: '/Users/tomolds/first-agent/browser-use/screenshots'.
2. Locate the search box at the top of the Outlook window and type in: From:{search_person}
   - IMPORTANT: Make sure you are using the Outlook Mail search box, not a global browser search.
3. After entering the search query "From:{search_person}", press Enter and then take another screenshot of the sorted inbox (the “All Results” view). Please confirm that the email list is fully visible with numerically labeled items. Print the screenshot name and its path.
4. Ensure that the screenshots are saved in '/Users/tomolds/first-agent/browser-use/screenshots' and allow at least 20 seconds for the inbox to load properly.

Next, process the emails as follows:
5. For the first {n_emails} emails in the list from {search_person} (if there are less than {n_emails}, process all available emails):
   a. Verify that you are viewing the sorted “All Results” inbox, not the “Focused” or “Top Results” view.
   b. Scroll down if needed so that at least 15 emails are visible on the page.
   c. Before clicking on an email, check the visual context (sender name, subject preview, and date) to ensure it is from {search_person}. If needed, take additional screenshots that show the numerical labels (bounding boxes) for confirmation.
   d. Click the email and immediately take a screenshot of the opened email to verify the full content is visible. If the content is truncated, scroll down and take further screenshots until the entire email is captured.
   e. Use the extract_email_email_text action to extract the full content of the email.
   f. Save the extracted content as text to a file in '/Users/tomolds/first-agent/browser-use/screenshots'. Between each email’s text in the file, include a line noting the email’s arrival date and its sequential number among the {n_emails} emails.
   g. After processing an email, return to the inbox and verify that you remain in the sorted “All Results” view before processing the next email.

6. Under no circumstances should any emails be deleted during this process.

Finally, once all emails have been processed and saved, use the done action to complete the task, and include a summary of the screenshot and text file paths for verification.

"""


task_text = f"""Please navigate to https://outlook.office.com and try to log in.
if you need help logging in, please ask user for credentials then proceed. username is tolds@3clife.info. password is annuiTy2024!
I will be prompted to execute MFA on my phone. Please wait at least 10 seconds for me to complete the MFA before proceeding.once inside the outlook application
Scroll down the Outlook inbox by 500 pixels and take a screenshot" to verify scrolling. Please do this three times.
please look at the screnshot between each step to make sure that the email box has indeeed scrolled down by 500 pixels.
"""



#task_text = f"""Please navigate to https://outlook.office.com and try to log in.
#if you need help logging in, please ask user for credentials then proceed. username is tolds@3clife.info. password is annuiTy2024!
#I will be prompted to execute MFA on my phone. Please wait at least 10 seconds for me to complete the MFA before proceeding.once inside the outlook application
# please take a screenshot and save it to the following folder on the local machine this code is running on : '/Users/tomolds/first-agent/browser-use/screenshots'.
#please locate the search box at the top of the outlook window and type in the search box: From:{search_person}
#then MAKE SURE TO search the email inbox by typing in the search box: From:{search_person}", BUT PLEASE MAKE SURE YOU ARE TYPING IN THE OUTLOOK MAIL SEARCH BOX, NOT A MORE GLOBAL BROWSER SEARCH.
# take and save another screenshot of the sorted email inbox. also please make sure to tell me the name of the screenshot an printout the path where this is save so I can find it.
#I really need to be able to find these screenshots in '/Users/tomolds/first-agent/browser-use/screenshots' so please make sure to save them there.
#please do not exit the process until you have allowed enough time to complete these steps.  but note I think 20 seconds should be enough time to complete these steps once you have entered outlook. 
#Once you have taken and saved this sreenshot,
# In sequence, I would like you to do the following for the first {n_emails} emails in the list of emails from LYNNNE GADUE.  If there are less than {n_emails} emails from {search_person}, then please do this for all emails from LYNN GADUE.
# I want you to OPEN THE FIRST EMAIL FROM {search_person} BY CLICKING ON ITS subject line which should be visible in the middle pane of the email view. 
# then click inside this email then copy the contents and display those contents in the console via a print() statement. also please save a text file version of the contents to the following folder on the local machine this code is running on : '/Users/tomolds/first-agent/browser-use/screenshots'. 
 
#  """
#task_text = f"""
#Your task is to automate the following sequence on Outlook **without ending the process early**. 
#DO NOT use the 'done' action until **all** steps below are fully completed.

#1. **Navigate and Log In:**
#   - Open the URL: "https://outlook.office.com".
#   - Log in using these credentials:
#     - **Username:** "tolds@3clife.info"
#     - **Password:** "annuiTy2024!"
#   - If additional credentials or multi-factor authentication (MFA) are required, prompt the user for the required input.
#   - Wait at least 10 seconds after any MFA prompt before proceeding.
#   - **Important:** Even after successful login, do not conclude the task; proceed to the following steps.

#2. **Initial Screenshot:**
#   - Once logged in and inside the Outlook application, use the "Take and Save Screenshot" action to capture a screenshot of the initial view.
#   - Save the screenshot in the directory "/Users/tomolds/first-agent/browser-use/screenshots".
#   - Confirm the screenshot file name and path in your output.

#3. **Email Search:**
#   - Locate the search box in the Outlook mail interface (ensure it is the Outlook mail search box, not a browser-wide search).
#   - Enter the text "From:{search_person}" into the search box to filter emails from the specified sender.
#   - Execute the search.
#   - **Important:** Ensure that the sorted list of emails remains visible. If navigating away from the inbox (e.g., when opening an email), you must return to the sorted inbox view before processing the next email.

#4. **Screenshot of Filtered Inbox:**
#   - After the inbox updates with the search results, use the "Take and Save Screenshot" action again to capture a screenshot of the filtered inbox.
#   - Save this screenshot in the directory "/Users/tomolds/first-agent/browser-use/screenshots".
#   - Print out the screenshot file name and full path.

#5. **Processing Emails:**
#   - Identify the emails in the sorted list from "{search_person}".
#   - For the first {n_emails} emails (or all emails if fewer than {n_emails} are available), perform the following steps in sequence:
#     a. **Open the Email in a New Window:** 
#        - Double-click on the subject line of the email. This should open the email in a new, separate window.  
#     b. **Copy Email Content:** 
#        - Once the email is open, click inside the email body and copy all its content.  
#     c. **Display Content:** 
#        - Print the email content to the console.  
#     d. **Save Content to File:** 
#        - Save the email content as a text file in the directory "/Users/tomolds/first-agent/browser-use/screenshots". Confirm the file name and path in your output.  
#     e. **Close the New Window:** 
#        - Click the red circle (or equivalent close button) at the top of the new email window to close it. This should return you to the original Outlook window, which still has the filtered list visible.  
#     f. **Maintain Filter and Track Progress:** 
#        - Verify that the inbox is still filtered by "From:{search_person}". If the filter is lost, reapply it by:
#          1. Clicking the search box,
#          2. Clearing any previous text,
#          3. Entering "From:{search_person}",
#          4. Pressing Enter.
#        - Keep track of how many emails you have processed so far. If you have processed {n_emails} emails (or there are no more emails from {search_person}), proceed to Final Confirmation. Otherwise, open the next email in the list.

#6. **Final Confirmation:**
#   - Only after confirming that all screenshots and email content files have been successfully saved, and that all required emails have been processed, should you use the "done" action.
#   - Do not exit or conclude the process until every one of the above steps has been executed.

#Remember: Even if login and MFA are successful, you must continue with Steps 2 through 5. 
#Ensure that the sorted inbox list remains available throughout the process, and do not issue a done action until all steps are completed.
#"""



#async def main():
#    agent = Agent(
#        task = task_text,
#        llm=llm,
#        save_conversation_path="/Users/tomolds/first-agent/browser-use/conversations/conversation/agent_history.log"
#    )
#    #pdb.set_trace()
#    result = await agent.run()
#    print(result)
#    # after task execution
#    with open("agent_history.json", "w", encoding="utf-8") as f:
#        json.dump(agent.history, f, indent=2, cls=CustomEncoder)
import json
import datetime

#def recursive_sanitize(obj):
#    """
#    Recursively walk through the object.
#    For any dict encountered, if it has a "screenshot" key, set its value to None.
#    """
#    if isinstance(obj, dict):
#        new_obj = {}
#        for key, value in obj.items():
#            # If the key is "screenshot", remove it (or set to None)
#            if key == "screenshot":
#                new_obj[key] = None
#            else:
#                new_obj[key] = recursive_sanitize(value)
#        return new_obj
#    elif isinstance(obj, list):
#        return [recursive_sanitize(item) for item in obj]
#    elif isinstance(obj, tuple):
#        # Convert tuple elements recursively and then keep as tuple.
#        return tuple(recursive_sanitize(item) for item in obj)
#    else:
#        return obj


EXAMPLE_PROMPT = (
    "Task: Navigate to a given URL and extract relevant information from the page.\n"
    "Constraints: Do not include extraneous data; focus only on the main content.\n"
    "Context: The browser should open the page, wait until it is fully loaded, and then capture the content.\n"
    "Instructions: Return a concise summary of the page's content along with the key data points."
)



EXAMPLE_PROMPT = (
    f"""Navigate to Twitter and create a post and reply to a tweet.

        Here are the specific steps:

        1. Go to config.base_url. See the text input field at the top of the page that says "What's happening?"
        2. Look for the text input field at the top of the page that says "What's happening?"
        3. Click the input field and type exactly this message:
        full_message
        4. Find and click the "Post" button (look for attributes: 'button' and 'data-testid="tweetButton"')
        5. Do not click on the '+' button which will add another tweet.

        6. Navigate to config.reply_url
        7. Before replying, understand the context of the tweet by scrolling down and reading the comments.
        8. Reply to the tweet under 50 characters.

        Important:
        - Wait for each element to load before interacting
        - Make sure the message is typed exactly as shown
        - Verify the post button is clickable before clicking
        - Do not click on the '+' button which will add another tweet
        """
)


def modify_task_text(task_text, llm):
    """
    Uses the LLM to modify the provided task_text so that it conforms to the structure
    and style exemplified by the EXAMPLE_PROMPT. The composite prompt instructs the LLM
    to return only the modified task text.
    """
    composite_prompt = (
        "Below is an example prompt from the browser-use repository:\n\n"
        f"{EXAMPLE_PROMPT}\n\n"
        "Please modify the following task text so that it follows the same structure and style as the example above:\n\n"
        f"{task_text}\n\n"
        "Return only the modified task text."
    )
    # Call the LLM. Here we assume that 'llm' is a callable that returns the response text.
    response = llm(composite_prompt)
     # If the response is an AIMessage-like object, extract its content.
    if hasattr(response, "content"):
        text = response.content
    else:
        text = response
    return text.strip()


def cleanup_result(result, llm):
    """
    Uses the LLM to modify the provided task_text so that it conforms to the structure
    and style exemplified by the EXAMPLE_PROMPT. The composite prompt instructs the LLM
    to return only the modified task text.
    """
    composite_prompt = (
        "Here is a result of a text extraction process I ran:\n\n"
        f"{result}\n\n"
        "It contains a list of results from a series of steps meant to extract email text from my outlook inbox.\n\n"
        
        "Please remove any stange characters or unnecessary, eliminate any duplicate entries, and create a version of the concatenated text that is a complete and coherent representation of the concatenated contents of these emails."
    )
    # Call the LLM. Here we assume that 'llm' is a callable that returns the response text.
    response = llm(composite_prompt)
     # If the response is an AIMessage-like object, extract its content.
    if hasattr(response, "content"):
        text = response.content
    else:
        text = response
    return text.strip()



async def main():
    
    
    modified_task_text = modify_task_text(task_text, llm)
    print("Modified Task Text:")
    print(modified_task_text)
    #pdb.set_trace()
    
   

# In your main function, you might log the start of the task:
    logger.info("Starting agent task with task_text: %s", task_text)                    
    
    
    
    agent = Agent(
        task=task_text,
        #task=modified_task_text,
        llm=llm,
        n_emails=n_emails,
        save_conversation_path="/Users/tomolds/first-agent/browser-use/conversations/conversation/agent_history.log"
    )
    result = await agent.run()
        
    email_contents = []
    for action in result.action_results():
        # Check if the action has an 'extracted_content' attribute and that it's not None
        if hasattr(action, "extracted_content") and action.extracted_content:
            content = action.extracted_content.strip()  # Remove leading/trailing whitespace
            # Check if "extracted" or "Extracted" appears in the first 20 characters
            if "extracted" in content[:20].lower():  
                email_contents.append(content)


    # Now email_contents contains all extracted_content values
    print(email_contents)
    print(" ####################################################################")
    modified_result = cleanup_result(email_contents, llm)

    print("Modified Result:")

    print(modified_result)
    
    
    #print(result)
    pdb.set_trace()
    # Use recursive sanitization on the entire agent.history
    #sanitized_history = recursive_sanitize(agent.history)

    # Create an output object that includes a timestamp and the sanitized history.
    output_data = {
        "timestamp": datetime.datetime.now().isoformat(),
        "history": sanitized_history
    }

    # Generate a unique filename with a timestamp (e.g., agent_history_20250221_172943.json)
    timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"agent_history_{timestamp_str}.json"

    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, cls=CustomEncoder)

asyncio.run(main())



#task_text = """Please navigate to https://outlook.office.com and try to log in.
#if you need help logging in, please ask user for credentials then proceed. username is tolds@3clife.info. password is annuiTy2024!
#I will be prompted to execute MFA on my phone. Please wait at least 10 seconds for me to complete the MFA before proceeding.once inside the outlook application please take a screenshot and save it to the following folder on the local machine this code is running on : '/Users/tomolds/first-agent/browser-use/screenshots'.
#then please MAKE SURE TO search the email inbox by typing in the search box: "From:Lynn Gadue", take and save another screenshot of the sorted email inbox. also please make sure to tell me the name of the screenshot an printout the path where this is save so I can find it.
#I really need to be able to find these screenshots in '/Users/tomolds/first-agent/browser-use/screenshots' so please make sure to save them there.
#please do not exit the process until you have allowed enough time to complete these steps.  but not I think 20 seconds should be enough time to complete these steps once you have entered outlook.  """
