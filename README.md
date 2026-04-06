# 地球村民监察互助联盟

**监督企业就业歧视 | 保障劳动者权益 | 实现社会透明化**

一个开源的群众监督投票平台，让全体劳动者共同参与社会治理。

## 🌟 项目特色

### 四大观察榜

| 榜单名称 | 说明 |
|---------|------|
| 📊 **35 岁以上就业歧视观察榜** | 监测年龄歧视行为 |
| 👩 **性别歧视观察榜** | 保护平等就业权 |
| 😔 **职场 PUA 专制观察榜** | 曝光精神压迫现象 |
| ⏰ **职场过劳剥削观察榜** | 反对强制加班文化 |

### 核心功能

- ✅ **匿名投票**: 保障用户隐私，自由表达意见
- ✅ **防刷票机制**: IP 限制 + 设备指纹 + 验证码绑定
- ✅ **证据上传**: 支持图片/PDF 凭证材料提交
- ✅ **手机注册**: Fernet 加密存储敏感信息
- ✅ **双端支持**: Web API + Windows 桌面客户端

## 📦 快速开始

### 环境要求

```bash
Python >= 3.10
Windows 10/11 (桌面端)
```

### 安装与启动

```bash
# 后端服务
cd backend
pip install -r requirements.txt
python manage.py migrate
python scripts/init_data.py
python manage.py runserver

# 访问地址
- Web API: http://localhost:8000/api/
- Admin:   http://localhost:8000/admin
```

### 桌面客户端

```bash
cd desktop
python main.py

# 打包为 exe
pyinstaller --windowed --onefile --name="地球村民监察互助联盟" main.py
```

## 🔑 管理员账号

- **用户名**: `11011912000`
- **密码**: `110119120`

访问 http://localhost:8000/admin 登录后台管理。

## 🛡️ 隐私与防刷票

### 技术保障

| 措施 | 说明 |
|------|------|
| 🔐 Fernet 加密 | 手机号等敏感字段对称加密存储 |
| 👆 设备指纹 | MD5(UserAgent + Language) 唯一标识 |
| 🚫 IP 频率限制 | 单日单 IP 最多投票 3 次 |
| 📱 验证码绑定 | 每次投票需重新验证手机 |

### 匿名机制

- 榜单仅展示统计结果，不显示投票者信息
- 企业无法知道具体是谁投了票
- 管理员只能查看排行，无法追溯 IP/设备

## 🏗️ 技术架构

```
地球村民监察互助联盟
├── backend/                    # Django Web API
│   ├── config/                 # Django 配置
│   ├── apps/
│   │   ├── accounts/           # 用户认证 (手机 + 验证码)
│   │   ├── voting/             # 投票核心功能
│   │   ├── list/               # 榜单管理
│   │   └── evidence/           # 证据上传
├── desktop/                    # PyQt6 Windows 客户端
├── docs/                       # 文档
└── config.json                 # 全局配置
```

## 📝 API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/register/` | 手机 + 验证码注册 |
| POST | `/api/auth/login/` | 用户登录 |
| POST | `/api/auth/send-verification/` | 获取验证码 |
| GET | `/api/list/ranking/` | 查看排行榜 |
| GET | `/api/list/companies/search/?q=关键词` | 搜索企业 |

## 📄 开源协议

本项目完全开源，允许任何形式的二次开发和部署。

**免责声明**: 本平台数据来源于网友投票，仅供参考。所披露的企业名单仅供社会监督使用，不涉及任何商业用途。

## 🙏 致谢

感谢所有参与社会治理、维护劳动者权益的志愿者和 contributors！

---

**让每一票都有力量 · 推动更公平的社会环境**
