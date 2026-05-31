# DormFix - 宿舍报修与维修进度管理系统

软件工程课程大作业 — 第二组

## 项目简介

DormFix 是一个面向高校宿舍的报修与维修进度管理系统，支持学生在线报修、管理员审核派单、维修人员处理任务、服务评价与投诉等功能。系统采用前后端分离架构，提供完整的RESTful API和现代化的Web前端界面。

## 功能特性

### 用户管理
- 支持学生、管理员、维修人员三种角色
- 用户注册、登录、个人信息管理
- 管理员可管理所有用户账户（新增/编辑/删除/重置密码）

### 报修管理
- 学生提交报修申请（支持多级分类选择）
- 查看报修进度和工单详情
- 撤销未派发的工单

### 派单管理
- 管理员审核报修申请
- 派发任务给指定维修人员
- 查看派单历史记录

### 维修处理
- 维修人员接单处理
- 更新维修状态和进度
- 学生确认维修完成

### 评价投诉
- 学生对维修服务进行评价（1-5星评分）
- 提交投诉和意见反馈
- 管理员处理投诉工单

### 数据统计
- 管理员查看统计报表
- 支持导出Excel报表
- 图表可视化展示（使用ECharts）

### 前端界面
- 响应式设计，支持多设备访问
- 学生端：工单列表、报修申请、进度时间线、评价投诉
- 维修端：接单看板、任务管理
- 管理端：审核派单、用户管理、投诉处理、数据统计

## 技术栈

### 后端
- **框架**: Django 4.2 + Django REST Framework
- **数据库**: SQLite (开发) / MySQL (部署)
- **认证**: Token Authentication
- **图片处理**: Pillow
- **Excel导出**: openpyxl

### 前端
- **模板引擎**: Django Template
- **CSS框架**: Tailwind CSS
- **图表库**: ECharts
- **JavaScript**: 原生JS + Fetch API

## 数据库

### 数据库配置

开发环境使用SQLite，生产环境可切换为MySQL。

```python
# settings.py 数据库配置
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # 开发环境
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 生产环境MySQL配置示例
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'dormfix_db',
#         'USER': 'root',
#         'PASSWORD': 'your_password',
#         'HOST': 'localhost',
#         'PORT': '3306',
#     }
# }
```

### 数据库表结构

系统包含以下主要数据表：

#### 用户相关
| 表名 | 说明 | 主要字段 |
|------|------|----------|
| `user` | 用户表 | account, name, student_or_staff_no, phone, role, status |
| `dorm_building` | 宿舍楼表 | building_code, building_name, gender_limit |
| `dorm_room` | 宿舍房间表 | building(FK), room_no, floor_no |

#### 工单相关
| 表名 | 说明 | 主要字段 |
|------|------|----------|
| `work_order` | 报修工单表 | order_no, student(FK), maintainer(FK), room(FK), category, status |
| `work_order_image` | 工单图片表 | work_order(FK), image |
| `work_order_log` | 工单日志表 | work_order(FK), operator(FK), from_status, to_status, operation_type |

#### 评价投诉相关
| 表名 | 说明 | 主要字段 |
|------|------|----------|
| `evaluation` | 服务评价表 | work_order(O2O), speed_score, attitude_score, quality_score, content |
| `complaint` | 投诉记录表 | work_order(FK), student(FK), type, content, status, process_result |

### 数据库迁移

```bash
# 进入Django项目目录
cd src/dormfix

# 创建迁移文件
python manage.py makemigrations

# 执行迁移
python manage.py migrate

# 查看迁移状态
python manage.py showmigrations
```

### 种子数据

项目提供种子数据脚本，用于初始化测试数据：

```bash
cd src/dormfix
python create_seed_data.py
```

种子数据包含：
- 3个测试账号（管理员、学生、维修人员）
- 宿舍楼和房间数据
- 示例报修工单
- 评价和投诉记录

## 项目结构

```
software_engineering/
├── src/dormfix/                   # Django项目根目录
│   ├── accounts/                  # 用户管理模块
│   ├── repairs/                   # 报修管理模块
│   ├── dispatch/                  # 派单管理模块
│   ├── maintenance/               # 维修处理模块
│   ├── feedback/                  # 评价投诉模块
│   ├── dashboard/                 # 数据统计模块
│   ├── templates/                 # 前端页面模板
│   │   ├── base.html              # 基础模板
│   │   ├── login.html             # 登录页
│   │   ├── profile.html           # 个人中心
│   │   ├── student/               # 学生端页面
│   │   ├── maintainer/            # 维修端页面
│   │   └── admin/                 # 管理端页面
│   ├── static/                    # 静态资源（CSS/JS/图片）
│   ├── media/                     # 用户上传文件
│   ├── tests/                     # 单元测试
│   ├── create_seed_data.py        # 种子数据脚本
│   └── manage.py                  # Django管理脚本
├── docs/                          # 项目文档
│   ├── api_documentation.md       # API接口文档
│   ├── backend_guide.md           # 后端开发指南
│   └── implementation_plan.md     # 实现计划
├── requirements.txt               # Python依赖
└── README.md
```

## 快速开始

### 环境要求
- Python 3.9+
- pip

### 安装步骤

```bash
# 克隆仓库
git clone https://github.com/sunsun3662/software_engineering.git

# 进入项目目录
cd software_engineering

# 创建虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# 安装依赖
pip install -r requirements.txt

# 进入Django项目目录
cd src/dormfix

# 数据库迁移
python manage.py migrate

# 创建种子数据（包含测试账号和示例数据）
python create_seed_data.py

# 启动开发服务器
python manage.py runserver
```

访问 http://127.0.0.1:8000/ 即可使用系统。

## 测试账号

| 角色 | 账号 | 密码 |
|------|------|------|
| 管理员 | admin | admin123456 |
| 学生 | student001 | 123456 |
| 维修人员 | maintainer001 | 123456 |

## 运行测试

```bash
cd src/dormfix
python manage.py test tests --verbosity=2
```

## API接口

系统提供完整的RESTful API，详见 [API接口文档](docs/api_documentation.md)

### 主要API端点

- `/api/accounts/` - 用户认证与管理
- `/api/repairs/` - 报修工单管理
- `/api/dispatch/` - 派单管理
- `/api/maintenance/` - 维修处理
- `/api/feedback/` - 评价投诉
- `/api/dashboard/` - 数据统计

## 文档

- [API接口文档](docs/api_documentation.md) - 详细的API接口说明
- [后端开发指南](docs/backend_guide.md) - 后端架构和开发规范
- [实现计划](docs/implementation_plan.md) - 项目实现计划和进度


## 协作者

- @sunsun3662
- @samar2334
- @Wyb2310425
- @heye723902338


