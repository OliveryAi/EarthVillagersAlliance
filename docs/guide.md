# 地球村民监察互助联盟 - 使用指南

## 🚀 快速开始

### 环境要求
- Python 3.10+
- Windows 10/11（桌面端）
- 网络连接

### 安装依赖

```bash
cd D:\Develop\地球村民监察互助联盟\backend
pip install -r requirements.txt
```

### 数据库初始化

```bash
python manage.py makemigrations
python manage.py migrate
python scripts/init_data.py
```

### 启动服务

```bash
# Django Web API
python manage.py runserver

# 访问地址
- API: http://localhost:8000/api/
- Admin: http://localhost:8000/admin
```

### 桌面客户端运行

```bash
cd D:\Develop\地球村民监察互助联盟\desktop
python main.py
```

## 📱 管理员账号

| 用户名 | 密码 |
|--------|------|
| 11011912000 | 110119120 |

## 🔐 防刷票机制

- **设备指纹**: MD5(UserAgent + Language)
- **IP 频率限制**: 单日最多 3 次投票
- **验证码绑定**: 每次投票需手机验证
- **人脸识别预留接口**: 可扩展接入第三方 OCR/人脸服务

## 📊 四个榜单分类

1. **35 岁以上就业歧视观察榜** (age_discrimination)
2. **性别歧视观察榜** (gender_discrimination)
3. **职场 PUA 专制观察榜** (pua_despotism)
4. **职场过劳剥削观察榜** (overwork_exploitation)

## 🔒 隐私保护

- 手机号 Fernet 加密存储
- 投票匿名处理
- 证据材料 AES-GCM 文件级加密（可扩展）
- 管理员只能看到统计结果，无法追踪到具体投票者 IP/设备信息

## 📦 打包为 exe

```bash
cd D:\Develop\地球村民监察互助联盟\desktop
python build_exe.py
# 或手动执行:
pyinstaller --windowed --onefile --icon=app.ico main.py
```

## 🌐 问卷网 API 预留接口

可在 `apps.evidence.views` 中添加：

```python
def import_from_wjxapi(vote_id, wjx_id):
    """从问卷网导入数据"""
    # TODO: 实现问卷网 API 对接
    pass
```

## 🛠️ 常见问题

**Q: 验证码不显示？**
A: 测试环境下验证码打印到控制台，请查看 Django 服务日志

**Q: 如何修改管理员密码？**
A: 登录 admin 后台后修改用户凭据

**Q: 数据备份?**
A: 直接复制 `backend/data.db` 文件即可
