const i18n = {
  zh: {
    ui: {
      appTitleShort: "NexoRig", appSubtitle: "钻完井管理平台", pageTitle: "钻井日报填报工作台", drillingPageKicker: "DRILLING DAILY REPORT", completionPageTitle: "完井日报填报工作台", completionPageKicker: "COMPLETION DAILY REPORT", workoverPageTitle: "修井日报填报工作台", workoverPageKicker: "WORKOVER DAILY REPORT", movePageTitle: "搬迁日报填报工作台", movePageKicker: "RIG MOVE DAILY REPORT",
      systemAdmin: "系统后台",
      menuDailyParsing: "日报管理", menuDrillingDaily: "钻井日报", menuCompletionDaily: "完井日报", menuWorkoverDaily: "修井日报", menuMoveDaily: "搬迁日报",
      menuProductionReport: "生产分析", menuRigProductionSummary: "时效分析", menuProductionDetailReport: "生产报表", menuWellNptConfirm: "NPT统计", menuRigNptRanking: "NPT确认",
      menuHsse: "HSSE管理", menuHsseCollection: "HSSE填报", menuHsseDashboard: "安全驾驶舱", menuDailySafetySummary: "HSSE报表", menuPeriodSafetyReport: "HSSE报表",
      descDrillingDaily: "支持上传钻井或搬迁 PDF 日报，解析井基础信息及 Operation 内容，并进入钻井日报填报页面。",
      descCompletionDaily: "上传完井日报 PDF，解析基础信息、Operation、库存和射孔区间，预览后可二次编辑。", descWorkoverDaily: "上传修井日报 PDF，解析 WO 信息、Operation、库存、安全备注和射孔区间，预览后可二次编辑。", descMoveDaily: "上传搬迁日报 PDF，解析 Operation、重型设备和载荷清单，预览后可二次编辑。",
      descRigProductionSummary: "基于日报解析数据，按井队、日报类型和月份展示生产作业时效。", descProductionDetailReport: "按项目周期、井队和井号归属查询生产时效明细。", descWellNptConfirm: "统计各钻井队历史作业 NPT 时长、占比及排名，支持井队对比分析。", descRigNptRanking: "确认每口井 P、SC、NPT 时长及具体情况，并支持后续按时效确认表修正。",
      descHsseCollection: "按井、按队伍记录每日安全生产信息，包括人的不安全行为、物的不安全状态、不放心人员、生产异常和公共安全事件。", descHsseDashboard: "集中展示全油田各队伍 HSSE 关键指标、异常情况和跟踪总览。", descDailySafetySummary: "基于 HSSE 采集数据生成安全报表。", descPeriodSafetyReport: "合并日报统计与周月报，基于 HSSE 数据生成安全报表，支持阶段性分析和汇报。",
      moduleStatusPlanned: "功能规划", moduleComingSoon: "功能待开发", moduleCurrent: "当前菜单", moduleComingSoonDesc: "该功能已按需求菜单预留入口，后续可在此接入数据采集、统计报表或数据分析页面。",
      navBasic: "基础信息", navSummary: "作业摘要", navWellControl: "施工参数", navSurvey: "测斜数据", navMud: "泥浆数据", navBitBha: "钻头与 BHA", navOperations: "作业明细", navCosts: "漏失与库存", navIncidents: "事故与备注",
      importPdf: "导入 PDF 日报", originalReport: "原文", translateChinese: "翻译为中文", translationRunning: "正在切换日报语言...", translationRunningShort: "翻译中", translationReady: "日报语言已切换。", translationFailed: "翻译数据暂不可用，请确认本地大模型服务或后台翻译任务状态。", translationPreviewNotice: "当前显示数据库译文，只读展示；切回原文可编辑原始日报。", translationTitle: "中英西混合日报翻译", translationOriginal: "原文", translationLanguage: "语言", translationChinese: "中文翻译", translationPath: "字段", translationTerms: "术语替换", translationWarnings: "告警", translationEmpty: "暂无可显示翻译结果", saveDatabase: "保存", downloadDatabase: "数据库状态", backRecords: "返回记录", databaseSaved: "已保存到 MySQL 数据库。", databaseSaveFailed: "保存 MySQL 数据库失败。", recordLoadFailed: "打开日报详情失败。", databaseRecord: "数据库记录", sourceFileEmpty: "未上传文件",
      uploadDashboardTitle: "日报管理 Dashboard", wellSelection: "井选择", searchWell: "搜索井号", reportCalendar: "日报日历", uploadRecords: "上传文件记录", allTypes: "全部类型", allStatuses: "全部状态", exportList: "导出", preview: "查看", download: "下载", detail: "详情", uploaded: "已完成", queued: "排队中", parsing: "解析中", parseDoneStatus: "解析完成", failed: "失败", warningStatus: "有告警", pending: "待补传", translationPendingStatus: "待翻译", translationQueuedStatus: "排队中", translationRunningStatus: "翻译中", translationDoneStatus: "翻译完成", translationNotRequiredStatus: "无需翻译", translationFailedStatus: "翻译失败", translationNotReady: "译文未完成，完成后才能切换语言。", noRecords: "暂无上传记录", addWell: "添加新井", selectedWell: "当前井", monthlyUploaded: "本月已上传", monthlyPending: "待补传", reportKinds: "日报类型", monthlyUploaders: "本月上传人", calendarHint: "提示：点击已有完成记录的日期可直接预览", recordsCount: "条记录", uploader: "上传人", uploadTime: "上传时间", fileName: "文件名称", status: "状态", operation: "操作", date: "日期", well: "井号", reportType: "日报类型", page: "页", prevPage: "上一页", nextPage: "下一页", sourcePdfMissing: "源文件未保存，请重新导入该日报后查看。", sourcePdfTitle: "源文件PDF", sortFirstUpload: "初传", sortLastUpload: "最近", sortWellName: "井号", deleteFailedImport: "删除", failedImportDeleted: "失败的导入记录已删除。",
      metricCompletion: "完成度", metricIssues: "校验问题", metricHours: "作业合计", metricProgress: "进尺", metricIntervals: "射孔区间", metricWellDate: "井号 / 日期", metricDailyHours: "当日作业时长", metricNptHours: "NPT时长", metricDataCompleteness: "数据完整性",
      metricWorkDays: "作业天数", metricNptShare: "NPT时长 / 占比", metricPScShare: "P / SC工况占比", metricReportCompleteness: "日报完整性", metricMoveDrillingDays: "搬迁 / 钻井", noWells: "暂无已识别井号",
      analyticsKicker: "数据看板", analyticsProductionScope: "基于已保存到 MySQL 的日报解析数据", analyticsNptScope: "P按日报原值直接生效；SC/NPT仅在NPT确认提交后进入正式统计", search: "查询", reset: "重置", wellborePlaceholder: "请输入井号",
      chartRigHours: "各井队累计NPT排名", chartOperationMix: "作业时效构成", chartMonthlyHours: "单井作业甘特图", chartNptRig: "各井队NPT对比 (h)", chartNptReason: "作业代码 / 作业子项分布", chartNptWell: "各井NPT排行", chartNptMonthly: "月度NPT趋势 (h)", productionDetailTitle: "生产报表明细", nptDetailTitle: "NPT统计明细", analyticsRowHint: "点击行可打开日报详情", productionReportRowHint: "点击井号新开日报首页并选中该井", nptRowHint: "按日报作业代码 / 作业子项原文汇总，点击行可追溯日报",
      kpiRigCount: "井队数", kpiNptRigCount: "NPT井队数", kpiWellCount: "涉及井数", kpiTotalHours: "总作业时长", kpiTotalNpt: "总NPT", kpiReportCompleteness: "日报完整性", kpiNptEvents: "NPT事件数", analyticsDefaultCaption: "基于已入库日报", analyticsNptCaption: "按作业代码 / 作业子项汇总", analyticsCompletenessCaption: "缺失 {missing} 天 / 告警 {warning} 天", noAnalyticsData: "暂无可统计数据", noExportData: "暂无可导出数据", normalStatus: "正常", reasonMissing: "未填写作业代码 / 作业子项",
      allRigs: "全部井队", allProjects: "全部项目", allReportTypes: "全部类型", allReasons: "全部分类", scopeByRig: "按井队", scopeByProject: "按项目", productionNptCaption: "累计 NPT 时长（h）", nptHoursCaption: "NPT 时长（h）", nptDailyShareCaption: "日均 NPT 占比（%）", nptNotePlaceholder: "请输入备注内容（选填）", opCodeSub: "作业代码 / 子项", opCode: "作业代码", opSub: "作业子项", category: "分类", tableProject: "项目", tableContractProject: "合同(项目)", tableRig: "井队", tableWell: "井号", tableReportType: "日报类型", tableStartDate: "开工时间", tableEndDate: "完工时间", tableMoveDate: "搬迁日期", tableDrillingStartDate: "开钻日期", tableDrillingFinishDate: "完钻日期", tableCompletionDate: "完井日期", tableWorkoverDate: "修井日期", tableDrillingHours: "钻井(h)", tableCompletionHours: "完井(h)", tableWorkoverHours: "修井(h)", tableMoveHours: "搬迁(h)", tableNptHours: "NPT(h)", tableRemarks: "备注", tableDate: "日期", tableOperationDetails: "作业详情",
      sectionBasic: "基础信息", sectionSummary: "作业摘要", sectionWellControl: "施工参数", sectionSurvey: "测斜数据（最近 6 条）", sectionMud: "泥浆数据", sectionBitBha: "钻头与 BHA", sectionOperations: "作业明细", sectionFluidLossInventory: "漏失情况与库存", sectionInventory: "库存", sectionIncidents: "事故与备注", sectionPersonnel: "人员信息", sectionPerforationIntervals: "射孔区间",
      noteBasic: "对应 PDF 顶部日报抬头和井基本信息", noteSummary: "当前作业、24 小时总结、下一步计划", noteWellControl: "套管、井控试压、泵压、钻柱重量和扭矩", noteIncidents: "HSE 状态、同步作业和其他说明",
      completionNoteBasic: "对应完井 PDF 顶部日报抬头、AFP 和井基本信息", completionNotePersonnel: "Supervisor、Engineer、Geologist 与现场总人数", completionNoteRemarks: "安全备注、固控说明和其他现场备注", workoverNoteBasic: "对应修井 PDF 顶部日报抬头、AFP 和井基本信息", workoverNotePersonnel: "Supervisor、Engineer、Geologist 与现场总人数", workoverNoteRemarks: "安全备注、固控说明和其他现场备注", moveNoteBasic: "对应搬迁 PDF 顶部日报抬头、AFE 和井队信息", moveNoteRemarks: "其他现场备注原文",
      rulesTitle: "基础条件限制规则", liveValidation: "实时校验",
      uploadedDays: "已上传", daysUnit: "天", missingDate: "缺失日期",
      prevMonth: "上一月", nextMonth: "下一月", savedWarnings: "保存时校验",
      noIssues: "当前没有校验问题。", pdfImporting: "正在解析 PDF 日报...", pdfImported: "PDF 日报已解析并填充到界面。", pdfImportFailed: "PDF 解析失败，请检查文件格式或模板。",
      thMd: "测量深度 MD (ft)", thIncl: "井斜角 (deg)", thAzi: "方位角 (deg)", thTvd: "垂深 TVD (ft)", thVse: "垂直剖面 VSE (ft)", thNs: "南北位移 N/-S (ft)", thEw: "东西位移 E/-W (ft)", thDls: "狗腿度 DLS (deg/100ft)", thBuild: "造斜率 (deg/100ft)", thComponent: "组件", thOd: "外径 OD (in)", thId: "内径 ID (in)", thJts: "根数", thLength: "长度 (ft)", thFrom: "开始 (HH:MM)", thTo: "结束 (HH:MM)", thHrs: "时长 (h)", thOpCode: "作业代码", thOpSub: "作业子项", thType: "类型", thOperationDetails: "作业详情", thInjectedVolumeBbl: "注入体积 (bbl)", thReturnedVolumeBbl: "返出体积 (bbl)", thBulk: "库存物料", thQtyStart: "期初数量", thQtyUsed: "使用数量", thQtyEnd: "期末数量", thFormation: "地层", thTopMd: "顶部 MD (ft)", thBaseMd: "底部 MD (ft)", thDensity: "孔密 (spf)", thCharges: "射孔弹数", thPhase: "相位 (deg)", thPenetration: "穿透深度 (in)", thDiameter: "孔径 (in)", thDate: "日期", thStatus: "状态", thComments: "备注", thLocation: "地点", thEquipment: "设备", thPlate: "车牌", thEntryDate: "录入日期", thEntryTime: "录入时间", thGuide: "引导员", thCargo: "货物", thTrip: "车次"
    },
    fields: {
      event: "事件", reportDate: "日期", project: "项目", date_from: "日期起", date_to: "日期止", scope_type: "筛选方式", scope_value: "井队", nptConfirmNote: "备注说明", report_type: "日报类型", reason: "作业代码 / 子项", nptWellbore: "井号", nptRig: "井队", nptStatus: "确认状态", reportNo: "报告编号", wellbore: "井号", rig: "井队", primaryReason: "主要原因", afeNumber: "AFE 编号", refDatum: "参考基准 (ft)", todayMd: "当日 MD (ft)", prevMd: "前日 MD (ft)", progress: "进尺 (ft)", rotHrsToday: "当日旋转时长 (h)",
      currentOps: "当前作业", summary24h: "24 小时总结", forecast24h: "未来 24 小时计划", lastCasing: "上一层套管", lastCasingSize: "上一层套管尺寸 (in)", lastCasingDepth: "上一层套管深度 (ft)", nextCasing: "下一层套管", nextCasingSize: "下一层套管尺寸 (in)", nextCasingDepth: "下一层套管深度 (ft)", formTestType: "地层测试类型", formTestEmw: "地层测试 EMW (ppg)", lastBopPressTest: "最近一次 BOP 试压日期", pumpRate: "泵排量 (gpm)", pumpPress: "泵压 (psi)", stringWeightUp: "钻柱上提重量 (kip)", stringWeightDown: "钻柱下放重量 (kip)", stringWeightUpDown: "钻柱上提/下放重量", torqueOffBottom: "离底扭矩 (ft-lbf)", torqueOnBottom: "井底扭矩 (ft-lbf)",
      mudEngineer: "泥浆工程师", sampleFrom: "取样位置", mudType: "泥浆类型", mudTimeMd: "时间 / MD", mudTime: "泥浆取样时间", mudMd: "泥浆取样 MD (ft)", mudDensity: "密度 (ppg)", mudTemperature: "泥浆温度 (°F)", rheologyTemp: "流变测试温度 (°F)", viscosity: "黏度 (sec/qt)", pvYp: "PV / YP", pv: "塑性黏度 PV (cP)", yp: "动切力 YP (lb/100ft²)", gels: "静切力 10s/10m/30m (lb/100ft²)", gel10s: "10 秒静切力 (lb/100ft²)", gel10m: "10 分钟静切力 (lb/100ft²)", gel30m: "30 分钟静切力 (lb/100ft²)", apiWl: "API 失水 (cc/30min)", oilWater: "油 / 水", oilPercent: "含油量 (%)", waterPercent: "含水量 (%)", sand: "含砂量 (%)", ecd: "当量循环密度 ECD (ppg)", mudComments: "泥浆备注",
      bitNo: "钻头序号", bitSize: "钻头尺寸 (in)", bitManufacturer: "制造商", bitSerial: "钻头序列号", bitWearIodl: "钻头磨损 I-O-D-L", bitWearBgor: "钻头磨损 B-G-O-R", bhaNo: "BHA 编号", bhaMdIn: "入井 MD (ft)", bhaMdOut: "出井 MD (ft)", bhaTotalLength: "总长度 (ft)", safetyIncident: "是否发生安全事故？", environmentIncident: "是否发生环境事故？", daysSinceRi: "距上次 RI 天数", daysSinceLta: "距上次 LTA 天数", incidentComments: "事故说明", otherRemarks: "其他备注",
      description: "说明", operationStartDate: "作业开始日期", workoverNo: "修井编号", afeCost: "AFP 成本 (USD)", dailyCost: "当日成本 (USD)", cumulativeCost: "累计成本 (USD)", supervisor1: "监督 1", supervisor2: "监督 2", engineer: "工程师", pamEngineer: "PAM 工程师", geologist: "地质师", totalPersonnel: "现场总人数", safetyComments: "安全备注", groundElev: "地面海拔 (ft)", afeMdDays: "AFE 设计井深/天数 (ft/d)"
    },
    rules: [
      "<strong>必填：</strong>Date、Report No、Wellbore、Rig、Current Ops、24-Hr Summary、Mud Type、Today's MD。",
      "<strong>日期：</strong>日报日期不能晚于当前日期。",
      "<strong>井深：</strong>Today's MD 必须大于等于 Prev MD，Progress 应等于两者差值，允许 0.5 ft 误差。",
      "<strong>工时：</strong>同一日报类型、同一井仅最早日和最晚日校验 Operations Hrs 合计 24.00 小时，允许 0.05 小时误差。",
      "<strong>作业行：</strong>From、To、Hrs、Op Code、Type、Operation Details 至少应完整填写；Type 只能是附录中的 P、SC 或 NPT。",
      "<strong>测斜：</strong>Survey MD 不能大于 Today's MD，Incl 范围 0 到 180，DLS 不能为负。",
      "<strong>泥浆：</strong>Density 推荐 6 到 20 ppg，Sand 推荐不超过 10%。",
      "<strong>设备：</strong>BHA 组件 OD、ID、Jts、Length 不能为负，OD 应大于等于 ID。",
      "<strong>HSE：</strong>Safety 或 Environmental Incident 为 Y 时，Incident Comments 必填。",
      "<strong>漏失与库存：</strong>漏失体积和库存数量按数字解析并结构化回显，不参与工时校验。"
    ],
    completionRules: [
      "<strong>必填：</strong>Date、Report No、Wellbore、Rig、Current Ops、24-Hr Summary、24-Hr Forecast。",
      "<strong>日期：</strong>日报日期不能晚于当前日期，Operation Start 不能晚于日报日期。",
      "<strong>工时：</strong>同一日报类型、同一井仅最早日和最晚日校验 Operations Hrs 合计 24.00 小时，允许 0.05 小时误差。",
      "<strong>作业行：</strong>From、To、Hrs、Op Code、Type、Operation Details 建议完整填写；Type 只能是 P、SC 或 NPT。",
      "<strong>射孔区间：</strong>Base MD 应大于等于 Top MD，Length 不能为负。",
      "<strong>库存：</strong>库存数量按数字解析并结构化回显，不参与工时校验。"
    ],
    workoverRules: [
      "<strong>必填：</strong>Date、Report No、Wellbore、Rig、Current Ops、24-Hr Summary、24-Hr Forecast。",
      "<strong>日期：</strong>日报日期不能晚于当前日期，Operation Start 不能晚于日报日期。",
      "<strong>工时：</strong>同一日报类型、同一井仅最早日和最晚日校验 Operations Hrs 合计 24.00 小时，允许 0.05 小时误差。",
      "<strong>作业行：</strong>From、To、Hrs、Op Code、Type、Operation Details 建议完整填写；Type 只能是 P、SC 或 NPT。",
      "<strong>射孔区间：</strong>Base MD 应大于等于 Top MD，Length 不能为负。",
      "<strong>库存：</strong>库存数量按数字解析并结构化回显，不参与工时校验。"
    ],
    moveRules: [
      "<strong>必填：</strong>Date、Report No、Wellbore、Rig、Current Ops、24-Hr Summary、24-Hr Forecast。",
      "<strong>工时：</strong>同一日报类型、同一井仅最早日和最晚日校验 Operations Hrs 合计 24.00 小时，允许 0.05 小时误差。",
      "<strong>作业行：</strong>From、To、Hrs、Op Code、Type、Operation Details 建议完整填写；Type 只能是 P、SC 或 NPT。",
      "<strong>备注：</strong>Other Remarks 可保留 PDF 末页原文，便于人工复核。"
    ],
    msg: {
      required: "{field} 为必填项。", futureDate: "日报日期不能晚于当前日期。", operationStartDate: "Operation Start 不能晚于日报日期。", mdOrder: "Today's MD 必须大于等于 Prev MD。", progressMismatch: "Progress 与井深差值不一致，当前差值为 {value} ft。", operationMissingTable: "作业明细不能为空。", operationHours: "Operations 工时合计应为 24.00 h，当前为 {value} h。", operationMissing: "作业明细第 {row} 行缺少 {field}。", operationTimeMismatch: "作业明细第 {row} 行 From/To 对应时长为 {value} h，与 Hrs 不一致。", operationType: "作业明细第 {row} 行 Type 为空或不是 P/SC/NPT，请复核。", completionOperationType: "完井作业第 {row} 行 Type 为空或不是 P/SC/NPT，请复核。", workoverOperationType: "修井作业第 {row} 行 Type 为空或不是 P/SC/NPT，请复核。", moveOperationType: "搬迁作业第 {row} 行 Type 为空或不是 P/SC/NPT，请复核。", operationHourRange: "作业明细第 {row} 行 Hrs 必须在 0 到 24 之间。", intervalDepth: "射孔区间第 {row} 行 Base MD 应大于等于 Top MD。", intervalLength: "射孔区间第 {row} 行 Length 不能为负。", surveyMd: "测斜第 {row} 行 MD 不能大于 Today's MD。", surveyIncl: "测斜第 {row} 行 Incl 应在 0 到 180 之间。", surveyDls: "测斜第 {row} 行 DLS 不能为负。", mudDensity: "泥浆 Density 推荐范围为 6 到 20 ppg。", sand: "泥浆 Sand 超过 10%，请复核。", bhaOdId: "BHA 第 {row} 行 OD 应大于等于 ID。", bhaNegative: "BHA 第 {row} 行存在负数。", negativeValue: "第 {row} 行 {field} 不能为负。", incidentRequired: "发生 Safety 或 Environmental Incident 时，Incident Comments 必填。"
    }
  },
  en: {
    ui: {
      appTitleShort: "NexoRig", appSubtitle: "Drilling Intelligence", pageTitle: "Drilling Daily Report Workspace", drillingPageKicker: "DRILLING DAILY REPORT", completionPageTitle: "Completion Daily Report Workspace", completionPageKicker: "COMPLETION DAILY REPORT", workoverPageTitle: "Workover Daily Report Workspace", workoverPageKicker: "WORKOVER DAILY REPORT",
      systemAdmin: "System Admin",
      menuDailyParsing: "Daily Reports", menuDrillingDaily: "Drilling Daily", menuCompletionDaily: "Completion Daily", menuWorkoverDaily: "Workover Daily", menuMoveDaily: "Move Daily",
      menuProductionReport: "Production Analysis", menuRigProductionSummary: "Time Analysis", menuProductionDetailReport: "Production Report", menuWellNptConfirm: "NPT Stats", menuRigNptRanking: "NPT Confirmation",
      menuHsse: "HSSE Management", menuHsseCollection: "HSSE Entry", menuHsseDashboard: "Safety Cockpit", menuDailySafetySummary: "HSSE Reports", menuPeriodSafetyReport: "HSSE Reports",
      descDrillingDaily: "Upload drilling or rig move PDF daily reports, parse well basics and Operation content, then edit the drilling daily report.",
      descCompletionDaily: "Upload completion daily PDFs, parse basics, operations, bulks, and perforated intervals, then preview and edit.", descWorkoverDaily: "Upload workover daily PDFs, parse WO information, operations, bulks, safety comments, and perforated intervals, then preview and edit.", descMoveDaily: "Reserved entry for rig move daily PDF parsing and structured entry.",
      descRigProductionSummary: "Show production time by rig, report type, and month from parsed daily reports.", descProductionDetailReport: "Query production time details by project period, rig, and well assignment.", descWellNptConfirm: "Rank drilling rigs by historical NPT duration and share for comparison analysis.", descRigNptRanking: "Confirm P, SC, and NPT hours by well, with later updates from time-class confirmation sheets.",
      descHsseCollection: "Capture daily HSSE information by well and team, including unsafe acts, unsafe conditions, personnel concerns, production exceptions, and public security events.", descHsseDashboard: "Show field-wide HSSE KPIs, exceptions, tracking, and overview by team.", descDailySafetySummary: "Generate safety reports from HSSE collection data.", descPeriodSafetyReport: "Combine daily safety stats with weekly and monthly reporting into one safety report entry.",
      moduleStatusPlanned: "Planned Feature", moduleComingSoon: "Feature Reserved", moduleCurrent: "Current Menu", moduleComingSoonDesc: "This menu entry is reserved from the requirement list. Data entry, reporting, or analytics pages can be connected here later.",
      navBasic: "Basic Info", navSummary: "Operations Summary", navWellControl: "Operational Parameters", navSurvey: "Survey Data", navMud: "Mud Data", navBitBha: "Bit & BHA", navOperations: "Operations Log", navCosts: "Fluid Loss & Inventory", navIncidents: "Incidents & Remarks",
      importPdf: "Import PDF Report", originalReport: "Original", translateChinese: "Translate to Chinese", translationRunning: "Switching report language...", translationRunningShort: "Translating", translationReady: "Report language switched.", translationFailed: "Translation data is not available. Check the local model service or translation task status.", translationPreviewNotice: "Database translation is shown read-only. Switch back to Original to edit the source report.", translationTitle: "Mixed EN/ES Drilling Report Translation", translationOriginal: "Original", translationLanguage: "Language", translationChinese: "Chinese", translationPath: "Field", translationTerms: "Terms", translationWarnings: "Warnings", translationEmpty: "No translation results to show", saveDatabase: "Save", downloadDatabase: "Database Status", backRecords: "Back to Records", databaseSaved: "Saved to MySQL.", databaseSaveFailed: "Failed to save to MySQL.", recordLoadFailed: "Failed to open report detail.", databaseRecord: "Database record", sourceFileEmpty: "No file uploaded",
      uploadDashboardTitle: "Daily Report Dashboard", wellSelection: "Well Selection", searchWell: "Search well", reportCalendar: "Report Calendar", uploadRecords: "Upload Records", allTypes: "All Types", allStatuses: "All Statuses", exportList: "Export", preview: "View", download: "Download", detail: "Details", uploaded: "Complete", queued: "Queued", parsing: "Parsing", parseDoneStatus: "Parsing complete", failed: "Failed", warningStatus: "Warnings", pending: "Pending", translationQueuedStatus: "Translation queued", translationRunningStatus: "Translating", translationDoneStatus: "Translation done", translationFailedStatus: "Translation failed", translationNotReady: "Translation is not complete yet. Language switching is available after completion.", noRecords: "No upload records", addWell: "Add Well", selectedWell: "Selected Well", monthlyUploaded: "Uploaded This Month", monthlyPending: "Pending Uploads", reportKinds: "Report Types", monthlyUploaders: "Uploaders This Month", calendarHint: "Tip: click a completed calendar date to preview it", recordsCount: "records", uploader: "Uploader", uploadTime: "Upload Time", fileName: "File Name", status: "Status", operation: "Actions", date: "Date", well: "Well", reportType: "Report Type", page: "Page", prevPage: "Previous", nextPage: "Next", sourcePdfMissing: "The source PDF was not saved. Re-import this report to view it.", sourcePdfTitle: "Source PDF", sortFirstUpload: "First", sortLastUpload: "Latest", sortWellName: "Well", deleteFailedImport: "Delete", failedImportDeleted: "Failed import record deleted.",
      metricCompletion: "Completion", metricIssues: "Validation Issues", metricHours: "Operation Total", metricProgress: "Progress", metricIntervals: "Intervals", metricWellDate: "Well / Date", metricDailyHours: "Daily Hours", metricNptHours: "NPT Hours", metricDataCompleteness: "Data Completeness",
      metricWorkDays: "Work Days", metricNptShare: "NPT Hours / Share", metricPScShare: "P / SC Share", metricReportCompleteness: "Report Completeness", metricMoveDrillingDays: "Move / Drilling", noWells: "No identified wells",
      analyticsKicker: "Analytics", analyticsProductionScope: "Based on daily report data saved in MySQL", analyticsNptScope: "P is effective from the source report; SC/NPT enters official statistics only after NPT confirmation", search: "Search", reset: "Reset", wellborePlaceholder: "Enter well",
      chartRigHours: "Rig Cumulative NPT Ranking", chartOperationMix: "Operation Mix", chartMonthlyHours: "Well Operation Gantt", chartNptRig: "Rig NPT Comparison (h)", chartNptReason: "OP Code / OP Sub Distribution", chartNptWell: "Well NPT Ranking", chartNptMonthly: "Monthly NPT Trend (h)", productionDetailTitle: "Production Report Details", nptDetailTitle: "NPT Details", analyticsRowHint: "Click a row to open the report details", productionReportRowHint: "Click a well to open its report homepage in a new tab", nptRowHint: "Grouped by original OP Code / OP Sub from reports; click a row to trace the report",
      kpiRigCount: "Rig Count", kpiNptRigCount: "NPT Rig Count", kpiWellCount: "Wells", kpiTotalHours: "Total Hours", kpiTotalNpt: "Total NPT", kpiReportCompleteness: "Report Completeness", kpiNptEvents: "NPT Events", analyticsDefaultCaption: "Based on saved reports", analyticsNptCaption: "Grouped by OP Code / OP Sub", analyticsCompletenessCaption: "Missing {missing} days / Warnings {warning} days", noAnalyticsData: "No data available", noExportData: "No data to export", normalStatus: "Normal", reasonMissing: "No OP Code / OP Sub",
      allRigs: "All Rigs", allProjects: "All Projects", allReportTypes: "All Types", allReasons: "All Categories", opCodeSub: "OP Code / OP Sub", opCode: "OP Code", opSub: "OP Sub", category: "Category", tableProject: "Project", tableContractProject: "Contract (Project)", tableRig: "Rig", tableWell: "Well", tableReportType: "Report Type", tableStartDate: "Start Date", tableEndDate: "End Date", tableMoveDate: "Move Date", tableDrillingStartDate: "Drilling Start", tableDrillingFinishDate: "Drilling Finish", tableCompletionDate: "Completion Date", tableWorkoverDate: "Workover Date", tableDrillingHours: "Drilling (h)", tableCompletionHours: "Completion (h)", tableWorkoverHours: "Workover (h)", tableMoveHours: "Move (h)", tableNptHours: "NPT (h)", tableRemarks: "Remarks", tableDate: "Date", tableOperationDetails: "Operation Details",
      sectionBasic: "Basic Info", sectionSummary: "Operations Summary", sectionWellControl: "Operational Parameters", sectionSurvey: "Survey Data (Last 6)", sectionMud: "Mud Data", sectionBitBha: "Bit & BHA", sectionOperations: "Operations", sectionFluidLossInventory: "Fluid Losses & Inventory", sectionInventory: "Inventory", sectionIncidents: "Incidents & Remarks", sectionPersonnel: "Personnel", sectionPerforationIntervals: "Perforated Intervals",
      noteBasic: "Header and well information from the PDF template", noteSummary: "Current operation, 24-hour summary, and next plan", noteWellControl: "Casing, pressure tests, pump parameters, string weight, and torque", noteIncidents: "HSE status, simultaneous operations, and remarks",
      completionNoteBasic: "Completion PDF header, AFP, and well information", completionNotePersonnel: "Supervisors, engineers, geologist, and total personnel", completionNoteRemarks: "Safety comments, solids control, and field remarks", workoverNoteBasic: "Workover PDF header, AFP, and well information", workoverNotePersonnel: "Supervisors, engineers, geologist, and total personnel", workoverNoteRemarks: "Safety comments, solids control, and field remarks",
      rulesTitle: "Basic Validation Rules", liveValidation: "Live Validation",
      uploadedDays: "Uploaded", daysUnit: "days", missingDate: "Missing",
      prevMonth: "Previous month", nextMonth: "Next month", savedWarnings: "Saved Checks",
      noIssues: "No validation issues.", pdfImporting: "Parsing PDF report...", pdfImported: "PDF report parsed and filled into the form.", pdfImportFailed: "PDF parsing failed. Check the file format or template.",
      thMd: "MD (ft)", thIncl: "Incl (deg)", thAzi: "Azi (deg)", thTvd: "TVD (ft)", thVse: "VSE (ft)", thNs: "N/-S (ft)", thEw: "E/-W (ft)", thDls: "DLS (deg/100ft)", thBuild: "Build (deg/100ft)", thComponent: "Component", thOd: "OD (in)", thId: "ID (in)", thJts: "Jts", thLength: "Length (ft)", thFrom: "From (HH:MM)", thTo: "To (HH:MM)", thHrs: "Hrs (h)", thOpCode: "Op Code", thOpSub: "Op Sub", thType: "Type", thOperationDetails: "Operation Details", thInjectedVolumeBbl: "Injected Volume (bbl)", thReturnedVolumeBbl: "Returned Volume (bbl)", thBulk: "Bulk", thQtyStart: "Qty Start", thQtyUsed: "Qty Used", thQtyEnd: "Qty End", thFormation: "Formation", thTopMd: "Top MD (ft)", thBaseMd: "Base MD (ft)", thDensity: "Density (spf)", thCharges: "Charges", thPhase: "Phase (deg)", thPenetration: "Penetration (in)", thDiameter: "Diameter (in)", thDate: "Date", thStatus: "Status", thComments: "Comments"
    },
    fields: {
      event: "Event", reportDate: "Date", project: "Project", date_from: "Date From", date_to: "Date To", report_type: "Report Type", reason: "OP Code / OP Sub", nptWellbore: "Wellbore", nptRig: "Rig", nptStatus: "Confirmation Status", reportNo: "Report No", wellbore: "Wellbore", rig: "Rig", primaryReason: "Primary Reason", afeNumber: "AFE Number", refDatum: "Reference Datum (ft)", todayMd: "Today's MD (ft)", prevMd: "Previous MD (ft)", progress: "Progress (ft)", rotHrsToday: "Rotating Hours Today (h)",
      currentOps: "Current Operations", summary24h: "24-Hour Summary", forecast24h: "24-Hour Forecast", lastCasing: "Last Casing", lastCasingSize: "Last Casing Size (in)", lastCasingDepth: "Last Casing Depth (ft)", nextCasing: "Next Casing", nextCasingSize: "Next Casing Size (in)", nextCasingDepth: "Next Casing Depth (ft)", formTestType: "Formation Test Type", formTestEmw: "Formation Test EMW (ppg)", lastBopPressTest: "Last BOP Pressure Test Date", pumpRate: "Pump Rate (gpm)", pumpPress: "Pump Pressure (psi)", stringWeightUp: "String Weight Up (kip)", stringWeightDown: "String Weight Down (kip)", stringWeightUpDown: "String Weight Up/Down", torqueOffBottom: "Torque Off Bottom (ft-lbf)", torqueOnBottom: "Torque On Bottom (ft-lbf)",
      mudEngineer: "Mud Engineer", sampleFrom: "Sample From", mudType: "Mud Type", mudTimeMd: "Time / MD", mudTime: "Mud Time", mudMd: "Mud MD (ft)", mudDensity: "Density (ppg)", mudTemperature: "Mud Temp (°F)", rheologyTemp: "Rheology Temp (°F)", viscosity: "Viscosity (sec/qt)", pvYp: "PV / YP", pv: "PV (cP)", yp: "YP (lb/100ft²)", gels: "Gels 10s/10m/30m (lb/100ft²)", gel10s: "Gel 10s (lb/100ft²)", gel10m: "Gel 10m (lb/100ft²)", gel30m: "Gel 30m (lb/100ft²)", apiWl: "API WL (cc/30min)", oilWater: "Oil / Water", oilPercent: "Oil (%)", waterPercent: "Water (%)", sand: "Sand (%)", ecd: "ECD (ppg)", mudComments: "Mud Comments",
      bitNo: "Bit Sequence No", bitSize: "Bit Size (in)", bitManufacturer: "Manufacturer", bitSerial: "Bit Serial No", bitWearIodl: "Bit Wear I-O-D-L", bitWearBgor: "Bit Wear B-G-O-R", bhaNo: "BHA No", bhaMdIn: "MD In (ft)", bhaMdOut: "MD Out (ft)", bhaTotalLength: "Total Length (ft)", safetyIncident: "Safety Incident?", environmentIncident: "Environmental Incident?", daysSinceRi: "Days since Last RI", daysSinceLta: "Days since Last LTA", incidentComments: "Incident Comments", otherRemarks: "Other Remarks",
      description: "Description", operationStartDate: "Operation Start", workoverNo: "WO No", afeCost: "AFP Cost (USD)", dailyCost: "Daily Cost (USD)", cumulativeCost: "Cumulative Cost (USD)", supervisor1: "Supervisor 1", supervisor2: "Supervisor 2", engineer: "Engineer", pamEngineer: "PAM Engineer", geologist: "Geologist", totalPersonnel: "Total Personnel", safetyComments: "Safety Comments", groundElev: "Ground Elev (ft)", afeMdDays: "AFE MD/Days (ft/d)"
    },
    rules: [
      "<strong>Required:</strong> Date, Report No, Wellbore, Rig, Current Operations, 24-Hour Summary, Mud Type, and Today's MD.",
      "<strong>Date:</strong> report date cannot be later than today.",
      "<strong>Depth:</strong> Today's MD must be greater than or equal to Previous MD; Progress should match the difference with 0.5 ft tolerance.",
      "<strong>Hours:</strong> Only the earliest and latest day for each report type and well are checked for a 24.00-hour Operations total, with 0.05 h tolerance.",
      "<strong>Operation rows:</strong> From, To, Hrs, Op Code, Type, and Operation Details should be complete; Type must be P, SC, or NPT from the appendix.",
      "<strong>Survey:</strong> Survey MD cannot exceed Today's MD; Incl must be 0 to 180; DLS cannot be negative.",
      "<strong>Mud:</strong> Density should be 6 to 20 ppg; Sand should not exceed 10%.",
      "<strong>Equipment:</strong> BHA OD, ID, Jts, and Length cannot be negative; OD should be greater than or equal to ID.",
      "<strong>HSE:</strong> Incident Comments are required when Safety or Environmental Incident is Y.",
      "<strong>Fluid losses and inventory:</strong> volumes and quantities are parsed as numbers and do not affect hour validation."
    ],
    completionRules: [
      "<strong>Required:</strong> Date, Report No, Wellbore, Rig, Current Operations, 24-Hour Summary, and 24-Hour Forecast.",
      "<strong>Date:</strong> report date cannot be later than today, and Operation Start cannot be later than the report date.",
      "<strong>Hours:</strong> Only the earliest and latest day for each report type and well are checked for a 24.00-hour Operations total, with 0.05 h tolerance.",
      "<strong>Operation rows:</strong> From, To, Hrs, Op Code, Type, and Operation Details should be complete; Type must be P, SC, or NPT.",
      "<strong>Perforated intervals:</strong> Base MD should be greater than or equal to Top MD; Length cannot be negative.",
      "<strong>Inventory:</strong> quantities are parsed as numbers and do not affect hour validation."
    ],
    workoverRules: [
      "<strong>Required:</strong> Date, Report No, Wellbore, Rig, Current Operations, 24-Hour Summary, and 24-Hour Forecast.",
      "<strong>Date:</strong> report date cannot be later than today, and Operation Start cannot be later than the report date.",
      "<strong>Hours:</strong> Only the earliest and latest day for each report type and well are checked for a 24.00-hour Operations total, with 0.05 h tolerance.",
      "<strong>Operation rows:</strong> From, To, Hrs, Op Code, Type, and Operation Details should be complete; Type must be P, SC, or NPT.",
      "<strong>Perforated intervals:</strong> Base MD should be greater than or equal to Top MD; Length cannot be negative.",
      "<strong>Inventory:</strong> quantities are parsed as numbers and do not affect hour validation."
    ],
    moveRules: [
      "<strong>Required:</strong> Date, Report No, Wellbore, Rig, Current Operations, 24-Hour Summary, and 24-Hour Forecast.",
      "<strong>Hours:</strong> Only the earliest and latest day for each report type and well are checked for a 24.00-hour Operations total, with 0.05 h tolerance.",
      "<strong>Operation rows:</strong> From, To, Hrs, Op Code, Type, and Operation Details should be complete; Type must be P, SC, or NPT.",
      "<strong>Remarks:</strong> Other Remarks can keep the original final-page text for manual review."
    ],
    msg: {
      required: "{field} is required.", futureDate: "Report date cannot be later than today.", operationStartDate: "Operation Start cannot be later than the report date.", mdOrder: "Today's MD must be greater than or equal to Previous MD.", progressMismatch: "Progress does not match the MD difference. Current difference is {value} ft.", operationMissingTable: "Operations cannot be empty.", operationHours: "Operations total must be 24.00 h. Current total is {value} h.", operationMissing: "Operations row {row} is missing {field}.", operationTimeMismatch: "Operations row {row} From/To duration is {value} h and does not match Hrs.", operationType: "Operations row {row} Type is empty or not P/SC/NPT; please review.", completionOperationType: "Completion operation row {row} Type is empty or not P/SC/NPT; please review.", workoverOperationType: "Workover operation row {row} Type is empty or not P/SC/NPT; please review.", moveOperationType: "Move operation row {row} Type is empty or not P/SC/NPT; please review.", operationHourRange: "Operations row {row} Hrs must be between 0 and 24.", intervalDepth: "Perforated interval row {row} Base MD should be greater than or equal to Top MD.", intervalLength: "Perforated interval row {row} Length cannot be negative.", surveyMd: "Survey row {row} MD cannot exceed Today's MD.", surveyIncl: "Survey row {row} Incl must be between 0 and 180.", surveyDls: "Survey row {row} DLS cannot be negative.", mudDensity: "Mud density should be between 6 and 20 ppg.", sand: "Mud sand is above 10%; please review.", bhaOdId: "BHA row {row} OD should be greater than or equal to ID.", bhaNegative: "BHA row {row} contains a negative value.", negativeValue: "Row {row} {field} cannot be negative.", incidentRequired: "Incident Comments are required when Safety or Environmental Incident is Y."
    }
  },
  es: {
    ui: {
      appTitleShort: "NexoRig", appSubtitle: "Inteligencia de Perforación", pageTitle: "Mesa de Registro del Reporte Diario", drillingPageKicker: "REPORTE DIARIO DE PERFORACIÓN", completionPageTitle: "Mesa del Reporte Diario de Completación", completionPageKicker: "REPORTE DIARIO DE COMPLETACIÓN", workoverPageTitle: "Mesa del Reporte Diario de Workover", workoverPageKicker: "REPORTE DIARIO DE WORKOVER",
      systemAdmin: "Administración",
      menuDailyParsing: "Reportes Diarios", menuDrillingDaily: "Reporte Diario de Perforación", menuCompletionDaily: "Reporte Diario de Completación", menuWorkoverDaily: "Reporte Diario de Workover", menuMoveDaily: "Reporte Diario de Movilización",
      menuProductionReport: "Análisis de Producción", menuRigProductionSummary: "Análisis de Tiempos", menuProductionDetailReport: "Reporte de Producción", menuWellNptConfirm: "Estadística NPT", menuRigNptRanking: "Confirmación NPT",
      menuHsse: "Gestión HSSE", menuHsseCollection: "Registro HSSE", menuHsseDashboard: "Cabina de Seguridad", menuDailySafetySummary: "Reportes HSSE", menuPeriodSafetyReport: "Reportes HSSE",
      descDrillingDaily: "Carga reportes diarios PDF de perforación o movilización, extrae datos básicos y operaciones, y permite editar el reporte diario de perforación.",
      descCompletionDaily: "Carga PDFs diarios de completación, extrae datos básicos, operaciones, inventarios e intervalos cañoneados, y permite revisar y editar.", descWorkoverDaily: "Carga PDFs diarios de workover, extrae información WO, operaciones, inventarios, comentarios de seguridad e intervalos cañoneados, y permite revisar y editar.", descMoveDaily: "Entrada reservada para análisis PDF y captura estructurada de reportes diarios de movilización.",
      descRigProductionSummary: "Muestra tiempos de producción por equipo, tipo de reporte y mes desde reportes diarios procesados.", descProductionDetailReport: "Consulta detalles de producción por periodo de proyecto, equipo y asignación de pozo.", descWellNptConfirm: "Clasifica equipos de perforación por duración y proporción histórica de NPT.", descRigNptRanking: "Confirma horas P, SC y NPT por pozo, con actualización posterior desde tablas de confirmación de tiempos.",
      descHsseCollection: "Registra información HSSE diaria por pozo y equipo, incluyendo actos inseguros, condiciones inseguras, personal vulnerable, anomalías productivas y seguridad pública.", descHsseDashboard: "Muestra KPIs HSSE, excepciones y seguimiento general por equipo.", descDailySafetySummary: "Genera reportes de seguridad a partir de datos HSSE.", descPeriodSafetyReport: "Combina estadísticas diarias y reportes semanales o mensuales en una entrada de reporte de seguridad.",
      moduleStatusPlanned: "Función Planificada", moduleComingSoon: "Función Reservada", moduleCurrent: "Menú Actual", moduleComingSoonDesc: "Esta entrada queda reservada según la lista de requisitos. Luego se podrá conectar captura de datos, reportes o análisis.",
      navBasic: "Información Básica", navSummary: "Resumen Operacional", navWellControl: "Parámetros Operacionales", navSurvey: "Datos Direccionales", navMud: "Datos de Lodo", navBitBha: "Broca y BHA", navOperations: "Registro de Operaciones", navCosts: "Pérdida de Fluido e Inventario", navIncidents: "Incidentes y Observaciones",
      importPdf: "Importar Reporte PDF", originalReport: "Original", translateChinese: "Traducir a chino", translationRunning: "Cambiando idioma del reporte...", translationRunningShort: "Traduciendo", translationReady: "Idioma del reporte cambiado.", translationFailed: "Los datos traducidos no están disponibles. Revise el modelo local o el estado de la tarea.", translationPreviewNotice: "Se muestra la traducción de base de datos en modo lectura. Vuelva a Original para editar el reporte fuente.", translationTitle: "Traducción EN/ES del Reporte Diario", translationOriginal: "Original", translationLanguage: "Idioma", translationChinese: "Chino", translationPath: "Campo", translationTerms: "Términos", translationWarnings: "Alertas", translationEmpty: "No hay resultados de traducción", saveDatabase: "Guardar", downloadDatabase: "Estado BD", backRecords: "Volver a registros", databaseSaved: "Guardado en MySQL.", databaseSaveFailed: "No se pudo guardar en MySQL.", recordLoadFailed: "No se pudo abrir el detalle del reporte.", databaseRecord: "Registro de base", sourceFileEmpty: "No se ha cargado archivo",
      uploadDashboardTitle: "Panel de Reportes Diarios", wellSelection: "Selección de Pozo", searchWell: "Buscar pozo", reportCalendar: "Calendario", uploadRecords: "Registros de Carga", allTypes: "Todos los tipos", allStatuses: "Todos los estados", exportList: "Exportar", preview: "Ver", download: "Descargar", detail: "Detalle", uploaded: "Completo", queued: "En cola", parsing: "Analizando", parseDoneStatus: "Análisis completo", failed: "Falló", warningStatus: "Alertas", pending: "Pendiente", translationQueuedStatus: "Traducción en cola", translationRunningStatus: "Traduciendo", translationDoneStatus: "Traducción completa", translationFailedStatus: "Traducción falló", translationNotReady: "La traducción aún no está completa. El cambio de idioma estará disponible al finalizar.", noRecords: "Sin registros", addWell: "Agregar pozo", selectedWell: "Pozo actual", monthlyUploaded: "Cargados del mes", monthlyPending: "Pendientes", reportKinds: "Tipos de reporte", monthlyUploaders: "Cargadores del mes", calendarHint: "Tip: haga clic en una fecha completada para previsualizar", recordsCount: "registros", uploader: "Usuario", uploadTime: "Hora de carga", fileName: "Archivo", status: "Estado", operation: "Acciones", date: "Fecha", well: "Pozo", reportType: "Tipo", page: "Página", prevPage: "Anterior", nextPage: "Siguiente", sourcePdfMissing: "El PDF fuente no se guardó. Vuelva a importarlo para verlo.", sourcePdfTitle: "PDF fuente", sortFirstUpload: "Prim.", sortLastUpload: "Rec.", sortWellName: "Pozo", deleteFailedImport: "Eliminar", failedImportDeleted: "Se eliminó el registro de importación fallida.",
      metricCompletion: "Avance", metricIssues: "Alertas", metricHours: "Total Operativo", metricProgress: "Progreso", metricIntervals: "Intervalos", metricWellDate: "Pozo / Fecha", metricDailyHours: "Horas del Día", metricNptHours: "Horas NPT", metricDataCompleteness: "Integridad de Datos",
      metricWorkDays: "Días Operativos", metricNptShare: "Horas NPT / %", metricPScShare: "% P / SC", metricReportCompleteness: "Integridad del Reporte", metricMoveDrillingDays: "Movilización / Perforación", noWells: "No hay pozos identificados",
      analyticsKicker: "Panel de Datos", analyticsProductionScope: "Basado en reportes diarios guardados en MySQL", analyticsNptScope: "P entra directo; SC/NPT entra a estadísticas oficiales solo después de la confirmación NPT", search: "Consultar", reset: "Restablecer", wellborePlaceholder: "Ingrese pozo",
      chartRigHours: "Ranking NPT acumulado por taladro", chartOperationMix: "Composición Operativa", chartMonthlyHours: "Gantt de Operaciones por Pozo", chartNptRig: "Comparación NPT por Taladro (h)", chartNptReason: "Distribución por Código / Subcódigo", chartNptWell: "Ranking NPT por Pozo", chartNptMonthly: "Tendencia Mensual NPT (h)", productionDetailTitle: "Detalle del Reporte de Producción", nptDetailTitle: "Detalle NPT", analyticsRowHint: "Haga clic en una fila para abrir el detalle del reporte", productionReportRowHint: "Haga clic en un pozo para abrir su página diaria en una pestaña nueva", nptRowHint: "Agrupado por código / subcódigo original del reporte; haga clic en una fila para rastrear el reporte",
      kpiRigCount: "Taladros", kpiNptRigCount: "Taladros con NPT", kpiWellCount: "Pozos", kpiTotalHours: "Horas Totales", kpiTotalNpt: "NPT Total", kpiReportCompleteness: "Integridad del Reporte", kpiNptEvents: "Eventos NPT", analyticsDefaultCaption: "Basado en reportes guardados", analyticsNptCaption: "Agrupado por código / subcódigo", analyticsCompletenessCaption: "Faltan {missing} días / Alertas {warning} días", noAnalyticsData: "No hay datos para estadística", noExportData: "No hay datos para exportar", normalStatus: "Normal", reasonMissing: "Sin código / subcódigo",
      allRigs: "Todos los taladros", allProjects: "Todos los proyectos", allReportTypes: "Todos los tipos", allReasons: "Todas las categorías", scopeByRig: "Por taladro", scopeByProject: "Por proyecto", productionNptCaption: "Horas NPT acumuladas (h)", nptHoursCaption: "Horas NPT (h)", nptDailyShareCaption: "Promedio diario de NPT (%)", nptNotePlaceholder: "Ingrese observaciones (opcional)", opCodeSub: "Código / Subcódigo", opCode: "Código Op", opSub: "Subcódigo Op", category: "Categoría", tableProject: "Proyecto", tableContractProject: "Contrato (Proyecto)", tableRig: "Taladro", tableWell: "Pozo", tableReportType: "Tipo de Reporte", tableStartDate: "Fecha Inicio", tableEndDate: "Fecha Fin", tableMoveDate: "Fecha Movilización", tableDrillingStartDate: "Inicio Perforación", tableDrillingFinishDate: "Fin Perforación", tableCompletionDate: "Fecha Completación", tableWorkoverDate: "Fecha Workover", tableDrillingHours: "Perforación (h)", tableCompletionHours: "Completación (h)", tableWorkoverHours: "Workover (h)", tableMoveHours: "Movilización (h)", tableNptHours: "NPT (h)", tableRemarks: "Observaciones", tableDate: "Fecha", tableOperationDetails: "Detalle de Operación",
      sectionBasic: "Información Básica", sectionSummary: "Resumen Operacional", sectionWellControl: "Parámetros Operacionales", sectionSurvey: "Datos Direccionales (Últimos 6)", sectionMud: "Datos de Lodo", sectionBitBha: "Broca y BHA", sectionOperations: "Operaciones", sectionFluidLossInventory: "Pérdidas de Fluido e Inventario", sectionInventory: "Inventario", sectionIncidents: "Incidentes y Observaciones", sectionPersonnel: "Personal", sectionPerforationIntervals: "Intervalos Cañoneados",
      noteBasic: "Encabezado e información del pozo según la plantilla PDF", noteSummary: "Operación actual, resumen de 24 horas y plan siguiente", noteWellControl: "Casing, pruebas de presión, parámetros de bomba, peso de sarta y torque", noteIncidents: "Estado HSE, operaciones simultáneas y observaciones",
      completionNoteBasic: "Encabezado PDF de completación, AFP e información del pozo", completionNotePersonnel: "Supervisores, ingenieros, geólogo y personal total", completionNoteRemarks: "Comentarios de seguridad, control de sólidos y observaciones de campo", workoverNoteBasic: "Encabezado PDF de workover, AFP e información del pozo", workoverNotePersonnel: "Supervisores, ingenieros, geólogo y personal total", workoverNoteRemarks: "Comentarios de seguridad, control de sólidos y observaciones de campo",
      rulesTitle: "Reglas Básicas de Validación", liveValidation: "Validación en Vivo",
      uploadedDays: "Cargados", daysUnit: "días", missingDate: "Faltante",
      prevMonth: "Mes anterior", nextMonth: "Mes siguiente", savedWarnings: "Validaciones guardadas",
      noIssues: "Sin alertas de validación.", pdfImporting: "Analizando reporte PDF...", pdfImported: "Reporte PDF analizado y cargado en el formulario.", pdfImportFailed: "No se pudo analizar el PDF. Revise el formato o la plantilla.",
      thMd: "MD (ft)", thIncl: "Incl (deg)", thAzi: "Azi (deg)", thTvd: "TVD (ft)", thVse: "VSE (ft)", thNs: "N/-S (ft)", thEw: "E/-W (ft)", thDls: "DLS (deg/100ft)", thBuild: "Build (deg/100ft)", thComponent: "Componente", thOd: "OD (in)", thId: "ID (in)", thJts: "Jts", thLength: "Longitud (ft)", thFrom: "Desde (HH:MM)", thTo: "Hasta (HH:MM)", thHrs: "Hrs (h)", thOpCode: "Código Op", thOpSub: "Sub Op", thType: "Tipo", thOperationDetails: "Detalle de Operación", thInjectedVolumeBbl: "Volumen Inyectado (bbl)", thReturnedVolumeBbl: "Volumen Retornado (bbl)", thBulk: "Inventario", thQtyStart: "Cant. Inicial", thQtyUsed: "Cant. Usada", thQtyEnd: "Cant. Final", thFormation: "Formación", thTopMd: "Tope MD (ft)", thBaseMd: "Base MD (ft)", thDensity: "Densidad (spf)", thCharges: "Cargas", thPhase: "Fase (deg)", thPenetration: "Penetración (in)", thDiameter: "Diámetro (in)", thDate: "Fecha", thStatus: "Estado", thComments: "Comentarios"
    },
    fields: {
      event: "Evento", reportDate: "Fecha", project: "Proyecto", date_from: "Fecha Inicio", date_to: "Fecha Fin", scope_type: "Modo de filtro", scope_value: "Taladro", nptConfirmNote: "Observaciones", report_type: "Tipo de Reporte", reason: "Código / Subcódigo", nptWellbore: "Pozo", nptRig: "Taladro", nptStatus: "Estado de Confirmación", reportNo: "No. de Reporte", wellbore: "Pozo", rig: "Taladro", primaryReason: "Razón Principal", afeNumber: "Número AFE", refDatum: "Datum de Referencia (ft)", todayMd: "MD de Hoy (ft)", prevMd: "MD Anterior (ft)", progress: "Progreso (ft)", rotHrsToday: "Horas Rotando Hoy (h)",
      currentOps: "Operación Actual", summary24h: "Resumen 24 h", forecast24h: "Pronóstico 24 h", lastCasing: "Último Casing", lastCasingSize: "Tamaño Último Casing (in)", lastCasingDepth: "Profundidad Último Casing (ft)", nextCasing: "Próximo Casing", nextCasingSize: "Tamaño Próximo Casing (in)", nextCasingDepth: "Profundidad Próximo Casing (ft)", formTestType: "Tipo de Prueba de Formación", formTestEmw: "EMW de Prueba de Formación (ppg)", lastBopPressTest: "Fecha de Última Prueba BOP", pumpRate: "Caudal Bomba (gpm)", pumpPress: "Presión Bomba (psi)", stringWeightUp: "Peso de Sarta Arriba (kip)", stringWeightDown: "Peso de Sarta Abajo (kip)", stringWeightUpDown: "Peso Sarta Arriba/Abajo", torqueOffBottom: "Torque Fuera de Fondo (ft-lbf)", torqueOnBottom: "Torque en Fondo (ft-lbf)",
      mudEngineer: "Ingeniero de Lodo", sampleFrom: "Muestra de", mudType: "Tipo de Lodo", mudTimeMd: "Hora / MD", mudTime: "Hora Lodo", mudMd: "MD Lodo (ft)", mudDensity: "Densidad (ppg)", mudTemperature: "Temp. Lodo (°F)", rheologyTemp: "Temp. Reología (°F)", viscosity: "Viscosidad (sec/qt)", pvYp: "PV / YP", pv: "PV (cP)", yp: "YP (lb/100ft²)", gels: "Geles 10s/10m/30m (lb/100ft²)", gel10s: "Gel 10s (lb/100ft²)", gel10m: "Gel 10m (lb/100ft²)", gel30m: "Gel 30m (lb/100ft²)", apiWl: "API WL (cc/30min)", oilWater: "Aceite / Agua", oilPercent: "Aceite (%)", waterPercent: "Agua (%)", sand: "Arena (%)", ecd: "ECD (ppg)", mudComments: "Comentarios de Lodo",
      bitNo: "Secuencia de Broca", bitSize: "Tamaño Broca (in)", bitManufacturer: "Fabricante", bitSerial: "Serie de Broca", bitWearIodl: "Desgaste I-O-D-L", bitWearBgor: "Desgaste B-G-O-R", bhaNo: "No. BHA", bhaMdIn: "MD Entrada (ft)", bhaMdOut: "MD Salida (ft)", bhaTotalLength: "Longitud Total (ft)", safetyIncident: "¿Incidente de Seguridad?", environmentIncident: "¿Incidente Ambiental?", daysSinceRi: "Días desde Último RI", daysSinceLta: "Días desde Último LTA", incidentComments: "Comentarios de Incidente", otherRemarks: "Otras Observaciones",
      description: "Descripción", operationStartDate: "Inicio OPR", workoverNo: "No. WO", afeCost: "Costo AFP (USD)", dailyCost: "Costo Diario (USD)", cumulativeCost: "Costo Acumulado (USD)", supervisor1: "Supervisor 1", supervisor2: "Supervisor 2", engineer: "Ingeniero", pamEngineer: "Ingeniero PAM", geologist: "Geólogo", totalPersonnel: "Total Personal", safetyComments: "Comentarios de Seguridad", groundElev: "Elevación Terreno (ft)", afeMdDays: "AFE MD/Días (ft/d)"
    },
    rules: [
      "<strong>Obligatorio:</strong> Fecha, No. de Reporte, Pozo, Taladro, Operación Actual, Resumen 24 h, Tipo de Lodo y MD de Hoy.",
      "<strong>Fecha:</strong> la fecha del reporte no puede ser posterior a hoy.",
      "<strong>Profundidad:</strong> el MD de hoy debe ser mayor o igual al MD anterior; el progreso debe coincidir con tolerancia de 0.5 ft.",
      "<strong>Horas:</strong> solo se valida un total de 24.00 h en el primer y último día de cada tipo de reporte y pozo, con tolerancia de 0.05 h.",
      "<strong>Filas de operación:</strong> Desde, Hasta, Hrs, Código Op, Tipo y Detalle deben estar completos; Tipo debe ser P, SC o NPT del apéndice.",
      "<strong>Survey:</strong> MD no puede superar el MD de hoy; Incl debe estar entre 0 y 180; DLS no puede ser negativo.",
      "<strong>Lodo:</strong> densidad entre 6 y 20 ppg; arena no mayor a 10%.",
      "<strong>Equipo:</strong> OD, ID, Jts y Longitud de BHA no pueden ser negativos; OD debe ser mayor o igual a ID.",
      "<strong>HSE:</strong> comentarios obligatorios si Safety o Environmental Incident es Y.",
      "<strong>Pérdidas de fluido e inventario:</strong> volúmenes y cantidades se interpretan como números y no afectan la validación de horas."
    ],
    completionRules: [
      "<strong>Obligatorio:</strong> Fecha, No. de Reporte, Pozo, Taladro, Operación Actual, Resumen 24 h y Pronóstico 24 h.",
      "<strong>Fecha:</strong> la fecha del reporte no puede ser posterior a hoy e Inicio OPR no puede ser posterior a la fecha del reporte.",
      "<strong>Horas:</strong> solo se valida un total de 24.00 h en el primer y último día de cada tipo de reporte y pozo, con tolerancia de 0.05 h.",
      "<strong>Filas de operación:</strong> Desde, Hasta, Hrs, Código Op, Tipo y Detalle deben estar completos; Tipo debe ser P, SC o NPT.",
      "<strong>Intervalos cañoneados:</strong> Base MD debe ser mayor o igual que Tope MD; Longitud no puede ser negativa.",
      "<strong>Inventario:</strong> las cantidades se interpretan como números y no afectan la validación de horas."
    ],
    workoverRules: [
      "<strong>Obligatorio:</strong> Fecha, No. de Reporte, Pozo, Taladro, Operación Actual, Resumen 24 h y Pronóstico 24 h.",
      "<strong>Fecha:</strong> la fecha del reporte no puede ser posterior a hoy e Inicio OPR no puede ser posterior a la fecha del reporte.",
      "<strong>Horas:</strong> solo se valida un total de 24.00 h en el primer y último día de cada tipo de reporte y pozo, con tolerancia de 0.05 h.",
      "<strong>Filas de operación:</strong> Desde, Hasta, Hrs, Código Op, Tipo y Detalle deben estar completos; Tipo debe ser P, SC o NPT.",
      "<strong>Intervalos cañoneados:</strong> Base MD debe ser mayor o igual que Tope MD; Longitud no puede ser negativa.",
      "<strong>Inventario:</strong> las cantidades se interpretan como números y no afectan la validación de horas."
    ],
    moveRules: [
      "<strong>Obligatorio:</strong> Fecha, No. de Reporte, Pozo, Taladro, Operación Actual, Resumen 24 h y Pronóstico 24 h.",
      "<strong>Horas:</strong> solo se valida un total de 24.00 h en el primer y último día de cada tipo de reporte y pozo, con tolerancia de 0.05 h.",
      "<strong>Filas de operación:</strong> Desde, Hasta, Hrs, Código Op, Tipo y Detalle deben estar completos; Tipo debe ser P, SC o NPT.",
      "<strong>Observaciones:</strong> Other Remarks puede conservar el texto original de la última página para revisión manual."
    ],
    msg: {
      required: "{field} es obligatorio.", futureDate: "La fecha del reporte no puede ser posterior a hoy.", operationStartDate: "Inicio OPR no puede ser posterior a la fecha del reporte.", mdOrder: "El MD de hoy debe ser mayor o igual al MD anterior.", progressMismatch: "El progreso no coincide con la diferencia de MD. La diferencia actual es {value} ft.", operationMissingTable: "Las operaciones no pueden estar vacías.", operationHours: "El total de operaciones debe ser 24.00 h. El total actual es {value} h.", operationMissing: "La fila de operaciones {row} no tiene {field}.", operationTimeMismatch: "La duración Desde/Hasta de la fila {row} es {value} h y no coincide con Hrs.", operationType: "El Tipo en la fila de operaciones {row} está vacío o no es P/SC/NPT; revisar.", completionOperationType: "El Tipo en la fila de completación {row} está vacío o no es P/SC/NPT; revisar.", workoverOperationType: "El Tipo en la fila de workover {row} está vacío o no es P/SC/NPT; revisar.", moveOperationType: "El Tipo en la fila de traslado {row} está vacío o no es P/SC/NPT; revisar.", operationHourRange: "Las Hrs de la fila {row} deben estar entre 0 y 24.", intervalDepth: "En intervalo cañoneado fila {row}, Base MD debe ser mayor o igual que Tope MD.", intervalLength: "La Longitud del intervalo cañoneado fila {row} no puede ser negativa.", surveyMd: "El MD de survey en la fila {row} no puede superar el MD de hoy.", surveyIncl: "La inclinación en la fila {row} debe estar entre 0 y 180.", surveyDls: "El DLS en la fila {row} no puede ser negativo.", mudDensity: "La densidad del lodo debe estar entre 6 y 20 ppg.", sand: "La arena del lodo supera 10%; revisar.", bhaOdId: "En BHA fila {row}, OD debe ser mayor o igual que ID.", bhaNegative: "La fila BHA {row} contiene un valor negativo.", negativeValue: "Fila {row}: {field} no puede ser negativo.", incidentRequired: "Los comentarios son obligatorios cuando Safety o Environmental Incident es Y."
    }
  }
};

Object.assign(i18n.zh.msg, {
  operationHours: "当前为该类日报此井的首日或末日，Operations 工时合计应为 24.00 h，当前为 {value} h。",
});
Object.assign(i18n.en.msg, {
  operationHours: "This is the first or last day for this report type and well. Operations must total 24.00 h; current total is {value} h.",
});
Object.assign(i18n.es.msg, {
  operationHours: "Este es el primer o último día para este tipo de reporte y pozo. El total debe ser 24.00 h; actualmente es {value} h.",
});

Object.assign(i18n.en.ui, {
  translationPendingStatus: "Pending translation",
  translationQueuedStatus: "Queued",
  translationNotRequiredStatus: "Not required",
});
Object.assign(i18n.es.ui, {
  translationPendingStatus: "Pendiente de traducción",
  translationQueuedStatus: "En cola",
  translationNotRequiredStatus: "No requiere traducción",
});
Object.assign(i18n.zh.ui, {
  roleAdmin: "管理员", roleEngineer: "工程师", roleReviewer: "审阅者", roleViewer: "查看者", logout: "退出",
  breadcrumbAria: "页面路径", wellSortAria: "井排序", wellHasNpt: "出现过 NPT", wellNoNpt: "未出现 NPT",
  wellHasNptTitle: "本井历史日报出现过 NPT", wellNoNptTitle: "本井历史日报未出现 NPT",
});
Object.assign(i18n.es.ui, {
  roleAdmin: "Administrador", roleEngineer: "Ingeniero", roleReviewer: "Revisor", roleViewer: "Consulta", logout: "Salir",
  breadcrumbAria: "Ruta de página", wellSortAria: "Orden de pozos", wellHasNpt: "Con NPT", wellNoNpt: "Sin NPT",
  wellHasNptTitle: "El pozo registra NPT en su historial", wellNoNptTitle: "El pozo no registra NPT en su historial",
});

const DEFAULT_TIME_TYPE_VALUES = [
  { value_code: "P", value_name: "P", display_color: "#16875B" },
  { value_code: "SC", value_name: "SC", display_color: "#B7791F" },
  { value_code: "NPT", value_name: "NPT", display_color: "#D43F3A" },
];
let timeTypeValues = [...DEFAULT_TIME_TYPE_VALUES];
const DEFAULT_NPT_REFERENCE_VALUES = {
  WORK_BUCKET: [["OPERATION","作业"],["MOVE","搬迁"],["STANDBY_STAFFED","有人待工"],["STANDBY_UNSTAFFED","无人待工"],["FORCE_MAJEURE","不可抗力"],["MAINTENANCE","维修"]],
  RESPONSIBILITY: [["OURS","我方"],["CLIENT","甲方"],["THIRD_PARTY","第三方"],["FORCE_MAJEURE","不可抗力"]],
  BILLING_STATUS: [["FULL_RATE","全日费"],["PARTIAL_RATE","部分日费"],["ZERO_RATE","零日费"]],
  CAUSE_CODE: [["EQUIPMENT","设备"],["TOOL","工具"],["PERSONNEL","人员"],["MATERIAL","物资"],["COMMUNITY","社区"],["WEATHER","天气"],["INCIDENT","事故"],["OTHER","其他"]],
};
const nptReferenceValues = Object.fromEntries(Object.entries(DEFAULT_NPT_REFERENCE_VALUES).map(([key, values]) => [key, [...values]]));

function timeTypeCodes() {
  return timeTypeValues.map((item) => String(item.value_code || "").trim().toUpperCase()).filter(Boolean);
}

const tableSchemas = {
  surveyTable: [{ name: "md", type: "number" }, { name: "incl", type: "number" }, { name: "azi", type: "number" }, { name: "tvd", type: "number" }, { name: "vse", type: "number" }, { name: "ns", type: "number" }, { name: "ew", type: "number" }, { name: "dls", type: "number" }, { name: "build", type: "number" }],
  bhaTable: [{ name: "component", type: "text" }, { name: "od", type: "number" }, { name: "id", type: "number" }, { name: "joints", type: "number" }, { name: "length", type: "number" }],
  operationsTable: [{ name: "from", type: "text" }, { name: "to", type: "text" }, { name: "hours", type: "number" }, { name: "op_code", type: "text" }, { name: "op_sub", type: "text" }, { name: "op_type", type: "select", options: timeTypeCodes() }, { name: "operation_details", type: "textarea" }],
  fluidLossTable: [{ name: "injected_volume_bbl", type: "number" }, { name: "returned_volume_bbl", type: "number" }],
  bulkTable: [{ name: "bulk", type: "text" }, { name: "qty_start", type: "number" }, { name: "qty_used", type: "number" }, { name: "qty_end", type: "number" }],
  completionOperationsTable: [{ name: "from", type: "text" }, { name: "to", type: "text" }, { name: "hours", type: "number" }, { name: "op_code", type: "text" }, { name: "op_sub", type: "text" }, { name: "op_type", type: "select", options: timeTypeCodes() }, { name: "operation_details", type: "textarea" }],
  completionBulkTable: [{ name: "bulk", type: "text" }, { name: "qty_start", type: "number" }, { name: "qty_used", type: "number" }, { name: "qty_end", type: "number" }],
  perforationIntervalsTable: [{ name: "formation", type: "text" }, { name: "top_md", type: "number" }, { name: "base_md", type: "number" }, { name: "length", type: "number" }, { name: "density", type: "number" }, { name: "charges", type: "text" }, { name: "phase", type: "number" }, { name: "penetration", type: "number" }, { name: "diameter", type: "number" }, { name: "date", type: "text" }, { name: "status", type: "text" }, { name: "comments", type: "textarea" }],
  workoverOperationsTable: [{ name: "from", type: "text" }, { name: "to", type: "text" }, { name: "hours", type: "number" }, { name: "op_code", type: "text" }, { name: "op_sub", type: "text" }, { name: "op_type", type: "select", options: timeTypeCodes() }, { name: "operation_details", type: "textarea" }],
  workoverBulkTable: [{ name: "bulk", type: "text" }, { name: "qty_start", type: "number" }, { name: "qty_used", type: "number" }, { name: "qty_end", type: "number" }],
  workoverIntervalsTable: [{ name: "formation", type: "text" }, { name: "top_md", type: "number" }, { name: "base_md", type: "number" }, { name: "length", type: "number" }, { name: "density", type: "number" }, { name: "charges", type: "text" }, { name: "phase", type: "number" }, { name: "penetration", type: "number" }, { name: "diameter", type: "number" }, { name: "date", type: "text" }, { name: "status", type: "text" }, { name: "comments", type: "textarea" }],
  moveOperationsTable: [{ name: "from", type: "text" }, { name: "to", type: "text" }, { name: "hours", type: "number" }, { name: "op_code", type: "text" }, { name: "op_sub", type: "text" }, { name: "op_type", type: "select", options: timeTypeCodes() }, { name: "operation_details", type: "textarea" }]
};

const drillingTableIds = ["surveyTable", "bhaTable", "operationsTable", "fluidLossTable", "bulkTable"];
const completionTableIds = ["completionOperationsTable", "completionBulkTable", "perforationIntervalsTable"];
const workoverTableIds = ["workoverOperationsTable", "workoverBulkTable", "workoverIntervalsTable"];
const moveTableIds = ["moveOperationsTable"];
const form = document.querySelector("#reportForm");
const completionForm = document.querySelector("#completionReportForm");
const workoverForm = document.querySelector("#workoverReportForm");
const moveForm = document.querySelector("#moveReportForm");
const issuesEl = document.querySelector("#issues");
const completionIssuesEl = document.querySelector("#completionIssues");
const workoverIssuesEl = document.querySelector("#workoverIssues");
const moveIssuesEl = document.querySelector("#moveIssues");
const toast = document.querySelector("#toast");
const storedLanguage = localStorage.getItem("drillingReportLanguage") || "zh";
let currentLanguage = ["zh", "es"].includes(storedLanguage) ? storedLanguage : "zh";
let reportContentLanguageMode = "original";
let activeMenuTarget = "drilling-daily";
let drillingSourceFileName = "";
let reportTranslationBusy = { reportType: "", language: "" };
const MANUAL_WELLS_STORAGE_KEY = "drillingReportManualWellProfiles";
localStorage.removeItem(MANUAL_WELLS_STORAGE_KEY);
const currentRecordIds = { drilling: "", completion: "", workover: "", move: "" };
const savedReportSignatures = { drilling: "", completion: "", workover: "", move: "" };
const lockedRecordIds = new Set();
const reportContentState = {
  drilling: { mode: "original", selectedLanguage: currentLanguage === "es" ? "es" : "original", original: null, cache: {}, targetLanguage: "" },
  completion: { mode: "original", selectedLanguage: currentLanguage === "es" ? "es" : "original", original: null, cache: {}, targetLanguage: "" },
  workover: { mode: "original", selectedLanguage: currentLanguage === "es" ? "es" : "original", original: null, cache: {}, targetLanguage: "" },
  move: { mode: "original", selectedLanguage: currentLanguage === "es" ? "es" : "original", original: null, cache: {}, targetLanguage: "" }
};
const DEFAULT_PAGE_SIZE = 20;
const PAGE_SIZE_OPTIONS = [10, 20, 50];
const recordState = {
  drilling: { records: [], selectedWell: "", selectedDate: "", search: "", calendarMonth: "", page: 1, pageSize: DEFAULT_PAGE_SIZE, sortBy: "last" },
  completion: { records: [], selectedWell: "", selectedDate: "", search: "", calendarMonth: "", page: 1, pageSize: DEFAULT_PAGE_SIZE, sortBy: "last" },
  workover: { records: [], selectedWell: "", selectedDate: "", search: "", calendarMonth: "", page: 1, pageSize: DEFAULT_PAGE_SIZE, sortBy: "last" },
  move: { records: [], selectedWell: "", selectedDate: "", search: "", calendarMonth: "", page: 1, pageSize: DEFAULT_PAGE_SIZE, sortBy: "last" }
};
const translationPollTimers = { drilling: null, completion: null, workover: null, move: null };
const serverWarnings = { drilling: [], completion: [], workover: [], move: [] };
const wellStatsCache = {};
const analyticsState = {
  production: { payload: null, detailPage: 1, detailPageSize: DEFAULT_PAGE_SIZE, sortField: "", sortDir: "desc" },
  productionReport: {
    payload: null,
    detailPage: 1,
    detailPageSize: DEFAULT_PAGE_SIZE,
    sortField: "",
    sortDir: "desc",
    activeTab: "rig",
    availableRigs: [],
    availableProjects: [],
    selectedRigs: new Set(),
    selectedProjects: new Set(),
    rigTouched: false,
    projectTouched: false,
    selectionInitialized: false,
    sideSearch: "",
    wellQuery: ""
  },
  npt: {
    payload: null,
    detailPage: 1,
    detailPageSize: DEFAULT_PAGE_SIZE,
    sortField: "",
    sortDir: "desc",
    activeTab: "rig",
    availableRigs: [],
    availableProjects: [],
    selectedRigs: new Set(),
    selectedProjects: new Set(),
    rigTouched: false,
    projectTouched: false,
    selectionInitialized: false,
    sideSearch: "",
    keywordQuery: ""
  }
};
const REPORT_HOME_TARGETS = {
  drilling: "drilling-daily",
  completion: "completion-daily",
  workover: "workover-daily",
  move: "move-daily"
};
const initialReportRoute = parseInitialReportRoute();
const nptConfirmState = {
  items: [],
  filters: { wellbore: "", rig: "", status: "", scope: "all" },
  detail: null,
  scope: { all_rigs: false, rig: "" },
  loading: false,
  expandedRows: new Set()
};
const frontSession = {
  authenticated: false,
  user: null,
  permissions: {}
};
const uploadJobs = [];
let sourcePdfObjectUrl = "";
const reportNames = {
  drilling: "钻井日报",
  completion: "完井日报",
  workover: "修井日报",
  move: "搬迁日报"
};
const reportInputIds = {
  drilling: "pdfInput",
  completion: "completionPdfInput",
  workover: "workoverPdfInput",
  move: "movePdfInput"
};
let manualWellProfiles = [];

function ui(key) {
  return i18n[currentLanguage].ui[key] || i18n.zh.ui[key] || key;
}

function message(key, values = {}) {
  let text = i18n[currentLanguage].msg[key] || i18n.zh.msg[key] || key;
  Object.entries(values).forEach(([name, value]) => {
    text = text.replaceAll(`{${name}}`, value);
  });
  return text;
}

function labelFor(name) {
  return i18n[currentLanguage].fields[name] || i18n.zh.fields[name] || name;
}

function saveManualWellProfiles() {
  localStorage.setItem(MANUAL_WELLS_STORAGE_KEY, JSON.stringify(manualWellProfiles));
}

function normalizeManualWellProfile(profile = {}) {
  const now = new Date().toISOString();
  return {
    wellbore: String(profile.wellbore || "").trim(),
    rig: String(profile.rig || "").trim(),
    afeNumber: String(profile.afeNumber || "").trim(),
    note: String(profile.note || "").trim(),
    created_at: String(profile.created_at || now),
    updated_at: String(profile.updated_at || now),
  };
}

function manualProfileForWell(wellbore) {
  const normalized = String(wellbore || "").trim().toLowerCase();
  return manualWellProfiles.find((profile) => profile.wellbore.toLowerCase() === normalized) || null;
}

function activeMenuLink() {
  return document.querySelector(`.menu-link[data-menu-target="${activeMenuTarget}"]`);
}

function setDrillingSourceFile(filename = "") {
  drillingSourceFileName = filename;
  const sourceLabel = document.querySelector("#drillingSourceFile");
  if (sourceLabel) sourceLabel.textContent = filename || ui("sourceFileEmpty");
}

function setNptConfirmBreadcrumb(current = "") {
  const currentLabel = document.querySelector("[data-npt-breadcrumb-current]");
  const separator = document.querySelector("[data-npt-breadcrumb-separator]");
  const backButton = document.querySelector("[data-npt-global-back]");
  if (!currentLabel || !separator) return;
  const hasCurrent = Boolean(String(current || "").trim());
  currentLabel.textContent = hasCurrent ? current : "";
  currentLabel.hidden = !hasCurrent;
  separator.hidden = !hasCurrent;
  if (backButton) backButton.hidden = !hasCurrent;
}

function reportName(reportType) {
  const keys = { drilling: "menuDrillingDaily", completion: "menuCompletionDaily", workover: "menuWorkoverDaily", move: "menuMoveDaily" };
  return ui(keys[reportType]) || reportNames[reportType] || reportType;
}

function recordUploadInput(reportType) {
  return document.querySelector(`#${reportInputIds[reportType]}`);
}

function setReportMode(reportType, mode) {
  document.querySelectorAll(`[data-record-dashboard="${reportType}"]`).forEach((el) => {
    el.hidden = mode !== "records";
  });
  document.querySelectorAll(`[data-detail-view="${reportType}"]`).forEach((el) => {
    el.hidden = mode !== "detail";
  });
  document.querySelectorAll(`[data-back-records="${reportType}"], [data-save-report="${reportType}"]`).forEach((el) => {
    el.hidden = mode !== "detail" || (el.matches("[data-save-report]") && !frontCan("save"));
  });
  applyFrontPermissions();
  syncLanguageButtons();
}

function showReportRecords(reportType) {
  setReportMode(reportType, "records");
  refreshRecords(reportType);
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function frontCan(permission) {
  return Boolean(frontSession.permissions?.[permission]);
}

function frontRoleLabel(role) {
  return ({ admin: ui("roleAdmin"), engineer: ui("roleEngineer"), reviewer: ui("roleReviewer"), viewer: ui("roleViewer") }[role] || role || "-");
}

async function loadFrontSession() {
  try {
    const payload = await adminRequest("/api/admin/session");
    frontSession.authenticated = Boolean(payload.authenticated);
    frontSession.user = payload.user || null;
    frontSession.permissions = payload.permissions || {};
    if (!frontSession.authenticated) {
      window.location.href = `/login/?next=${encodeURIComponent("/web_form/")}`;
      return;
    }
    await Promise.all([loadTimeTypeValues(), loadNptReferenceValues()]);
    renderFrontUserBar();
    renderFrontAdminEntry();
    applyFrontPermissions();
  } catch (error) {
    console.error(error);
    showToast(error.message || "登录状态读取失败");
  }
}

function renderFrontUserBar() {
  document.querySelectorAll(".front-userbar").forEach((bar) => bar.remove());
  const user = frontSession.user || {};
  const name = user.display_name || user.username || "-";
  document.querySelectorAll(".module-page > .topbar .top-actions, .placeholder-topbar .top-actions").forEach((actions) => {
    const bar = document.createElement("div");
    bar.className = "front-userbar";
    bar.innerHTML = `
      <span class="front-user-name">${escapeHtml(name)}</span>
      <small>${escapeHtml(frontRoleLabel(user.role))}</small>
      <button class="link-button" type="button" data-front-logout>${escapeHtml(ui("logout"))}</button>
    `;
    actions.appendChild(bar);
  });
}

function renderFrontAdminEntry() {
  document.querySelectorAll("[data-front-admin-entry]").forEach((entry) => {
    entry.hidden = !frontCan("admin");
  });
}

function applyFrontPermissions() {
  const canImport = frontCan("import");
  const canEdit = frontCan("edit");
  const canSave = frontCan("save");
  const canExport = frontCan("export");
  document.body.dataset.userRole = frontSession.user?.role || "";
  document.querySelectorAll("#importPdf,#importCompletionPdf,#importWorkoverPdf,#importMovePdf,[data-record-upload]").forEach((el) => {
    el.hidden = !canImport;
    el.disabled = !canImport;
  });
  document.querySelectorAll("[data-save-report]").forEach((el) => {
    el.hidden = el.hidden || !canSave;
    el.disabled = !canSave;
  });
  document.querySelectorAll(".download-link,[data-analytics-export]").forEach((el) => {
    el.hidden = !canExport;
    el.disabled = !canExport;
  });
  document.querySelectorAll(".report-form input,.report-form textarea,.report-form select,.report-form button").forEach((el) => {
    el.disabled = !canEdit;
  });
  applyTranslationPreviewState();
}

async function logoutFront() {
  await adminRequest("/api/admin/logout", { method: "POST", body: "{}" }).catch(() => {});
  window.location.href = "/login/";
}

function showReportDetail(reportType) {
  setReportMode(reportType, "detail");
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function rememberRecord(reportType, payload = {}) {
  const recordId = payload.metadata?.record_id || "";
  currentRecordIds[reportType] = recordId;
  if (recordId && truthy(payload.metadata?.locked)) lockedRecordIds.add(recordId);
  if (reportType === "drilling") {
    const source = payload.metadata?.source_file || drillingSourceFileName || "";
    const suffix = recordId ? ` · ${ui("databaseRecord")}: ${recordId}` : "";
    const sourceLabel = document.querySelector("#drillingSourceFile");
    if (sourceLabel) sourceLabel.textContent = source ? `${source}${suffix}` : ui("sourceFileEmpty");
  }
  syncLanguageButtons();
}

function truthy(value) {
  return ["1", "true", "yes", "y", "locked", "confirmed"].includes(String(value || "").trim().toLowerCase());
}

function isCurrentReportLocked(reportType) {
  const recordId = currentRecordIds[reportType];
  if (!recordId) return false;
  if (lockedRecordIds.has(recordId)) return true;
  return recordState[reportType]?.records?.some((record) => record.record_id === recordId && truthy(record.locked));
}

function renderModulePlaceholder(link = activeMenuLink()) {
  if (!link || activeMenuTarget === "drilling-daily" || activeMenuTarget === "completion-daily" || activeMenuTarget === "workover-daily" || activeMenuTarget === "move-daily" || activeMenuTarget === "rig-production-summary" || activeMenuTarget === "production-report" || activeMenuTarget === "well-npt-confirm" || activeMenuTarget === "rig-npt-ranking") return;
  const parentKey = link.closest(".menu-group")?.querySelector(".menu-group-toggle span[data-i18n]")?.dataset.i18n || "moduleStatusPlanned";
  const parentLabel = document.querySelector("#placeholderModule");
  if (parentLabel) {
    parentLabel.dataset.i18n = parentKey;
    parentLabel.textContent = ui(parentKey);
  }
  document.querySelector("#placeholderTitle").textContent = ui(link.dataset.titleI18n);
  document.querySelector("#placeholderDescription").textContent = ui(link.dataset.descI18n);
}

function setActiveMenu(target) {
  activeMenuTarget = target;
  document.querySelectorAll(".menu-link[data-menu-target]").forEach((link) => {
    link.classList.toggle("active", link.dataset.menuTarget === target);
  });
  const isDrillingDaily = target === "drilling-daily";
  const isCompletionDaily = target === "completion-daily";
  const isWorkoverDaily = target === "workover-daily";
  const isMoveDaily = target === "move-daily";
  const isProductionSummary = target === "rig-production-summary";
  const isProductionReport = target === "production-report";
  const isNptStats = target === "well-npt-confirm";
  const isNptConfirm = target === "rig-npt-ranking";
  document.querySelector("#drillingDailyPage").hidden = !isDrillingDaily;
  document.querySelector("#drillingDailyPage").classList.toggle("active", isDrillingDaily);
  document.querySelector("#completionDailyPage").hidden = !isCompletionDaily;
  document.querySelector("#completionDailyPage").classList.toggle("active", isCompletionDaily);
  document.querySelector("#workoverDailyPage").hidden = !isWorkoverDaily;
  document.querySelector("#workoverDailyPage").classList.toggle("active", isWorkoverDaily);
  document.querySelector("#moveDailyPage").hidden = !isMoveDaily;
  document.querySelector("#moveDailyPage").classList.toggle("active", isMoveDaily);
  document.querySelector("#productionSummaryPage").hidden = !isProductionSummary;
  document.querySelector("#productionSummaryPage").classList.toggle("active", isProductionSummary);
  document.querySelector("#productionReportPage").hidden = !isProductionReport;
  document.querySelector("#productionReportPage").classList.toggle("active", isProductionReport);
  document.querySelector("#nptStatsPage").hidden = !isNptStats;
  document.querySelector("#nptStatsPage").classList.toggle("active", isNptStats);
  document.querySelector("#nptConfirmPage").hidden = !isNptConfirm;
  document.querySelector("#nptConfirmPage").classList.toggle("active", isNptConfirm);
  const showPlaceholder = !isDrillingDaily && !isCompletionDaily && !isWorkoverDaily && !isMoveDaily && !isProductionSummary && !isProductionReport && !isNptStats && !isNptConfirm;
  document.querySelector("#modulePlaceholder").hidden = !showPlaceholder;
  document.querySelector("#modulePlaceholder").classList.toggle("active", showPlaceholder);
  if (showPlaceholder) renderModulePlaceholder();
  if (isDrillingDaily) showReportRecords("drilling");
  if (isCompletionDaily) showReportRecords("completion");
  if (isWorkoverDaily) showReportRecords("workover");
  if (isMoveDaily) showReportRecords("move");
  if (isProductionSummary) loadAnalytics("production");
  if (isProductionReport) loadAnalytics("productionReport");
  if (isNptStats) loadAnalytics("npt");
  if (isNptConfirm) loadNptConfirmations();
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function setLeadingLabelText(label, text) {
  const firstText = [...label.childNodes].find((node) => node.nodeType === Node.TEXT_NODE && node.textContent.trim());
  if (firstText) {
    firstText.textContent = text;
  } else {
    label.insertBefore(document.createTextNode(text), label.firstChild);
  }
}

function applyLanguage(language) {
  if (!["zh", "es"].includes(language)) return;
  currentLanguage = language;
  localStorage.setItem("drillingReportLanguage", language);
  document.documentElement.lang = language === "zh" ? "zh-CN" : language;
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    el.textContent = ui(el.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
    el.placeholder = ui(el.dataset.i18nPlaceholder);
  });
  document.querySelectorAll("[data-i18n-title]").forEach((el) => {
    const label = ui(el.dataset.i18nTitle);
    el.title = label;
    el.setAttribute("aria-label", label);
  });
  document.querySelectorAll(".page-breadcrumb").forEach((el) => el.setAttribute("aria-label", ui("breadcrumbAria")));
  renderFrontUserBar();
  syncLanguageButtons();
  document.querySelectorAll("label").forEach((label) => {
    if (label.closest(".admin-page")) return;
    if (label.classList.contains("npt-date-range")) {
      setLeadingLabelText(label, currentLanguage === "es" ? "Rango de Fecha" : "日期起止");
      return;
    }
    const control = label.querySelector("[name]");
    if (control?.name === "scope_value") return;
    if (control) setLeadingLabelText(label, labelFor(control.name));
  });
  setDrillingSourceFile(drillingSourceFileName);
  if (currentRecordIds.drilling) rememberRecord("drilling", { metadata: { source_file: drillingSourceFileName, record_id: currentRecordIds.drilling } });
  Object.keys(recordState).forEach((reportType) => renderRecordDashboard(reportType));
  if (analyticsState.production.payload) {
    renderProductionAnalytics(analyticsState.production.payload);
    const productionFilter = document.querySelector('[data-analytics-filter="production"]');
    if (productionFilter) populateProductionSummaryScopeFilter(productionFilter, analyticsState.production.payload.filters || {});
  }
  if (analyticsState.productionReport.payload) renderProductionReportAnalytics(analyticsState.productionReport.payload);
  if (analyticsState.npt.payload) renderNptAnalytics(analyticsState.npt.payload);
  renderModulePlaceholder();
  validate();
  validateCompletion();
  validateWorkover();
  validateMove();
  updateAllSaveButtons();
  applyTranslationPreviewState();
}

function syncLanguageButtons() {
  document.querySelectorAll(".language-switch [data-lang]").forEach((button) => {
    const reportType = activeReportType(button);
    const language = button.dataset.lang;
    const selectedLanguage = reportType
      ? reportContentState[reportType]?.selectedLanguage || "original"
      : currentLanguage === "es" ? "es" : reportContentLanguageMode === "translated" ? "zh" : "original";
    const isLoading = reportTranslationBusy.language
      && language === reportTranslationBusy.language
      && (!reportTranslationBusy.reportType || reportType === reportTranslationBusy.reportType);
    const needsReportTranslation = language === "zh" && reportType;
    const disabledForTranslation = needsReportTranslation && !canSwitchReportTranslation(reportType);
    button.textContent = isLoading ? ui("translationRunningShort") : languageButtonLabel(language);
    button.classList.toggle("active", language === selectedLanguage);
    button.setAttribute("aria-pressed", language === selectedLanguage ? "true" : "false");
    button.classList.toggle("is-loading", Boolean(isLoading));
    button.disabled = Boolean(reportTranslationBusy.language) || disabledForTranslation;
    button.title = disabledForTranslation ? ui("translationNotReady") : "";
    button.setAttribute("aria-busy", isLoading ? "true" : "false");
  });
}

async function handleLanguageChoice(language, sourceButton = null) {
  if (reportTranslationBusy.language) return;
  const reportType = activeReportType(sourceButton);
  if (language === "original") {
    if (reportType) restoreReportOriginal(reportType);
    else restoreActiveReportOriginal();
    reportContentLanguageMode = "original";
    if (reportType) reportContentState[reportType].selectedLanguage = "original";
    applyLanguage("zh");
    renderLocalizedOperationDescriptions();
    syncLanguageButtons();
    return;
  }
  if (!["zh", "es"].includes(language)) return;
  if (language === "es") {
    if (reportType) restoreReportOriginal(reportType);
    else reportContentLanguageMode = "original";
    if (reportType) reportContentState[reportType].selectedLanguage = "es";
    applyLanguage("es");
    if (!reportType) renderLocalizedOperationDescriptions();
    syncLanguageButtons();
    return;
  }
  if (!reportType) {
    reportContentLanguageMode = "translated";
    applyLanguage(language);
    renderLocalizedOperationDescriptions();
    syncLanguageButtons();
    return;
  }
  if (reportType && !canSwitchReportTranslation(reportType)) {
    showToast(ui("translationNotReady"));
    return;
  }
  const previousLanguage = currentLanguage;
  const previousSelection = reportContentState[reportType]?.selectedLanguage || "original";
  setReportTranslationBusy(reportType, language);
  try {
    applyLanguage(language);
    const translated = await translateVisibleReportContent(language, reportType);
    if (translated) {
      reportContentLanguageMode = language;
      reportContentState[reportType].selectedLanguage = language;
    } else {
      reportContentState[reportType].selectedLanguage = previousSelection;
      applyLanguage(previousLanguage);
    }
  } finally {
    clearReportTranslationBusy();
  }
}

function setReportTranslationBusy(reportType, language) {
  reportTranslationBusy = { reportType: reportType || activeReportType() || "", language };
  syncLanguageButtons();
}

function clearReportTranslationBusy() {
  reportTranslationBusy = { reportType: "", language: "" };
  syncLanguageButtons();
}

function languageButtonLabel(language) {
  if (language === "original") return ui("originalReport");
  if (language === "zh") return "中";
  if (language === "es") return "ES";
  return language || "";
}

function canSwitchReportTranslation(reportType) {
  const record = currentReportRecord(reportType);
  if (!record) return false;
  return String(record.translation_status || "").toUpperCase() === "COMPLETED";
}

function currentReportRecord(reportType) {
  const recordId = currentRecordIds[reportType];
  if (!recordId) return null;
  return recordState[reportType]?.records?.find((record) => record.record_id === recordId) || null;
}

function activeReportType(sourceEl = null) {
  const pageFromSource = sourceEl?.closest?.(".module-page");
  if (pageFromSource && !pageFromSource.hidden && pageFromSource.classList.contains("active")) {
    const sourceReportType = reportTypeFromPage(pageFromSource);
    if (sourceReportType && isReportDetailVisible(sourceReportType)) return sourceReportType;
  }
  return ["drilling", "completion", "workover", "move"].find((reportType) => {
    const page = reportPage(reportType);
    if (!page || page.hidden || !page.classList.contains("active")) return false;
    return isReportDetailVisible(reportType);
  }) || "";
}

function reportTypeFromPage(page) {
  const ids = {
    drillingDailyPage: "drilling",
    completionDailyPage: "completion",
    workoverDailyPage: "workover",
    moveDailyPage: "move",
  };
  return ids[page?.id] || "";
}

function isReportDetailVisible(reportType) {
  const page = reportPage(reportType);
  if (!page || page.hidden || !page.classList.contains("active")) return false;
  return [...page.querySelectorAll(`[data-detail-view="${reportType}"]`)].some((el) => !el.hidden && el.offsetParent !== null);
}

function reportPage(reportType) {
  const ids = {
    drilling: "drillingDailyPage",
    completion: "completionDailyPage",
    workover: "workoverDailyPage",
    move: "moveDailyPage",
  };
  return document.querySelector(`#${ids[reportType]}`);
}

function clonePayload(payload) {
  return JSON.parse(JSON.stringify(payload || {}));
}

function setReportOriginalPayload(reportType, payload) {
  if (!reportContentState[reportType]) return;
  reportContentState[reportType] = {
    mode: "original",
    selectedLanguage: currentLanguage === "es" ? "es" : "original",
    original: clonePayload(payload),
    cache: {},
    targetLanguage: "",
  };
  reportContentLanguageMode = "original";
  syncLanguageButtons();
  applyTranslationPreviewState(reportType);
}

function captureOriginalReport(reportType) {
  const state = reportContentState[reportType];
  if (!state) return null;
  if (state.mode === "original" && state.original) return clonePayload(state.original);
  if (!state.original) {
    state.original = clonePayload(reportPayload(reportType));
    state.cache = {};
  }
  return clonePayload(state.original);
}

function markReportOriginalEdited(reportType) {
  const state = reportContentState[reportType];
  if (!state || state.mode !== "original") return;
  state.original = null;
  state.cache = {};
}

function restoreActiveReportOriginal() {
  const reportType = activeReportType();
  if (!reportType) return;
  restoreReportOriginal(reportType);
}

function restoreReportOriginal(reportType) {
  const state = reportContentState[reportType];
  if (!state) return;
  const payload = state.original ? clonePayload(state.original) : reportPayload(reportType);
  state.mode = "original";
  state.targetLanguage = "";
  renderReportPayload(reportType, payload);
  applyFrontPermissions();
  updateSaveButton(reportType);
}

async function translateVisibleReportContent(targetLanguage, explicitReportType = "") {
  const reportType = explicitReportType || activeReportType();
  if (!reportType) {
    showToast(ui("translationFailed"));
    return false;
  }
  const sourcePayload = captureOriginalReport(reportType);
  if (!sourcePayload) return false;
  const state = reportContentState[reportType];
  try {
    showToast(ui("translationRunning"));
    let result = state.cache[targetLanguage];
    if (!result && currentRecordIds[reportType]) {
      const response = await fetch("/api/load-report", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ record_id: currentRecordIds[reportType], lang: apiLanguage(targetLanguage) }),
      });
      result = await response.json();
      if (response.ok) {
        state.cache[targetLanguage] = result;
      } else {
        throw new Error(result.error || "Load failed");
      }
    }
    if (!result) throw new Error(ui("translationNotReady"));
    renderReportPayload(reportType, result.translated_payload || result || sourcePayload);
    state.mode = "translated";
    state.targetLanguage = targetLanguage;
    state.lastResult = result;
    applyFrontPermissions();
    updateSaveButton(reportType);
    showToast(ui("translationReady"));
    return true;
  } catch (error) {
    console.error(error);
    const detail = error?.message ? `：${error.message}` : "";
    showToast(`${ui("translationFailed")}${detail}`);
    return false;
  }
}

function apiLanguage(language) {
  return language === "zh" ? "zh-CN" : language;
}

function renderReportPayload(reportType, payload = {}) {
  if (reportType === "drilling") {
    applyReportFields(payload.report_fields || {});
    setDrillingSourceFile(payload.metadata?.source_file || drillingSourceFileName || "");
    loadRows({
      surveyTable: rowsFromPayload(payload.survey_data, "surveyTable"),
      bhaTable: rowsFromPayload(payload.bha_components, "bhaTable"),
      operationsTable: rowsFromPayload(payload.operations, "operationsTable"),
      fluidLossTable: rowsFromPayload(payload.fluid_losses, "fluidLossTable"),
      bulkTable: rowsFromPayload(payload.bulks, "bulkTable")
    });
  }
  if (reportType === "completion") {
    applyReportFields(payload.report_fields || {}, completionForm);
    loadRows({
      completionOperationsTable: rowsFromPayload(payload.operations, "completionOperationsTable"),
      completionBulkTable: rowsFromPayload(payload.bulks, "completionBulkTable"),
      perforationIntervalsTable: rowsFromPayload(payload.perforation_intervals, "perforationIntervalsTable")
    }, completionTableIds);
  }
  if (reportType === "workover") {
    applyReportFields(payload.report_fields || {}, workoverForm);
    loadRows({
      workoverOperationsTable: rowsFromPayload(payload.operations, "workoverOperationsTable"),
      workoverBulkTable: rowsFromPayload(payload.bulks, "workoverBulkTable"),
      workoverIntervalsTable: rowsFromPayload(payload.perforation_intervals, "workoverIntervalsTable")
    }, workoverTableIds);
  }
  if (reportType === "move") {
    applyReportFields(payload.report_fields || {}, moveForm);
    loadRows({
      moveOperationsTable: rowsFromPayload(payload.operations, "moveOperationsTable")
    }, moveTableIds);
  }
}

function applyTranslationPreviewState(reportType = "") {
  const reportTypes = reportType ? [reportType] : Object.keys(reportContentState);
  reportTypes.forEach((type) => {
    const page = reportPage(type);
    if (!page) return;
    const preview = reportContentState[type]?.mode === "translated";
    page.classList.toggle("translation-preview-mode", preview);
    updateTranslationPreviewNotice(type, preview);
    if (!preview) return;
    page.querySelectorAll(".report-form input,.report-form textarea,.report-form select,.report-form button").forEach((el) => {
      el.disabled = true;
    });
  });
}

function updateTranslationPreviewNotice(reportType, show) {
  const page = reportPage(reportType);
  if (!page) return;
  let notice = page.querySelector(`[data-translation-preview-notice="${reportType}"]`);
  if (!show) {
    notice?.remove();
    return;
  }
  if (!notice) {
    notice = document.createElement("div");
    notice.className = "translation-preview-notice";
    notice.dataset.translationPreviewNotice = reportType;
    const statusStrip = page.querySelector(`[data-detail-view="${reportType}"].status-strip`);
    if (statusStrip) statusStrip.insertAdjacentElement("afterend", notice);
    else page.querySelector(`[data-detail-view="${reportType}"]`)?.insertAdjacentElement("beforebegin", notice);
  }
  notice.textContent = ui("translationPreviewNotice");
}

function makeInput(field, value = "") {
  const control = field.type === "textarea" ? document.createElement("textarea") : field.type === "select" ? document.createElement("select") : document.createElement("input");
  control.name = field.name;
  if (field.type === "textarea") {
    control.classList.add("multiline-source-text");
    control.rows = Math.min(12, Math.max(3, String(value || "").split("\n").length));
  }
  if (field.type === "select") {
    (field.options || []).forEach((optionValue) => {
      const option = document.createElement("option");
      option.value = optionValue;
      option.textContent = optionValue;
      const reference = timeTypeValues.find((item) => item.value_code === optionValue);
      if (field.name === "op_type" && reference?.display_color) option.style.color = reference.display_color;
      control.appendChild(option);
    });
  }
  control.value = value;
  if (field.name === "op_type") {
    if (!timeTypeCodes().includes(String(value || "").trim().toUpperCase())) control.selectedIndex = 0;
    control.classList.add("operation-type-select");
    syncOperationTypeStyle(control);
    control.addEventListener("change", () => syncOperationTypeStyle(control));
  }
  if (field.type === "number") {
    control.type = "number";
    control.step = "0.01";
  }
  return control;
}

function syncOperationTypeStyle(control) {
  const type = String(control.value || "").trim().toLowerCase();
  control.classList.remove("type-p", "type-sc", "type-npt");
  control.removeAttribute("data-reference-color");
  control.style.removeProperty("--operation-type-color");
  const reference = timeTypeValues.find((item) => String(item.value_code || "").trim().toLowerCase() === type);
  if (reference?.display_color) {
    control.dataset.referenceColor = reference.display_color;
    control.style.setProperty("--operation-type-color", reference.display_color);
  }
  if (["p", "sc", "npt"].includes(type)) control.classList.add(`type-${type}`);
}

function applyTimeTypeValues(items = []) {
  const normalized = items
    .map((item) => ({
      value_code: String(item.value_code || "").trim().toUpperCase(),
      value_name: String(item.value_name || item.value_code || "").trim(),
      display_color: String(item.display_color || "").trim(),
    }))
    .filter((item) => item.value_code);
  if (normalized.length) timeTypeValues = normalized;
  const codes = timeTypeCodes();
  ["operationsTable", "completionOperationsTable", "workoverOperationsTable", "moveOperationsTable"].forEach((tableId) => {
    const field = tableSchemas[tableId].find((item) => item.name === "op_type");
    if (field) field.options = [...codes];
  });
  document.querySelectorAll("select.operation-type-select").forEach((control) => {
    const previous = String(control.value || "").trim().toUpperCase();
    control.replaceChildren(...codes.map((code) => {
      const option = document.createElement("option");
      const reference = timeTypeValues.find((item) => item.value_code === code);
      option.value = code;
      option.textContent = reference?.value_name || code;
      if (reference?.display_color) option.style.color = reference.display_color;
      return option;
    }));
    control.value = codes.includes(previous) ? previous : codes[0] || "";
    syncOperationTypeStyle(control);
  });
}

async function loadTimeTypeValues() {
  try {
    const payload = await adminRequest("/api/reference-data/TIME_TYPE");
    applyTimeTypeValues(payload.items || []);
  } catch (error) {
    console.warn("时效类型附录加载失败，使用内置安全值。", error);
    applyTimeTypeValues(DEFAULT_TIME_TYPE_VALUES);
  }
}

async function loadNptReferenceValues() {
  await Promise.all(Object.keys(DEFAULT_NPT_REFERENCE_VALUES).map(async (category) => {
    try {
      const payload = await adminRequest(`/api/reference-data/${category}`);
      const values = (payload.items || [])
        .map((item) => [String(item.value_code || "").trim(), String(item.value_name || item.value_code || "").trim()])
        .filter(([value]) => value);
      nptReferenceValues[category] = values.length ? values : [...DEFAULT_NPT_REFERENCE_VALUES[category]];
    } catch (error) {
      console.warn(`${category}附录加载失败，使用内置安全值。`, error);
      nptReferenceValues[category] = [...DEFAULT_NPT_REFERENCE_VALUES[category]];
    }
  }));
}

function renderTableRow(tableId, values = []) {
  const tbody = document.querySelector(`#${tableId} tbody`);
  const tr = document.createElement("tr");
  tableSchemas[tableId].forEach((field, index) => {
    const td = document.createElement("td");
    td.appendChild(makeInput(field, values[index] ?? ""));
    tr.appendChild(td);
  });
  tbody.appendChild(tr);
}

function loadRows(rows = {}, tableIds = drillingTableIds) {
  tableIds.forEach((tableId) => {
    document.querySelector(`#${tableId} tbody`).innerHTML = "";
    (rows[tableId] || []).forEach((row) => renderTableRow(tableId, row));
  });
  if (tableIds.some((tableId) => completionTableIds.includes(tableId))) validateCompletion();
  if (tableIds.some((tableId) => workoverTableIds.includes(tableId))) validateWorkover();
  if (tableIds.some((tableId) => moveTableIds.includes(tableId))) validateMove();
  if (tableIds.some((tableId) => drillingTableIds.includes(tableId))) validate();
}

function escapeHtml(value = "") {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;", "'": "&#39;" })[char]);
}

function todayIsoDate() {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(now.getDate()).padStart(2, "0")}`;
}

function latestReportDate(records = []) {
  const dates = records
    .map((record) => String(record.reportDate || "").slice(0, 10))
    .filter(Boolean)
    .sort();
  return dates[dates.length - 1] || "";
}

function requiresBoundaryHoursValidation(reportType, data = {}) {
  const reportDate = String(data.reportDate || "").slice(0, 10);
  const wellbore = String(data.wellbore || "").trim().toUpperCase();
  if (!reportDate || !wellbore) return true;
  const currentRecordId = String(currentRecordIds[reportType] || "");
  const dates = (recordState[reportType]?.records || [])
    .filter((record) => String(record.record_id || "") !== currentRecordId)
    .filter((record) => String(record.wellbore || "").trim().toUpperCase() === wellbore)
    .map((record) => String(record.reportDate || "").slice(0, 10))
    .filter(Boolean);
  dates.push(reportDate);
  dates.sort();
  return reportDate === dates[0] || reportDate === dates[dates.length - 1];
}

function normalizeReportType(value) {
  const reportType = String(value || "").trim().toLowerCase();
  return REPORT_HOME_TARGETS[reportType] ? reportType : "drilling";
}

function reportTypeFromMenuTarget(target) {
  return Object.entries(REPORT_HOME_TARGETS).find(([, menuTarget]) => menuTarget === target)?.[0] || "";
}

function parseInitialReportRoute() {
  const params = new URLSearchParams(window.location.search);
  const target = params.get("page") || params.get("target") || "";
  const reportType = reportTypeFromMenuTarget(target);
  return {
    target: reportType ? target : "drilling-daily",
    reportType: reportType || "drilling",
    well: (params.get("well") || params.get("wellbore") || "").trim(),
    applied: false
  };
}

function reportHomeUrl(reportType, wellbore) {
  const url = new URL(window.location.href);
  const params = new URLSearchParams();
  params.set("page", REPORT_HOME_TARGETS[normalizeReportType(reportType)] || REPORT_HOME_TARGETS.drilling);
  if (wellbore) params.set("well", wellbore);
  url.search = params.toString();
  url.hash = "";
  return url.toString();
}

function openReportHomeForWell(reportType, wellbore) {
  if (!wellbore) return;
  window.open(reportHomeUrl(reportType, wellbore), "_blank", "noopener");
}

function applyInitialWellSelection(reportType) {
  if (initialReportRoute.applied || initialReportRoute.reportType !== reportType || !initialReportRoute.well) return;
  const state = recordState[reportType];
  state.selectedWell = initialReportRoute.well;
  state.selectedDate = "";
  state.calendarMonth = "";
  state.page = 1;
  initialReportRoute.applied = true;
}

async function refreshRecords(reportType, options = {}) {
  const statusOnly = options.statusOnly === true;
  const previousRecords = recordState[reportType].records || [];
  try {
    const response = await fetch(`/api/records?report_type=${encodeURIComponent(reportType)}`);
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || "Records failed");
    const nextRecords = payload.records || [];
    recordState[reportType].records = nextRecords;
    recordState[reportType].records.forEach((record) => {
      if (truthy(record.locked)) lockedRecordIds.add(record.record_id);
    });
    if (statusOnly && !recordsRequireDashboardRender(previousRecords, nextRecords)) {
      patchRecordTranslationStatuses(reportType, nextRecords);
      scheduleTranslationStatusRefresh(reportType);
      return;
    }
    invalidateWellStats(reportType);
    scheduleTranslationStatusRefresh(reportType);
  } catch (error) {
    console.error(error);
    if (statusOnly) {
      scheduleTranslationStatusRefresh(reportType);
      return;
    }
    recordState[reportType].records = [];
  }
  applyInitialWellSelection(reportType);
  renderRecordDashboard(reportType);
  syncLanguageButtons();
}

function scheduleTranslationStatusRefresh(reportType) {
  if (translationPollTimers[reportType]) {
    clearTimeout(translationPollTimers[reportType]);
    translationPollTimers[reportType] = null;
  }
  const hasRunningTranslation = (recordState[reportType]?.records || []).some((record) => {
    const status = String(record.translation_status || "").toUpperCase();
    return ["QUEUED", "IN_PROGRESS"].includes(status);
  });
  if (hasRunningTranslation) {
    translationPollTimers[reportType] = setTimeout(() => refreshRecords(reportType, { statusOnly: true }), 5000);
  }
}

function recordsRequireDashboardRender(previousRecords = [], nextRecords = []) {
  if (previousRecords.length !== nextRecords.length) return true;
  const structuralFields = ["record_id", "reportDate", "wellbore", "report_type", "source_file", "validation_status", "validation_warnings", "locked", "p_hours", "sc_hours", "npt_hours"];
  return previousRecords.some((record, index) => {
    const nextRecord = nextRecords[index] || {};
    return structuralFields.some((field) => String(record[field] ?? "") !== String(nextRecord[field] ?? ""));
  });
}

function patchRecordTranslationStatuses(reportType, records = []) {
  const host = document.querySelector(`[data-record-dashboard="${reportType}"]`);
  if (!host) return;
  const recordsById = new Map(records.map((record) => [String(record.record_id || ""), record]));
  host.querySelectorAll("[data-record-status-id]").forEach((statusCell) => {
    const record = recordsById.get(String(statusCell.dataset.recordStatusId || ""));
    if (record) statusCell.innerHTML = recordStatusMarkup(record);
  });
}

function invalidateWellStats(reportType) {
  Object.keys(wellStatsCache).forEach((key) => {
    if (key.startsWith(`${reportType}:`)) delete wellStatsCache[key];
  });
}

function renderRecordDashboard(reportType) {
  const host = document.querySelector(`[data-record-dashboard="${reportType}"]`);
  if (!host) return;
  const state = recordState[reportType];
  const records = state.records;
  const jobs = uploadJobs.filter((job) => job.reportType === reportType);
  const wells = [...new Set(records.map((record) => record.wellbore).filter(Boolean))];
  const wellList = sortWells(wells, records, state.sortBy).filter((well) => !state.search || well.toLowerCase().includes(state.search.toLowerCase()));
  if (!state.selectedWell || !wellList.includes(state.selectedWell)) state.selectedWell = wellList[0] || "";
  const selectedRecords = records.filter((record) => !state.selectedWell || record.wellbore === state.selectedWell);
  const selectedJobs = jobs.filter((job) => !state.selectedWell || !job.wellbore || job.wellbore === state.selectedWell);
  const monthBase = state.calendarMonth || latestReportDate(selectedRecords) || todayIsoDate();
  const monthRecords = recordsForMonth(selectedRecords, monthBase);
  const uploadedDays = new Set(monthRecords.map((record) => dayOfMonth(record.reportDate)));
  const showCalendarStages = reportType === "drilling";
  const calendarStages = showCalendarStages ? calendarStageDays(monthRecords) : { move: new Set(), drilling: new Set() };
  const calendarOperations = calendarOperationDays(monthRecords);
  const wellStats = cachedWellStats(reportType, state.selectedWell);
  const nptShare = percentage(wellStats.npt_hours, wellStats.total_hours);
  const pShare = percentage(wellStats.p_hours, wellStats.total_hours);
  const scShare = percentage(wellStats.sc_hours, wellStats.total_hours);
  const stageDays = showCalendarStages ? calendarStageDays(selectedRecords) : { move: new Set(), drilling: new Set() };
  const moveDayCount = stageDays.move.size;
  const drillingDayCount = stageDays.drilling.size;
  const tableRecords = sortedRecords(state.selectedDate ? selectedRecords.filter((record) => record.reportDate === state.selectedDate) : selectedRecords);
  const totalTableRows = tableRecords.length + selectedJobs.length;
  const pageSize = normalizedPageSize(state.pageSize);
  const totalPages = Math.max(1, Math.ceil(totalTableRows / pageSize));
  state.page = Math.min(Math.max(Number(state.page) || 1, 1), totalPages);

  host.innerHTML = `
    <div class="record-layout">
      <aside class="well-panel panel">
        <div class="panel-heading">
          <h2>${ui("wellSelection")}</h2>
        </div>
        <input class="well-search" type="search" value="${escapeHtml(state.search)}" placeholder="${ui("searchWell")}" data-well-search="${reportType}" />
        <div class="well-sort-toggle" role="group" aria-label="${escapeHtml(ui("wellSortAria"))}">
          ${wellSortButton(reportType, state.sortBy, "first", ui("sortFirstUpload"))}
          ${wellSortButton(reportType, state.sortBy, "last", ui("sortLastUpload"))}
          ${wellSortButton(reportType, state.sortBy, "name", ui("sortWellName"))}
        </div>
        <div class="well-list">
          ${wellList.map((well, index) => {
            const wellRecords = records.filter((record) => record.wellbore === well);
            const hasNpt = wellHasNpt(wellRecords);
            const uploadedCount = uniqueReportDays(wellRecords).size;
            return `
            <button class="well-card ${well === state.selectedWell ? "active" : ""}" type="button" data-well="${escapeHtml(well)}" data-report-type="${reportType}">
              <span class="well-icon">${String(index + 1).padStart(2, "0")}</span>
              <span><strong>${escapeHtml(well)}</strong><small>${ui("uploadedDays")} ${uploadedCount} ${ui("daysUnit")}</small></span>
              <i class="well-status-marker ${hasNpt ? "dot-npt" : "dot-no-npt"}" role="img" aria-label="${escapeHtml(ui(hasNpt ? "wellHasNpt" : "wellNoNpt"))}" title="${escapeHtml(ui(hasNpt ? "wellHasNptTitle" : "wellNoNptTitle"))}"></i>
            </button>
            `;
          }).join("") || `<div class="empty-well-list">${escapeHtml(ui("noWells"))}</div>`}
        </div>
      </aside>
      <section class="record-main">
        <div class="record-top-grid">
          <section class="panel calendar-panel">
            <div class="panel-heading calendar-heading">
              <h2>${ui("reportCalendar")}</h2>
              <div class="calendar-nav">
                <button class="icon-button" type="button" data-report-type="${reportType}" data-month-nav="-1" aria-label="${ui("prevMonth")}">‹</button>
                <strong class="calendar-month">${calendarMonthLabel(monthBase)}</strong>
                <button class="icon-button" type="button" data-report-type="${reportType}" data-month-nav="1" aria-label="${ui("nextMonth")}">›</button>
              </div>
            </div>
            ${calendarMarkup(reportType, monthBase, uploadedDays, calendarStages, calendarOperations)}
          </section>
          <section class="panel record-summary-panel">
            ${wellBasicInfoMarkup(reportType, state.selectedWell, selectedRecords)}
            <div class="record-summary-grid ${showCalendarStages ? "" : "without-stages"}">
              ${summaryCard("metricWorkDays", `${uniqueReportDays(selectedRecords).size}`, ui("daysUnit"), "blue")}
              ${summaryCard("metricNptShare", `${formatHours(wellStats.npt_hours)} h`, `${nptShare}`, "red")}
              ${summaryCard("metricPScShare", `P ${pShare}`, `SC ${scShare}`, "green")}
              ${showCalendarStages ? summaryCard("metricMoveDrillingDays", `${moveDayCount} / ${drillingDayCount}`, `搬迁 ${moveDayCount} ${ui("daysUnit")} / 钻井 ${drillingDayCount} ${ui("daysUnit")}`, "violet") : ""}
            </div>
            <div class="calendar-hint">${ui("calendarHint")}</div>
          </section>
        </div>
        <section class="panel upload-record-panel">
          <div class="panel-heading record-table-heading">
            <h2>${ui("uploadRecords")}</h2>
            <div class="record-actions">
              <button class="button secondary small" type="button" data-record-upload="${reportType}">${ui("importPdf")}</button>
            </div>
          </div>
          <div class="table-wrap">
            ${recordTableMarkup(reportType, tableRecords, selectedJobs, state.page, pageSize)}
          </div>
        </section>
      </section>
    </div>
  `;
  requestWellStats(reportType, state.selectedWell);
  applyFrontPermissions();
}

function wellSortButton(reportType, activeSort, sortValue, label) {
  return `<button class="${activeSort === sortValue ? "active" : ""}" type="button" data-well-sort="${sortValue}" data-report-type="${reportType}">${escapeHtml(label)}</button>`;
}

function sortWells(wells, records, sortBy = "last") {
  const metrics = wellDateMetrics(records);
  return [...wells].sort((left, right) => {
    const leftMetrics = metrics[left] || {};
    const rightMetrics = metrics[right] || {};
    if (sortBy === "name") return left.localeCompare(right, "zh-Hans-CN", { numeric: true, sensitivity: "base" });
    const key = sortBy === "first" ? "first" : "last";
    const dateCompare = String(rightMetrics[key] || "").localeCompare(String(leftMetrics[key] || ""));
    if (dateCompare !== 0) return dateCompare;
    return left.localeCompare(right, "zh-Hans-CN", { numeric: true, sensitivity: "base" });
  });
}

function wellDateMetrics(records) {
  return records.reduce((metrics, record) => {
    const well = record.wellbore;
    const dateValue = record.reportDate || "";
    if (!well || !dateValue) return metrics;
    const item = metrics[well] || { first: dateValue, last: dateValue };
    if (dateValue < item.first) item.first = dateValue;
    if (dateValue > item.last) item.last = dateValue;
    metrics[well] = item;
    return metrics;
  }, {});
}

function shiftMonth(reportType, delta) {
  const state = recordState[reportType];
  const selectedRecords = state.records.filter((record) => !state.selectedWell || record.wellbore === state.selectedWell);
  const latest = latestReportDate(selectedRecords) || todayIsoDate();
  const current = (state.calendarMonth || latest).slice(0, 7);
  const [year, month] = current.split("-").map(Number);
  const next = new Date(year, (month - 1) + delta, 1);
  state.calendarMonth = `${next.getFullYear()}-${String(next.getMonth() + 1).padStart(2, "0")}`;
  renderRecordDashboard(reportType);
}

function wellBasicInfoMarkup(reportType, wellbore, records = []) {
  const latestRecord = sortedRecords(records)[0] || null;
  const stats = cachedWellStats(reportType, wellbore);
  const source = latestRecord ? "日报解析" : "待上传日报";
  const items = [
    ["井队", stats.rig || latestRecord?.rig || "-"],
    ["AFE", stats.afe_number || latestRecord?.afeNumber || "-"],
    ...wellBasicDateItems(reportType, stats, records),
  ];
  return `
    <section class="well-basic-card" aria-label="当前井基础信息">
      <div class="well-basic-heading">
        <div>
          <span>当前井基础信息</span>
          <strong>${escapeHtml(latestRecord?.wellbore || wellbore || "-")}</strong>
        </div>
        <small>${escapeHtml(source)}</small>
      </div>
      <div class="well-basic-grid">
        ${items.map(([label, value]) => `<span><small>${escapeHtml(label)}</small><b>${escapeHtml(value)}</b></span>`).join("")}
      </div>
    </section>
  `;
}

function wellBasicDateItems(reportType, stats = {}, records = []) {
  if (reportType === "drilling") {
    return [
      ["搬迁日期", stats.move_date || firstStageDate(records, "move") || "-"],
      ["开钻日期", stats.drilling_start_date || firstStageDate(records, "drilling") || "-"],
    ];
  }
  if (reportType === "completion") {
    return [["完井日期", stats.completion_date || "-"]];
  }
  if (reportType === "workover") {
    return [["修井日期", stats.workover_date || "-"]];
  }
  if (reportType === "move") {
    return [["搬迁日期", stats.move_date || "-"]];
  }
  return [];
}

function openAddWellModal(reportType) {
  if (!frontCan("edit")) return showToast("当前账号没有编辑权限");
  const currentWell = recordState[reportType]?.selectedWell || "";
  const existing = manualProfileForWell(currentWell) || {};
  document.querySelector(".well-profile-modal")?.remove();
  const modal = document.createElement("div");
  modal.className = "admin-modal well-profile-modal";
  modal.innerHTML = `
    <div class="admin-modal-backdrop" data-well-modal-close></div>
    <section class="admin-modal-panel well-profile-modal-panel" role="dialog" aria-modal="true" aria-label="添加新井">
      <header class="admin-modal-header">
        <div>
          <p class="page-kicker">WELL PROFILE</p>
          <h2>${ui("addWell")}</h2>
        </div>
        <button class="icon-button" type="button" data-well-modal-close aria-label="关闭">×</button>
      </header>
      <div class="admin-modal-body">
        <div class="well-profile-note">手动资料用于未上传日报时的井档案展示；同井号上传日报后，展示信息以日报解析结果为准。</div>
        <div class="well-profile-form">
          <label>井号<input name="wellbore" required value="${escapeHtml(existing.wellbore || "")}" placeholder="例如 PCNC-040" /></label>
          <label>井队<input name="rig" value="${escapeHtml(existing.rig || "")}" placeholder="例如 SINOPEC 248" /></label>
          <label>AFE<input name="afeNumber" value="${escapeHtml(existing.afeNumber || "")}" /></label>
          <label class="wide">备注<textarea name="note">${escapeHtml(existing.note || "")}</textarea></label>
        </div>
      </div>
      <footer class="admin-modal-footer">
        <div>
          ${existing.wellbore ? `<button class="button secondary" type="button" data-delete-well-profile="${escapeHtml(reportType)}">删除手动井</button>` : ""}
        </div>
        <button class="button secondary" type="button" data-well-modal-close>取消</button>
        <button class="button" type="button" data-save-well-profile="${escapeHtml(reportType)}">保存井信息</button>
      </footer>
    </section>
  `;
  document.body.appendChild(modal);
  document.body.classList.add("modal-open");
  modal.querySelector('[name="wellbore"]')?.focus();
}

function closeWellProfileModal() {
  document.querySelector(".well-profile-modal")?.remove();
  document.body.classList.remove("modal-open");
}

function saveWellProfileFromModal(reportType) {
  const modal = document.querySelector(".well-profile-modal");
  if (!modal) return;
  const profile = normalizeManualWellProfile({
    wellbore: modal.querySelector('[name="wellbore"]')?.value,
    rig: modal.querySelector('[name="rig"]')?.value,
    afeNumber: modal.querySelector('[name="afeNumber"]')?.value,
    note: modal.querySelector('[name="note"]')?.value,
  });
  if (!profile.wellbore) {
    showToast("请填写井号");
    modal.querySelector('[name="wellbore"]')?.focus();
    return;
  }
  const existingIndex = manualWellProfiles.findIndex((item) => item.wellbore.toLowerCase() === profile.wellbore.toLowerCase());
  if (existingIndex >= 0) {
    profile.created_at = manualWellProfiles[existingIndex].created_at;
    manualWellProfiles[existingIndex] = profile;
  } else {
    manualWellProfiles.push(profile);
  }
  saveManualWellProfiles();
  recordState[reportType].selectedWell = profile.wellbore;
  recordState[reportType].selectedDate = "";
  recordState[reportType].page = 1;
  closeWellProfileModal();
  renderRecordDashboard(reportType);
  showToast("井信息已保存");
}

function deleteWellProfileFromModal(reportType) {
  const modal = document.querySelector(".well-profile-modal");
  const wellbore = modal?.querySelector('[name="wellbore"]')?.value.trim() || "";
  if (!wellbore) return;
  manualWellProfiles = manualWellProfiles.filter((item) => item.wellbore.toLowerCase() !== wellbore.toLowerCase());
  saveManualWellProfiles();
  if (recordState[reportType]?.selectedWell?.toLowerCase() === wellbore.toLowerCase()) {
    recordState[reportType].selectedWell = "";
    recordState[reportType].selectedDate = "";
    recordState[reportType].page = 1;
  }
  closeWellProfileModal();
  renderRecordDashboard(reportType);
  showToast("手动井已删除");
}

function summaryCard(labelKey, value, caption, tone) {
  return `
    <div class="record-summary-card ${tone}">
      <span>${ui(labelKey)}</span>
      <strong>${metricValueHtml(value)}</strong>
      <small>${escapeHtml(caption)}</small>
    </div>
  `;
}

function cachedWellStats(reportType, wellbore) {
  const key = wellStatsKey(reportType, wellbore);
  return wellStatsCache[key]?.data || { days: 0, total_hours: 0, npt_hours: 0, p_hours: 0, sc_hours: 0 };
}

function wellStatsKey(reportType, wellbore) {
  return `${reportType}:${wellbore || ""}`;
}

async function requestWellStats(reportType, wellbore) {
  if (!wellbore) return;
  const key = wellStatsKey(reportType, wellbore);
  if (wellStatsCache[key]?.loading || wellStatsCache[key]?.loaded) return;
  wellStatsCache[key] = { loading: true, data: cachedWellStats(reportType, wellbore) };
  try {
    const response = await fetch(`/api/well-stats?report_type=${encodeURIComponent(reportType)}&wellbore=${encodeURIComponent(wellbore)}`);
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || "Stats failed");
    wellStatsCache[key] = { loaded: true, data: payload };
    if (recordState[reportType]?.selectedWell === wellbore) renderRecordDashboard(reportType);
  } catch (error) {
    console.error(error);
    wellStatsCache[key] = { loaded: true, data: cachedWellStats(reportType, wellbore) };
  }
}

function recordsForMonth(records, dateValue) {
  const month = (dateValue || "").slice(0, 7);
  return records.filter((record) => (record.reportDate || "").startsWith(month));
}

function sortedRecords(records) {
  return [...records].sort((a, b) => {
    const left = `${a.reportDate || ""} ${a.updated_at || a.created_at || ""}`;
    const right = `${b.reportDate || ""} ${b.updated_at || b.created_at || ""}`;
    return right.localeCompare(left);
  });
}

function dayOfMonth(dateValue) {
  const day = Number((dateValue || "").slice(8, 10));
  return Number.isFinite(day) ? day : 0;
}

function uniqueReportDays(records) {
  return new Set(records.map((record) => record.reportDate).filter(Boolean));
}

function wellHasNpt(records) {
  return records.some((record) => Math.max(0, Number(record.npt_hours) || 0) > 0);
}

function calendarStageDays(records) {
  return (records || []).reduce((days, record) => {
    const day = dayOfMonth(record.reportDate);
    if (!day) return days;
    const stage = recordStage(record);
    if (stage === "move") days.move.add(day);
    if (stage === "drilling") days.drilling.add(day);
    return days;
  }, { move: new Set(), drilling: new Set() });
}

function calendarOperationDays(records) {
  return (records || []).reduce((days, record) => {
    const day = dayOfMonth(record.reportDate);
    if (!day) return days;
    const values = days.get(day) || { p: 0, sc: 0, npt: 0 };
    values.p += Math.max(0, Number(record.p_hours) || 0);
    values.sc += Math.max(0, Number(record.sc_hours) || 0);
    values.npt += Math.max(0, Number(record.npt_hours) || 0);
    days.set(day, values);
    return days;
  }, new Map());
}

function calendarOperationBar(values) {
  if (!values) return "";
  const p = Math.max(0, Number(values.p) || 0);
  const sc = Math.max(0, Number(values.sc) || 0);
  const npt = Math.max(0, Number(values.npt) || 0);
  const total = p + sc + npt;
  if (total <= 0) return "";
  const title = `P ${formatHours(p)}h · SC ${formatHours(sc)}h · NPT ${formatHours(npt)}h`;
  const segments = [
    ["p", p],
    ["sc", sc],
    ["npt", npt],
  ].filter(([, hours]) => hours > 0).map(([type, hours]) => `<i class="${type}" style="width:${(hours / total * 100).toFixed(4)}%"></i>`).join("");
  return `<span class="calendar-operation-bar" title="${escapeHtml(title)}" aria-label="${escapeHtml(title)}">${segments}</span>`;
}

function recordStage(record = {}) {
  const eventText = String(record.event || "").toLowerCase();
  if (String(record.report_type || "") === "drilling" && eventText.includes("rig move")) return "move";
  if (String(record.report_type || "") === "drilling" && eventText.includes("drilling")) return "drilling";
  return "";
}

function firstStageDate(records, stage) {
  const dates = (records || [])
    .filter((record) => recordStage(record) === stage && record.reportDate)
    .map((record) => record.reportDate)
    .sort();
  return dates[0] || "";
}

function operationStats(rows) {
  return (rows || []).reduce((stats, row) => {
    const hours = toNumber(row.hours);
    const value = Number.isFinite(hours) ? hours : 0;
    const type = String(row.op_type || "").trim().toUpperCase();
    stats.total += value;
    if (type === "NPT") stats.npt += value;
    if (type === "P") stats.p += value;
    if (type === "SC") stats.sc += value;
    return stats;
  }, { total: 0, npt: 0, p: 0, sc: 0 });
}

function percentage(value, total) {
  return total > 0 ? `${Math.round((value / total) * 100)}%` : "0%";
}

function formatHours(value) {
  return (Number(value) || 0).toFixed(2);
}

function formatWellDate(data = {}) {
  const well = String(data.wellbore || "").trim() || "-";
  const date = String(data.reportDate || "").trim() || "-";
  return `${well} / ${date}`;
}

function detailCompleteness(required, issues) {
  const errorCount = issues.filter((issue) => issue.level === "error").length;
  const warningCount = issues.length - errorCount;
  const base = required.length ? Math.max(0, 100 - Math.round((errorCount * 18 + warningCount * 6) / Math.max(required.length, 1))) : 100;
  return Math.max(0, Math.min(100, base));
}

function setText(selector, value) {
  const element = document.querySelector(selector);
  if (element) element.textContent = value;
}

function calendarMonthLabel(dateValue) {
  const date = new Date(`${(dateValue || new Date().toISOString().slice(0, 10)).slice(0, 7)}-01T00:00:00`);
  if (currentLanguage === "zh") return `${date.getFullYear()}年${date.getMonth() + 1}月`;
  return date.toLocaleDateString(currentLanguage === "es" ? "es-ES" : "en-US", { year: "numeric", month: "long" });
}

function calendarMarkup(reportType, dateValue, uploadedDays, stageDays, operationDays = new Map()) {
  const base = new Date(`${(dateValue || new Date().toISOString().slice(0, 10)).slice(0, 7)}-01T00:00:00`);
  const year = base.getFullYear();
  const month = base.getMonth();
  const firstDay = base.getDay();
  const totalDays = new Date(year, month + 1, 0).getDate();
  const prevTotal = new Date(year, month, 0).getDate();
  const cells = [];
  const showStages = reportType === "drilling";
  const weekdays = currentLanguage === "es" ? ["D", "L", "M", "X", "J", "V", "S"] : ["日", "一", "二", "三", "四", "五", "六"];
  for (let i = firstDay - 1; i >= 0; i--) cells.push({ day: prevTotal - i, muted: true });
  for (let day = 1; day <= totalDays; day++) cells.push({ day, date: `${year}-${String(month + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}` });
  while (cells.length % 7) cells.push({ day: cells.length - totalDays - firstDay + 1, muted: true });
  return `
    <div class="calendar-grid calendar-weekdays">
      ${weekdays.map((day) => `<span>${day}</span>`).join("")}
    </div>
    <div class="calendar-grid calendar-days">
      ${cells.map((cell) => {
        const statusClass = cell.muted
          ? "muted"
          : showStages && stageDays.move.has(cell.day)
            ? "has-move"
            : showStages && stageDays.drilling.has(cell.day)
              ? "has-drilling"
              : uploadedDays.has(cell.day)
                ? "has-upload"
                : "";
        const operationBar = cell.muted ? "" : calendarOperationBar(operationDays.get(cell.day));
        return `<button type="button" class="${statusClass}" data-calendar-date="${cell.date || ""}" data-report-type="${reportType}" ${cell.muted ? "disabled" : ""}><span>${cell.day}</span>${operationBar}</button>`;
      }).join("")}
    </div>
    <div class="calendar-legend"><span class="calendar-operation-key"><i class="p"></i>P</span><span class="calendar-operation-key"><i class="sc"></i>SC</span><span class="calendar-operation-key"><i class="npt"></i>NPT</span>${showStages ? '<span class="calendar-stage-key"><i class="move"></i>Rig Move</span><span class="calendar-stage-key"><i class="drilling"></i>Drilling</span>' : ""}</div>
  `;
}

function recordTableMarkup(reportType, records, jobs = [], page = 1, pageSize = DEFAULT_PAGE_SIZE) {
  const rows = [
    ...jobs.map((job) => ({ kind: "job", value: job })),
    ...records.map((record) => ({ kind: "record", value: record })),
  ];
  if (!rows.length) return `<div class="empty-records">${ui("noRecords")}</div>`;
  pageSize = normalizedPageSize(pageSize);
  const totalPages = Math.max(1, Math.ceil(rows.length / pageSize));
  const currentPage = Math.min(Math.max(Number(page) || 1, 1), totalPages);
  const pageRows = rows.slice((currentPage - 1) * pageSize, currentPage * pageSize);
  return `
    <table class="record-table">
      <thead><tr><th>${ui("date")}</th><th>${ui("well")}</th><th>${ui("reportType")}</th><th>${ui("fileName")}</th><th>${ui("uploadTime")}</th><th>${ui("uploader")}</th><th>${ui("status")}</th><th>${ui("operation")}</th></tr></thead>
      <tbody>
        ${pageRows.map((row) => row.kind === "job" ? jobRecordRowMarkup(reportType, row.value) : savedRecordRowMarkup(reportType, row.value)).join("")}
      </tbody>
    </table>
    ${recordPaginationMarkup(reportType, currentPage, totalPages, rows.length, pageSize)}
  `;
}

function jobRecordRowMarkup(reportType, job) {
  const actions = [];
  if (job.recordId) actions.push(`<button class="link-button" type="button" data-record-preview="${escapeHtml(job.recordId)}" data-report-type="${reportType}">${ui("preview")}</button>`);
  if (job.status === "failed") actions.push(`<button class="link-button danger-link" type="button" data-delete-upload-job="${escapeHtml(job.id)}" data-report-type="${reportType}" aria-label="${escapeHtml(`${ui("deleteFailedImport")} ${job.fileName || ""}`)}">${ui("deleteFailedImport")}</button>`);
  return `
    <tr>
      <td>${escapeHtml(job.reportDate || "-")}</td>
      <td>${escapeHtml(job.wellbore || "识别中")}</td>
      <td><span class="type-pill">${reportName(reportType)}</span></td>
      <td>${escapeHtml(job.fileName)}</td>
      <td>${escapeHtml(formatRecordTime(job.updated_at))}</td>
      <td>${escapeHtml(job.uploader || "本地导入")}</td>
      <td>${jobStatusMarkup(job)}</td>
      <td><div class="record-row-actions">${actions.join("") || "-"}</div></td>
    </tr>
  `;
}

function deleteFailedUploadJob(reportType, jobId) {
  const index = uploadJobs.findIndex((job) => job.id === jobId && job.reportType === reportType && job.status === "failed");
  if (index < 0) return;
  uploadJobs.splice(index, 1);
  renderRecordDashboard(reportType);
  showToast(ui("failedImportDeleted"));
}

function savedRecordRowMarkup(reportType, record) {
  const sourceName = record.source_file || `${record.wellbore || reportType}_${record.reportDate || "report"}.pdf`;
  return `
    <tr>
      <td>${escapeHtml(record.reportDate)}</td>
      <td>${escapeHtml(record.wellbore)}</td>
      <td><span class="type-pill">${reportName(reportType)}</span></td>
      <td><button class="source-file-button" type="button" data-source-pdf="${escapeHtml(record.record_id)}" data-source-name="${escapeHtml(sourceName)}">${escapeHtml(sourceName)}</button></td>
      <td>${escapeHtml(formatRecordTime(record.updated_at || record.created_at))}</td>
      <td>${escapeHtml(record.uploader || "本地导入")}</td>
      <td><div data-record-status-id="${escapeHtml(record.record_id)}">${recordStatusMarkup(record)}</div></td>
      <td><button class="link-button" type="button" data-record-preview="${escapeHtml(record.record_id)}" data-report-type="${reportType}">${ui("preview")}</button></td>
    </tr>
  `;
}

function paginationSummary(totalRows, currentPage, pageSize) {
  const start = totalRows ? (currentPage - 1) * pageSize + 1 : 0;
  const end = Math.min(totalRows, currentPage * pageSize);
  if (currentLanguage === "es") return `${totalRows} registros, mostrando ${start}-${end}`;
  return `共 ${totalRows} 条，显示 ${start}-${end}`;
}

function pageSizeOptionsMarkup(pageSize) {
  return PAGE_SIZE_OPTIONS.map((size) => `<option value="${size}" ${size === pageSize ? "selected" : ""}>${size} 条</option>`).join("");
}

function normalizedPageSize(value) {
  const pageSize = Number(value);
  return PAGE_SIZE_OPTIONS.includes(pageSize) ? pageSize : DEFAULT_PAGE_SIZE;
}

function recordPaginationMarkup(reportType, currentPage, totalPages, totalRows, pageSize) {
  return `
    <div class="record-pagination standard-pagination">
      <span class="pagination-summary">${paginationSummary(totalRows, currentPage, pageSize)}</span>
      <div class="standard-pagination-controls">
        <label class="standard-page-size">每页
          <select data-record-page-size="${reportType}" aria-label="每页条数">${pageSizeOptionsMarkup(pageSize)}</select>
        </label>
        <div class="record-page-buttons">
        <button class="icon-button" type="button" data-record-page="${currentPage - 1}" data-report-type="${reportType}" ${currentPage <= 1 ? "disabled" : ""} aria-label="${ui("prevPage")}">‹</button>
        <label class="page-jump">第 <input type="number" min="1" max="${totalPages}" value="${currentPage}" inputmode="numeric" data-record-page-jump data-report-type="${reportType}" aria-label="跳转页码" /> / ${totalPages} 页</label>
        <button class="icon-button" type="button" data-record-page="${currentPage + 1}" data-report-type="${reportType}" ${currentPage >= totalPages ? "disabled" : ""} aria-label="${ui("nextPage")}">›</button>
        </div>
      </div>
    </div>
  `;
}

function analyticsPaginationMarkup(kind, currentPage, totalPages, totalRows) {
  if (!totalRows) return "";
  const pageSize = normalizedPageSize(analyticsState[kind]?.detailPageSize);
  return `
    <div class="record-pagination standard-pagination analytics-pagination">
      <span class="pagination-summary">${paginationSummary(totalRows, currentPage, pageSize)}</span>
      <div class="standard-pagination-controls">
        <label class="standard-page-size">每页
          <select data-analytics-page-size="${kind}" aria-label="每页条数">${pageSizeOptionsMarkup(pageSize)}</select>
        </label>
        <div class="record-page-buttons">
        <button class="icon-button" type="button" data-analytics-page="${currentPage - 1}" data-analytics-kind="${kind}" ${currentPage <= 1 ? "disabled" : ""} aria-label="${ui("prevPage")}">‹</button>
        <label class="page-jump">第 <input type="number" min="1" max="${totalPages}" value="${currentPage}" inputmode="numeric" data-analytics-page-jump data-analytics-kind="${kind}" aria-label="跳转页码" /> / ${totalPages} 页</label>
        <button class="icon-button" type="button" data-analytics-page="${currentPage + 1}" data-analytics-kind="${kind}" ${currentPage >= totalPages ? "disabled" : ""} aria-label="${ui("nextPage")}">›</button>
        </div>
      </div>
    </div>
  `;
}

function analyticsPageSlice(kind, rows) {
  const state = analyticsState[kind];
  const pageSize = normalizedPageSize(state.detailPageSize);
  const totalPages = Math.max(1, Math.ceil(rows.length / pageSize));
  const currentPage = Math.min(Math.max(1, Number(state.detailPage) || 1), totalPages);
  state.detailPage = currentPage;
  const start = (currentPage - 1) * pageSize;
  return {
    pageRows: rows.slice(start, start + pageSize),
    currentPage,
    totalPages
  };
}

function clampPage(value, totalPages) {
  const page = Number.parseInt(value, 10);
  return Math.min(Math.max(Number.isFinite(page) ? page : 1, 1), Math.max(1, totalPages));
}

function renderAnalyticsPage(kind) {
  if (kind === "npt") return renderNptTable(nptReportVisibleRows(analyticsState.npt.payload?.details || []));
  if (kind === "productionReport") return renderProductionReportTable(productionReportVisibleRows(analyticsState.productionReport.payload?.details || []));
  return renderProductionTable(analyticsState.production.payload?.details || []);
}

function commitRecordPageJump(input) {
  const reportType = input?.dataset.reportType;
  if (!recordState[reportType]) return;
  recordState[reportType].page = clampPage(input.value, Number(input.max || 1));
  renderRecordDashboard(reportType);
}

function commitAnalyticsPageJump(input) {
  const kind = input?.dataset.analyticsKind;
  if (!analyticsState[kind]) return;
  analyticsState[kind].detailPage = clampPage(input.value, Number(input.max || 1));
  renderAnalyticsPage(kind);
}

function setRecordPageSize(reportType, value) {
  if (!recordState[reportType]) return;
  recordState[reportType].pageSize = normalizedPageSize(value);
  recordState[reportType].page = 1;
  renderRecordDashboard(reportType);
}

function setAnalyticsPageSize(kind, value) {
  if (!analyticsState[kind]) return;
  analyticsState[kind].detailPageSize = normalizedPageSize(value);
  analyticsState[kind].detailPage = 1;
  renderAnalyticsPage(kind);
}

function analyticsSortHeader(kind, field, label) {
  const state = analyticsState[kind];
  const active = state.sortField === field;
  const nextDir = active && state.sortDir === "asc" ? "desc" : "asc";
  const icon = active ? (state.sortDir === "asc" ? "↑" : "↓") : "↕";
  return `<th><button class="table-sort-button ${active ? "active" : ""}" type="button" data-analytics-sort="${escapeHtml(field)}" data-analytics-kind="${kind}" data-sort-dir="${nextDir}" aria-label="${escapeHtml(label)}">${escapeHtml(label)}<span>${icon}</span></button></th>`;
}

function analyticsSortedRows(kind, rows) {
  const state = analyticsState[kind];
  if (kind === "npt" && !state.sortField) return nptDefaultSortedRows(rows);
  if (!state.sortField) return rows;
  const direction = state.sortDir === "asc" ? 1 : -1;
  return [...rows].sort((left, right) => analyticsCompare(left, right, state.sortField) * direction);
}

function nptDefaultSortedRows(rows) {
  return [...rows].sort((left, right) => (
    analyticsCompare(left, right, "wellbore")
    || analyticsCompare(left, right, "reportDate")
    || analyticsCompare(left, right, "project_name")
    || analyticsCompare(left, right, "rig")
  ));
}

function analyticsCompare(left, right, field) {
  const leftValue = analyticsSortValue(left, field);
  const rightValue = analyticsSortValue(right, field);
  const leftEmpty = leftValue === "" || leftValue === null || leftValue === undefined;
  const rightEmpty = rightValue === "" || rightValue === null || rightValue === undefined;
  if (leftEmpty && rightEmpty) return 0;
  if (leftEmpty) return 1;
  if (rightEmpty) return -1;
  if (["hours", "drilling_hours", "completion_hours", "workover_hours", "move_hours", "npt_hours"].includes(field)) {
    return Number(leftValue || 0) - Number(rightValue || 0);
  }
  if (["reportDate", "start_date", "end_date", "move_date", "drilling_start_date", "drilling_finish_date", "completion_date", "workover_date"].includes(field)) {
    return String(leftValue).localeCompare(String(rightValue));
  }
  return String(leftValue).localeCompare(String(rightValue), currentLanguage === "zh" ? "zh-Hans" : currentLanguage, { numeric: true, sensitivity: "base" });
}

function analyticsSortValue(row, field) {
  if (field === "report_type") return reportTypeLabel(row.report_type);
  if (field === "reason") return reasonLabel(row.reason);
  return row[field] ?? "";
}

async function openSourcePdf(recordId, sourceName = "") {
  const modal = document.querySelector("#sourcePdfModal");
  const frame = document.querySelector("#sourcePdfFrame");
  const empty = document.querySelector("#sourcePdfEmpty");
  const title = document.querySelector("#sourcePdfTitle");
  if (!modal || !frame || !empty || !title) return;
  title.textContent = sourceName || ui("sourcePdfTitle");
  empty.hidden = true;
  frame.hidden = false;
  modal.hidden = false;
  document.body.classList.add("modal-open");
  if (sourcePdfObjectUrl) URL.revokeObjectURL(sourcePdfObjectUrl);
  sourcePdfObjectUrl = "";
  try {
    const response = await fetch(`/api/source-pdf?record_id=${encodeURIComponent(recordId)}`);
    if (!response.ok) {
      showSourcePdfMissing(sourceName);
      return;
    }
    const blob = await response.blob();
    sourcePdfObjectUrl = URL.createObjectURL(blob);
    frame.src = `${sourcePdfObjectUrl}#toolbar=1&navpanes=0`;
  } catch (error) {
    console.error(error);
    showSourcePdfMissing(sourceName);
  }
}

function showSourcePdfMissing(sourceName = "") {
  const modal = document.querySelector("#sourcePdfModal");
  const frame = document.querySelector("#sourcePdfFrame");
  const empty = document.querySelector("#sourcePdfEmpty");
  const title = document.querySelector("#sourcePdfTitle");
  if (!modal || !frame || !empty || !title) return;
  title.textContent = sourceName || ui("sourcePdfTitle");
  frame.hidden = true;
  frame.removeAttribute("src");
  empty.hidden = false;
  empty.textContent = ui("sourcePdfMissing");
  modal.hidden = false;
  document.body.classList.add("modal-open");
}

function closeSourcePdf() {
  const modal = document.querySelector("#sourcePdfModal");
  const frame = document.querySelector("#sourcePdfFrame");
  if (!modal || !frame) return;
  modal.hidden = true;
  frame.removeAttribute("src");
  if (sourcePdfObjectUrl) URL.revokeObjectURL(sourcePdfObjectUrl);
  sourcePdfObjectUrl = "";
  document.body.classList.remove("modal-open");
}

function recordStatusMarkup(record) {
  const parsingMarkup = `<span class="status-pill uploaded">${ui("parseDoneStatus")}</span>`;
  return `<div class="record-status-stack">${parsingMarkup}${translationStatusMarkup(record)}</div>`;
}

function translationStatusMarkup(record) {
  const status = String(record.translation_status || "").toUpperCase();
  const progress = translationProgress(record);
  const error = record.translation_error || "";
  if (status === "COMPLETED") {
    return `<span class="status-pill translated">${ui("translationDoneStatus")}</span>`;
  }
  if (status === "NOT_REQUIRED") return `<span class="status-pill translated">${ui("translationNotRequiredStatus")}</span>`;
  if (status === "FAILED") {
    return `<span class="status-pill failed" title="${escapeHtml(error)}">${ui("translationFailedStatus")}</span>`;
  }
  if (status === "QUEUED") return `<span class="status-pill queued">${ui("translationQueuedStatus")}</span>`;
  if (status === "PENDING") return `<span class="status-pill queued">${ui("translationPendingStatus")}</span>`;
  if (status === "IN_PROGRESS") {
    return `
      <div class="progress-status translation-progress">
        <span>${ui("translationRunningStatus")}</span>
        <div class="progress-track"><i style="width:${Math.max(4, Math.min(100, progress))}%"></i></div>
        <span class="translation-progress-value">${progress}%</span>
      </div>
    `;
  }
  return `<span class="status-pill queued">${ui("translationPendingStatus")}</span>`;
}

function translationProgress(record) {
  const value = Number(record.translation_progress);
  if (Number.isFinite(value)) return Math.max(0, Math.min(100, Math.round(value)));
  const status = String(record.translation_status || "").toUpperCase();
  if (status === "COMPLETED" || status === "NOT_REQUIRED") return 100;
  return 0;
}

function jobStatusMarkup(job) {
  if (job.status === "failed") return `<span class="status-pill failed" title="${escapeHtml(job.error || "")}">${ui("failed")}</span>`;
  const label = job.status === "queued" ? ui("queued") : job.status === "done" ? ui("uploaded") : ui("parsing");
  return `
    <div class="progress-status">
      <span>${label} ${job.progress}%</span>
      <div class="progress-track"><i style="width:${Math.max(4, Math.min(100, job.progress))}%"></i></div>
    </div>
  `;
}

function formatRecordTime(value = "") {
  if (!value) return "";
  return value.replace("T", " ").replace("+00:00", "").slice(0, 16);
}

function toNumber(value) {
  const parsed = Number(String(value || "").replace(/,/g, ""));
  return Number.isFinite(parsed) ? parsed : NaN;
}

function analyticsEndpoint(kind) {
  return kind === "npt" ? "/api/npt-stats" : "/api/production-summary";
}

function analyticsFilterValues(kind) {
  const formEl = document.querySelector(`[data-analytics-filter="${kind}"]`);
  const params = new URLSearchParams();
  if (!formEl) return params;
  if (kind === "productionReport") {
    const state = analyticsState.productionReport;
    params.set("project_mode", "1");
    appendProductionReportParams(params, "rig", state.selectedRigs, state.availableRigs, state.rigTouched);
    appendProductionReportParams(params, "project", state.selectedProjects, state.availableProjects, state.projectTouched);
    if (state.wellQuery.trim()) params.set("wellbore", state.wellQuery.trim());
    return params;
  }
  if (kind === "npt") {
    const state = analyticsState.npt;
    params.set("project_mode", "1");
    appendProductionReportParams(params, "rig", state.selectedRigs, state.availableRigs, state.rigTouched);
    appendProductionReportParams(params, "project", state.selectedProjects, state.availableProjects, state.projectTouched);
    if (state.keywordQuery.trim()) params.set("wellbore", state.keywordQuery.trim());
    return params;
  }
  if (kind === "production") {
    params.set("project_mode", "1");
    const scopeType = formEl.querySelector("[data-production-scope-type]")?.value === "project" ? "project" : "rig";
    const scopeValue = formEl.querySelector("[data-production-scope-value]")?.value || "";
    if (scopeValue) params.set(scopeType, scopeValue);
  }
  formEl.querySelectorAll("input, select").forEach((control) => {
    if (!control.name) return;
    if (kind === "production" && (control.name === "scope_type" || control.name === "scope_value")) return;
    if (control.multiple) {
      [...control.selectedOptions].forEach((option) => {
        if (option.value) params.append(control.name, option.value);
      });
      return;
    }
    const value = control.value.trim();
    if (value) params.set(control.name, value);
  });
  return params;
}

function appendProductionReportParams(params, name, selected, available, touched) {
  if (!available.length) return;
  if (!selected.size) {
    if (touched) params.append(name, "__none__");
    return;
  }
  [...selected].forEach((value) => params.append(name, value));
}

async function loadAnalytics(kind, options = {}) {
  const params = analyticsFilterValues(kind);
  if (options.force) params.set("_ts", String(Date.now()));
  const response = await fetch(`${analyticsEndpoint(kind)}?${params.toString()}`, { cache: options.force ? "no-store" : "default" });
  const payload = await response.json();
  if (!response.ok) {
    showToast(payload.error || "统计数据加载失败");
    return;
  }
  analyticsState[kind].payload = payload;
  analyticsState[kind].detailPage = 1;
  const defaultSelectionApplied = populateAnalyticsFilters(kind, payload.filters || {});
  if ((kind === "productionReport" || kind === "npt") && defaultSelectionApplied && !options.skipSelectionReload) {
    await loadAnalytics(kind, { force: true, skipSelectionReload: true });
    return;
  }
  if (kind === "npt") renderNptAnalytics(payload);
  else if (kind === "productionReport") renderProductionReportAnalytics(payload);
  else renderProductionAnalytics(payload);
}

function populateAnalyticsFilters(kind, filters) {
  const formEl = document.querySelector(`[data-analytics-filter="${kind}"]`);
  if (!formEl) return false;
  if (kind === "productionReport") {
    return initializeProductionReportSelections(filters);
  }
  if (kind === "npt") {
    return initializeNptReportSelections(filters);
  }
  if (kind === "production") {
    populateProductionSummaryScopeFilter(formEl, filters);
    return false;
  }
  if (kind !== "productionReport") setSelectOptions(formEl.querySelector('[name="rig"]'), filters.rigs || [], ui("allRigs"));
  const defaultProjectApplied = kind === "productionReport"
    ? populateProductionRigFilter(formEl, filters.rigs || [])
    : (setMultiSelectOptions(formEl.querySelector('[name="project"]'), (filters.projects || []).map((item) => [item.value, projectOptionLabel(item)])), false);
  setSelectOptions(formEl.querySelector('[name="report_type"]'), (filters.report_types || []).map((item) => [item.value, reportTypeLabel(item.value)]), ui("allReportTypes"));
  setSelectOptions(formEl.querySelector('[name="reason"]'), (filters.reasons || []).map((item) => [item, reasonLabel(item)]), ui("allReasons"));
  return defaultProjectApplied;
}

function populateProductionSummaryScopeFilter(formEl, filters = {}) {
  const scopeType = formEl.querySelector("[data-production-scope-type]");
  const scopeValue = formEl.querySelector("[data-production-scope-value]");
  const scopeLabel = formEl.querySelector("[data-production-scope-label]");
  if (!scopeType || !scopeValue) return;
  const mode = scopeType.value === "project" ? "project" : "rig";
  const current = scopeValue.value;
  if (mode === "project") {
    if (scopeLabel) scopeLabel.textContent = ui("tableProject");
    const projects = (filters.projects || []).map((item) => [item.value, item.label || item.value]);
    setSelectOptions(scopeValue, projects, ui("allProjects"));
  } else {
    if (scopeLabel) scopeLabel.textContent = ui("tableRig");
    setSelectOptions(scopeValue, filters.rigs || [], ui("allRigs"));
  }
  scopeValue.value = [...scopeValue.options].some((option) => option.value === current) ? current : "";
}

function setSelectOptions(select, values, emptyLabel) {
  if (!select) return;
  const current = select.value;
  const items = values.map((item) => Array.isArray(item) ? item : [item, item]);
  select.innerHTML = `<option value="">${emptyLabel}</option>${items.map(([value, label]) => `<option value="${escapeHtml(value)}">${escapeHtml(label)}</option>`).join("")}`;
  select.value = items.some(([value]) => value === current) ? current : "";
}

function setMultiSelectOptions(select, values) {
  if (!select) return;
  const current = new Set([...select.selectedOptions].map((option) => option.value));
  const items = values.map((item) => Array.isArray(item) ? item : [item, item]);
  select.innerHTML = items.map(([value, label]) => `<option value="${escapeHtml(value)}">${escapeHtml(label)}</option>`).join("");
  [...select.options].forEach((option) => {
    option.selected = current.has(option.value);
  });
}

function productionProjectItems(projects = []) {
  return (projects || []).map((item) => {
    const value = String(item.value || "").trim();
    return {
      value,
      label: projectOptionLabel(item),
      start_date: item.start_date || "",
      searchText: [item.label, item.contract_no, item.start_date, item.end_date, value].filter(Boolean).join(" ").toLowerCase(),
    };
  }).filter((item) => item.value).sort((left, right) => {
    const byDate = String(right.start_date).localeCompare(String(left.start_date));
    return byDate || left.label.localeCompare(right.label, "zh-Hans-CN", { numeric: true });
  });
}

function productionRigItems(rigs = []) {
  return (rigs || []).map((rig) => String(rig || "").trim()).filter(Boolean).sort((left, right) => {
    return left.localeCompare(right, "zh-Hans-CN", { numeric: true, sensitivity: "base" });
  }).map((rig) => ({ value: rig, label: rig, searchText: rig.toLowerCase() }));
}

function initializeProductionReportSelections(filters = {}) {
  const state = analyticsState.productionReport;
  const rigs = productionRigItems(filters.rigs || []);
  const projects = productionProjectItems(filters.projects || []);
  const wasInitialized = state.selectionInitialized;
  state.availableRigs = rigs;
  state.availableProjects = projects;
  const rigValues = rigs.map((item) => item.value);
  const projectValues = projects.map((item) => item.value);

  state.selectedRigs = state.rigTouched ? intersectSelection(state.selectedRigs, rigValues) : new Set(rigValues);
  state.selectedProjects = state.projectTouched ? intersectSelection(state.selectedProjects, projectValues) : new Set(projectValues);
  state.selectionInitialized = true;
  return !wasInitialized && (rigValues.length > 0 || projectValues.length > 0);
}

function intersectSelection(selected, validValues) {
  const valid = new Set(validValues);
  return new Set([...selected].filter((value) => valid.has(value)));
}

function setProductionProjectSelection(field, selected) {
  const valuesHost = field.querySelector("[data-project-values]");
  const items = field._productionProjectItems || [];
  const valueName = field.dataset.valueName || "project";
  const selectedValues = new Set([...selected].filter(Boolean));
  if (valuesHost) {
    valuesHost.innerHTML = [...selectedValues].map((value) => `<input type="hidden" name="${escapeHtml(valueName)}" value="${escapeHtml(value)}" />`).join("");
  }
  field.querySelectorAll('[data-project-option] input[type="checkbox"]').forEach((checkbox) => {
    checkbox.checked = selectedValues.has(checkbox.value);
  });
  const summary = field.querySelector("[data-project-summary]");
  if (summary) {
    const labels = items.filter((item) => selectedValues.has(item.value)).map((item) => item.label);
    summary.textContent = labels.length === 0 ? (field.dataset.emptyLabel || ui("allProjects")) : labels.length === 1 ? labels[0] : `已选 ${labels.length} ${field.dataset.selectedUnit || "个项目"}`;
    summary.title = labels.join("\n");
  }
}

function filterProductionProjectOptions(field) {
  const term = (field.querySelector("[data-project-search]")?.value || "").trim().toLowerCase();
  field.querySelectorAll("[data-project-option]").forEach((option) => {
    option.hidden = Boolean(term) && !option.dataset.projectSearchText.includes(term);
  });
  positionProductionProjectDropdown(field);
}

function closeProductionProjectDropdowns(except = null) {
  document.querySelectorAll("[data-production-project-filter], [data-production-rig-filter]").forEach((field) => {
    if (except && field === except) return;
    const menu = field.querySelector("[data-project-dropdown]");
    const trigger = field.querySelector("[data-project-dropdown-toggle]");
    if (menu) menu.hidden = true;
    if (trigger) trigger.setAttribute("aria-expanded", "false");
  });
}

function positionProductionProjectDropdown(field) {
  const menu = field?.querySelector("[data-project-dropdown]");
  const trigger = field?.querySelector("[data-project-dropdown-toggle]");
  if (!field || !menu || !trigger || menu.hidden) return;
  const rect = trigger.getBoundingClientRect();
  const viewportGap = 14;
  const width = Math.min(520, Math.max(rect.width, window.innerWidth - rect.left - viewportGap));
  menu.style.left = `${Math.max(viewportGap, rect.left)}px`;
  menu.style.top = `${rect.bottom + 6}px`;
  menu.style.width = `${width}px`;
  menu.style.maxHeight = `${Math.max(180, window.innerHeight - rect.bottom - 24)}px`;
}

function positionOpenProductionProjectDropdowns() {
  document.querySelectorAll("[data-production-project-filter], [data-production-rig-filter]").forEach((field) => positionProductionProjectDropdown(field));
}

function resetAnalyticsFilter(kind) {
  const formEl = document.querySelector(`[data-analytics-filter="${kind}"]`);
  if (!formEl) return;
  if (kind === "productionReport") {
    const state = analyticsState.productionReport;
    state.selectedRigs = new Set(state.availableRigs.map((item) => item.value));
    state.selectedProjects = new Set(state.availableProjects.map((item) => item.value));
    state.rigTouched = false;
    state.projectTouched = false;
    state.sideSearch = "";
    state.wellQuery = "";
    state.detailPage = 1;
    refreshProductionReportView();
    return;
  }
  if (kind === "npt") {
    const state = analyticsState.npt;
    state.selectedRigs = new Set(state.availableRigs.map((item) => item.value));
    state.selectedProjects = new Set(state.availableProjects.map((item) => item.value));
    state.rigTouched = false;
    state.projectTouched = false;
    state.sideSearch = "";
    state.keywordQuery = "";
    state.detailPage = 1;
    refreshNptReportView();
    return;
  }
  formEl.querySelectorAll("input, select").forEach((control) => {
    if (control.name === "project_mode") return;
    control.value = "";
  });
  formEl.querySelectorAll("[data-production-project-filter], [data-production-rig-filter]").forEach((field) => {
    delete field.dataset.projectTouched;
    field.querySelector("[data-project-search]") && (field.querySelector("[data-project-search]").value = "");
    setProductionProjectSelection(field, new Set());
    filterProductionProjectOptions(field);
  });
}

function projectOptionLabel(item = {}) {
  const dates = [item.start_date, item.end_date].filter(Boolean).join(" ~ ");
  const contract = item.contract_no ? `${item.contract_no} / ` : "";
  return `${contract}${item.label || item.value || ""}${dates ? ` (${dates})` : ""}`;
}

function renderProductionAnalytics(payload) {
  const kpis = payload.kpis || {};
  const note = document.querySelector('[data-analytics-note="production"]');
  if (note) note.textContent = ui("analyticsProductionScope");
  document.querySelector('[data-analytics-kpis="production"]').innerHTML = [
    analyticsKpi(ui("kpiRigCount"), kpis.rig_count || 0, ""),
    analyticsKpi(ui("kpiWellCount"), kpis.well_count || 0, ""),
    analyticsKpi(ui("kpiTotalHours"), `${formatHours(kpis.total_hours)} h`, ""),
    analyticsKpi(ui("kpiTotalNpt"), `${formatHours(kpis.npt_hours)} h`, ""),
  ].join("");
  const reportTypeSeries = Object.keys(REPORT_TYPE_LABELS_JS).map((key) => ({ key, label: reportTypeLabel(key) }));
  renderProductionNptRanking('[data-chart="production-rig"]', payload.npt_by_rig || []);
  renderDonut('[data-chart="production-type"]', (payload.by_type || []).map((item) => ({ label: reportTypeLabel(item.report_type || item.type || item.value || item.label), value: item.hours })));
  renderProductionWellGantt('[data-chart="production-monthly"]', payload);
}

function renderProductionReportAnalytics(payload) {
  renderProductionReportTabs();
  renderProductionReportSide();
  renderProductionReportFilters();
  renderProductionReportTable(productionReportVisibleRows(payload.details || []));
}

function renderProductionReportTabs() {
  const state = analyticsState.productionReport;
  document.querySelectorAll("[data-production-report-tab]").forEach((button) => {
    const active = button.dataset.productionReportTab === state.activeTab;
    button.classList.toggle("active", active);
    button.setAttribute("aria-selected", active ? "true" : "false");
  });
}

function renderProductionReportSide() {
  const state = analyticsState.productionReport;
  const host = document.querySelector("[data-production-report-side]");
  if (!host) return;
  const isRigTab = state.activeTab === "rig";
  const items = isRigTab ? state.availableRigs : state.availableProjects;
  const selected = isRigTab ? state.selectedRigs : state.selectedProjects;
  const title = isRigTab ? "钻井队列表" : "项目列表";
  const placeholder = isRigTab ? "搜索井队" : "搜索项目";
  const term = state.sideSearch.trim().toLowerCase();
  const visibleItems = items.filter((item) => !term || item.searchText.includes(term));
  host.innerHTML = `
    <div class="production-side-heading">
      <div><h3>${escapeHtml(title)}</h3></div>
      <strong>${selected.size}/${items.length}</strong>
    </div>
    <input class="production-side-search" type="search" placeholder="${escapeHtml(placeholder)}" value="${escapeHtml(state.sideSearch)}" data-production-side-search />
    <div class="production-side-actions">
      <button class="link-button" type="button" data-production-side-select="all">全选</button>
      <button class="link-button" type="button" data-production-side-select="clear">清空</button>
    </div>
    <div class="production-side-list">
      ${visibleItems.map((item) => productionReportCheckbox("production-side-option", item, selected.has(item.value))).join("") || `<div class="empty-records">暂无可选项</div>`}
    </div>
  `;
}

function renderProductionReportFilters() {
  const state = analyticsState.productionReport;
  const host = document.querySelector("[data-production-report-filters]");
  if (!host) return;
  const isRigTab = state.activeTab === "rig";
  const filterItems = isRigTab ? state.availableProjects : state.availableRigs;
  const selected = isRigTab ? state.selectedProjects : state.selectedRigs;
  const filterType = isRigTab ? "project" : "rig";
  const title = isRigTab ? "项目过滤" : "井队过滤";
  const hint = isRigTab ? "可复选项目，进一步收窄当前井队范围" : "可复选井队，进一步收窄当前项目范围";
  const placeholder = isRigTab ? "搜索合同 / 项目" : "搜索井队";
  const emptyText = isRigTab ? "暂无项目" : "暂无井队";
  const summary = productionReportFilterSummary(filterItems, selected, filterType);
  host.innerHTML = `
    <div class="production-filter-field production-report-filter-dropdown" data-production-report-filter-field="${escapeHtml(filterType)}">
      <div class="production-filter-label">
        <span>${escapeHtml(title)}</span>
        <em data-production-report-filter-count>${selected.size}/${filterItems.length}</em>
      </div>
      <button class="project-multiselect-trigger production-report-filter-trigger" type="button" data-production-report-filter-toggle aria-expanded="false">
        <span data-production-report-filter-summary title="${escapeHtml(summary.title)}">${escapeHtml(summary.text)}</span>
      </button>
      <div class="project-multiselect-menu production-report-filter-menu" data-production-report-filter-menu hidden>
        <input class="project-multiselect-search" type="search" placeholder="${escapeHtml(placeholder)}" data-production-report-filter-search />
        <div class="production-filter-menu-actions">
          <span>${escapeHtml(hint)}</span>
          <div>
            <button class="link-button" type="button" data-production-filter-select="${filterType}" data-mode="all">全选</button>
            <button class="link-button" type="button" data-production-filter-select="${filterType}" data-mode="clear">清空</button>
          </div>
        </div>
        <div class="project-multiselect-options production-report-filter-options">
          ${filterItems.map((item) => productionReportCheckbox("production-filter-option", item, selected.has(item.value), filterType)).join("") || `<div class="project-multiselect-empty">${escapeHtml(emptyText)}</div>`}
        </div>
      </div>
    </div>
    <label class="production-search-field production-filter-field">
      <span>井号查找</span>
      <input type="search" placeholder="输入井号" value="${escapeHtml(state.wellQuery)}" data-production-well-query />
    </label>
    <div class="production-report-actions production-filter-field">
      <button class="button production-action-button" type="button" data-analytics-search="productionReport"><span aria-hidden="true">⌕</span><b data-i18n="search">查询</b></button>
      <button class="button secondary production-action-button" type="button" data-analytics-reset="productionReport"><span aria-hidden="true">↻</span><b data-i18n="reset">重置</b></button>
      <button class="button secondary production-action-button" type="button" data-analytics-export="productionReport"><span aria-hidden="true">⇩</span><b>导出Excel</b></button>
    </div>
  `;
}

function productionReportCheckbox(dataName, item, checked, type = "") {
  return `
    <label class="production-check-option" data-project-option data-project-search-text="${escapeHtml(item.searchText || item.label || item.value || "")}">
      <input type="checkbox" value="${escapeHtml(item.value)}" ${checked ? "checked" : ""} data-${dataName}${type ? `="${escapeHtml(type)}"` : ""} />
      <span>${escapeHtml(item.label)}</span>
    </label>
  `;
}

function productionReportFilterSummary(items, selected, type) {
  const selectedItems = items.filter((item) => selected.has(item.value));
  const unit = type === "project" ? "个项目" : "个井队";
  const allLabel = type === "project" ? "全部项目" : "全部井队";
  const emptyLabel = type === "project" ? "未选择项目" : "未选择井队";
  if (!items.length) return { text: allLabel, title: "" };
  if (!selectedItems.length) return { text: emptyLabel, title: "" };
  if (selectedItems.length === items.length) return { text: allLabel, title: selectedItems.map((item) => item.label).join("\n") };
  if (selectedItems.length === 1) return { text: selectedItems[0].label, title: selectedItems[0].label };
  return {
    text: `已选 ${selectedItems.length} ${unit}`,
    title: selectedItems.map((item) => item.label).join("\n"),
  };
}

function currentProductionReportFilterItems(type) {
  const state = analyticsState.productionReport;
  return type === "project" ? state.availableProjects : state.availableRigs;
}

function currentProductionReportFilterSelection(type) {
  const state = analyticsState.productionReport;
  return type === "project" ? state.selectedProjects : state.selectedRigs;
}

function setProductionReportFilterSelection(type, selected) {
  const state = analyticsState.productionReport;
  if (type === "project") {
    state.selectedProjects = selected;
    state.projectTouched = true;
  } else {
    state.selectedRigs = selected;
    state.rigTouched = true;
  }
  state.detailPage = 1;
}

function syncProductionReportFilterField(field) {
  if (!field) return;
  const type = field.dataset.productionReportFilterField;
  const items = currentProductionReportFilterItems(type);
  const selected = currentProductionReportFilterSelection(type);
  field.querySelectorAll("[data-production-filter-option]").forEach((checkbox) => {
    checkbox.checked = selected.has(checkbox.value);
  });
  const count = field.querySelector("[data-production-report-filter-count]");
  if (count) count.textContent = `${selected.size}/${items.length}`;
  const summary = productionReportFilterSummary(items, selected, type);
  const summaryEl = field.querySelector("[data-production-report-filter-summary]");
  if (summaryEl) {
    summaryEl.textContent = summary.text;
    summaryEl.title = summary.title;
  }
}

function filterProductionReportDropdownOptions(field) {
  const term = (field?.querySelector("[data-production-report-filter-search]")?.value || "").trim().toLowerCase();
  field?.querySelectorAll("[data-project-option]").forEach((option) => {
    option.hidden = Boolean(term) && !option.dataset.projectSearchText.includes(term);
  });
  positionProductionReportFilterDropdown(field);
}

function closeProductionReportFilterDropdowns(except = null) {
  document.querySelectorAll("[data-production-report-filter-field]").forEach((field) => {
    if (except && field === except) return;
    const menu = field.querySelector("[data-production-report-filter-menu]");
    const trigger = field.querySelector("[data-production-report-filter-toggle]");
    if (menu) menu.hidden = true;
    if (trigger) trigger.setAttribute("aria-expanded", "false");
  });
}

function positionProductionReportFilterDropdown(field) {
  const menu = field?.querySelector("[data-production-report-filter-menu]");
  const trigger = field?.querySelector("[data-production-report-filter-toggle]");
  if (!field || !menu || !trigger || menu.hidden) return;
  const rect = trigger.getBoundingClientRect();
  menu.style.left = "";
  menu.style.top = "";
  menu.style.width = "";
  menu.style.maxHeight = `${Math.max(180, window.innerHeight - rect.bottom - 24)}px`;
}

function positionOpenProductionReportDropdowns() {
  document.querySelectorAll("[data-production-report-filter-field]").forEach((field) => positionProductionReportFilterDropdown(field));
}

function productionReportVisibleRows(rows) {
  const state = analyticsState.productionReport;
  const rigSelected = state.selectedRigs;
  const projectSelected = state.selectedProjects;
  const query = state.wellQuery.trim().toLowerCase();
  if ((state.rigTouched || state.availableRigs.length) && !rigSelected.size) return [];
  if ((state.projectTouched || state.availableProjects.length) && !projectSelected.size) return [];
  return (rows || []).filter((row) => {
    if (rigSelected.size && !rigSelected.has(String(row.rig || ""))) return false;
    if (projectSelected.size && !projectSelected.has(String(row.project_id || ""))) return false;
    if (query && !String(row.wellbore || "").toLowerCase().includes(query)) return false;
    return true;
  });
}

function refreshProductionReportView() {
  const payload = analyticsState.productionReport.payload;
  if (payload) renderProductionReportAnalytics(payload);
}

function initializeNptReportSelections(filters = {}) {
  const state = analyticsState.npt;
  state.availableRigs = (filters.rigs || []).map((rig) => ({ value: rig, label: rig, searchText: String(rig || "").toLowerCase() }));
  state.availableProjects = productionProjectItems(filters.projects || []);
  const rigValues = new Set(state.availableRigs.map((item) => item.value));
  const projectValues = new Set(state.availableProjects.map((item) => item.value));
  let defaultApplied = false;
  if (!state.selectionInitialized) {
    state.selectedRigs = new Set(rigValues);
    state.selectedProjects = new Set(projectValues);
    state.selectionInitialized = true;
    defaultApplied = true;
  } else {
    state.selectedRigs = new Set([...state.selectedRigs].filter((value) => rigValues.has(value)));
    state.selectedProjects = new Set([...state.selectedProjects].filter((value) => projectValues.has(value)));
    if (!state.rigTouched && state.selectedRigs.size !== rigValues.size) state.selectedRigs = new Set(rigValues);
    if (!state.projectTouched && state.selectedProjects.size !== projectValues.size) state.selectedProjects = new Set(projectValues);
  }
  refreshNptReportView();
  return defaultApplied;
}

function refreshNptReportView() {
  const payload = analyticsState.npt.payload;
  if (payload) renderNptAnalytics(payload);
}

function renderNptReportTabs() {
  const state = analyticsState.npt;
  document.querySelectorAll("[data-npt-report-tab]").forEach((button) => {
    const active = button.dataset.nptReportTab === state.activeTab;
    button.classList.toggle("active", active);
    button.setAttribute("aria-selected", active ? "true" : "false");
  });
}

function renderNptReportSide() {
  const state = analyticsState.npt;
  const host = document.querySelector("[data-npt-report-side]");
  if (!host) return;
  const isRigTab = state.activeTab === "rig";
  const items = isRigTab ? state.availableRigs : state.availableProjects;
  const selected = isRigTab ? state.selectedRigs : state.selectedProjects;
  const title = isRigTab ? "钻井队列表" : "项目列表";
  const placeholder = isRigTab ? "搜索井队" : "搜索项目";
  const term = state.sideSearch.trim().toLowerCase();
  const visibleItems = items.filter((item) => !term || item.searchText.includes(term));
  host.innerHTML = `
    <div class="production-side-heading">
      <div><h3>${escapeHtml(title)}</h3></div>
      <strong>${selected.size}/${items.length}</strong>
    </div>
    <input class="production-side-search" type="search" placeholder="${escapeHtml(placeholder)}" value="${escapeHtml(state.sideSearch)}" data-npt-side-search />
    <div class="production-side-actions">
      <button class="link-button" type="button" data-npt-side-select="all">全选</button>
      <button class="link-button" type="button" data-npt-side-select="clear">清空</button>
    </div>
    <div class="production-side-list">
      ${visibleItems.map((item) => productionReportCheckbox("npt-side-option", item, selected.has(item.value))).join("") || `<div class="empty-records">暂无可选项</div>`}
    </div>
  `;
}

function renderNptReportFilters() {
  const state = analyticsState.npt;
  const host = document.querySelector("[data-npt-report-filters]");
  if (!host) return;
  const isRigTab = state.activeTab === "rig";
  const filterItems = isRigTab ? state.availableProjects : state.availableRigs;
  const selected = isRigTab ? state.selectedProjects : state.selectedRigs;
  const filterType = isRigTab ? "project" : "rig";
  const title = isRigTab ? "项目过滤" : "井队过滤";
  const placeholder = isRigTab ? "搜索合同 / 项目" : "搜索井队";
  const emptyText = isRigTab ? "暂无项目" : "暂无井队";
  const summary = productionReportFilterSummary(filterItems, selected, filterType);
  host.innerHTML = `
    <div class="production-filter-field production-report-filter-dropdown" data-npt-report-filter-field="${escapeHtml(filterType)}">
      <div class="production-filter-label">
        <span>${escapeHtml(title)}</span>
        <em data-npt-report-filter-count>${selected.size}/${filterItems.length}</em>
      </div>
      <button class="project-multiselect-trigger production-report-filter-trigger" type="button" data-npt-report-filter-toggle aria-expanded="false">
        <span data-npt-report-filter-summary title="${escapeHtml(summary.title)}">${escapeHtml(summary.text)}</span>
      </button>
      <div class="project-multiselect-menu production-report-filter-menu" data-npt-report-filter-menu hidden>
        <input class="project-multiselect-search" type="search" placeholder="${escapeHtml(placeholder)}" data-npt-report-filter-search />
        <div class="production-filter-menu-actions">
          <span>可复选，用于进一步收窄当前统计范围</span>
          <div>
            <button class="link-button" type="button" data-npt-filter-select="${filterType}" data-mode="all">全选</button>
            <button class="link-button" type="button" data-npt-filter-select="${filterType}" data-mode="clear">清空</button>
          </div>
        </div>
        <div class="project-multiselect-options production-report-filter-options">
          ${filterItems.map((item) => productionReportCheckbox("npt-filter-option", item, selected.has(item.value), filterType)).join("") || `<div class="project-multiselect-empty">${escapeHtml(emptyText)}</div>`}
        </div>
      </div>
    </div>
    <label class="production-search-field production-filter-field">
      <span>井号搜索</span>
      <input type="search" placeholder="输入井号" value="${escapeHtml(state.keywordQuery)}" data-npt-keyword-query />
    </label>
    <div class="production-report-actions production-filter-field">
      <button class="button production-action-button" type="button" data-analytics-search="npt"><span aria-hidden="true">⌕</span><b data-i18n="search">查询</b></button>
      <button class="button secondary production-action-button" type="button" data-analytics-reset="npt"><span aria-hidden="true">↻</span><b data-i18n="reset">重置</b></button>
      <button class="button secondary production-action-button" type="button" data-analytics-export="npt"><span aria-hidden="true">⇩</span><b>导出Excel</b></button>
    </div>
  `;
}

function currentNptReportFilterItems() {
  const state = analyticsState.npt;
  return state.activeTab === "rig" ? state.availableProjects : state.availableRigs;
}

function currentNptReportFilterSelection() {
  const state = analyticsState.npt;
  return state.activeTab === "rig" ? state.selectedProjects : state.selectedRigs;
}

function setNptReportFilterSelection(type, selected) {
  const state = analyticsState.npt;
  if (type === "project") {
    state.selectedProjects = selected;
    state.projectTouched = true;
  } else {
    state.selectedRigs = selected;
    state.rigTouched = true;
  }
}

function syncNptReportFilterField(field) {
  if (!field) return;
  const type = field.dataset.nptReportFilterField;
  const items = currentNptReportFilterItems();
  const selected = currentNptReportFilterSelection();
  const summary = productionReportFilterSummary(items, selected, type);
  field.querySelector("[data-npt-report-filter-count]") && (field.querySelector("[data-npt-report-filter-count]").textContent = `${selected.size}/${items.length}`);
  const summaryEl = field.querySelector("[data-npt-report-filter-summary]");
  if (summaryEl) {
    summaryEl.textContent = summary.text;
    summaryEl.title = summary.title;
  }
  field.querySelectorAll("[data-npt-filter-option]").forEach((input) => {
    input.checked = selected.has(input.value);
  });
}

function filterNptReportDropdownOptions(field) {
  if (!field) return;
  const term = (field.querySelector("[data-npt-report-filter-search]")?.value || "").trim().toLowerCase();
  field.querySelectorAll("[data-project-option]").forEach((option) => {
    option.hidden = Boolean(term) && !String(option.dataset.projectSearchText || "").toLowerCase().includes(term);
  });
}

function closeNptReportFilterDropdowns(except = null) {
  document.querySelectorAll("[data-npt-report-filter-field]").forEach((field) => {
    if (except && field === except) return;
    const menu = field.querySelector("[data-npt-report-filter-menu]");
    const trigger = field.querySelector("[data-npt-report-filter-toggle]");
    if (menu) menu.hidden = true;
    if (trigger) trigger.setAttribute("aria-expanded", "false");
  });
}

function nptReportVisibleRows(rows) {
  const keyword = analyticsState.npt.keywordQuery.trim().toLowerCase();
  if (!keyword) return rows;
  return rows.filter((row) => String(row.wellbore || "").toLowerCase().includes(keyword));
}

function renderNptAnalytics(payload) {
  const details = payload.details || [];
  const note = document.querySelector('[data-analytics-note="npt"]');
  if (note) note.textContent = payload.scope_note || ui("analyticsNptScope");
  const officialNote = document.querySelector("[data-npt-official-note]");
  if (officialNote) {
    const pendingCount = Number(payload.kpis?.pending_review_count || 0);
    const pendingHours = Number(payload.kpis?.pending_review_hours || 0);
    officialNote.textContent = pendingCount
      ? `正式统计仅含已提交确认的NPT；另有 ${pendingCount} 条 / ${formatHours(pendingHours)}h SC或NPT待确认。`
      : "正式统计仅含已提交确认的NPT；当前没有待确认SC/NPT。";
  }
  renderNptReportTabs();
  renderNptReportSide();
  renderNptReportFilters();
  renderNptTable(nptReportVisibleRows(details));
}

const REPORT_TYPE_LABELS_JS = {
  drilling: { zh: "钻井", en: "Drilling", es: "Perforación" },
  completion: { zh: "完井", en: "Completion", es: "Completación" },
  workover: { zh: "修井", en: "Workover", es: "Workover" },
  move: { zh: "搬迁/推井架", en: "Rig Move", es: "Movilización" }
};
const CHART_COLORS = ["#1f6ff2", "#ff9f1c", "#23b8a7", "#8b5cf6", "#f5b755", "#37a2ff", "#7c8fb8"];

function analyticsKpi(label, value, caption) {
  return `<div class="analytics-kpi"><span>${escapeHtml(label)}</span><strong>${metricValueHtml(value)}</strong><small>${escapeHtml(caption || ui("analyticsDefaultCaption"))}</small></div>`;
}

function reportTypeLabel(value) {
  const key = String(value || "").toLowerCase();
  return REPORT_TYPE_LABELS_JS[key]?.[currentLanguage] || REPORT_TYPE_LABELS_JS[key]?.zh || value || "";
}

function reasonLabel(value) {
  const text = String(value || "");
  if (!text || text === "未填写 OP CODE / OP SUB") return ui("reasonMissing");
  return text;
}

function statusLabel(value) {
  const text = String(value || "");
  if (text === "有告警") return ui("warningStatus");
  if (text === "正常") return ui("normalStatus");
  return text;
}

function metricValueHtml(value) {
  const text = String(value ?? "");
  const match = text.match(/^(.+?)(?:\s+)?(h|%)$/);
  if (!match) return escapeHtml(text);
  return `${escapeHtml(match[1])}<small>${escapeHtml(match[2])}</small>`;
}

function renderProductionNptRanking(selector, rows) {
  const host = document.querySelector(selector);
  if (!host) return;
  const usable = [...(rows || [])]
    .sort((left, right) => Number(right.hours || 0) - Number(left.hours || 0));
  if (!usable.length) return host.innerHTML = emptyAnalytics();
  const max = Math.max(...usable.map((row) => Number(row.hours || 0)), 1);
  host.innerHTML = `
    <div class="production-npt-ranking">
      ${usable.map((row, index) => {
        const hours = Number(row.hours || 0);
        const width = hours > 0 ? Math.max(4, (hours / max) * 100) : 0;
        return `
          <div class="production-npt-rank-row">
            <span class="production-npt-rank-no">${index + 1}</span>
            <strong>${escapeHtml(row.label || "-")}</strong>
            <div class="production-npt-rank-track"><i style="width:${width}%"></i></div>
            <b>${formatHours(row.hours)}</b>
          </div>
        `;
      }).join("")}
    </div>
    <div class="production-npt-ranking-caption"><i></i>${escapeHtml(ui("productionNptCaption"))}</div>
  `;
}

const PRODUCTION_GANTT_TYPES = [
  { key: "move", label: "搬迁", start: "move_date", end: "move_date", hours: "move_hours", color: "#f59e0b" },
  { key: "drilling", label: "钻井", start: "drilling_start_date", end: "drilling_finish_date", hours: "drilling_hours", color: "#2563eb" },
  { key: "completion", label: "完井", start: "completion_date", end: "completion_date", hours: "completion_hours", color: "#f97316" },
  { key: "workover", label: "修井", start: "workover_date", end: "workover_date", hours: "workover_hours", color: "#14b8a6" },
];

function renderProductionWellGantt(selector, payload = {}) {
  const host = document.querySelector(selector);
  if (!host) return;
  const details = Array.isArray(payload.details) ? payload.details : [];
  const rows = productionGanttRows(details);
  const segments = rows.flatMap((row) => row.segments);
  if (!rows.length || !segments.length) {
    host.innerHTML = emptyAnalytics();
    return;
  }
  const timestamps = segments.flatMap((segment) => [parseDateMs(segment.start), parseDateMs(segment.end)]).filter(Number.isFinite);
  const minMs = Math.min(...timestamps);
  const maxMs = Math.max(...timestamps);
  const domainDays = Math.max(1, daysBetweenMs(minMs, maxMs) + 1);
  host.innerHTML = `
    <div class="production-gantt">
      <div class="production-gantt-axis">
        <span>${escapeHtml(formatDateFromMs(minMs))}</span>
        <span>${escapeHtml(formatDateFromMs(maxMs))}</span>
      </div>
      <div class="production-gantt-rows">
        ${rows.map((row) => `
          <div class="production-gantt-row">
            <div class="production-gantt-label">
              <strong>${escapeHtml(row.wellbore || "-")}</strong>
              <span>${escapeHtml(row.rig || "-")} / ${escapeHtml(row.project_name || "-")}</span>
            </div>
            <div class="production-gantt-track">
              ${row.segments.map((segment) => {
                const startOffset = daysBetweenMs(minMs, parseDateMs(segment.start));
                const segmentDays = daysBetweenMs(parseDateMs(segment.start), parseDateMs(segment.end)) + 1;
                const left = Math.max(0, Math.min(100, (startOffset / domainDays) * 100));
                const width = Math.max(3, Math.min(100 - left, (Math.max(1, segmentDays) / domainDays) * 100));
                const title = `${segment.label} ${segment.start}${segment.end !== segment.start ? ` ~ ${segment.end}` : ""} ${formatHours(segment.hours)}h`;
                return `<i class="production-gantt-segment" style="left:${left}%;width:${width}%;background:${segment.color}" title="${escapeHtml(title)}"><span>${escapeHtml(segment.label)}</span></i>`;
              }).join("")}
            </div>
          </div>
        `).join("")}
      </div>
      <div class="production-gantt-legend">
        ${PRODUCTION_GANTT_TYPES.map((type) => `<span><i style="background:${type.color}"></i>${escapeHtml(type.label)}</span>`).join("")}
      </div>
    </div>
  `;
}

function productionGanttRows(details) {
  return (details || []).map((row) => {
    const segments = PRODUCTION_GANTT_TYPES.flatMap((type) => {
      const start = String(row[type.start] || "");
      const end = String(row[type.end] || start);
      const hours = Number(row[type.hours] || 0);
      if (!start || !Number.isFinite(parseDateMs(start)) || hours <= 0) return [];
      return [{ ...type, start, end: end || start, hours }];
    });
    return {
      wellbore: row.wellbore || "",
      rig: row.rig || "",
      project_id: row.project_id || "",
      project_name: row.project_name || row.contract_project || "",
      segments,
    };
  }).filter((row) => row.wellbore && row.segments.length)
    .sort((left, right) => String(left.wellbore).localeCompare(String(right.wellbore), currentLanguage === "zh" ? "zh-Hans" : currentLanguage, { numeric: true, sensitivity: "base" }));
}

function parseDateMs(value) {
  const text = String(value || "").slice(0, 10);
  if (!/^\d{4}-\d{2}-\d{2}$/.test(text)) return NaN;
  return Date.parse(`${text}T00:00:00Z`);
}

function daysBetweenMs(startMs, endMs) {
  return Math.max(0, Math.round((endMs - startMs) / 86400000));
}

function formatDateFromMs(ms) {
  return new Date(ms).toISOString().slice(0, 10);
}

function renderDonut(selector, rows) {
  const host = document.querySelector(selector);
  if (!host) return;
  if (!rows.length || !rows.some((row) => Number(row.value || 0) > 0)) return host.innerHTML = emptyAnalytics();
  const total = rows.reduce((sum, row) => sum + Number(row.value || 0), 0);
  let offset = 0;
  const circles = rows.map((row, index) => {
    const value = Number(row.value || 0);
    const dash = (value / total) * 100;
    const circle = `<circle r="15.9" cx="20" cy="20" fill="transparent" stroke="${CHART_COLORS[index % CHART_COLORS.length]}" stroke-width="8" stroke-dasharray="${dash} ${100 - dash}" stroke-dashoffset="${-offset}" />`;
    offset += dash;
    return circle;
  }).join("");
  host.innerHTML = `<div class="donut-wrap"><svg viewBox="0 0 40 40" class="donut">${circles}</svg><div class="donut-legend">${rows.map((row, index) => `<span><i style="background:${CHART_COLORS[index % CHART_COLORS.length]}"></i>${escapeHtml(row.label)} ${formatHours(row.value)}</span>`).join("")}</div></div>`;
}

function legend(keys) {
  return `<div class="chart-legend">${keys.map((key, index) => `<span><i style="background:${CHART_COLORS[index % CHART_COLORS.length]}"></i>${escapeHtml(key)}</span>`).join("")}</div>`;
}

function emptyAnalytics() {
  return `<div class="empty-records">${escapeHtml(ui("noAnalyticsData"))}</div>`;
}

function renderProductionTable(rows) {
  const host = document.querySelector('[data-table-host="production"]');
  if (!host) return;
  if (!rows.length) return host.innerHTML = emptyAnalytics();
  const sortedRows = analyticsSortedRows("production", rows);
  const { pageRows, currentPage, totalPages } = analyticsPageSlice("production", sortedRows);
  const headers = [
    analyticsSortHeader("production", "rig", ui("tableRig")),
    analyticsSortHeader("production", "wellbore", ui("tableWell")),
    analyticsSortHeader("production", "report_type", ui("tableReportType")),
    analyticsSortHeader("production", "start_date", ui("tableStartDate")),
    analyticsSortHeader("production", "end_date", ui("tableEndDate")),
    analyticsSortHeader("production", "drilling_hours", ui("tableDrillingHours")),
    analyticsSortHeader("production", "completion_hours", ui("tableCompletionHours")),
    analyticsSortHeader("production", "workover_hours", ui("tableWorkoverHours")),
    analyticsSortHeader("production", "move_hours", ui("tableMoveHours")),
    analyticsSortHeader("production", "npt_hours", ui("tableNptHours")),
    `<th>${escapeHtml(ui("tableRemarks"))}</th>`
  ].join("");
  host.innerHTML = `<table class="record-table analytics-table"><thead><tr>${headers}</tr></thead><tbody>${pageRows.map((row) => `<tr data-open-record="${escapeHtml(row.record_id)}" data-report-type="${escapeHtml(row.report_type)}"><td>${escapeHtml(row.rig)}</td><td>${escapeHtml(row.wellbore)}</td><td>${escapeHtml(reportTypeLabel(row.report_type))}</td><td>${escapeHtml(row.start_date)}</td><td>${escapeHtml(row.end_date)}</td><td>${formatHours(row.drilling_hours)}</td><td>${formatHours(row.completion_hours)}</td><td>${formatHours(row.workover_hours)}</td><td>${formatHours(row.move_hours)}</td><td>${formatHours(row.npt_hours)}</td><td>${escapeHtml(statusLabel(row.status))}</td></tr>`).join("")}</tbody></table>${analyticsPaginationMarkup("production", currentPage, totalPages, rows.length)}`;
}

function renderProductionReportTable(rows) {
  const host = document.querySelector('[data-table-host="productionReport"]');
  if (!host) return;
  if (!rows.length) return host.innerHTML = emptyAnalytics();
  const sortedRows = analyticsSortedRows("productionReport", rows);
  const { pageRows, currentPage, totalPages } = analyticsPageSlice("productionReport", sortedRows);
  const showRig = analyticsState.productionReport.activeTab === "project";
  const headers = [
    analyticsSortHeader("productionReport", "wellbore", ui("tableWell")),
    showRig ? analyticsSortHeader("productionReport", "rig", ui("tableRig")) : "",
    analyticsSortHeader("productionReport", "contract_project", ui("tableContractProject")),
    analyticsSortHeader("productionReport", "move_date", ui("tableMoveDate")),
    analyticsSortHeader("productionReport", "drilling_start_date", ui("tableDrillingStartDate")),
    analyticsSortHeader("productionReport", "drilling_finish_date", ui("tableDrillingFinishDate")),
    analyticsSortHeader("productionReport", "completion_date", ui("tableCompletionDate")),
    analyticsSortHeader("productionReport", "workover_date", ui("tableWorkoverDate")),
    analyticsSortHeader("productionReport", "move_hours", ui("tableMoveHours")),
    analyticsSortHeader("productionReport", "drilling_hours", ui("tableDrillingHours")),
    analyticsSortHeader("productionReport", "completion_hours", ui("tableCompletionHours")),
    analyticsSortHeader("productionReport", "workover_hours", ui("tableWorkoverHours")),
    analyticsSortHeader("productionReport", "npt_hours", ui("tableNptHours")),
    `<th>${escapeHtml(ui("tableRemarks"))}</th>`
  ].filter(Boolean).join("");
  host.innerHTML = `<table class="record-table analytics-table production-report-table"><thead><tr>${headers}</tr></thead><tbody>${pageRows.map((row) => {
    const rigCell = showRig ? `<td>${escapeHtml(row.rig || "-")}</td>` : "";
    return `<tr><td>${productionReportWellShortcut(row)}</td>${rigCell}<td>${escapeHtml(row.contract_project || row.project_name || "-")}</td><td>${escapeHtml(row.move_date || "-")}</td><td>${escapeHtml(row.drilling_start_date || "-")}</td><td>${escapeHtml(row.drilling_finish_date || "-")}</td><td>${escapeHtml(row.completion_date || "-")}</td><td>${escapeHtml(row.workover_date || "-")}</td><td>${formatHours(row.move_hours)}</td><td>${formatHours(row.drilling_hours)}</td><td>${formatHours(row.completion_hours)}</td><td>${formatHours(row.workover_hours)}</td><td>${formatHours(row.npt_hours)}</td><td>${productionRemarkCell(row)}</td></tr>`;
  }).join("")}</tbody></table>${analyticsPaginationMarkup("productionReport", currentPage, totalPages, rows.length)}`;
}

function productionReportWellShortcut(row) {
  const wellbore = row.wellbore || "";
  if (!wellbore) return "<strong>-</strong>";
  const reportType = normalizeReportType(row.report_type || "drilling");
  return `<button class="link-button production-well-shortcut" type="button" data-open-report-home data-report-type="${escapeHtml(reportType)}" data-wellbore="${escapeHtml(wellbore)}"><strong>${escapeHtml(wellbore)}</strong></button>`;
}

function productionRemarkCell(row) {
  return `
    <div class="production-remark-cell">
      <textarea class="production-remark-input" data-production-remark data-remark-key="${escapeHtml(row.remark_key || "")}" maxlength="500" rows="1">${escapeHtml(row.remarks || "")}</textarea>
      <button class="link-button production-remark-save" type="button" data-production-remark-save data-remark-key="${escapeHtml(row.remark_key || "")}">保存</button>
    </div>
  `;
}

async function saveProductionRemark(button) {
  if (!frontCan("save")) return showToast("当前账号没有保存权限");
  const cell = button.closest(".production-remark-cell");
  const remarkKey = button.dataset.remarkKey || cell?.querySelector("[data-production-remark]")?.dataset.remarkKey || "";
  const input = cell?.querySelector("[data-production-remark]");
  if (!remarkKey || !input) return showToast("缺少备注行标识");
  const remarks = input.value.trim();
  button.disabled = true;
  try {
    const response = await fetch("/api/production-report-remarks", {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ remark_key: remarkKey, remarks }),
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(payload.error || "备注保存失败");
    const rows = analyticsState.productionReport.payload?.details || [];
    rows.forEach((row) => {
      if (row.remark_key === remarkKey) row.remarks = payload.remarks || "";
    });
    showToast("备注已保存");
  } catch (error) {
    showToast(error.message || "备注保存失败");
  } finally {
    button.disabled = false;
  }
}

function renderNptTable(rows) {
  const host = document.querySelector('[data-table-host="npt"]');
  if (!host) return;
  if (!rows.length) return host.innerHTML = emptyAnalytics();
  const sortedRows = analyticsSortedRows("npt", rows);
  const { pageRows, currentPage, totalPages } = analyticsPageSlice("npt", sortedRows);
  const showRig = analyticsState.npt.activeTab === "project";
  const headers = [
    analyticsSortHeader("npt", "wellbore", ui("tableWell")),
    showRig ? analyticsSortHeader("npt", "rig", ui("tableRig")) : "",
    analyticsSortHeader("npt", "project_name", "项目"),
    analyticsSortHeader("npt", "reportDate", ui("tableDate")),
    analyticsSortHeader("npt", "time_range", "NPT时间段"),
    analyticsSortHeader("npt", "hours", ui("tableNptHours")),
    analyticsSortHeader("npt", "service_line", "责任方 Service Line"),
    analyticsSortHeader("npt", "reason", "NPT描述关键词"),
    `<th>${escapeHtml("备注（NPT描述）")}</th>`
  ].filter(Boolean).join("");
  host.innerHTML = `<table class="record-table analytics-table npt-detail-table-lite npt-report-table ${showRig ? "npt-show-rig" : ""}"><thead><tr>${headers}</tr></thead><tbody>${pageRows.map((row) => {
    const rigCell = showRig ? `<td>${escapeHtml(row.rig || "-")}</td>` : "";
    const projectName = row.project_name || row.contract_project || "-";
    const keyword = row.op_sub || row.op_code || reasonLabel(row.reason) || "-";
    const description = localizedOperationDescription(row);
    const timeRange = row.time_range || [row.from, row.to].filter(Boolean).join(" - ") || "-";
    return `<tr data-open-record="${escapeHtml(row.record_id)}" data-report-type="${escapeHtml(row.report_type)}"><td>${escapeHtml(row.wellbore || "-")}</td>${rigCell}<td>${escapeHtml(projectName)}</td><td>${escapeHtml(row.reportDate || "-")}</td><td>${escapeHtml(timeRange)}</td><td>${formatHours(row.hours)}</td><td>${nptExtractionCell(row)}</td><td>${escapeHtml(keyword)}</td><td class="npt-report-description"><button type="button" class="npt-report-description-button" data-npt-description="${escapeHtml(description.text)}">${translationStateBadge(description.translated)}${escapeHtml(description.text)}</button></td></tr>`;
  }).join("")}</tbody></table>${analyticsPaginationMarkup("npt", currentPage, totalPages, rows.length)}`;
}

function nptExtractionCell(row = {}) {
  const status = String(row.extraction_status || "").toUpperCase();
  const labels = {
    PENDING: "待提炼", QUEUED: "排队中", IN_PROGRESS: "提炼中", COMPLETED: row.service_line ? "已提炼" : "未识别",
    FAILED: "更新失败", STALE: "规则已更新", NOT_REQUIRED: "无需提炼"
  };
  const label = labels[status] || "待提炼";
  const tone = status === "COMPLETED" ? (row.service_line ? "completed" : "empty") : status.toLowerCase() || "pending";
  const title = row.extraction_error || `AI 数据提炼状态：${label}`;
  return `<div class="npt-extraction-cell" title="${escapeHtml(title)}"><span>${escapeHtml(row.service_line || "-")}</span><small class="npt-extraction-status ${escapeHtml(tone)}">${escapeHtml(label)}</small></div>`;
}

async function loadNptConfirmations() {
  const params = new URLSearchParams();
  const filterHost = document.querySelector("#nptConfirmPage .npt-confirm-filter");
  if (filterHost) {
    const wellbore = filterHost.querySelector('[name="nptWellbore"]')?.value.trim() || nptConfirmState.filters.wellbore;
    const status = filterHost.querySelector('[name="nptStatus"]')?.value || nptConfirmState.filters.status;
    const rig = filterHost.querySelector('[name="nptRig"]')?.value || nptConfirmState.filters.rig;
    if (wellbore) params.set("wellbore", wellbore);
    if (status) params.set("status", status);
    if (rig) params.set("rig", rig);
  }
  nptConfirmState.loading = true;
  try {
    const response = await fetch(`/api/npt-confirmations?${params.toString()}`);
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || "NPT确认列表加载失败");
    nptConfirmState.items = payload.items || [];
    nptConfirmState.scope = payload.scope || { all_rigs: false, rig: "" };
    nptConfirmState.loading = false;
    populateNptConfirmFilters(payload.filters || {});
    showNptConfirmList();
  } catch (error) {
    console.error(error);
    showToast(error.message || "NPT确认列表加载失败");
  } finally {
    nptConfirmState.loading = false;
  }
}

function populateNptConfirmFilters(filters) {
  const host = document.querySelector("#nptConfirmPage .npt-confirm-filter");
  if (!host) return;
  setSelectOptions(host.querySelector('[name="nptRig"]'), filters.rigs || [], "全部井队");
  setSelectOptions(host.querySelector('[name="nptStatus"]'), (filters.statuses || []).map((item) => [item.value, item.label]), "全部状态");
  host.querySelector('[name="nptWellbore"]').value = nptConfirmState.filters.wellbore || "";
  host.querySelector('[name="nptRig"]').value = nptConfirmState.filters.rig || "";
  host.querySelector('[name="nptStatus"]').value = nptConfirmState.filters.status || "";
  const note = document.querySelector("[data-npt-scope-note]");
  if (note) note.textContent = nptConfirmState.scope.all_rigs ? "当前账号可查看全部井队" : (nptConfirmState.scope.rig ? `当前账号仅查看 ${nptConfirmState.scope.rig}` : "当前账号未配置井队限制");
}

function showNptConfirmList() {
  setNptConfirmBreadcrumb("");
  document.querySelector('[data-npt-confirm-view="list"]').hidden = false;
  document.querySelector('[data-npt-confirm-view="detail"]').hidden = true;
  const tbody = document.querySelector("[data-npt-confirm-list]");
  if (!tbody) return;
  if (nptConfirmState.loading) {
    tbody.innerHTML = `<tr><td colspan="7">加载中...</td></tr>`;
    return;
  }
  if (!nptConfirmState.items.length) {
    tbody.innerHTML = `<tr><td colspan="7">暂无需要确认的井；系统识别全部为 P 的井不会进入确认列表。</td></tr>`;
    return;
  }
  tbody.innerHTML = nptConfirmState.items.map((item) => `
    <tr>
      <td><strong>${escapeHtml(item.wellbore)}</strong></td>
      <td>${escapeHtml(item.rig)}</td>
      <td>${escapeHtml(item.start_date || "-")}</td>
      <td>${escapeHtml(item.end_date || "-")}</td>
      <td><span class="npt-hours-pill">SC ${formatHours(item.sc_hours)}h</span><span class="npt-hours-pill danger">NPT ${formatHours(item.npt_hours)}h</span></td>
      <td>${nptConfirmStatusPill(item.status)}</td>
      <td class="npt-row-actions">
        <button class="button small secondary" type="button" data-npt-open="${escapeHtml(item.wellbore)}" data-rig="${escapeHtml(item.rig)}">查看</button>
      </td>
    </tr>
  `).join("");
}

function nptConfirmStatusPill(status) {
  const map = {
    pending: ["warning", "待确认"],
    draft: ["type-pill", "确认中"],
    confirmed: ["uploaded", "已确认"],
  };
  const [tone, label] = map[status] || map.pending;
  return `<span class="status-pill ${tone}">${label}</span>`;
}

async function openNptConfirmationDetail(wellbore, rig = "", readonly = false) {
  try {
    const params = new URLSearchParams({ wellbore });
    if (rig) params.set("rig", rig);
    const response = await fetch(`/api/npt-confirmation?${params.toString()}`);
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || "NPT确认详情加载失败");
    nptConfirmState.detail = payload;
    nptConfirmState.expandedRows = new Set();
    renderNptConfirmationDetail(readonly);
  } catch (error) {
    console.error(error);
    showToast(error.message || "NPT确认详情加载失败");
  }
}

function renderNptConfirmationDetail(readonly = false) {
  const detail = nptConfirmState.detail;
  if (!detail) return;
  const meta = detail.meta || {};
  const locked = readonly || Boolean(meta.locked);
  document.querySelector('[data-npt-confirm-view="list"]').hidden = true;
  document.querySelector('[data-npt-confirm-view="detail"]').hidden = false;
  setNptConfirmBreadcrumb(meta.wellbore ? `${meta.wellbore}时效确认` : "时效确认");
  document.querySelector("[data-npt-detail-meta]").innerHTML = [
    nptMetaItem("井号", meta.wellbore || "-"),
    nptMetaItem("井队", meta.rig || "-"),
    nptMetaItem("开钻日期", meta.start_date || "-"),
    nptMetaItem("完井日期", meta.end_date || "-"),
    nptMetaItem("当前状态", nptConfirmStatusText(meta.status)),
  ].join("");
  const onlyScNpt = document.querySelector("[data-npt-only-sc-npt]");
  if (onlyScNpt) onlyScNpt.checked = true;
  renderNptOperationRows(locked);
  const note = document.querySelector('[name="nptConfirmNote"]');
  note.value = meta.confirmation_note || "";
  note.disabled = locked;
  updateNptNoteCount();
  document.querySelector("[data-npt-save]").disabled = locked || !frontCan("save");
  document.querySelector("[data-npt-submit]").disabled = locked || !frontCan("save");
  if (locked) showToast("该井已确认锁定，只能查看。");
}

function renderNptOperationRows(locked = false) {
  const detail = nptConfirmState.detail;
  if (!detail) return;
  const rowsHost = document.querySelector("[data-npt-detail-rows]");
  const onlyScNpt = document.querySelector("[data-npt-only-sc-npt]")?.checked ?? true;
  const rows = detail.operations || [];
  const visibleRows = rows
    .map((row, index) => ({ row, index }))
    .filter(({ row }) => !onlyScNpt || ["SC", "NPT"].includes(String(row.system_op_type || "").toUpperCase()));
  if (!visibleRows.length) {
    rowsHost.innerHTML = `<tr><td colspan="7">当前没有 SC 或 NPT 时效。</td></tr>`;
    return;
  }
  rowsHost.innerHTML = visibleRows.map(({ row, index }) => {
    const description = localizedOperationDescription(row);
    const sourceType = String(row.system_op_type || "").toUpperCase();
    const effectiveType = String(row.confirmed_op_type || sourceType).toUpperCase();
    const needsReview = ["SC", "NPT"].includes(sourceType);
    const expanded = nptConfirmState.expandedRows.has(index);
    return `
    <tr data-npt-row="${index}">
      <td>${escapeHtml((row.reportDate || "").slice(5) || "-")}</td>
      <td>${escapeHtml(row.from || "-")} ~ ${escapeHtml(row.to || "-")}</td>
      <td class="npt-description-cell"><button type="button" class="npt-description-preview" data-npt-description="${escapeHtml(description.text)}">${translationStateBadge(description.translated)}${escapeHtml(description.text)}</button></td>
      <td>${opTypePill(sourceType)}</td>
      <td>${opTypePill(effectiveType)}<small class="npt-review-state">${needsReview ? nptReviewStatusLabel(row.review_status) : "直接生效"}</small></td>
      <td>${formatHours(row.hours)}</td>
      <td>${needsReview ? `<button class="button small secondary" type="button" data-npt-classify="${index}">${expanded ? "收起" : "进一步划定"}</button>` : `<span class="status-pill uploaded">无需确认</span>`}</td>
    </tr>
    ${expanded && needsReview ? nptClassificationEditorRow(row, index, locked) : ""}
  `;
  }).join("");
}

function nptReviewStatusLabel(status = "") {
  return ({ AUTO_CONFIRMED: "直接生效", PENDING: "待确认", DRAFT: "草稿", CONFIRMED: "已确认" })[String(status).toUpperCase()] || "待确认";
}

function nptFormOptions(values, current = "", placeholder = "请选择") {
  return `<option value="">${placeholder}</option>${values.map(([value, label]) => `<option value="${value}" ${value === current ? "selected" : ""}>${label}</option>`).join("")}`;
}

function nptClassificationEditorRow(row, index, locked) {
  const selectedType = String(row.confirmed_op_type || row.system_op_type || "").toUpperCase();
  const typeOptions = timeTypeValues.map((item) => [String(item.value_code || "").toUpperCase(), item.value_name || item.value_code]);
  return `<tr class="npt-classification-editor-row" data-npt-classification-row="${index}"><td colspan="7">
    <section class="npt-classification-editor">
      <div class="npt-classification-editor-heading"><strong>进一步人工划定</strong><span>调整类型后，SC/NPT必须指定责任方及工作量归类；有人/无人待工直接在工作量归类中选择。</span></div>
      <div class="npt-classification-fields">
        <label>复核类型<select data-npt-confirm-type ${locked ? "disabled" : ""}>${nptFormOptions(typeOptions, selectedType, "请选择类型")}</select></label>
        <label>工作量归类<select data-npt-work-bucket ${locked ? "disabled" : ""}>${nptFormOptions(nptReferenceValues.WORK_BUCKET, row.work_bucket, "请选择（必填）")}</select></label>
        <label>责任方<select data-npt-responsibility ${locked ? "disabled" : ""}>${nptFormOptions(nptReferenceValues.RESPONSIBILITY, row.responsibility, "请选择（必填）")}</select></label>
        <label>计费状态<select data-npt-billing ${locked ? "disabled" : ""}>${nptFormOptions(nptReferenceValues.BILLING_STATUS, row.billing_status, "请选择（选填）")}</select></label>
        <label>原因编码<select data-npt-cause ${locked ? "disabled" : ""}>${nptFormOptions(nptReferenceValues.CAUSE_CODE, row.cause_code, "请选择（选填）")}</select></label>
        <label>服务线<input data-npt-service-line value="${escapeHtml(row.service_line || "")}" placeholder="机组、泥浆、定向、固井等" ${locked ? "disabled" : ""} /></label>
      </div>
    </section>
  </td></tr>`;
}

function usesTranslatedOperationDescriptions() {
  return currentLanguage === "zh" && reportContentLanguageMode === "translated";
}

function localizedOperationDescription(row = {}) {
  const source = row.operation_details || row.op_sub || row.op_code || "-";
  const translated = String(row.operation_translation_status || "").toUpperCase() === "COMPLETED"
    && String(row.translated_operation_details || "").trim();
  if (usesTranslatedOperationDescriptions() && translated) {
    return { text: String(row.translated_operation_details).trim(), translated: true };
  }
  return { text: source, translated: false };
}

function translationStateBadge(translated) {
  if (!usesTranslatedOperationDescriptions()) return "";
  const label = translated ? "译" : "原";
  const title = translated ? "已显示中文译文" : "暂无有效译文，显示原文";
  return `<small class="operation-translation-badge ${translated ? "translated" : "source"}" title="${title}">${label}</small>`;
}

function renderLocalizedOperationDescriptions() {
  if (analyticsState.productionReport.payload) renderProductionReportTable(productionReportVisibleRows(analyticsState.productionReport.payload.details || []));
  if (analyticsState.npt.payload) renderNptTable(nptReportVisibleRows(analyticsState.npt.payload.details || []));
  if (nptConfirmState.detail) renderNptOperationRows(Boolean(nptConfirmState.detail.meta?.locked));
}

function nptMetaItem(label, value) {
  return `<div><span>${escapeHtml(label)}</span><strong>${escapeHtml(value)}</strong></div>`;
}

function nptConfirmStatusText(status) {
  return ({ pending: "待确认", draft: "确认中", confirmed: "已确认" }[status] || "待确认");
}

function opTypePill(type) {
  const normalized = String(type || "").toUpperCase();
  const tone = normalized === "NPT" ? "danger" : normalized === "SC" ? "sc" : "pt";
  return `<span class="op-type-pill ${tone}">${escapeHtml(normalized || "-")}</span>`;
}

function showNptDescriptionPopover(trigger) {
  const text = trigger?.dataset?.nptDescription || trigger?.textContent || "";
  if (!text.trim()) return;
  document.querySelector(".npt-description-popover")?.remove();
  const rect = trigger.getBoundingClientRect();
  const popover = document.createElement("div");
  popover.className = "npt-description-popover";
  popover.setAttribute("role", "dialog");
  popover.setAttribute("aria-label", "完整工况描述");
  popover.tabIndex = 0;
  popover.textContent = text;
  document.body.appendChild(popover);
  const width = Math.min(720, Math.max(420, window.innerWidth - 48));
  const left = Math.min(Math.max(24, rect.left), window.innerWidth - width - 24);
  const top = Math.min(rect.bottom + 8, window.innerHeight - 260);
  popover.style.width = `${width}px`;
  popover.style.left = `${left}px`;
  popover.style.top = `${Math.max(24, top)}px`;
  popover.focus({ preventScroll: true });
}

function collectNptConfirmationRows() {
  const rows = nptConfirmState.detail?.operations || [];
  document.querySelectorAll("[data-npt-classification-row]").forEach((tr) => {
    const index = Number(tr.dataset.nptClassificationRow);
    if (!rows[index]) return;
    rows[index].confirmed_op_type = tr.querySelector("[data-npt-confirm-type]")?.value || rows[index].confirmed_op_type;
    rows[index].work_bucket = tr.querySelector("[data-npt-work-bucket]")?.value || "";
    rows[index].responsibility = tr.querySelector("[data-npt-responsibility]")?.value || "";
    rows[index].billing_status = tr.querySelector("[data-npt-billing]")?.value || "";
    rows[index].cause_code = tr.querySelector("[data-npt-cause]")?.value || "";
    rows[index].service_line = tr.querySelector("[data-npt-service-line]")?.value || "";
  });
  return rows;
}

async function saveNptConfirmation(submit = false) {
  const detail = nptConfirmState.detail;
  if (!detail) return;
  const meta = detail.meta || {};
  const operations = collectNptConfirmationRows();
  const note = document.querySelector('[name="nptConfirmNote"]')?.value || "";
  if (submit) {
    const incompleteIndex = operations.findIndex((row) => {
      if (!["SC", "NPT"].includes(String(row.system_op_type || "").toUpperCase())) return false;
      const confirmed = String(row.confirmed_op_type || row.system_op_type || "").toUpperCase();
      return confirmed !== "P" && (!row.work_bucket || !row.responsibility);
    });
    if (incompleteIndex >= 0) {
      nptConfirmState.expandedRows.add(incompleteIndex);
      renderNptOperationRows(false);
      showToast("提交前请完成每条SC/NPT的工作量归类和责任方划定。");
      return;
    }
  }
  try {
    const response = await fetch("/api/npt-confirmation", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ wellbore: meta.wellbore, rig: meta.rig, note, operations, submit })
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || "NPT确认保存失败");
    showToast(submit ? "已提交确认并锁定该井日报。" : "已保存NPT确认。");
    await loadNptConfirmations();
    if (!submit) await openNptConfirmationDetail(meta.wellbore, meta.rig);
  } catch (error) {
    console.error(error);
    showToast(error.message || "NPT确认保存失败");
  }
}

function updateNptNoteCount() {
  const note = document.querySelector('[name="nptConfirmNote"]');
  const counter = document.querySelector("[data-npt-note-count]");
  if (counter) counter.textContent = String((note?.value || "").length);
}

function downloadProductionReportExcelFromServer() {
  const state = analyticsState.productionReport;
  const params = analyticsFilterValues("productionReport");
  params.set("view", state.activeTab);
  if (state.sortField) {
    params.set("sort_field", state.sortField);
    params.set("sort_dir", state.sortDir || "desc");
  }
  const link = document.createElement("a");
  link.href = `/api/production-summary-export?${params.toString()}`;
  link.download = "";
  link.style.display = "none";
  document.body.appendChild(link);
  link.click();
  link.remove();
}

function downloadNptReportExcelFromServer() {
  const state = analyticsState.npt;
  const params = analyticsFilterValues("npt");
  params.set("view", state.activeTab);
  if (state.sortField) {
    params.set("sort_field", state.sortField);
    params.set("sort_dir", state.sortDir || "desc");
  }
  const link = document.createElement("a");
  link.href = `/api/npt-stats-export?${params.toString()}`;
  link.download = "";
  link.style.display = "none";
  document.body.appendChild(link);
  link.click();
  link.remove();
}

function exportAnalytics(kind) {
  const payload = analyticsState[kind].payload;
  if (!payload) return;
  const rows = kind === "productionReport"
    ? productionReportVisibleRows(payload.details || [])
    : kind === "npt"
      ? nptReportVisibleRows(payload.details || [])
      : payload.details || [];
  if (!rows.length) return showToast(ui("noExportData"));
  if (kind === "productionReport") {
    downloadProductionReportExcelFromServer();
    return;
  }
  if (kind === "npt") {
    downloadNptReportExcelFromServer();
    return;
  }
  const headers = Object.keys(rows[0]);
  const csv = [headers.join(","), ...rows.map((row) => headers.map((key) => `"${String(row[key] ?? "").replace(/"/g, '""')}"`).join(","))].join("\n");
  const blob = new Blob(["\ufeff", csv], { type: "text/csv;charset=utf-8" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = `${kind}-analytics.csv`;
  link.style.display = "none";
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(link.href);
}

async function adminRequest(path, options = {}) {
  return window.NexoHttp.requestJson(path, options, "后台请求失败");
}

function splitAt(value, marker = "@") {
  const text = String(value || "");
  if (!text.includes(marker)) return [text.trim(), ""];
  const [left, right] = text.split(marker, 2);
  return [left.trim(), right.trim()];
}

function splitSlash(value, count) {
  const parts = String(value || "").split("/").map((part) => part.trim());
  while (parts.length < count) parts.push("");
  return parts.slice(0, count);
}

function joinSlash(...values) {
  return values.some((value) => String(value || "").trim()) ? values.map((value) => String(value || "").trim()).join(" / ") : "";
}

function joinAt(size, depth) {
  const left = String(size || "").trim();
  const right = String(depth || "").trim();
  if (left && right) return `${left} @ ${right}`;
  if (left) return left;
  return right ? `@ ${right}` : "";
}

function expandLegacyFields(fields = {}) {
  const expanded = { ...fields };
  if ((!expanded.lastCasingSize && !expanded.lastCasingDepth) && expanded.lastCasing) {
    [expanded.lastCasingSize, expanded.lastCasingDepth] = splitAt(expanded.lastCasing);
  }
  if ((!expanded.nextCasingSize && !expanded.nextCasingDepth) && expanded.nextCasing) {
    [expanded.nextCasingSize, expanded.nextCasingDepth] = splitAt(expanded.nextCasing);
  }
  if (!expanded.formTestType && expanded.formTestEmw) {
    expanded.formTestType = String(expanded.formTestEmw).match(/\b(FIT|LOT)\b/i)?.[1]?.toUpperCase() || "";
  }
  if ((!expanded.stringWeightUp && !expanded.stringWeightDown) && expanded.stringWeightUpDown) {
    [expanded.stringWeightUp, expanded.stringWeightDown] = numericValues(expanded.stringWeightUpDown, 2);
  }
  if ((!expanded.mudTime && !expanded.mudMd) && expanded.mudTimeMd) {
    [expanded.mudTime, expanded.mudMd] = splitSlash(expanded.mudTimeMd, 2);
  }
  if ((!expanded.pv && !expanded.yp) && expanded.pvYp) {
    [expanded.pv, expanded.yp] = splitSlash(expanded.pvYp, 2);
  }
  if ((!expanded.gel10s && !expanded.gel10m && !expanded.gel30m) && expanded.gels) {
    [expanded.gel10s, expanded.gel10m, expanded.gel30m] = splitSlash(expanded.gels, 3);
  }
  if ((!expanded.oilPercent && !expanded.waterPercent) && expanded.oilWater) {
    [expanded.oilPercent, expanded.waterPercent] = splitSlash(expanded.oilWater, 2);
  }
  return expanded;
}

function normalizedReportFields(fields = {}) {
  const normalized = expandLegacyFields(fields);
  STRICT_NUMERIC_REPORT_FIELDS.forEach((name) => { normalized[name] = numericDatumValue(normalized[name]); });
  normalized.formTestType = ["FIT", "LOT"].includes(String(normalized.formTestType || "").toUpperCase()) ? String(normalized.formTestType).toUpperCase() : "";
  normalized.lastBopPressTest = dateInputValue(normalized.lastBopPressTest);
  normalized.lastCasing = joinAt(normalized.lastCasingSize, normalized.lastCasingDepth);
  normalized.nextCasing = joinAt(normalized.nextCasingSize, normalized.nextCasingDepth);
  normalized.stringWeightUpDown = joinSlash(normalized.stringWeightUp, normalized.stringWeightDown);
  normalized.mudTimeMd = joinSlash(normalized.mudTime, normalized.mudMd);
  normalized.pvYp = joinSlash(normalized.pv, normalized.yp);
  normalized.gels = joinSlash(normalized.gel10s, normalized.gel10m, normalized.gel30m);
  normalized.oilWater = joinSlash(normalized.oilPercent, normalized.waterPercent);
  return normalized;
}

const STRICT_NUMERIC_REPORT_FIELDS = new Set([
  "lastCasingSize", "lastCasingDepth", "nextCasingSize", "nextCasingDepth", "formTestEmw",
  "pumpRate", "pumpPress", "stringWeightUp", "stringWeightDown", "torqueOffBottom", "torqueOnBottom",
  "bitSize", "bhaMdIn", "bhaMdOut", "bhaTotalLength",
]);

function numericValues(value, count = 1) {
  const values = [...String(value ?? "").matchAll(/[-+]?\d[\d,]*(?:\.\d+)?/g)].map((match) => match[0].replaceAll(",", ""));
  while (values.length < count) values.push("");
  return values.slice(0, count);
}

function numericDatumValue(value) {
  return numericValues(value, 1)[0];
}

function dateInputValue(value) {
  const text = String(value ?? "").trim();
  if (/^\d{4}-\d{2}-\d{2}$/.test(text)) return text;
  const match = text.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})$/);
  return match ? `${match[3]}-${match[1].padStart(2, "0")}-${match[2].padStart(2, "0")}` : "";
}

function applyReportFields(fields = {}, targetForm = form) {
  const expanded = expandLegacyFields(fields);
  targetForm.querySelectorAll("[name]").forEach((control) => {
    if (control.type === "checkbox" || control.type === "radio") control.checked = false;
    else control.value = "";
  });
  Object.entries(expanded).forEach(([name, value]) => {
    if (!targetForm.elements[name]) return;
    if (name === "refDatum" || STRICT_NUMERIC_REPORT_FIELDS.has(name)) targetForm.elements[name].value = numericDatumValue(value);
    else if (name === "lastBopPressTest") targetForm.elements[name].value = dateInputValue(value);
    else targetForm.elements[name].value = value ?? "";
  });
}

function formData(targetForm = form) {
  return Object.fromEntries(new FormData(targetForm).entries());
}

function readTable(tableId) {
  const rows = [];
  document.querySelectorAll(`#${tableId} tbody tr`).forEach((tr) => {
    const row = {};
    tableSchemas[tableId].forEach((field, index) => {
      row[field.name] = tr.children[index].querySelector("input, textarea, select").value.trim();
    });
    if (Object.values(row).some(Boolean)) rows.push(row);
  });
  return rows;
}

function pushIssue(issues, issue) {
  issues.push(issue);
}

function resetValidationHints(rootSelector) {
  document.querySelectorAll(`${rootSelector} .invalid, ${rootSelector} .warning-cell`).forEach((el) => el.classList.remove("invalid", "warning-cell"));
  document.querySelectorAll(`${rootSelector} [data-validation-hint-managed]`).forEach((control) => {
    control.classList.remove("has-validation-hint", "has-validation-issue");
    control.removeAttribute("title");
    control.removeAttribute("aria-description");
    delete control.dataset.validationHintManaged;
    delete control.dataset.validationHintText;
  });
  document.querySelectorAll(`${rootSelector} .field-has-validation-hint`).forEach((label) => {
    label.classList.remove("field-has-validation-hint", "field-has-validation-issue");
    label.removeAttribute("title");
  });
  document.querySelectorAll(`${rootSelector} .validation-issue-host`).forEach((host) => {
    host.classList.remove("validation-issue-host");
    host.removeAttribute("data-validation-message");
    host.removeAttribute("title");
  });
}

function applyControlHint(control, text, level = "hint") {
  if (!control || !text) return;
  const current = control.dataset.validationHintText || "";
  const next = current && !current.split("\n").includes(text) ? `${current}\n${text}` : (current || text);
  control.dataset.validationHintManaged = "1";
  control.dataset.validationHintText = next;
  control.title = next;
  control.setAttribute("aria-description", next);
  control.classList.add("has-validation-hint");
  const isIssue = level === "error" || level === "warning";
  control.classList.toggle("has-validation-issue", isIssue);
  const label = control.closest("label");
  if (label) {
    label.classList.add("field-has-validation-hint");
    label.classList.toggle("field-has-validation-issue", isIssue);
    label.title = next;
  }
  const host = label || control.closest("td");
  if (host && isIssue) {
    host.classList.add("validation-issue-host");
    host.dataset.validationMessage = next;
    host.title = next;
  }
}

function markIssues(formEl, issues) {
  issues.forEach((issue) => {
    const className = "invalid";
    if (issue.field && formEl?.elements?.[issue.field]) {
      const controls = formEl.elements[issue.field];
      if (controls.classList) {
        controls.classList.add(className);
        applyControlHint(controls, issue.text, issue.level);
      } else if (typeof controls.length === "number") {
        Array.from(controls).forEach((control) => {
          control.classList?.add(className);
          applyControlHint(control, issue.text, issue.level);
        });
      }
    }
    if (issue.tableId && Number.isInteger(issue.rowIndex) && issue.field) {
      const row = document.querySelectorAll(`#${issue.tableId} tbody tr`)[issue.rowIndex];
      const control = row?.querySelector(`[name='${issue.field}']`);
      if (control) {
        control.classList.add(className);
        applyControlHint(control, issue.text, issue.level);
      }
    }
  });
}

function validateReportDate(issues, data) {
  if (!data.reportDate) return;
  const reportDate = new Date(`${data.reportDate}T00:00:00`);
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  if (reportDate > today) pushIssue(issues, { level: "error", text: message("futureDate"), field: "reportDate" });
}

function validateOperationStartDate(issues, data) {
  if (!data.reportDate || !data.operationStartDate) return;
  const reportDate = new Date(`${data.reportDate}T00:00:00`);
  const startDate = new Date(`${data.operationStartDate}T00:00:00`);
  if (startDate > reportDate) pushIssue(issues, { level: "error", text: message("operationStartDate"), field: "operationStartDate" });
}

function validateMdProgress(issues, data, fields = { today: "todayMd", previous: "prevMd", progress: "progress" }) {
  const todayMd = toNumber(data[fields.today]);
  const prevMd = toNumber(data[fields.previous]);
  const progress = toNumber(data[fields.progress]);
  const computedProgress = Number.isFinite(todayMd) && Number.isFinite(prevMd) ? todayMd - prevMd : 0;
  if (Number.isFinite(todayMd) && Number.isFinite(prevMd) && todayMd < prevMd) {
    pushIssue(issues, { level: "error", text: message("mdOrder"), field: fields.today });
  }
  if (Number.isFinite(progress) && Number.isFinite(todayMd) && Number.isFinite(prevMd) && Math.abs(progress - computedProgress) > 0.5) {
    pushIssue(issues, { level: "warning", text: message("progressMismatch", { value: computedProgress.toFixed(2) }), field: fields.progress });
  }
}

function validateOperationsTable(issues, tableId, rows, validTypes, typeMessageKey, validateTotalHours = true) {
  const stats = operationStats(rows);
  if (!rows.length) {
    pushIssue(issues, { level: "error", text: message("operationMissingTable") });
    return stats;
  }
  const clockHoursByRow = operationClockHoursByRow(rows);
  if (validateTotalHours && Math.abs(stats.total - 24) > 0.05) {
    pushIssue(issues, { level: "error", text: message("operationHours", { value: stats.total.toFixed(2) }) });
  }
  rows.forEach((row, index) => {
    ["from", "to", "hours", "op_code", "operation_details"].forEach((field) => {
      if (!row[field]) pushIssue(issues, { level: "warning", text: message("operationMissing", { row: index + 1, field }), tableId, rowIndex: index, field });
    });
    if (!validTypes.includes(row.op_type)) {
      pushIssue(issues, { level: "warning", text: message(typeMessageKey, { row: index + 1 }), tableId, rowIndex: index, field: "op_type" });
    }
    const hours = toNumber(row.hours);
    if (hours <= 0 || hours > 24) {
      pushIssue(issues, { level: "error", text: message("operationHourRange", { row: index + 1 }), tableId, rowIndex: index, field: "hours" });
    }
    const clockHours = clockHoursByRow.get(index);
    if (Number.isFinite(clockHours) && Number.isFinite(hours) && Math.abs(clockHours - hours) > 0.1) {
      pushIssue(issues, { level: "warning", text: message("operationTimeMismatch", { row: index + 1, value: clockHours.toFixed(2) }), tableId, rowIndex: index, field: "hours" });
    }
  });
  return stats;
}

function operationClockHoursByRow(rows) {
  const durations = new Map();
  let previousEnd = null;
  rows.forEach((row, index) => {
    const start = clockMinutes(row.from);
    const end = clockMinutes(row.to);
    if (!Number.isFinite(start) || !Number.isFinite(end)) return;
    let startAbs = start;
    if (Number.isFinite(previousEnd)) {
      while (startAbs < previousEnd) startAbs += 24 * 60;
    }
    const dayOffset = Math.floor(startAbs / (24 * 60));
    let endAbs = end + dayOffset * 24 * 60;
    while (endAbs < startAbs) endAbs += 24 * 60;
    if (endAbs === startAbs && toNumber(row.hours) >= 23.9) endAbs += 24 * 60;
    durations.set(index, (endAbs - startAbs) / 60);
    previousEnd = endAbs;
  });
  return durations;
}

function clockMinutes(value) {
  const match = String(value || "").trim().match(/^(\d{1,2})[:：](\d{2})$/);
  if (!match) return NaN;
  const hour = Number(match[1]);
  const minute = Number(match[2]);
  if (hour === 24 && minute === 0) return 24 * 60;
  if (hour < 0 || hour > 23 || minute < 0 || minute > 59) return NaN;
  return hour * 60 + minute;
}

function validateIntervalRows(issues, tableId, rows) {
  rows.forEach((row, index) => {
    const topMd = toNumber(row.top_md);
    const baseMd = toNumber(row.base_md);
    const length = toNumber(row.length);
    if (Number.isFinite(topMd) && Number.isFinite(baseMd) && baseMd < topMd) {
      pushIssue(issues, { level: "error", text: message("intervalDepth", { row: index + 1 }), tableId, rowIndex: index, field: "base_md" });
    }
    if (Number.isFinite(length) && length < 0) {
      pushIssue(issues, { level: "error", text: message("intervalLength", { row: index + 1 }), tableId, rowIndex: index, field: "length" });
    }
    ["density", "phase", "penetration", "diameter"].forEach((field) => {
      const value = toNumber(row[field]);
      if (Number.isFinite(value) && value < 0) {
        pushIssue(issues, { level: "error", text: message("negativeValue", { row: index + 1, field }), tableId, rowIndex: index, field });
      }
    });
  });
}

function rowsFromPayload(rows, tableId) {
  return (rows || []).map((row) => tableSchemas[tableId].map((field) => row[field.name] ?? ""));
}

function reportPayload(reportType) {
  const builders = {
    drilling: () => ({
      metadata: { report_type: "drilling", record_id: currentRecordIds.drilling, source_file: drillingSourceFileName },
      report_fields: normalizedReportFields(formData(form)),
      survey_data: readTable("surveyTable"),
      bha_components: readTable("bhaTable"),
      operations: readTable("operationsTable"),
      fluid_losses: readTable("fluidLossTable"),
      bulks: readTable("bulkTable")
    }),
    completion: () => ({
      metadata: { report_type: "completion", record_id: currentRecordIds.completion },
      report_fields: formData(completionForm),
      operations: readTable("completionOperationsTable"),
      bulks: readTable("completionBulkTable"),
      perforation_intervals: readTable("perforationIntervalsTable")
    }),
    workover: () => ({
      metadata: { report_type: "workover", record_id: currentRecordIds.workover },
      report_fields: formData(workoverForm),
      operations: readTable("workoverOperationsTable"),
      bulks: readTable("workoverBulkTable"),
      perforation_intervals: readTable("workoverIntervalsTable")
    }),
    move: () => ({
      metadata: { report_type: "move", record_id: currentRecordIds.move },
      report_fields: formData(moveForm),
      operations: readTable("moveOperationsTable")
    })
  };
  return builders[reportType]();
}

function reportSignature(reportType) {
  try {
    return JSON.stringify(reportPayload(reportType));
  } catch {
    return "";
  }
}

function markReportSaved(reportType) {
  savedReportSignatures[reportType] = reportSignature(reportType);
  updateSaveButton(reportType);
}

function updateSaveButton(reportType) {
  if (!reportType) return;
  const button = document.querySelector(`[data-save-report="${reportType}"]`);
  if (!button) return;
  const translatedMode = reportContentState[reportType]?.mode === "translated";
  button.textContent = ui("saveDatabase");
  const currentSignature = reportSignature(reportType);
  button.disabled = translatedMode || isCurrentReportLocked(reportType) || !currentSignature || currentSignature === savedReportSignatures[reportType];
}

function updateAllSaveButtons() {
  Object.keys(savedReportSignatures).forEach((reportType) => updateSaveButton(reportType));
}

function tableReportType(tableId) {
  if (completionTableIds.includes(tableId)) return "completion";
  if (workoverTableIds.includes(tableId)) return "workover";
  if (moveTableIds.includes(tableId)) return "move";
  return "drilling";
}

async function saveCurrentReport(reportType) {
  const translatedMode = reportContentState[reportType]?.mode === "translated";
  if (!translatedMode && isCurrentReportLocked(reportType)) {
    showToast("该日报已被NPT确认锁定，不能再修改保存。");
    return;
  }
  updateSaveButton(reportType);
  const button = document.querySelector(`[data-save-report="${reportType}"]`);
  if (button?.disabled) return;
  const payload = payloadForSave(reportType);
  try {
    const response = await fetch("/api/save-report", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ report_type: reportType, payload })
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "Save failed");
    payload.metadata = { ...(payload.metadata || {}), ...(result.metadata || {}) };
    rememberRecord(reportType, payload);
    markReportSaved(reportType);
    refreshRecords(reportType);
    showToast(ui("databaseSaved"));
  } catch (error) {
    console.error(error);
    showToast(ui("recordLoadFailed"));
  }
}

function payloadForSave(reportType) {
  const payload = reportPayload(reportType);
  return payload;
}

async function openRecordDetail(reportType, recordId) {
  try {
    const response = await fetch("/api/load-report", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ record_id: recordId })
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || "Load failed");
    if (reportType === "drilling") applyImportedPayload(payload);
    if (reportType === "completion") applyImportedCompletionPayload(payload);
    if (reportType === "workover") applyImportedWorkoverPayload(payload);
    if (reportType === "move") applyImportedMovePayload(payload);
    const record = recordState[reportType].records.find((item) => item.record_id === recordId) || {};
    setServerWarnings(reportType, { metadata: record });
    if (reportType === "drilling") validate();
    if (reportType === "completion") validateCompletion();
    if (reportType === "workover") validateWorkover();
    if (reportType === "move") validateMove();
  } catch (error) {
    console.error(error);
    showToast(ui("databaseSaveFailed"));
  }
}

function applyImportedPayload(payload) {
  setReportOriginalPayload("drilling", payload);
  renderReportPayload("drilling", payload);
  rememberRecord("drilling", payload);
  showReportDetail("drilling");
  markReportSaved("drilling");
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function applyImportedCompletionPayload(payload) {
  setReportOriginalPayload("completion", payload);
  renderReportPayload("completion", payload);
  rememberRecord("completion", payload);
  setActiveMenu("completion-daily");
  showReportDetail("completion");
  markReportSaved("completion");
}

function applyImportedWorkoverPayload(payload) {
  setReportOriginalPayload("workover", payload);
  renderReportPayload("workover", payload);
  rememberRecord("workover", payload);
  setActiveMenu("workover-daily");
  showReportDetail("workover");
  markReportSaved("workover");
}

function applyImportedMovePayload(payload) {
  setReportOriginalPayload("move", payload);
  renderReportPayload("move", payload);
  rememberRecord("move", payload);
  setActiveMenu("move-daily");
  showReportDetail("move");
  markReportSaved("move");
}

function importEndpoint(reportType) {
  return {
    drilling: "/api/import-pdf",
    completion: "/api/import-completion-pdf",
    workover: "/api/import-workover-pdf",
    move: "/api/import-move-pdf"
  }[reportType];
}

async function importReportFiles(reportType, fileList) {
  const files = Array.from(fileList || []).filter(Boolean);
  if (!files.length) return;
  showReportRecords(reportType);
  showToast(`${ui("pdfImporting")} ${files.length}`);
  const jobs = files.map((file) => ({
    id: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
    reportType,
    fileName: file.name,
    status: "queued",
    progress: 0,
    updated_at: new Date().toISOString()
  }));
  uploadJobs.unshift(...jobs);
  renderRecordDashboard(reportType);
  for (const job of jobs) {
    await uploadReportFile(reportType, job, files.find((file) => file.name === job.fileName));
  }
  refreshRecords(reportType);
}

async function uploadReportFile(reportType, job, file) {
  if (!file) return;
  job.status = "parsing";
  job.progress = 15;
  job.updated_at = new Date().toISOString();
  renderRecordDashboard(reportType);
  const body = new FormData();
  body.append("report", file);
  try {
    const response = await fetch(importEndpoint(reportType), { method: "POST", body });
    job.progress = 70;
    renderRecordDashboard(reportType);
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || "PDF import failed");
    payload.metadata = { ...(payload.metadata || {}), source_file: payload.metadata?.source_file || file.name };
    job.status = "done";
    job.progress = 100;
    job.recordId = payload.metadata?.record_id || "";
    job.wellbore = payload.report_fields?.wellbore || "";
    job.reportDate = payload.report_fields?.reportDate || "";
    job.updated_at = new Date().toISOString();
    rememberRecord(reportType, payload);
    await refreshRecords(reportType);
    const index = uploadJobs.findIndex((item) => item.id === job.id);
    if (index >= 0) uploadJobs.splice(index, 1);
    renderRecordDashboard(reportType);
    showToast(ui("pdfImported"));
  } catch (error) {
    console.error(error);
    job.status = "failed";
    job.progress = 100;
    job.error = error?.message || "";
    job.updated_at = new Date().toISOString();
    renderRecordDashboard(reportType);
    showImportError(error);
  }
}

function validate() {
  const data = normalizedReportFields(formData());
  const issues = [];
  const required = ["event", "reportDate", "reportNo", "wellbore", "rig", "todayMd", "progress", "currentOps", "summary24h", "forecast24h", "mudType", "mudDensity"];
  resetValidationHints("#drillingDailyPage");

  required.forEach((name) => {
    if (!String(data[name] || "").trim()) pushIssue(issues, { level: "error", text: message("required", { field: labelFor(name) }), field: name });
  });

  validateReportDate(issues, data);
  validateMdProgress(issues, data);

  const operations = readTable("operationsTable");
  const opStats = validateOperationsTable(
    issues,
    "operationsTable",
    operations,
    timeTypeCodes(),
    "operationType",
    requiresBoundaryHoursValidation("drilling", data)
  );
  setText("#operationHours", formatHours(opStats.total));
  setText("#drillingNptHours", formatHours(opStats.npt));
  setText("#drillingWellDate", formatWellDate(data));

  const todayMd = toNumber(data.todayMd);
  readTable("surveyTable").forEach((row, index) => {
    const md = toNumber(row.md);
    const incl = toNumber(row.incl);
    const dls = toNumber(row.dls);
    if (Number.isFinite(md) && Number.isFinite(todayMd) && md > todayMd) pushIssue(issues, { level: "error", text: message("surveyMd", { row: index + 1 }), tableId: "surveyTable", rowIndex: index, field: "md" });
    if (Number.isFinite(incl) && (incl < 0 || incl > 180)) pushIssue(issues, { level: "error", text: message("surveyIncl", { row: index + 1 }), tableId: "surveyTable", rowIndex: index, field: "incl" });
    if (Number.isFinite(dls) && dls < 0) pushIssue(issues, { level: "error", text: message("surveyDls", { row: index + 1 }), tableId: "surveyTable", rowIndex: index, field: "dls" });
  });

  const density = toNumber(data.mudDensity);
  if (Number.isFinite(density) && (density < 6 || density > 20)) pushIssue(issues, { level: "error", text: message("mudDensity"), field: "mudDensity" });
  const sand = toNumber(data.sand);
  if (Number.isFinite(sand) && sand > 10) pushIssue(issues, { level: "warning", text: message("sand"), field: "sand" });

  readTable("bhaTable").forEach((row, index) => {
    const values = [toNumber(row.od), toNumber(row.id), toNumber(row.joints), toNumber(row.length)];
    if (Number.isFinite(values[0]) && Number.isFinite(values[1]) && values[0] < values[1]) pushIssue(issues, { level: "error", text: message("bhaOdId", { row: index + 1 }), tableId: "bhaTable", rowIndex: index, field: "od" });
    ["od", "id", "joints", "length"].forEach((field, fieldIndex) => {
      if (Number.isFinite(values[fieldIndex]) && values[fieldIndex] < 0) pushIssue(issues, { level: "error", text: message("bhaNegative", { row: index + 1 }), tableId: "bhaTable", rowIndex: index, field });
    });
  });

  if ((data.safetyIncident === "Y" || data.environmentIncident === "Y") && !String(data.incidentComments || "").trim()) {
    pushIssue(issues, { level: "error", text: message("incidentRequired"), field: "incidentComments" });
  }

  markIssues(form, issues);
  renderIssues(issues);
  updateCompletion(required, issues, data);
  return issues;
}

function validateCompletion() {
  const data = formData(completionForm);
  const issues = [];
  const required = ["event", "reportDate", "reportNo", "wellbore", "rig", "currentOps", "summary24h", "forecast24h"];
  resetValidationHints("#completionDailyPage");

  required.forEach((name) => {
    if (!String(data[name] || "").trim()) pushIssue(issues, { level: "error", text: message("required", { field: labelFor(name) }), field: name });
  });

  validateReportDate(issues, data);
  validateOperationStartDate(issues, data);

  const operations = readTable("completionOperationsTable");
  const opStats = validateOperationsTable(
    issues,
    "completionOperationsTable",
    operations,
    timeTypeCodes(),
    "completionOperationType",
    requiresBoundaryHoursValidation("completion", data)
  );
  setText("#completionOperationHours", formatHours(opStats.total));
  setText("#completionNptHours", formatHours(opStats.npt));
  setText("#completionWellDate", formatWellDate(data));

  validateIntervalRows(issues, "perforationIntervalsTable", readTable("perforationIntervalsTable"));

  markIssues(completionForm, issues);
  renderCompletionIssues(issues);
  updateCompletionProgress(required, issues, data);
  return issues;
}

function validateWorkover() {
  const data = formData(workoverForm);
  const issues = [];
  const required = ["event", "reportDate", "reportNo", "wellbore", "rig", "currentOps", "summary24h", "forecast24h"];
  resetValidationHints("#workoverDailyPage");

  required.forEach((name) => {
    if (!String(data[name] || "").trim()) pushIssue(issues, { level: "error", text: message("required", { field: labelFor(name) }), field: name });
  });

  validateReportDate(issues, data);
  validateOperationStartDate(issues, data);

  const operations = readTable("workoverOperationsTable");
  const opStats = validateOperationsTable(
    issues,
    "workoverOperationsTable",
    operations,
    timeTypeCodes(),
    "workoverOperationType",
    requiresBoundaryHoursValidation("workover", data)
  );
  setText("#workoverOperationHours", formatHours(opStats.total));
  setText("#workoverNptHours", formatHours(opStats.npt));
  setText("#workoverWellDate", formatWellDate(data));

  validateIntervalRows(issues, "workoverIntervalsTable", readTable("workoverIntervalsTable"));

  markIssues(workoverForm, issues);
  renderWorkoverIssues(issues);
  updateWorkoverProgress(required, issues, data);
  return issues;
}

function validateMove() {
  const data = formData(moveForm);
  const issues = [];
  const required = ["event", "reportDate", "reportNo", "wellbore", "rig", "currentOps", "summary24h", "forecast24h"];
  resetValidationHints("#moveDailyPage");

  required.forEach((name) => {
    if (!String(data[name] || "").trim()) pushIssue(issues, { level: "error", text: message("required", { field: labelFor(name) }), field: name });
  });

  validateReportDate(issues, data);
  validateMdProgress(issues, data);

  const operations = readTable("moveOperationsTable");
  const opStats = validateOperationsTable(
    issues,
    "moveOperationsTable",
    operations,
    timeTypeCodes(),
    "moveOperationType",
    requiresBoundaryHoursValidation("move", data)
  );
  setText("#moveOperationHours", formatHours(opStats.total));
  setText("#moveNptHours", formatHours(opStats.npt));
  setText("#moveWellDate", formatWellDate(data));

  markIssues(moveForm, issues);
  renderMoveIssues(issues);
  updateMoveProgress(required, issues, data);
  return issues;
}

function setServerWarnings(reportType, payload = {}) {
  const text = String(payload?.metadata?.validation_warnings || "");
  serverWarnings[reportType] = text ? text.split(";").map((part) => part.trim()).filter(Boolean) : [];
}

function renderIssuePanel(reportType, countSelector, container, issues) {
  const saved = serverWarnings[reportType] || [];
  const count = saved.length + issues.length;
  setText(countSelector, count);
  if (!container) return;
  if (!count) {
    container.innerHTML = `<div class="issue ok">${ui("noIssues")}</div>`;
    return;
  }
  const savedHtml = saved.length
    ? `<div class="issue-group"><span class="issue-group-title">${ui("savedWarnings")}</span>${saved.map((text) => `<div class="issue warning">${escapeHtml(text)}</div>`).join("")}</div>`
    : "";
  const liveHtml = issues.map((issue) => `<div class="issue ${issue.level}">${issue.text}</div>`).join("");
  container.innerHTML = savedHtml + liveHtml;
}

function renderIssues(issues) {
  renderIssuePanel("drilling", "#issueCount", issuesEl, issues);
}

function renderCompletionIssues(issues) {
  renderIssuePanel("completion", "#completionIssueCount", completionIssuesEl, issues);
}

function renderWorkoverIssues(issues) {
  renderIssuePanel("workover", "#workoverIssueCount", workoverIssuesEl, issues);
}

function renderMoveIssues(issues) {
  renderIssuePanel("move", "#moveIssueCount", moveIssuesEl, issues);
}

function updateCompletion(required, issues) {
  setText("#completionRate", `${detailCompleteness(required, issues)}%`);
}

function updateCompletionProgress(required, issues) {
  setText("#completionCompletionRate", `${detailCompleteness(required, issues)}%`);
}

function updateWorkoverProgress(required, issues) {
  setText("#workoverCompletionRate", `${detailCompleteness(required, issues)}%`);
}

function updateMoveProgress(required, issues) {
  setText("#moveCompletionRate", `${detailCompleteness(required, issues)}%`);
}

function showToast(text) {
  toast.textContent = text;
  toast.classList.add("show");
  window.setTimeout(() => toast.classList.remove("show"), 2200);
}

function showImportError(error) {
  const detail = error?.message ? `：${error.message}` : "";
  showToast(`${ui("pdfImportFailed")}${detail}`);
}

document.querySelectorAll("[data-save-report]").forEach((button) => {
  button.addEventListener("click", () => {
    if (!frontCan("save")) return showToast("当前账号没有保存权限");
    saveCurrentReport(button.dataset.saveReport);
  });
});

document.querySelectorAll("[data-back-records]").forEach((button) => {
  button.addEventListener("click", () => {
    showReportRecords(button.dataset.backRecords);
  });
});

document.addEventListener("click", (event) => {
  const projectToggle = event.target.closest("[data-project-dropdown-toggle]");
  if (projectToggle) {
    const field = projectToggle.closest("[data-production-project-filter], [data-production-rig-filter]");
    const menu = field?.querySelector("[data-project-dropdown]");
    if (field && menu) {
      const willOpen = menu.hidden;
      closeProductionProjectDropdowns(field);
      menu.hidden = !willOpen;
      projectToggle.setAttribute("aria-expanded", String(willOpen));
      if (willOpen) {
        positionProductionProjectDropdown(field);
        field.querySelector("[data-project-search]")?.focus();
      }
    }
    return;
  }
  const productionReportFilterToggle = event.target.closest("[data-production-report-filter-toggle]");
  if (productionReportFilterToggle) {
    const field = productionReportFilterToggle.closest("[data-production-report-filter-field]");
    const menu = field?.querySelector("[data-production-report-filter-menu]");
    if (field && menu) {
      const willOpen = menu.hidden;
      closeProductionReportFilterDropdowns(field);
      menu.hidden = !willOpen;
      productionReportFilterToggle.setAttribute("aria-expanded", String(willOpen));
      if (willOpen) {
        positionProductionReportFilterDropdown(field);
        field.querySelector("[data-production-report-filter-search]")?.focus();
      }
    }
    return;
  }
  const nptReportFilterToggle = event.target.closest("[data-npt-report-filter-toggle]");
  if (nptReportFilterToggle) {
    const field = nptReportFilterToggle.closest("[data-npt-report-filter-field]");
    const menu = field?.querySelector("[data-npt-report-filter-menu]");
    if (field && menu) {
      const willOpen = menu.hidden;
      closeNptReportFilterDropdowns(field);
      menu.hidden = !willOpen;
      nptReportFilterToggle.setAttribute("aria-expanded", String(willOpen));
      if (willOpen) field.querySelector("[data-npt-report-filter-search]")?.focus();
    }
    return;
  }
  if (!event.target.closest("[data-production-project-filter], [data-production-rig-filter]")) closeProductionProjectDropdowns();
  if (!event.target.closest("[data-production-report-filter-field]")) closeProductionReportFilterDropdowns();
  if (!event.target.closest("[data-npt-report-filter-field]")) closeNptReportFilterDropdowns();

  const nptDescription = event.target.closest("[data-npt-description]");
  if (nptDescription) {
    showNptDescriptionPopover(nptDescription);
    return;
  }
  if (!event.target.closest(".npt-description-popover")) {
    document.querySelector(".npt-description-popover")?.remove();
  }
  const frontLogout = event.target.closest("[data-front-logout]");
  if (frontLogout) {
    logoutFront();
    return;
  }
  const productionReportTab = event.target.closest("[data-production-report-tab]");
  if (productionReportTab) {
    analyticsState.productionReport.activeTab = productionReportTab.dataset.productionReportTab === "project" ? "project" : "rig";
    analyticsState.productionReport.detailPage = 1;
    analyticsState.productionReport.sortField = "";
    analyticsState.productionReport.sortDir = "desc";
    analyticsState.productionReport.sideSearch = "";
    refreshProductionReportView();
    return;
  }
  const productionSideSelect = event.target.closest("[data-production-side-select]");
  if (productionSideSelect) {
    const state = analyticsState.productionReport;
    const isRigTab = state.activeTab === "rig";
    const values = (isRigTab ? state.availableRigs : state.availableProjects).map((item) => item.value);
    const selected = productionSideSelect.dataset.productionSideSelect === "all" ? new Set(values) : new Set();
    if (isRigTab) {
      state.selectedRigs = selected;
      state.rigTouched = true;
    } else {
      state.selectedProjects = selected;
      state.projectTouched = true;
    }
    state.detailPage = 1;
    refreshProductionReportView();
    return;
  }
  const productionFilterSelect = event.target.closest("[data-production-filter-select]");
  if (productionFilterSelect) {
    const state = analyticsState.productionReport;
    const type = productionFilterSelect.dataset.productionFilterSelect;
    const values = (type === "project" ? state.availableProjects : state.availableRigs).map((item) => item.value);
    const selected = productionFilterSelect.dataset.mode === "all" ? new Set(values) : new Set();
    setProductionReportFilterSelection(type, selected);
    syncProductionReportFilterField(productionFilterSelect.closest("[data-production-report-filter-field]"));
    renderProductionReportTable(productionReportVisibleRows(state.payload?.details || []));
    return;
  }
  const nptReportTab = event.target.closest("[data-npt-report-tab]");
  if (nptReportTab) {
    analyticsState.npt.activeTab = nptReportTab.dataset.nptReportTab === "project" ? "project" : "rig";
    analyticsState.npt.detailPage = 1;
    analyticsState.npt.sortField = "";
    analyticsState.npt.sortDir = "desc";
    analyticsState.npt.sideSearch = "";
    refreshNptReportView();
    return;
  }
  const nptSideSelect = event.target.closest("[data-npt-side-select]");
  if (nptSideSelect) {
    const state = analyticsState.npt;
    const isRigTab = state.activeTab === "rig";
    const values = (isRigTab ? state.availableRigs : state.availableProjects).map((item) => item.value);
    const selected = nptSideSelect.dataset.nptSideSelect === "all" ? new Set(values) : new Set();
    if (isRigTab) {
      state.selectedRigs = selected;
      state.rigTouched = true;
    } else {
      state.selectedProjects = selected;
      state.projectTouched = true;
    }
    state.detailPage = 1;
    refreshNptReportView();
    return;
  }
  const nptFilterSelect = event.target.closest("[data-npt-filter-select]");
  if (nptFilterSelect) {
    const state = analyticsState.npt;
    const type = nptFilterSelect.dataset.nptFilterSelect;
    const values = (type === "project" ? state.availableProjects : state.availableRigs).map((item) => item.value);
    const selected = nptFilterSelect.dataset.mode === "all" ? new Set(values) : new Set();
    setNptReportFilterSelection(type, selected);
    syncNptReportFilterField(nptFilterSelect.closest("[data-npt-report-filter-field]"));
    renderNptTable(nptReportVisibleRows(state.payload?.details || []));
    return;
  }
  const analyticsSearch = event.target.closest("[data-analytics-search]");
  if (analyticsSearch) {
    loadAnalytics(analyticsSearch.dataset.analyticsSearch, { force: true });
    return;
  }
  const analyticsReset = event.target.closest("[data-analytics-reset]");
  if (analyticsReset) {
    const kind = analyticsReset.dataset.analyticsReset;
    resetAnalyticsFilter(kind);
    loadAnalytics(kind);
    return;
  }
  const analyticsExport = event.target.closest("[data-analytics-export]");
  if (analyticsExport) {
    if (!frontCan("export")) return showToast("当前账号没有导出权限");
    exportAnalytics(analyticsExport.dataset.analyticsExport);
    return;
  }
  const analyticsSortButton = event.target.closest("[data-analytics-sort]");
  if (analyticsSortButton) {
    const kind = analyticsSortButton.dataset.analyticsKind;
    if (analyticsState[kind]) {
      analyticsState[kind].sortField = analyticsSortButton.dataset.analyticsSort || "";
      analyticsState[kind].sortDir = analyticsSortButton.dataset.sortDir === "desc" ? "desc" : "asc";
      analyticsState[kind].detailPage = 1;
      if (kind === "npt") renderNptTable(nptReportVisibleRows(analyticsState.npt.payload?.details || []));
      else if (kind === "productionReport") renderProductionReportTable(productionReportVisibleRows(analyticsState.productionReport.payload?.details || []));
      else renderProductionTable(analyticsState.production.payload?.details || []);
    }
    return;
  }
  const productionRemarkSave = event.target.closest("[data-production-remark-save]");
  if (productionRemarkSave) {
    saveProductionRemark(productionRemarkSave);
    return;
  }
  if (event.target.closest("[data-production-remark]")) {
    return;
  }
  const reportHomeShortcut = event.target.closest("[data-open-report-home]");
  if (reportHomeShortcut) {
    openReportHomeForWell(reportHomeShortcut.dataset.reportType, reportHomeShortcut.dataset.wellbore || "");
    return;
  }
  const openAnalyticsRecord = event.target.closest("[data-open-record]");
  if (openAnalyticsRecord) {
    const reportType = openAnalyticsRecord.dataset.reportType;
    const recordId = openAnalyticsRecord.dataset.openRecord;
    if (reportType && recordId) {
      setActiveMenu(`${reportType}-daily`);
      openRecordDetail(reportType, recordId);
    }
    return;
  }
  if (event.target.closest("[data-npt-confirm-search]")) {
    const filterHost = document.querySelector("#nptConfirmPage .npt-confirm-filter");
    nptConfirmState.filters.wellbore = filterHost?.querySelector('[name="nptWellbore"]')?.value.trim() || "";
    nptConfirmState.filters.rig = filterHost?.querySelector('[name="nptRig"]')?.value || "";
    nptConfirmState.filters.status = filterHost?.querySelector('[name="nptStatus"]')?.value || "";
    loadNptConfirmations();
    return;
  }
  if (event.target.closest("[data-npt-confirm-reset]")) {
    nptConfirmState.filters = { wellbore: "", rig: "", status: "", scope: "all" };
    document.querySelector("#nptConfirmPage .npt-confirm-filter")?.querySelectorAll("input, select").forEach((control) => {
      control.value = "";
    });
    loadNptConfirmations();
    return;
  }
  const nptConfirmShortcut = event.target.closest("[data-npt-confirm-shortcut]");
  if (nptConfirmShortcut) {
    setActiveMenu("rig-npt-ranking");
    openNptConfirmationDetail(nptConfirmShortcut.dataset.nptConfirmShortcut, nptConfirmShortcut.dataset.rig || "", false);
    return;
  }
  if (event.target.closest("[data-npt-show-all-wells]")) {
    document.querySelector(".npt-detail-panel")?.scrollIntoView({ behavior: "smooth", block: "start" });
    return;
  }
  const nptMenuTarget = event.target.closest(".npt-stats-dashboard [data-menu-target]");
  if (nptMenuTarget) {
    setActiveMenu(nptMenuTarget.dataset.menuTarget);
    return;
  }
  const nptOpen = event.target.closest("[data-npt-open], [data-npt-view]");
  if (nptOpen) {
    openNptConfirmationDetail(nptOpen.dataset.nptOpen || nptOpen.dataset.nptView, nptOpen.dataset.rig || "", false);
    return;
  }
  if (event.target.closest("[data-npt-back]")) {
    showNptConfirmList();
    return;
  }
  const nptClassify = event.target.closest("[data-npt-classify]");
  if (nptClassify) {
    collectNptConfirmationRows();
    const index = Number(nptClassify.dataset.nptClassify);
    if (nptConfirmState.expandedRows.has(index)) nptConfirmState.expandedRows.delete(index);
    else nptConfirmState.expandedRows.add(index);
    renderNptOperationRows(Boolean(nptConfirmState.detail?.meta?.locked));
    return;
  }
  if (event.target.closest("[data-npt-save]")) {
    if (!frontCan("save")) return showToast("当前账号没有保存权限");
    saveNptConfirmation(false);
    return;
  }
  if (event.target.closest("[data-npt-submit]")) {
    if (!frontCan("save")) return showToast("当前账号没有保存权限");
    saveNptConfirmation(true);
    return;
  }
  const monthNavButton = event.target.closest("[data-month-nav]");
  if (monthNavButton) {
    shiftMonth(monthNavButton.dataset.reportType, Number(monthNavButton.dataset.monthNav));
    return;
  }
  const pageButton = event.target.closest("[data-record-page]");
  if (pageButton) {
    const reportType = pageButton.dataset.reportType;
    if (recordState[reportType]) {
      recordState[reportType].page = Number(pageButton.dataset.recordPage) || 1;
      renderRecordDashboard(reportType);
    }
    return;
  }
  const analyticsPageButton = event.target.closest("[data-analytics-page]");
  if (analyticsPageButton) {
    const kind = analyticsPageButton.dataset.analyticsKind;
    if (analyticsState[kind]) {
      analyticsState[kind].detailPage = Number(analyticsPageButton.dataset.analyticsPage) || 1;
      renderAnalyticsPage(kind);
    }
    return;
  }
  const sourceButton = event.target.closest("[data-source-pdf]");
  if (sourceButton) {
    openSourcePdf(sourceButton.dataset.sourcePdf, sourceButton.dataset.sourceName || sourceButton.textContent.trim());
    return;
  }
  if (event.target.closest("[data-close-source-pdf]")) {
    closeSourcePdf();
    return;
  }
  const sortButton = event.target.closest("[data-well-sort]");
  if (sortButton) {
    const reportType = sortButton.dataset.reportType;
    if (recordState[reportType]) {
      recordState[reportType].sortBy = sortButton.dataset.wellSort || "last";
      recordState[reportType].page = 1;
      renderRecordDashboard(reportType);
    }
    return;
  }
  const wellButton = event.target.closest("[data-well]");
  if (wellButton) {
    const reportType = wellButton.dataset.reportType;
    recordState[reportType].selectedWell = wellButton.dataset.well;
    recordState[reportType].selectedDate = "";
    recordState[reportType].calendarMonth = "";
    recordState[reportType].page = 1;
    renderRecordDashboard(reportType);
    return;
  }
  const dateButton = event.target.closest("[data-calendar-date]");
  if (dateButton && dateButton.dataset.calendarDate) {
    const reportType = dateButton.dataset.reportType;
    const state = recordState[reportType];
    const record = sortedRecords(state.records).find((item) => {
      return item.reportDate === dateButton.dataset.calendarDate
        && (!state.selectedWell || item.wellbore === state.selectedWell)
        && item.status !== "failed";
    });
    if (record) {
      openRecordDetail(reportType, record.record_id);
      return;
    }
    state.selectedDate = dateButton.dataset.calendarDate;
    state.page = 1;
    renderRecordDashboard(reportType);
    return;
  }
  const uploadButton = event.target.closest("[data-record-upload]");
  if (uploadButton) {
    if (!frontCan("import")) return showToast("当前账号没有导入权限");
    const input = recordUploadInput(uploadButton.dataset.recordUpload);
    if (input) {
      input.value = "";
      input.click();
    }
    return;
  }
  const previewButton = event.target.closest("[data-record-preview]");
  if (previewButton) {
    openRecordDetail(previewButton.dataset.reportType, previewButton.dataset.recordPreview);
    return;
  }
  const deleteUploadJob = event.target.closest("[data-delete-upload-job]");
  if (deleteUploadJob) {
    deleteFailedUploadJob(deleteUploadJob.dataset.reportType, deleteUploadJob.dataset.deleteUploadJob);
    return;
  }
  const addWellButton = event.target.closest(".add-well-button");
  if (addWellButton) {
    const dashboard = addWellButton.closest("[data-record-dashboard]");
    const reportType = dashboard?.dataset.recordDashboard;
    if (reportType) openAddWellModal(reportType);
    return;
  }
  const saveWellProfile = event.target.closest("[data-save-well-profile]");
  if (saveWellProfile) {
    saveWellProfileFromModal(saveWellProfile.dataset.saveWellProfile);
    return;
  }
  const deleteWellProfile = event.target.closest("[data-delete-well-profile]");
  if (deleteWellProfile) {
    deleteWellProfileFromModal(deleteWellProfile.dataset.deleteWellProfile);
    return;
  }
  if (event.target.closest("[data-well-modal-close]")) {
    closeWellProfileModal();
    return;
  }
});

document.addEventListener("change", (event) => {
  if (event.target.matches("[data-record-page-size]")) return setRecordPageSize(event.target.dataset.recordPageSize, event.target.value);
  if (event.target.matches("[data-analytics-page-size]")) return setAnalyticsPageSize(event.target.dataset.analyticsPageSize, event.target.value);
  if (event.target.matches("[data-record-page-jump]")) return commitRecordPageJump(event.target);
  if (event.target.matches("[data-analytics-page-jump]")) return commitAnalyticsPageJump(event.target);
  const productionScopeType = event.target.closest("[data-production-scope-type]");
  if (productionScopeType) {
    const payload = analyticsState.production.payload || {};
    populateProductionSummaryScopeFilter(productionScopeType.closest('[data-analytics-filter="production"]'), payload.filters || {});
    return;
  }
  if (event.target.matches("[data-production-side-option]")) {
    const state = analyticsState.productionReport;
    const isRigTab = state.activeTab === "rig";
    const selected = new Set(isRigTab ? state.selectedRigs : state.selectedProjects);
    if (event.target.checked) selected.add(event.target.value);
    else selected.delete(event.target.value);
    if (isRigTab) {
      state.selectedRigs = selected;
      state.rigTouched = true;
    } else {
      state.selectedProjects = selected;
      state.projectTouched = true;
    }
    state.detailPage = 1;
    refreshProductionReportView();
    return;
  }
  if (event.target.matches("[data-production-filter-option]")) {
    const state = analyticsState.productionReport;
    const type = event.target.dataset.productionFilterOption;
    const selected = new Set(type === "project" ? state.selectedProjects : state.selectedRigs);
    if (event.target.checked) selected.add(event.target.value);
    else selected.delete(event.target.value);
    setProductionReportFilterSelection(type, selected);
    syncProductionReportFilterField(event.target.closest("[data-production-report-filter-field]"));
    renderProductionReportTable(productionReportVisibleRows(state.payload?.details || []));
    return;
  }
  if (event.target.matches("[data-npt-side-option]")) {
    const state = analyticsState.npt;
    const isRigTab = state.activeTab === "rig";
    const selected = new Set(isRigTab ? state.selectedRigs : state.selectedProjects);
    if (event.target.checked) selected.add(event.target.value);
    else selected.delete(event.target.value);
    if (isRigTab) {
      state.selectedRigs = selected;
      state.rigTouched = true;
    } else {
      state.selectedProjects = selected;
      state.projectTouched = true;
    }
    state.detailPage = 1;
    refreshNptReportView();
    return;
  }
  if (event.target.matches("[data-npt-filter-option]")) {
    const state = analyticsState.npt;
    const type = event.target.dataset.nptFilterOption;
    const selected = new Set(type === "project" ? state.selectedProjects : state.selectedRigs);
    if (event.target.checked) selected.add(event.target.value);
    else selected.delete(event.target.value);
    setNptReportFilterSelection(type, selected);
    syncNptReportFilterField(event.target.closest("[data-npt-report-filter-field]"));
    renderNptTable(nptReportVisibleRows(state.payload?.details || []));
    return;
  }
  if (!event.target.matches('[data-project-option] input[type="checkbox"]')) return;
  const field = event.target.closest("[data-production-project-filter], [data-production-rig-filter]");
  if (!field) return;
  field.dataset.projectTouched = "1";
  const selected = selectedProductionProjectValues(field);
  if (event.target.checked) selected.add(event.target.value);
  else selected.delete(event.target.value);
  setProductionProjectSelection(field, selected);
});

document.addEventListener("input", (event) => {
  const productionSideSearch = event.target.closest("[data-production-side-search]");
  if (productionSideSearch) {
    analyticsState.productionReport.sideSearch = productionSideSearch.value;
    renderProductionReportSide();
    return;
  }
  const productionReportFilterSearch = event.target.closest("[data-production-report-filter-search]");
  if (productionReportFilterSearch) {
    filterProductionReportDropdownOptions(productionReportFilterSearch.closest("[data-production-report-filter-field]"));
    return;
  }
  const productionWellQuery = event.target.closest("[data-production-well-query]");
  if (productionWellQuery) {
    analyticsState.productionReport.wellQuery = productionWellQuery.value;
    analyticsState.productionReport.detailPage = 1;
    renderProductionReportTable(productionReportVisibleRows(analyticsState.productionReport.payload?.details || []));
    return;
  }
  const nptSideSearch = event.target.closest("[data-npt-side-search]");
  if (nptSideSearch) {
    analyticsState.npt.sideSearch = nptSideSearch.value;
    renderNptReportSide();
    return;
  }
  const nptReportFilterSearch = event.target.closest("[data-npt-report-filter-search]");
  if (nptReportFilterSearch) {
    filterNptReportDropdownOptions(nptReportFilterSearch.closest("[data-npt-report-filter-field]"));
    return;
  }
  const nptKeywordQuery = event.target.closest("[data-npt-keyword-query]");
  if (nptKeywordQuery) {
    analyticsState.npt.keywordQuery = nptKeywordQuery.value;
    analyticsState.npt.detailPage = 1;
    renderNptTable(nptReportVisibleRows(analyticsState.npt.payload?.details || []));
    return;
  }
  const projectSearch = event.target.closest("[data-project-search]");
  if (projectSearch) {
    filterProductionProjectOptions(projectSearch.closest("[data-production-project-filter], [data-production-rig-filter]"));
    return;
  }
  if (event.target.matches("[data-npt-only-sc-npt]")) {
    collectNptConfirmationRows();
    renderNptOperationRows(Boolean(nptConfirmState.detail?.meta?.locked));
    return;
  }
  if (event.target.matches('[name="nptConfirmNote"]')) {
    updateNptNoteCount();
    return;
  }
  const search = event.target.closest("[data-well-search]");
  if (!search) return;
  const reportType = search.dataset.wellSearch;
  const term = search.value.trim().toLowerCase();
  recordState[reportType].search = search.value.trim();
  recordState[reportType].page = 1;
  search.closest(".well-panel")?.querySelectorAll("[data-well]").forEach((button) => {
    button.hidden = term && !button.dataset.well.toLowerCase().includes(term);
  });
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && event.target.matches("[data-record-page-jump]")) {
    event.preventDefault();
    return commitRecordPageJump(event.target);
  }
  if (event.key === "Enter" && event.target.matches("[data-analytics-page-jump]")) {
    event.preventDefault();
    return commitAnalyticsPageJump(event.target);
  }
  if (event.key === "Escape") {
    document.querySelector(".npt-description-popover")?.remove();
  }
  if (event.key === "Escape" && !document.querySelector("#sourcePdfModal")?.hidden) {
    closeSourcePdf();
  }
  if (event.key === "Escape" && document.querySelector(".well-profile-modal")) {
    closeWellProfileModal();
  }
});

window.addEventListener("scroll", (event) => {
  const popover = document.querySelector(".npt-description-popover");
  if (!event.target?.closest?.(".npt-description-popover")) popover?.remove();
  positionOpenProductionProjectDropdowns();
  positionOpenProductionReportDropdowns();
}, true);
window.addEventListener("resize", () => {
  positionOpenProductionProjectDropdowns();
  positionOpenProductionReportDropdowns();
});

document.querySelectorAll(".menu-group-toggle").forEach((button) => {
  button.addEventListener("click", () => {
    const group = button.closest(".menu-group");
    const expanded = !group.classList.contains("open");
    group.classList.toggle("open", expanded);
    button.setAttribute("aria-expanded", String(expanded));
  });
});

document.querySelectorAll(".language-switch [data-lang]").forEach((button) => {
  button.addEventListener("click", () => handleLanguageChoice(button.dataset.lang, button));
});

document.querySelectorAll(".menu-link[data-menu-target]").forEach((link) => {
  link.addEventListener("click", (event) => {
    event.preventDefault();
    link.closest(".menu-group")?.classList.add("open");
    link.closest(".menu-group")?.querySelector(".menu-group-toggle")?.setAttribute("aria-expanded", "true");
    setActiveMenu(link.dataset.menuTarget);
  });
});

document.querySelector("#importPdf").addEventListener("click", () => {
  if (!frontCan("import")) return showToast("当前账号没有导入权限");
  const input = document.querySelector("#pdfInput");
  input.value = "";
  input.click();
});
document.querySelector("#pdfInput").addEventListener("change", (event) => {
  importReportFiles("drilling", event.target.files);
});
document.querySelector("#importCompletionPdf").addEventListener("click", () => {
  if (!frontCan("import")) return showToast("当前账号没有导入权限");
  const input = document.querySelector("#completionPdfInput");
  input.value = "";
  input.click();
});
document.querySelector("#completionPdfInput").addEventListener("change", (event) => {
  importReportFiles("completion", event.target.files);
});
document.querySelector("#importWorkoverPdf").addEventListener("click", () => {
  if (!frontCan("import")) return showToast("当前账号没有导入权限");
  const input = document.querySelector("#workoverPdfInput");
  input.value = "";
  input.click();
});
document.querySelector("#workoverPdfInput").addEventListener("change", (event) => {
  importReportFiles("workover", event.target.files);
});
document.querySelector("#importMovePdf").addEventListener("click", () => {
  if (!frontCan("import")) return showToast("当前账号没有导入权限");
  const input = document.querySelector("#movePdfInput");
  input.value = "";
  input.click();
});
document.querySelector("#movePdfInput").addEventListener("change", (event) => {
  importReportFiles("move", event.target.files);
});
form.addEventListener("input", () => { markReportOriginalEdited("drilling"); validate(); updateSaveButton("drilling"); });
form.addEventListener("change", () => { markReportOriginalEdited("drilling"); validate(); updateSaveButton("drilling"); });
completionForm.addEventListener("input", () => { markReportOriginalEdited("completion"); validateCompletion(); updateSaveButton("completion"); });
completionForm.addEventListener("change", () => { markReportOriginalEdited("completion"); validateCompletion(); updateSaveButton("completion"); });
workoverForm.addEventListener("input", () => { markReportOriginalEdited("workover"); validateWorkover(); updateSaveButton("workover"); });
workoverForm.addEventListener("change", () => { markReportOriginalEdited("workover"); validateWorkover(); updateSaveButton("workover"); });
moveForm.addEventListener("input", () => { markReportOriginalEdited("move"); validateMove(); updateSaveButton("move"); });
moveForm.addEventListener("change", () => { markReportOriginalEdited("move"); validateMove(); updateSaveButton("move"); });

loadRows();
loadRows({}, completionTableIds);
loadRows({}, workoverTableIds);
loadRows({}, moveTableIds);
applyLanguage(currentLanguage);
setDrillingSourceFile();
setActiveMenu(initialReportRoute.target || "drilling-daily");
Object.keys(savedReportSignatures).forEach((reportType) => {
  savedReportSignatures[reportType] = reportSignature(reportType);
});
updateAllSaveButtons();
loadFrontSession();
