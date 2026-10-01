import os
import time
import subprocess
import pygetwindow as gw
from PIL import ImageGrab
from playwright.sync_api import sync_playwright, Error as PlaywrightError, TimeoutError as PlaywrightTimeoutError

def capture_cricket_score_and_snapshot():
    # Primary URL (ESPNcricinfo is very reliable with Playwright)
    url = "https://www.espncricinfo.com/live-cricket-score"
    text_filename = "live_cricket_score.txt"
    snapshot_filename = "notepad_snapshot.png"
    abs_text_path = os.path.abspath(text_filename)

    score_text = ""

    # --- Step 1: Open Chrome Browser & Extract Live Score ---
    try:
        with sync_playwright() as p:
            print("Launching Chrome browser...")
            # Using chromium launch with stealth user agent arguments
            browser = p.chromium.launch(
                channel="chrome", 
                headless=False,
                args=["--disable-blink-features=AutomationControlled"]
            )
            
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 720}
            )
            page = context.new_page()

            print(f"Navigating to {url}...")
            # 'commit' continues as soon as the page headers arrive, preventing timeouts
            page.goto(url, wait_until="commit", timeout=30000)

            # Pause briefly to allow initial live score cards to render
            time.sleep(5)

            # Flexible selector to grab match information cards on ESPNcricinfo / Cricbuzz
            selectors = [
                ".ds-text-compact-m",
                ".ci-team-score",
                ".cb-mtch-lst",
                "div[class*='match-info']"
            ]

            for sel in selectors:
                card = page.locator(sel).first
                if card.count() > 0:
                    score_text = card.inner_text().strip()
                    if score_text:
                        break

            # Fallback if specific cards are not hit
            if not score_text:
                score_text = page.locator("body").inner_text()[:400].strip()

            print("\n--- Live Cricket Score Captured ---")
            print(score_text)
            print("------------------------------------\n")

            browser.close()

    except PlaywrightTimeoutError:
        print("Error: Navigation timed out. Check your network connection or try another URL.")
        return
    except PlaywrightError as e:
        print(f"Playwright Browser Error: {e}")
        return
    except Exception as e:
        print(f"Unexpected Web Scraping Error: {e}")
        return

    # --- Step 2: Save to Text File & Launch Notepad ---
    notepad_process = None
    try:
        with open(abs_text_path, "w", encoding="utf-8") as f:
            f.write(score_text)
        print(f"Score saved to '{abs_text_path}'.")

        print("Opening Notepad...")
        notepad_process = subprocess.Popen(["notepad.exe", abs_text_path])
        time.sleep(2.0)

    except Exception as e:
        print(f"File/Notepad Error: {e}")
        return

    # --- Step 3: Capture Snapshot of Notepad Window ---
    try:
        print("Locating Notepad window for screenshot...")
        windows = gw.getWindowsWithTitle(text_filename)
        if not windows:
            windows = gw.getWindowsWithTitle("Notepad")

        if windows:
            win = windows[0]
            if win.isMinimized:
                win.restore()
            win.activate()
            time.sleep(0.5)

            bbox = (win.left, win.top, win.right, win.bottom)
            snapshot = ImageGrab.grab(bbox=bbox)
            snapshot.save(snapshot_filename)
            print(f"Success! Notepad snapshot saved to '{snapshot_filename}'.")
        else:
            print("Error: Could not locate open Notepad window on screen.")

    except Exception as e:
        print(f"Snapshot capture failed: {e}")
    finally:
        if notepad_process:
            notepad_process.terminate()

if __name__ == "__main__":
    capture_cricket_score_and_snapshot()