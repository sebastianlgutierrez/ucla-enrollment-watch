import time, re
from playwright.sync_api import sync_playwright

def run_playwright(url, subject, class_name, lecture=None, discussion=None):
    with sync_playwright() as playwright:
        with playwright.chromium.launch(headless=True) as browser:
            # Load the schedule of classes page
            page = browser.new_page(
                java_script_enabled=True,
                viewport={'width': 1280, 'height': 720}
            )
            page.goto(url)
            # Fetch the class data 
            page.get_by_role(
                'combobox',
                name='Enter Subject Area (Required)').fill(subject)
            page.get_by_role(
                'option', name=subject).click()
            page.get_by_role(
                'button', name='Go').click()
            time.sleep(1)
            page.get_by_role(
                'button', name=class_name).click()
            # If Lecture, Discussion is specified
            if lecture is not None:
                # Select the exact lecture from the divs
                lecture_link = page.locator('.sectionColumn a').filter(has_text=re.compile(rf'^Lec {re.escape(str(lecture))}$'))
                lecture_div = page.locator('.data_row.primary-row').filter(has=lecture_link)
                # Handle exceptions if specified lecture not locatable
                lecture_div.wait_for(state='attached', timeout=15000)
                # Fetches the inner text corresponding to the exact lecture
                lecture_num = lecture_div.locator('.sectionColumn .hide-small').inner_text()
                status_text = lecture_div.locator('.statusColumn p').inner_text()

                print(lecture_num)
                print(status_text)
                
                status = status_text.strip().startswith('Open')
            else:
                page.get_by_role(
                'link', name=lecture)
                status = False if page.get_by_role('paragraph', name='Closed') else True
            time.sleep(2)
            page.close()
            return status

def main():
    # Set main variables to scan classes
    URL = 'https://sa.ucla.edu/ro/public/soc'
    SUBJECT = 'Statistics (STATS)'
    CLASS_NAME = '100A'
    LECTURE = '1'
    if (LECTURE and run_playwright(URL, SUBJECT, CLASS_NAME, LECTURE)):
        print('Lecture ' + LECTURE + ' of ' + SUBJECT + ' ' + CLASS_NAME + ' is open for enrollment.')
    elif (run_playwright(URL, SUBJECT, CLASS_NAME)):
        print(SUBJECT + ' ' + CLASS_NAME + ' is currently available for enrollment.')
    else:
        print(SUBJECT + ' ' + CLASS_NAME + ' is currently unavailable for enrollment.')

main()