from langchain_openai import ChatOpenAI
from browser_use import Agent
from dotenv import load_dotenv
load_dotenv()
import pdb
import os
import asyncio
import datetime
import json
#from datetime import datetime

#print("OPENAI_API_KEY from environment is:", os.getenv("OPENAI_API_KEY"))

#pdb.set_trace()
timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

os.environ["DEFAULT_FILE_DIR"] = '/Users/tomolds/first-agent/browser-use/screenshots'
os.environ["DEFAULT_FILE_NAME"] = 'agent_output.txt'



OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

 #Ensure the key is set before using it
if OPENAI_API_KEY is None:
    raise ValueError("Error: OPENAI_API_KEY is not set. Please check your environment variables.")









llm = ChatOpenAI(model="gpt-4o")



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

search_person= "Lynn Gadue"
n_emails = 15
task_text = f"""Please navigate to https://outlook.office.com and try to log in.
if you need help logging in, please ask user for credentials then proceed. username is tolds@3clife.info. password is annuiTy2024!
I will be prompted to execute MFA on my phone. Please wait at least 10 seconds for me to complete the MFA before proceeding.once inside the outlook application
 please take a screenshot and save it to the following folder on the local machine this code is running on : '/Users/tomolds/first-agent/browser-use/screenshots'.
please locate the search box at the top of the outlook window and type in the search box: From:{search_person}
then MAKE SURE TO search the email inbox by typing in the search box: From:{search_person}", BUT PLEASE MAKE SURE YOU ARE TYPING IN THE OUTLOOK MAIL SEARCH BOX, NOT A MORE GLOBAL BROWSER SEARCH.
 take and save another screenshot of the sorted email inbox. also please make sure to tell me the name of the screenshot an printout the path where this is save so I can find it.
I really need to be able to find these screenshots in '/Users/tomolds/first-agent/browser-use/screenshots' so please make sure to save them there.
please do not exit the process until you have allowed enough time to complete these steps.  but note I think 20 seconds should be enough time to complete these steps once you have entered outlook. 
Once you have taken and saved this sreenshot,
 In sequence, I would like you to do the following for the first {n_emails} emails in the list of emails from LYNNNE GADUE.  If there are less than 5 emails from {search_person}, then please do this for all emails from LYNN GADUE.
 I want you to OPEN THE FIRST EMAIL FROM {search_person} BY CLICKING ON ITS subject line which should be visible in the middle pane of the email view. 
 then click inside this email then copy the contents and display those contents in the console via a print() statement. also please save a text file version of the contents to the following folder on the local machine this code is running on : '/Users/tomolds/first-agent/browser-use/screenshots'. 
 also, between each email text saved to the file, please write a line of text telling what date the email arrived on, and what number of the {n_emails} this email is.
 note once you have clicked on an email, and you go back to the email inbox, we need to be sure we are still in the searched list, and we need to be sure we are stepping down the list of searched emails so we are not just capturing the same content over and over again.
 one way to be sure we are still in the searched list is to look at the screen and make sure we are looking at a list of emails from {search_person}. If not, then we need to resort the list

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

def recursive_sanitize(obj):
    """
    Recursively walk through the object.
    For any dict encountered, if it has a "screenshot" key, set its value to None.
    """
    if isinstance(obj, dict):
        new_obj = {}
        for key, value in obj.items():
            # If the key is "screenshot", remove it (or set to None)
            if key == "screenshot":
                new_obj[key] = None
            else:
                new_obj[key] = recursive_sanitize(value)
        return new_obj
    elif isinstance(obj, list):
        return [recursive_sanitize(item) for item in obj]
    elif isinstance(obj, tuple):
        # Convert tuple elements recursively and then keep as tuple.
        return tuple(recursive_sanitize(item) for item in obj)
    else:
        return obj

async def main():
    agent = Agent(
        task=task_text,
        llm=llm,
        save_conversation_path="/Users/tomolds/first-agent/browser-use/conversations/conversation/agent_history.log"
    )
    result = await agent.run()
    print(result)
    #pdb.set_trace()
    # Use recursive sanitization on the entire agent.history
    sanitized_history = recursive_sanitize(agent.history)

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
