import socket
import threading
import time
from datetime import datetime
import rumps
import sys

class MacStatusBarApp(rumps.App):
    def __init__(self, name):
        super(MacStatusBarApp, self).__init__(name)
        self.message = ""
        self.timer = None
        self.last_update_time = None
        self.server_running = True

    def update_message(self, new_message):
        self.message = new_message
        self.last_update_time = datetime.now()
        # 淡化显示 使用｜
        # self.title = f"📢 {self.message}"
        self.title = f"｜ {self.message}"
        
        # 取消之前的定时器（如果有）
        if self.timer and self.timer.is_alive():
            self.timer.cancel()
        
        # 设置1分钟后清除消息的定时器
        self.timer = threading.Timer(60.0, self.clear_message)
        self.timer.start()

    def clear_message(self):
        self.message = ""
        self.title = ""
        self.last_update_time = None

    @rumps.clicked("退出")
    def quit(self, _):
        self.server_running = False
        rumps.quit_application()

def handle_client(conn, addr, app):
    print(f"Connected by {addr}")
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            message = data.decode('utf-8')
            print(f"Received: {message}")
            # 在主线程中更新状态栏
            # 系统通知 注释掉
            # rumps.notification("新消息", "", message)
            app.update_message(message)
    except ConnectionResetError:
        print(f"Client {addr} disconnected unexpectedly")
    finally:
        conn.close()

def start_server(host, port, app):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen()
        print(f"Server started on {host}:{port}")
        s.settimeout(1)  # 设置超时以便定期检查是否应该退出
        
        try:
            while app.server_running:
                try:
                    conn, addr = s.accept()
                    client_thread = threading.Thread(target=handle_client, args=(conn, addr, app))
                    client_thread.daemon = True
                    client_thread.start()
                except socket.timeout:
                    continue
        except KeyboardInterrupt:
            print("Server shutting down...")
        finally:
            if app.timer and app.timer.is_alive():
                app.timer.cancel()
            s.close()

def main():
   # app = MacStatusBarApp("Message Server")
    app = MacStatusBarApp("M*")
    # 启动服务器线程
    server_thread = threading.Thread(target=start_server, args=("0.0.0.0", 65432, app))
    server_thread.daemon = True
    server_thread.start()
    
    # 在主线程中运行rumps应用
    app.run()

if __name__ == "__main__":
    main()