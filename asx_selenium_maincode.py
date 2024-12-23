from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import requests
import re


# Function to clean filenames
def clean_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "", filename).replace("\n", " ").strip()

# Output file headers
output_sheet = "Sl.No\tASX Code\tDate\tHeadline\tPDF URL\tStatus\n"
with open("Output_Sheet.txt", 'w') as SM:
    SM.write(output_sheet)
    
with open("Cookie.txt", 'r') as SM:
    cookie_data = SM.read()
    
# Get user input for the search date
search_date = input("Enter Search Date: ")
month = input("Enter Search Month: ")
year = input("Enter Search Year: ")

# Construct the URL
main_url = f"https://www.asx.com.au/asx/v2/statistics/announcements.do?by=asxCode&asxCode=&timeframe=R&dateReleased={search_date}%2F{month}%2F{year}"

driver = webdriver.Chrome()

driver.get(main_url)

# Give the page some time to load
time.sleep(5)

content = driver.page_source

with open ("Content.html",'w', encoding = "utf-8") as SM:
    SM.write(content)
si_no = 0
esi_no = 0
blocks = re.findall(r'(<tr\sclass=(?:"altrow"|"\s*")[\w\W]*?<\/tr>)',str(content))
total_pdf_count = len(blocks)
for block in blocks:
    si_no += 1
    asx_code = re.findall(r'<td>([^>]*?)<\/td>\s*<td>\s*\d+',str(block))[0]
    date = re.findall(r'<td>[^>]*?<\/td>\s*<td>\s*([^>]*?)\s*<br>',str(block))[0]
    headline = re.findall(r'href[^>]*?>\s*([^>]*?)\s*<br>',str(block))[0]
    pdf_link = re.findall(r'href\=\"([^>]*?)\"\s*>',str(block))[0]
    if pdf_link:
        pdf_link = re.sub('&amp;','&',str(pdf_link))
        pdf_link1 = pdf_link
        pdf_link = "https://www.asx.com.au" + str(pdf_link)
    pdf_headers = {
        "authority":"www.asx.com.au",
        "method":"GET",
        "path":str(pdf_link1),
        "scheme":"https",
        "accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-encoding":"gzip, deflate, br, zstd",
        "accept-language":"en-GB,en-US;q=0.9,en;q=0.8",
        "cookie":str(cookie_data),
        "priority":"u=0, i",
        "sec-ch-ua":'"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile":"?0",
        "sec-ch-ua-platform":"Windows",
        "sec-fetch-dest":"document",
        "sec-fetch-mode":"navigate",
        "sec-fetch-site":"none",
        "sec-fetch-user":"?1",
        "upgrade-insecure-requests":"1",
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"}
    pdf_resp = requests.get(pdf_link, headers = pdf_headers)
    pdf_resp_code = pdf_resp.status_code
    if pdf_resp_code == 200:
        file_name = str(si_no) + '_' + str(headline) + '.pdf'
        with open (file_name,'wb') as SM:
            SM.write(pdf_resp.content)
        status = "Downloaded"
        print("pdf_count: ",si_no)
    else:
        esi_no += 1
        status = "Not Downloaded"
        print("Error_pdf_count: ",esi_no)
    
    output_sheet = str(si_no) + "\t" + str(asx_code) + "\t" + str(date) + "\t" + str(headline) + "\t" + str(pdf_link) + "\t" + str(status) + "\n"   
    with open ("Output_Sheet.txt", 'a') as SM:
        SM.write(output_sheet)
print("Total PDF Count:", total_pdf_count)
print("Data Extraction Completed")