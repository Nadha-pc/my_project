import os
import pyautogui
import pygetwindow as gw
import base64
import requests
import io
from PIL import Image
from window_focus import activate_windowt_title

# Load API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("API key not found. Set the environment variable OPENAI_API_KEY.")


# Function to focus a window given its title
def focus_window(window_title):
    try:
        window = gw.getWindowsWithTitle(window_title)[0]  # Get the first window with the specific title
        window.activate()
        pyautogui.sleep(0.3)  # Allow some time for the window to come into focus
        return window
    except IndexError:
        print(f'No window with title "{window_title}" found.')
        return None


# Function to capture a screenshot of the specified window
def capture_screenshot(window=None, region=None):
    if region is not None:
        screenshot = pyautogui.screenshot(region=region)
    elif window is not None:
        window_box = window.box
        screenshot = pyautogui.screenshot(region=(window_box.left, window_box.top, window_box.width, window_box.height))
    else:
        screenshot = pyautogui.screenshot()
    return screenshot


# Function to encode image data to base64
def encode_image(image_data):
    return base64.b64encode(image_data).decode('utf-8')


# Function to analyze an image using OpenAI API
def analyze_image(base64_image, window_title, additional_context='What’s in this image?'):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": f"{additional_context}"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    return response.json()


# Function to both capture and analyze a specific region screenshot
def imaging(window_title=None, additional_context=None, x=None, y=None, screenshot_size=None):
    window = None
    region = None

    if screenshot_size == 'Full screen':
        pass
    elif window_title:
        window = focus_window(window_title)
        if not window:
            return None  
        if screenshot_size and isinstance(screenshot_size, tuple) and x is not None and y is not None:
            offset_x, offset_y = screenshot_size[0] // 2, screenshot_size[1] // 2
            window_box = window.box
            region = (
                window_box.left + x - offset_x, window_box.top + y - offset_y, screenshot_size[0], screenshot_size[1]
            )
        else:
            region = (window.box.left, window.box.top, window.box.width, window.box.height)

    screenshot = capture_screenshot(window, region)

    # Paste the cursor onto the screenshot
    cursor_img_path = r'media\Mouse_pointer_small.png'
    with Image.open(cursor_img_path) as cursor:
        cursor = cursor.convert("RGBA")  

        x_cursor, y_cursor = pyautogui.position()  

        if region:
            cursor_pos = (x_cursor - region[0], y_cursor - region[1])
        else:
            cursor_pos = (x_cursor, y_cursor)

        screenshot.paste(cursor, cursor_pos, cursor)

    # Convert the screenshot to bytes
    with io.BytesIO() as output_bytes:
        screenshot.save(output_bytes, 'PNG')
        bytes_data = output_bytes.getvalue()

    # Convert the bytes to a base64-encoded image and analyze
    base64_image = encode_image(bytes_data)
    analysis_result = analyze_image(base64_image, window_title, additional_context)

    return analysis_result


if __name__ == "__main__":
    app_name = "Firefox"
    coordinates = {'x': 132, 'y': 458}
    screenshot_size = (300, 300)
    x = coordinates['x']
    y = coordinates['y']
    pyautogui.moveTo(x, y, 0.5, pyautogui.easeOutQuad)
    single_step = "click on the 'Add a comment...' text input area"

    # Call imaging with the additional_context parameter
    element_analysis = (
        f"You are an AI Agent called Element Analyzer that receives a screenshot of the element and analyzes it to check if the mouse is in the correct position to click the element to interact with.\n"
        f"Element to interact with: {single_step}\nRespond only with \"Yes\" or \"No\"."
    )
    analysis_result = imaging(window_title=app_name, additional_context=element_analysis, x=x, y=y, screenshot_size=screenshot_size)
    print(analysis_result)
