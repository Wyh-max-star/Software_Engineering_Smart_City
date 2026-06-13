import bpy
import bmesh

# 确保 'ICity Base' 对象存在
obj_name = "ICity Base"
if obj_name not in bpy.data.objects:
    raise ValueError(f"Object '{obj_name}' not found in the scene!")

# 获取 'ICity Base' 对象
obj = bpy.data.objects[obj_name]

# 切换到对象模式并确保对象是活动对象
bpy.ops.object.mode_set(mode='OBJECT')
bpy.context.view_layer.objects.active = obj

# 切换到编辑模式
bpy.ops.object.mode_set(mode='EDIT')

# 使用 BMesh 操作网格数据
bm = bmesh.from_edit_mesh(obj.data)

vert=[(-422.31930542239945, 265.1601760939217, 0), (-218.25371217222988, 483.3783766383774, 0), (428.08830698168765, 500.0, 0), (443.94805659926783, 499.88573205989144, 0), (496.89227605211875, 485.14819767213885, 0), (500.0, 395.1173222000758, 0), (476.89867881524617, 347.21462938580544, 0), (423.34168277552203, 299.69268987307885, 0), (396.4785325111968, 255.52724541448129, 0), (374.81239520839006, -65.79851122606925, 0), (320.77601967813746, -194.77594516312178, 0), (327.93360553975685, -231.92782163855765, 0), (414.48025251456386, -313.84958865389024, 0), (436.93859845479255, -350.9503290459661, 0), (440.364088011194, -399.0440236869738, 0), (413.3044050904555, -450.46682639478604, 0), (370.2567916975263, -500.0, 0), (350.53678399480816, -490.50214074131304, 0), (317.42043522949893, -470.5841123785485, 0), (290.72161366941646, -455.87407406780943, 0), (253.5496518059963, -433.9909853363483, 0), (149.0781675077444, -365.0046218505547, 0), (-85.14103679114794, -173.4546070235084, 0), (-500.0, 183.78101093887074, 0), (-422.31930542239945, 265.1601760939217, 0)]

# 添加顶点并创建边
vertices = [bm.verts.new(v) for v in vert]  # 添加所有顶点
for i in range(10):
    bm.edges.new((vertices[i], vertices[i + 1]))  # 按顺序连接每两个相邻的顶点
# for i in range(len(vertices) - 1):
#     bm.edges.new((vertices[i], vertices[i + 1]))  # 按顺序连接每两个相邻的顶点
# bm.edges.new((vertices[len(vertices)-1], vertices[0]))
# # 添加两个孤立的点
# v1 = bm.verts.new((0, 0, 0))  # 第一个点的坐标
# v2 = bm.verts.new((50, 0, 0))  # 第二个点的坐标
# v3 = bm.verts.new((-50, 0, 0))  # 第二个点的坐标
# v4 = bm.verts.new((0, 50, 0))  # 第二个点的坐标
# v5 = bm.verts.new((0, -50, 0))  # 第二个点的坐标
#
# # 将两个点连接成一条边
# bm.edges.new((v1, v2))
# bm.edges.new((v1, v3))
# bm.edges.new((v1, v4))
# bm.edges.new((v1, v5))

# 更新 BMesh 数据
bmesh.update_edit_mesh(obj.data)

# 切换回对象模式
bpy.ops.object.mode_set(mode='OBJECT')

print("Two vertices added and connected to form an edge in 'ICity Base' successfully!")