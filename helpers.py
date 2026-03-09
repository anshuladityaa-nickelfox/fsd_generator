import datetime

def get_word_count(text):
    if not text:
        return 0
    return len(text.split())

def get_char_count(text):
    if not text:
        return 0
    return len(text)

def format_date(dt=None):
    if dt is None:
        dt = datetime.datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def generate_clipboard_js(element_id, content):
    escaped_content = content.replace('`', '\\`').replace('$', '\\$')
    return f"""
    <script>
    function copyToClipboard() {{
        const textToCopy = `{escaped_content}`;
        navigator.clipboard.writeText(textToCopy).then(() => {{
            console.log("Copied to clipboard!");
        }});
    }}
    </script>
    <button onclick="copyToClipboard()" style="padding: 0.5rem 1rem; border-radius: 6px; background: #3B82F6; color: white; border: none; cursor: pointer;">Copy to Clipboard</button>
    """

def styled_card(type_, title, message):
    types = {
        "info": "info-card",
        "success": "success-card",
        "warning": "warning-card",
        "error": "error-card",
    }
    class_name = types.get(type_, "info-card")
    return f"""
    <div class="{class_name}">
        <h4 style="margin-top: 0; margin-bottom: 0.5rem;">{title}</h4>
        <p style="margin: 0;">{message}</p>
    </div>
    """
