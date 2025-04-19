#!/usr/bin/env python3
import socket
import threading
import time
import logging
import netifaces
import sys
import PyTouchBar
from datetime import datetime
from objc import lookUpClass

# ==== 初始化配置 ====
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("server.log"),
        logging.StreamHandler()
    ]
)

# ==== Touch Bar 服务 ====
class TouchBarService:
    def __init__(self):
        self.bar = None
        try:
            NSString = lookUpClass('NSString')
            self.bar = PyTouchBar(
                items=[
                    TouchBarItems.Label(
                        title=NSString("📢 消息服务就绪"),
                        id="message_label"
                    ),
                    TouchBarItems.Button(
                        title=NSString("⏹ 停止服务"),
                        action=lambda _: self.shutdown(),
                        color=(255, 59, 48)
                    )
                ]
            )
            self.bar.start()
            logging.info("Touch Bar 初始化成功")
        except Exception as e:
            logging.error(f"Touch Bar 初始化失败: {str(e)}")
            self.bar = None

    def show_message(self, text):
        """显示消息（自动切换控制台模式）"""
        if self.bar:
            try:
                NSString = lookUpClass('NSString')
                self.bar.update_item(
                    "message_label",
                    title=NSString(f"📢 {text}")
                )
            except Exception as e:
                logging.error(f"更新失败: {str(e)}")
        print(f"[{datetime.now()}] {text}")

    def shutdown(self):
        if self.bar:
            self.bar.stop()
        sys.exit(0)

# ==== 网络服务 ====
def start_server():
    service = TouchBarService()
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('0.0.0.0', 65432))
        s.listen()
        logging.info("服务器启动，等待连接...")

        while True:
            conn, addr = s.accept()
            threading.Thread(
                target=lambda: handle_client(conn, addr, service),
                daemon=True
            ).start()

def handle_client(conn, addr, service):
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            message = data.decode('utf-8')
            service.show_message(message)
    finally:
        conn.close()

# ==== 主程序 ====
if __name__ == "__main__":
    # 环境检查
    try:
        NSString = lookUpClass('NSString')
        logging.info("环境验证通过")
    except Exception as e:
        logging.critical(f"环境不兼容: {str(e)}")
        sys.exit(1)

    # 启动服务
    threading.Thread(target=start_server, daemon=True).start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("服务器关闭")