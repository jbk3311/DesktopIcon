import winreg

class RegistryHelper:
    @staticmethod
    def get_icon_positions():
        positions = {}
        try:
            key_path = r"Software\Microsoft\Windows\Shell\Bags\1\Desktop"
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                key_path,
                0,
                winreg.KEY_READ
            )
            
            i = 0
            while True:
                try:
                    name, value, type_ = winreg.EnumValue(key, i)
                    if name.startswith("ItemPos_"):
                        item_name = name[8:]  # 移除 "ItemPos_" 前缀
                        positions[item_name] = value
                    i += 1
                except WindowsError:
                    break
                    
        except Exception as e:
            print(f"读取注册表失败: {str(e)}")
            
        return positions
    
    @staticmethod
    def set_icon_positions(positions):
        try:
            key_path = r"Software\Microsoft\Windows\Shell\Bags\1\Desktop"
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                key_path,
                0,
                winreg.KEY_WRITE
            )
            
            for item, position in positions.items():
                try:
                    icon_key = f"ItemPos_{item}"
                    winreg.SetValueEx(
                        key,
                        icon_key,
                        0,
                        winreg.REG_BINARY,
                        position
                    )
                except:
                    continue
                    
        except Exception as e:
            print(f"写入注册表失败: {str(e)}")