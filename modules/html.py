import html

progress_html = '''
<div class="loader-container">
  <div class="loader"></div>
  <div class="progress-container">
    <progress value="*number*" max="100"></progress>
  </div>
  <span>*text*</span>
</div>
'''


def make_progress_html(number, text):
    safe_number = html.escape(str(number), quote=True)
    safe_text = html.escape(str(text), quote=True)
    return progress_html.replace('*number*', safe_number).replace('*text*', safe_text)
