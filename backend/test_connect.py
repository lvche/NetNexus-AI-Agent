from netmiko import ConnectHandler

device = {
    'device_type': 'cisco_ios',
    'host': '127.0.0.1',
    'port': 2222,
    'username': 'admin',
    'password': 'cisco',
}

print("正在连接虚拟交换机...")
net_connect = ConnectHandler(**device)
print("连接成功! 准备发送命令...")

output = net_connect.send_command("show ip int brief")
print(output)