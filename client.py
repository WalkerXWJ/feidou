import socket
import sys

def get_server_ip():
    while True:
        ip = input("请输入服务器所在设备的局域网IP地址: ")
        # 简单的IP地址验证
        parts = ip.split('.')
        if len(parts) == 4 and all(part.isdigit() and 0 <= int(part) <= 255 for part in parts):
            return ip
        print("无效的IP地址，请重新输入")

def main():
    if len(sys.argv) > 1:
        SERVER_IP = sys.argv[1]
    else:
        SERVER_IP = get_server_ip()
    
    PORT = 65432  # 必须与服务器端口匹配
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((SERVER_IP, PORT))
            print(f"已连接到服务器 {SERVER_IP}")
            
            counter = 1
            while True:
                message = input(f"序号{counter} 输入要发送的内容(或输入'quit'退出): ")
                if message.lower() == 'quit':
                    break
                
                s.sendall(message.encode('utf-8'))
                counter += 1
                
    except ConnectionRefusedError:
        print("无法连接到服务器，请检查IP地址和服务器是否运行")
    except KeyboardInterrupt:
        print("\n客户端关闭")
    except Exception as e:
        print(f"发生错误: {e}")

if __name__ == "__main__":
    main()