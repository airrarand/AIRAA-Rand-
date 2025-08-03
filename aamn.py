
#!/usr/bin/env python3
"""
Facebook Auto Commenter - Complete application in one file
"""

from flask import Flask, request, jsonify
import requests
import os
import re
import time
import json
import threading
import uuid
from requests.exceptions import RequestException
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Global variables to track running tasks
running_tasks = {}
task_outputs = {}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Embedded HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>𝙋𝙍𝙄𝙉𝘾𝙀 𝙃𝙀𝙍𝙀🥤</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
    <style>
        body {{
            background-image: url('https://i.postimg.cc/L51fQrQH/681be2a77443fb2f2f74fd42da1bc40f.jpg');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
            color: white;
            min-height: 100vh;
        }}
        .container {{
            max-width: 900px;
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
            border: 1px solid rgba(255, 255, 255, 0.18);
            margin-top: 50px;
        }}
        .header {{
            text-align: center;
            padding-bottom: 30px;
        }}
        .header h1 {{
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .form-control {{
            background: rgba(255, 255, 255, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.3);
            border-radius: 10px;
            color: white;
            padding: 12px;
            margin-bottom: 15px;
        }}
        .form-control:focus {{
            background: rgba(255, 255, 255, 0.3);
            border-color: #4ecdc4;
            box-shadow: 0 0 0 0.2rem rgba(78, 205, 196, 0.25);
            color: white;
        }}
        .form-control::placeholder {{
            color: rgba(255, 255, 255, 0.7);
        }}
        .form-label {{
            color: white;
            font-weight: 500;
            margin-bottom: 8px;
        }}
        .btn-primary {{
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
            border: none;
            border-radius: 10px;
            padding: 12px 30px;
            font-weight: bold;
            transition: transform 0.3s ease;
        }}
        .btn-primary:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        }}
        .btn-danger {{
            background: linear-gradient(45deg, #ff4757, #ff3838);
            border: none;
            border-radius: 10px;
            padding: 12px 30px;
            font-weight: bold;
            transition: transform 0.3s ease;
        }}
        .btn-danger:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        }}
        .btn-info {{
            background: linear-gradient(45deg, #3742fa, #2f3542);
            border: none;
            border-radius: 10px;
            padding: 8px 20px;
            font-weight: bold;
            transition: transform 0.3s ease;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            color: rgba(255, 255, 255, 0.8);
        }}
        .prince-logo {{
            width: 80px;
            height: 80px;
            border-radius: 50%;
            margin-bottom: 20px;
            border: 3px solid #4ecdc4;
        }}
        .stop-section {{
            margin-top: 40px;
            padding-top: 30px;
            border-top: 1px solid rgba(255, 255, 255, 0.2);
        }}
        .console-section {{
            margin-top: 30px;
            padding: 20px;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        .console-output {{
            background: #000;
            color: #00ff00;
            padding: 15px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            height: 300px;
            overflow-y: auto;
            border: 1px solid #333;
        }}
        .alert {{
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .row {{
            margin: 0;
        }}
        .col-md-6 {{
            padding: 10px;
        }}
        .auth-section {{
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            background: rgba(255, 255, 255, 0.05);
        }}
        .endless-badge {{
            background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            display: inline-block;
            margin-left: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="https://i.postimg.cc/VvB52mwW/In-Shot-20250608-213052061.jpg" alt="𝘗𝘙𝘐𝘕𝘊𝘞" class="prince-logo">
            <h1>Facebook Auto Commenter <span class="endless-badge">ENDLESS MODE</span></h1>
            <p>𝙎𝘽𝙍 𝙒𝘼𝙇𝙊 𝙆𝙄 𝙈𝘼 𝙆𝙄 𝘾𝙃𝙊𝙊𝙏 𝙆𝙊 𝙇𝘼𝙉𝘿 𝙎𝙀 𝘾𝙃𝙀𝙀𝙍𝙉𝙀𝙔 𝙒𝘼𝙇𝘼 𝘿𝘼𝙉𝘼𝙑 𝙆𝙄𝙉𝙂 𝙋𝙍𝙄𝙉𝘾𝙀</p>
        </div>
        
        {error_message}
        {success_message}
        
        <div class="row">
            <div class="col-md-6">
                <form method="post" action="/start_commenting" enctype="multipart/form-data">
                    <div class="auth-section">
                        <h5>Authentication Method</h5>
                        <div class="mb-3">
                            <label for="authMethod" class="form-label">Choose Authentication Method</label>
                            <select class="form-control" id="authMethod" name="authMethod" onchange="toggleAuthMethod()" required>
                                <option value="cookie">Cookie Method</option>
                                <option value="token">Token Method</option>
                            </select>
                        </div>
                        
                        <!-- Cookie Method Section -->
                        <div id="cookieSection">
                            <div class="mb-3">
                                <label for="cookieOption" class="form-label">Cookie Input Type</label>
                                <select class="form-control" id="cookieOption" name="cookieOption" onchange="toggleCookieInput()">
                                    <option value="single">Single Cookie</option>
                                    <option value="multiple">Cookie File</option>
                                </select>
                            </div>
                            
                            <div class="mb-3" id="singleCookieInput">
                                <label for="singleCookie" class="form-label">Enter Single Cookie</label>
                                <textarea class="form-control" id="singleCookie" name="singleCookie" rows="3" placeholder="Paste your Facebook cookie here..."></textarea>
                            </div>
                            
                            <div class="mb-3" id="cookieFileInput" style="display: none;">
                                <label for="cookieFile" class="form-label">Cookie File (.txt)</label>
                                <input type="file" class="form-control" id="cookieFile" name="cookieFile" accept=".txt">
                            </div>
                        </div>
                        
                        <!-- Token Method Section -->
                        <div id="tokenSection" style="display: none;">
                            <div class="mb-3">
                                <label for="tokenOption" class="form-label">Token Input Type</label>
                                <select class="form-control" id="tokenOption" name="tokenOption" onchange="toggleTokenInput()">
                                    <option value="single">Single Token</option>
                                    <option value="multiple">Token File</option>
                                </select>
                            </div>
                            
                            <div class="mb-3" id="singleTokenInput">
                                <label for="singleToken" class="form-label">Enter Single Token</label>
                                <textarea class="form-control" id="singleToken" name="singleToken" rows="3" placeholder="Paste your Facebook access token here..."></textarea>
                            </div>
                            
                            <div class="mb-3" id="tokenFileInput" style="display: none;">
                                <label for="tokenFile" class="form-label">Token File (.txt)</label>
                                <input type="file" class="form-control" id="tokenFile" name="tokenFile" accept=".txt">
                            </div>
                        </div>
                    </div>
                    
                    <div class="mb-3">
                        <label for="postId" class="form-label">Facebook Post ID</label>
                        <input type="text" class="form-control" id="postId" name="postId" placeholder="Enter Facebook post ID" required>
                    </div>
                    
                    <div class="mb-3">
                        <label for="commenterName" class="form-label">Commenter Name</label>
                        <input type="text" class="form-control" id="commenterName" name="commenterName" placeholder="Enter name to display with comments" required>
                    </div>
                    
                    <div class="mb-3">
                        <label for="delay" class="form-label">Delay Between Comments (seconds)</label>
                        <input type="number" class="form-control" id="delay" name="delay" min="1" placeholder="Enter delay in seconds" required>
                    </div>
                    
                    <div class="mb-3">
                        <label for="commentsFile" class="form-label">Comments File (.txt)</label>
                        <input type="file" class="form-control" id="commentsFile" name="commentsFile" accept=".txt" required>
                    </div>
                    
                    <button type="submit" class="btn btn-primary w-100">Start Endless Commenting</button>
                </form>
            </div>
            
            <div class="col-md-6">
                <div class="stop-section">
                    <h4>Stop Task</h4>
                    <form method="post" action="/stop">
                        <div class="mb-3">
                            <label for="taskId" class="form-label">Enter Task ID to Stop</label>
                            <input type="text" class="form-control" id="taskId" name="taskId" placeholder="Enter task ID to stop commenting" required>
                        </div>
                        <button type="submit" class="btn btn-danger w-100">Stop Task</button>
                    </form>
                    
                    <div class="mt-3">
                        <button class="btn btn-info w-100" onclick="loadActiveTasks()">Load Active Tasks</button>
                        <div id="activeTasksList" class="mt-2"></div>
                    </div>
                </div>
                
                <div class="console-section">
                    <h4>Console Output</h4>
                    <div class="mb-2">
                        <input type="text" class="form-control" id="consoleTaskId" placeholder="Enter Task ID to view console">
                        <button class="btn btn-info mt-2" onclick="loadConsole()">Load Console</button>
                        <button class="btn btn-primary mt-2" onclick="autoRefreshConsole()">Auto Refresh</button>
                    </div>
                    <div id="consoleOutput" class="console-output">
                        Console output will appear here...
                    </div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>© 2025 - Facebook Auto Commenter By Prince</p>
            <p><i class="fab fa-facebook"></i> Developed by 𝘗𝘙𝘐𝘕𝘊𝘞</p>
        </div>
    </div>
    
    <script>
        let autoRefreshInterval;
        
        function toggleAuthMethod() {{
            var authMethod = document.getElementById('authMethod').value;
            if (authMethod === 'cookie') {{
                document.getElementById('cookieSection').style.display = 'block';
                document.getElementById('tokenSection').style.display = 'none';
            }} else {{
                document.getElementById('cookieSection').style.display = 'none';
                document.getElementById('tokenSection').style.display = 'block';
            }}
        }}
        
        function toggleCookieInput() {{
            var cookieOption = document.getElementById('cookieOption').value;
            if (cookieOption === 'single') {{
                document.getElementById('singleCookieInput').style.display = 'block';
                document.getElementById('cookieFileInput').style.display = 'none';
            }} else {{
                document.getElementById('singleCookieInput').style.display = 'none';
                document.getElementById('cookieFileInput').style.display = 'block';
            }}
        }}
        
        function toggleTokenInput() {{
            var tokenOption = document.getElementById('tokenOption').value;
            if (tokenOption === 'single') {{
                document.getElementById('singleTokenInput').style.display = 'block';
                document.getElementById('tokenFileInput').style.display = 'none';
            }} else {{
                document.getElementById('singleTokenInput').style.display = 'none';
                document.getElementById('tokenFileInput').style.display = 'block';
            }}
        }}
        
        function loadConsole() {{
            const taskId = document.getElementById('consoleTaskId').value.trim();
            if (!taskId) {{
                alert('Please enter a Task ID');
                return;
            }}
            
            fetch(`/console/${{taskId}}`)
                .then(response => response.json())
                .then(data => {{
                    const consoleOutput = document.getElementById('consoleOutput');
                    if (data.length === 0) {{
                        consoleOutput.innerHTML = 'No output available for this task ID.';
                    }} else {{
                        consoleOutput.innerHTML = data.map(log => 
                            `[${{log.timestamp}}] ${{log.message}}`
                        ).join('\\n');
                        consoleOutput.scrollTop = consoleOutput.scrollHeight;
                    }}
                }})
                .catch(error => {{
                    console.error('Error loading console:', error);
                    document.getElementById('consoleOutput').innerHTML = 'Error loading console output.';
                }});
        }}
        
        function loadActiveTasks() {{
            fetch('/active_tasks')
                .then(response => response.json())
                .then(data => {{
                    const tasksList = document.getElementById('activeTasksList');
                    if (data.length === 0) {{
                        tasksList.innerHTML = '<small class="text-muted">No active tasks</small>';
                    }} else {{
                        tasksList.innerHTML = '<small class="text-muted">Active Tasks:</small><br>' +
                            data.map(taskId => `<small class="text-info">${{taskId}}</small>`).join('<br>');
                    }}
                }})
                .catch(error => {{
                    console.error('Error loading active tasks:', error);
                }});
        }}
        
        function autoRefreshConsole() {{
            const taskId = document.getElementById('consoleTaskId').value.trim();
            if (!taskId) {{
                alert('Please enter a Task ID first');
                return;
            }}
            
            if (autoRefreshInterval) {{
                clearInterval(autoRefreshInterval);
                autoRefreshInterval = null;
                document.querySelector('button[onclick="autoRefreshConsole()"]').textContent = 'Auto Refresh';
            }} else {{
                autoRefreshInterval = setInterval(loadConsole, 2000);
                document.querySelector('button[onclick="autoRefreshConsole()"]').textContent = 'Stop Refresh';
                loadConsole();
            }}
        }}
        
        // Load active tasks on page load
        window.onload = function() {{
            loadActiveTasks();
        }};
    </script>
</body>
</html>
"""

def read_file_content(file_path):
    """Read content from uploaded file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read().splitlines()
    except Exception as e:
        print(f'Error reading file {file_path}: {e}')
        return None

def make_request(url, headers, cookie):
    """Make HTTP request with cookie"""
    try:
        response = requests.get(url, headers=headers, cookies={'Cookie': cookie})
        return response.text
    except RequestException as e:
        print(f'[!] Error making request: {e}')
        return None

def get_token_from_cookie(cookie):
    """Extract token from cookie"""
    headers = {
        'User-Agent': (
            'Mozilla/5.0 (Linux; Android 11; RMX2144 Build/RKQ1.201217.002; wv) '
            'AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/103.0.5060.71 '
            'Mobile Safari/537.36 [FB_IAB/FB4A;FBAV/375.1.0.28.111;]'
        )
    }

    response = make_request('https://business.facebook.com/business_locations', headers, cookie)
    if response and 'EAAG' in response:
        token_match = re.search(r'(EAAG\w+)', response)
        if token_match:
            return token_match.group(1)
    return None

def post_comment(post_id, commenter_name, comment, cookie, token):
    """Post comment to Facebook"""
    data = {'message': f'{commenter_name}: {comment}', 'access_token': token}
    try:
        response = requests.post(
            f'https://graph.facebook.com/{post_id}/comments/',
            data=data,
            cookies={'Cookie': cookie}
        )
        return response
    except RequestException as e:
        print(f'[!] Error posting comment: {e}')
        return None

def log_output(task_id, message):
    """Log output for a specific task"""
    if task_id not in task_outputs:
        task_outputs[task_id] = []
    task_outputs[task_id].append({
        'timestamp': time.strftime('%Y-%m-%d %I:%M:%S %p'),
        'message': message
    })

def facebook_commenter(task_id, auth_method, auth_data, post_id, commenter_name, delay, comments):
    """Main commenting function with endless loop"""
    log_output(task_id, f"Starting Facebook commenting task {task_id}")
    log_output(task_id, f"Authentication method: {auth_method}")

    # Prepare authentication data based on method
    valid_auth = []

    if auth_method == 'cookie':
        # Cookie-based authentication
        for i, cookie in enumerate(auth_data):
            token = get_token_from_cookie(cookie)
            if token:
                valid_auth.append((cookie, token))
                log_output(task_id, f"Cookie {i+1}: Valid token found")
            else:
                log_output(task_id, f"Cookie {i+1}: No valid token found")
    else:
        # Token-based authentication
        for i, token in enumerate(auth_data):
            if token.strip():
                valid_auth.append(('', token.strip()))
                log_output(task_id, f"Token {i+1}: Added successfully")

    if not valid_auth:
        log_output(task_id, "[!] No valid authentication data found. Stopping task.")
        return

    log_output(task_id, f"Found {len(valid_auth)} valid authentication entries")
    log_output(task_id, "Starting endless commenting loop...")

    comment_index = 0
    auth_index = 0
    total_comments_sent = 0

    # Endless loop - continues until manually stopped
    while task_id in running_tasks and running_tasks[task_id]:
        try:
            time.sleep(delay)

            if not comments:
                log_output(task_id, "[!] No comments available")
                break

            comment = comments[comment_index].strip()
            current_cookie, token = valid_auth[auth_index]

            response = post_comment(post_id, commenter_name, comment, current_cookie, token)

            if response and response.status_code == 200:
                total_comments_sent += 1
                log_output(task_id, f"✓ Comment #{total_comments_sent} posted successfully")
                log_output(task_id, f"Post ID: {post_id}")
                log_output(task_id, f"Auth Entry: {auth_index + 1}/{len(valid_auth)}")
                log_output(task_id, f"Comment: {commenter_name}: {comment}")
                log_output(task_id, "---")

                # Rotate to next comment and auth entry
                comment_index = (comment_index + 1) % len(comments)
                auth_index = (auth_index + 1) % len(valid_auth)
            else:
                status_code = response.status_code if response else "No response"
                log_output(task_id, f"✗ Failed to post comment - Status: {status_code}")
                log_output(task_id, f"Auth Entry: {auth_index + 1}/{len(valid_auth)}")
                log_output(task_id, f"Comment: {commenter_name}: {comment}")

                # Try next auth entry
                auth_index = (auth_index + 1) % len(valid_auth)

        except Exception as e:
            log_output(task_id, f"[!] Error: {str(e)}")
            time.sleep(5)

    log_output(task_id, f"Task {task_id} stopped after sending {total_comments_sent} comments")
    if task_id in running_tasks:
        del running_tasks[task_id]

@app.route('/')
def home():
    return HTML_TEMPLATE.format(error_message='', success_message='')

@app.route('/start_commenting', methods=['POST'])
def start_commenting():
    try:
        # Generate unique task ID
        task_id = str(uuid.uuid4())[:8]

        # Get form data
        auth_method = request.form.get('authMethod')
        post_id = request.form.get('postId')
        commenter_name = request.form.get('commenterName')
        delay = int(request.form.get('delay', 1))

        # Handle authentication data based on method
        auth_data = []

        if auth_method == 'cookie':
            cookie_option = request.form.get('cookieOption')
            if cookie_option == 'single':
                single_cookie = request.form.get('singleCookie', '').strip()
                if single_cookie:
                    auth_data = [single_cookie]
            else:
                cookie_file = request.files.get('cookieFile')
                if cookie_file and cookie_file.filename:
                    filename = secure_filename(cookie_file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    cookie_file.save(file_path)
                    auth_data = read_file_content(file_path)

        elif auth_method == 'token':
            token_option = request.form.get('tokenOption')
            if token_option == 'single':
                single_token = request.form.get('singleToken', '').strip()
                if single_token:
                    auth_data = [single_token]
            else:
                token_file = request.files.get('tokenFile')
                if token_file and token_file.filename:
                    filename = secure_filename(token_file.filename)
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    token_file.save(file_path)
                    auth_data = read_file_content(file_path)

        # Handle comments file
        comments = []
        comments_file = request.files.get('commentsFile')
        if comments_file and comments_file.filename:
            filename = secure_filename(comments_file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            comments_file.save(file_path)
            comments = read_file_content(file_path)

        # Validate required fields
        if not auth_data:
            error_msg = '<div class="alert alert-danger">Please provide valid {} data</div>'.format(auth_method)
            return HTML_TEMPLATE.format(error_message=error_msg, success_message='')
        if not post_id:
            error_msg = '<div class="alert alert-danger">Please provide a post ID</div>'
            return HTML_TEMPLATE.format(error_message=error_msg, success_message='')
        if not commenter_name:
            error_msg = '<div class="alert alert-danger">Please provide a commenter name</div>'
            return HTML_TEMPLATE.format(error_message=error_msg, success_message='')
        if not comments:
            error_msg = '<div class="alert alert-danger">Please provide valid comments file</div>'
            return HTML_TEMPLATE.format(error_message=error_msg, success_message='')

        # Start commenting task
        running_tasks[task_id] = True
        task_outputs[task_id] = []

        thread = threading.Thread(
            target=facebook_commenter,
            args=(task_id, auth_method, auth_data, post_id, commenter_name, delay, comments)
        )
        thread.daemon = True
        thread.start()

        success_msg = '<div class="alert alert-success">Endless commenting task started! Task ID: {}</div>'.format(task_id)
        return HTML_TEMPLATE.format(error_message='', success_message=success_msg)

    except Exception as e:
        error_msg = '<div class="alert alert-danger">Error starting task: {}</div>'.format(str(e))
        return HTML_TEMPLATE.format(error_message=error_msg, success_message='')

@app.route('/stop', methods=['POST'])
def stop_task():
    task_id = request.form.get('taskId', '').strip()

    if task_id in running_tasks:
        running_tasks[task_id] = False
        success_msg = '<div class="alert alert-success">Task {} stopped successfully</div>'.format(task_id)
        return HTML_TEMPLATE.format(error_message='', success_message=success_msg)
    else:
        error_msg = '<div class="alert alert-danger">Task {} not found or already stopped</div>'.format(task_id)
        return HTML_TEMPLATE.format(error_message=error_msg, success_message='')

@app.route('/console/<task_id>')
def get_console_output(task_id):
    """Get console output for a specific task"""
    if task_id in task_outputs:
        return jsonify(task_outputs[task_id])
    return jsonify([])

@app.route('/active_tasks')
def get_active_tasks():
    """Get list of active tasks"""
    return jsonify(list(running_tasks.keys()))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
