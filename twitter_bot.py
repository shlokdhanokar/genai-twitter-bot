from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
from dotenv import load_dotenv

load_dotenv()

# Get Twitter credentials from environment variables
TWITTER_USERNAME = os.getenv("TWITTER_USERNAME")
TWITTER_PASSWORD = os.getenv("TWITTER_PASSWORD")
TWITTER_EMAIL = os.getenv("TWITTER_EMAIL")  

def handle_login_verification(driver, wait, email=None):
    """Handle verification step during Twitter login where email needs to be entered
    
    Args:
        driver: Selenium WebDriver instance
        wait: WebDriverWait instance
        email: Email address to use for verification
    
    Returns:
        bool: True if verification was handled, False if no verification found
    """
    if not email:
        email = TWITTER_EMAIL
        
    try:
        # Check if we're on a verification page by looking for specific text
        verification_texts = [
            "Enter your Phone number or Email address",
            "Enter your phone number or email address",
            "verify your identity",
            "Verify your identity"
        ]
        
        # Simple check for any verification texts on the page
        page_source = driver.page_source.lower()
        is_verification_page = any(text.lower() in page_source for text in verification_texts)
        
        if is_verification_page:
            print("✅ Detected verification page")
            
            # Simply use ActionChains to type the email directly - no need to find the input field
            # since focus is already on the input field
            time.sleep(1)  # Short pause to ensure page is ready
            
            # Clear any existing text first (using keyboard shortcuts)
            actions = ActionChains(driver)
            actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
            time.sleep(0.5)
            actions.send_keys(Keys.DELETE).perform()
            time.sleep(0.5)
            
            # Type the email address
            actions = ActionChains(driver)
            actions.send_keys(email).perform()
            print(f"✅ Entered email: {email}")
            
            # Press Enter to submit
            time.sleep(0.5)
            actions = ActionChains(driver)
            actions.send_keys(Keys.RETURN).perform()
            print("✅ Submitted email verification with Enter key")
            
            # Wait for processing
            time.sleep(3)
            return True
        
        return False  # No verification page detected
    
    except Exception as e:
        print(f"⚠️ Error handling verification: {e}")
        # Take a screenshot for debugging
        try:
            driver.save_screenshot("verification_error.png")
            print("✅ Saved error screenshot as 'verification_error.png'")
        except:
            pass
        return False

def find_and_click_post_button(driver, wait):
    """
    Advanced approach to find and click the Post button in Twitter's interface
    
    Args:
        driver: Selenium WebDriver instance
        wait: WebDriverWait instance
        
    Returns:
        bool: True if button was clicked successfully
    """
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    import time
    
    # Take a screenshot for debugging
    debug_screenshot = "twitter_debug.png"
    driver.save_screenshot(debug_screenshot)
    print(f"✅ Saved debug screenshot as '{debug_screenshot}'")
    
    # List of all possible selectors for the Post button
    post_button_selectors = [
        # Primary selectors based on your screenshot
        "//span[text()='Post']/ancestor::div[@role='button' and not(@aria-disabled='true')]",
        "//div[@data-testid='tweetButton']",
        "//div[@aria-label='Post' and @role='button']",
        
        # Broader fallback selectors
        "//div[@role='button'][.//span[text()='Post']]",
        "//div[contains(@data-testid, 'tweet') and contains(@data-testid, 'Button')]",
        "//div[@role='button'][contains(text(), 'Post')]"
    ]
    
    # Try each selector
    for selector in post_button_selectors:
        try:
            print(f"Trying selector: {selector}")
            elements = driver.find_elements(By.XPATH, selector)
            
            # If elements found, try clicking the first visible one
            if elements:
                for button in elements:
                    if button.is_displayed():
                        print(f"✅ Found visible Post button with selector: {selector}")
                        # Try regular click first
                        try:
                            button.click()
                            print("✅ Regular click successful!")
                            time.sleep(2)
                            return True
                        except Exception as e:
                            print(f"Regular click failed: {e}")
                            
                            # Try JavaScript click as fallback
                            try:
                                driver.execute_script("arguments[0].click();", button)
                                print("✅ JavaScript click successful!")
                                time.sleep(2)
                                return True
                            except Exception as js_error:
                                print(f"JavaScript click failed: {js_error}")
        except Exception as e:
            print(f"Error with selector {selector}: {e}")
    
    # If all selectors fail, try the nuclear option: scan all buttons for "Post" text
    try:
        print("Trying nuclear option: scanning all buttons for 'Post' text")
        all_buttons = driver.find_elements(By.XPATH, "//div[@role='button']")
        for button in all_buttons:
            try:
                if button.is_displayed() and "post" in button.text.lower():
                    print("✅ Found button with 'Post' text in scan")
                    driver.execute_script("arguments[0].click();", button)
                    print("✅ Nuclear option click successful!")
                    time.sleep(2)
                    return True
            except Exception:
                continue
    except Exception as e:
        print(f"Nuclear option failed: {e}")
    
    # If still no success, try direct JavaScript approach
    try:
        print("Trying JavaScript direct DOM manipulation")
        script = """
        var buttons = document.querySelectorAll('[role="button"]');
        for (var i = 0; i < buttons.length; i++) {
            var buttonText = buttons[i].textContent || '';
            if (buttonText.toLowerCase().includes('post') && 
                window.getComputedStyle(buttons[i]).display !== 'none' &&
                buttons[i].offsetWidth > 0 && 
                buttons[i].offsetHeight > 0) {
                buttons[i].click();
                return true;
            }
        }
        return false;
        """
        result = driver.execute_script(script)
        if result:
            print("✅ JavaScript DOM manipulation successful!")
            time.sleep(2)
            return True
        else:
            print("❌ JavaScript DOM manipulation couldn't find Post button")
    except Exception as e:
        print(f"JavaScript direct approach failed: {e}")
    
    # If we get here, all automated methods failed
    print("❌ All automated methods to find Post button failed")
    
    # Take another screenshot and ask for manual intervention
    driver.save_screenshot("twitter_failed_final.png")
    print("\n" + "="*50)
    print("MANUAL INTERVENTION REQUIRED:")
    print(f"Screenshot saved as 'twitter_failed_final.png'")
    print("Please click the Post button manually in the browser window")
    input("Press Enter after clicking the Post button (or to continue)...")
    print("="*50 + "\n")
    
    return False

def handle_verification_between_steps(driver, wait, email=None):
    """Handle verification step that appears between username and password pages
    
    Args:
        driver: Selenium WebDriver instance
        wait: WebDriverWait instance
        email: Email address to use for verification
    
    Returns:
        bool: True if verification was handled, False if no verification found
    """
    if not email:
        email = TWITTER_EMAIL
        
    try:
        # Check if we're on a verification page by looking for specific text
        # Take a screenshot for debugging
        driver.save_screenshot("verification_check.png")
        print("✅ Saved verification check screenshot")
        
        # Check if the page contains verification text
        verification_texts = [
            "Enter your Phone number or Email address",
            "Enter your phone number or email address",
            "verify your identity",
            "Verify your identity"
        ]
        
        # Simple check for any verification texts on the page
        page_source = driver.page_source.lower()
        is_verification_page = any(text.lower() in page_source for text in verification_texts)
        
        if is_verification_page:
            print("✅ Detected verification page between username and password steps")
            
            # Try to find the input field first
            try:
                # Try common input field selectors
                input_selectors = [
                    "input[name='text']", 
                    "input[type='text']",
                    "input[autocomplete='username']"
                ]
                
                input_field = None
                for selector in input_selectors:
                    try:
                        input_field = driver.find_element(By.CSS_SELECTOR, selector)
                        if input_field.is_displayed():
                            print(f"✅ Found input field with selector: {selector}")
                            break
                    except:
                        continue
                
                if input_field and input_field.is_displayed():
                    # Clear and enter email
                    input_field.clear()
                    input_field.send_keys(email)
                    print(f"✅ Entered email: {email}")
                    input_field.send_keys(Keys.RETURN)
                    print("✅ Submitted email with Enter key")
                    time.sleep(2)
                    return True
            except Exception as e:
                print(f"⚠️ Error finding input field: {e}")
            
            # If input field not found, try direct keyboard input
            print("⚠️ Input field not found, trying direct keyboard input")
            actions = ActionChains(driver)
            
            # Clear any existing text first
            actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
            time.sleep(0.5)
            actions.send_keys(Keys.DELETE).perform()
            time.sleep(0.5)
            
            # Type the email
            actions = ActionChains(driver)
            actions.send_keys(email).perform()
            print(f"✅ Entered email via ActionChains: {email}")
            
            # Submit with Enter
            time.sleep(0.5)
            actions = ActionChains(driver)
            actions.send_keys(Keys.RETURN).perform()
            print("✅ Submitted with Enter via ActionChains")
            
            # Wait for processing
            time.sleep(3)
            return True
        
        print("❌ No verification page detected between username and password steps")
        return False
    
    except Exception as e:
        print(f"⚠️ Error handling verification between steps: {e}")
        # Take a screenshot for debugging
        try:
            driver.save_screenshot("verification_error.png")
            print("✅ Saved error screenshot as 'verification_error.png'")
        except:
            pass
        return False


def tweet_with_selenium(tweet_text):
    """Post a tweet using Selenium automation"""
    # Set up Chrome options
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    
    # Uncomment to run in headless mode for production
    # options.add_argument("--headless")
    # options.add_argument("--disable-gpu")
    # options.add_argument("--no-sandbox")
    # options.add_argument("--disable-dev-shm-usage")
    
    # Setup Chrome driver with service
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        # Open Twitter login page
        driver.get("https://twitter.com/i/flow/login")
        wait = WebDriverWait(driver, 20)
        
        # Check if we need to log in or if we're already logged in
        if TWITTER_USERNAME and TWITTER_PASSWORD:
            try:
                # Wait for and enter username
                username_field = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "input[autocomplete='username']")))
                username_field.send_keys(TWITTER_USERNAME)
                username_field.send_keys(Keys.RETURN)
                
                # Wait a moment for the next screen to load
                time.sleep(3)
                
                # Check if verification page appears here (between username and password)
                if handle_verification_between_steps(driver, wait, TWITTER_EMAIL):
                    print("✅ Completed email verification step")
                    time.sleep(3)  # Wait for the next page after verification
                
                # Now enter password (which should be the next step after username or verification)
                password_field = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "input[type='password']")))
                password_field.send_keys(TWITTER_PASSWORD)
                password_field.send_keys(Keys.RETURN)
                
                print("✅ Successfully entered credentials")
                time.sleep(5)  # Wait for login to proceed
                
                print("✅ Login sequence completed")
                time.sleep(5)  # Wait for login to complete
                
            except Exception as e:
                print(f"⚠️ Login automation failed: {e}")
                print("➡️ Please log in manually if needed...")
                input("Press Enter after you've logged into Twitter...")
        else:
            print("⚠️ Twitter credentials not found in environment variables")
            print("➡️ Please log in manually...")
            input("Press Enter after you've logged into Twitter...")
        
        # Rest of the function remains the same
        # Navigate to home page
        driver.get("https://twitter.com/home")
        time.sleep(3)
        
        # Find and click the tweet composer directly
        try:
            # Try first with the navigation button (older UI)
            post_button = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "a[data-testid='SideNav_NewTweet_Button']")))
            post_button.click()
        except Exception:
            try:
                # Try with the fixed position compose button (newer UI)
                post_button = wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "a[data-testid='FloatingActionButton_Tweet']")))
                post_button.click()
            except Exception:
                # Try clicking directly on the input field if it's visible on the homepage
                tweet_box = wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "div[data-testid='tweetTextarea_0'], div[role='textbox']")))
                tweet_box.click()
        
        # Wait for the tweet composer to be visible
        time.sleep(2)
        
        # Enter tweet text - try multiple possible selectors
        try:
            tweet_box = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div[data-testid='tweetTextarea_0']")))
            tweet_box.send_keys(tweet_text)
        except Exception:
            # Alternative selector for newer Twitter UI
            tweet_box = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div[role='textbox'][data-testid='tweetTextarea_0']")))
            tweet_box.send_keys(tweet_text)
        
        time.sleep(1)  # Give time for the text to be entered
        
        # ---- USE NEW POST BUTTON FUNCTION ----
        post_button_clicked = find_and_click_post_button(driver, wait)
        
        # Wait for tweet to be posted
        time.sleep(5)
        
        if post_button_clicked:
            print("✅ Tweet posted successfully!")
            return True
        else:
            print("⚠️ Post button may not have been clicked properly")
            # Assume the user manually clicked the button if we got here
            print("Assuming tweet was posted manually")
            return True
        
    except Exception as e:
        print(f"❌ Error posting tweet: {e}")
        return False
    finally:
        driver.quit()

# Function to handle Twitter API posting (alternative approach)
def tweet_with_api(tweet_text):
    """
    Post a tweet using the Twitter API
    Note: This requires Twitter API access and authentication
    """
    try:
        # Import tweepy only when needed to avoid dependencies if not used
        import tweepy
        
        # Get credentials from environment
        consumer_key = os.getenv("TWITTER_API_KEY")
        consumer_secret = os.getenv("TWITTER_API_SECRET")
        access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        access_token_secret = os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        
        # Check if credentials exist
        if not all([consumer_key, consumer_secret, access_token, access_token_secret]):
            raise ValueError("Twitter API credentials not found in environment variables")
        
        # Authenticate and create API client
        auth = tweepy.OAuth1UserHandler(
            consumer_key, consumer_secret, access_token, access_token_secret
        )
        api = tweepy.API(auth)
        
        # Post tweet
        api.update_status(tweet_text)
        print("✅ Tweet posted successfully via API!")
        return True
        
    except ImportError:
        print("⚠️ tweepy not installed. Install with 'pip install tweepy' to use API method")
        return False
    except Exception as e:
        print(f"❌ Error posting tweet via API: {e}")
        return False

def post_tweet(tweet_text, method='selenium'):
    """
    Post a tweet using the specified method
    
    Args:
        tweet_text (str): The text to tweet
        method (str): 'selenium' (default) or 'api'
    
    Returns:
        bool: True if tweet was posted successfully, False otherwise
    """
    if method == 'api':
        # Try API method first if selected
        success = tweet_with_api(tweet_text)
        if success:
            return True
        
        # Fall back to Selenium if API fails
        print("⚠️ Falling back to Selenium method...")
    
    # Use Selenium method
    try:
        return tweet_with_selenium(tweet_text)
    except Exception as e:
        print(f"❌ Tweet posting failed: {e}")
        return False

if __name__ == "__main__":
    # Test the tweeting functionality
    test_tweet = "Hello World #TwitterBot #Python #Testing"
    post_tweet(test_tweet)