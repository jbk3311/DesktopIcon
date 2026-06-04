中文 | [English](README_EN.md)

---

# Desktop Icon Manager

一个用于管理 Windows 桌面图标的工具，可以帮助你轻松地控制桌面图标的显示、隐藏，操作显示与隐藏时可还原回图标原来的位置。

## 功能特点

- 控制桌面图标的显示和隐藏
- 图标分组管理，快速勾选分组内图标进行批量隐藏/显示
- 保存和恢复桌面图标位置
- 简洁的图形用户界面
- 支持管理员权限操作
- 自动保存图标位置配置
- 分组配置保存在 `icon_groups.json`

## 分组功能

1. 点击「管理分组」创建分组，并为桌面图标指定所属分组
2. 在主界面选择分组后点击「选中分组」，可一键勾选该组内图标（不影响其他已勾选项）
3. 再点击「隐藏选中」或「显示选中」完成批量操作
4. 每个图标最多属于一个分组；未分配的图标属于「未分组」

## 系统要求

- Windows 操作系统
- Python 3.6 或更高版本
- 管理员权限（用于完全控制桌面图标）

## 安装说明

1. 克隆或下载本项目到本地
2. 安装依赖包：
   ```bash
   pip install -r requirements.txt
   ```

## 使用方法

1. 运行主程序：
   ```bash
   python main.py
   ```
2. 程序会自动请求管理员权限（这是必需的，用于控制桌面图标）
3. 使用图形界面来管理你的桌面图标

## 打包为 exe

本项目支持使用 [Nuitka](https://nuitka.net/) 打包为 Windows 可执行文件，打包脚本见 [`build.py`](build.py)。

### 环境要求

- Windows 10 或更高版本
- 已安装 Python 3.6+（与开发环境相同）
- 网络连接（首次打包时 Nuitka 可能需要自动下载 C 编译器组件）

### 打包步骤

1. 进入项目根目录（包含 `main.py`、`build.py` 的目录）：
   ```bash
   cd desktopicon
   ```

2. 安装依赖（含 `nuitka`、`pywin32`）。请确保 `python` 与 `pip` 指向**同一个** Python 安装：
   ```bash
   python -m pip install -r requirements.txt
   ```
   若系统安装了多个 Python（例如 MSYS2 与官方 CPython 并存），推荐使用：
   ```bash
   py -3.10 -m pip install -r requirements.txt
   py -3.10 build.py
   ```

3. 执行打包脚本：
   ```bash
   python build.py
   ```

4. 打包完成后，在 `dist` 目录下生成单个 exe 文件：
   ```
   dist/桌面图标管理器v1.0.0.exe
   ```
   文件名中的版本号与 [`src/config.py`](src/config.py) 里的 `APP_VERSION` 一致。

5. 双击 exe 运行。程序会通过 UAC 请求管理员权限（打包时已启用 `--windows-uac-admin`），无需再单独安装 Python。

### 打包说明

- `build.py` 会自动清理旧的 `build`、`dist` 等中间目录后再构建
- 打包为**单文件 exe**（`--onefile`），并内置程序图标与 `src/resources` 资源
- 首次打包耗时可能较长，请耐心等待；若失败，可检查是否缺少 C 编译环境，或重新执行 `python -m pip install -U nuitka`

### 常见打包错误

**`No module named nuitka`**

说明当前执行 `python build.py` 的解释器里没装 Nuitka，但 `pip install` 可能装到了另一个 Python。可先查看路径：

```bash
where python
where pip
python -c "import sys; print(sys.executable)"
```

解决方式：用**同一个**解释器安装依赖并打包，例如：

```bash
py -3.10 -m pip install -r requirements.txt
py -3.10 build.py
```

**`No matching distribution found for tkinter`**

`tkinter` 是 Python 标准库组件，Windows 官方 Python 已自带，不能通过 pip 安装。本项目 `requirements.txt` 已不再包含该项；若仍报错，请更新代码后重试。

### 配置文件位置

运行 exe 后，以下配置文件会在 **exe 所在目录**自动生成：

- `icon_positions.json` — 图标位置备份
- `icon_groups.json` — 图标分组配置

> **注意**：Nuitka `--onefile` 打包的 exe 每次运行会将自身解压到系统临时目录，程序直接使用 `__file__` 路径会导致数据写入临时目录并随程序退出被删除。本项目已通过 `sys.executable` 确保两个配置文件始终保存在 **exe 文件旁边**，数据不会丢失。

如需备份分组或位置数据，复制 exe 同目录下这两个 JSON 文件即可。

## 注意事项

- 程序需要管理员权限才能完全控制桌面图标
- 修改后可能需要刷新桌面才能看到效果
- 如果程序异常中断导致图标消失，请重新运行程序并打开显示即可

## 许可证

本项目采用 GNU 许可证 - 详见 [LICENSE](LICENSE) 文件

## 作者

- 作者：[jbk3311]

## 贡献

欢迎提交 Issue 和 Pull Request 来帮助改进这个项目。


