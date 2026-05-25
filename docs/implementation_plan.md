# DormFix - Django 实现计划 (前后端分离版)

## 背景

软件工程课程作业，两人并行开发。系统为"宿舍报修与维修进度管理系统"。

## 技术选型

- **后端**: Django 4.2 + Django REST Framework
- **前端**: HTML + Bootstrap 5 + JavaScript (独立页面，通过AJAX调用API)
- **数据库**: SQLite (开发) → MySQL 8.0 (部署)
- **认证**: DRF Token Authentication

## 项目结构

```
software_engineering/
├── src/
│   └── dormfix/
│       ├── manage.py
│       ├── dormfix/              # 项目配置
│       │   ├── settings.py
│       │   ├── urls.py
│       │   └── wsgi.py
│       ├── accounts/             # 用户管理
│       │   ├── models.py         # User, DormBuilding, DormRoom
│       │   ├── serializers.py
│       │   ├── views.py          # 登录、注册、个人信息API
│       │   └── urls.py
│       ├── repairs/              # 报修管理
│       │   ├── models.py         # WorkOrder, WorkOrderLog
│       │   ├── serializers.py
│       │   ├── views.py          # 报修CRUD API
│       │   └── urls.py
│       ├── dispatch/             # 派单管理
│       │   ├── serializers.py
│       │   ├── views.py          # 审核、派单 API
│       │   └── urls.py
│       ├── maintenance/          # 维修处理
│       │   ├── serializers.py
│       │   ├── views.py          # 接单、更新状态、确认完成 API
│       │   └── urls.py
│       ├── feedback/             # 评价投诉
│       │   ├── models.py         # Evaluation, Complaint
│       │   ├── serializers.py
│       │   ├── views.py          # 评价、投诉 API
│       │   └── urls.py
│       ├── dashboard/            # 数据统计
│       │   ├── views.py          # 统计报表 API
│       │   └── urls.py
│       ├── templates/            # 前端页面 (前端同学负责)
│       │   ├── base.html
│       │   ├── login.html
│       │   ├── student/          # 学生端页面
│       │   ├── admin/            # 管理员端页面
│       │   └── maintainer/       # 维修人员端页面
│       ├── static/               # CSS/JS (前端同学负责)
│       │   ├── css/
│       │   └── js/
│       └── media/                # 上传文件
├── tests/
│   ├── test_accounts.py
│   ├── test_repairs.py
│   ├── test_dispatch.py
│   ├── test_maintenance.py
│   ├── test_feedback.py
│   └── test_dashboard.py
├── requirements.txt
└── README.md
```

## 两人分工 (完全独立，并行开发)

### Person A: 后端开发

**工作范围**: `src/dormfix/` 下所有Python代码（除templates和static）

**职责**:
1. Django项目初始化和配置 (settings.py)
2. 数据库模型 (所有models.py)
3. 序列化器 (所有serializers.py)
4. API视图 (所有views.py)
5. URL路由 (所有urls.py)
6. 权限控制和认证
7. 数据库迁移脚本
8. 种子数据脚本 (create_seed_data.py)
9. requirements.txt
10. 单元测试 (tests/)
11. API接口文档 (供前端参考)

**交付物**:
- 可运行的API服务
- API接口文档（每个接口的URL、参数、返回格式）
- 测试代码

---

### Person B: 前端开发

**工作范围**: `templates/` 和 `static/` 目录

**职责**:
1. base.html (公共布局、导航栏)
2. 所有页面模板:
   - login.html (登录页)
   - student/*.html (学生端：报修表单、我的工单、工单详情、评价、投诉)
   - admin/*.html (管理员端：审核列表、派单列表、统计报表)
   - maintainer/*.html (维修人员端：我的任务、更新状态)
3. CSS样式 (Bootstrap 5 + 自定义样式)
4. JavaScript:
   - API调用封装 (api.js)
   - 图片上传预览
   - 星级评分组件
   - 状态时间线组件
   - 统计图表 (Chart.js)
   - 表单验证
   - 确认对话框
5. 响应式设计 (移动端适配)

**交付物**:
- 所有前端页面
- 静态资源文件

---

## 前后端接口约定

两人通过API文档解耦，后端先定义好接口格式，前端独立开发。

### 认证接口
```
POST /api/accounts/login/
请求: { "account": "xxx", "password": "xxx" }
响应: { "token": "xxx", "user": { "id": 1, "name": "xxx", "role": "student" } }
```

### 报修接口
```
GET    /api/repairs/                    # 获取工单列表
POST   /api/repairs/                    # 创建报修
GET    /api/repairs/{id}/               # 获取工单详情
POST   /api/repairs/{id}/cancel/        # 撤销工单
```

### 派单接口 (管理员)
```
GET    /api/dispatch/pending-review/    # 待审核列表
POST   /api/dispatch/{id}/approve/      # 审核通过
POST   /api/dispatch/{id}/reject/       # 审核驳回
GET    /api/dispatch/pending-dispatch/  # 待派单列表
POST   /api/dispatch/{id}/assign/       # 派发任务
GET    /api/dispatch/maintainers/       # 维修人员列表
```

### 维修接口
```
GET    /api/maintenance/tasks/          # 我的任务列表
POST   /api/maintenance/{id}/accept/    # 接收任务
POST   /api/maintenance/{id}/complete/  # 完成维修
POST   /api/maintenance/{id}/confirm/   # 学生确认完成
```

### 评价投诉接口
```
POST   /api/feedback/evaluate/{id}/     # 提交评价
POST   /api/feedback/complaint/{id}/    # 提交投诉
GET    /api/feedback/complaints/         # 投诉列表 (管理员)
POST   /api/feedback/complaints/{id}/process/  # 处理投诉
```

### 统计接口 (管理员)
```
GET    /api/dashboard/statistics/       # 获取统计数据
GET    /api/dashboard/export/           # 导出报表
```

### 基础数据接口
```
GET    /api/accounts/profile/           # 获取个人信息
PUT    /api/accounts/profile/           # 更新个人信息
GET    /api/accounts/buildings/         # 宿舍楼列表
GET    /api/accounts/rooms/?building=1  # 某楼栋的房间列表
```

---

## 数据库模型 (后端负责)

| 模型 | 字段 |
|------|------|
| User | id, account, name, student_or_staff_no, phone, role, status, created_at |
| DormBuilding | id, building_code, building_name, gender_limit |
| DormRoom | id, building(FK), room_no, floor_no |
| WorkOrder | id, order_no, student(FK), maintainer(FK), room(FK), category, description, image, urgency_level, status, submit_time, assign_time, finish_time, cancel_flag |
| WorkOrderLog | id, work_order(FK), operator(FK), from_status, to_status, operation_type, operation_time, remark |
| Evaluation | id, work_order(OneToOne), score, content, created_at |
| Complaint | id, work_order(FK), student(FK), content, process_result, status, created_at, handled_at |

---

## 开发阶段

### Phase 1: 基础搭建 (Day 1-2) - 两人并行
**后端**:
- Django项目初始化
- 所有models.py
- 数据库迁移
- 登录API (Token认证)
- 种子数据脚本

**前端**:
- base.html 搭建
- 登录页面
- api.js (API调用封装，含token管理)

**接口约定**: 登录API格式确定

### Phase 2: 核心功能 (Day 3-6) - 两人并行
**后端**:
- 报修CRUD API (UC002-004)
- 派单API (UC005-006)
- 维修API (UC007-009)

**前端**:
- 学生端页面 (报修表单、我的工单、工单详情)
- 管理员端页面 (审核、派单)
- 维修人员端页面 (我的任务)

**接口约定**: 所有业务API格式确定

### Phase 3: 评价统计 (Day 7-9) - 两人并行
**后端**:
- 评价API (UC010)
- 投诉API (UC011)
- 统计API (UC012)
- 报表导出API

**前端**:
- 评价页面 (星级评分组件)
- 投诉页面
- 统计报表页面 (图表组件)

### Phase 4: 测试完善 (Day 10-12) - 两人并行
**后端**:
- 单元测试
- API测试
- Bug修复

**前端**:
- 页面美化
- 响应式适配
- 交互优化

### Phase 5: 集成联调 (Day 13-14) - 两人合作
- 前后端联调
- 集成测试
- Bug修复
- 演示准备

---

## 依赖包

```
# 后端
Django>=4.2,<5.0
djangorestframework>=3.14
django-cors-headers>=4.0
Pillow>=10.0
openpyxl>=3.1
```

## 验证方式

1. 启动后端API服务
2. 打开前端页面，完整走一遍业务流程
3. 测试三个角色各自的权限
4. 测试异常流程
5. 移动端浏览器测试
