from dotenv import load_dotenv
import logging
import validators
import re
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Initialize environment variables and logging
load_dotenv()
logging.basicConfig(level=logging.INFO)

def extract_combined_contact_urls(base_url, html):
    # General regex pattern to match 'contact' URLs (case-insensitive)
    # Updated to include patterns like '...>Contact</span>...' inside <a> tags
    general_contact_regex = r'href="([^"]*(?:/contact|contact/)[^"]*)"[^>]*>[^<]*(?:<[^>]+>)*\s*Contact\s*(?:<[^>]+>)*'
    urls = re.findall(general_contact_regex, html, re.IGNORECASE)

    # Find URLs in a submenu structure
    submenu_regex = r'<li class="[^"]*menu-item-has-children[^"]*">[^<]*<a[^>]*href="#"[^>]*>[^<]*Contact[^<]*</a>(.*?)</ul>'
    submenu_html = re.search(submenu_regex, html, re.DOTALL | re.IGNORECASE)
    if submenu_html:
        submenu_urls = re.findall(r'href="([^"]+)"', submenu_html.group(1), re.IGNORECASE)
        urls.extend(submenu_urls)

    # Find URLs in specific class structures
    specific_class_structure_regex = r'<li class="[^"]*has-sub dropdown[^"]*">[^<]*<a href="([^"]+)"[^>]*>[^<]*Contact[^<]*</a>(.*?)</ul>'
    specific_submenu_html = re.search(specific_class_structure_regex, html, re.DOTALL | re.IGNORECASE)
    if specific_submenu_html:
        specific_submenu_urls = re.findall(r'href="([^"]+)"', specific_submenu_html.group(2), re.IGNORECASE)
        urls.extend(specific_submenu_urls)

    # Additional patterns for different structures
    additional_patterns = [
        r'<a class="[^"]*" href="([^"]+)"[^>]*>Contact</a>',
        r'<a href="([^"]+)"[^>]*onclick="[^"]*">Contact</a>',
        r'<a [^>]*href="([^"]+)"[^>]*style="[^"]*">contact</a>',
        # New pattern to match complex anchor tags like provided
        r'<a [^>]*href="([^"]+)"[^>]*>[^<]*(?:<[^>]+>)*\s*Contact\s*(?:<[^>]+>)*</a>'
    ]

    for pattern in additional_patterns:
        additional_urls = re.findall(pattern, html, re.IGNORECASE)
        urls.extend(additional_urls)

    # Remove duplicates
    urls = list(set(urls))

    # Complete the URLs if they are relative
    full_urls = [url if url.startswith('http') else base_url + url for url in urls]

    return full_urls

def find_school_website_url(source_code):
    # Define a regular expression pattern to match URLs
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    # Use re.findall to extract all URLs from the HTML source
    urls = re.findall(url_pattern, source_code)

def find_email_addresses(source_code):
    # Regular expression to match email addresses in <a> tags, either in href or text
    pattern = r'<a[^>]*>([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})</a>|<a[^>]*href=["\']mailto:([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})["\'][^>]*>'
    email_addresses = re.findall(pattern, source_code)

    # Flatten the list of tuples and remove empty strings
    email_addresses = [email for tuple in email_addresses for email in tuple if email]
    
    return email_addresses

# Connect to the Selenium Hub
hub_url = "http://selenium-hub:4444/wd/hub"

options = Options()
driver = webdriver.Remote(command_executor=hub_url, options=options)

places = ['Hengelo', 'Borne', 'Delden', 'Haaksbergen', 'markelo', 'Goor', 'Oldenzaal', 'Glanerbrug', 'Losser', 'Weerselo']

for place in places:
    driver.get(f"https://scholenopdekaart.nl/zoeken/basisscholen?zoektermen={place}&weergave=Lijst")
    # Wait for the page to load and for the button to be clickable
    try:
        more_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.zoeken-resultaten-lijst-meer')))
        more_button.click()
    except:
        pass

    # Extract the URLs for 'Bekijk school'
    school_links = [element.get_attribute('href') for element in driver.find_elements(By.CSS_SELECTOR, '.zoekresultaat-actions a')]

    for link in school_links:
        if validators.url(link):
            contact_url = link + 'contact/'
            driver.get(contact_url)
            school_title = driver.find_element(By.CSS_SELECTOR, 'h1').text

            # Wait for the contact details section to load
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.school-sectie-contactgegevens')))

            try:
                school_website_url = driver.find_element(By.CSS_SELECTOR, '.school-sectie-contactgegevens a[href^="http://"], .school-sectie-contactgegevens a[href^="https://"]').get_attribute('href')

                # Get the source code of the school website
                if validators.url(school_website_url):
                    driver.get(school_website_url)
                    source_code = driver.page_source

                    # Use the source code to find the contact URL
                    contact_urls = extract_combined_contact_urls(school_website_url, source_code)

                    email_addresses = []

                    for contact in contact_urls:
                        if validators.url(contact):
                            driver.get(contact)
                            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'body')))
                    
                            # Get source code of the contact page
                            source_code = driver.page_source
                    
                            # Find contact URLs and email addresses
                            emails = find_email_addresses(source_code)
                            for email in emails:
                                if email not in email_addresses:
                                    email_addresses.append(email)
                
                # Open (or create) a CSV file for writing
                with open('school_emails.csv', 'a', newline='') as csvfile:
                    fieldnames = ['EMAIL', 'FIRSTNAME', 'PLACE']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                    # Write the header if the file is new
                    if csvfile.tell() == 0:
                        writer.writeheader()
                
                    # Write the school title and email addresses to the CSV
                    for email in email_addresses:
                        writer.writerow({'EMAIL': email, 'FIRSTNAME': school_title, 'PLACE': place})
                print(f"School Website: {school_website_url}, School title: {school_title}, Email Addresses: {email_addresses}\n")
            except:
                print(f"School URL: {link}, Contact Page: {contact_url}, School Website: Not Found")

driver.quit()