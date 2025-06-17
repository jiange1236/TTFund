import requests
from bs4 import BeautifulSoup
import xlsxwriter
import re

def main():
    # This URL is known to contain the fund list in a JavaScript variable
    url = "http://fund.eastmoney.com/js/fundcode_search.js"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status() # Raises an HTTPError for bad responses (4XX or 5XX)
        # The content is JavaScript, so we need to decode it properly.
        # Eastmoney often uses 'gbk' or 'gb2312' for these JS files.
        # If response.apparent_encoding is not accurate, we might need to set it manually.
        # For fundcode_search.js, it's typically UTF-8 or GBK. Let's try apparent_encoding first.
        response.encoding = response.apparent_encoding 
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return

    # The content is a JavaScript file, not HTML, so BeautifulSoup is not needed here.
    # The data is typically in a format like: var r = [["code","short_pinyin","name","type","full_pinyin"],...];
    # We need to extract the array part.
    script_content = response.text

    # Regex to find the array assigned to a variable (commonly 'r' or 'fundcode_search')
    # It looks for a variable assignment followed by a JavaScript array literal.
    match = re.search(r'var\s+\w+\s*=\s*(\[\[.*?\]\]);', script_content)
    if not match:
        print("Could not find or parse fund data array in the JavaScript file.")
        # Fallback: try to find any array that looks like fund data
        match = re.search(r'(\[\[.*?\]\])', script_content) # More generic array search
        if not match:
            print("Fallback regex also failed. Content might not be as expected.")
            print("First 500 chars of content for debugging:")
            print(script_content[:500])
            return

    fund_data_str = match.group(1)

    # The extracted string is a JavaScript array. We can't directly use json.loads
    # because it's not strict JSON (e.g., strings might not always be double-quoted internally by JS).
    # A safer way for this specific format is to parse it carefully.
    # A simpler, though potentially fragile, way for this specific known structure:
    try:
        # This uses eval, which can be a security risk if the source is not trusted.
        # Given this is from a well-known site and we've regexed a specific structure, risk is lower.
        # For a more robust solution, a proper JS parser or more complex regex would be needed.
        all_funds = eval(fund_data_str)
    except Exception as e:
        print(f"Error evaluating fund data: {e}")
        return

    if not all_funds:
        print("No fund data extracted.")
        return

    # Create a new Excel file and add a worksheet.
    workbook = xlsxwriter.Workbook('funds.xlsx')
    worksheet = workbook.add_worksheet()

    # Add a bold format to use to highlight cells.
    bold = workbook.add_format({'bold': True})

    # Write the headers.
    worksheet.write('A1', '基金代码', bold)
    worksheet.write('B1', '基金名称', bold)

    row_num = 1
    for fund_info in all_funds:
        if len(fund_info) >= 3: # Ensure there's at least code, pinyin initial, and name
            fund_code = fund_info[0]
            fund_name = fund_info[2]
            worksheet.write(row_num, 0, fund_code)
            worksheet.write(row_num, 1, fund_name)
            row_num += 1
        else:
            print(f"Skipping malformed fund data: {fund_info}")

    try:
        workbook.close()
        print(f"Successfully wrote {row_num -1} funds to funds.xlsx")
    except xlsxwriter.exceptions.FileCreateError as e:
        print(f"Error writing XLSX file: {e}. Please ensure the file is not open elsewhere.")

if __name__ == '__main__':
    main()
