#!/usr/bin/env python3
import socket
import logging
import sys

# === 配置日志 ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def discover_server():
    """通过UDP广播发现服务器"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0", 65432))
    sock.settimeout(5)  # 5秒超时
    
    logging.info("正在寻找服务器...")
    try:
        while True:
            data, addr = sock.recvfrom(1024)
            if data == b"ServerDiscovery":
                logging.info(f"发现服务器: {addr[0]}")
                return addr[0]
    except socket.timeout:
        logging.error("未找到服务器，请确认服务器已启动")
        sys.exit(1)
    finally:
        sock.close()

def send_messages(server_ip):
    """向服务器发送消息"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((server_ip, 65432))
            logging.info(f"已连接到服务器 {server_ip}")
            
            counter = 1
            while True:
                message = input(f"消息{counter} > (输入 'quit' 退出): ")
                if message.lower() == 'quit':
                    break
                s.sendall(message.encode('utf-8'))
                counter += 1
    except ConnectionRefusedError:
        logging.error("连接被拒绝，请检查服务器状态")
    except KeyboardInterrupt:
        logging.info("客户端退出")
    except Exception as e:
        logging.error(f"发生错误: {e}")

if __name__ == "__main__":
    server_ip = discover_server()
    send_messages(server_ip)