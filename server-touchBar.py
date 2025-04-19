#!/usr/bin/env python3
import socket
import threading
import time
import logging
import netifaces
import sys
from objc import NSString  # 关键依赖

# === 配置日志 ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("server.log"),
        logging.StreamHandler()
    ]
)

# === Touch Bar 初始化 ===
try:
    from PyTouchBar import PyTouchBar, TouchBarItems
    TOUCHBAR_ENABLED = True
except ImportError:
    TOUCHBAR_ENABLED = False
    logging.warning("PyTouchBar 不可用，回退到控制台模式")

class MessageServer:
    def __init__(self):
        self._lock = threading.Lock()
        self.current_message = ""
        self.timer = None
        self.server_running = True
        self.touch_bar = None
        
        if TOUCHBAR_ENABLED:
            self._init_touch_bar()

    def _init_touch_bar(self):
        """初始化 Touch Bar 组件"""
        try:
            # 必须使用 NSString 包装字符串
            title = NSString("📢 等待消息...")
            quit_title = NSString("❌ 退出")
            
            self.touch_bar = PyTouchBar(
                items=[
                    TouchBarItems.Label(
                        title=title,
                        id="message_label",
                        customization_allow=True,
                    ),
                    TouchBarItems.Button(
                        title=quit_title,
                        action=self.safe_quit,
                        color=(255, 59, 48),  # 红色
                    ),
                ]
            )
            self.touch_bar.start()
            logging.info("Touch Bar 初始化成功")
        except Exception as e:
            logging.error(f"Touch Bar 初始化失败: {e}")
            self.touch_bar = None

    def update_display(self, message):
        """更新消息显示（线程安全）"""
        with self._lock:
            self.current_message = message
            
            # Touch Bar 或控制台输出
            if self.touch_bar:
                try:
                    self.touch_bar.update_item(
                        "message_label",
                        title=NSString(f"📢 {message}")
                    )
                except Exception as e:
                    logging.error(f"更新 Touch Bar 失败: {e}")
            else:
                print(f"新消息: {message}")

            # 重置清除计时器
            if self.timer and self.timer.is_alive():
                self.timer.cancel()
            self.timer = threading.Timer(60.0, self.clear_display)
            self.timer.start()

    def clear_display(self):
        """清除显示"""
        with self._lock:
            self.current_message = ""
            if self.touch_bar:
                self.touch_bar.update_item(
                    "message_label",
                    title=NSString("📢 等待消息...")
                )
            logging.info("消息已清除")

    def safe_quit(self, _=None):
        """安全退出服务器"""
        with self._lock:
            self.server_running = False
            if self.timer:
                self.timer.cancel()
            if self.touch_bar:
                self.touch_bar.stop()
            logging.info("服务器正在退出...")
            sys.exit(0)

# === 网络功能 ===
def broadcast_server_ip():
    """广播服务器IP（所有网络接口）"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    while True:
        try:
            for interface in netifaces.interfaces():
                addrs = netifaces.ifaddresses(interface)
                if netifaces.AF_INET in addrs:
                    for addr_info in addrs[netifaces.AF_INET]:
                        if 'broadcast' in addr_info:
                            sock.sendto(
                                b"ServerDiscovery",
                                (addr_info['broadcast'], 65432)
                            )
                            logging.debug(f"广播发送到 {addr_info['broadcast']}")
            time.sleep(5)  # 每5秒广播一次
        except Exception as e:
            logging.error(f"广播错误: {e}")
            break

def handle_client(conn, addr, server):
    """处理客户端连接"""
    logging.info(f"客户端连接: {addr}")
    try:
        while True:
            data = conn.recv(1024)
            if not data:
                break
            message = data.decode("utf-8")
            logging.info(f"收到消息: {message}")
            server.update_display(message)
    except ConnectionResetError:
        logging.warning(f"客户端 {addr} 断开连接")
    finally:
        conn.close()

def start_server(host, port, server):
    """启动TCP服务器"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.listen()
        s.settimeout(1)  # 设置超时以便检查退出标志
        logging.info(f"服务器启动: {host}:{port}")

        try:
            while server.server_running:
                try:
                    conn, addr = s.accept()
                    client_thread = threading.Thread(
                        target=handle_client,
                        args=(conn, addr, server),
                        daemon=True
                    )
                    client_thread.start()
                except socket.timeout:
                    continue
        except KeyboardInterrupt:
            server.safe_quit()
        finally:
            s.close()

# === 主程序 ===
if __name__ == "__main__":
    # 启动服务器
    server = MessageServer()
    
    # 广播线程
    broadcast_thread = threading.Thread(
        target=broadcast_server_ip,
        daemon=True
    )
    broadcast_thread.start()
    
    # 主服务器线程
    server_thread = threading.Thread(
        target=start_server,
        args=("0.0.0.0", 65432, server),
        daemon=True
    )
    server_thread.start()
    
    # 主循环（等待退出）
    try:
        while server.server_running:
            time.sleep(1)
    except KeyboardInterrupt:
        server.safe_quit()