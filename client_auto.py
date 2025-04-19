import socket
import threading
import time

def discover_server():
    """监听广播，发现服务端IP"""
    discovery_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    discovery_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    discovery_socket.bind(("0.0.0.0", 65432))
    
    print("正在寻找服务器...")
    while True:
        data, addr = discovery_socket.recvfrom(1024)
        if data == b"ServerDiscovery":
            print(f"发现服务器: {addr[0]}")
            return addr[0]  # 返回服务器IP

def connect_to_server(server_ip):
    """连接到服务器并发送消息"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((server_ip, 65432))
            print(f"已连接到服务器 {server_ip}")
            
            counter = 1
            while True:
                message = input(f"序号{counter} 输入要发送的内容(或输入'quit'退出): ")
                if message.lower() == 'quit':
                    break
                
                s.sendall(message.encode('utf-8'))
                counter += 1
    except ConnectionRefusedError:
        print("无法连接到服务器，请检查服务器是否运行")
    except KeyboardInterrupt:
        print("\n客户端关闭")
    except Exception as e:
        print(f"发生错误: {e}")

def main():
    server_ip = discover_server()
    connect_to_server(server_ip)

if __name__ == "__main__":
    main()