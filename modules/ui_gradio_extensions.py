# based on https://github.com/AUTOMATIC1111/stable-diffusion-webui/blob/v1.6.0/modules/ui_gradio_extensions.py

import json
import os
import args_manager

from modules.localization import localization_js

modules_path = os.path.dirname(os.path.realpath(__file__))
script_path = os.path.dirname(modules_path)


def webpath(fn):
    abs_fn = os.path.abspath(fn)
    mtime = os.path.getmtime(abs_fn) if os.path.exists(abs_fn) else 0
    return f'/gradio_api/file={abs_fn}?{mtime}'


def javascript_html():
    script_js_path = webpath('javascript/script.js')
    context_menus_js_path = webpath('javascript/contextMenus.js')
    localization_js_path = webpath('javascript/localization.js')
    edit_attention_js_path = webpath('javascript/edit-attention.js')
    viewer_js_path = webpath('javascript/viewer.js')
    image_viewer_js_path = webpath('javascript/imageviewer.js')
    samples_path = webpath(os.path.abspath('./sdxl_styles/samples/fooocus_v2.jpg'))
    head = f'<script type="text/javascript">{localization_js(args_manager.args.language)}</script>\n'
    head += f'<script type="text/javascript" src="{script_js_path}"></script>\n'
    head += f'<script type="text/javascript" src="{context_menus_js_path}"></script>\n'
    head += f'<script type="text/javascript" src="{localization_js_path}"></script>\n'
    head += f'<script type="text/javascript" src="{edit_attention_js_path}"></script>\n'
    head += f'<script type="text/javascript" src="{viewer_js_path}"></script>\n'
    head += f'<script type="text/javascript" src="{image_viewer_js_path}"></script>\n'
    head += f'<meta name="samples-path" content="{samples_path}">\n'

    if args_manager.args.theme:
        safe_theme = json.dumps(str(args_manager.args.theme)).replace('</', '<\\/')
        head += f'<script type="text/javascript">set_theme({safe_theme});</script>\n'

    return head


def css_content():
    style_css_path = os.path.abspath('css/style.css')
    if os.path.exists(style_css_path):
        with open(style_css_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ''


def reload_javascript():
    # Kept for backward compatibility; Gradio 5 injects head/css via gr.Blocks(head=..., css=...)
    return
