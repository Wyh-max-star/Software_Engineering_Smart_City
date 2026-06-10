# ICity Traffic & Crowd Design

## Goal

在 `iCity Start` 已生成基础城市的前提下，新增一个独立的 Blender 插件子模块，用于生成交通与人群动态演示。该模块只读取城市边界信息，不依赖生态湖泊/河流布局，不与生态扩展共用生成入口。

## Scope

本次只覆盖课程作业中“交通和人群模拟”要求对应的最小可演示范围：

- 向场景中加入动态车辆与动态人群
- 轨迹满足基础社会规则
- 提供独立面板、独立参数、独立生成与清理
- 能基于 `iCity Start` 的城市结果稳定运行

明确不在本次范围内：

- 真实道路网络级别的交通规划
- 红绿灯、路口让行、碰撞检测
- 与生态模块共用同一生成入口
- 依赖 iCity 内部复杂节点细节去解析原始道路骨架

## User-Facing Design

右侧 `N` 面板新增 `ICity Traffic & Crowd`。

用户工作流：

1. 在原始 `iCity` 面板点击 `Start`
2. 展开 `ICity Traffic & Crowd`
3. 设置车辆、人群、动画参数
4. 点击 `Generate / Update`
5. 预览动画
6. 点击 `Clear`

## Architecture

### Module Boundary

新增独立模块 `iCity/smart_city/traffic_extension.py`，负责：

- 交通与人群设置定义
- 交通与人群面板
- 交通与人群生成/清理 Operator
- 独立集合管理
- 交通与步行布局计算
- 车辆/人群代理模型与动画生成

保留现有 `ecology_extension.py` 与 `ecology_traffic.py`，但不作为本次功能主入口。

### Dependency Rule

该模块只依赖以下现有能力：

- `asset_extension.py` / `ecology_common.py` 中已经稳定的城市边界获取思路
- Blender 基础数据结构与动画能力
- `iCity Start` 生成出来的城市集合

该模块不依赖：

- 湖泊中心
- 河流走向
- 生态布局结果
- 生态集合名称

## Scene Structure

生成后在场景中创建以下集合：

- `ICity Traffic Crowd`
- `ICity Traffic Vehicles`
- `ICity Traffic Pedestrians`
- `ICity Traffic Paths`

清理操作只删除这几个集合及其子对象。

## Layout Strategy

### City Anchor

通过城市包围盒得到：

- `city_center`
- `city_radius`
- `ground_z`

### Traffic Band

在城市外缘生成一条椭圆环形交通带：

- 中心与城市中心保持一致，避免视觉漂移
- 半径在 `city_radius + outer_offset` 基础上计算
- 交通带整体位于城市外侧，不穿入建筑体量内部

### Pedestrian Band

在人行交通带外侧再生成步行带：

- 与车辆带平行
- 与车辆保持明确间距
- 形成“车行在内、步行在外”的演示关系

### Social Rule Approximation

课程作业中的“符合社会规则”按保守可演示标准解释为：

- 车辆全部沿车道单向运动
- Bus 作为更大体量车辆，占用外侧车道
- Taxi 与 Car 共用主车道，通过颜色与尺度区分
- Pedestrian 不与车辆共道
- 两条步行流使用错位相位，避免完全重叠
- 所有动态对象默认保持均匀间距分布

## Asset Design

### Vehicles

使用程序化低模代理模型，至少包含：

- Car
- Taxi
- Bus

区分方式：

- 尺寸
- 材质颜色
- 所属车道

### Pedestrians

继续采用轻量代理模型，保证：

- 数量可配置
- 性能稳定
- 动画效果清晰可见

## Error Handling

若未检测到 `ICity` 主集合或城市边界，直接报错提示用户先执行 `iCity Start`。

若动画结束帧小于等于开始帧，拒绝生成。

若用户重复点击 `Generate / Update`，先清理本模块旧结果，再重新生成。

## Testing Strategy

测试分为两层：

### Unit Tests

新增独立 `unittest`，验证：

- 布局计算结果位于城市外侧
- 步行带在车辆带外侧
- 车辆与人群的集合边界独立
- 生成入口不会调用生态模块布局
- 车辆类型配置被正确展开

### Blender Manual Validation

手动验证：

1. `iCity Start` 后能看到新面板
2. 点击 `Generate / Update` 后生成独立交通集合
3. 车辆和人群在视图中可见
4. 时间轴播放时车辆和人群会移动
5. `Clear` 只清理交通模块内容

## Acceptance Criteria

以下条件同时满足即视为本阶段完成：

- 能在 `iCity Start` 之后独立生成交通与人群
- 不需要打开生态模块也能使用
- 至少包含 `car / taxi / bus / pedestrian`
- 动态对象位于城市外圈合理区域
- 清理不影响资产扩展与生态模块
- 具备自动化测试与 Blender 手动测试说明
