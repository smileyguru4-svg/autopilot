"""Five Survey bot - Real automation for fivesurvey.com"""

import time
from typing import Optional, Callable
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from core.persona import PersonaBuilder

class FiveSurveyBot:
    """Autonomous bot for completing surveys on Five Survey."""
    
    def __init__(self, persona: PersonaBuilder, log_callback: Optional[Callable] = None):
        self.persona = persona
        self.log_callback = log_callback
        self.driver = None
        self.is_running = True
        self.survey_count = 0
        self.question_count = 0
    
    def log(self, message: str):
        """Log a message."""
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)
    
    def start(self, url: str):
        """Start the bot and begin survey automation."""
        try:
            # Initialize Chrome driver
            options = webdriver.ChromeOptions()
            # Uncomment for headless mode:
            # options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            self.driver = webdriver.Chrome(options=options)
            self.log(f"[BOT] Chrome driver initialized")
            
            # Navigate to Five Survey
            self.log(f"[BOT] Navigating to {url}")
            self.driver.get(url)
            
            # Wait for page load
            time.sleep(3)
            self.log(f"[BOT] Page loaded. Title: {self.driver.title}")
            
            # Get available surveys
            self.log(f"[BOT] Searching for surveys...")
            surveys = self.find_surveys()
            
            if not surveys:
                self.log(f"[BOT] ❌ No surveys found on this page")
                return
            
            self.log(f"[BOT] Found {len(surveys)} surveys")
            
            # Complete surveys
            for survey in surveys:
                if not self.is_running:
                    break
                
                self.survey_count += 1
                self.log(f"\n[BOT] === SURVEY {self.survey_count} ===")
                self.log(f"[BOT] Title: {survey.get('title', 'Unknown')}")
                
                try:
                    self.complete_survey(survey)
                except Exception as e:
                    self.log(f"[BOT] ❌ Error completing survey: {e}")
            
            self.log(f"\n[BOT] ✅ Automation complete! {self.survey_count} survey(s) completed.")
            
        except Exception as e:
            self.log(f"[BOT] ❌ Fatal error: {e}")
        finally:
            self.stop()
    
    def find_surveys(self) -> list:
        """Find available surveys on the page."""
        surveys = []
        try:
            # Five Survey usually has survey cards/listings
            # Adjust selectors based on actual site structure
            survey_elements = self.driver.find_elements(By.CSS_SELECTOR, "[class*='survey'], [class*='panel'], .card")
            
            self.log(f"[BOT] Found {len(survey_elements)} potential survey elements")
            
            for elem in survey_elements[:3]:  # Limit to 3 for testing
                try:
                    title = elem.find_element(By.CSS_SELECTOR, "h2, h3, .title").text
                    link = elem.find_element(By.CSS_SELECTOR, "a").get_attribute('href')
                    surveys.append({
                        'title': title,
                        'link': link,
                        'element': elem
                    })
                except NoSuchElementException:
                    continue
        
        except Exception as e:
            self.log(f"[BOT] Error finding surveys: {e}")
        
        return surveys
    
    def complete_survey(self, survey: dict):
        """Complete a single survey."""
        try:
            # Click survey link
            if survey.get('link'):
                self.driver.get(survey['link'])
            else:
                survey['element'].find_element(By.CSS_SELECTOR, "a").click()
            
            time.sleep(2)
            self.log(f"[BOT] Survey page loaded")
            
            self.question_count = 0
            
            # Answer questions in a loop
            while self.is_running:
                self.question_count += 1
                
                # Check if survey is complete
                if self.is_survey_complete():
                    self.log(f"[BOT] ✅ Survey complete!")
                    break
                
                # Get current question
                question_data = self.get_current_question()
                if not question_data:
                    self.log(f"[BOT] No more questions found")
                    break
                
                self.log(f"\n[BOT] Q{self.question_count}: {question_data['text'][:80]}...")
                
                # Determine answer
                answer = self.persona.get_answer_for_question(
                    question_data['text'],
                    question_data['type']
                )
                
                if answer:
                    self.log(f"[BOT] Answer: {answer[:60]}...")
                    self.submit_answer(answer, question_data)
                else:
                    self.log(f"[BOT] ⚠️  Could not determine answer, using default")
                    if question_data.get('options'):
                        self.submit_answer(question_data['options'][0], question_data)
                
                # Small delay between answers
                time.sleep(0.5)
        
        except Exception as e:
            self.log(f"[BOT] Error in survey completion: {e}")
    
    def get_current_question(self) -> Optional[dict]:
        """Get the current survey question."""
        try:
            # Common question selectors
            selectors = [
                "[class*='question']",
                ".question-text",
                "label",
                "[role='dialog'] div"
            ]
            
            question_text = None
            for selector in selectors:
                try:
                    elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    question_text = elem.text.strip()
                    if question_text and len(question_text) > 10:
                        break
                except NoSuchElementException:
                    continue
            
            if not question_text:
                return None
            
            # Find answer options
            options = []
            try:
                option_elements = self.driver.find_elements(By.CSS_SELECTOR, "input[type='radio'], input[type='checkbox'], button[class*='option']")
                for opt in option_elements[:10]:  # Limit to 10 options
                    label = opt.get_attribute('aria-label') or opt.find_element(By.XPATH, "...").text
                    if label:
                        options.append(label)
            except:
                pass
            
            return {
                'text': question_text,
                'type': 'multiple_choice' if options else 'text',
                'options': options
            }
        
        except Exception as e:
            self.log(f"[BOT] Error getting question: {e}")
            return None
    
    def submit_answer(self, answer: str, question_data: dict):
        """Submit an answer to the current question."""
        try:
            if question_data.get('options'):
                # Multiple choice - find and click matching option
                option_elements = self.driver.find_elements(By.CSS_SELECTOR, "input[type='radio'], input[type='checkbox']")
                for opt in option_elements:
                    label = opt.get_attribute('aria-label') or opt.find_element(By.XPATH, "../label").text
                    if answer.lower() in label.lower() or label.lower() in answer.lower():
                        opt.click()
                        self.log(f"[BOT] Selected: {label}")
                        break
            else:
                # Text input
                text_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='text'], textarea")
                text_input.send_keys(answer)
                self.log(f"[BOT] Entered text")
            
            # Look for Next/Continue button
            time.sleep(0.3)
            next_button = self.find_next_button()
            if next_button:
                next_button.click()
                time.sleep(1)
        
        except Exception as e:
            self.log(f"[BOT] Error submitting answer: {e}")
    
    def find_next_button(self):
        """Find and return the Next/Continue button."""
        selectors = [
            "button:contains('Next')",
            "button:contains('Continue')",
            "[class*='next']",
            "[class*='continue']",
            "button[type='submit']"
        ]
        
        for selector in selectors:
            try:
                return self.driver.find_element(By.XPATH, f"//{selector}")
            except:
                continue
        
        return None
    
    def is_survey_complete(self) -> bool:
        """Check if the survey is complete."""
        try:
            complete_indicators = [
                "Thank you",
                "Survey Complete",
                "Completed",
                "Success"
            ]
            
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            return any(indicator in page_text for indicator in complete_indicators)
        except:
            return False
    
    def stop(self):
        """Stop the bot and clean up."""
        self.is_running = False
        if self.driver:
            try:
                self.driver.quit()
                self.log(f"[BOT] Chrome driver closed")
            except:
                pass
