// 每个模板各一套 iCity 真实资产缩略图（树/路/椅），与插件实际效果一致
import road0 from './assets/templates/road-0.png'
import tree0 from './assets/templates/tree-0.png'
import bench0 from './assets/templates/bench-0.png'
import road1 from './assets/templates/road-1.png'
import tree1 from './assets/templates/tree-1.png'
import bench1 from './assets/templates/bench-1.png'
import road2 from './assets/templates/road-2.png'
import tree2 from './assets/templates/tree-2.png'
import bench2 from './assets/templates/bench-2.png'

export type TemplateId = '0' | '1' | '2'

export type CityTemplate = {
  id: TemplateId
  name: string
  sceneType: string
  description: string
  tree_type: number
  road_texture: number
  bench_type: number
  pluginValues: {
    tree: string
    road: string
    bench: string
  }
  // 整城场景维度概要（与插件 templates.json 的 scene 对应）
  scene: {
    traffic: string
    pedestrian: string
    ecology: string
  }
  preview: {
    road: string
    tree: string
    bench: string
  }
  tags: string[]
  fit: string
}

export const templates: CityTemplate[] = [
  {
    id: '0',
    name: '公园城市模板',
    sceneType: '生态慢行街区',
    description:
      '绿色行道树 + 干净路面 + 木质座椅，配混凝土大道、花箱绿植与稀疏车流人流，旁边一片湖光山色生态地块。',
    tree_type: 1,
    road_texture: 5,
    bench_type: 1,
    pluginValues: {
      tree: 'Tree1_Tree_ICity_Default',
      road: 'ICity_Road 4 clean_Default',
      bench: 'Bench1_Bench_ICity_Default',
    },
    scene: {
      traffic: '4 辆',
      pedestrian: '12 人',
      ecology: '湖+山',
    },
    preview: {
      road: road0,
      tree: tree0,
      bench: bench0,
    },
    tags: ['绿化慢行', '稀疏车流', '湖光山色'],
    fit: '清新生态绿城，适合作为默认整城模板。',
  },
  {
    id: '1',
    name: '金秋商业街模板',
    sceneType: '暖色商业主街',
    description:
      '金黄行道树 + 做旧沥青路 + 现代黑金属椅，带车道线主干道与公交站，车水马龙、人潮汹涌的繁华商业街，无山水。',
    tree_type: 7,
    road_texture: 7,
    bench_type: 11,
    pluginValues: {
      tree: 'Tree7_Tree_ICity_Default',
      road: 'ICity_Road 8 dirty_Default',
      bench: 'Bench11_Bench_ICity_Default',
    },
    scene: {
      traffic: '26 辆',
      pedestrian: '48 人',
      ecology: '无',
    },
    preview: {
      road: road1,
      tree: tree1,
      bench: bench1,
    },
    tags: ['车水马龙', '人潮汹涌', '金秋商业'],
    fit: '暖色繁华老街，最能体现交通/人群密集效果。',
  },
  {
    id: '2',
    name: '滨海社区模板',
    sceneType: '南国滨海社区',
    description:
      '棕榈行道树 + 干净路面 + 木椅，暖色木栈道与长椅，中等车流人流，旁边蜿蜒河谷（河流 + 两岸青山）。',
    tree_type: 14,
    road_texture: 1,
    bench_type: 3,
    pluginValues: {
      tree: 'Tree14_Tree_ICity_Default',
      road: 'ICity_Road 1 clean_Default',
      bench: 'Bench3_Bench_ICity_Default',
    },
    scene: {
      traffic: '8 辆',
      pedestrian: '20 人',
      ecology: '河谷',
    },
    preview: {
      road: road2,
      tree: tree2,
      bench: bench2,
    },
    tags: ['滨海度假', '木栈道', '河谷生态'],
    fit: '南国度假滨海风，与前两者一眼可分。',
  },
]

export const roles = [
  {
    id: 'modeler',
    name: '场景建模师',
    description: '选择模板、进入 Blender 插件并完成城市生成。',
  },
  {
    id: 'admin',
    name: '系统管理员',
    description: '管理用户权限、插件审核和系统运行状态。',
  },
  {
    id: 'analyst',
    name: '行业分析师',
    description: '查看模板指标、验收插件功能并输出评审意见。',
  },
] as const

export type RoleId = (typeof roles)[number]['id']

export function getTemplate(id?: string | null) {
  return templates.find((template) => template.id === id) ?? templates[0]
}
