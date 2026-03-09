C:/Users/chengkun.zheng/AppData/Local/Programs/Python/Python312/python.exe -m PyInstaller --clean "QA任务提醒工具.spec"

C:/Users/chengkun.zheng/AppData/Local/Programs/Python/Python312/python.exe -m PyInstaller --clean --onefile --noconsole --icon=app_icon.ico --name "QA任务提醒工具" --add-data "tasks_sample.json;." --add-data "feishu_push.py;." --add-data "app_icon.ico;." --hidden-import "pynput.keyboard._win32" --hidden-import "pynput.mouse._win32" --hidden-import "pynput._util.win32" main.py

pyinstaller my_app_name.spec
