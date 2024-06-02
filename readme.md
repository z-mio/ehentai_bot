# EHentai Telegram Bot

解析EHentai画廊链接, 返回画廊信息和下载链接/压缩包

### 直接下载返回压缩包

![](https://img.155155155.xyz/i/2024/06/665c0b221e053.webp)
![](https://img.155155155.xyz/i/2024/06/665c0b3921987.webp)

### 返回下载链接

![](https://img.155155155.xyz/i/2024/06/665c0b4e10171.webp)

## 安装

1. git clone 本项目

```bash
git clone https://github.com/z-mio/ehentai_bot.git
```

2. 修改配置文件

复制 `bot.yaml.example` 为 `bot.yaml`, 修改其中的配置  
复制 `config/config.yaml.example` 为 `config/config.yaml`, 修改其中的配置  

3. 安装依赖

Python版本 >= 3.10

```bash 
sudo apt install python3-pip -y
pip install -r requirements.txt
```

4. 运行

```bash
python3 bot.py
```

发送 `/menu` 设置 Bot 菜单