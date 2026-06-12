import {
  ArrowRight,
  BadgeCheck,
  BarChart3,
  BookOpenCheck,
  Boxes,
  Building2,
  CheckCircle2,
  ChevronLeft,
  ChevronRight,
  ClipboardCheck,
  ClipboardList,
  DoorOpen,
  ExternalLink,
  LayoutDashboard,
  LogOut,
  Menu,
  MonitorPlay,
  Plus,
  PlugZap,
  Save,
  Search,
  Send,
  ShieldCheck,
  Store,
  Trash2,
  Trees,
  UserRoundCog,
  XCircle,
} from 'lucide-react'
import { useEffect, useMemo, useState, type FormEvent, type ReactNode } from 'react'
import { Link, Navigate, Route, Routes, useLocation, useNavigate, useParams } from 'react-router-dom'
import './App.css'
import { getTemplate, roles, templates, type CityTemplate, type RoleId } from './templates'

const selectedTemplateKey = 'icity-selected-template'
const roleKey = 'icity-current-role'
const usersKey = 'icity-local-users'
const currentUserKey = 'icity-current-user'
const sessionExpiresAtKey = 'icity-session-expires-at'
const sidebarCollapsedKey = 'icity-sidebar-collapsed'
const pageHistoryKey = 'icity-page-history'
const pluginReviewsKey = 'icity-plugin-review-items'
const acceptanceStandardsKey = 'icity-acceptance-standards'
const industryMemoKey = 'icity-industry-demand-memo'
const adminLogsKey = 'icity-admin-operation-logs'
const rememberedLoginMethodKey = 'icity-remembered-login-method'
const rememberedEmailLoginKey = 'icity-remembered-email-login'
const rememberedUsernameLoginKey = 'icity-remembered-username-login'
const sessionDurationMs = 12 * 60 * 60 * 1000

type LocalUser = {
  id: string
  email: string
  username: string
  password: string
  role: RoleId
  createdAt: string
}

type LoginMethod = 'email' | 'username'
type RememberedLogin = {
  rememberIdentifier: boolean
  identifier: string
  rememberPassword: boolean
  password: string
}
type AnalystReviewStatus = 'pending' | 'passed' | 'changes_requested'
type AdminReviewStatus = 'waiting_analyst' | 'pending' | 'listed' | 'rejected'
type PluginReviewAction = (id: string, updater: (item: PluginReviewItem) => PluginReviewItem) => void
type AdminLogAction = 'role_change' | 'delete_user' | 'plugin_listed' | 'plugin_rejected'
type AdminLogInput = {
  action: AdminLogAction
  target: string
  detail: string
}
type PermissionKey =
  | 'viewTemplates'
  | 'applyTemplate'
  | 'enterBlender'
  | 'managePermissions'
  | 'reviewPlugin'
  | 'recordAcceptance'

type PluginReviewItem = {
  id: string
  name: string
  version: string
  submitter: string
  submittedAt: string
  summary: string
  capabilities: string[]
  analystStatus: AnalystReviewStatus
  analystNotes: string
  analystUpdatedAt?: string
  adminStatus: AdminReviewStatus
  adminNotes: string
  adminUpdatedAt?: string
}

type AcceptanceStandard = {
  id: string
  category: string
  title: string
  description: string
}

type IndustryDemandMemo = {
  title: string
  content: string
  updatedAt?: string
}

type AdminOperationLog = {
  id: string
  operator: string
  action: AdminLogAction
  target: string
  detail: string
  createdAt: string
}

const defaultPluginReviews: PluginReviewItem[] = [
  {
    id: 'icity-template-100',
    name: 'ICity Template Generator',
    version: '1.0.0',
    submitter: 'iCity 插件维护组',
    submittedAt: '2026-06-04',
    summary: '提交三套整城模板、模板参数映射和 Blender 侧一键应用入口。',
    capabilities: ['模板 0/1/2', '树木/道路/座椅映射', 'Blender 应用模板'],
    analystStatus: 'pending',
    analystNotes: '',
    adminStatus: 'waiting_analyst',
    adminNotes: '',
  },
  {
    id: 'icity-traffic-crowd-110',
    name: 'ICity Traffic & Crowd Pack',
    version: '1.1.0',
    submitter: '交通人群扩展小组',
    submittedAt: '2026-06-05',
    summary: '新增车辆与行人生成配置，支持模板中车流、人流档位同步。',
    capabilities: ['交通模拟', '行人动画', '模板场景档位'],
    analystStatus: 'passed',
    analystNotes: '已覆盖高/中/低车流和人流档位，能支撑商业街与社区模板演示。',
    analystUpdatedAt: '2026-06-06',
    adminStatus: 'pending',
    adminNotes: '',
  },
  {
    id: 'icity-ecology-100',
    name: 'ICity Ecology Assets',
    version: '1.0.0',
    submitter: '生态扩展小组',
    submittedAt: '2026-06-03',
    summary: '提供湖+山、纯山、河谷生态地块，用于丰富智慧城市周边环境。',
    capabilities: ['生态地块', '湖泊/山体/河谷', '模板生态参数'],
    analystStatus: 'passed',
    analystNotes: '生态模式与三个模板的场景目标一致，建议作为稳定能力上架。',
    analystUpdatedAt: '2026-06-04',
    adminStatus: 'listed',
    adminNotes: '已完成上架，允许建模师在 Blender 插件中使用。',
    adminUpdatedAt: '2026-06-05',
  },
]

const defaultAcceptanceStandards: AcceptanceStandard[] = [
  {
    id: 'std-role-auth',
    category: '权限',
    title: '角色登录与访问隔离',
    description: '系统需支持管理员、行业分析师、场景建模师三类用户，并按角色限制页面入口和操作按钮。',
  },
  {
    id: 'std-plugin-entry',
    category: '插件入口',
    title: '主系统到 Blender 的演示链路',
    description: '建模师应能从主系统带着模板 ID 和资产参数进入 Blender 插件模拟入口。',
  },
  {
    id: 'std-template-fields',
    category: '模板',
    title: '模板参数与插件字段一致',
    description: '模板需明确 tree_type、road_texture、bench_type 及对应 iCity 资产名。',
  },
  {
    id: 'std-smart-city-scope',
    category: '行业需求',
    title: '覆盖智慧城市核心场景',
    description: '提交物应覆盖交通、人群、生态或城市资产至少一个智慧城市场景维度。',
  },
]

const defaultIndustryMemo: IndustryDemandMemo = {
  title: '智慧城市行业需求调研备忘录',
  content: [
    '# 智慧城市行业需求调研',
    '',
    '## 关注方向',
    '- 多角色协同：管理员、分析师、建模师需要看到不同的工作界面',
    '- 城市生成效率：模板应减少重复配置成本',
    '- 演示可信度：前端参数需要能对应到 Blender 插件资产',
    '',
    '## 待确认',
    '- 是否需要更多行业模板，例如交通枢纽、政务中心、校园社区',
    '- 是否需要把自然语言编辑作为后续插件能力重点展示',
  ].join('\n'),
}

const naturalLanguageDemos = [
  {
    id: 'busy-lake',
    command: '车水马龙、有山有湖、街上很多人，把树换成金黄的',
    engine: 'DeepSeek 优先 / 规则兜底',
    result: [
      ['tree', 'Tree7_Tree_ICity_Default'],
      ['traffic', 'high'],
      ['pedestrian', 'high'],
      ['ecology_mode', 'LAKE_RING'],
    ],
    effects: ['金黄行道树', '高密度车流', '高密度人群', '湖光山色生态地块'],
    operators: ['icity.apply_nl_command', 'sna.road_apply_5c3ab', 'icity.generate_traffic', 'icity.generate_pedestrians', 'icity.add_ecology_plot'],
  },
  {
    id: 'coast-boardwalk',
    command: '海边木栈道，棕榈树，中等车流，路边放木质长椅',
    engine: 'DeepSeek 优先 / 规则兜底',
    result: [
      ['tree', 'Tree14_Tree_ICity_Default'],
      ['bench', 'Bench1_Bench_ICity_Default'],
      ['surface', 'BOARDWALK_WARM'],
      ['traffic', 'medium'],
    ],
    effects: ['棕榈行道树', '暖色木栈道', '中等车流', '木质长椅'],
    operators: ['icity.apply_nl_command', 'sna.road_apply_5c3ab', 'icity.apply_asset_surface', 'icity.generate_traffic'],
  },
  {
    id: 'quiet-clear',
    command: '去掉车辆和人群，清空山湖，改成安静干净的公园街区',
    engine: '规则解析可离线执行',
    result: [
      ['road_material', 'ICity_Road 4 clean_Default'],
      ['traffic', 'none'],
      ['pedestrian', 'none'],
      ['ecology_mode', 'NONE'],
    ],
    effects: ['干净路面', '清空车流', '清空人群', '移除生态地块'],
    operators: ['icity.apply_nl_command', 'sna.road_apply_5c3ab', 'icity.clear_traffic', 'icity.clear_pedestrians', 'icity.clear_ecology'],
  },
]

const layoutSamples = [
  {
    id: 'rectangle',
    name: '矩形街区',
    summary: '4 nodes / 4 edges / 1 face',
    nodes: [
      { id: 'n0', x: 0, y: 0 },
      { id: 'n1', x: 100, y: 0 },
      { id: 'n2', x: 100, y: 100 },
      { id: 'n3', x: 0, y: 100 },
    ],
    edges: [
      { id: 'e0', start: 'n0', end: 'n1' },
      { id: 'e1', start: 'n1', end: 'n2' },
      { id: 'e2', start: 'n2', end: 'n3' },
      { id: 'e3', start: 'n3', end: 'n0' },
    ],
    stats: ['Validate Draft: 通过', '闭合道路推断 1 个城市块', 'Preview 不修改 ICity Base'],
  },
  {
    id: 'cross',
    name: '十字路口',
    summary: '5 nodes / 4 edges / 0 face',
    nodes: [
      { id: 'n0', x: 50, y: 0 },
      { id: 'n1', x: 50, y: 100 },
      { id: 'n2', x: 0, y: 50 },
      { id: 'n3', x: 100, y: 50 },
      { id: 'n4', x: 50, y: 50 },
    ],
    edges: [
      { id: 'e0', start: 'n0', end: 'n4' },
      { id: 'e1', start: 'n4', end: 'n1' },
      { id: 'e2', start: 'n2', end: 'n4' },
      { id: 'e3', start: 'n4', end: 'n3' },
    ],
    stats: ['交叉道路拆分为共享节点', '重复边与过短边会被清理', '适合演示 Normalize Draft'],
  },
  {
    id: 'grid',
    name: '田字路网',
    summary: '9 nodes / 12 edges / 4+ faces',
    nodes: [
      { id: 'n0', x: 0, y: 0 },
      { id: 'n1', x: 50, y: 0 },
      { id: 'n2', x: 100, y: 0 },
      { id: 'n3', x: 0, y: 50 },
      { id: 'n4', x: 50, y: 50 },
      { id: 'n5', x: 100, y: 50 },
      { id: 'n6', x: 0, y: 100 },
      { id: 'n7', x: 50, y: 100 },
      { id: 'n8', x: 100, y: 100 },
    ],
    edges: [
      { id: 'e0', start: 'n0', end: 'n1' },
      { id: 'e1', start: 'n1', end: 'n2' },
      { id: 'e2', start: 'n3', end: 'n4' },
      { id: 'e3', start: 'n4', end: 'n5' },
      { id: 'e4', start: 'n6', end: 'n7' },
      { id: 'e5', start: 'n7', end: 'n8' },
      { id: 'e6', start: 'n0', end: 'n3' },
      { id: 'e7', start: 'n3', end: 'n6' },
      { id: 'e8', start: 'n1', end: 'n4' },
      { id: 'e9', start: 'n4', end: 'n7' },
      { id: 'e10', start: 'n2', end: 'n5' },
      { id: 'e11', start: 'n5', end: 'n8' },
    ],
    stats: ['黑白草图可识别为点线 Draft', 'Apply 后替换真实 ICity Base', '闭合道路生成 Procedural 城市块'],
  },
]

const permissionRules: { key: PermissionKey; title: string; description: string }[] = [
  {
    key: 'viewTemplates',
    title: '查看模板',
    description: '进入模板商城和模板详情页',
  },
  {
    key: 'applyTemplate',
    title: '应用模板',
    description: '把模板写入当前插件输入',
  },
  {
    key: 'enterBlender',
    title: '进入 Blender',
    description: '访问插件入口并模拟跳转',
  },
  {
    key: 'managePermissions',
    title: '权限管理',
    description: '进入管理员权限管理页',
  },
  {
    key: 'reviewPlugin',
    title: '插件审核',
    description: '查看 Blender 入口审核状态',
  },
  {
    key: 'recordAcceptance',
    title: '验收记录',
    description: '查看模板指标和验收说明',
  },
]

const rolePermissions: Record<RoleId, Record<PermissionKey, boolean>> = {
  modeler: {
    viewTemplates: true,
    applyTemplate: true,
    enterBlender: true,
    managePermissions: false,
    reviewPlugin: false,
    recordAcceptance: false,
  },
  admin: {
    viewTemplates: true,
    applyTemplate: false,
    enterBlender: false,
    managePermissions: true,
    reviewPlugin: true,
    recordAcceptance: false,
  },
  analyst: {
    viewTemplates: true,
    applyTemplate: false,
    enterBlender: false,
    managePermissions: false,
    reviewPlugin: false,
    recordAcceptance: true,
  },
}

type PageHistoryState = {
  entries: string[]
  index: number
}

function readPageHistory(): PageHistoryState {
  try {
    const rawHistory = sessionStorage.getItem(pageHistoryKey)
    if (!rawHistory) return { entries: [], index: -1 }
    const parsedHistory = JSON.parse(rawHistory) as PageHistoryState
    if (!Array.isArray(parsedHistory.entries)) return { entries: [], index: -1 }

    const entries = parsedHistory.entries.filter((entry) => typeof entry === 'string')
    const parsedIndex = Number(parsedHistory.index)
    const safeIndex = Number.isFinite(parsedIndex) ? parsedIndex : -1
    const index = Math.min(Math.max(safeIndex, -1), entries.length - 1)
    return { entries, index }
  } catch {
    return { entries: [], index: -1 }
  }
}

function writePageHistory(history: PageHistoryState) {
  sessionStorage.setItem(pageHistoryKey, JSON.stringify(history))
}

function isTrackedPage(pathname: string) {
  return pathname !== '/login' && pathname !== '/register'
}

function normalizeIdentifier(value: string) {
  return value.trim().toLowerCase()
}

function rememberStorageKey(method: LoginMethod) {
  return method === 'email' ? rememberedEmailLoginKey : rememberedUsernameLoginKey
}

function emptyRememberedLogin(): RememberedLogin {
  return {
    rememberIdentifier: false,
    identifier: '',
    rememberPassword: false,
    password: '',
  }
}

function readRememberedLogin(method: LoginMethod): RememberedLogin {
  try {
    const rawRemembered = localStorage.getItem(rememberStorageKey(method))
    if (!rawRemembered) return emptyRememberedLogin()
    const parsedRemembered = JSON.parse(rawRemembered) as Partial<RememberedLogin>
    const rememberIdentifier = parsedRemembered.rememberIdentifier === true
    const rememberPassword = parsedRemembered.rememberPassword === true

    return {
      rememberIdentifier,
      identifier: rememberIdentifier && typeof parsedRemembered.identifier === 'string' ? parsedRemembered.identifier : '',
      rememberPassword,
      password: rememberPassword && typeof parsedRemembered.password === 'string' ? parsedRemembered.password : '',
    }
  } catch {
    return emptyRememberedLogin()
  }
}

function writeRememberedLogin(method: LoginMethod, remembered: RememberedLogin) {
  localStorage.setItem(rememberStorageKey(method), JSON.stringify(remembered))
  localStorage.setItem(rememberedLoginMethodKey, method)
}

function readRememberedLoginMethod(): LoginMethod {
  const storedMethod = localStorage.getItem(rememberedLoginMethodKey)
  return storedMethod === 'username' ? 'username' : 'email'
}

function readUsers(): LocalUser[] {
  try {
    const rawUsers = localStorage.getItem(usersKey)
    if (!rawUsers) return []
    const parsedUsers = JSON.parse(rawUsers)
    return Array.isArray(parsedUsers) ? parsedUsers : []
  } catch {
    return []
  }
}

function writeUsers(users: LocalUser[]) {
  localStorage.setItem(usersKey, JSON.stringify(users))
}

function readPluginReviews(): PluginReviewItem[] {
  try {
    const rawReviews = localStorage.getItem(pluginReviewsKey)
    if (!rawReviews) return defaultPluginReviews
    const parsedReviews = JSON.parse(rawReviews)
    return Array.isArray(parsedReviews) ? parsedReviews : defaultPluginReviews
  } catch {
    return defaultPluginReviews
  }
}

function writePluginReviews(reviews: PluginReviewItem[]) {
  localStorage.setItem(pluginReviewsKey, JSON.stringify(reviews))
}

function readAcceptanceStandards(): AcceptanceStandard[] {
  try {
    const rawStandards = localStorage.getItem(acceptanceStandardsKey)
    if (!rawStandards) return defaultAcceptanceStandards
    const parsedStandards = JSON.parse(rawStandards)
    return Array.isArray(parsedStandards) ? parsedStandards : defaultAcceptanceStandards
  } catch {
    return defaultAcceptanceStandards
  }
}

function writeAcceptanceStandards(standards: AcceptanceStandard[]) {
  localStorage.setItem(acceptanceStandardsKey, JSON.stringify(standards))
}

function readIndustryMemo(): IndustryDemandMemo {
  try {
    const rawMemo = localStorage.getItem(industryMemoKey)
    if (!rawMemo) return defaultIndustryMemo
    const parsedMemo = JSON.parse(rawMemo) as IndustryDemandMemo
    return {
      title: typeof parsedMemo.title === 'string' ? parsedMemo.title : defaultIndustryMemo.title,
      content: typeof parsedMemo.content === 'string' ? parsedMemo.content : defaultIndustryMemo.content,
      updatedAt: typeof parsedMemo.updatedAt === 'string' ? parsedMemo.updatedAt : undefined,
    }
  } catch {
    return defaultIndustryMemo
  }
}

function writeIndustryMemo(memo: IndustryDemandMemo) {
  localStorage.setItem(industryMemoKey, JSON.stringify(memo))
}

function readAdminLogs(): AdminOperationLog[] {
  try {
    const rawLogs = localStorage.getItem(adminLogsKey)
    if (!rawLogs) return []
    const parsedLogs = JSON.parse(rawLogs)
    return Array.isArray(parsedLogs) ? parsedLogs : []
  } catch {
    return []
  }
}

function writeAdminLogs(logs: AdminOperationLog[]) {
  localStorage.setItem(adminLogsKey, JSON.stringify(logs))
}

function createSessionExpiry() {
  return Date.now() + sessionDurationMs
}

function readSessionExpiry() {
  const rawExpiry = localStorage.getItem(sessionExpiresAtKey)
  const expiry = rawExpiry ? Number(rawExpiry) : NaN
  return Number.isFinite(expiry) ? expiry : null
}

function clearStoredSession() {
  localStorage.removeItem(currentUserKey)
  localStorage.removeItem(sessionExpiresAtKey)
  sessionStorage.removeItem(pageHistoryKey)
}

function readCurrentUser() {
  try {
    const rawUser = localStorage.getItem(currentUserKey)
    if (!rawUser) return null
    const expiresAt = readSessionExpiry()
    if (expiresAt && expiresAt <= Date.now()) {
      clearStoredSession()
      return null
    }
    if (!expiresAt) {
      localStorage.setItem(sessionExpiresAtKey, String(createSessionExpiry()))
    }
    const parsedUser = JSON.parse(rawUser) as LocalUser
    return roles.some((item) => item.id === parsedUser.role) ? parsedUser : null
  } catch {
    return null
  }
}

function createUser(email: string, username: string, password: string, role: RoleId): LocalUser {
  return {
    id: globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random()}`,
    email: email.trim(),
    username: username.trim(),
    password,
    role,
    createdAt: new Date().toISOString(),
  }
}

function canApplyTemplate(role: RoleId) {
  return rolePermissions[role].applyTemplate
}

function canEnterBlender(role: RoleId) {
  return rolePermissions[role].enterBlender
}

function canManagePermissions(role: RoleId) {
  return rolePermissions[role].managePermissions
}

function canRecordAcceptance(role: RoleId) {
  return rolePermissions[role].recordAcceptance
}

function makeLocalId(prefix: string) {
  return `${prefix}-${globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random()}`}`
}

function formatDateTime(value?: string) {
  if (!value) return '未记录'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function analystStatusLabel(status: AnalystReviewStatus) {
  if (status === 'passed') return '分析师已通过'
  if (status === 'changes_requested') return '分析师要求修改'
  return '待分析师验收'
}

function adminStatusLabel(status: AdminReviewStatus) {
  if (status === 'listed') return '已上架'
  if (status === 'rejected') return '管理员驳回'
  if (status === 'pending') return '待管理员审核'
  return '等待分析师验收'
}

function roleName(role: RoleId) {
  return roles.find((item) => item.id === role)?.name ?? role
}

function adminLogActionLabel(action: AdminLogAction) {
  if (action === 'role_change') return '权限变更'
  if (action === 'delete_user') return '删除用户'
  if (action === 'plugin_listed') return '插件上架'
  return '插件驳回'
}

function App() {
  const [currentUser, setCurrentUser] = useState<LocalUser | null>(() => readCurrentUser())
  const [role, setRole] = useState<RoleId>(() => {
    if (currentUser) return currentUser.role
    const storedRole = localStorage.getItem(roleKey) as RoleId | null
    return roles.some((item) => item.id === storedRole) ? storedRole! : 'modeler'
  })
  const [selectedTemplateId, setSelectedTemplateId] = useState(() => {
    return localStorage.getItem(selectedTemplateKey) ?? '0'
  })
  const [pluginReviews, setPluginReviews] = useState<PluginReviewItem[]>(() => readPluginReviews())
  const [adminLogs, setAdminLogs] = useState<AdminOperationLog[]>(() => readAdminLogs())
  const activeRole = currentUser?.role ?? role

  useEffect(() => {
    localStorage.setItem(roleKey, role)
  }, [role])

  useEffect(() => {
    if (!currentUser) return

    const expiresAt = readSessionExpiry() ?? createSessionExpiry()
    localStorage.setItem(sessionExpiresAtKey, String(expiresAt))
    const remainingMs = expiresAt - Date.now()

    const timer = window.setTimeout(() => {
      clearStoredSession()
      setCurrentUser(null)
    }, Math.max(0, remainingMs))

    return () => window.clearTimeout(timer)
  }, [currentUser])

  function selectTemplate(id: string) {
    if (!canApplyTemplate(activeRole)) return
    localStorage.setItem(selectedTemplateKey, id)
    setSelectedTemplateId(id)
  }

  function signIn(user: LocalUser) {
    localStorage.setItem(currentUserKey, JSON.stringify(user))
    localStorage.setItem(sessionExpiresAtKey, String(createSessionExpiry()))
    setCurrentUser(user)
    setRole(user.role)
  }

  function signOut() {
    clearStoredSession()
    setCurrentUser(null)
  }

  function updatePluginReview(id: string, updater: (item: PluginReviewItem) => PluginReviewItem) {
    setPluginReviews((currentReviews) => {
      const nextReviews = currentReviews.map((item) => (item.id === id ? updater(item) : item))
      writePluginReviews(nextReviews)
      return nextReviews
    })
  }

  function addAdminLog(input: AdminLogInput) {
    const nextLog: AdminOperationLog = {
      id: makeLocalId('admin-log'),
      operator: currentUser?.username ?? '未知管理员',
      action: input.action,
      target: input.target,
      detail: input.detail,
      createdAt: new Date().toISOString(),
    }
    setAdminLogs((currentLogs) => {
      const nextLogs = [nextLog, ...currentLogs].slice(0, 30)
      writeAdminLogs(nextLogs)
      return nextLogs
    })
  }

  return (
    <Routes>
      <Route path="/" element={<Navigate to={currentUser ? '/dashboard' : '/login'} replace />} />
      <Route
        path="/login"
        element={
          currentUser ? (
            <Navigate to="/dashboard" replace />
          ) : (
            <LoginPage role={role} setRole={setRole} onLogin={signIn} />
          )
        }
      />
      <Route
        path="/register"
        element={
          currentUser ? (
            <Navigate to="/dashboard" replace />
          ) : (
            <RegisterPage role={role} setRole={setRole} onRegister={signIn} />
          )
        }
      />
      <Route
        path="/dashboard"
        element={
          currentUser ? (
            <DashboardPage role={activeRole} selectedTemplateId={selectedTemplateId} onLogout={signOut} />
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />
      <Route
        path="/templates"
        element={
          currentUser ? (
            <TemplateMarketPage
              role={activeRole}
              selectedTemplateId={selectedTemplateId}
              onSelectTemplate={selectTemplate}
              onLogout={signOut}
            />
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />
      <Route
        path="/templates/:id"
        element={
          currentUser ? (
            <TemplateDetailPage
              role={activeRole}
              selectedTemplateId={selectedTemplateId}
              onSelectTemplate={selectTemplate}
              onLogout={signOut}
            />
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />
      <Route
        path="/nl-editor"
        element={
          currentUser ? (
            <NaturalLanguageDemoPage role={activeRole} selectedTemplateId={selectedTemplateId} onLogout={signOut} />
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />
      <Route
        path="/layout-control"
        element={
          currentUser ? (
            <LayoutControlDemoPage role={activeRole} selectedTemplateId={selectedTemplateId} onLogout={signOut} />
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />
      <Route
        path="/plugin-entry"
        element={
          currentUser && canEnterBlender(activeRole) ? (
            <PluginEntryPage role={activeRole} selectedTemplateId={selectedTemplateId} onLogout={signOut} />
          ) : currentUser ? (
            <AccessDeniedPage role={activeRole} selectedTemplateId={selectedTemplateId} onLogout={signOut} />
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />
      <Route
        path="/admin"
        element={
          currentUser && canManagePermissions(activeRole) ? (
            <AdminManagementPage
              adminLogs={adminLogs}
              currentUserId={currentUser.id}
              role={activeRole}
              selectedTemplateId={selectedTemplateId}
              onAddAdminLog={addAdminLog}
              onLogout={signOut}
            />
          ) : currentUser ? (
            <AccessDeniedPage role={activeRole} selectedTemplateId={selectedTemplateId} onLogout={signOut} />
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />
      <Route
        path="/admin/audit"
        element={
          currentUser && canManagePermissions(activeRole) ? (
            <AdminAuditPage
              adminLogs={adminLogs}
              pluginReviews={pluginReviews}
              role={activeRole}
              selectedTemplateId={selectedTemplateId}
              onAddAdminLog={addAdminLog}
              onLogout={signOut}
              onUpdatePluginReview={updatePluginReview}
            />
          ) : currentUser ? (
            <AccessDeniedPage role={activeRole} selectedTemplateId={selectedTemplateId} onLogout={signOut} />
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />
      <Route
        path="/analyst"
        element={
          currentUser && canRecordAcceptance(activeRole) ? (
            <AnalystAcceptancePage
              pluginReviews={pluginReviews}
              role={activeRole}
              selectedTemplateId={selectedTemplateId}
              onLogout={signOut}
              onUpdatePluginReview={updatePluginReview}
            />
          ) : currentUser ? (
            <AccessDeniedPage role={activeRole} selectedTemplateId={selectedTemplateId} onLogout={signOut} />
          ) : (
            <Navigate to="/login" replace />
          )
        }
      />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}

function Shell({
  children,
  role,
  selectedTemplateId,
  onLogout,
}: {
  children: ReactNode
  role?: RoleId
  selectedTemplateId?: string
  onLogout: () => void
}) {
  const currentRole = roles.find((item) => item.id === role) ?? roles[0]
  const selectedTemplate = getTemplate(selectedTemplateId)
  const navigate = useNavigate()
  const location = useLocation()
  const [sidebarCollapsed, setSidebarCollapsed] = useState(() => {
    return localStorage.getItem(sidebarCollapsedKey) === 'true'
  })

  useEffect(() => {
    localStorage.setItem(sidebarCollapsedKey, String(sidebarCollapsed))
  }, [sidebarCollapsed])

  const pageHistory = useMemo(() => {
    const currentHistory = readPageHistory()
    if (!isTrackedPage(location.pathname)) return currentHistory
    if (currentHistory.entries[currentHistory.index] === location.pathname) return currentHistory

    const activeEntries =
      currentHistory.index >= 0
        ? currentHistory.entries.slice(0, currentHistory.index + 1)
        : []
    const entries = [...activeEntries, location.pathname].slice(-24)
    const nextHistory = { entries, index: entries.length - 1 }
    writePageHistory(nextHistory)
    return nextHistory
  }, [location.pathname])

  function handleLogout() {
    onLogout()
    navigate('/login', { replace: true })
  }

  function movePageHistory(delta: -1 | 1) {
    const currentHistory = readPageHistory()
    const nextIndex = currentHistory.index + delta
    const target = currentHistory.entries[nextIndex]

    if (!target) return

    const nextHistory = { entries: currentHistory.entries, index: nextIndex }
    writePageHistory(nextHistory)
    navigate(target)
  }

  const canGoBack = pageHistory.index > 0
  const canGoForward = pageHistory.index >= 0 && pageHistory.index < pageHistory.entries.length - 1

  return (
    <div className={`app-shell role-theme-${currentRole.id} ${sidebarCollapsed ? 'sidebar-collapsed' : ''}`}>
      <aside className="sidebar">
        <div className="brand">
          <button
            className="brand-control"
            type="button"
            aria-label={sidebarCollapsed ? '展开侧边栏' : '收起侧边栏'}
            aria-expanded={!sidebarCollapsed}
            onClick={() => setSidebarCollapsed((collapsed) => !collapsed)}
          >
            <span className="brand-icon icon-city">
              <Building2 size={20} />
            </span>
            <span className="brand-icon icon-menu">
              <Menu size={20} />
            </span>
            <span className="brand-icon icon-expand">
              <ChevronRight size={20} />
            </span>
          </button>
          <Link className="brand-text" to="/dashboard" aria-label="返回工作台">
            <strong>智能城市生成系统</strong>
            <small>ICity Prototype</small>
          </Link>
        </div>

        <nav className="nav-list" aria-label="主导航">
          <Link to="/dashboard" title="工作台">
            <LayoutDashboard size={18} />
            <span className="nav-label">工作台</span>
          </Link>
          <Link to="/templates" title="模板商城">
            <Store size={18} />
            <span className="nav-label">模板商城</span>
          </Link>
          <Link to="/nl-editor" title="自然语言编辑">
            <Send size={18} />
            <span className="nav-label">自然语言编辑</span>
          </Link>
          <Link to="/layout-control" title="布局控制">
            <ClipboardList size={18} />
            <span className="nav-label">布局控制</span>
          </Link>
          {currentRole.id === 'modeler' ? (
            <Link to="/plugin-entry" title="Blender 入口">
              <PlugZap size={18} />
              <span className="nav-label">Blender 入口</span>
            </Link>
          ) : (
            <span className="nav-disabled" title="仅建模师可进入 Blender">
              <PlugZap size={18} />
              <span className="nav-label">Blender 入口</span>
            </span>
          )}
          {canManagePermissions(currentRole.id) && (
            <>
              <Link to="/admin" title="权限管理">
                <ShieldCheck size={18} />
                <span className="nav-label">权限管理</span>
              </Link>
              <Link to="/admin/audit" title="插件审核">
                <ClipboardList size={18} />
                <span className="nav-label">插件审核</span>
              </Link>
            </>
          )}
          {canRecordAcceptance(currentRole.id) && (
            <Link to="/analyst" title="验收中心">
              <ClipboardCheck size={18} />
              <span className="nav-label">验收中心</span>
            </Link>
          )}
        </nav>

        <div className="side-card">
          <span className="eyebrow">当前角色</span>
          <strong>{currentRole.name}</strong>
          <p>{currentRole.description}</p>
        </div>

        <div className="side-card selected">
          <span className="eyebrow">已选模板</span>
          <strong>模板 {selectedTemplate.id}</strong>
          <p>{selectedTemplate.name}</p>
        </div>

        <button className="logout-button" type="button" onClick={handleLogout} title="退出登录">
          <LogOut size={18} />
          <span className="nav-label">退出登录</span>
        </button>
      </aside>
      <main className="content">
        <div className="content-nav" aria-label="页面历史导航">
          <button
            className="history-button"
            type="button"
            disabled={!canGoBack}
            onClick={() => movePageHistory(-1)}
            title="后退"
          >
            <ChevronLeft size={18} />
          </button>
          <button
            className="history-button"
            type="button"
            disabled={!canGoForward}
            onClick={() => movePageHistory(1)}
            title="前进"
          >
            <ChevronRight size={18} />
          </button>
        </div>
        {children}
      </main>
    </div>
  )
}

function AuthVisual() {
  return (
    <section className="login-visual" aria-label="系统概览">
      <div className="city-window">
        <div className="map-grid">
          <span className="road horizontal top"></span>
          <span className="road horizontal mid"></span>
          <span className="road vertical left"></span>
          <span className="road vertical right"></span>
          <span className="block tall"></span>
          <span className="block low"></span>
          <span className="block park"></span>
          <span className="block civic"></span>
        </div>
      </div>
      <div className="login-copy">
        <h1>智能城市生成系统</h1>
        <p>管理城市模板、角色权限和 Blender 插件入口的原型系统。</p>
      </div>
    </section>
  )
}

function LoginPage({
  role,
  setRole,
  onLogin,
}: {
  role: RoleId
  setRole: (role: RoleId) => void
  onLogin: (user: LocalUser) => void
}) {
  const navigate = useNavigate()
  const initialMethod = useMemo(() => readRememberedLoginMethod(), [])
  const initialRemembered = useMemo(() => readRememberedLogin(initialMethod), [initialMethod])
  const [method, setMethod] = useState<LoginMethod>(initialMethod)
  const [identifier, setIdentifier] = useState(initialRemembered.identifier)
  const [password, setPassword] = useState(initialRemembered.password)
  const [rememberIdentifier, setRememberIdentifier] = useState(initialRemembered.rememberIdentifier)
  const [rememberPassword, setRememberPassword] = useState(initialRemembered.rememberPassword)
  const [error, setError] = useState('')

  function changeMethod(nextMethod: LoginMethod) {
    const remembered = readRememberedLogin(nextMethod)
    setMethod(nextMethod)
    setIdentifier(remembered.identifier)
    setPassword(remembered.password)
    setRememberIdentifier(remembered.rememberIdentifier)
    setRememberPassword(remembered.rememberPassword)
    setError('')
  }

  function submitLogin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const normalizedIdentifier = normalizeIdentifier(identifier)
    const matchedUser = readUsers().find((user) => {
      const fieldValue = method === 'email' ? user.email : user.username
      return (
        user.role === role &&
        normalizeIdentifier(fieldValue) === normalizedIdentifier &&
        user.password === password
      )
    })

    if (!matchedUser) {
      setError(method === 'email' ? '邮箱、密码或身份不匹配' : '账号名、密码或身份不匹配')
      return
    }

    writeRememberedLogin(method, {
      rememberIdentifier,
      identifier: rememberIdentifier ? identifier : '',
      rememberPassword,
      password: rememberPassword ? password : '',
    })
    onLogin(matchedUser)
    navigate('/dashboard')
  }

  return (
    <main className="login-page">
      <AuthVisual />

      <section className="login-panel" aria-label="账号登录">
        <div className="auth-mode" role="tablist" aria-label="登录方式">
          <button
            className={method === 'email' ? 'active' : ''}
            onClick={() => changeMethod('email')}
            type="button"
          >
            邮箱登录
          </button>
          <button
            className={method === 'username' ? 'active' : ''}
            onClick={() => changeMethod('username')}
            type="button"
          >
            账号名登录
          </button>
        </div>

        <form className="auth-form" noValidate onSubmit={submitLogin}>
          <label className="field">
            <span>{method === 'email' ? '邮箱' : '账号名'}</span>
            <input
              autoComplete={method === 'email' ? 'email' : 'username'}
              onChange={(event) => {
                setIdentifier(event.target.value)
                setError('')
              }}
              placeholder={method === 'email' ? 'name@example.com' : '请输入账号名'}
              type={method === 'email' ? 'email' : 'text'}
              value={identifier}
            />
          </label>

          <label className="field">
            <span>密码</span>
            <input
              autoComplete="current-password"
              onChange={(event) => {
                setPassword(event.target.value)
                setError('')
              }}
              placeholder="请输入密码"
              type="password"
              value={password}
            />
          </label>

          <div className="remember-options" aria-label="登录记忆选项">
            <label className="checkbox-field">
              <input
                checked={rememberIdentifier}
                onChange={(event) => setRememberIdentifier(event.target.checked)}
                type="checkbox"
              />
              <span>{method === 'email' ? '记住邮箱' : '记住用户名'}</span>
            </label>
            <label className="checkbox-field">
              <input
                checked={rememberPassword}
                onChange={(event) => setRememberPassword(event.target.checked)}
                type="checkbox"
              />
              <span>记住密码</span>
            </label>
          </div>

          {error && (
            <p className="form-error" role="alert">
              {error}
            </p>
          )}

          <div className="role-grid compact">
            {roles.map((item) => (
              <button
                className={`role-option ${role === item.id ? 'active' : ''}`}
                key={item.id}
                onClick={() => setRole(item.id)}
                type="button"
              >
                <span className="role-icon">{roleIcon(item.id)}</span>
                <strong>{item.name}</strong>
                <small>{item.description}</small>
              </button>
            ))}
          </div>

          <button className="primary-action" type="submit">
            进入系统
            <ArrowRight size={18} />
          </button>
        </form>

        <Link className="auth-link" to="/register">
          未注册账号？立即注册
        </Link>
      </section>
    </main>
  )
}

function RegisterPage({
  role,
  setRole,
  onRegister,
}: {
  role: RoleId
  setRole: (role: RoleId) => void
  onRegister: (user: LocalUser) => void
}) {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [errors, setErrors] = useState<{
    email?: string
    username?: string
    password?: string
  }>({})

  function submitRegister(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    const nextErrors: typeof errors = {}
    const trimmedEmail = email.trim()
    const trimmedUsername = username.trim()

    if (!trimmedEmail) {
      nextErrors.email = '请输入邮箱'
    } else if (!/^\S+@\S+\.\S+$/.test(trimmedEmail)) {
      nextErrors.email = '请输入有效邮箱'
    }

    if (!trimmedUsername) {
      nextErrors.username = '请输入账号名'
    }

    if (!password) {
      nextErrors.password = '请输入密码'
    }

    if (Object.keys(nextErrors).length) {
      setErrors(nextErrors)
      return
    }

    const users = readUsers()
    const sameRoleUsers = users.filter((user) => user.role === role)
    const usernameTaken = users.some(
      (user) => normalizeIdentifier(user.username) === normalizeIdentifier(trimmedUsername),
    )
    const emailTaken = sameRoleUsers.some(
      (user) => normalizeIdentifier(user.email) === normalizeIdentifier(trimmedEmail),
    )

    if (usernameTaken) {
      nextErrors.username = '账号名已经被注册，请更换；用户名在所有角色中都必须唯一'
    }

    if (emailTaken) {
      nextErrors.email = `该邮箱已经注册过${roleName(role)}，同一邮箱每个角色只能注册一次`
    }

    if (Object.keys(nextErrors).length) {
      setErrors(nextErrors)
      return
    }

    const user = createUser(trimmedEmail, trimmedUsername, password, role)
    writeUsers([...users, user])
    onRegister(user)
    navigate('/dashboard')
  }

  return (
    <main className="login-page">
      <AuthVisual />

      <section className="login-panel" aria-label="账号注册">
        <div>
          <span className="eyebrow">账号注册</span>
          <h2>创建本地演示账号</h2>
        </div>

        <form className="auth-form" noValidate onSubmit={submitRegister}>
          <label className="field">
            <span>邮箱</span>
            <input
              autoComplete="email"
              onChange={(event) => {
                setEmail(event.target.value)
                setErrors((currentErrors) => ({ ...currentErrors, email: undefined }))
              }}
              placeholder="name@example.com"
              type="email"
              value={email}
            />
            {errors.email && (
              <small className="field-error" role="alert">
                {errors.email}
              </small>
            )}
          </label>

          <label className="field">
            <span>账号名</span>
            <input
              autoComplete="username"
              onChange={(event) => {
                setUsername(event.target.value)
                setErrors((currentErrors) => ({ ...currentErrors, username: undefined }))
              }}
              placeholder="请输入账号名"
              type="text"
              value={username}
            />
            {errors.username && (
              <small className="field-error" role="alert">
                {errors.username}
              </small>
            )}
          </label>

          <label className="field">
            <span>密码</span>
            <input
              autoComplete="new-password"
              onChange={(event) => {
                setPassword(event.target.value)
                setErrors((currentErrors) => ({ ...currentErrors, password: undefined }))
              }}
              placeholder="请输入密码"
              type="password"
              value={password}
            />
            {errors.password && (
              <small className="field-error" role="alert">
                {errors.password}
              </small>
            )}
          </label>

          <div className="role-grid compact">
            {roles.map((item) => (
              <button
                className={`role-option ${role === item.id ? 'active' : ''}`}
                key={item.id}
                onClick={() => setRole(item.id)}
                type="button"
              >
                <span className="role-icon">{roleIcon(item.id)}</span>
                <strong>{item.name}</strong>
                <small>{item.description}</small>
              </button>
            ))}
          </div>

          <button className="primary-action" type="submit">
            注册并进入系统
            <ArrowRight size={18} />
          </button>
        </form>

        <Link className="auth-link" to="/login">
          已有账号？返回登录
        </Link>
      </section>
    </main>
  )
}

function getDashboardView(role: RoleId) {
  if (role === 'admin') {
    return {
      eyebrow: '管理员工作台',
      title: '管理角色权限、插件审核和系统状态',
      description: '管理员视图突出权限管理与运行检查，同时保留模板商城和 Blender 入口用于演示完整链路。',
      actionText: '进入权限管理',
      actionLink: '/admin',
      workflowTitle: '权限与插件管理流程',
      steps: ['核对用户角色', '检查功能权限', '审核插件入口', '确认系统状态'],
      tasks: [
        {
          icon: <ShieldCheck size={19} />,
          label: '权限管理',
          title: '用户权限总览',
          text: '查看不同角色可用模块，查看各角色可访问的页面和操作范围。',
        },
        {
          icon: <PlugZap size={19} />,
          label: '插件审核',
          title: 'Blender 入口审核',
          text: '确认插件入口、模板参数和演示流程是否满足上架与使用要求。',
        },
        {
          icon: <MonitorPlay size={19} />,
          label: '系统状态',
          title: 'Demo 模块状态',
          text: '快速检查登录、模板商城、详情页和插件入口是否处于可演示状态。',
        },
      ],
    }
  }

  if (role === 'analyst') {
    return {
      eyebrow: '分析师工作台',
      title: '验收模板能力与插件演示链路',
      description: '分析师视图强调需求核对、验收评审和指标记录，用于沉淀模板评审、需求核对和验收记录。',
      actionText: '进入验收中心',
      actionLink: '/analyst',
      workflowTitle: '验收与评审流程',
      steps: ['查看场景需求', '核对模板参数', '评审插件链路', '记录验收结论'],
      tasks: [
        {
          icon: <BarChart3 size={19} />,
          label: '行业需求',
          title: '模板适配分析',
          text: '对比不同城市模板的适用场景，判断是否覆盖当前智慧城市场景需求。',
        },
        {
          icon: <BadgeCheck size={19} />,
          label: '验收评审',
          title: '功能完整度核对',
          text: '检查多角色登录、权限区分和 Blender 入口模拟是否形成完整闭环。',
        },
        {
          icon: <Boxes size={19} />,
          label: '指标记录',
          title: '模板参数追踪',
          text: '记录 tree_type、road_texture、bench_type 等字段与插件资产的映射关系。',
        },
      ],
    }
  }

  return {
    eyebrow: '建模师工作台',
    title: '完成模板选择与 Blender 生成演示',
    description: '建模师视图聚焦模板挑选、参数查看和进入 Blender 插件，适合展示普通使用者的核心操作链路。',
    actionText: '模拟进入 Blender',
    actionLink: '/plugin-entry',
    workflowTitle: '模板化场景生成',
    steps: ['选择模板', '写入模板 ID', '进入插件', '应用资产配置'],
    tasks: [
      {
        icon: <Store size={19} />,
        label: '模板选择',
        title: '挑选城市模板',
        text: '从模板商城选择城市风格，并将模板 ID 保存为插件输入。',
      },
      {
        icon: <Boxes size={19} />,
        label: '资产映射',
        title: '查看资源字段',
        text: '核对树木、道路纹理和长椅类型对应的 iCity 插件资产。',
      },
      {
        icon: <PlugZap size={19} />,
        label: '插件生成',
        title: '进入 Blender',
        text: '带着当前模板参数跳转至模拟插件入口，完成生成流程演示。',
      },
    ],
  }
}

function DashboardPage({
  role,
  selectedTemplateId,
  onLogout,
}: {
  role: RoleId
  selectedTemplateId: string
  onLogout: () => void
}) {
  const currentTemplate = getTemplate(selectedTemplateId)
  const dashboardView = getDashboardView(role)

  return (
    <Shell role={role} selectedTemplateId={selectedTemplateId} onLogout={onLogout}>
      <section className="page-heading">
        <div>
          <span className="eyebrow">{dashboardView.eyebrow}</span>
          <h1>{dashboardView.title}</h1>
          <p>
            {dashboardView.description}
          </p>
        </div>
        <Link className="secondary-action" to={dashboardView.actionLink}>
          {dashboardView.actionText}
          <ExternalLink size={17} />
        </Link>
      </section>

      <section className="dashboard-grid">
        <div className="workspace-panel main-workflow">
          <div className="panel-head">
            <span className="eyebrow">核心流程</span>
            <h2>{dashboardView.workflowTitle}</h2>
          </div>
          <div className="flow-line">
            {dashboardView.steps.map((item, index) => (
              <div className="flow-step" key={item}>
                <span>{index + 1}</span>
                <strong>{item}</strong>
              </div>
            ))}
          </div>
          <div className="selected-template-strip">
            <img src={currentTemplate.preview.road} alt="" />
            <div>
              <span className="eyebrow">当前模板</span>
              <h3>{currentTemplate.name}</h3>
              <p>{currentTemplate.fit}</p>
            </div>
            <Link className="icon-action" to={`/templates/${currentTemplate.id}`} aria-label="查看模板详情">
              <ArrowRight size={18} />
            </Link>
          </div>
        </div>

        <div className="workspace-panel">
          <div className="panel-head">
            <span className="eyebrow">权限视图</span>
            <h2>{roleLabel(role)}</h2>
          </div>
          <PermissionList role={role} />
        </div>
      </section>

      <section className="role-task-grid" aria-label="角色任务区">
        {dashboardView.tasks.map((task) => (
          <article className="role-task-card" key={task.title}>
            <span className="role-task-icon">{task.icon}</span>
            <div>
              <span className="eyebrow">{task.label}</span>
              <h3>{task.title}</h3>
              <p>{task.text}</p>
            </div>
          </article>
        ))}
      </section>

      <section className="module-grid">
        <FeatureCard
          icon={<Store size={20} />}
          title="模板商城"
          text="展示可选城市风格和参数组合，点击即可作为插件输入。"
          link="/templates"
        />
        <FeatureCard
          icon={<Boxes size={20} />}
          title="资产映射"
          text="模板参数对应 iCity 内部树木、道路纹理与长椅资产。"
          link={`/templates/${currentTemplate.id}`}
        />
        <FeatureCard
          icon={<Send size={20} />}
          title="自然语言编辑"
          text="用中文描述想要的街区效果，查看系统整理出的场景参数。"
          link="/nl-editor"
        />
        <FeatureCard
          icon={<ClipboardList size={20} />}
          title="布局控制"
          text="编辑点线道路，查看 JSON 草稿，并从黑白草图生成路网。"
          link="/layout-control"
        />
        <FeatureCard
          icon={<MonitorPlay size={20} />}
          title="Blender 入口"
          text={
            canEnterBlender(role)
              ? '打开当前模板的插件参数面板，继续完成场景生成。'
              : '该入口仅建模师可直接进入，其他角色可在各自面板中查看审核或验收信息。'
          }
          link="/plugin-entry"
          locked={!canEnterBlender(role)}
          reason={role === 'admin' ? '管理员通过权限管理页审核入口' : '分析师仅查看验收链路'}
        />
      </section>
    </Shell>
  )
}

function TemplateMarketPage({
  role,
  selectedTemplateId,
  onSelectTemplate,
  onLogout,
}: {
  role: RoleId
  selectedTemplateId: string
  onSelectTemplate: (id: string) => void
  onLogout: () => void
}) {
  const [query, setQuery] = useState('')
  const visibleTemplates = useMemo(() => {
    const normalized = query.trim().toLowerCase()
    if (!normalized) return templates
    return templates.filter((template) => {
      return [template.name, template.sceneType, template.description, ...template.tags]
        .join(' ')
        .toLowerCase()
        .includes(normalized)
    })
  }, [query])

  return (
    <Shell role={role} selectedTemplateId={selectedTemplateId} onLogout={onLogout}>
      <section className="page-heading">
        <div>
          <span className="eyebrow">模板商城</span>
          <h1>选择一套城市资产组合</h1>
          <p>每个模板是一套“整城”配置：同时设定 树木 / 道路 / 座椅 等街道资产 + 交通、人群、生态，可直接同步到 iCity 插件。</p>
        </div>
        <label className="search-box">
          <Search size={17} />
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="搜索模板、场景或标签"
          />
        </label>
      </section>

      {!canApplyTemplate(role) && (
        <div className="permission-banner">
          <ShieldCheck size={18} />
          当前身份仅可查看模板详情，只有场景建模师可以应用模板。
        </div>
      )}

      <section className="template-grid">
        {visibleTemplates.map((template) => (
          <TemplateCard
            key={template.id}
            role={role}
            selected={selectedTemplateId === template.id}
            template={template}
            onSelectTemplate={onSelectTemplate}
          />
        ))}
      </section>
    </Shell>
  )
}

function TemplateDetailPage({
  role,
  selectedTemplateId,
  onSelectTemplate,
  onLogout,
}: {
  role: RoleId
  selectedTemplateId: string
  onSelectTemplate: (id: string) => void
  onLogout: () => void
}) {
  const { id } = useParams()
  const template = getTemplate(id)
  const navigate = useNavigate()
  const isSelected = selectedTemplateId === template.id
  const canApply = canApplyTemplate(role)
  const canEnterPlugin = canEnterBlender(role)
  const applyLabel = isSelected ? '当前已选择' : canApply ? '使用该模板' : '仅建模师可使用'

  return (
    <Shell role={role} selectedTemplateId={selectedTemplateId} onLogout={onLogout}>
      <button className="back-button" onClick={() => navigate('/templates')} type="button">
        <ChevronLeft size={17} />
        返回模板商城
      </button>

      <section className="detail-layout">
        <div className="detail-preview">
          <div className="road-stage">
            <img className="road-texture" src={template.preview.road} alt={`${template.name}道路纹理`} />
            <img className="tree-asset" src={template.preview.tree} alt={`${template.name}树木资产`} />
            <img className="bench-asset" src={template.preview.bench} alt={`${template.name}长椅资产`} />
          </div>
        </div>

        <div className="detail-copy">
          <span className="template-id">模板 {template.id}</span>
          <h1>{template.name}</h1>
          <p>{template.description}</p>
          <div className="tag-row">
            {template.tags.map((tag) => (
              <span key={tag}>{tag}</span>
            ))}
          </div>

          <div className="param-table">
            <ParamRow label="tree_type" value={template.tree_type} asset={template.pluginValues.tree} />
            <ParamRow label="road_texture" value={template.road_texture} asset={template.pluginValues.road} />
            <ParamRow label="bench_type" value={template.bench_type} asset={template.pluginValues.bench} />
          </div>

          <div className="compact-params">
            <span>车流 {template.scene.traffic}</span>
            <span>人群 {template.scene.pedestrian}</span>
            <span>生态 {template.scene.ecology}</span>
          </div>

          <div className="action-row">
            <button
              className={`primary-action ${isSelected ? 'is-selected' : ''}`}
              disabled={isSelected || !canApply}
              type="button"
              onClick={() => {
                if (canApply && !isSelected) onSelectTemplate(template.id)
              }}
            >
              {applyLabel}
              <CheckCircle2 size={18} />
            </button>
            {canEnterPlugin ? (
              <Link className="secondary-action" to="/plugin-entry">
                进入 Blender
                <ExternalLink size={17} />
              </Link>
            ) : (
              <button className="secondary-action is-locked" disabled type="button">
                无权限进入 Blender
                <ShieldCheck size={17} />
              </button>
            )}
          </div>
        </div>
      </section>
    </Shell>
  )
}

function NaturalLanguageDemoPage({
  role,
  selectedTemplateId,
  onLogout,
}: {
  role: RoleId
  selectedTemplateId: string
  onLogout: () => void
}) {
  const [activeDemoId, setActiveDemoId] = useState(naturalLanguageDemos[0].id)
  const activeDemo = naturalLanguageDemos.find((demo) => demo.id === activeDemoId) ?? naturalLanguageDemos[0]

  return (
    <Shell role={role} selectedTemplateId={selectedTemplateId} onLogout={onLogout}>
      <section className="page-heading">
        <div>
          <span className="eyebrow">自然语言交互</span>
          <h1>中文指令映射到 iCity 场景编辑</h1>
          <p>输入中文指令后，系统会整理出场景参数，并列出将执行的插件操作。</p>
        </div>
        <Link className="secondary-action" to="/plugin-entry">
          查看插件入口
          <ExternalLink size={17} />
        </Link>
      </section>

      <section className="nl-demo-layout">
        <div className="workspace-panel nl-command-panel">
          <div className="panel-head">
            <span className="eyebrow">输入示例</span>
            <h2>自然语言指令</h2>
          </div>
          <div className="nl-input-preview">
            <span>{activeDemo.command}</span>
            <Send size={19} />
          </div>
          <div className="demo-choice-list">
            {naturalLanguageDemos.map((demo) => (
              <button
                className={activeDemo.id === demo.id ? 'active' : ''}
                key={demo.id}
                onClick={() => setActiveDemoId(demo.id)}
                type="button"
              >
                {demo.command}
              </button>
            ))}
          </div>
        </div>

        <div className="workspace-panel nl-result-panel">
          <div className="panel-head">
            <span className="eyebrow">解析结果</span>
            <h2>{activeDemo.engine}</h2>
          </div>
          <div className="code-block result-code">
            <span>{'{'}</span>
            {activeDemo.result.map(([key, value]) => (
              <span key={key}>  "{key}": "{value}",</span>
            ))}
            <span>  "operator": "icity.apply_nl_command"</span>
            <span>{'}'}</span>
          </div>
          <div className="compact-params">
            {activeDemo.effects.map((effect) => (
              <span key={effect}>{effect}</span>
            ))}
          </div>
        </div>
      </section>

      <section className="capability-grid">
        <div className="workspace-panel">
          <div className="panel-head">
            <span className="eyebrow">控制维度</span>
            <h2>资产、交通、人群、生态统一表达</h2>
          </div>
          <div className="capability-list">
            {['树木/座椅/路面材质', '车流 none-low-medium-high-max', '人群 none-low-medium-high-max', '湖光山色 / 群山 / 河谷 / 清空生态'].map((item) => (
              <span key={item}>
                <BadgeCheck size={17} />
                {item}
              </span>
            ))}
          </div>
        </div>

        <div className="workspace-panel">
          <div className="panel-head">
            <span className="eyebrow">后端调用</span>
            <h2>即将执行的插件操作</h2>
          </div>
          <div className="operator-list">
            {activeDemo.operators.map((operator) => (
              <code key={operator}>{operator}</code>
            ))}
          </div>
        </div>
      </section>
    </Shell>
  )
}

function LayoutControlDemoPage({
  role,
  selectedTemplateId,
  onLogout,
}: {
  role: RoleId
  selectedTemplateId: string
  onLogout: () => void
}) {
  const [activeSampleId, setActiveSampleId] = useState(layoutSamples[0].id)
  const activeSample = layoutSamples.find((sample) => sample.id === activeSampleId) ?? layoutSamples[0]
  const graphJson = JSON.stringify(
    {
      version: 1,
      nodes: activeSample.nodes.map((node) => ({ ...node, z: 0 })),
      edges: activeSample.edges.map((edge) => ({ ...edge, enabled_as_road: true })),
      faces: [],
    },
    null,
    2,
  )

  return (
    <Shell role={role} selectedTemplateId={selectedTemplateId} onLogout={onLogout}>
      <section className="page-heading">
        <div>
          <span className="eyebrow">道路布局控制</span>
          <h1>点线 Draft、JSON 输入与草图识别展示</h1>
          <p>选择路网草稿，查看点线结构、JSON 数据和草图识别后的可编辑道路。</p>
        </div>
        <Link className="secondary-action" to="/templates">
          返回模板商城
          <ChevronLeft size={17} />
        </Link>
      </section>

      <section className="layout-demo-layout">
        <div className="workspace-panel layout-map-panel">
          <div className="panel-head">
            <span className="eyebrow">Draft Preview</span>
            <h2>{activeSample.name}</h2>
          </div>
          <div className="layout-map">
            {activeSample.edges.map((edge) => {
              const start = activeSample.nodes.find((node) => node.id === edge.start)
              const end = activeSample.nodes.find((node) => node.id === edge.end)
              if (!start || !end) return null
              return (
                <span
                  className="layout-edge"
                  key={edge.id}
                  style={{
                    left: `${Math.min(start.x, end.x)}%`,
                    top: `${Math.min(start.y, end.y)}%`,
                    width: start.x === end.x ? 4 : `${Math.abs(end.x - start.x)}%`,
                    height: start.y === end.y ? 4 : `${Math.abs(end.y - start.y)}%`,
                  }}
                />
              )
            })}
            {activeSample.nodes.map((node) => (
              <span
                className="layout-node"
                key={node.id}
                style={{ left: `${node.x}%`, top: `${node.y}%` }}
                title={node.id}
              >
                {node.id.replace('n', '')}
              </span>
            ))}
          </div>
          <div className="layout-sample-switch">
            {layoutSamples.map((sample) => (
              <button
                className={sample.id === activeSample.id ? 'active' : ''}
                key={sample.id}
                onClick={() => setActiveSampleId(sample.id)}
                type="button"
              >
                {sample.name}
              </button>
            ))}
          </div>
        </div>

        <div className="workspace-panel layout-json-panel">
          <div className="panel-head">
            <span className="eyebrow">LayoutGraph JSON</span>
            <h2>{activeSample.summary}</h2>
          </div>
          <pre className="json-preview">{graphJson}</pre>
        </div>
      </section>

      <section className="capability-grid">
        <div className="workspace-panel">
          <div className="panel-head">
            <span className="eyebrow">操作链路</span>
            <h2>从草稿到真实 ICity Base</h2>
          </div>
          <div className="flow-line compact-flow">
            {['Inspect', 'Validate', 'Normalize', 'Preview', 'Apply'].map((step, index) => (
              <div className="flow-step" key={step}>
                <span>{index + 1}</span>
                <strong>{step}</strong>
              </div>
            ))}
          </div>
          <div className="capability-list">
            {activeSample.stats.map((stat) => (
              <span key={stat}>
                <BadgeCheck size={17} />
                {stat}
              </span>
            ))}
          </div>
        </div>

        <div className="workspace-panel sketch-panel">
          <div className="panel-head">
            <span className="eyebrow">草图识别</span>
            <h2>白底黑线图转可编辑道路</h2>
          </div>
          <div className="sketch-preview">
            <span className="sketch-line horizontal"></span>
            <span className="sketch-line vertical"></span>
            <span className="sketch-caption">PNG / JPG 草图</span>
          </div>
          <div className="operator-list">
            {['OpenCV 阈值提取', '骨架化中心线', '端点吸附', '转为 LayoutGraph'].map((item) => (
              <code key={item}>{item}</code>
            ))}
          </div>
        </div>
      </section>
    </Shell>
  )
}

function PluginEntryPage({
  role,
  selectedTemplateId,
  onLogout,
}: {
  role: RoleId
  selectedTemplateId: string
  onLogout: () => void
}) {
  const template = getTemplate(selectedTemplateId)
  const [open, setOpen] = useState(false)

  return (
    <Shell role={role} selectedTemplateId={selectedTemplateId} onLogout={onLogout}>
      <section className="page-heading">
        <div>
          <span className="eyebrow">插件系统入口</span>
          <h1>模拟跳转至 ICity Blender 插件</h1>
          <p>当前模板参数已准备好，可带入 iCity Blender 插件继续生成场景。</p>
        </div>
      </section>

      <section className="plugin-panel">
        <div className="plugin-window">
          <div className="window-bar">
            <span></span>
            <span></span>
            <span></span>
            <strong>ICity Template Generator</strong>
          </div>
          <div className="plugin-body">
            <div className="field-preview">
              <label>Template ID</label>
              <strong>{template.id}</strong>
            </div>
            <div className="code-block">
              <span>{'{'}</span>
              <span>  "tree_type": {template.tree_type},</span>
              <span>  "road_texture": {template.road_texture},</span>
              <span>  "bench_type": {template.bench_type}</span>
              <span>{'}'}</span>
            </div>
            <button className="primary-action" type="button" onClick={() => setOpen(true)}>
              模拟进入 Blender
              <DoorOpen size={18} />
            </button>
          </div>
        </div>

        <div className="plugin-notes">
          <span className="eyebrow">插件配置</span>
          <h2>模板参数将作为插件生成配置使用</h2>
          <ul>
            <li>
              <BadgeCheck size={18} />
              当前模板 ID 会保存在浏览器本地状态中。
            </li>
            <li>
              <BadgeCheck size={18} />
              参数字段与后续 iCity 插件模板化 JSON 保持一致。
            </li>
            <li>
              <BadgeCheck size={18} />
              确认参数后，在 Blender 插件中应用同一模板。
            </li>
          </ul>
        </div>
      </section>

      {open && (
        <div className="modal-backdrop" role="presentation" onClick={() => setOpen(false)}>
          <div className="modal" role="dialog" aria-modal="true" onClick={(event) => event.stopPropagation()}>
            <span className="modal-icon">
              <PlugZap size={24} />
            </span>
            <h2>Blender 插件参数已准备好</h2>
            <p>请在插件中输入模板 ID：{template.id}，然后点击 Apply Template。</p>
            <button className="primary-action" type="button" onClick={() => setOpen(false)}>
              知道了
            </button>
          </div>
        </div>
      )}
    </Shell>
  )
}

function AccessDeniedPage({
  role,
  selectedTemplateId,
  onLogout,
}: {
  role: RoleId
  selectedTemplateId: string
  onLogout: () => void
}) {
  const currentRole = roles.find((item) => item.id === role) ?? roles[0]
  const location = useLocation()
  const isAdminRoute = location.pathname.startsWith('/admin')
  const deniedTitle = isAdminRoute
    ? '只有系统管理员可以进入权限管理页'
    : role === 'admin'
      ? '管理员通过权限管理页审核插件入口'
      : '非建模师仅可查看模板与验收链路'
  const deniedDescription = isAdminRoute
    ? '权限管理页仅对系统管理员开放；建模师和分析师会被拦截到当前提示页。'
    : 'Blender 生成入口仅对场景建模师开放；管理员负责权限与审核，分析师负责需求核对和验收记录。'

  return (
    <Shell role={role} selectedTemplateId={selectedTemplateId} onLogout={onLogout}>
      <section className="page-heading">
        <div>
          <span className="eyebrow">权限限制</span>
          <h1>当前身份无法访问该模块</h1>
          <p>
            你正在使用“{currentRole.name}”身份。该模块已经接入前端权限控制，请返回对应工作台使用当前角色允许的功能。
          </p>
        </div>
        <Link className="secondary-action" to="/dashboard">
          返回工作台
          <ChevronLeft size={17} />
        </Link>
      </section>

      <section className="workspace-panel access-panel">
        <span className="modal-icon">
          <ShieldCheck size={24} />
        </span>
        <div>
          <span className="eyebrow">无权限访问</span>
          <h2>{deniedTitle}</h2>
          <p>{deniedDescription}</p>
          <div className="action-row">
            {canManagePermissions(role) && (
              <Link className="primary-action" to="/admin">
                进入权限管理
                <ShieldCheck size={18} />
              </Link>
            )}
            {canEnterBlender(role) && (
              <Link className="primary-action" to="/plugin-entry">
                进入 Blender
                <PlugZap size={18} />
              </Link>
            )}
            <Link className="secondary-action" to="/templates">
              查看模板商城
              <Store size={17} />
            </Link>
          </div>
        </div>
      </section>
    </Shell>
  )
}

function AnalystAcceptancePage({
  pluginReviews,
  role,
  selectedTemplateId,
  onLogout,
  onUpdatePluginReview,
}: {
  pluginReviews: PluginReviewItem[]
  role: RoleId
  selectedTemplateId: string
  onLogout: () => void
  onUpdatePluginReview: PluginReviewAction
}) {
  const [standards, setStandards] = useState<AcceptanceStandard[]>(() => readAcceptanceStandards())
  const [newStandard, setNewStandard] = useState({ category: '功能', title: '', description: '' })
  const [memo, setMemo] = useState<IndustryDemandMemo>(() => readIndustryMemo())
  const [memoSaved, setMemoSaved] = useState(false)
  const pendingReviewCount = pluginReviews.filter((item) => item.analystStatus === 'pending').length
  const passedReviewCount = pluginReviews.filter((item) => item.analystStatus === 'passed').length

  function addStandard(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const title = newStandard.title.trim()
    const description = newStandard.description.trim()
    const category = newStandard.category.trim() || '功能'

    if (!title || !description) return

    const nextStandards = [
      ...standards,
      {
        id: makeLocalId('standard'),
        category,
        title,
        description,
      },
    ]
    setStandards(nextStandards)
    writeAcceptanceStandards(nextStandards)
    setNewStandard({ category: '功能', title: '', description: '' })
  }

  function saveMemo() {
    const nextMemo = { ...memo, updatedAt: new Date().toISOString() }
    setMemo(nextMemo)
    writeIndustryMemo(nextMemo)
    setMemoSaved(true)
    window.setTimeout(() => setMemoSaved(false), 1500)
  }

  return (
    <Shell role={role} selectedTemplateId={selectedTemplateId} onLogout={onLogout}>
      <section className="page-heading">
        <div>
          <span className="eyebrow">分析师专属</span>
          <h1>标准制定、插件验收与行业需求备忘录</h1>
          <p>分析师先基于行业需求制定验收标准，再对插件提交物进行评审；通过后进入管理员上架审核队列。</p>
        </div>
        <Link className="secondary-action" to="/dashboard">
          返回工作台
          <ChevronLeft size={17} />
        </Link>
      </section>

      <section className="analyst-layout">
        <div className="workspace-panel analyst-panel standards-panel">
          <div className="panel-head">
            <span className="eyebrow">验收标准</span>
            <h2>插件功能标准库</h2>
          </div>
          <form className="standard-form" onSubmit={addStandard}>
            <label className="field">
              <span>分类</span>
              <input
                onChange={(event) => setNewStandard((current) => ({ ...current, category: event.target.value }))}
                placeholder="例如：功能 / 权限 / 模板"
                value={newStandard.category}
              />
            </label>
            <label className="field">
              <span>标准标题</span>
              <input
                onChange={(event) => setNewStandard((current) => ({ ...current, title: event.target.value }))}
                placeholder="输入一条验收标准"
                value={newStandard.title}
              />
            </label>
            <label className="field">
              <span>说明</span>
              <textarea
                onChange={(event) => setNewStandard((current) => ({ ...current, description: event.target.value }))}
                placeholder="说明该标准面向谁、验收什么、通过条件是什么"
                value={newStandard.description}
              />
            </label>
            <button className="primary-action" type="submit">
              新增标准
              <Plus size={18} />
            </button>
          </form>

          <div className="standard-list">
            {standards.map((standard) => (
              <article className="standard-item" key={standard.id}>
                <span className="status-badge neutral">{standard.category}</span>
                <strong>{standard.title}</strong>
                <p>{standard.description}</p>
              </article>
            ))}
          </div>
        </div>

        <div className="workspace-panel analyst-panel review-panel">
          <div className="panel-head">
            <span className="eyebrow">验收评审</span>
            <h2>插件提交物评审队列</h2>
          </div>
          <div className="review-summary">
            <span>
              <strong>{pendingReviewCount}</strong>
              待验收
            </span>
            <span>
              <strong>{passedReviewCount}</strong>
              已通过
            </span>
            <span>
              <strong>{standards.length}</strong>
              标准项
            </span>
          </div>
          <div className="audit-flow">
            <span>
              <BookOpenCheck size={17} />
              行业需求
            </span>
            <ChevronRight size={17} />
            <span>
              <ClipboardCheck size={17} />
              验收评审
            </span>
            <ChevronRight size={17} />
            <span>
              <ShieldCheck size={17} />
              管理员上架
            </span>
          </div>
          <div className="audit-card-list">
            {pluginReviews.map((item) => (
              <AnalystPluginReviewCard item={item} key={item.id} onUpdatePluginReview={onUpdatePluginReview} />
            ))}
          </div>
        </div>

        <div className="workspace-panel analyst-panel memo-panel">
          <div className="panel-head">
            <span className="eyebrow">行业需求调研</span>
            <h2>Markdown 备忘录</h2>
          </div>
          <div className="memo-layout">
            <div className="memo-editor">
              <label className="field">
                <span>标题</span>
                <input
                  onChange={(event) => setMemo((current) => ({ ...current, title: event.target.value }))}
                  value={memo.title}
                />
              </label>
              <label className="field">
                <span>Markdown 内容</span>
                <textarea
                  className="memo-textarea"
                  onChange={(event) => setMemo((current) => ({ ...current, content: event.target.value }))}
                  value={memo.content}
                />
              </label>
              <button className="primary-action" type="button" onClick={saveMemo}>
                {memoSaved ? '已保存' : '保存备忘录'}
                <Save size={18} />
              </button>
              <small className="memo-time">最近保存：{formatDateTime(memo.updatedAt)}</small>
            </div>
            <MarkdownPreview content={memo.content} title={memo.title} />
          </div>
        </div>
      </section>
    </Shell>
  )
}

function AnalystPluginReviewCard({
  item,
  onUpdatePluginReview,
}: {
  item: PluginReviewItem
  onUpdatePluginReview: PluginReviewAction
}) {
  const [notes, setNotes] = useState(item.analystNotes)
  const canReview =
    item.adminStatus === 'waiting_analyst' ||
    item.adminStatus === 'rejected' ||
    item.analystStatus === 'pending' ||
    item.analystStatus === 'changes_requested'

  function submitReview(status: Extract<AnalystReviewStatus, 'passed' | 'changes_requested'>) {
    const fallback =
      status === 'passed'
        ? '验收通过：提交物满足当前智慧城市插件功能标准，可进入管理员上架审核。'
        : '验收未通过：需插件提交方补充功能、说明或演示材料。'
    onUpdatePluginReview(item.id, (currentItem) => ({
      ...currentItem,
      analystStatus: status,
      analystNotes: notes.trim() || fallback,
      analystUpdatedAt: new Date().toISOString(),
      adminStatus: status === 'passed' ? 'pending' : 'waiting_analyst',
    }))
  }

  return (
    <article className="audit-card">
      <div className="audit-card-head">
        <div>
          <span className="eyebrow">{item.submitter}</span>
          <h3>
            {item.name} <small>v{item.version}</small>
          </h3>
        </div>
        <div className="status-stack">
          <span className={`status-badge analyst-${item.analystStatus}`}>{analystStatusLabel(item.analystStatus)}</span>
          <span className={`status-badge admin-${item.adminStatus}`}>{adminStatusLabel(item.adminStatus)}</span>
        </div>
      </div>

      <p>{item.summary}</p>
      <div className="tag-row">
        {item.capabilities.map((capability) => (
          <span key={capability}>{capability}</span>
        ))}
      </div>

      <label className="field audit-note-field">
        <span>验收意见</span>
        <textarea
          onChange={(event) => setNotes(event.target.value)}
          placeholder="记录行业需求适配、标准项通过情况和修改意见"
          value={notes}
        />
      </label>

      <div className="review-note">
        <strong>管理员审核记录</strong>
        <span>{item.adminNotes || '尚未进入或完成管理员审核'}</span>
        <small>{formatDateTime(item.adminUpdatedAt)}</small>
      </div>

      <div className="action-row">
        <button className="primary-action" disabled={!canReview} type="button" onClick={() => submitReview('passed')}>
          验收通过并提交管理员
          <Send size={18} />
        </button>
        <button
          className="secondary-action danger-action"
          disabled={item.adminStatus === 'listed'}
          type="button"
          onClick={() => submitReview('changes_requested')}
        >
          要求修改
          <XCircle size={17} />
        </button>
        {!canReview && <small className="action-hint">该提交物已进入管理员流程，当前不可重复验收</small>}
      </div>
    </article>
  )
}

function MarkdownPreview({ content, title }: { content: string; title: string }) {
  const lines = content.split('\n')

  return (
    <div className="markdown-preview" aria-label="Markdown 预览">
      <span className="eyebrow">预览</span>
      <h3>{title || '未命名备忘录'}</h3>
      {lines.map((line, index) => {
        const key = `${index}-${line}`
        const trimmed = line.trim()

        if (!trimmed) return <br key={key} />
        if (trimmed.startsWith('## ')) return <h4 key={key}>{trimmed.replace(/^##\s+/, '')}</h4>
        if (trimmed.startsWith('# ')) return <h3 key={key}>{trimmed.replace(/^#\s+/, '')}</h3>
        if (trimmed.startsWith('- [ ] ')) return <p className="markdown-check" key={key}>□ {trimmed.replace(/^- \[ \]\s+/, '')}</p>
        if (trimmed.startsWith('- [x] ') || trimmed.startsWith('- [X] ')) {
          return <p className="markdown-check" key={key}>✓ {trimmed.replace(/^- \[[xX]\]\s+/, '')}</p>
        }
        if (trimmed.startsWith('- ')) return <p className="markdown-bullet" key={key}>{trimmed.replace(/^-\s+/, '')}</p>
        return <p key={key}>{line}</p>
      })}
    </div>
  )
}

function AdminManagementPage({
  adminLogs,
  currentUserId,
  role,
  selectedTemplateId,
  onAddAdminLog,
  onLogout,
}: {
  adminLogs: AdminOperationLog[]
  currentUserId: string
  role: RoleId
  selectedTemplateId: string
  onAddAdminLog: (input: AdminLogInput) => void
  onLogout: () => void
}) {
  const [users, setUsers] = useState<LocalUser[]>(() => readUsers())
  const [notice, setNotice] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  function changeUserRole(userId: string, nextRole: RoleId) {
    const targetUser = users.find((user) => user.id === userId)
    if (!targetUser || targetUser.role === nextRole) return

    const duplicateEmailUser = users.find((user) => {
      return (
        user.id !== userId &&
        user.role === nextRole &&
        normalizeIdentifier(user.email) === normalizeIdentifier(targetUser.email)
      )
    })

    if (duplicateEmailUser) {
      setNotice({
        type: 'error',
        text: `不能把 ${targetUser.username} 改为${roleName(nextRole)}：邮箱 ${targetUser.email} 已经存在同角色用户 ${duplicateEmailUser.username}。此操作会导致同一邮箱拥有两个${roleName(nextRole)}账号，请先删除其中一个重复邮箱用户，再修改权限。`,
      })
      return
    }

    const nextUsers = users.map((user) => (user.id === userId ? { ...user, role: nextRole } : user))
    setUsers(nextUsers)
    writeUsers(nextUsers)
    setNotice({
      type: 'success',
      text: `已将 ${targetUser.username} 从${roleName(targetUser.role)}调整为${roleName(nextRole)}。`,
    })
    onAddAdminLog({
      action: 'role_change',
      target: targetUser.username,
      detail: `${targetUser.email}：${roleName(targetUser.role)} -> ${roleName(nextRole)}`,
    })
  }

  function deleteUser(userId: string) {
    const targetUser = users.find((user) => user.id === userId)
    if (!targetUser) return

    if (targetUser.id === currentUserId) {
      setNotice({
        type: 'error',
        text: '不能删除当前登录的管理员账号，否则会立刻失去后台入口。请先切换到另一个管理员账号后再删除。',
      })
      return
    }

    const nextUsers = users.filter((user) => user.id !== userId)
    setUsers(nextUsers)
    writeUsers(nextUsers)
    setNotice({
      type: 'success',
      text: `已从本地用户库中完全删除 ${targetUser.username}。`,
    })
    onAddAdminLog({
      action: 'delete_user',
      target: targetUser.username,
      detail: `${targetUser.email} / ${roleName(targetUser.role)} 已从本地用户库删除`,
    })
  }

  return (
    <Shell role={role} selectedTemplateId={selectedTemplateId} onLogout={onLogout}>
      <section className="page-heading">
        <div>
          <span className="eyebrow">管理员专属</span>
          <h1>用户权限管理</h1>
          <p>这里用本地用户库模拟后台权限管理：管理员可分配用户角色，也可把用户从本地用户库中完全删除。</p>
        </div>
        <Link className="secondary-action" to="/admin/audit">
          进入插件审核
          <ClipboardList size={17} />
        </Link>
      </section>

      {notice && (
        <div className={`permission-banner ${notice.type}`}>
          {notice.type === 'error' ? <XCircle size={18} /> : <CheckCircle2 size={18} />}
          {notice.text}
        </div>
      )}

      <section className="admin-layout" id="admin-permissions">
        <div className="workspace-panel admin-panel admin-users-panel">
          <div className="panel-head">
            <span className="eyebrow">权限分配</span>
            <h2>本地注册用户角色</h2>
          </div>
          <div className="admin-user-list">
            {users.length ? (
              users.map((user) => (
                <div className="admin-user-row" key={user.id}>
                  <div>
                    <strong>{user.username}</strong>
                    <span>{user.email}</span>
                  </div>
                  <label className="role-select-wrap">
                    <span>角色</span>
                    <select
                      className="role-select"
                      disabled={user.id === currentUserId}
                      value={user.role}
                      onChange={(event) => changeUserRole(user.id, event.target.value as RoleId)}
                    >
                      {roles.map((roleItem) => (
                        <option key={roleItem.id} value={roleItem.id}>
                          {roleItem.name}
                        </option>
                      ))}
                    </select>
                  </label>
                  <button
                    className="delete-user-button"
                    disabled={user.id === currentUserId}
                    type="button"
                    onClick={() => deleteUser(user.id)}
                    title={user.id === currentUserId ? '不能删除当前登录账号' : '删除用户'}
                  >
                    <Trash2 size={17} />
                    <span>删除</span>
                  </button>
                  {user.id === currentUserId && <small>当前登录账号不可在演示中调整自身角色或删除自身</small>}
                </div>
              ))
            ) : (
              <div className="empty-row">暂无注册用户</div>
            )}
          </div>
        </div>

        <div className="workspace-panel admin-panel">
          <div className="panel-head">
            <span className="eyebrow">权限矩阵</span>
            <h2>角色功能限制</h2>
          </div>
          <PermissionMatrix />
        </div>

        <div className="workspace-panel admin-panel">
          <div className="panel-head">
            <span className="eyebrow">系统状态</span>
            <h2>后台运行概览</h2>
          </div>
          <div className="system-metric-grid">
            <span>
              <strong>{users.length}</strong>
              本地用户
            </span>
            <span>
              <strong>3</strong>
              系统角色
            </span>
            <span>
              <strong>ON</strong>
              用户名全局唯一
            </span>
            <span>
              <strong>{adminLogs.length}</strong>
              操作日志
            </span>
          </div>
        </div>

        <div className="workspace-panel admin-panel admin-audit-panel">
          <div className="panel-head">
            <span className="eyebrow">管理员操作日志</span>
            <h2>权限变更与删除记录</h2>
          </div>
          <AdminOperationLogPanel logs={adminLogs} />
        </div>
      </section>
    </Shell>
  )
}

function AdminAuditPage({
  adminLogs,
  pluginReviews,
  role,
  selectedTemplateId,
  onAddAdminLog,
  onLogout,
  onUpdatePluginReview,
}: {
  adminLogs: AdminOperationLog[]
  pluginReviews: PluginReviewItem[]
  role: RoleId
  selectedTemplateId: string
  onAddAdminLog: (input: AdminLogInput) => void
  onLogout: () => void
  onUpdatePluginReview: PluginReviewAction
}) {
  const [selectedPlugin, setSelectedPlugin] = useState<PluginReviewItem | null>(null)
  const pendingAdminCount = pluginReviews.filter((item) => item.adminStatus === 'pending').length
  const analystPendingCount = pluginReviews.filter((item) => item.analystStatus === 'pending').length
  const listedCount = pluginReviews.filter((item) => item.adminStatus === 'listed').length

  return (
    <Shell role={role} selectedTemplateId={selectedTemplateId} onLogout={onLogout}>
      <section className="page-heading">
        <div>
          <span className="eyebrow">管理员专属</span>
          <h1>插件上架审核</h1>
          <p>该页面只处理插件提交物：分析师验收通过后，管理员才能执行上架或驳回，并留下审核日志。</p>
        </div>
        <Link className="secondary-action" to="/admin">
          返回权限管理
          <ChevronLeft size={17} />
        </Link>
      </section>

      <section className="admin-audit-layout">
        <div className="workspace-panel admin-panel">
          <div className="panel-head">
            <span className="eyebrow">审核概览</span>
            <h2>插件审核队列状态</h2>
          </div>
          <div className="system-metric-grid">
            <span>
              <strong>{pendingAdminCount}</strong>
              待上架审核
            </span>
            <span>
              <strong>{analystPendingCount}</strong>
              待分析师验收
            </span>
            <span>
              <strong>{listedCount}</strong>
              已上架插件
            </span>
            <span>
              <strong>{pluginReviews.length}</strong>
              提交物总数
            </span>
          </div>
          <div className="audit-flow">
            <span>
              <ClipboardList size={17} />
              分析师验收
            </span>
            <ChevronRight size={17} />
            <span>
              <ShieldCheck size={17} />
              管理员审核
            </span>
            <ChevronRight size={17} />
            <span>
              <Store size={17} />
              上架开放
            </span>
          </div>
        </div>

        <div className="workspace-panel admin-panel admin-audit-panel">
          <div className="panel-head">
            <span className="eyebrow">插件列表</span>
            <h2>上架审核列表</h2>
          </div>
          <div className="audit-card-list">
            {pluginReviews.map((item) => (
              <AdminPluginReviewCard
                item={item}
                key={item.id}
                onAddAdminLog={onAddAdminLog}
                onOpenDetail={setSelectedPlugin}
                onUpdatePluginReview={onUpdatePluginReview}
              />
            ))}
          </div>
        </div>

        <div className="workspace-panel admin-panel">
          <div className="panel-head">
            <span className="eyebrow">管理员操作日志</span>
            <h2>最近审核与权限操作</h2>
          </div>
          <AdminOperationLogPanel logs={adminLogs} />
        </div>
      </section>

      {selectedPlugin && <PluginDetailDrawer item={selectedPlugin} onClose={() => setSelectedPlugin(null)} />}
    </Shell>
  )
}

function AdminOperationLogPanel({ logs }: { logs: AdminOperationLog[] }) {
  return (
    <div className="admin-log-list">
      {logs.length ? (
        logs.map((log) => (
          <article className="admin-log-item" key={log.id}>
            <span className={`status-badge log-${log.action}`}>{adminLogActionLabel(log.action)}</span>
            <div>
              <strong>{log.target}</strong>
              <p>{log.detail}</p>
              <small>
                {log.operator} · {formatDateTime(log.createdAt)}
              </small>
            </div>
          </article>
        ))
      ) : (
        <div className="empty-row">暂无管理员操作日志</div>
      )}
    </div>
  )
}

function AdminPluginReviewCard({
  item,
  onAddAdminLog,
  onOpenDetail,
  onUpdatePluginReview,
}: {
  item: PluginReviewItem
  onAddAdminLog: (input: AdminLogInput) => void
  onOpenDetail: (item: PluginReviewItem) => void
  onUpdatePluginReview: PluginReviewAction
}) {
  const [notes, setNotes] = useState(item.adminNotes)
  const canDecide = item.analystStatus === 'passed' && item.adminStatus === 'pending'
  const blockedReason =
    item.analystStatus === 'pending'
      ? '需等待行业分析师完成验收'
      : item.analystStatus === 'changes_requested'
        ? '分析师要求插件提交方修改后重新验收'
        : item.adminStatus === 'listed'
          ? '该插件已上架'
          : item.adminStatus === 'rejected'
            ? '该插件已被管理员驳回'
            : ''

  function decide(status: Extract<AdminReviewStatus, 'listed' | 'rejected'>) {
    const fallback = status === 'listed' ? '管理员审核通过，允许上架。' : '管理员驳回上架申请，需补充材料后再提交。'
    onUpdatePluginReview(item.id, (currentItem) => ({
      ...currentItem,
      adminStatus: status,
      adminNotes: notes.trim() || fallback,
      adminUpdatedAt: new Date().toISOString(),
    }))
    onAddAdminLog({
      action: status === 'listed' ? 'plugin_listed' : 'plugin_rejected',
      target: item.name,
      detail: `v${item.version}：${notes.trim() || fallback}`,
    })
  }

  return (
    <article className="audit-card">
      <div className="audit-card-head">
        <div>
          <span className="eyebrow">{item.submitter}</span>
          <h3>
            {item.name} <small>v{item.version}</small>
          </h3>
        </div>
        <div className="status-stack">
          <span className={`status-badge analyst-${item.analystStatus}`}>{analystStatusLabel(item.analystStatus)}</span>
          <span className={`status-badge admin-${item.adminStatus}`}>{adminStatusLabel(item.adminStatus)}</span>
        </div>
      </div>

      <p>{item.summary}</p>
      <div className="tag-row">
        {item.capabilities.map((capability) => (
          <span key={capability}>{capability}</span>
        ))}
      </div>

      <div className="review-note">
        <strong>分析师验收意见</strong>
        <span>{item.analystNotes || '尚未填写验收意见'}</span>
        <small>{formatDateTime(item.analystUpdatedAt)}</small>
      </div>

      <label className="field audit-note-field">
        <span>管理员审核意见</span>
        <textarea
          onChange={(event) => setNotes(event.target.value)}
          placeholder="记录上架依据、驳回原因或后续要求"
          value={notes}
        />
      </label>

      <div className="action-row">
        <button className="primary-action" disabled={!canDecide} type="button" onClick={() => decide('listed')}>
          通过上架
          <CheckCircle2 size={18} />
        </button>
        <button className="secondary-action danger-action" disabled={!canDecide} type="button" onClick={() => decide('rejected')}>
          驳回
          <XCircle size={17} />
        </button>
        <button className="secondary-action" type="button" onClick={() => onOpenDetail(item)}>
          查看详情
          <ExternalLink size={17} />
        </button>
        {!canDecide && blockedReason && <small className="action-hint">{blockedReason}</small>}
      </div>
    </article>
  )
}

function PluginDetailDrawer({ item, onClose }: { item: PluginReviewItem; onClose: () => void }) {
  return (
    <div className="modal-backdrop drawer-backdrop" role="presentation" onClick={onClose}>
      <aside className="plugin-detail-drawer" role="dialog" aria-modal="true" onClick={(event) => event.stopPropagation()}>
        <div className="drawer-head">
          <div>
            <span className="eyebrow">插件详情</span>
            <h2>{item.name}</h2>
            <p>提交方：{item.submitter} · 版本 v{item.version}</p>
          </div>
          <button className="icon-action drawer-close" type="button" onClick={onClose} aria-label="关闭详情">
            <XCircle size={18} />
          </button>
        </div>

        <div className="status-stack drawer-status">
          <span className={`status-badge analyst-${item.analystStatus}`}>{analystStatusLabel(item.analystStatus)}</span>
          <span className={`status-badge admin-${item.adminStatus}`}>{adminStatusLabel(item.adminStatus)}</span>
        </div>

        <section className="drawer-section">
          <span className="eyebrow">提交说明</span>
          <p>{item.summary}</p>
        </section>

        <section className="drawer-section">
          <span className="eyebrow">模拟提交物</span>
          <ul className="mock-file-list">
            <li>plugin-manifest.json</li>
            <li>{item.id}.zip</li>
            <li>验收说明.md</li>
            <li>演示截图/视频占位</li>
          </ul>
        </section>

        <section className="drawer-section">
          <span className="eyebrow">能力范围</span>
          <div className="tag-row">
            {item.capabilities.map((capability) => (
              <span key={capability}>{capability}</span>
            ))}
          </div>
        </section>

        <section className="drawer-section">
          <span className="eyebrow">流程记录</span>
          <div className="review-note">
            <strong>分析师验收意见</strong>
            <span>{item.analystNotes || '尚未填写验收意见'}</span>
            <small>{formatDateTime(item.analystUpdatedAt)}</small>
          </div>
          <div className="review-note">
            <strong>管理员审核意见</strong>
            <span>{item.adminNotes || '尚未填写审核意见'}</span>
            <small>{formatDateTime(item.adminUpdatedAt)}</small>
          </div>
        </section>
      </aside>
    </div>
  )
}

function PermissionMatrix() {
  return (
    <div className="permission-matrix" aria-label="角色权限矩阵">
      <div className="permission-matrix-head">
        <span>角色</span>
        {permissionRules.map((rule) => (
          <span key={rule.key}>{rule.title}</span>
        ))}
      </div>
      {roles.map((roleItem) => (
        <div className="permission-matrix-row" key={roleItem.id}>
          <strong>{roleItem.name}</strong>
          {permissionRules.map((rule) => {
            const enabled = rolePermissions[roleItem.id][rule.key]

            return (
              <span
                className={`permission-chip ${enabled ? 'enabled' : 'blocked'}`}
                key={rule.key}
                title={rule.description}
              >
                {enabled ? '允许' : '限制'}
              </span>
            )
          })}
        </div>
      ))}
    </div>
  )
}

function TemplateCard({
  role,
  template,
  selected,
  onSelectTemplate,
}: {
  role: RoleId
  template: CityTemplate
  selected: boolean
  onSelectTemplate: (id: string) => void
}) {
  const canApply = canApplyTemplate(role)

  return (
    <article className={`template-card ${selected ? 'active' : ''}`}>
      <div className="template-preview">
        <img className="preview-road" src={template.preview.road} alt="" />
        <img className="preview-tree" src={template.preview.tree} alt="" />
        <img className="preview-bench" src={template.preview.bench} alt="" />
        <span>模板 {template.id}</span>
      </div>
      <div className="template-card-body">
        <div>
          <span className="eyebrow">{template.sceneType}</span>
          <h2>{template.name}</h2>
          <p>{template.description}</p>
        </div>
        <div className="compact-params">
          <span>Tree {template.tree_type}</span>
          <span>Road {template.road_texture}</span>
          <span>Bench {template.bench_type}</span>
        </div>
        <div className="compact-params">
          <span>车流 {template.scene.traffic}</span>
          <span>人群 {template.scene.pedestrian}</span>
          <span>生态 {template.scene.ecology}</span>
        </div>
        <div className="template-actions">
          <button
            disabled={selected || !canApply}
            type="button"
            onClick={() => {
              if (canApply && !selected) onSelectTemplate(template.id)
            }}
          >
            {selected ? '已选择' : canApply ? '使用模板' : '仅可查看'}
          </button>
          <Link to={`/templates/${template.id}`}>查看详情</Link>
        </div>
      </div>
    </article>
  )
}

function FeatureCard({
  icon,
  title,
  text,
  link,
  locked = false,
  reason,
}: {
  icon: ReactNode
  title: string
  text: string
  link: string
  locked?: boolean
  reason?: string
}) {
  if (locked) {
    return (
      <div className="feature-card locked" aria-disabled="true">
        <span>{icon}</span>
        <strong>{title}</strong>
        <p>{text}</p>
        {reason && <small>{reason}</small>}
      </div>
    )
  }

  return (
    <Link className="feature-card" to={link}>
      <span>{icon}</span>
      <strong>{title}</strong>
      <p>{text}</p>
    </Link>
  )
}

function PermissionList({ role }: { role: RoleId }) {
  const items = {
    modeler: [
      ['模板商城', '可选择并应用城市模板'],
      ['Blender 入口', '可模拟进入插件系统'],
      ['插件参数', '可查看模板对应资产字段'],
    ],
    admin: [
      ['用户权限', '可查看不同角色功能范围'],
      ['插件审核', '模拟插件上架与审核流程'],
      ['系统状态', '查看当前 Demo 模块状态'],
    ],
    analyst: [
      ['行业需求', '查看模板适配场景'],
      ['验收评审', '核对功能完整度与演示链路'],
      ['指标记录', '追踪模板参数与测试结果'],
    ],
  }[role]

  return (
    <ul className="permission-list">
      {items.map(([title, text]) => (
        <li key={title}>
          <ShieldCheck size={18} />
          <div>
            <strong>{title}</strong>
            <span>{text}</span>
          </div>
        </li>
      ))}
    </ul>
  )
}

function ParamRow({ label, value, asset }: { label: string; value: number; asset: string }) {
  return (
    <div className="param-row">
      <span>{label}</span>
      <strong>{value}</strong>
      <code>{asset}</code>
    </div>
  )
}

function roleIcon(id: RoleId) {
  if (id === 'admin') return <UserRoundCog size={20} />
  if (id === 'analyst') return <BarChart3 size={20} />
  return <Trees size={20} />
}

function roleLabel(id: RoleId) {
  if (id === 'admin') return '管理员视图'
  if (id === 'analyst') return '分析师视图'
  return '建模师视图'
}

export default App
