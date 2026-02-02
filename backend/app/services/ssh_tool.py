from netmiko import ConnectHandler

def run_cli_command(command: str):
    """底层 SSH 执行函数"""
    print(f"\n🔌 [SSH Tool] 执行: {command}")
    
    device = {
        'device_type': 'cisco_ios',
        'host': '127.0.0.1',
        'port': 2222,
        'username': 'admin',
        'password': 'cisco',
        
        # ★★★ 关键修改：增加超时设置 ★★★
        'fast_cli': False,          # 关闭快速模式，提高稳定性
        'global_delay_factor': 4,   # 把所有默认等待时间乘以 4 (给模拟器更多反应时间)
        'read_timeout_override': 20, # 强制等待最多 20 秒
        'session_timeout': 30,      # 会话超时时间
    }
    
    try:
        with ConnectHandler(**device) as net_connect:
            # send_command 也会自动处理等待提示符
            # strip_command=False 可以防止有时候回显被误删
            return net_connect.send_command(command, strip_command=False)
            
    except Exception as e:
        print(f"❌ SSH 错误: {e}")
        # 返回友好的错误信息，而不是抛出异常炸掉程序
        return f"设备连接超时或指令错误。请检查 Mock Device 是否运行。详情: {str(e)}"