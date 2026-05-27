# DormFix - 宿舍报修与维修进度管理系统

软件工程课程大作业 — 第二组

## 项目简介

DormFix 是一个面向高校宿舍的报修与维修进度管理系统，支持学生在线报修、管理员审核派单、维修人员处理任务、服务评价与投诉等功能。

## 功能特性

- **用户管理**: 支持学生、管理员、维修人员三种角色
- **报修管理**: 学生提交报修、查看进度、撤销工单
- **派单管理**: 管理员审核报修、派发任务给维修人员
- **维修处理**: 维修人员接单、更新状态、学生确认完成
- **评价投诉**: 学生对维修服务进行评价和投诉
- **数据统计**: 管理员查看统计报表、导出Excel

## 技术栈

- **后端**: Django 4.2 + Django REST Framework
- **数据库**: SQLite (开发) / MySQL (部署)
- **认证**: Token Authentication

## 项目结构

```
software_engineering/
├── src/dormfix/               # Django项目
│   ├── accounts/              # 用户管理模块
│   ├── repairs/               # 报修管理模块
│   ├── dispatch/              # 派单管理模块
│   ├── maintenance/           # 维修处理模块
│   ├── feedback/              # 评价投诉模块
│   ├── dashboard/             # 数据统计模块
│   ├── templates/             # 前端页面
│   ├── static/                # 静态资源
│   └── create_seed_data.py    # 种子数据脚本
├── tests/                     # 单元测试
├── docs/                      # 文档
├── requirements.txt           # Python依赖
└── README.md
```

## 快速开始

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

# 创建种子数据
python create_seed_data.py

# 启动服务器
python manage.py runserver
```

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

详见 [API接口文档](docs/api_documentation.md)

## 协作者

- @sunsun3662
- @samar2334
- @Wyb2310425
- @heye723902338
