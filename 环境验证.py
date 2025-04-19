#!/usr/bin/env python3
from objc import lookUpClass
from Foundation import NSBundle

def check_environment():
    try:
        NSString = lookUpClass('NSString')
        test_str = NSString("环境检查")
        print(f"✅ 验证成功 | 类型: {type(test_str)} | 内容: {test_str}")
        return True
    except Exception as e:
        print(f"❌ 验证失败: {str(e)}")
        return False

if __name__ == "__main__":
    if not check_environment():
        print("\n修复建议:")
        print("1. 执行: pip3 install --upgrade pyobjc-core pyobjc-framework-Cocoa")
        print("2. 检查系统Python路径: which python3")
        print("3. 重置权限: sudo tccutil reset Accessibility")