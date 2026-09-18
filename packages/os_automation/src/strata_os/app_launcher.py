import subprocess
import os
import sys

def launch_app(name_or_path: str):
    """
    Launch an app. 
    In Windows, you can launch many things by just invoking their exe if they are in PATH,
    or using `start`.
    """
    if os.path.exists(name_or_path):
        os.startfile(name_or_path)
    else:
        os.system(f"start {name_or_path}")

def launch_url(url: str):
    os.startfile(url)
