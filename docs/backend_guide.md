# DormFix 后端 (Django) 开发指导指南

> 本指南供后端开发人员（Person A）参考，专门用于从已写好的前端代码和开发计划出发，设计和编码与之 100% 对齐的 Django 后端服务。
> 前端已完成所有的 HTML 页面（`src/dormfix/templates/`）、样式表（`src/dormfix/static/css/`）和 AJAX 异步代码（`src/dormfix/static/js/`），后端开发时请以此文档的详细参数要求为准。

---

## 📂 一、前端静态与模板资源物理路径

前端页面已在以下路径写好，后端在配置 Django 项目时需保证对应的目录结构：
- **静态资源文件夹**: `src/dormfix/static/`
  - 核心 CSS: [style.css](file:///e:/软件工程大作业/software_engineering/src/dormfix/static/css/style.css)
  - 核心 JS AJAX 封装: [api.js](file:///e:/软件工程大作业/software_engineering/src/dormfix/static/js/api.js)
- **模板资源文件夹**: `src/dormfix/templates/`
  - 骨架母版: [base.html](file:///e:/软件工程大作业/software_engineering/src/dormfix/templates/base.html)
  - 登录入口: [login.html](file:///e:/软件工程大作业/software_engineering/src/dormfix/templates/login.html)
  - 个人中心: [profile.html](file:///e:/软件工程大作业/software_engineering/src/dormfix/templates/profile.html)
  - 学生端 (templates/student/): [dashboard.html](file:///e:/软件工程大作业/software_engineering/src/dormfix/templates/student/dashboard.html), [repair_request.html](file:///e:/软件工程大作业/software_engineering/src/dormfix/templates/student/repair_request.html), [order_detail.html](file:///e:/软件工程大作业/software_engineering/src/dormfix/templates/student/order_detail.html), [evaluate.html](file:///e:/软件工程大作业/software_engineering/src/dormfix/templates/student/evaluate.html), [complaint.html](file:///e:/软件工程大作业/software_engineering/src/dormfix/templates/student/complaint.html)
  - 管理员端 (templates/admin/): [dashboard.html](file:///e:/软件工程大作业/software_engineering/src/dormfix/templates/admin/dashboard.html), [complaints.html](file:///e:/软件工程大作业/software_engineering/src/dormfix/templates/admin/complaints.html), [statistics.html](file:///e:/软件工程大作业/software_engineering/src/dormfix/templates/admin/statistics.html)
  - 维修员端 (templates/maintainer/): [dashboard.html](file:///e:/软件工程大作业/software_engineering/src/dormfix/templates/maintainer/dashboard.html)

---

## 🔒 二、前端 AJAX 机制与后端认证要求

### 2.1 Token 头约定
前端在 [api.js](file:///e:/软件工程大作业/software_engineering/src/dormfix/static/js/api.js) 中全局封包了 Fetch 请求。对于所有非登录接口，前端会在 Header 中加入：
```http
Authorization: Token <your_token>
```
后端必须在 Django REST Framework (DRF) 中启用 `TokenAuthentication`，并在未通过校验时返回标准 `401 Unauthorized` 状态码，前端将据此拦截并自动重定向跳转至 `/login/`。

### 2.2 响应状态码及错误负载要求
*   **字段验证失败 (400)**: 前端支持直接解析**键值对数组**类型错误（如 `{ "description": ["此字段不能为空"] }`），并会动态将其渲染在对应表单的下方 `.invalid-feedback` 中。
*   **全局业务拦截错误 (403)**: 前端遇到阻断型拦截（如学生报修超3件）时，会读取返回的 `{ "error": "错误说明信息" }` 并弹出大警告框。

---

## 📡 三、各页面对应的后端 API 详尽参数约定

请按照以下页面中已写好的 AJAX 逻辑，在后端实现对应的 Serializer 与 View：

### 3.1 登录页 ([login.html](file:///e:/软件工程大作业/software_engineering/src/dormfix/templates/login.html))
*   **接口**: `POST /api/accounts/login/`
*   **输入**: `{ "account": "username", "password": "password" }`
*   **输出 (200)**:
    ```json
    {
        "token": "加密的Token字符串",
        "user": {
            "id": 1,
            "account": "student001",
            "name": "张三",
            "role": "student", // 只能是 student, admin, maintainer
            "student_or_staff_no": "2023001"
        }
    }
    ```
*   **登录锁定拦截**: 登录失败 5 次，后端应将对应 User 实体的 `lockout_until` 更新为 15 分钟后，并在此期间返回 `400` 错误：`{ "error": "账户已临时锁定，请于XX分后重试" }`。

### 3.2 个人中心 ([profile.html](file:///e:/软件工程大作业/software_engineering/src/dormfix/templates/profile.html))
*   **获取个人信息接口**: `GET /api/accounts/profile/`
    *   **输出**: `{ "id": 1, "account": "st01", "name": "张三", "student_or_staff_no": "2023", "phone": "138...", "role": "student", "status": 1, "created_at": "ISO时间串" }`
*   **更新个人信息接口**: `PUT /api/accounts/profile/`
    *   **输入**: `{ "name": "新名字", "phone": "新电话" }`
    *   **输出 (200)**: `{ "id": 1, "name": "新名字", "phone": "新电话", "message": "更新成功" }`

### 3.3 学生仪表盘 ([dashboard.html](file:///e:/软件工程大作业/software_engineering/src/dormfix/templates/student/dashboard.html))
*   **工单列表接口**: `GET /api/repairs/?page=1&page_size=6` (支持筛选 `&status=xxx`、`&category=xxx`)
*   **输出 (标准分页结构)**:
    ```json
    {
        "count": 25,
        "next": "下一页的完整URL",
        "previous": "上一页的完整URL",
        "results": [
            {
                "id": 1,
                "order_no": "WX20260525000001",
                "category": "water_electric",
                "category_display": "水电",
                "description": "水龙头故障",
                "urgency_level": "normal",
                "urgency_level_display": "普通",
                "status": "pending_review",
                "submit_time": "2026-05-25T10:00:00",
                "room": {
                    "building_name": "1号楼",
                    "room_no": "101"
                }
            }
        ]
    }
    ```

### 3.4 发起报修申请 ([repair_request.html](file:///e:/软件工程大作业/software_engineering/src/dormfix/templates/student/repair_request.html))
*   **获取宿舍楼栋**: `GET /api/accounts/buildings/` -> 返回包含多个 `{ "id": 1, "building_name": "1号楼", "gender_limit": "男" }` 的 **JSON 数组**。
*   **获取关联房间**: `GET /api/accounts/rooms/?building={id}` -> 返回包含多个 `{ "id": 10, "room_no": "101", "floor_no": 1 }` 的 **JSON 数组**。
*   **提交报修 (FormData)**: `POST /api/repairs/`
    *   **载荷 (multipart/form-data)**: 包含 `room` (房间ID), `category`, `description`, `urgency_level` 和**多个同名文件项** `images`（后端应支持 `request.FILES.getlist('images')` 获取多个文件并进行保存）。
    *   **超限拦截**: 未结工单超 3 件时直接返回 `403` 错误：`{ "error": "您当前有多个工单正在处理中，暂不能提交新报修" }`。

### 3.5 工单详情与动作 ([order_detail.html](file:///e:/软件工程大作业/software_engineering/src/dormfix/templates/student/order_detail.html))
*   **详情接口**: `GET /api/repairs/{id}/`
    *   **输出**:
        ```json
        {
            "id": 1,
            "order_no": "WX2026...",
            "student": { "name": "张三", "phone": "138..." },
            "room": { "building_name": "1号楼", "room_no": "101" },
            "description": "描述...",
            "image_urls": ["/media/repair_images/pic1.jpg"], // 附件图片完整路径数组
            "maintainer": { "name": "李四", "phone": "136..." }, // 若尚未派单则返回 null
            "status": "pending_confirm",
            "status_display": "已完成待确认",
            "logs": [
                {
                    "operation_type": "提交报修",
                    "operator": { "name": "张三" },
                    "operation_time": "2026-05-25T10:00:00",
                    "remark": "附加信息" // 可选
                }
            ]
        }
        ```
*   **撤销工单**: `POST /api/repairs/{id}/cancel/` -> 返回 `{ "message": "报修申请已撤销" }`。
*   **确认/返修操作**: `POST /api/maintenance/{id}/confirm/`
    *   **输入 (确认完成)**: `{ "confirmed": true }` -> 返回 `{ "message": "已确认完成", "status": "completed" }`。
    *   **输入 (申请返修)**: `{ "confirmed": false, "reason": "返修原因" }` -> 后端需在 `logs` 中记录备注并自动将工单状态调回 `in_progress` -> 返回 `{ "message": "已申请返修", "status": "in_progress" }`。

### 3.6 评价与投诉
*   **评价工单 ([evaluate.html](file:///e:/软件工程大作业/software_engineering/src/dormfix/templates/student/evaluate.html))**: `POST /api/feedback/evaluate/{work_order_id}/`
    *   **输入**: `{ "speed_score": 5, "attitude_score": 4, "quality_score": 5, "content": "评语" }`
    *   **输出 (201)**: `{ "message": "感谢您的评价", "evaluation_id": 1 }`
*   **投诉工单 ([complaint.html](file:///e:/软件工程大作业/software_engineering/src/dormfix/templates/student/complaint.html))**: `POST /api/feedback/complaint/{work_order_id}/`
    *   **输入**: `{ "type": "quality", "content": "原因..." }`
    *   **输出 (201)**: `{ "message": "投诉已提交，管理员将尽快处理", "complaint_id": 1 }`

### 3.7 管理员工作台 ([dashboard.html](file:///e:/软件工程大作业/software_engineering/src/dormfix/templates/admin/dashboard.html))
*   **待审核列表**: `GET /api/dispatch/pending-review/` -> 返回分页格式，含 results 数组。
*   **审核通过**: `POST /api/dispatch/{id}/approve/` -> 返回 `{ "message": "审核通过，工单已进入派单队列", "status": "pending_dispatch" }`。
*   **审核驳回**: `POST /api/dispatch/{id}/reject/` -> 输入 `{ "reason": "驳回原因" }` -> 返回 `{ "message": "已驳回", "status": "rejected" }`。
*   **待派单列表**: `GET /api/dispatch/pending-dispatch/` -> 返回分页格式，含 results 数组。
*   **获取维修工列表**: `GET /api/dispatch/maintainers/` -> 返回包含多个 `{ "id": 3, "name": "李师傅", "student_or_staff_no": "W01", "phone": "13...", "today_task_count": 2, "status": "在岗" }` 的 **JSON 数组**。
*   **指派任务**: `POST /api/dispatch/{id}/assign/`
    *   **输入**: `{ "maintainer_id": 3 }`
    *   **输出 (200)**: `{ "message": "派发成功", "status": "assigned" }`
    *   **超载拦截**: 对应工人的 `today_task_count >= 5` 时返回 `400` 错误 `{ "error": "该维修人员今日任务已饱和，请重新选择" }`。

### 3.8 管理员投诉处理 ([complaints.html](file:///e:/软件工程大作业/software_engineering/src/dormfix/templates/admin/complaints.html))
*   **拉取投诉列表**: `GET /api/feedback/complaints/` (支持状态筛选 `&status=pending`) -> 返回分页 results 格式。
*   **投诉处理接口**: `POST /api/feedback/complaints/{id}/process/`
    *   **输入**: `{ "result": "调查及处理结果说明", "status": "resolved" }`
    *   **输出 (200)**: `{ "message": "投诉已处理", "status": "resolved" }`

### 3.9 管理员统计与报表 ([statistics.html](file:///e:/软件工程大作业/software_engineering/src/dormfix/templates/admin/statistics.html))
*   **获取分析数据**: `GET /api/dashboard/statistics/` (支持参数过滤 `&start_date=...&end_date=...&building=...&category=...`)
    *   **输出**: 需符合 Chart.js 图表渲染所需的多维数据包：
        ```json
        {
            "summary": {
                "total_orders": 150, "completed_orders": 120, "completion_rate": 80.0,
                "avg_response_hours": 3.5, "avg_completion_hours": 24.0, "urgent_orders": 15
            },
            "category_distribution": [
                { "category": "water_electric", "count": 60 }, { "category": "door_window", "count": 30 }
            ],
            "status_distribution": [
                { "status": "pending_review", "count": 5 }, { "status": "in_progress", "count": 10 }
            ],
            "daily_trend": [
                { "date": "2026-05-20", "count": 12 }
            ],
            "maintainer_performance": [
                { "maintainer": "王师傅", "completed_count": 45, "avg_hours": 18.5, "avg_score": 4.8 }
            ],
            "satisfaction_distribution": [
                { "score": 5, "count": 50 }, { "score": 4, "count": 40 }
            ]
        }
        ```
*   **导出 Excel 报表**: `GET /api/dashboard/export/` (支持参数过滤) -> 后端使用 `openpyxl` 生成表单并返回 `HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')` 文件二进制流。

### 3.10 维修工控制台 ([dashboard.html](file:///e:/软件工程大作业/software_engineering/src/dormfix/templates/maintainer/dashboard.html))
*   **我的任务列表**: `GET /api/maintenance/tasks/?status=assigned` (或 `status=in_progress`) -> 返回分页 results 格式。
*   **接收任务**: `POST /api/maintenance/{id}/accept/` -> 返回 `{ "message": "已接单", "status": "in_progress" }`。
*   **完工反馈**: `POST /api/maintenance/{id}/complete/`
    *   **输入**: `{ "result": "维修结果说明", "materials": "耗材说明 (选填)" }`
    *   **输出 (200)**: `{ "message": "维修完成，等待学生确认", "status": "pending_confirm" }`
