#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import psutil
import requests
import subprocess
import time

def format_speed(bytes_per_sec):
    """智能格式化网速并确保固定宽度"""
    units = ['B', 'KB', 'MB', 'GB']
    for unit in units:
        if bytes_per_sec < 1024:
            return f"{bytes_per_sec:5.1f}{unit}"  # 固定5字符宽度
        bytes_per_sec /= 1024.0
    return f"{bytes_per_sec:5.1f}GB"

def check_github_status():
    """检查GitHub连接状态并返回固定宽度结果"""
    # HTTPS检测
    try:
        resp = requests.get("https://api.github.com", timeout=5)
        https_status = ("API: ✅ ", 6) if resp.status_code == 200 else (f"API: 🔴 {resp.status_code}", 10)
    except Exception as e:
        https_status = (f"API: ❌ {str(e)[:8]}", 12)
    
    # Git协议检测
    try:
        proc = subprocess.run(
            ["git", "ls-remote", "https://github.com"],
            capture_output=True,
            text=True,
            timeout=10
        )
        git_status = ("Git: ✅ ", 6) if proc.returncode == 0 else (f"Git: ❌ {proc.returncode}", 10)
    except subprocess.TimeoutExpired:
        git_status = ("Git:⌛", 6)
    except Exception as e:
        git_status = (f"Git: ❌ {str(e)[:8]}", 12)
    
    return https_status, git_status

def main():
    # 初始化网络基准值
    last_sent = psutil.net_io_counters().bytes_sent
    last_recv = psutil.net_io_counters().bytes_recv
    
    # 字段宽度定义（单位：字符）
    widths = {
        'time': 10,
        'upload': 9,  # 如 " 12.3KB"
        'download': 9,
        'api': 12,    # 最宽可能值
        'git': 12
    }
    
    # 打印格式说明（仅首次运行时显示）
    print("监控格式：[时间] [上传速度] [下载速度] [API状态] [Git状态]")
    print("-" * 65)
    
    try:
        while True:
            # 获取当前网络统计
            counters = psutil.net_io_counters()
            
            # 计算速度并格式化
            upload = format_speed(counters.bytes_sent - last_sent) + "/s"
            download = format_speed(counters.bytes_recv - last_recv) + "/s"
            
            # 更新基准值
            last_sent = counters.bytes_sent
            last_recv = counters.bytes_recv
            
            # 检查GitHub状态
            (api_status, _), (git_status, _) = check_github_status()
            
            # 获取当前时间
            current_time = time.strftime("%H:%M:%S")
            
            # 严格对齐的输出
            print(
                f"[{current_time}] "
                f"[↑{upload:>{widths['upload']}}] "
                f"[↓{download:>{widths['download']}}] "
                f"[{api_status:<{widths['api']}}] "
                f"[{git_status:<{widths['git']}}]"
            )
            
            # 等待1秒
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n监控已停止")

if __name__ == "__main__":
    main()