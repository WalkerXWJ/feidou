#!/usr/bin/env python3
import socket
import logging
import sys
import threading

# ==== 配置日志 ====
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

# ==== 服务器自动发现 ====
def discover_server():
    """通过UDP广播发现服务器IP"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0', 65432))
    sock.settimeout(5)  # 5秒超时

    logging.info("正在搜索服务器...")
    try:
        while True:
            data, addr = sock.recvfrom(1024)
            if data == b"ServerDiscovery":
                logging.info(f"发现服务器: {addr[0]}")
                return addr[0]
    except socket.timeout:
        logging.error("未找到服务器，请确认服务器已启动")
        return None
    finally:
        sock.close()

# ==== 消息发送 ====
def send_message(sock, message):
    """发送消息到服务器"""
    try:
        sock.sendall(message.encode('utf-8'))
    except Exception as e:
        logging.error(f"发送失败: {str(e)}")
        return False
    return True

# ==== 主程序 ====
def main():
    # 自动发现服务器
    server_ip = discover_server()
    if not server_ip:
        return

    # 连接服务器
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((server_ip, 65432))
            logging.info(f"已连接到服务器 {server_ip}")

            # 接收消息线程
            def receive_messages():
                while True:
                    try:
                        data = s.recv(1024)
                        if not data:
                            break
                        print(f"\n[服务器回复] {data.decode('utf-8')}")
                    except ConnectionResetError:
                        logging.warning("连接被服务器关闭")
                        break

            threading.Thread(target=receive_messages, daemon=True).start()

            # 用户输入循环
            message_count = 1
            while True:
                try:
                    message = input(f"消息{message_count} > (输入'quit'退出): ")
                    if message.lower() == 'quit':
                        break
                    if send_message(s, message):
                        message_count += 1
                except KeyboardInterrupt:
                    break

    except ConnectionRefusedError:
        logging.error("连接被拒绝，请检查服务器状态")
    except Exception as e:
        logging.error(f"发生错误: {str(e)}")

if __name__ == "__main__":
    main()