# 地球村民监察互助联盟 - 项目介绍

## 中文版本

### 🌍 核心理念

**人类命运共同体 · 天下为公 · 天赋人权**

我们坚信：天道基于事实，慈悲、理性、平衡、协调、可持续。人类社会应当构建一个公平公正、透明、民主、自由的社会系统。实现这样的社会环境，需要全体社会成员的集体智慧和广泛参与。

**地球村民监察互助联盟**是一个开源的群众监督投票平台，旨在通过匿名投票和证据上传机制，实时监测和记录就业歧视与剥削行为，推动社会透明化和企业用工环境的改善。

### 🎯 项目愿景

本项目诞生于对现实社会的深刻观察：
- **公平正义**是每个人的基本权利
- **信息透明**是防止腐败和歧视的前提
- **公众参与**是社会进步的根本动力
- **集体智慧**可以汇聚成推动变革的强大力量

我们相信，通过建立一个开放、透明、可验证的监督平台，可以让每一个劳动者发出自己的声音，让每一份不公都得到应有的关注。

### 📜 开发历程

#### 项目起源
开发者基于以下理念发起此项目：
1. **天赋人权**：每个劳动者都应享有平等就业权
2. **天下为公**：社会监督应当是开放、透明、全民参与的事业
3. **事实为基础**：榜单数据来源于真实投票和证据，非主观臆断

#### 技术演进
从最初的构思到最终实现，项目经历了以下关键阶段：

| 阶段 | 时间 | 主要成果 |
|------|------|----------|
| 概念设计 | v1.0 | 确定四大观察榜体系和核心功能架构 |
| 后端开发 | v1.1 | Django REST Framework API 完整实现 |
| 模型迭代 | v1.2 | 用户认证、投票、证据表优化与字段修复 |
| 安全加固 | v1.3 | 设备指纹、IP 频率限制、Fernet 加密存储 |
| 客户端开发 | v1.4 | PyQt6 Windows 桌面应用，支持离线操作 |
| 完整测试 | v1.5 | 端到端功能验证和压力测试完成 |

### 🚀 核心功能

#### 1. 四大观察榜体系

| 榜单 | 代码 | 监督内容 |
|------|------|----------|
| **35 岁以上就业歧视观察榜** | `age_discrimination` | 记录存在年龄歧视行为的企业 |
| **性别歧视观察榜** | `gender_discrimination` | 记录存在性别歧视行为的企业 |
| **职场 PUA 专制观察榜** | `pua_despotism` | 记录存在精神控制、专制管理的企业 |
| **过劳剥削观察榜** | `overwork_exploitation` | 记录存在强制加班、无加班费的企业 |

#### 2. 匿名投票系统
- 用户通过手机号 +6 位验证码注册登录
- 单日最多投 3 票（同一用户对同类别不可重复）
- 榜单仅展示统计结果，不显示任何投票者信息

#### 3. 证据上传机制
- 支持图片格式：JPG、JPEG、PNG
- 支持文档格式：PDF、DOCX
- 文件大小限制：5MB
- 每个投票仅限一次证据提交

#### 4. 用户隐私保护
| 保护措施 | 技术实现 |
|----------|----------|
| **敏感数据加密** | Fernet 对称加密存储手机号等信息 |
| **设备指纹** | MD5(UserAgent + Language) 生成唯一标识 |
| **IP 频率限制** | django-ratelimit，单日单 IP 最多投票 3 次 |
| **验证码绑定** | 每次投票需重新获取手机验证码验证 |

### 🛡️ 防刷票机制

#### 技术架构
```
第一层：用户身份认证
├── 手机号 + 验证码双重验证
└── Token 认证（24 小时有效）

第二层：设备指纹识别
├── MD5(UserAgent + ScreenResolution + Timezone)
└── 跨设备追踪防止多账号刷票

第三层：IP 频率限制
├── django-ratelimit 中间件
├── 单 IP/日最多 3 次投票
└── 异常 IP 自动封禁

第四层：业务规则约束
├── 单日用户投票上限：3 票
├── 同一企业不可重复投同类别票
└── 证据上传限时（仅首次提交时可传）
```

#### 验证算法伪代码
```python
def check_vote_eligibility(user, category, company):
    # 1. 用户每日投票数检查
    daily_votes = Vote.objects.filter(
        voter_id=user.id,
        category=category,
        created_at__gte=today_midnight
    ).count()
    if daily_votes >= 3:
        raise TooManyRequestsError("今日投票已达上限")

    # 2. 重复投票检查
    existing = Vote.objects.filter(
        voter_id=user.id,
        company=company,
        category=category
    ).exists()
    if existing:
        raise ValidationError("您已对该企业投过同类别票")

    # 3. IP 频率限制检查
    ip_address = request.META.get('REMOTE_ADDR')
    ip_votes_today = Vote.objects.filter(
        ip_address__startswith=ip_address.split(',')[0],
        created_at__gte=today_midnight
    ).count()
    if ip_votes_today >= 3:
        raise TooManyRequestsError("IP 今日投票已达上限")

    # 4. 验证码验证
    if not verify_code(user.phone, request.data['code']):
        raise ValidationError("验证码错误或已过期")

    return True
```

### 🌱 开源目的与目标

#### 为什么选择开源？

1. **透明可信**：开源代码让算法和逻辑完全公开，任何人都可以审计投票机制的公正性
2. **集体智慧**：汇聚全球开发者的智慧和经验，持续优化系统性能和安全性
3. **广泛参与**：降低技术门槛，让更多人关注就业歧视问题，参与社会监督
4. **可持续发展**：社区维护确保项目长期稳定运行，不依赖单一团队

#### 核心目标

| 短期目标 | 中期目标 | 长期目标 |
|----------|----------|----------|
| 建立完善的举报和投票机制 | 拓展至更多就业歧视类型 | 形成全球性的劳动者权益保护网络 |
| 积累真实数据，推动企业自省 | 实现多语言、多平台部署 | 构建独立第三方社会监督标准体系 |
| 提升公众对就业歧视的认知 | 与 NGO/研究机构合作发布报告 | 推动相关政策法规的完善和落实 |

### 🤝 社区共建

#### 欢迎 Contributions

本项目完全开源，我们热烈欢迎：

- **开发者**：参与代码开发、Bug 修复、性能优化
- **测试者**：发现问题、提交 Bug Report、提供改进建议
- **翻译者**：协助多语言本地化工作
- **推广者**：帮助传播项目理念，扩大社会影响力
- **部署志愿者**：在各类云平台免费部署镜像站点

#### 参与方式

1. 访问 GitHub 仓库，Star ⭐️ 本项目支持我们
2. Fork 仓库，创建 Feature Branch 开发新功能
3. 提交 Pull Request，描述修改内容和原因
4. 提出 Issue，报告 Bug 或功能建议

### 📜 使用条款与授权

#### 非商业用途
- ✅ 允许自由下载、研究、学习
- ✅ 允许在社区内免费部署镜像站点
- ✅ 允许用于教育、研究等非商业目的
- ✅ 欢迎在 GitHub 上 Fork 和二次开发

#### 商业用途
如需将本项目或其衍生作品用于商业用途（包括但不限于收费服务、广告支持平台、商业化 SaaS 等），**必须事先获得项目维护者的书面授权**。

联系方式：通过 GitHub Issues 或发送邮件至项目邮箱。

### 📢 关于未成年人

对于未成年人或缺乏独立判断能力的个人，**建议在监护人指导下使用本平台**。我们的目标是促进社会进步，而非引发不必要的争议或伤害。

### ⚖️ 法律声明

本平台数据来源于网友投票和证据提交：
- 榜单结果仅供参考，**不构成事实认定**
- **不针对任何企事业机构和个人**，仅为数据统计展示
- **无法律效力**，不可作为法律诉讼依据
- 用户需**自行独立思考，仔细甄别信息真伪**
- 平台**不承担法律责任**

### 🙏 致谢

感谢所有参与社会治理、维护劳动者权益的志愿者和贡献者！

感谢开源社区提供的技术框架：
- [Django](https://www.djangoproject.com/) - Web 框架
- [Django REST Framework](https://www.django-rest-framework.org/) - API 构建
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - 桌面客户端

---

## English Version

### 🌍 Core Philosophy

**Community with a Shared Future for Mankind · Public Ownership of the World · Natural Rights**

We firmly believe: **The Way of Heaven is based on facts, compassion, rationality, balance, coordination, and sustainability.** Human society should construct a fair and just, transparent, democratic, and free social system. Achieving such a social environment requires collective wisdom and broad participation from all members of society.

**Earth Citizens Supervision Alliance** is an open-source citizen supervision voting platform designed to monitor and record employment discrimination and exploitation practices through anonymous voting and evidence submission mechanisms, promoting social transparency and improvement in corporate labor environments.

### 🎯 Vision

This project was born from deep observation of contemporary society:
- **Justice and fairness** are fundamental rights for every individual
- **Transparency** is the prerequisite for preventing corruption and discrimination
- **Public participation** is the driving force behind social progress
- **Collective wisdom** can converge into a powerful force for change

We believe that by building an open, transparent, and verifiable supervision platform, we can give every worker a voice and ensure every injustice receives due attention.

### 📜 Development Journey

#### Project Origins
The developer initiated this project based on the following principles:
1. **Natural Rights**: Every worker should enjoy equal employment rights
2. **Public Affairs for All**: Social supervision should be open, transparent, and a cause of universal participation
3. **Facts as Foundation**: List data comes from real votes and evidence, not subjective assumptions

#### Technical Evolution
From initial conception to final implementation, the project progressed through these key stages:

| Stage | Version | Major Achievements |
|-------|---------|-------------------|
| Concept Design | v1.0 | Established four observation categories and core architecture |
| Backend Development | v1.1 | Complete Django REST Framework API implementation |
| Model Iteration | v1.2 | User authentication, voting, evidence table optimization and field repairs |
| Security Hardening | v1.3 | Device fingerprinting, IP rate limiting, Fernet encrypted storage |
| Client Development | v1.4 | PyQt6 Windows desktop application with offline support |
| Full Testing | v1.5 | End-to-end functional validation and stress testing completed |

### 🚀 Core Features

#### 1. Four Observation Categories System

| Category | Code | Supervision Content |
|----------|------|---------------------|
| **35+ Age Discrimination Watchlist** | `age_discrimination` | Records enterprises with age-based hiring discrimination |
| **Gender Discrimination Watchlist** | `gender_discrimination` | Records enterprises with gender-based employment discrimination |
| **Workplace PUA Despotism Watchlist** | `pua_despotism` | Records enterprises with psychological manipulation and authoritarian management |
| **Overwork Exploitation Watchlist** | `overwork_exploitation` | Records enterprises with forced overtime and unpaid labor practices |

#### 2. Anonymous Voting System
- User registration via phone number + 6-digit verification code
- Maximum 3 votes per day (no repeat voting for the same enterprise/category)
- Lists display only statistical results, no voter information revealed

#### 3. Evidence Submission Mechanism
- Image formats: JPG, JPEG, PNG
- Document formats: PDF, DOCX
- File size limit: 5MB
- One-time evidence submission per vote

#### 4. User Privacy Protection

| Protection Measure | Technical Implementation |
|-------------------|--------------------------|
| **Sensitive Data Encryption** | Fernet symmetric encryption for phone numbers and sensitive information |
| **Device Fingerprinting** | MD5(UserAgent + ScreenResolution + Timezone) generates unique identifier |
| **IP Rate Limiting** | django-ratelimit middleware, max 3 votes per IP daily |
| **Code Verification Binding** | Re-verification required for each vote via SMS code |

### 🛡️ Anti-Fraud Mechanism

#### Technical Architecture
```
Layer 1: User Identity Authentication
├── Phone number + 6-digit verification code dual authentication
└── Token-based authentication (24-hour validity)

Layer 2: Device Fingerprint Recognition
├── MD5(UserAgent + ScreenResolution + Timezone)
└── Cross-device tracking to prevent multi-account fraud

Layer 3: IP Rate Limiting
├── django-ratelimit middleware
├── Maximum 3 votes per IP per day
└── Automatic ban for suspicious IPs

Layer 4: Business Rule Constraints
├── Daily user vote limit: 3 votes
├── No repeat voting for same enterprise/category
└── Evidence upload time-limited (only on first submission)
```

#### Verification Algorithm Pseudocode
```python
def check_vote_eligibility(user, category, company):
    # 1. Daily user vote count check
    daily_votes = Vote.objects.filter(
        voter_id=user.id,
        category=category,
        created_at__gte=today_midnight
    ).count()
    if daily_votes >= 3:
        raise TooManyRequestsError("Daily vote limit reached")

    # 2. Duplicate voting check
    existing = Vote.objects.filter(
        voter_id=user.id,
        company=company,
        category=category
    ).exists()
    if existing:
        raise ValidationError("Already voted for this enterprise in this category")

    # 3. IP frequency limit check
    ip_address = request.META.get('REMOTE_ADDR')
    ip_votes_today = Vote.objects.filter(
        ip_address__startswith=ip_address.split(',')[0],
        created_at__gte=today_midnight
    ).count()
    if ip_votes_today >= 3:
        raise TooManyRequestsError("IP daily vote limit reached")

    # 4. Verification code validation
    if not verify_code(user.phone, request.data['code']):
        raise ValidationError("Invalid or expired verification code")

    return True
```

### 🌱 Open Source Purpose and Goals

#### Why Choose Open Source?

1. **Transparency and Trust**: Open-source code makes all algorithms and logic fully public for anyone to audit voting mechanism fairness
2. **Collective Wisdom**: Aggregates global developer expertise for continuous optimization of system performance and security
3. **Broad Participation**: Lowers technical barriers, enabling more people to engage with employment discrimination issues and participate in social supervision
4. **Sustainable Development**: Community maintenance ensures long-term stable operation independent of any single team

#### Core Objectives

| Short-term | Mid-term | Long-term |
|------------|----------|-----------|
| Establish comprehensive reporting and voting mechanisms | Expand to cover more employment discrimination types | Build a global worker rights protection network |
| Accumulate authentic data, drive corporate self-reflection | Multi-language support and cross-platform deployment | Develop independent third-party social supervision standards |
| Increase public awareness of employment discrimination | Collaborate with NGOs/research institutions on reports | Promote improvements in relevant policies and regulations |

### 🤝 Community Collaboration

#### Welcome Contributions

This project is completely open-source. We warmly welcome:

- **Developers**: Participate in code development, bug fixes, performance optimization
- **Testers**: Discover issues, submit Bug Reports, provide improvement suggestions
- **Translators**: Assist with multi-language localization work
- **Promoters**: Help spread the project mission and expand social influence
- **Deployment Volunteers**: Host mirror sites on various cloud platforms for free

#### How to Participate

1. Visit GitHub repository, Star ⭐️ this project to show support
2. Fork repository, create Feature Branches for new feature development
3. Submit Pull Requests with descriptions of changes and rationale
4. Open Issues to report bugs or suggest features

### 📜 Terms of Use and Licensing

#### Non-Commercial Use
- ✅ Free download, research, and learning allowed
- ✅ Free mirror site deployment within communities permitted
- ✅ Educational and research non-commercial use allowed
- ✅ Forking and secondary development on GitHub welcome

#### Commercial Use
For any commercial application of this project or its derivatives (including but not limited to paid services, ad-supported platforms, commercialized SaaS offerings), **written authorization from the project maintainers must be obtained in advance**.

Contact methods: Via GitHub Issues or email.

### 📢 Regarding Minors

**Minors and individuals lacking independent decision-making capacity are advised to use this platform under guardian supervision.** Our goal is promoting social progress, not generating unnecessary controversy or harm.

### ⚖️ Legal Disclaimer

Platform data originates from citizen voting and evidence submission:
- List results are for reference only, **do not constitute factual determinations**
- **Not targeted at any enterprise or individual**, purely statistical display
- **No legal effect**, cannot be used as basis for legal proceedings
- Users must **think independently and carefully verify information authenticity**
- Platform **assumes no legal liability**

### 🙏 Acknowledgments

Gratitude to all volunteers and contributors engaged in social governance and protecting worker rights!

Thanks to the open-source community for providing technical frameworks:
- [Django](https://www.djangoproject.com/) - Web Framework
- [Django REST Framework](https://www.django-rest-framework.org/) - API Development
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - Desktop Client

---

**让每一票都有力量 · Let Every Vote Have Power · 推动更公平的社会环境 · Building a Fairer Society Together**
