import asyncio
import os
import glob
import pandas as pd
import json
import yaml
import argparse
import sys
from playwright.async_api import async_playwright, TimeoutError
from openai import OpenAI

# Configuration
PAPER_DIR = "../paper"
COOKIES_PATH = "cookies.json"
TOKENS_PATH = "tokens.yaml"
BASE_URL = "https://www.qianwen.com/read"

# Load OpenAI config from tokens.yaml
def load_openai_client():
    if not os.path.exists(TOKENS_PATH):
        # Check if it exists in parent directory as a fallback
        alt_path = os.path.join("..", TOKENS_PATH)
        if os.path.exists(alt_path):
            with open(alt_path, 'r') as f:
                config = yaml.safe_load(f)
        else:
            print(f"Error: {TOKENS_PATH} not found.")
            sys.exit(1)
    else:
        with open(TOKENS_PATH, 'r') as f:
            config = yaml.safe_load(f)
            
    client = OpenAI(
        api_key=config['openai']['api_key'],
        base_url=config['openai']['base_url']
    )
    return client

async def upload_file(page, file_path):
    print(f"Uploading {file_path}...")
    await page.goto(BASE_URL, wait_until="networkidle")
    
    try:
        file_input = page.locator("input[type='file']")
        await file_input.set_input_files(file_path)
    except TimeoutError:
        print("Error: Could not find upload input. Are you logged in? Check cookies.json.")
        raise

    print("Waiting for upload and processing to begin...")
    await asyncio.sleep(5)

async def process_task_and_get_summary(page, filename):
    display_name = filename.replace(".pdf", "")
    print(f"Opening task for {display_name}...")
    
    await page.goto(BASE_URL, wait_until="networkidle")
    await asyncio.sleep(2)
    
    try:
        view_all = page.get_by_text("查看全部")
        if await view_all.is_visible():
            await view_all.click()
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(3)
    except Exception as e:
        print(f"Warning: Could not click '查看全部': {e}")

    try:
        # Looking for exact text match or containing text
        task_item = page.get_by_text(display_name, exact=True).first
        if not await task_item.is_visible():
            task_item = page.get_by_text(display_name).first
            
        print(f"Clicking on document: {display_name}...")
        await task_item.click()
        
        # Alternative click if navigation doesn't trigger
        await asyncio.sleep(2)
        if "read/" not in page.url:
             print("Trying alternative click approach...")
             await page.locator(f"div:has-text('{display_name}')").last.click()

        print("Waiting for reading interface to load...")
        await asyncio.sleep(8)
    except Exception as e:
        print(f"Failed to open document {display_name}: {e}")
        await page.screenshot(path=f"error_open_{filename}.png")
        raise
    
    # Extract Guide (Summary)
    print("Extracting summary...")
    summary_text = ""
    try:
        summary_locators = [
            "text=全文概述",
            "[class*='summary']",
            ".markdown-body",
            "article"
        ]
        for selector in summary_locators:
            loc = page.locator(selector).first
            if await loc.is_visible():
                if selector == "text=全文概述":
                    summary_text = await loc.evaluate("el => el.parentElement.innerText")
                else:
                    summary_text = await loc.inner_text()
                
                if len(summary_text) > 50:
                    break
        
        if not summary_text or len(summary_text) < 10:
            summary_text = await page.locator("main, [class*='page-container']").inner_text()
    except Exception as e:
        print(f"Error extracting summary: {e}")
        summary_text = "Error"

    return summary_text

def get_ai_answer(client, summary, custom_question):
    # Construct prompt with custom question and summary
    prompt = f"{custom_question}\n\n本文的概述如下：{summary}"
    print("Requesting AI analysis...")
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "你是一个学术辅助助手，擅长分析论文概述并回答问题。"},
            {"role": "user", "content": prompt}
        ]
    )
    
    ai_response = response.choices[0].message.content
    print(f"AI Response: {ai_response}")
    return ai_response

async def main():
    parser = argparse.ArgumentParser(description="AutoRead: Paper Analysis Tool")
    parser.add_argument("--question", type=str, required=True, help="The question to ask about the paper summary.")
    parser.add_argument("--output", type=str, default="answer.csv", help="Output CSV filename (default: answer.csv)")
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    cookies_file = os.path.join(script_dir, COOKIES_PATH)
    paper_dir = os.path.join(script_dir, PAPER_DIR)
    output_path = os.path.join(script_dir, args.output)
    screenshot_dir = os.path.join(script_dir, "chat_screenshots")
    
    os.makedirs(screenshot_dir, exist_ok=True)
    client = load_openai_client()

    if not os.path.exists(cookies_file):
        print(f"Error: {COOKIES_PATH} not found in {script_dir}.")
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 800}
        )
        
        with open(cookies_file, 'r') as f:
            cookies = json.load(f)
            valid_samesite = ["Strict", "Lax", "None"]
            for cookie in cookies:
                if "sameSite" in cookie:
                    ss = cookie["sameSite"].capitalize()
                    if ss == "No_restriction":
                        cookie["sameSite"] = "None"
                    elif ss not in valid_samesite:
                        cookie["sameSite"] = "None"
            await context.add_cookies(cookies)
            
        page = await context.new_page()
        
        results = []
        papers = sorted(glob.glob(os.path.join(paper_dir, "*.pdf")))
        
        for paper_path in papers:
            filename = os.path.basename(paper_path)
            print(f"--- Processing {filename} ---")
            try:
                # 1. Upload
                await upload_file(page, paper_path)
                
                # 2. Get Summary from Web
                summary = await process_task_and_get_summary(page, filename)
                
                # Take screenshot of the reading page for verification
                screenshot_path = os.path.join(screenshot_dir, f"view_{filename.replace('.pdf', '')}.png")
                await page.screenshot(path=screenshot_path)
                
                # 3. Get Answer via API using the custom question
                answer = get_ai_answer(client, summary, args.question)
                
                results.append({
                    "title": filename,
                    "summary": summary,
                    "answer": answer
                })
                print(f"Success: {filename} processed.")
                
            except Exception as e:
                print(f"Failed to process {filename}: {e}")
                await page.screenshot(path=os.path.join(script_dir, f"error_{filename}.png"))

        # Save to CSV
        if results:
            df = pd.DataFrame(results)
            df.to_csv(output_path, index=False)
            print(f"Final results saved to {output_path}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
