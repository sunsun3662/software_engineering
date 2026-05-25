# DormFix API 接口文档

> 后端提供给前端的接口说明，前端根据此文档开发页面。

## 基础信息

- **Base URL**: `http://localhost:8000/api`
- **认证方式**: Token Authentication
- **请求头**: `Authorization: Token <your_token>`
- **数据格式**: JSON

---

## 一、认证接口 (accounts)

### 1.1 登录

```
POST /api/accounts/login/
```

**请求**:
```json
{
    "account": "student001",
    "password": "123456"
}
```

**响应 (200)**:
```json
{
    "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
    "user": {
        "id": 1,
        "account": "student001",
        "name": "张三",
        "role": "student",
        "student_or_staff_no": "2023001"
    }
}
```

**错误响应 (400)**:
```json
{
    "error": "账号或密码错误"
}
```

---

### 1.2 登出

```
POST /api/accounts/logout/
```

**请求头**: `Authorization: Token <token>`

**响应 (200)**:
```json
{
    "message": "登出成功"
}
```

---

### 1.3 获取个人信息

```
GET /api/accounts/profile/
```

**请求头**: `Authorization: Token <token>`

**响应 (200)**:
```json
{
    "id": 1,
    "account": "student001",
    "name": "张三",
    "student_or_staff_no": "2023001",
    "phone": "13800138000",
    "role": "student",
    "status": 1,
    "created_at": "2026-05-25T10:00:00"
}
```

---

### 1.4 更新个人信息

```
PUT /api/accounts/profile/
```

**请求**:
```json
{
    "name": "张三",
    "phone": "13900139000"
}
```

**响应 (200)**:
```json
{
    "id": 1,
    "name": "张三",
    "phone": "13900139000",
    "message": "更新成功"
}
```

---

### 1.5 获取宿舍楼列表

```
GET /api/accounts/buildings/
```

**响应 (200)**:
```json
[
    {
        "id": 1,
        "building_code": "A01",
        "building_name": "1号楼",
        "gender_limit": "男"
    },
    {
        "id": 2,
        "building_code": "A02",
        "building_name": "2号楼",
        "gender_limit": "女"
    }
]
```

---

### 1.6 获取房间列表

```
GET /api/accounts/rooms/?building=1
```

**参数**:
- `building`: 楼栋ID (必填)

**响应 (200)**:
```json
[
    {
        "id": 1,
        "building": 1,
        "room_no": "101",
        "floor_no": 1
    },
    {
        "id": 2,
        "building": 1,
        "room_no": "102",
        "floor_no": 1
    }
]
```

---

## 二、报修接口 (repairs)

### 2.1 获取工单列表

```
GET /api/repairs/
```

**权限**: 学生只能看自己的，管理员看全部

**查询参数**:
- `status`: 按状态筛选 (可选)
- `category`: 按类别筛选 (可选)
- `page`: 页码 (默认1)
- `page_size`: 每页数量 (默认10)

**响应 (200)**:
```json
{
    "count": 25,
    "next": "http://localhost:8000/api/repairs/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "order_no": "WX17166432001234",
            "student": {
                "id": 1,
                "name": "张三"
            },
            "room": {
                "id": 1,
                "building_name": "1号楼",
                "room_no": "101"
            },
            "category": "water_electric",
            "category_display": "水电",
            "description": "水龙头漏水",
            "urgency_level": "normal",
            "urgency_level_display": "普通",
            "status": "pending_review",
            "status_display": "待审核",
            "submit_time": "2026-05-25T10:00:00",
            "image_urls": ["/media/repair_images/1.jpg"]
        }
    ]
}
```

---

### 2.2 创建报修

```
POST /api/repairs/
```

**权限**: 仅学生

**请求 (multipart/form-data)**:
```
room: 1
category: water_electric
description: 水龙头漏水，已经三天了
urgency_level: normal
images: [文件1, 文件2, 文件3]  (可选，最多3张，每张≤5MB)
```

**category 可选值**:
- `water_electric` - 水电
- `door_window` - 门窗
- `network` - 网络
- `furniture` - 家具
- `other` - 其他

**urgency_level 可选值**:
- `normal` - 普通 (默认)
- `urgent` - 紧急

**响应 (201)**:
```json
{
    "id": 1,
    "order_no": "WX17166432001234",
    "status": "pending_review",
    "message": "报修申请已提交，请等待审核"
}
```

**错误响应 (400)**:
```json
{
    "description": ["此字段不能为空"],
    "images": ["图片大小不能超过5MB"]
}
```

**错误响应 (403)**:
```json
{
    "error": "您当前有多个工单正在处理中，暂不能提交新报修"
}
```

---

### 2.3 获取工单详情

```
GET /api/repairs/{id}/
```

**响应 (200)**:
```json
{
    "id": 1,
    "order_no": "WX17166432001234",
    "student": {
        "id": 1,
        "name": "张三",
        "phone": "13800138000"
    },
    "maintainer": {
        "id": 3,
        "name": "王五",
        "phone": "13700137000"
    },
    "room": {
        "id": 1,
        "building_name": "1号楼",
        "room_no": "101",
        "floor_no": 1
    },
    "category": "water_electric",
    "category_display": "水电",
    "description": "水龙头漏水，已经三天了",
    "urgency_level": "normal",
    "urgency_level_display": "普通",
    "status": "in_progress",
    "status_display": "处理中",
    "submit_time": "2026-05-25T10:00:00",
    "assign_time": "2026-05-25T14:00:00",
    "finish_time": null,
    "image_urls": ["/media/repair_images/1.jpg"],
    "logs": [
        {
            "id": 1,
            "operator": {"id": 1, "name": "张三"},
            "from_status": null,
            "to_status": "pending_review",
            "operation_type": "提交报修",
            "operation_time": "2026-05-25T10:00:00",
            "remark": null
        },
        {
            "id": 2,
            "operator": {"id": 2, "name": "李四"},
            "from_status": "pending_review",
            "to_status": "pending_dispatch",
            "operation_type": "审核通过",
            "operation_time": "2026-05-25T12:00:00",
            "remark": "已审核"
        },
        {
            "id": 3,
            "operator": {"id": 2, "name": "李四"},
            "from_status": "pending_dispatch",
            "to_status": "assigned",
            "operation_type": "派发任务",
            "operation_time": "2026-05-25T14:00:00",
            "remark": "派给王五"
        },
        {
            "id": 4,
            "operator": {"id": 3, "name": "王五"},
            "from_status": "assigned",
            "to_status": "in_progress",
            "operation_type": "接收任务",
            "operation_time": "2026-05-25T15:00:00",
            "remark": null
        }
    ]
}
```

---

### 2.4 撤销工单

```
POST /api/repairs/{id}/cancel/
```

**权限**: 仅学生，且工单状态为"待审核"

**响应 (200)**:
```json
{
    "message": "报修申请已撤销"
}
```

**错误响应 (400)**:
```json
{
    "error": "该工单已被审核，无法撤销"
}
```

---

## 三、派单接口 (dispatch)

### 3.1 获取待审核列表

```
GET /api/dispatch/pending-review/
```

**权限**: 仅管理员

**响应 (200)**:
```json
{
    "count": 5,
    "results": [
        {
            "id": 1,
            "order_no": "WX17166432001234",
            "student": {"id": 1, "name": "张三"},
            "room": {"building_name": "1号楼", "room_no": "101"},
            "category": "water_electric",
            "category_display": "水电",
            "description": "水龙头漏水",
            "urgency_level": "normal",
            "submit_time": "2026-05-25T10:00:00",
            "image_urls": ["/media/repair_images/1.jpg"]
        }
    ]
}
```

---

### 3.2 审核通过

```
POST /api/dispatch/{id}/approve/
```

**权限**: 仅管理员

**响应 (200)**:
```json
{
    "message": "审核通过，工单已进入派单队列",
    "status": "pending_dispatch"
}
```

**错误响应 (400)**:
```json
{
    "error": "该工单状态不允许此操作"
}
```

---

### 3.3 审核驳回

```
POST /api/dispatch/{id}/reject/
```

**权限**: 仅管理员

**请求**:
```json
{
    "reason": "信息描述不清，请补充详细信息"
}
```

**响应 (200)**:
```json
{
    "message": "已驳回",
    "status": "rejected"
}
```

---

### 3.4 获取待派单列表

```
GET /api/dispatch/pending-dispatch/
```

**权限**: 仅管理员

**响应 (200)**: 同 3.1 格式

---

### 3.5 派发任务

```
POST /api/dispatch/{id}/assign/
```

**权限**: 仅管理员

**请求**:
```json
{
    "maintainer_id": 3
}
```

**响应 (200)**:
```json
{
    "message": "派发成功",
    "status": "assigned"
}
```

**错误响应 (400)**:
```json
{
    "error": "该维修人员今日任务已饱和，请重新选择"
}
```

---

### 3.6 获取维修人员列表

```
GET /api/dispatch/maintainers/
```

**权限**: 仅管理员

**响应 (200)**:
```json
[
    {
        "id": 3,
        "name": "王五",
        "student_or_staff_no": "W001",
        "phone": "13700137000",
        "today_task_count": 2,
        "status": "在岗"
    },
    {
        "id": 4,
        "name": "赵六",
        "student_or_staff_no": "W002",
        "phone": "13600136000",
        "today_task_count": 5,
        "status": "在岗"
    }
]
```

---

## 四、维修接口 (maintenance)

### 4.1 获取我的任务列表

```
GET /api/maintenance/tasks/
```

**权限**: 仅维修人员

**查询参数**:
- `status`: 按状态筛选 (可选: assigned, in_progress, pending_confirm)

**响应 (200)**:
```json
{
    "count": 3,
    "results": [
        {
            "id": 1,
            "order_no": "WX17166432001234",
            "student": {"id": 1, "name": "张三", "phone": "13800138000"},
            "room": {"building_name": "1号楼", "room_no": "101"},
            "category": "water_electric",
            "category_display": "水电",
            "description": "水龙头漏水",
            "urgency_level": "normal",
            "status": "assigned",
            "status_display": "已派单",
            "assign_time": "2026-05-25T14:00:00"
        }
    ]
}
```

---

### 4.2 接收任务

```
POST /api/maintenance/{id}/accept/
```

**权限**: 仅维修人员，且工单状态为"已派单"

**响应 (200)**:
```json
{
    "message": "已接单",
    "status": "in_progress"
}
```

**错误响应 (400)**:
```json
{
    "error": "无法处理，申请转单"
}
```

---

### 4.3 完成维修

```
POST /api/maintenance/{id}/complete/
```

**权限**: 仅维修人员，且工单状态为"处理中"

**请求**:
```json
{
    "result": "已更换水龙头，修复漏水问题",
    "materials": "水龙头1个"
}
```

**响应 (200)**:
```json
{
    "message": "维修完成，等待学生确认",
    "status": "pending_confirm"
}
```

---

### 4.4 学生确认完成

```
POST /api/maintenance/{id}/confirm/
```

**权限**: 仅学生，且工单状态为"已完成待确认"

**请求 (可选)**:
```json
{
    "confirmed": true
}
```

**响应 - 确认完成 (200)**:
```json
{
    "message": "已确认完成",
    "status": "completed"
}
```

**响应 - 申请返修 (200)**:
```json
{
    "message": "已申请返修",
    "status": "in_progress"
}
```

**请求 - 申请返修**:
```json
{
    "confirmed": false,
    "reason": "漏水问题未解决"
}
```

---

## 五、评价投诉接口 (feedback)

### 5.1 提交评价

```
POST /api/feedback/evaluate/{work_order_id}/
```

**权限**: 仅学生，且工单状态为"已完成"且未评价

**请求**:
```json
{
    "speed_score": 5,
    "attitude_score": 4,
    "quality_score": 5,
    "content": "维修很及时，态度很好"  // 可选
}
```

**响应 (201)**:
```json
{
    "message": "感谢您的评价",
    "evaluation_id": 1
}
```

**错误响应 (400)**:
```json
{
    "speed_score": ["评分范围为1-5"],
    "content": ["内容包含不当词汇，请修改"]
}
```

---

### 5.2 提交投诉

```
POST /api/feedback/complaint/{work_order_id}/
```

**权限**: 仅学生，且工单状态为"已完成"或"已评价"

**请求**:
```json
{
    "type": "quality",  // quality-维修质量, attitude-服务态度, other-其他
    "content": "维修后还是漏水，问题没有解决"
}
```

**响应 (201)**:
```json
{
    "message": "投诉已提交，管理员将尽快处理",
    "complaint_id": 1
}
```

**错误响应 (400)**:
```json
{
    "error": "该工单已有投诉在处理中，请勿重复提交"
}
```

---

### 5.3 获取投诉列表 (管理员)

```
GET /api/feedback/complaints/
```

**权限**: 仅管理员

**查询参数**:
- `status`: pending, processing, resolved (可选)

**响应 (200)**:
```json
{
    "count": 2,
    "results": [
        {
            "id": 1,
            "work_order": {
                "id": 1,
                "order_no": "WX17166432001234"
            },
            "student": {"id": 1, "name": "张三"},
            "type": "quality",
            "type_display": "维修质量",
            "content": "维修后还是漏水",
            "status": "pending",
            "status_display": "待处理",
            "created_at": "2026-05-26T10:00:00",
            "process_result": null,
            "handled_at": null
        }
    ]
}
```

---

### 5.4 处理投诉

```
POST /api/feedback/complaints/{id}/process/
```

**权限**: 仅管理员

**请求**:
```json
{
    "result": "已安排维修人员重新上门维修",
    "status": "resolved"
}
```

**status 可选值**:
- `processing` - 处理中
- `resolved` - 已处理

**响应 (200)**:
```json
{
    "message": "投诉已处理",
    "status": "resolved"
}
```

---

## 六、统计接口 (dashboard)

### 6.1 获取统计数据

```
GET /api/dashboard/statistics/
```

**权限**: 仅管理员

**查询参数**:
- `start_date`: 开始日期 (可选，格式: 2026-05-01)
- `end_date`: 结束日期 (可选)
- `building`: 楼栋ID (可选)
- `category`: 报修类别 (可选)

**响应 (200)**:
```json
{
    "summary": {
        "total_orders": 150,
        "completed_orders": 120,
        "completion_rate": 80.0,
        "avg_response_hours": 3.5,
        "avg_completion_hours": 24.0,
        "urgent_orders": 15
    },
    "category_distribution": [
        {"category": "water_electric", "count": 60},
        {"category": "door_window", "count": 30},
        {"category": "network", "count": 25},
        {"category": "furniture", "count": 20},
        {"category": "other", "count": 15}
    ],
    "status_distribution": [
        {"status": "pending_review", "count": 5},
        {"status": "in_progress", "count": 10},
        {"status": "completed", "count": 120},
        {"status": "rejected", "count": 15}
    ],
    "daily_trend": [
        {"date": "2026-05-20", "count": 12},
        {"date": "2026-05-21", "count": 15},
        {"date": "2026-05-22", "count": 8}
    ],
    "maintainer_performance": [
        {
            "maintainer": "王五",
            "completed_count": 45,
            "avg_hours": 18.5,
            "avg_score": 4.5
        }
    ],
    "satisfaction_distribution": [
        {"score": 5, "count": 50},
        {"score": 4, "count": 40},
        {"score": 3, "count": 20},
        {"score": 2, "count": 8},
        {"score": 1, "count": 2}
    ]
}
```

---

### 6.2 导出报表

```
GET /api/dashboard/export/
```

**权限**: 仅管理员

**查询参数**: 同 6.1

**响应**: 返回 Excel 文件 (application/vnd.openxmlformats-officedocument.spreadsheetml.sheet)

---

## 七、状态说明

### 工单状态流转

```
pending_review (待审核)
    ↓ 审核通过
pending_dispatch (待派单)
    ↓ 派发任务
assigned (已派单)
    ↓ 接收任务
in_progress (处理中)
    ↓ 完成维修
pending_confirm (已完成待确认)
    ↓ 学生确认
completed (已完成)
    ↓ 提交评价
evaluated (已评价)
```

**特殊状态**:
- `rejected` (已驳回) - 审核不通过
- `cancelled` (已撤销) - 学生主动撤销

### 状态显示名称映射

```javascript
const STATUS_MAP = {
    'pending_review': '待审核',
    'pending_dispatch': '待派单',
    'assigned': '已派单',
    'in_progress': '处理中',
    'pending_confirm': '已完成待确认',
    'completed': '已完成',
    'evaluated': '已评价',
    'rejected': '已驳回',
    'cancelled': '已撤销'
};
```

---

## 八、错误码说明

| 状态码 | 含义 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未认证 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 500 | 服务器错误 |

---

## 九、前端需要准备的页面

| 页面 | 路由建议 | 对应接口 |
|------|---------|---------|
| 登录页 | `/login` | 1.1 |
| 学生-我的工单 | `/student/orders` | 2.1 |
| 学生-提交报修 | `/student/repairs/create` | 2.2, 1.5, 1.6 |
| 学生-工单详情 | `/student/orders/{id}` | 2.3 |
| 学生-评价 | `/student/evaluate/{id}` | 5.1 |
| 学生-投诉 | `/student/complaint/{id}` | 5.2 |
| 管理员-审核列表 | `/admin/pending-review` | 3.1 |
| 管理员-派单列表 | `/admin/pending-dispatch` | 3.4, 3.6 |
| 管理员-投诉列表 | `/admin/complaints` | 5.3 |
| 管理员-统计报表 | `/admin/dashboard` | 6.1 |
| 维修人员-我的任务 | `/maintainer/tasks` | 4.1 |
| 维修人员-任务详情 | `/maintainer/tasks/{id}` | 4.2, 4.3 |
