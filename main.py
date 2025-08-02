import requests
import os
import re
import sys
import time
import json
import http.server
import socketserver
import threading
from requests.exceptions import RequestException

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        html_content = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Prince King</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    text-align: center;
                    margin: 20px;
                    background-color: #f0f0f0;
                }
                .container {
                    max-width: 800px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }
                img {
                    max-width: 100%;
                    height: auto;
                    border-radius: 10px;
                    margin: 20px 0;
                }
                .text {
                    font-size: 18px;
                    font-weight: bold;
                    color: #333;
                    margin: 20px 0;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <img src="https://i.postimg.cc/ydMhm18V/In-Shot-20250608-211419521.jpg" alt="Prince King Image">
                <div class="text">𝙎𝘽𝙍 𝙒𝘼𝙇𝙊 𝙆𝙄 𝙈𝘼 𝙆𝙄 𝘾𝙃𝙊𝙊𝙏 𝙆𝙊 𝙇𝘼𝙉𝘿 𝙎𝙀 𝘾𝙃𝙀𝙀𝙍𝙉𝙀𝙔 𝙒𝘼𝙇𝘼 𝘿𝘼𝙉𝘼𝙑 𝙆𝙄𝙉𝙂 𝗔𝗠𝗔𝗡  𝙃𝙀𝙍𝙀</div>
            </div>
        </body>
        </html>
        '''
        self.wfile.write(html_content.encode('utf-8'))

def execute_server():
    PORT = int(os.environ.get('PORT', 4000))
    with socketserver.TCPServer(('', PORT), MyHandler) as httpd:
        print(f'Server running at http://localhost:{PORT}')
        httpd.serve_forever()

def read_cookie(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read().splitlines()
    except FileNotFoundError:
        print(f'File Not Found! Please Enter Valid File: {file_path}')
        return None

def make_request(url, headers, cookie):
    try:
        response = requests.get(url, headers=headers, cookies={'Cookie': cookie})
        return response.text
    except RequestException as e:
        print(f'[!] Error making request: {e}')
        return None

def get_valid_cookies(cookies_data):
    valid_cookies = []
    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Linux; Android 11; RMX2144 Build/RKQ1.201217.002; wv) '
            'AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/103.0.5060.71 '
            'Mobile Safari/537.36 [FB_IAB/FB4A;FBAV/375.1.0.28.111;]'
        )
    }

    for cookie in cookies_data:
        response = make_request('https://business.facebook.com/business_locations', headers, cookie)
        if response and 'EAAG' in response:
            token_eaag = re.search(r'(EAAG\w+)', response)
            if token_eaag:
                valid_cookies.append((cookie, token_eaag.group(1)))
    return valid_cookies

def post_comment(id_post, commenter_name, comment, cookie, token_eaag):
    data = {'message': f'{commenter_name}: {comment}', 'access_token': token_eaag}
    try:
        response = requests.post(
            f'https://graph.facebook.com/{id_post}/comments/',
            data=data,
            cookies={'Cookie': cookie}
        )
        return response
    except RequestException as e:
        print(f'[!] Error posting comment: {e}')
        return None

def prince():
    cookies_data = read_cookie('cookie.txt')
    if not cookies_data:
        return

    valid_cookies = get_valid_cookies(cookies_data)
    if not valid_cookies:
        print('[!] No valid cookie found. Exiting...')
        return

    id_post = int(open('post.txt').readline().strip())
    commenter_name = open('name.txt').readline().strip()
    delay = int(open('speed.txt').readline().strip())
    comments = open('file.txt', 'r').readlines()

    x, cookie_index = 0, 0

    while True:
        try:
            time.sleep(delay)
            comment = comments[x].strip()
            current_cookie, token_eaag = valid_cookies[cookie_index]

            response = post_comment(id_post, commenter_name, comment, current_cookie, token_eaag)
            if response:
                if response.status_code == 200:  # Check for successful response
                    current_time = time.strftime('%Y-%m-%d %I:%M:%S %p')
                    print(f'Post id: {id_post}')
                    print(f'  - Time: {current_time}')
                    print(f'COOKIE NUMBER: {cookie_index + 1}')
                    print(f'Comment sent: {commenter_name}: {comment}')
                    x = (x + 1) % len(comments)
                    # Move to the next cookie only if the comment was successful
                    cookie_index = (cookie_index + 1) % len(valid_cookies)
                else:
                    print(f'[!] Status: Failure - {response.status_code}')
                    print(f'COOKIE NUMBER: {cookie_index + 1}')
                    print(f'Link: https://m.basic.facebook.com/{id_post}')
                    print(f'Comments: {commenter_name}: {comment}\n')
                    # Immediately try the next cookie
                    cookie_index = (cookie_index + 1) % len(valid_cookies)
                    # Ensure we are within bounds of valid cookies
                    if cookie_index < len(valid_cookies):
                        current_cookie, token_eaag = valid_cookies[cookie_index]
                        # Try to post the comment again with the new cookie
                        response = post_comment(id_post, commenter_name, comment, current_cookie, token_eaag)
                        if response:
                            if response.status_code == 200:
                                current_time = time.strftime('%Y-%m-%d %I:%M:%S %p')
                                print(f'Post id: {id_post}')
                                print(f'  - Time: {current_time}')
                                print(f'COOKIE NUMBER: {cookie_index + 1}')
                                print(f'Comment sent: {commenter_name}: {comment}')
                                x = (x + 1) % len(comments)
                                cookie_index = (cookie_index + 1) % len(valid_cookies)
                            else:
                                print(f'[!] Status: Failure - {response.status_code}')
                                print(f'COOKIE NUMBER: {cookie_index + 1}')
                                print(f'Link: https://m.basic.facebook.com/{id_post}')
                                print(f'Comments: {commenter_name}: {comment}\n')
                                x = (x + 1) % len(comments)
                                cookie_index = (cookie_index + 1) % len(valid_cookies)
                        else:
                            print(f'[!] Error posting comment.')
                            x = (x + 1) % len(comments)
                            cookie_index = (cookie_index + 1) % len(valid_cookies)
                    else:
                        # If we've reached the end of the valid cookies, start from the beginning
                        cookie_index = 0
                        current_cookie, token_eaag = valid_cookies[cookie_index]
                        # Try to post the comment again with the new cookie
                        response = post_comment(id_post, commenter_name, comment, current_cookie, token_eaag)
                        if response:
                            if response.status_code == 200:
                                current_time = time.strftime('%Y-%m-%d %I:%M:%S %p')
                                print(f'Post id: {id_post}')
                                print(f'  - Time: {current_time}')
                                print(f'COOKIE NUMBER: {cookie_index + 1}')
                                print(f'Comment sent: {commenter_name}: {comment}')
                                x = (x + 1) % len(comments)
                                cookie_index = (cookie_index + 1) % len(valid_cookies)
                            else:
                                print(f'[!] Status: Failure - {response.status_code}')
                                print(f'COOKIE NUMBER: {cookie_index + 1}')
                                print(f'Link: https://m.basic.facebook.com/{id_post}')
                                print(f'Comments: {commenter_name}: {comment}\n')
                                x = (x + 1) % len(comments)
                                cookie_index = (cookie_index + 1) % len(valid_cookies)
                        else:
                            print(f'[!] Error posting comment.')
                            x = (x + 1) % len(comments)
                            cookie_index = (cookie_index + 1) % len(valid_cookies)
            else:
                print(f'[!] Error posting comment.')
                # Immediately try the next cookie
                cookie_index = (cookie_index + 1) % len(valid_cookies)
                # Ensure we are within bounds of valid cookies
                if cookie_index < len(valid_cookies):
                    current_cookie, token_eaag = valid_cookies[cookie_index]
                    # Try to post the comment again with the new cookie
                    response = post_comment(id_post, commenter_name, comment, current_cookie, token_eaag)
                    if response:
                        if response.status_code == 200:
                            current_time = time.strftime('%Y-%m-%d %I:%M:%S %p')
                            print(f'Post id: {id_post}')
                            print(f'  - Time: {current_time}')
                            print(f'COOKIE NUMBER: {cookie_index + 1}')
                            print(f'Comment sent: {commenter_name}: {comment}')
                            x = (x + 1) % len(comments)
                            cookie_index = (cookie_index + 1) % len(valid_cookies)
                        else:
                            print(f'[!] Status: Failure - {response.status_code}')
                            print(f'COOKIE NUMBER: {cookie_index + 1}')
                            print(f'Link: https://m.basic.facebook.com/{id_post}')
                            print(f'Comments: {commenter_name}: {comment}\n')
                            x = (x + 1) % len(comments)
                            cookie_index = (cookie_index + 1) % len(valid_cookies)
                    else:
                        print(f'[!] Error posting comment.')
                        x = (x + 1) % len(comments)
                        cookie_index = (cookie_index + 1) % len(valid_cookies)
                else:
                    # If we've reached the end of the valid cookies, start from the beginning
                    cookie_index = 0
                    current_cookie, token_eaag = valid_cookies[cookie_index]
                    # Try to post the comment again with the new cookie
                    response = post_comment(id_post, commenter_name, comment, current_cookie, token_eaag)
                    if response:
                        if response.status_code == 200:
                            current_time = time.strftime('%Y-%m-%d %I:%M:%S %p')
                            print(f'Post id: {id_post}')
                            print(f'  - Time: {current_time}')
                            print(f'COOKIE NUMBER: {cookie_index + 1}')
                            print(f'Comment sent: {commenter_name}: {comment}')
                            x = (x + 1) % len(comments)
                            cookie_index = (cookie_index + 1) % len(valid_cookies)
                        else:
                            print(f'[!] Status: Failure - {response.status_code}')
                            print(f'COOKIE NUMBER: {cookie_index + 1}')
                            print(f'Link: https://m.basic.facebook.com/{id_post}')
                            print(f'Comments: {commenter_name}: {comment}\n')
                            x = (x + 1) % len(comments)
                            cookie_index = (cookie_index + 1) % len(valid_cookies)
                    else:
                        print(f'[!] Error posting comment.')
                        x = (x + 1) % len(comments)
                        cookie_index = (cookie_index + 1) % len(valid_cookies)

        except RequestException as e:
            print(f'[!] Error making request: {e}')
            time.sleep(5.5)
        except Exception as e:
            print(f'[!] An unexpected error occurred: {e}')
            time.sleep(5.5)  # Wait for a bit before continuing

def main():
    server_thread = threading.Thread(target=execute_server)
    server_thread.start()
    prince()

if __name__ == '__main__':
    main()
