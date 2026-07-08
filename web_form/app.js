const i18n = {
  zh: {
    ui: {
      appTitleShort: "厄瓜油田", appSubtitle: "Report Platform", pageTitle: "钻井日报填报工作台", drillingPageKicker: "DRILLING DAILY REPORT", completionPageTitle: "完井日报填报工作台", completionPageKicker: "COMPLETION DAILY REPORT", workoverPageTitle: "修井日报填报工作台", workoverPageKicker: "WORKOVER DAILY REPORT", movePageTitle: "搬迁日报填报工作台", movePageKicker: "RIG MOVE DAILY REPORT",
      systemAdmin: "系统后台",
      menuDailyParsing: "日报解析", menuDrillingDaily: "钻井日报", menuCompletionDaily: "完井日报", menuWorkoverDaily: "修井日报", menuMoveDaily: "搬迁日报",
      menuProductionReport: "生产报表", menuRigProductionSummary: "生产时效", menuProductionDetailReport: "生产报表", menuWellNptConfirm: "NPT统计", menuRigNptRanking: "NPT确认",
      menuHsse: "HSSE管理", menuHsseCollection: "信息填报", menuHsseDashboard: "安全驾驶舱", menuDailySafetySummary: "安全报表", menuPeriodSafetyReport: "安全报表",
      descDrillingDaily: "支持上传钻井或搬迁 PDF 日报，解析井基础信息及 Operation 内容，并进入钻井日报填报页面。",
      descCompletionDaily: "上传完井日报 PDF，解析基础信息、Operation、库存和射孔区间，预览后可二次编辑。", descWorkoverDaily: "上传修井日报 PDF，解析 WO 信息、Operation、库存、安全备注和射孔区间，预览后可二次编辑。", descMoveDaily: "上传搬迁日报 PDF，解析 Operation、重型设备和载荷清单，预览后可二次编辑。",
      descRigProductionSummary: "基于日报解析数据，按井队、日报类型和月份展示生产作业时效。", descProductionDetailReport: "按项目周期、井队和井号归属查询生产时效明细。", descWellNptConfirm: "统计各钻井队历史作业 NPT 时长、占比及排名，支持井队对比分析。", descRigNptRanking: "确认每口井 P、SC、NPT 时长及具体情况，并支持后续按时效确认表修正。",
      descHsseCollection: "按井、按队伍记录每日安全生产信息，包括人的不安全行为、物的不安全状态、不放心人员、生产异常和公共安全事件。", descHsseDashboard: "集中展示全油田各队伍 HSSE 关键指标、异常情况和跟踪总览。", descDailySafetySummary: "基于 HSSE 采集数据生成安全报表。", descPeriodSafetyReport: "合并日报统计与周月报，基于 HSSE 数据生成安全报表，支持阶段性分析和汇报。",
      moduleStatusPlanned: "功能规划", moduleComingSoon: "功能待开发", moduleCurrent: "当前菜单", moduleComingSoonDesc: "该功能已按需求菜单预留入口，后续可在此接入数据采集、统计报表或数据分析页面。",
      navBasic: "基础信息", navSummary: "作业摘要", navWellControl: "井控与液压", navSurvey: "测斜数据", navMud: "泥浆数据", navBitBha: "钻头与 BHA", navOperations: "作业明细", navCosts: "成本与库存", navIncidents: "事故与备注",
      importPdf: "导入 PDF 日报", originalReport: "原文", translateChinese: "翻译为中文", translationRunning: "正在切换日报语言...", translationReady: "译文预览已生成。", translationFailed: "翻译失败，请确认本地翻译服务已启动。", translationPreviewNotice: "译文仅供查看，切回原文后编辑保存。", translationTitle: "中英西混合日报翻译", translationOriginal: "原文", translationLanguage: "语言", translationChinese: "中文翻译", translationPath: "字段", translationTerms: "术语替换", translationWarnings: "告警", translationEmpty: "暂无可显示翻译结果", saveDatabase: "保存", downloadDatabase: "下载Excel库", backRecords: "返回记录", databaseSaved: "已保存到Excel数据库。", databaseSaveFailed: "保存Excel数据库失败。", recordLoadFailed: "打开日报详情失败。", databaseRecord: "数据库记录", sourceFileEmpty: "未上传文件",
      uploadDashboardTitle: "日报管理 Dashboard", wellSelection: "井选择", searchWell: "搜索井号", reportCalendar: "日报日历", uploadRecords: "上传文件记录", allTypes: "全部类型", allStatuses: "全部状态", exportList: "导出", preview: "查看", download: "下载", detail: "详情", uploaded: "已完成", queued: "排队中", parsing: "解析中", failed: "失败", warningStatus: "有告警", pending: "待补传", noRecords: "暂无上传记录", addWell: "添加新井", selectedWell: "当前井", monthlyUploaded: "本月已上传", monthlyPending: "待补传", reportKinds: "日报类型", monthlyUploaders: "本月上传人", calendarHint: "提示：点击已有完成记录的日期可直接预览", recordsCount: "条记录", uploader: "上传人", uploadTime: "上传时间", fileName: "文件名称", status: "状态", operation: "操作", date: "日期", well: "井号", reportType: "日报类型", page: "页", prevPage: "上一页", nextPage: "下一页", sourcePdfMissing: "源文件未保存，请重新导入该日报后查看。", sourcePdfTitle: "源文件PDF", sortFirstUpload: "初传", sortLastUpload: "最近", sortWellName: "井号",
      metricCompletion: "完成度", metricIssues: "校验问题", metricHours: "作业合计", metricProgress: "进尺", metricIntervals: "射孔区间", metricWellDate: "井号 / 日期", metricDailyHours: "当日作业时长", metricNptHours: "NPT时长", metricDataCompleteness: "数据完整性",
      metricWorkDays: "作业天数", metricNptShare: "NPT时长 / 占比", metricPScShare: "P / SC工况占比", metricReportCompleteness: "日报完整性", metricMoveDrillingDays: "搬迁 / 钻井",
      analyticsKicker: "数据看板", analyticsProductionScope: "基于已保存到 Excel 库的日报解析数据", analyticsNptScope: "基于已保存到 Excel 库的日报解析数据；分类按日报作业代码 / 作业子项汇总", search: "查询", reset: "重置", wellborePlaceholder: "请输入井号",
      chartRigHours: "各井队累计NPT排名", chartOperationMix: "作业时效构成", chartMonthlyHours: "单井作业甘特图", chartNptRig: "各井队NPT对比 (h)", chartNptReason: "作业代码 / 作业子项分布", chartNptWell: "各井NPT排行", chartNptMonthly: "月度NPT趋势 (h)", productionDetailTitle: "生产报表明细", nptDetailTitle: "NPT统计明细", analyticsRowHint: "点击行可打开日报详情", productionReportRowHint: "点击井号新开日报首页并选中该井", nptRowHint: "按日报作业代码 / 作业子项原文汇总，点击行可追溯日报",
      kpiRigCount: "井队数", kpiNptRigCount: "NPT井队数", kpiWellCount: "涉及井数", kpiTotalHours: "总作业时长", kpiTotalNpt: "总NPT", kpiReportCompleteness: "日报完整性", kpiNptEvents: "NPT事件数", analyticsDefaultCaption: "基于已入库日报", analyticsNptCaption: "按作业代码 / 作业子项汇总", analyticsCompletenessCaption: "缺失 {missing} 天 / 告警 {warning} 天", noAnalyticsData: "暂无可统计数据", noExportData: "暂无可导出数据", normalStatus: "正常", reasonMissing: "未填写作业代码 / 作业子项",
      allRigs: "全部井队", allProjects: "全部项目", allReportTypes: "全部类型", allReasons: "全部分类", opCodeSub: "作业代码 / 子项", opCode: "作业代码", opSub: "作业子项", category: "分类", tableProject: "项目", tableContractProject: "合同(项目)", tableRig: "井队", tableWell: "井号", tableReportType: "日报类型", tableStartDate: "开工时间", tableEndDate: "完工时间", tableMoveDate: "搬迁日期", tableDrillingStartDate: "开钻日期", tableDrillingFinishDate: "完钻日期", tableCompletionDate: "完井日期", tableWorkoverDate: "修井日期", tableDrillingHours: "钻井(h)", tableCompletionHours: "完井(h)", tableWorkoverHours: "修井(h)", tableMoveHours: "搬迁(h)", tableNptHours: "NPT(h)", tableRemarks: "备注", tableDate: "日期", tableOperationDetails: "作业详情",
      sectionBasic: "基础信息", sectionSummary: "作业摘要", sectionWellControl: "井控与液压", sectionSurvey: "Survey Data (Last 6)", sectionMud: "泥浆数据", sectionBitBha: "钻头与 BHA", sectionOperations: "Operations", sectionCosts: "成本与库存", sectionIncidents: "事故与备注", sectionPersonnel: "人员信息", sectionPerforationIntervals: "射孔区间",
      noteBasic: "对应 PDF 顶部日报抬头和井基本信息", noteSummary: "当前作业、24 小时总结、下一步计划", noteWellControl: "套管、BOP、泵压、扭矩和钩载", noteIncidents: "HSE 状态、同步作业和其他说明",
      completionNoteBasic: "对应完井 PDF 顶部日报抬头、AFP 和井基本信息", completionNotePersonnel: "Supervisor、Engineer、Geologist 与现场总人数", completionNoteRemarks: "安全备注、固控说明和其他现场备注", workoverNoteBasic: "对应修井 PDF 顶部日报抬头、AFP 和井基本信息", workoverNotePersonnel: "Supervisor、Engineer、Geologist 与现场总人数", workoverNoteRemarks: "安全备注、固控说明和其他现场备注", moveNoteBasic: "对应搬迁 PDF 顶部日报抬头、AFE 和井队信息", moveNoteRemarks: "其他现场备注原文",
      addSurvey: "新增测斜", addBha: "新增 BHA", addOperation: "新增作业行", addCost: "新增成本", addBulk: "新增库存", addInterval: "新增区间", rulesTitle: "基础条件限制规则", liveValidation: "实时校验",
      uploadedDays: "已上传", daysUnit: "天", missingDate: "缺失日期",
      prevMonth: "上一月", nextMonth: "下一月", savedWarnings: "保存时校验",
      noIssues: "当前没有校验问题。", pdfImporting: "正在解析 PDF 日报...", pdfImported: "PDF 日报已解析并填充到界面。", pdfImportFailed: "PDF 解析失败，请检查文件格式或模板。",
      thMd: "MD (ft)", thIncl: "Incl (deg)", thAzi: "Azi (deg)", thTvd: "TVD (ft)", thVse: "VSE (ft)", thNs: "N/-S (ft)", thDls: "DLS (deg/100ft)", thBuild: "Build (deg/100ft)", thComponent: "Component", thOd: "OD (in)", thId: "ID (in)", thJts: "Jts", thLength: "Length (ft)", thFrom: "From (HH:MM)", thTo: "To (HH:MM)", thHrs: "Hrs (h)", thOpCode: "Op Code", thOpSub: "Op Sub", thType: "Type", thOperationDetails: "Operation Details", thCostDescription: "Cost Description", thVendor: "Vendor", thAmount: "Amount (USD)", thBulk: "Bulk", thQtyStart: "Qty Start", thQtyUsed: "Qty Used", thQtyEnd: "Qty End", thFormation: "Formation", thTopMd: "Top MD (ft)", thBaseMd: "Base MD (ft)", thDensity: "Density (spf)", thCharges: "Charges", thPhase: "Phase (deg)", thPenetration: "Penetration (in)", thDiameter: "Diameter (in)", thDate: "Date", thStatus: "Status", thComments: "Comments", thLocation: "Location", thEquipment: "Equipment", thPlate: "Plate", thEntryDate: "Entry Date", thEntryTime: "Entry Time", thGuide: "Guide", thCargo: "Cargo", thTrip: "Trip"
    },
    fields: {
      event: "事件", reportDate: "日期", project: "项目", date_from: "日期起", date_to: "日期止", scope_type: "筛选方式", scope_value: "范围", report_type: "日报类型", reason: "作业代码 / 子项", nptWellbore: "井号", nptRig: "井队", nptStatus: "确认状态", reportNo: "报告编号", wellbore: "井号", rig: "井队", primaryReason: "主要原因", afeNumber: "AFE 编号", refDatum: "参考基准", todayMd: "当日 MD (ft)", prevMd: "前日 MD (ft)", progress: "进尺 (ft)", rotHrsToday: "当日旋转时长",
      currentOps: "Current Ops", summary24h: "24-Hr Summary", forecast24h: "24-Hr Forecast", lastCasing: "Last Casing", lastCasingSize: "Last Casing Size", lastCasingDepth: "Last Casing Depth", nextCasing: "Next Casing", nextCasingSize: "Next Casing Size", nextCasingDepth: "Next Casing Depth", formTestEmw: "Form Test/EMW", lastBopPressTest: "Last BOP Press Test", pumpRate: "Pump Rate (gpm)", pumpPress: "Pump Press (psi)", stringWeightUpDown: "String Wt Up/Dn", torqueOnBottom: "Torque On Btm",
      mudEngineer: "Mud Engineer", sampleFrom: "Sample From", mudType: "Mud Type", mudTimeMd: "Time / MD", mudTime: "Mud Time", mudMd: "Mud MD", mudDensity: "Density (ppg)", mudTemperature: "Mud Temp", rheologyTemp: "Rheology Temp", viscosity: "Viscosity", pvYp: "PV / YP", pv: "PV", yp: "YP", gels: "Gels 10s/10m/30m", gel10s: "Gel 10s", gel10m: "Gel 10m", gel30m: "Gel 30m", apiWl: "API WL", oilWater: "Oil / Water", oilPercent: "Oil (%)", waterPercent: "Water (%)", sand: "Sand (%)", ecd: "ECD", mudComments: "Mud Comments",
      bitNo: "Bit No", bitSize: "Bit Size", bitManufacturer: "Manufacturer", bitSerial: "Serial No", bhaNo: "BHA No", bhaMdIn: "MD In", bhaMdOut: "MD Out", bhaTotalLength: "Total Length (ft)", safetyIncident: "Safety Incident?", environmentIncident: "Environ Incident?", daysSinceRi: "Days since Last RI", daysSinceLta: "Days since Last LTA", incidentComments: "Incident Comments", otherRemarks: "Other Remarks",
      description: "Description", operationStartDate: "Operation Start", workoverNo: "WO No", afeCost: "AFP Cost", dailyCost: "Daily Cost", cumulativeCost: "Cumulative Cost", supervisor1: "Supervisor 1", supervisor2: "Supervisor 2", engineer: "Engineer", pamEngineer: "PAM Engineer", geologist: "Geologist", totalPersonnel: "Total Personnel", safetyComments: "Safety Comments", groundElev: "Ground Elev", afeMdDays: "AFE MD/Days", environmentIncident: "Environmental Incident", daysSinceRi: "Days since RI", daysSinceLta: "Days since LTA"
    },
    rules: [
      "<strong>必填：</strong>Date、Report No、Wellbore、Rig、Current Ops、24-Hr Summary、Mud Type、Today's MD。",
      "<strong>日期：</strong>日报日期不能晚于当前日期。",
      "<strong>井深：</strong>Today's MD 必须大于等于 Prev MD，Progress 应等于两者差值，允许 0.5 ft 误差。",
      "<strong>工时：</strong>Operations 明细 Hrs 合计必须为 24.00 小时，允许 0.05 小时误差。",
      "<strong>作业行：</strong>From、To、Hrs、Op Code、Type、Operation Details 至少应完整填写；Type 只能是 P 或 NPT。",
      "<strong>测斜：</strong>Survey MD 不能大于 Today's MD，Incl 范围 0 到 180，DLS 不能为负。",
      "<strong>泥浆：</strong>Density 推荐 6 到 20 ppg，Sand 推荐不超过 10%。",
      "<strong>设备：</strong>BHA 组件 OD、ID、Jts、Length 不能为负，OD 应大于等于 ID。",
      "<strong>HSE：</strong>Safety 或 Environmental Incident 为 Y 时，Incident Comments 必填。",
      "<strong>成本与库存：</strong>仅结构化回显导入内容，不参与单元格校验。"
    ],
    completionRules: [
      "<strong>必填：</strong>Date、Report No、Wellbore、Rig、Current Ops、24-Hr Summary、24-Hr Forecast。",
      "<strong>日期：</strong>日报日期不能晚于当前日期，Operation Start 不能晚于日报日期。",
      "<strong>工时：</strong>Operations 明细 Hrs 合计必须为 24.00 小时，允许 0.05 小时误差。",
      "<strong>作业行：</strong>From、To、Hrs、Op Code、Type、Operation Details 建议完整填写；Type 只能是 P、SC 或 NPT。",
      "<strong>射孔区间：</strong>Base MD 应大于等于 Top MD，Length 不能为负。",
      "<strong>库存和成本：</strong>仅结构化回显导入内容，不参与单元格校验。"
    ],
    workoverRules: [
      "<strong>必填：</strong>Date、Report No、Wellbore、Rig、Current Ops、24-Hr Summary、24-Hr Forecast。",
      "<strong>日期：</strong>日报日期不能晚于当前日期，Operation Start 不能晚于日报日期。",
      "<strong>工时：</strong>Operations 明细 Hrs 合计必须为 24.00 小时，允许 0.05 小时误差。",
      "<strong>作业行：</strong>From、To、Hrs、Op Code、Type、Operation Details 建议完整填写；Type 只能是 P、SC 或 NPT。",
      "<strong>射孔区间：</strong>Base MD 应大于等于 Top MD，Length 不能为负。",
      "<strong>库存和成本：</strong>仅结构化回显导入内容，不参与单元格校验。"
    ],
    moveRules: [
      "<strong>必填：</strong>Date、Report No、Wellbore、Rig、Current Ops、24-Hr Summary、24-Hr Forecast。",
      "<strong>工时：</strong>Operations 明细 Hrs 合计必须为 24.00 小时，允许 0.05 小时误差。",
      "<strong>作业行：</strong>From、To、Hrs、Op Code、Type、Operation Details 建议完整填写；Type 只能是 P、SC 或 NPT。",
      "<strong>备注：</strong>Other Remarks 可保留 PDF 末页原文，便于人工复核。"
    ],
    msg: {
      required: "{field} 为必填项。", futureDate: "日报日期不能晚于当前日期。", operationStartDate: "Operation Start 不能晚于日报日期。", mdOrder: "Today's MD 必须大于等于 Prev MD。", progressMismatch: "Progress 与井深差值不一致，当前差值为 {value} ft。", operationMissingTable: "作业明细不能为空。", operationHours: "Operations 工时合计应为 24.00 h，当前为 {value} h。", operationMissing: "作业明细第 {row} 行缺少 {field}。", operationTimeMismatch: "作业明细第 {row} 行 From/To 对应时长为 {value} h，与 Hrs 不一致。", operationType: "作业明细第 {row} 行 Type 为空或不是 P/NPT，请复核。", completionOperationType: "完井作业第 {row} 行 Type 为空或不是 P/SC/NPT，请复核。", workoverOperationType: "修井作业第 {row} 行 Type 为空或不是 P/SC/NPT，请复核。", moveOperationType: "搬迁作业第 {row} 行 Type 为空或不是 P/SC/NPT，请复核。", operationHourRange: "作业明细第 {row} 行 Hrs 必须在 0 到 24 之间。", intervalDepth: "射孔区间第 {row} 行 Base MD 应大于等于 Top MD。", intervalLength: "射孔区间第 {row} 行 Length 不能为负。", surveyMd: "测斜第 {row} 行 MD 不能大于 Today's MD。", surveyIncl: "测斜第 {row} 行 Incl 应在 0 到 180 之间。", surveyDls: "测斜第 {row} 行 DLS 不能为负。", mudDensity: "泥浆 Density 推荐范围为 6 到 20 ppg。", sand: "泥浆 Sand 超过 10%，请复核。", bhaOdId: "BHA 第 {row} 行 OD 应大于等于 ID。", bhaNegative: "BHA 第 {row} 行存在负数。", negativeValue: "第 {row} 行 {field} 不能为负。", incidentRequired: "发生 Safety 或 Environmental Incident 时，Incident Comments 必填。"
    }
  },
  en: {
    ui: {
      appTitleShort: "Ecuador Field", appSubtitle: "Report Platform", pageTitle: "Drilling Daily Report Workspace", drillingPageKicker: "DRILLING DAILY REPORT", completionPageTitle: "Completion Daily Report Workspace", completionPageKicker: "COMPLETION DAILY REPORT", workoverPageTitle: "Workover Daily Report Workspace", workoverPageKicker: "WORKOVER DAILY REPORT",
      systemAdmin: "System Admin",
      menuDailyParsing: "Daily Parsing", menuDrillingDaily: "Drilling Daily", menuCompletionDaily: "Completion Daily", menuWorkoverDaily: "Workover Daily", menuMoveDaily: "Move Daily",
      menuProductionReport: "Production Reports", menuRigProductionSummary: "Production Time", menuProductionDetailReport: "Production Report", menuWellNptConfirm: "NPT Stats", menuRigNptRanking: "NPT Confirmation",
      menuHsse: "HSSE Management", menuHsseCollection: "Information Entry", menuHsseDashboard: "Safety Cockpit", menuDailySafetySummary: "Safety Report", menuPeriodSafetyReport: "Safety Report",
      descDrillingDaily: "Upload drilling or rig move PDF daily reports, parse well basics and Operation content, then edit the drilling daily report.",
      descCompletionDaily: "Upload completion daily PDFs, parse basics, operations, bulks, and perforated intervals, then preview and edit.", descWorkoverDaily: "Upload workover daily PDFs, parse WO information, operations, bulks, safety comments, and perforated intervals, then preview and edit.", descMoveDaily: "Reserved entry for rig move daily PDF parsing and structured entry.",
      descRigProductionSummary: "Show production time by rig, report type, and month from parsed daily reports.", descProductionDetailReport: "Query production time details by project period, rig, and well assignment.", descWellNptConfirm: "Rank drilling rigs by historical NPT duration and share for comparison analysis.", descRigNptRanking: "Confirm P, SC, and NPT hours by well, with later updates from time-class confirmation sheets.",
      descHsseCollection: "Capture daily HSSE information by well and team, including unsafe acts, unsafe conditions, personnel concerns, production exceptions, and public security events.", descHsseDashboard: "Show field-wide HSSE KPIs, exceptions, tracking, and overview by team.", descDailySafetySummary: "Generate safety reports from HSSE collection data.", descPeriodSafetyReport: "Combine daily safety stats with weekly and monthly reporting into one safety report entry.",
      moduleStatusPlanned: "Planned Feature", moduleComingSoon: "Feature Reserved", moduleCurrent: "Current Menu", moduleComingSoonDesc: "This menu entry is reserved from the requirement list. Data entry, reporting, or analytics pages can be connected here later.",
      navBasic: "Basic Info", navSummary: "Operations Summary", navWellControl: "Well Control & Hydraulics", navSurvey: "Survey Data", navMud: "Mud Data", navBitBha: "Bit & BHA", navOperations: "Operations Log", navCosts: "Costs & Bulks", navIncidents: "Incidents & Remarks",
      importPdf: "Import PDF Report", originalReport: "Original", translateChinese: "Translate to Chinese", translationRunning: "Switching report language...", translationReady: "Translation preview is ready.", translationFailed: "Translation failed. Check that the local translation service is running.", translationPreviewNotice: "Translation is view-only. Switch back to Original before editing or saving.", translationTitle: "Mixed EN/ES Drilling Report Translation", translationOriginal: "Original", translationLanguage: "Language", translationChinese: "Chinese", translationPath: "Field", translationTerms: "Terms", translationWarnings: "Warnings", translationEmpty: "No translation results to show", saveDatabase: "Save", downloadDatabase: "Download Excel DB", backRecords: "Back to Records", databaseSaved: "Saved to the Excel database.", databaseSaveFailed: "Failed to save the Excel database.", recordLoadFailed: "Failed to open report detail.", databaseRecord: "Database record", sourceFileEmpty: "No file uploaded",
      uploadDashboardTitle: "Daily Report Dashboard", wellSelection: "Well Selection", searchWell: "Search well", reportCalendar: "Report Calendar", uploadRecords: "Upload Records", allTypes: "All Types", allStatuses: "All Statuses", exportList: "Export", preview: "View", download: "Download", detail: "Details", uploaded: "Complete", queued: "Queued", parsing: "Parsing", failed: "Failed", warningStatus: "Warnings", pending: "Pending", noRecords: "No upload records", addWell: "Add Well", selectedWell: "Selected Well", monthlyUploaded: "Uploaded This Month", monthlyPending: "Pending Uploads", reportKinds: "Report Types", monthlyUploaders: "Uploaders This Month", calendarHint: "Tip: click a completed calendar date to preview it", recordsCount: "records", uploader: "Uploader", uploadTime: "Upload Time", fileName: "File Name", status: "Status", operation: "Actions", date: "Date", well: "Well", reportType: "Report Type", page: "Page", prevPage: "Previous", nextPage: "Next", sourcePdfMissing: "The source PDF was not saved. Re-import this report to view it.", sourcePdfTitle: "Source PDF", sortFirstUpload: "First", sortLastUpload: "Latest", sortWellName: "Well",
      metricCompletion: "Completion", metricIssues: "Validation Issues", metricHours: "Operation Total", metricProgress: "Progress", metricIntervals: "Intervals", metricWellDate: "Well / Date", metricDailyHours: "Daily Hours", metricNptHours: "NPT Hours", metricDataCompleteness: "Data Completeness",
      metricWorkDays: "Work Days", metricNptShare: "NPT Hours / Share", metricPScShare: "P / SC Share", metricReportCompleteness: "Report Completeness", metricMoveDrillingDays: "Move / Drilling",
      analyticsKicker: "Analytics", analyticsProductionScope: "Based on daily report data saved in the Excel library", analyticsNptScope: "Based on daily report data saved in the Excel library; grouped by report OP Code / OP Sub", search: "Search", reset: "Reset", wellborePlaceholder: "Enter well",
      chartRigHours: "Rig Cumulative NPT Ranking", chartOperationMix: "Operation Mix", chartMonthlyHours: "Well Operation Gantt", chartNptRig: "Rig NPT Comparison (h)", chartNptReason: "OP Code / OP Sub Distribution", chartNptWell: "Well NPT Ranking", chartNptMonthly: "Monthly NPT Trend (h)", productionDetailTitle: "Production Report Details", nptDetailTitle: "NPT Details", analyticsRowHint: "Click a row to open the report details", productionReportRowHint: "Click a well to open its report homepage in a new tab", nptRowHint: "Grouped by original OP Code / OP Sub from reports; click a row to trace the report",
      kpiRigCount: "Rig Count", kpiNptRigCount: "NPT Rig Count", kpiWellCount: "Wells", kpiTotalHours: "Total Hours", kpiTotalNpt: "Total NPT", kpiReportCompleteness: "Report Completeness", kpiNptEvents: "NPT Events", analyticsDefaultCaption: "Based on saved reports", analyticsNptCaption: "Grouped by OP Code / OP Sub", analyticsCompletenessCaption: "Missing {missing} days / Warnings {warning} days", noAnalyticsData: "No data available", noExportData: "No data to export", normalStatus: "Normal", reasonMissing: "No OP Code / OP Sub",
      allRigs: "All Rigs", allProjects: "All Projects", allReportTypes: "All Types", allReasons: "All Categories", opCodeSub: "OP Code / OP Sub", opCode: "OP Code", opSub: "OP Sub", category: "Category", tableProject: "Project", tableContractProject: "Contract (Project)", tableRig: "Rig", tableWell: "Well", tableReportType: "Report Type", tableStartDate: "Start Date", tableEndDate: "End Date", tableMoveDate: "Move Date", tableDrillingStartDate: "Drilling Start", tableDrillingFinishDate: "Drilling Finish", tableCompletionDate: "Completion Date", tableWorkoverDate: "Workover Date", tableDrillingHours: "Drilling (h)", tableCompletionHours: "Completion (h)", tableWorkoverHours: "Workover (h)", tableMoveHours: "Move (h)", tableNptHours: "NPT (h)", tableRemarks: "Remarks", tableDate: "Date", tableOperationDetails: "Operation Details",
      sectionBasic: "Basic Info", sectionSummary: "Operations Summary", sectionWellControl: "Well Control & Hydraulics", sectionSurvey: "Survey Data (Last 6)", sectionMud: "Mud Data", sectionBitBha: "Bit & BHA", sectionOperations: "Operations", sectionCosts: "Costs & Bulks", sectionIncidents: "Incidents & Remarks", sectionPersonnel: "Personnel", sectionPerforationIntervals: "Perforated Intervals",
      noteBasic: "Header and well information from the PDF template", noteSummary: "Current operation, 24-hour summary, and next plan", noteWellControl: "Casing, BOP, pump pressure, torque, and hookload", noteIncidents: "HSE status, simultaneous operations, and remarks",
      completionNoteBasic: "Completion PDF header, AFP, and well information", completionNotePersonnel: "Supervisors, engineers, geologist, and total personnel", completionNoteRemarks: "Safety comments, solids control, and field remarks", workoverNoteBasic: "Workover PDF header, AFP, and well information", workoverNotePersonnel: "Supervisors, engineers, geologist, and total personnel", workoverNoteRemarks: "Safety comments, solids control, and field remarks",
      addSurvey: "Add Survey", addBha: "Add BHA", addOperation: "Add Operation", addCost: "Add Cost", addBulk: "Add Bulk", addInterval: "Add Interval", rulesTitle: "Basic Validation Rules", liveValidation: "Live Validation",
      uploadedDays: "Uploaded", daysUnit: "days", missingDate: "Missing",
      prevMonth: "Previous month", nextMonth: "Next month", savedWarnings: "Saved Checks",
      noIssues: "No validation issues.", pdfImporting: "Parsing PDF report...", pdfImported: "PDF report parsed and filled into the form.", pdfImportFailed: "PDF parsing failed. Check the file format or template.",
      thMd: "MD (ft)", thIncl: "Incl (deg)", thAzi: "Azi (deg)", thTvd: "TVD (ft)", thVse: "VSE (ft)", thNs: "N/-S (ft)", thDls: "DLS (deg/100ft)", thBuild: "Build (deg/100ft)", thComponent: "Component", thOd: "OD (in)", thId: "ID (in)", thJts: "Jts", thLength: "Length (ft)", thFrom: "From (HH:MM)", thTo: "To (HH:MM)", thHrs: "Hrs (h)", thOpCode: "Op Code", thOpSub: "Op Sub", thType: "Type", thOperationDetails: "Operation Details", thCostDescription: "Cost Description", thVendor: "Vendor", thAmount: "Amount (USD)", thBulk: "Bulk", thQtyStart: "Qty Start", thQtyUsed: "Qty Used", thQtyEnd: "Qty End", thFormation: "Formation", thTopMd: "Top MD (ft)", thBaseMd: "Base MD (ft)", thDensity: "Density (spf)", thCharges: "Charges", thPhase: "Phase (deg)", thPenetration: "Penetration (in)", thDiameter: "Diameter (in)", thDate: "Date", thStatus: "Status", thComments: "Comments"
    },
    fields: {
      event: "Event", reportDate: "Date", project: "Project", date_from: "Date From", date_to: "Date To", scope_type: "Filter By", scope_value: "Scope", report_type: "Report Type", reason: "OP Code / OP Sub", nptWellbore: "Wellbore", nptRig: "Rig", nptStatus: "Confirmation Status", reportNo: "Report No", wellbore: "Wellbore", rig: "Rig", primaryReason: "Primary Reason", afeNumber: "AFE Number", refDatum: "Reference Datum", todayMd: "Today's MD (ft)", prevMd: "Previous MD (ft)", progress: "Progress (ft)", rotHrsToday: "Rotating Hours Today",
      currentOps: "Current Operations", summary24h: "24-Hour Summary", forecast24h: "24-Hour Forecast", lastCasing: "Last Casing", lastCasingSize: "Last Casing Size", lastCasingDepth: "Last Casing Depth", nextCasing: "Next Casing", nextCasingSize: "Next Casing Size", nextCasingDepth: "Next Casing Depth", formTestEmw: "Formation Test / EMW", lastBopPressTest: "Last BOP Pressure Test", pumpRate: "Pump Rate (gpm)", pumpPress: "Pump Pressure (psi)", stringWeightUpDown: "String Weight Up/Down", torqueOnBottom: "Torque On Bottom",
      mudEngineer: "Mud Engineer", sampleFrom: "Sample From", mudType: "Mud Type", mudTimeMd: "Time / MD", mudTime: "Mud Time", mudMd: "Mud MD", mudDensity: "Density (ppg)", mudTemperature: "Mud Temp", rheologyTemp: "Rheology Temp", viscosity: "Viscosity", pvYp: "PV / YP", pv: "PV", yp: "YP", gels: "Gels 10s/10m/30m", gel10s: "Gel 10s", gel10m: "Gel 10m", gel30m: "Gel 30m", apiWl: "API WL", oilWater: "Oil / Water", oilPercent: "Oil (%)", waterPercent: "Water (%)", sand: "Sand (%)", ecd: "ECD", mudComments: "Mud Comments",
      bitNo: "Bit No", bitSize: "Bit Size", bitManufacturer: "Manufacturer", bitSerial: "Serial No", bhaNo: "BHA No", bhaMdIn: "MD In", bhaMdOut: "MD Out", bhaTotalLength: "Total Length (ft)", safetyIncident: "Safety Incident?", environmentIncident: "Environmental Incident?", daysSinceRi: "Days since Last RI", daysSinceLta: "Days since Last LTA", incidentComments: "Incident Comments", otherRemarks: "Other Remarks",
      description: "Description", operationStartDate: "Operation Start", workoverNo: "WO No", afeCost: "AFP Cost", dailyCost: "Daily Cost", cumulativeCost: "Cumulative Cost", supervisor1: "Supervisor 1", supervisor2: "Supervisor 2", engineer: "Engineer", pamEngineer: "PAM Engineer", geologist: "Geologist", totalPersonnel: "Total Personnel", safetyComments: "Safety Comments"
    },
    rules: [
      "<strong>Required:</strong> Date, Report No, Wellbore, Rig, Current Operations, 24-Hour Summary, Mud Type, and Today's MD.",
      "<strong>Date:</strong> report date cannot be later than today.",
      "<strong>Depth:</strong> Today's MD must be greater than or equal to Previous MD; Progress should match the difference with 0.5 ft tolerance.",
      "<strong>Hours:</strong> Operations Hrs must total 24.00 hours with 0.05 h tolerance.",
      "<strong>Operation rows:</strong> From, To, Hrs, Op Code, Type, and Operation Details should be complete; Type must be P or NPT.",
      "<strong>Survey:</strong> Survey MD cannot exceed Today's MD; Incl must be 0 to 180; DLS cannot be negative.",
      "<strong>Mud:</strong> Density should be 6 to 20 ppg; Sand should not exceed 10%.",
      "<strong>Equipment:</strong> BHA OD, ID, Jts, and Length cannot be negative; OD should be greater than or equal to ID.",
      "<strong>HSE:</strong> Incident Comments are required when Safety or Environmental Incident is Y.",
      "<strong>Costs and bulks:</strong> parsed values are shown for review only and are not cell-validated."
    ],
    completionRules: [
      "<strong>Required:</strong> Date, Report No, Wellbore, Rig, Current Operations, 24-Hour Summary, and 24-Hour Forecast.",
      "<strong>Date:</strong> report date cannot be later than today, and Operation Start cannot be later than the report date.",
      "<strong>Hours:</strong> Operations Hrs must total 24.00 hours with 0.05 h tolerance.",
      "<strong>Operation rows:</strong> From, To, Hrs, Op Code, Type, and Operation Details should be complete; Type must be P, SC, or NPT.",
      "<strong>Perforated intervals:</strong> Base MD should be greater than or equal to Top MD; Length cannot be negative.",
      "<strong>Bulks and costs:</strong> parsed values are shown for review only and are not cell-validated."
    ],
    workoverRules: [
      "<strong>Required:</strong> Date, Report No, Wellbore, Rig, Current Operations, 24-Hour Summary, and 24-Hour Forecast.",
      "<strong>Date:</strong> report date cannot be later than today, and Operation Start cannot be later than the report date.",
      "<strong>Hours:</strong> Operations Hrs must total 24.00 hours with 0.05 h tolerance.",
      "<strong>Operation rows:</strong> From, To, Hrs, Op Code, Type, and Operation Details should be complete; Type must be P, SC, or NPT.",
      "<strong>Perforated intervals:</strong> Base MD should be greater than or equal to Top MD; Length cannot be negative.",
      "<strong>Bulks and costs:</strong> parsed values are shown for review only and are not cell-validated."
    ],
    moveRules: [
      "<strong>Required:</strong> Date, Report No, Wellbore, Rig, Current Operations, 24-Hour Summary, and 24-Hour Forecast.",
      "<strong>Hours:</strong> Operations Hrs must total 24.00 hours with 0.05 h tolerance.",
      "<strong>Operation rows:</strong> From, To, Hrs, Op Code, Type, and Operation Details should be complete; Type must be P, SC, or NPT.",
      "<strong>Remarks:</strong> Other Remarks can keep the original final-page text for manual review."
    ],
    msg: {
      required: "{field} is required.", futureDate: "Report date cannot be later than today.", operationStartDate: "Operation Start cannot be later than the report date.", mdOrder: "Today's MD must be greater than or equal to Previous MD.", progressMismatch: "Progress does not match the MD difference. Current difference is {value} ft.", operationMissingTable: "Operations cannot be empty.", operationHours: "Operations total must be 24.00 h. Current total is {value} h.", operationMissing: "Operations row {row} is missing {field}.", operationTimeMismatch: "Operations row {row} From/To duration is {value} h and does not match Hrs.", operationType: "Operations row {row} Type is empty or not P/NPT; please review.", completionOperationType: "Completion operation row {row} Type is empty or not P/SC/NPT; please review.", workoverOperationType: "Workover operation row {row} Type is empty or not P/SC/NPT; please review.", moveOperationType: "Move operation row {row} Type is empty or not P/SC/NPT; please review.", operationHourRange: "Operations row {row} Hrs must be between 0 and 24.", intervalDepth: "Perforated interval row {row} Base MD should be greater than or equal to Top MD.", intervalLength: "Perforated interval row {row} Length cannot be negative.", surveyMd: "Survey row {row} MD cannot exceed Today's MD.", surveyIncl: "Survey row {row} Incl must be between 0 and 180.", surveyDls: "Survey row {row} DLS cannot be negative.", mudDensity: "Mud density should be between 6 and 20 ppg.", sand: "Mud sand is above 10%; please review.", bhaOdId: "BHA row {row} OD should be greater than or equal to ID.", bhaNegative: "BHA row {row} contains a negative value.", negativeValue: "Row {row} {field} cannot be negative.", incidentRequired: "Incident Comments are required when Safety or Environmental Incident is Y."
    }
  },
  es: {
    ui: {
      appTitleShort: "Campo Ecuador", appSubtitle: "Plataforma de Reportes", pageTitle: "Mesa de Registro del Reporte Diario", drillingPageKicker: "REPORTE DIARIO DE PERFORACIÓN", completionPageTitle: "Mesa del Reporte Diario de Completación", completionPageKicker: "REPORTE DIARIO DE COMPLETACIÓN", workoverPageTitle: "Mesa del Reporte Diario de Workover", workoverPageKicker: "REPORTE DIARIO DE WORKOVER",
      systemAdmin: "Administración",
      menuDailyParsing: "Análisis de Reportes", menuDrillingDaily: "Reporte Diario de Perforación", menuCompletionDaily: "Reporte Diario de Completación", menuWorkoverDaily: "Reporte Diario de Workover", menuMoveDaily: "Reporte Diario de Movilización",
      menuProductionReport: "Reportes de Producción", menuRigProductionSummary: "Tiempo de Producción", menuProductionDetailReport: "Reporte de Producción", menuWellNptConfirm: "Estadística NPT", menuRigNptRanking: "Confirmación NPT",
      menuHsse: "Gestión HSSE", menuHsseCollection: "Registro de Información", menuHsseDashboard: "Cabina de Seguridad", menuDailySafetySummary: "Reporte de Seguridad", menuPeriodSafetyReport: "Reporte de Seguridad",
      descDrillingDaily: "Carga reportes diarios PDF de perforación o movilización, extrae datos básicos y operaciones, y permite editar el reporte diario de perforación.",
      descCompletionDaily: "Carga PDFs diarios de completación, extrae datos básicos, operaciones, inventarios e intervalos cañoneados, y permite revisar y editar.", descWorkoverDaily: "Carga PDFs diarios de workover, extrae información WO, operaciones, inventarios, comentarios de seguridad e intervalos cañoneados, y permite revisar y editar.", descMoveDaily: "Entrada reservada para análisis PDF y captura estructurada de reportes diarios de movilización.",
      descRigProductionSummary: "Muestra tiempos de producción por equipo, tipo de reporte y mes desde reportes diarios procesados.", descProductionDetailReport: "Consulta detalles de producción por periodo de proyecto, equipo y asignación de pozo.", descWellNptConfirm: "Clasifica equipos de perforación por duración y proporción histórica de NPT.", descRigNptRanking: "Confirma horas P, SC y NPT por pozo, con actualización posterior desde tablas de confirmación de tiempos.",
      descHsseCollection: "Registra información HSSE diaria por pozo y equipo, incluyendo actos inseguros, condiciones inseguras, personal vulnerable, anomalías productivas y seguridad pública.", descHsseDashboard: "Muestra KPIs HSSE, excepciones y seguimiento general por equipo.", descDailySafetySummary: "Genera reportes de seguridad a partir de datos HSSE.", descPeriodSafetyReport: "Combina estadísticas diarias y reportes semanales o mensuales en una entrada de reporte de seguridad.",
      moduleStatusPlanned: "Función Planificada", moduleComingSoon: "Función Reservada", moduleCurrent: "Menú Actual", moduleComingSoonDesc: "Esta entrada queda reservada según la lista de requisitos. Luego se podrá conectar captura de datos, reportes o análisis.",
      navBasic: "Información Básica", navSummary: "Resumen Operacional", navWellControl: "Control de Pozo e Hidráulica", navSurvey: "Datos Direccionales", navMud: "Datos de Lodo", navBitBha: "Broca y BHA", navOperations: "Registro de Operaciones", navCosts: "Costos e Inventario", navIncidents: "Incidentes y Observaciones",
      importPdf: "Importar Reporte PDF", originalReport: "Original", translateChinese: "Traducir a chino", translationRunning: "Cambiando idioma del reporte...", translationReady: "Vista traducida lista.", translationFailed: "Falló la traducción. Verifique que el servicio local esté iniciado.", translationPreviewNotice: "La traducción es solo lectura. Vuelva a Original para editar o guardar.", translationTitle: "Traducción EN/ES del Reporte Diario", translationOriginal: "Original", translationLanguage: "Idioma", translationChinese: "Chino", translationPath: "Campo", translationTerms: "Términos", translationWarnings: "Alertas", translationEmpty: "No hay resultados de traducción", saveDatabase: "Guardar", downloadDatabase: "Descargar Excel", backRecords: "Volver a registros", databaseSaved: "Guardado en la base Excel.", databaseSaveFailed: "No se pudo guardar la base Excel.", recordLoadFailed: "No se pudo abrir el detalle del reporte.", databaseRecord: "Registro de base", sourceFileEmpty: "No se ha cargado archivo",
      uploadDashboardTitle: "Panel de Reportes Diarios", wellSelection: "Selección de Pozo", searchWell: "Buscar pozo", reportCalendar: "Calendario", uploadRecords: "Registros de Carga", allTypes: "Todos los tipos", allStatuses: "Todos los estados", exportList: "Exportar", preview: "Ver", download: "Descargar", detail: "Detalle", uploaded: "Completo", queued: "En cola", parsing: "Analizando", failed: "Falló", warningStatus: "Alertas", pending: "Pendiente", noRecords: "Sin registros", addWell: "Agregar pozo", selectedWell: "Pozo actual", monthlyUploaded: "Cargados del mes", monthlyPending: "Pendientes", reportKinds: "Tipos de reporte", monthlyUploaders: "Cargadores del mes", calendarHint: "Tip: haga clic en una fecha completada para previsualizar", recordsCount: "registros", uploader: "Usuario", uploadTime: "Hora de carga", fileName: "Archivo", status: "Estado", operation: "Acciones", date: "Fecha", well: "Pozo", reportType: "Tipo", page: "Página", prevPage: "Anterior", nextPage: "Siguiente", sourcePdfMissing: "El PDF fuente no se guardó. Vuelva a importarlo para verlo.", sourcePdfTitle: "PDF fuente", sortFirstUpload: "Prim.", sortLastUpload: "Rec.", sortWellName: "Pozo",
      metricCompletion: "Avance", metricIssues: "Alertas", metricHours: "Total Operativo", metricProgress: "Progreso", metricIntervals: "Intervalos", metricWellDate: "Pozo / Fecha", metricDailyHours: "Horas del Día", metricNptHours: "Horas NPT", metricDataCompleteness: "Integridad de Datos",
      metricWorkDays: "Días Operativos", metricNptShare: "Horas NPT / %", metricPScShare: "% P / SC", metricReportCompleteness: "Integridad del Reporte", metricMoveDrillingDays: "Movilización / Perforación",
      analyticsKicker: "Panel de Datos", analyticsProductionScope: "Basado en reportes diarios guardados en la biblioteca Excel", analyticsNptScope: "Basado en reportes diarios guardados en la biblioteca Excel; agrupado por código y subcódigo de operación", search: "Consultar", reset: "Restablecer", wellborePlaceholder: "Ingrese pozo",
      chartRigHours: "Ranking NPT acumulado por taladro", chartOperationMix: "Composición Operativa", chartMonthlyHours: "Gantt de Operaciones por Pozo", chartNptRig: "Comparación NPT por Taladro (h)", chartNptReason: "Distribución por Código / Subcódigo", chartNptWell: "Ranking NPT por Pozo", chartNptMonthly: "Tendencia Mensual NPT (h)", productionDetailTitle: "Detalle del Reporte de Producción", nptDetailTitle: "Detalle NPT", analyticsRowHint: "Haga clic en una fila para abrir el detalle del reporte", productionReportRowHint: "Haga clic en un pozo para abrir su página diaria en una pestaña nueva", nptRowHint: "Agrupado por código / subcódigo original del reporte; haga clic en una fila para rastrear el reporte",
      kpiRigCount: "Taladros", kpiNptRigCount: "Taladros con NPT", kpiWellCount: "Pozos", kpiTotalHours: "Horas Totales", kpiTotalNpt: "NPT Total", kpiReportCompleteness: "Integridad del Reporte", kpiNptEvents: "Eventos NPT", analyticsDefaultCaption: "Basado en reportes guardados", analyticsNptCaption: "Agrupado por código / subcódigo", analyticsCompletenessCaption: "Faltan {missing} días / Alertas {warning} días", noAnalyticsData: "No hay datos para estadística", noExportData: "No hay datos para exportar", normalStatus: "Normal", reasonMissing: "Sin código / subcódigo",
      allRigs: "Todos los taladros", allProjects: "Todos los proyectos", allReportTypes: "Todos los tipos", allReasons: "Todas las categorías", opCodeSub: "Código / Subcódigo", opCode: "Código Op", opSub: "Subcódigo Op", category: "Categoría", tableProject: "Proyecto", tableContractProject: "Contrato (Proyecto)", tableRig: "Taladro", tableWell: "Pozo", tableReportType: "Tipo de Reporte", tableStartDate: "Fecha Inicio", tableEndDate: "Fecha Fin", tableMoveDate: "Fecha Movilización", tableDrillingStartDate: "Inicio Perforación", tableDrillingFinishDate: "Fin Perforación", tableCompletionDate: "Fecha Completación", tableWorkoverDate: "Fecha Workover", tableDrillingHours: "Perforación (h)", tableCompletionHours: "Completación (h)", tableWorkoverHours: "Workover (h)", tableMoveHours: "Movilización (h)", tableNptHours: "NPT (h)", tableRemarks: "Observaciones", tableDate: "Fecha", tableOperationDetails: "Detalle de Operación",
      sectionBasic: "Información Básica", sectionSummary: "Resumen Operacional", sectionWellControl: "Control de Pozo e Hidráulica", sectionSurvey: "Datos Direccionales (Últimos 6)", sectionMud: "Datos de Lodo", sectionBitBha: "Broca y BHA", sectionOperations: "Operaciones", sectionCosts: "Costos e Inventario", sectionIncidents: "Incidentes y Observaciones", sectionPersonnel: "Personal", sectionPerforationIntervals: "Intervalos Cañoneados",
      noteBasic: "Encabezado e información del pozo según la plantilla PDF", noteSummary: "Operación actual, resumen de 24 horas y plan siguiente", noteWellControl: "Casing, BOP, presión de bomba, torque y hookload", noteIncidents: "Estado HSE, operaciones simultáneas y observaciones",
      completionNoteBasic: "Encabezado PDF de completación, AFP e información del pozo", completionNotePersonnel: "Supervisores, ingenieros, geólogo y personal total", completionNoteRemarks: "Comentarios de seguridad, control de sólidos y observaciones de campo", workoverNoteBasic: "Encabezado PDF de workover, AFP e información del pozo", workoverNotePersonnel: "Supervisores, ingenieros, geólogo y personal total", workoverNoteRemarks: "Comentarios de seguridad, control de sólidos y observaciones de campo",
      addSurvey: "Agregar Survey", addBha: "Agregar BHA", addOperation: "Agregar Operación", addCost: "Agregar Costo", addBulk: "Agregar Inventario", addInterval: "Agregar Intervalo", rulesTitle: "Reglas Básicas de Validación", liveValidation: "Validación en Vivo",
      uploadedDays: "Cargados", daysUnit: "días", missingDate: "Faltante",
      prevMonth: "Mes anterior", nextMonth: "Mes siguiente", savedWarnings: "Validaciones guardadas",
      noIssues: "Sin alertas de validación.", pdfImporting: "Analizando reporte PDF...", pdfImported: "Reporte PDF analizado y cargado en el formulario.", pdfImportFailed: "No se pudo analizar el PDF. Revise el formato o la plantilla.",
      thMd: "MD (ft)", thIncl: "Incl (deg)", thAzi: "Azi (deg)", thTvd: "TVD (ft)", thVse: "VSE (ft)", thNs: "N/-S (ft)", thDls: "DLS (deg/100ft)", thBuild: "Build (deg/100ft)", thComponent: "Componente", thOd: "OD (in)", thId: "ID (in)", thJts: "Jts", thLength: "Longitud (ft)", thFrom: "Desde (HH:MM)", thTo: "Hasta (HH:MM)", thHrs: "Hrs (h)", thOpCode: "Código Op", thOpSub: "Sub Op", thType: "Tipo", thOperationDetails: "Detalle de Operación", thCostDescription: "Descripción de Costo", thVendor: "Proveedor", thAmount: "Monto (USD)", thBulk: "Inventario", thQtyStart: "Cant. Inicial", thQtyUsed: "Cant. Usada", thQtyEnd: "Cant. Final", thFormation: "Formación", thTopMd: "Tope MD (ft)", thBaseMd: "Base MD (ft)", thDensity: "Densidad (spf)", thCharges: "Cargas", thPhase: "Fase (deg)", thPenetration: "Penetración (in)", thDiameter: "Diámetro (in)", thDate: "Fecha", thStatus: "Estado", thComments: "Comentarios"
    },
    fields: {
      event: "Evento", reportDate: "Fecha", project: "Proyecto", date_from: "Fecha Inicio", date_to: "Fecha Fin", scope_type: "Filtrar Por", scope_value: "Alcance", report_type: "Tipo de Reporte", reason: "Código / Subcódigo", nptWellbore: "Pozo", nptRig: "Taladro", nptStatus: "Estado de Confirmación", reportNo: "No. de Reporte", wellbore: "Pozo", rig: "Taladro", primaryReason: "Razón Principal", afeNumber: "Número AFE", refDatum: "Datum de Referencia", todayMd: "MD de Hoy (ft)", prevMd: "MD Anterior (ft)", progress: "Progreso (ft)", rotHrsToday: "Horas Rotando Hoy",
      currentOps: "Operación Actual", summary24h: "Resumen 24 h", forecast24h: "Pronóstico 24 h", lastCasing: "Último Casing", lastCasingSize: "Tamaño Último Casing", lastCasingDepth: "Profundidad Último Casing", nextCasing: "Próximo Casing", nextCasingSize: "Tamaño Próximo Casing", nextCasingDepth: "Profundidad Próximo Casing", formTestEmw: "Prueba Formación / EMW", lastBopPressTest: "Última Prueba BOP", pumpRate: "Caudal Bomba (gpm)", pumpPress: "Presión Bomba (psi)", stringWeightUpDown: "Peso Sarta Arriba/Abajo", torqueOnBottom: "Torque en Fondo",
      mudEngineer: "Ingeniero de Lodo", sampleFrom: "Muestra de", mudType: "Tipo de Lodo", mudTimeMd: "Hora / MD", mudTime: "Hora Lodo", mudMd: "MD Lodo", mudDensity: "Densidad (ppg)", mudTemperature: "Temp. Lodo", rheologyTemp: "Temp. Reología", viscosity: "Viscosidad", pvYp: "PV / YP", pv: "PV", yp: "YP", gels: "Geles 10s/10m/30m", gel10s: "Gel 10s", gel10m: "Gel 10m", gel30m: "Gel 30m", apiWl: "API WL", oilWater: "Aceite / Agua", oilPercent: "Aceite (%)", waterPercent: "Agua (%)", sand: "Arena (%)", ecd: "ECD", mudComments: "Comentarios de Lodo",
      bitNo: "No. Broca", bitSize: "Tamaño Broca", bitManufacturer: "Fabricante", bitSerial: "No. Serie", bhaNo: "No. BHA", bhaMdIn: "MD Entrada", bhaMdOut: "MD Salida", bhaTotalLength: "Longitud Total (ft)", safetyIncident: "¿Incidente de Seguridad?", environmentIncident: "¿Incidente Ambiental?", daysSinceRi: "Días desde Último RI", daysSinceLta: "Días desde Último LTA", incidentComments: "Comentarios de Incidente", otherRemarks: "Otras Observaciones",
      description: "Descripción", operationStartDate: "Inicio OPR", workoverNo: "No. WO", afeCost: "Costo AFP", dailyCost: "Costo Diario", cumulativeCost: "Costo Acumulado", supervisor1: "Supervisor 1", supervisor2: "Supervisor 2", engineer: "Ingeniero", pamEngineer: "Ingeniero PAM", geologist: "Geólogo", totalPersonnel: "Total Personal", safetyComments: "Comentarios de Seguridad"
    },
    rules: [
      "<strong>Obligatorio:</strong> Fecha, No. de Reporte, Pozo, Taladro, Operación Actual, Resumen 24 h, Tipo de Lodo y MD de Hoy.",
      "<strong>Fecha:</strong> la fecha del reporte no puede ser posterior a hoy.",
      "<strong>Profundidad:</strong> el MD de hoy debe ser mayor o igual al MD anterior; el progreso debe coincidir con tolerancia de 0.5 ft.",
      "<strong>Horas:</strong> las Hrs de operaciones deben sumar 24.00 horas con tolerancia de 0.05 h.",
      "<strong>Filas de operación:</strong> Desde, Hasta, Hrs, Código Op, Tipo y Detalle deben estar completos; Tipo debe ser P o NPT.",
      "<strong>Survey:</strong> MD no puede superar el MD de hoy; Incl debe estar entre 0 y 180; DLS no puede ser negativo.",
      "<strong>Lodo:</strong> densidad entre 6 y 20 ppg; arena no mayor a 10%.",
      "<strong>Equipo:</strong> OD, ID, Jts y Longitud de BHA no pueden ser negativos; OD debe ser mayor o igual a ID.",
      "<strong>HSE:</strong> comentarios obligatorios si Safety o Environmental Incident es Y.",
      "<strong>Costo:</strong> el monto no puede ser negativo; una tabla vacía puede guardarse con alerta."
    ],
    completionRules: [
      "<strong>Obligatorio:</strong> Fecha, No. de Reporte, Pozo, Taladro, Operación Actual, Resumen 24 h y Pronóstico 24 h.",
      "<strong>Fecha:</strong> la fecha del reporte no puede ser posterior a hoy e Inicio OPR no puede ser posterior a la fecha del reporte.",
      "<strong>Horas:</strong> las Hrs de operaciones deben sumar 24.00 horas con tolerancia de 0.05 h.",
      "<strong>Filas de operación:</strong> Desde, Hasta, Hrs, Código Op, Tipo y Detalle deben estar completos; Tipo debe ser P, SC o NPT.",
      "<strong>Intervalos cañoneados:</strong> Base MD debe ser mayor o igual que Tope MD; Longitud no puede ser negativa.",
      "<strong>Inventarios y costos:</strong> cantidades de inventario y montos no pueden ser negativos."
    ],
    workoverRules: [
      "<strong>Obligatorio:</strong> Fecha, No. de Reporte, Pozo, Taladro, Operación Actual, Resumen 24 h y Pronóstico 24 h.",
      "<strong>Fecha:</strong> la fecha del reporte no puede ser posterior a hoy e Inicio OPR no puede ser posterior a la fecha del reporte.",
      "<strong>Horas:</strong> las Hrs de operaciones deben sumar 24.00 horas con tolerancia de 0.05 h.",
      "<strong>Filas de operación:</strong> Desde, Hasta, Hrs, Código Op, Tipo y Detalle deben estar completos; Tipo debe ser P, SC o NPT.",
      "<strong>Intervalos cañoneados:</strong> Base MD debe ser mayor o igual que Tope MD; Longitud no puede ser negativa.",
      "<strong>Inventarios y costos:</strong> cantidades de inventario y montos no pueden ser negativos."
    ],
    moveRules: [
      "<strong>Obligatorio:</strong> Fecha, No. de Reporte, Pozo, Taladro, Operación Actual, Resumen 24 h y Pronóstico 24 h.",
      "<strong>Horas:</strong> las Hrs de operaciones deben sumar 24.00 horas con tolerancia de 0.05 h.",
      "<strong>Filas de operación:</strong> Desde, Hasta, Hrs, Código Op, Tipo y Detalle deben estar completos; Tipo debe ser P, SC o NPT.",
      "<strong>Observaciones:</strong> Other Remarks puede conservar el texto original de la última página para revisión manual."
    ],
    msg: {
      required: "{field} es obligatorio.", futureDate: "La fecha del reporte no puede ser posterior a hoy.", operationStartDate: "Inicio OPR no puede ser posterior a la fecha del reporte.", mdOrder: "El MD de hoy debe ser mayor o igual al MD anterior.", progressMismatch: "El progreso no coincide con la diferencia de MD. La diferencia actual es {value} ft.", operationMissingTable: "Las operaciones no pueden estar vacías.", operationHours: "El total de operaciones debe ser 24.00 h. El total actual es {value} h.", operationMissing: "La fila de operaciones {row} no tiene {field}.", operationTimeMismatch: "La duración Desde/Hasta de la fila {row} es {value} h y no coincide con Hrs.", operationType: "El Tipo en la fila de operaciones {row} está vacío o no es P/NPT; revisar.", completionOperationType: "El Tipo en la fila de completación {row} está vacío o no es P/SC/NPT; revisar.", workoverOperationType: "El Tipo en la fila de workover {row} está vacío o no es P/SC/NPT; revisar.", moveOperationType: "El Tipo en la fila de traslado {row} está vacío o no es P/SC/NPT; revisar.", operationHourRange: "Las Hrs de la fila {row} deben estar entre 0 y 24.", intervalDepth: "En intervalo cañoneado fila {row}, Base MD debe ser mayor o igual que Tope MD.", intervalLength: "La Longitud del intervalo cañoneado fila {row} no puede ser negativa.", surveyMd: "El MD de survey en la fila {row} no puede superar el MD de hoy.", surveyIncl: "La inclinación en la fila {row} debe estar entre 0 y 180.", surveyDls: "El DLS en la fila {row} no puede ser negativo.", mudDensity: "La densidad del lodo debe estar entre 6 y 20 ppg.", sand: "La arena del lodo supera 10%; revisar.", bhaOdId: "En BHA fila {row}, OD debe ser mayor o igual que ID.", bhaNegative: "La fila BHA {row} contiene un valor negativo.", negativeValue: "Fila {row}: {field} no puede ser negativo.", incidentRequired: "Los comentarios son obligatorios cuando Safety o Environmental Incident es Y."
    }
  }
};

const tableSchemas = {
  surveyTable: [{ name: "md", type: "number" }, { name: "incl", type: "number" }, { name: "azi", type: "number" }, { name: "tvd", type: "number" }, { name: "vse", type: "number" }, { name: "ns", type: "number" }, { name: "dls", type: "number" }, { name: "build", type: "number" }],
  bhaTable: [{ name: "component", type: "text" }, { name: "od", type: "number" }, { name: "id", type: "number" }, { name: "joints", type: "number" }, { name: "length", type: "number" }],
  operationsTable: [{ name: "from", type: "text" }, { name: "to", type: "text" }, { name: "hours", type: "number" }, { name: "op_code", type: "text" }, { name: "op_sub", type: "text" }, { name: "op_type", type: "select", options: ["", "P", "NPT"] }, { name: "operation_details", type: "textarea" }],
  costTable: [{ name: "cost_description", type: "text" }, { name: "vendor", type: "text" }, { name: "amount", type: "number" }],
  bulkTable: [{ name: "bulk", type: "text" }, { name: "qty_start", type: "number" }, { name: "qty_used", type: "number" }, { name: "qty_end", type: "number" }],
  completionOperationsTable: [{ name: "from", type: "text" }, { name: "to", type: "text" }, { name: "hours", type: "number" }, { name: "op_code", type: "text" }, { name: "op_sub", type: "text" }, { name: "op_type", type: "select", options: ["", "P", "SC", "NPT"] }, { name: "operation_details", type: "textarea" }],
  completionBulkTable: [{ name: "bulk", type: "text" }, { name: "qty_start", type: "number" }, { name: "qty_used", type: "number" }, { name: "qty_end", type: "number" }],
  completionCostTable: [{ name: "cost_description", type: "text" }, { name: "vendor", type: "text" }, { name: "amount", type: "number" }],
  perforationIntervalsTable: [{ name: "formation", type: "text" }, { name: "top_md", type: "number" }, { name: "base_md", type: "number" }, { name: "length", type: "number" }, { name: "density", type: "number" }, { name: "charges", type: "text" }, { name: "phase", type: "number" }, { name: "penetration", type: "number" }, { name: "diameter", type: "number" }, { name: "date", type: "text" }, { name: "status", type: "text" }, { name: "comments", type: "textarea" }],
  workoverOperationsTable: [{ name: "from", type: "text" }, { name: "to", type: "text" }, { name: "hours", type: "number" }, { name: "op_code", type: "text" }, { name: "op_sub", type: "text" }, { name: "op_type", type: "select", options: ["", "P", "SC", "NPT"] }, { name: "operation_details", type: "textarea" }],
  workoverBulkTable: [{ name: "bulk", type: "text" }, { name: "qty_start", type: "number" }, { name: "qty_used", type: "number" }, { name: "qty_end", type: "number" }],
  workoverCostTable: [{ name: "cost_description", type: "text" }, { name: "vendor", type: "text" }, { name: "amount", type: "number" }],
  workoverIntervalsTable: [{ name: "formation", type: "text" }, { name: "top_md", type: "number" }, { name: "base_md", type: "number" }, { name: "length", type: "number" }, { name: "density", type: "number" }, { name: "charges", type: "text" }, { name: "phase", type: "number" }, { name: "penetration", type: "number" }, { name: "diameter", type: "number" }, { name: "date", type: "text" }, { name: "status", type: "text" }, { name: "comments", type: "textarea" }],
  moveOperationsTable: [{ name: "from", type: "text" }, { name: "to", type: "text" }, { name: "hours", type: "number" }, { name: "op_code", type: "text" }, { name: "op_sub", type: "text" }, { name: "op_type", type: "select", options: ["", "P", "SC", "NPT"] }, { name: "operation_details", type: "textarea" }]
};

const drillingTableIds = ["surveyTable", "bhaTable", "operationsTable", "costTable", "bulkTable"];
const completionTableIds = ["completionOperationsTable", "completionBulkTable", "completionCostTable", "perforationIntervalsTable"];
const workoverTableIds = ["workoverOperationsTable", "workoverBulkTable", "workoverCostTable", "workoverIntervalsTable"];
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
let currentLanguage = ["zh", "en", "es"].includes(storedLanguage) ? storedLanguage : "zh";
let reportContentLanguageMode = "original";
let activeMenuTarget = "drilling-daily";
let drillingSourceFileName = "";
const MANUAL_WELLS_STORAGE_KEY = "drillingReportManualWellProfiles";
const currentRecordIds = { drilling: "", completion: "", workover: "", move: "" };
const savedReportSignatures = { drilling: "", completion: "", workover: "", move: "" };
const lockedRecordIds = new Set();
const reportContentState = {
  drilling: { mode: "original", original: null, cache: {}, targetLanguage: "" },
  completion: { mode: "original", original: null, cache: {}, targetLanguage: "" },
  workover: { mode: "original", original: null, cache: {}, targetLanguage: "" },
  move: { mode: "original", original: null, cache: {}, targetLanguage: "" }
};
const RECORDS_PER_PAGE = 10;
const ANALYTICS_DETAIL_PAGE_SIZE = 10;
const recordState = {
  drilling: { records: [], selectedWell: "", selectedDate: "", search: "", calendarMonth: "", page: 1, sortBy: "last" },
  completion: { records: [], selectedWell: "", selectedDate: "", search: "", calendarMonth: "", page: 1, sortBy: "last" },
  workover: { records: [], selectedWell: "", selectedDate: "", search: "", calendarMonth: "", page: 1, sortBy: "last" },
  move: { records: [], selectedWell: "", selectedDate: "", search: "", calendarMonth: "", page: 1, sortBy: "last" }
};
const serverWarnings = { drilling: [], completion: [], workover: [], move: [] };
const wellStatsCache = {};
const analyticsState = {
  production: { payload: null, detailPage: 1, sortField: "", sortDir: "desc" },
  productionReport: {
    payload: null,
    detailPage: 1,
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
  loading: false
};
const adminState = {
  authenticated: false,
  user: null,
  permissions: {},
  tab: "overview",
  users: [],
  roles: [],
  config: {},
  dataStatus: null,
  logs: []
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
const fallbackWells = ["SCHAO-611", "PCNC-040", "SCHAS-513", "LOBC-010", "ACAH-270H", "TCHA-006I"];
let manualWellProfiles = loadManualWellProfiles();

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

function loadManualWellProfiles() {
  try {
    const parsed = JSON.parse(localStorage.getItem(MANUAL_WELLS_STORAGE_KEY) || "[]");
    return Array.isArray(parsed) ? parsed.filter((item) => item && item.wellbore).map(normalizeManualWellProfile) : [];
  } catch (error) {
    console.warn("Manual well profiles reset after invalid storage.", error);
    return [];
  }
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
  if (!currentLabel || !separator) return;
  const hasCurrent = Boolean(String(current || "").trim());
  currentLabel.textContent = hasCurrent ? current : "";
  currentLabel.hidden = !hasCurrent;
  separator.hidden = !hasCurrent;
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
  return ({ admin: "管理员", engineer: "工程师", reviewer: "审阅者", viewer: "查看者" }[role] || role || "-");
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
      <button class="link-button" type="button" data-front-logout>退出</button>
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
    el.disabled = !canSave || el.disabled;
  });
  document.querySelectorAll(".download-link,[data-analytics-export]").forEach((el) => {
    el.hidden = !canExport;
    el.disabled = !canExport;
  });
  document.querySelectorAll(".report-form input,.report-form textarea,.report-form select,.report-form button").forEach((el) => {
    el.disabled = !canEdit;
  });
  document.querySelectorAll("[data-add-row],.row-delete").forEach((el) => {
    el.hidden = !canEdit;
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
  if (!["zh", "en", "es"].includes(language)) return;
  currentLanguage = language;
  localStorage.setItem("drillingReportLanguage", language);
  document.documentElement.lang = language === "zh" ? "zh-CN" : language;
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    el.textContent = ui(el.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
    el.placeholder = ui(el.dataset.i18nPlaceholder);
  });
  syncLanguageButtons();
  document.querySelectorAll("label").forEach((label) => {
    if (label.closest(".admin-page")) return;
    if (label.classList.contains("npt-date-range")) {
      setLeadingLabelText(label, currentLanguage === "en" ? "Date Range" : currentLanguage === "es" ? "Rango de Fecha" : "日期起止");
      return;
    }
    const control = label.querySelector("[name]");
    if (control) setLeadingLabelText(label, labelFor(control.name));
  });
  setDrillingSourceFile(drillingSourceFileName);
  if (currentRecordIds.drilling) rememberRecord("drilling", { metadata: { source_file: drillingSourceFileName, record_id: currentRecordIds.drilling } });
  document.querySelector("#rulesList").innerHTML = i18n[language].rules.map((rule) => `<li>${rule}</li>`).join("");
  document.querySelector("#completionRulesList").innerHTML = i18n[language].completionRules.map((rule) => `<li>${rule}</li>`).join("");
  document.querySelector("#workoverRulesList").innerHTML = i18n[language].workoverRules.map((rule) => `<li>${rule}</li>`).join("");
  document.querySelector("#moveRulesList").innerHTML = i18n[language].moveRules.map((rule) => `<li>${rule}</li>`).join("");
  Object.keys(recordState).forEach((reportType) => renderRecordDashboard(reportType));
  if (analyticsState.production.payload) renderProductionAnalytics(analyticsState.production.payload);
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
    button.classList.toggle("active", button.dataset.lang === reportContentLanguageMode);
  });
}

async function handleLanguageChoice(language) {
  if (language === "original") {
    restoreActiveReportOriginal();
    reportContentLanguageMode = "original";
    syncLanguageButtons();
    return;
  }
  if (!["zh", "en", "es"].includes(language)) return;
  reportContentLanguageMode = language;
  applyLanguage(language);
  await translateVisibleReportContent(language);
  syncLanguageButtons();
}

function activeReportType() {
  return ["drilling", "completion", "workover", "move"].find((reportType) => {
    const page = reportPage(reportType);
    if (!page || page.hidden || !page.classList.contains("active")) return false;
    return [...document.querySelectorAll(`[data-detail-view="${reportType}"]`)].some((el) => !el.hidden);
  }) || "";
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
  if (state.mode === "original" || !state.original) {
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

async function translateVisibleReportContent(targetLanguage) {
  const reportType = activeReportType();
  if (!reportType) return;
  const sourcePayload = captureOriginalReport(reportType);
  if (!sourcePayload) return;
  const state = reportContentState[reportType];
  const cacheKey = translationCacheKey(reportType, sourcePayload, targetLanguage);
  try {
    showToast(ui("translationRunning"));
    let result = state.cache[cacheKey];
    if (!result) {
      const response = await fetch("/api/translate-report", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ target_language: targetLanguage, payload: sourcePayload }),
      });
      result = await response.json();
      if (!response.ok) throw new Error(result.error || "Translation failed");
      state.cache[cacheKey] = result;
    }
    renderReportPayload(reportType, result.translated_payload || sourcePayload);
    state.mode = "translated";
    state.targetLanguage = targetLanguage;
    state.lastResult = result;
    applyFrontPermissions();
    showToast(ui("translationReady"));
  } catch (error) {
    console.error(error);
    const detail = error?.message ? `：${error.message}` : "";
    showToast(`${ui("translationFailed")}${detail}`);
  }
}

function translationCacheKey(reportType, payload, targetLanguage) {
  const metadata = payload?.metadata || {};
  const identity = metadata.record_id || metadata.source_file || "";
  return `${reportType}|${identity}|${targetLanguage}|${JSON.stringify(payload)}`;
}

function renderReportPayload(reportType, payload = {}) {
  if (reportType === "drilling") {
    applyReportFields(payload.report_fields || {});
    setDrillingSourceFile(payload.metadata?.source_file || drillingSourceFileName || "");
    loadRows({
      surveyTable: rowsFromPayload(payload.survey_data, "surveyTable"),
      bhaTable: rowsFromPayload(payload.bha_components, "bhaTable"),
      operationsTable: rowsFromPayload(payload.operations, "operationsTable"),
      costTable: rowsFromPayload(payload.daily_costs, "costTable"),
      bulkTable: rowsFromPayload(payload.bulks, "bulkTable")
    });
  }
  if (reportType === "completion") {
    applyReportFields(payload.report_fields || {}, completionForm);
    loadRows({
      completionOperationsTable: rowsFromPayload(payload.operations, "completionOperationsTable"),
      completionBulkTable: rowsFromPayload(payload.bulks, "completionBulkTable"),
      completionCostTable: rowsFromPayload(payload.daily_costs, "completionCostTable"),
      perforationIntervalsTable: rowsFromPayload(payload.perforation_intervals, "perforationIntervalsTable")
    }, completionTableIds);
  }
  if (reportType === "workover") {
    applyReportFields(payload.report_fields || {}, workoverForm);
    loadRows({
      workoverOperationsTable: rowsFromPayload(payload.operations, "workoverOperationsTable"),
      workoverBulkTable: rowsFromPayload(payload.bulks, "workoverBulkTable"),
      workoverCostTable: rowsFromPayload(payload.daily_costs, "workoverCostTable"),
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
    page.querySelectorAll(".report-form input,.report-form textarea,.report-form select,.report-form button,[data-add-row],.row-delete").forEach((el) => {
      el.disabled = true;
      if (el.matches("[data-add-row],.row-delete")) el.hidden = true;
    });
    document.querySelectorAll(`[data-save-report="${type}"]`).forEach((el) => {
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
  if (field.type === "select") {
    (field.options || []).forEach((optionValue) => {
      const option = document.createElement("option");
      option.value = optionValue;
      option.textContent = optionValue || "-";
      control.appendChild(option);
    });
  }
  control.value = value;
  if (field.type === "number") {
    control.type = "number";
    control.step = "0.01";
  }
  return control;
}

function addRow(tableId, values = []) {
  const tbody = document.querySelector(`#${tableId} tbody`);
  const tr = document.createElement("tr");
  tableSchemas[tableId].forEach((field, index) => {
    const td = document.createElement("td");
    td.appendChild(makeInput(field, values[index] ?? ""));
    tr.appendChild(td);
  });
  const action = document.createElement("td");
  const button = document.createElement("button");
  button.type = "button";
  button.className = "row-delete";
  button.setAttribute("aria-label", "Delete row");
  button.textContent = "×";
  button.addEventListener("click", () => {
    markReportOriginalEdited(tableReportType(tableId));
    tr.remove();
    validateForTable(tableId);
    updateSaveButton(tableReportType(tableId));
  });
  action.appendChild(button);
  tr.appendChild(action);
  tbody.appendChild(tr);
  applyFrontPermissions();
}

function loadRows(rows = {}, tableIds = drillingTableIds) {
  tableIds.forEach((tableId) => {
    document.querySelector(`#${tableId} tbody`).innerHTML = "";
    (rows[tableId] || [[]]).forEach((row) => addRow(tableId, row));
  });
  if (tableIds.some((tableId) => completionTableIds.includes(tableId))) validateCompletion();
  if (tableIds.some((tableId) => workoverTableIds.includes(tableId))) validateWorkover();
  if (tableIds.some((tableId) => moveTableIds.includes(tableId))) validateMove();
  if (tableIds.some((tableId) => drillingTableIds.includes(tableId))) validate();
}

function validateForTable(tableId) {
  if (completionTableIds.includes(tableId)) {
    validateCompletion();
  } else if (workoverTableIds.includes(tableId)) {
    validateWorkover();
  } else if (moveTableIds.includes(tableId)) {
    validateMove();
  } else {
    validate();
  }
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

async function refreshRecords(reportType) {
  invalidateWellStats(reportType);
  try {
    const response = await fetch(`/api/records?report_type=${encodeURIComponent(reportType)}`);
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || "Records failed");
    recordState[reportType].records = payload.records || [];
    recordState[reportType].records.forEach((record) => {
      if (truthy(record.locked)) lockedRecordIds.add(record.record_id);
    });
  } catch (error) {
    console.error(error);
    recordState[reportType].records = [];
  }
  applyInitialWellSelection(reportType);
  renderRecordDashboard(reportType);
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
  const manualWells = manualWellProfiles.map((profile) => profile.wellbore).filter(Boolean);
  const sourceWells = [...new Set([...(wells.length || manualWells.length ? [] : fallbackWells), ...manualWells, ...wells])];
  const wellList = sortWells(sourceWells, records, state.sortBy).filter((well) => !state.search || well.toLowerCase().includes(state.search.toLowerCase()));
  if (!state.selectedWell || !wellList.includes(state.selectedWell)) state.selectedWell = wellList[0] || "";
  const selectedRecords = records.filter((record) => !state.selectedWell || record.wellbore === state.selectedWell);
  const selectedJobs = jobs.filter((job) => !state.selectedWell || !job.wellbore || job.wellbore === state.selectedWell);
  const monthBase = state.calendarMonth || latestReportDate(selectedRecords) || todayIsoDate();
  const monthRecords = recordsForMonth(selectedRecords, monthBase);
  const uploadedDays = new Set(monthRecords.map((record) => dayOfMonth(record.reportDate)));
  const calendarStages = calendarStageDays(monthRecords);
  const wellStats = cachedWellStats(reportType, state.selectedWell);
  const nptShare = percentage(wellStats.npt_hours, wellStats.total_hours);
  const pShare = percentage(wellStats.p_hours, wellStats.total_hours);
  const scShare = percentage(wellStats.sc_hours, wellStats.total_hours);
  const stageDays = calendarStageDays(selectedRecords);
  const moveDayCount = stageDays.move.size;
  const drillingDayCount = stageDays.drilling.size;
  const tableRecords = sortedRecords(state.selectedDate ? selectedRecords.filter((record) => record.reportDate === state.selectedDate) : selectedRecords);
  const totalTableRows = tableRecords.length + selectedJobs.length;
  const totalPages = Math.max(1, Math.ceil(totalTableRows / RECORDS_PER_PAGE));
  state.page = Math.min(Math.max(Number(state.page) || 1, 1), totalPages);

  host.innerHTML = `
    <div class="record-layout">
      <aside class="well-panel panel">
        <div class="panel-heading">
          <h2>${ui("wellSelection")}</h2>
        </div>
        <input class="well-search" type="search" value="${escapeHtml(state.search)}" placeholder="${ui("searchWell")}" data-well-search="${reportType}" />
        <div class="well-sort-toggle" role="group" aria-label="井排序">
          ${wellSortButton(reportType, state.sortBy, "first", ui("sortFirstUpload"))}
          ${wellSortButton(reportType, state.sortBy, "last", ui("sortLastUpload"))}
          ${wellSortButton(reportType, state.sortBy, "name", ui("sortWellName"))}
        </div>
        <button class="button secondary add-well-button" type="button">${ui("addWell")}</button>
        <div class="well-list">
          ${wellList.map((well, index) => {
            const wellRecords = records.filter((record) => record.wellbore === well);
            const dotTone = wellStatusTone(wellRecords);
            const uploadedCount = uniqueReportDays(wellRecords).size;
            return `
            <button class="well-card ${well === state.selectedWell ? "active" : ""}" type="button" data-well="${escapeHtml(well)}" data-report-type="${reportType}">
              <span class="well-icon">${String(index + 1).padStart(2, "0")}</span>
              <span><strong>${escapeHtml(well)}</strong><small>${ui("uploadedDays")} ${uploadedCount} ${ui("daysUnit")}</small></span>
              ${dotTone ? `<i class="well-status-marker dot-${dotTone}" aria-hidden="true"></i>` : ""}
            </button>
            `;
          }).join("")}
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
            ${calendarMarkup(reportType, monthBase, uploadedDays, calendarStages)}
          </section>
          <section class="panel record-summary-panel">
            ${wellBasicInfoMarkup(reportType, state.selectedWell, selectedRecords)}
            <div class="record-summary-grid">
              ${summaryCard("metricWorkDays", `${uniqueReportDays(selectedRecords).size}`, ui("daysUnit"), "blue")}
              ${summaryCard("metricNptShare", `${formatHours(wellStats.npt_hours)} h`, `${nptShare}`, "red")}
              ${summaryCard("metricPScShare", `P ${pShare}`, `SC ${scShare}`, "green")}
              ${summaryCard("metricMoveDrillingDays", `${moveDayCount} / ${drillingDayCount}`, `搬迁 ${moveDayCount} ${ui("daysUnit")} / 钻井 ${drillingDayCount} ${ui("daysUnit")}`, "violet")}
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
            ${recordTableMarkup(reportType, tableRecords, selectedJobs, state.page)}
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
  const manual = manualProfileForWell(wellbore) || {};
  const latestRecord = sortedRecords(records)[0] || null;
  const stats = cachedWellStats(reportType, wellbore);
  const source = latestRecord ? "日报解析" : manual.wellbore ? "手动创建" : "待上传日报";
  const items = [
    ["井队", stats.rig || latestRecord?.rig || manual.rig || "-"],
    ["AFE", stats.afe_number || latestRecord?.afeNumber || manual.afeNumber || "-"],
    ...wellBasicDateItems(reportType, stats, records),
  ];
  return `
    <section class="well-basic-card" aria-label="当前井基础信息">
      <div class="well-basic-heading">
        <div>
          <span>当前井基础信息</span>
          <strong>${escapeHtml(latestRecord?.wellbore || manual.wellbore || wellbore || "-")}</strong>
        </div>
        <small>${escapeHtml(source)}</small>
      </div>
      <div class="well-basic-grid">
        ${items.map(([label, value]) => `<span><small>${escapeHtml(label)}</small><b>${escapeHtml(value)}</b></span>`).join("")}
      </div>
      ${manual.note ? `<p>${escapeHtml(manual.note)}</p>` : ""}
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

function reportSpan(records) {
  const dates = records.map((record) => record.reportDate).filter(Boolean).sort();
  if (!dates.length) return null;
  return { start: dates[0], end: dates[dates.length - 1] };
}

function hasMissingInSpan(records, span) {
  if (!span) return false;
  const uploaded = new Set(records.map((record) => record.reportDate));
  const cursor = new Date(`${span.start}T00:00:00Z`);
  const end = new Date(`${span.end}T00:00:00Z`);
  while (cursor <= end) {
    const dateStr = cursor.toISOString().slice(0, 10);
    if (!uploaded.has(dateStr)) return true;
    cursor.setUTCDate(cursor.getUTCDate() + 1);
  }
  return false;
}

function wellStatusTone(records) {
  if (!records.length) return "";
  if (hasMissingInSpan(records, reportSpan(records))) return "red";
  if (records.some((record) => record.validation_status === "warning")) return "yellow";
  return "upload";
}

function missingCalendarDays(uploadedDays, monthBase, span) {
  const days = new Set();
  if (!span) return days;
  const base = new Date(`${(monthBase || new Date().toISOString().slice(0, 10)).slice(0, 7)}-01T00:00:00`);
  const year = base.getFullYear();
  const month = base.getMonth();
  const totalDays = new Date(year, month + 1, 0).getDate();
  for (let day = 1; day <= totalDays; day++) {
    const dateStr = `${year}-${String(month + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
    if (dateStr >= span.start && dateStr <= span.end && !uploadedDays.has(day)) days.add(day);
  }
  return days;
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

function reportCompleteness(records, missingDays) {
  const uploadedCount = uniqueReportDays(records).size;
  const warningDays = new Set(records.filter((record) => record.validation_status === "warning").map((record) => record.reportDate).filter(Boolean)).size;
  const expected = uploadedCount + missingDays.size;
  const percent = expected ? Math.max(0, Math.round(((uploadedCount - warningDays * 0.35) / expected) * 100)) : 0;
  return { percent, warningDays };
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

function calendarMarkup(reportType, dateValue, uploadedDays, stageDays) {
  const base = new Date(`${(dateValue || new Date().toISOString().slice(0, 10)).slice(0, 7)}-01T00:00:00`);
  const year = base.getFullYear();
  const month = base.getMonth();
  const firstDay = base.getDay();
  const totalDays = new Date(year, month + 1, 0).getDate();
  const prevTotal = new Date(year, month, 0).getDate();
  const cells = [];
  for (let i = firstDay - 1; i >= 0; i--) cells.push({ day: prevTotal - i, muted: true });
  for (let day = 1; day <= totalDays; day++) cells.push({ day, date: `${year}-${String(month + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}` });
  while (cells.length % 7) cells.push({ day: cells.length - totalDays - firstDay + 1, muted: true });
  return `
    <div class="calendar-grid calendar-weekdays">
      ${["日", "一", "二", "三", "四", "五", "六"].map((day) => `<span>${day}</span>`).join("")}
    </div>
    <div class="calendar-grid calendar-days">
      ${cells.map((cell) => {
        const statusClass = cell.muted
          ? "muted"
          : stageDays.move.has(cell.day)
            ? "has-move"
            : stageDays.drilling.has(cell.day)
              ? "has-drilling"
              : uploadedDays.has(cell.day)
                ? "has-upload"
                : "";
        return `<button type="button" class="${statusClass}" data-calendar-date="${cell.date || ""}" data-report-type="${reportType}" ${cell.muted ? "disabled" : ""}><span>${cell.day}</span></button>`;
      }).join("")}
    </div>
    <div class="calendar-legend"><span class="dot move"></span>Rig Move<span class="dot drilling"></span>Drilling</div>
  `;
}

function recordTableMarkup(reportType, records, jobs = [], page = 1) {
  const rows = [
    ...jobs.map((job) => ({ kind: "job", value: job })),
    ...records.map((record) => ({ kind: "record", value: record })),
  ];
  if (!rows.length) return `<div class="empty-records">${ui("noRecords")}</div>`;
  const totalPages = Math.max(1, Math.ceil(rows.length / RECORDS_PER_PAGE));
  const currentPage = Math.min(Math.max(Number(page) || 1, 1), totalPages);
  const pageRows = rows.slice((currentPage - 1) * RECORDS_PER_PAGE, currentPage * RECORDS_PER_PAGE);
  return `
    <table class="record-table">
      <thead><tr><th>${ui("date")}</th><th>${ui("well")}</th><th>${ui("reportType")}</th><th>${ui("fileName")}</th><th>${ui("uploadTime")}</th><th>${ui("uploader")}</th><th>${ui("status")}</th><th>${ui("operation")}</th></tr></thead>
      <tbody>
        ${pageRows.map((row) => row.kind === "job" ? jobRecordRowMarkup(reportType, row.value) : savedRecordRowMarkup(reportType, row.value)).join("")}
      </tbody>
    </table>
    ${recordPaginationMarkup(reportType, currentPage, totalPages, rows.length)}
  `;
}

function jobRecordRowMarkup(reportType, job) {
  return `
    <tr>
      <td>${escapeHtml(job.reportDate || "-")}</td>
      <td>${escapeHtml(job.wellbore || "识别中")}</td>
      <td><span class="type-pill">${reportName(reportType)}</span></td>
      <td>${escapeHtml(job.fileName)}</td>
      <td>${escapeHtml(formatRecordTime(job.updated_at))}</td>
      <td>${escapeHtml(job.uploader || "本地导入")}</td>
      <td>${jobStatusMarkup(job)}</td>
      <td>${job.recordId ? `<button class="link-button" type="button" data-record-preview="${escapeHtml(job.recordId)}" data-report-type="${reportType}">${ui("preview")}</button>` : "-"}</td>
    </tr>
  `;
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
      <td>${recordStatusMarkup(record)}</td>
      <td><button class="link-button" type="button" data-record-preview="${escapeHtml(record.record_id)}" data-report-type="${reportType}">${ui("preview")}</button></td>
    </tr>
  `;
}

function recordPaginationMarkup(reportType, currentPage, totalPages, totalRows) {
  return `
    <div class="record-pagination">
      <span>${totalRows} ${ui("recordsCount")} / ${ui("page")} ${currentPage} / ${totalPages}</span>
      <div class="record-page-buttons">
        <button class="icon-button" type="button" data-record-page="${currentPage - 1}" data-report-type="${reportType}" ${currentPage <= 1 ? "disabled" : ""} aria-label="${ui("prevPage")}">‹</button>
        <button class="icon-button" type="button" data-record-page="${currentPage + 1}" data-report-type="${reportType}" ${currentPage >= totalPages ? "disabled" : ""} aria-label="${ui("nextPage")}">›</button>
      </div>
    </div>
  `;
}

function analyticsPaginationMarkup(kind, currentPage, totalPages, totalRows) {
  if (totalRows <= ANALYTICS_DETAIL_PAGE_SIZE) return "";
  return `
    <div class="record-pagination analytics-pagination">
      <span>${totalRows} ${ui("recordsCount")} / ${ui("page")} ${currentPage} / ${totalPages}</span>
      <div class="record-page-buttons">
        <button class="icon-button" type="button" data-analytics-page="${currentPage - 1}" data-analytics-kind="${kind}" ${currentPage <= 1 ? "disabled" : ""} aria-label="${ui("prevPage")}">‹</button>
        <button class="icon-button" type="button" data-analytics-page="${currentPage + 1}" data-analytics-kind="${kind}" ${currentPage >= totalPages ? "disabled" : ""} aria-label="${ui("nextPage")}">›</button>
      </div>
    </div>
  `;
}

function analyticsPageSlice(kind, rows) {
  const state = analyticsState[kind];
  const totalPages = Math.max(1, Math.ceil(rows.length / ANALYTICS_DETAIL_PAGE_SIZE));
  const currentPage = Math.min(Math.max(1, Number(state.detailPage) || 1), totalPages);
  state.detailPage = currentPage;
  const start = (currentPage - 1) * ANALYTICS_DETAIL_PAGE_SIZE;
  return {
    pageRows: rows.slice(start, start + ANALYTICS_DETAIL_PAGE_SIZE),
    currentPage,
    totalPages
  };
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
  const warnings = record.validation_warnings || "";
  if (record.validation_status === "warning") {
    return `<span class="status-pill warning" title="${escapeHtml(warnings)}">${ui("warningStatus")}</span>`;
  }
  return `<span class="status-pill uploaded">${ui("uploaded")}</span>`;
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
    if (scopeLabel) scopeLabel.textContent = "项目";
    const projects = (filters.projects || []).map((item) => [item.value, item.label || item.value]);
    setSelectOptions(scopeValue, projects, ui("allProjects"));
  } else {
    if (scopeLabel) scopeLabel.textContent = "井队";
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

function populateProductionProjectFilter(formEl, projects = []) {
  const field = formEl.querySelector("[data-production-project-filter]");
  if (!field) return false;
  const items = productionProjectItems(projects);
  field._productionProjectItems = items;
  const existing = selectedProductionProjectValues(field);
  const validValues = new Set(items.map((item) => item.value));
  let selected = new Set([...existing].filter((value) => validValues.has(value)));
  let defaultApplied = false;
  if (!selected.size && !field.dataset.projectTouched) {
    selected = new Set(items.filter((item) => projectStartYear(item) === String(new Date().getFullYear())).map((item) => item.value));
    defaultApplied = selected.size > 0;
  }
  renderProductionProjectOptions(field, items, selected);
  setProductionProjectSelection(field, selected);
  filterProductionProjectOptions(field);
  return defaultApplied && !existing.size;
}

function populateProductionRigFilter(formEl, rigs = []) {
  const field = formEl.querySelector("[data-production-rig-filter]");
  if (!field) return false;
  const items = productionRigItems(rigs);
  field._productionProjectItems = items;
  field.dataset.valueName = "rig";
  field.dataset.emptyLabel = ui("allRigs");
  field.dataset.selectedUnit = "个井队";
  const existing = selectedProductionProjectValues(field);
  const validValues = new Set(items.map((item) => item.value));
  let selected = new Set([...existing].filter((value) => validValues.has(value)));
  let defaultApplied = false;
  if (!selected.size && !field.dataset.projectTouched) {
    selected = new Set(items.map((item) => item.value));
    defaultApplied = selected.size > 0;
  }
  renderProductionProjectOptions(field, items, selected);
  setProductionProjectSelection(field, selected);
  filterProductionProjectOptions(field);
  return defaultApplied && !existing.size;
}

function productionProjectItems(projects = []) {
  return (projects || []).map((item) => {
    const value = String(item.value || "").trim();
    return {
      value,
      label: projectOptionLabel(item),
      start_date: item.start_date || "",
      end_date: item.end_date || "",
      searchText: [item.label, item.contract_no, item.start_date, item.end_date, value].filter(Boolean).join(" ").toLowerCase(),
    };
  }).filter((item) => item.value).sort((left, right) => {
    const byDate = String(right.start_date || "").localeCompare(String(left.start_date || ""));
    return byDate || left.label.localeCompare(right.label, "zh-Hans-CN", { numeric: true });
  });
}

function productionRigItems(rigs = []) {
  return (rigs || []).map((rig) => String(rig || "").trim()).filter(Boolean).sort((left, right) => {
    return left.localeCompare(right, "zh-Hans-CN", { numeric: true, sensitivity: "base" });
  }).map((rig) => ({
    value: rig,
    label: rig,
    searchText: rig.toLowerCase(),
  }));
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

  if (!state.rigTouched) state.selectedRigs = new Set(rigValues);
  else state.selectedRigs = intersectSelection(state.selectedRigs, rigValues);
  if (!state.projectTouched) state.selectedProjects = new Set(projectValues);
  else state.selectedProjects = intersectSelection(state.selectedProjects, projectValues);

  state.selectionInitialized = true;
  return !wasInitialized && (rigValues.length > 0 || projectValues.length > 0);
}

function intersectSelection(selected, validValues) {
  const valid = new Set(validValues);
  return new Set([...selected].filter((value) => valid.has(value)));
}

function projectStartYear(item = {}) {
  return String(item.start_date || "").slice(0, 4);
}

function selectedProductionProjectValues(field) {
  return new Set([...field.querySelectorAll('input[type="hidden"][name="project"]')].map((input) => input.value).filter(Boolean));
}

function renderProductionProjectOptions(field, items, selected) {
  const host = field.querySelector("[data-project-options]");
  if (!host) return;
  host.innerHTML = items.map((item) => `
    <label class="project-multiselect-option" data-project-option data-project-search-text="${escapeHtml(item.searchText)}">
      <input type="checkbox" value="${escapeHtml(item.value)}" ${selected.has(item.value) ? "checked" : ""} />
      <span>${escapeHtml(item.label)}</span>
    </label>
  `).join("") || `<div class="project-multiselect-empty">暂无项目</div>`;
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
  const completeness = kpis.completeness || {};
  const note = document.querySelector('[data-analytics-note="production"]');
  if (note) note.textContent = ui("analyticsProductionScope");
  document.querySelector('[data-analytics-kpis="production"]').innerHTML = [
    analyticsKpi(ui("kpiRigCount"), kpis.rig_count || 0, ""),
    analyticsKpi(ui("kpiWellCount"), kpis.well_count || 0, ""),
    analyticsKpi(ui("kpiTotalHours"), `${formatHours(kpis.total_hours)} h`, ""),
    analyticsKpi(ui("kpiTotalNpt"), `${formatHours(kpis.npt_hours)} h`, ""),
    analyticsKpi(ui("kpiReportCompleteness"), `${completeness.percent || 0}%`, ui("analyticsCompletenessCaption").replace("{missing}", completeness.missing_days || 0).replace("{warning}", completeness.warning_days || 0)),
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
  if (note) note.textContent = ui("analyticsNptScope");
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

function nptKpiCard(label, value, caption, icon, tone = "neutral") {
  return `
    <div class="analytics-kpi npt-kpi ${escapeHtml(tone)}">
      <div>
        <span>${escapeHtml(label)}</span>
        <strong>${metricValueHtml(value)}</strong>
        <small>${escapeHtml(caption || "")}</small>
      </div>
      <i class="npt-kpi-icon ${escapeHtml(icon)}" aria-hidden="true"></i>
    </div>
  `;
}

function nptRigShare(payload) {
  const totalRigs = new Set((payload.details || []).map((row) => row.rig).filter(Boolean)).size;
  return totalRigs ? Math.round((Number(payload.kpis?.rig_count || 0) / totalRigs) * 1000) / 10 : 0;
}

function nptWellShare(payload) {
  const totalWells = new Set((payload.details || []).map((row) => row.wellbore).filter(Boolean)).size;
  return totalWells ? Math.round((Number(payload.kpis?.well_count || 0) / totalWells) * 1000) / 10 : 0;
}

function nptDeltaCaption(delta, unit = "") {
  const arrow = delta.value > 0 ? "↑" : delta.value < 0 ? "↓" : "→";
  const suffix = unit ? unit : "";
  return `较上期 ${arrow} ${formatHours(Math.abs(delta.value))}${suffix}`;
}

function nptTrendDelta(rows, field) {
  const values = rows.map((row) => Number(row[field] || 0));
  if (values.length < 2) return { value: 0, direction: "neutral" };
  const half = Math.max(1, Math.floor(values.length / 2));
  const previous = values.slice(0, half);
  const current = values.slice(-half);
  const avg = (items) => items.reduce((sum, item) => sum + item, 0) / Math.max(1, items.length);
  const value = avg(current) - avg(previous);
  return { value, direction: value > 0 ? "up" : value < 0 ? "down" : "neutral" };
}

function nptDailyRows(details, monthlyRows = []) {
  const byDate = new Map();
  details.forEach((row) => {
    const key = row.reportDate || "";
    if (!key) return;
    byDate.set(key, (byDate.get(key) || 0) + Number(row.hours || 0));
  });
  const daily = [...byDate.entries()]
    .sort(([left], [right]) => left.localeCompare(right))
    .map(([date, hours]) => ({ label: date.slice(5) || date, hours: Math.round(hours * 100) / 100, share: Math.round((hours / 24) * 1000) / 10 }));
  if (daily.length) return daily;
  return (monthlyRows || []).map((row) => {
    const hours = Number(row.hours || 0);
    return { label: row.month || "", hours, share: Math.round((hours / 24) * 1000) / 10 };
  });
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

function renderStackedBars(selector, rows, series) {
  const host = document.querySelector(selector);
  if (!host) return;
  if (!rows.length) return host.innerHTML = emptyAnalytics();
  const max = Math.max(...rows.map((row) => series.reduce((sum, item) => sum + Number(row[item.key] || 0), 0)), 1);
  host.innerHTML = `<div class="bar-list">${rows.map((row) => {
    const total = series.reduce((sum, item) => sum + Number(row[item.key] || 0), 0);
    return `<div class="bar-row"><span>${escapeHtml(row.rig || row.label)}</span><div class="stack-bar">${series.map((item, index) => `<i style="width:${(Number(row[item.key] || 0) / max) * 100}%;background:${CHART_COLORS[index % CHART_COLORS.length]}"></i>`).join("")}</div><b>${formatHours(total)}</b></div>`;
  }).join("")}</div>${legend(series.map((item) => item.label))}`;
}

function renderSimpleBars(selector, rows) {
  const host = document.querySelector(selector);
  if (!host) return;
  if (!rows.length) return host.innerHTML = emptyAnalytics();
  const max = Math.max(...rows.map((row) => Number(row.hours || 0)), 1);
  host.innerHTML = `<div class="bar-list">${rows.map((row) => `<div class="bar-row"><span>${escapeHtml(row.label)}</span><div class="single-bar"><i style="width:${(Number(row.hours || 0) / max) * 100}%"></i></div><b>${formatHours(row.hours)}</b></div>`).join("")}</div>`;
}

function renderProductionNptRanking(selector, rows) {
  const host = document.querySelector(selector);
  if (!host) return;
  const usable = [...(rows || [])].filter((row) => Number(row.hours || 0) > 0)
    .sort((left, right) => Number(right.hours || 0) - Number(left.hours || 0));
  if (!usable.length) return host.innerHTML = emptyAnalytics();
  const max = Math.max(...usable.map((row) => Number(row.hours || 0)), 1);
  host.innerHTML = `
    <div class="production-npt-ranking">
      ${usable.map((row, index) => {
        const width = Math.max(4, (Number(row.hours || 0) / max) * 100);
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
    <div class="production-npt-ranking-caption"><i></i>累计NPT时长 (h)</div>
  `;
}

function renderNptRigBars(selector, rows) {
  const host = document.querySelector(selector);
  if (!host) return;
  if (!rows.length) return host.innerHTML = emptyAnalytics();
  const sorted = [...rows].sort((left, right) => Number(right.hours || 0) - Number(left.hours || 0)).slice(0, 6);
  const max = Math.max(...sorted.map((row) => Number(row.hours || 0)), 1);
  host.innerHTML = `
    <div class="npt-horizontal-chart">
      ${sorted.map((row) => {
        const width = Math.max(4, (Number(row.hours || 0) / max) * 100);
        return `
          <div class="npt-horizontal-row">
            <span>${escapeHtml(row.label || "-")}</span>
            <div class="npt-horizontal-track"><i style="width:${width}%"></i></div>
            <b>${formatHours(row.hours)}</b>
          </div>
        `;
      }).join("")}
      <div class="npt-axis"><span>0</span><span>20</span><span>40</span><span>60</span><span>80</span><span>100</span></div>
    </div>
    <div class="npt-chart-caption"><i></i>NPT时长 (h)</div>
  `;
}

function renderNptReasonDonut(selector, rows, totalNpt) {
  const host = document.querySelector(selector);
  if (!host) return;
  const usable = (rows || []).filter((row) => Number(row.hours || 0) > 0);
  if (!usable.length) return host.innerHTML = emptyAnalytics();
  const total = totalNpt || usable.reduce((sum, row) => sum + Number(row.hours || 0), 0);
  let offset = 25;
  const radius = 15.9;
  const circles = usable.map((row, index) => {
    const value = Number(row.hours || 0);
    const dash = (value / total) * 100;
    const circle = `<circle r="${radius}" cx="20" cy="20" fill="transparent" stroke="${CHART_COLORS[index % CHART_COLORS.length]}" stroke-width="7" stroke-dasharray="${dash} ${100 - dash}" stroke-dashoffset="${-offset}" />`;
    offset += dash;
    return circle;
  }).join("");
  host.innerHTML = `
    <div class="npt-donut-layout">
      <div class="npt-donut-stage">
        <svg viewBox="0 0 40 40" class="npt-donut" role="img" aria-label="NPT原因分布">${circles}</svg>
        <div class="npt-donut-center"><strong>${formatHours(total)}</strong><span>总NPT时长</span></div>
      </div>
      <div class="npt-donut-list">
        ${usable.slice(0, 7).map((row, index) => `
          <span><i style="background:${CHART_COLORS[index % CHART_COLORS.length]}"></i>${escapeHtml(reasonLabel(row.label))} ${Number(row.share || ((Number(row.hours || 0) / total) * 100)).toFixed(1)}% (${formatHours(row.hours)} h)</span>
        `).join("")}
      </div>
    </div>
  `;
}

function renderNptWellRanking(selector, rows, totalNpt) {
  const host = document.querySelector(selector);
  if (!host) return;
  const rankedRows = [...(rows || [])].sort((left, right) => Number(right.hours || 0) - Number(left.hours || 0));
  if (!rankedRows.length) return host.innerHTML = emptyAnalytics();
  const total = totalNpt || rankedRows.reduce((sum, row) => sum + Number(row.hours || 0), 0);
  host.innerHTML = `
    <div class="npt-ranking-scroll">
      <table class="npt-ranking-table">
        <thead><tr><th>排名</th><th>井号</th><th>NPT时长(h)</th><th>占比</th></tr></thead>
        <tbody>
          ${rankedRows.map((row, index) => `
            <tr>
              <td><span class="npt-rank-medal rank-${index + 1}">${index + 1}</span></td>
              <td>${escapeHtml(row.label || "-")}</td>
              <td>${formatHours(row.hours)}</td>
              <td>${total ? ((Number(row.hours || 0) / total) * 100).toFixed(1) : "0.0"}%</td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    </div>
  `;
}

function renderNptLineChart(selector, rows, field, unit) {
  const host = document.querySelector(selector);
  if (!host) return;
  const usable = (rows || []).filter((row) => row.label);
  if (!usable.length) return host.innerHTML = emptyAnalytics();
  const width = 620, height = 190, padX = 34, padY = 24;
  const max = Math.max(...usable.map((row) => Number(row[field] || 0)), 1);
  const step = usable.length > 1 ? (width - padX * 2) / (usable.length - 1) : 0;
  const points = usable.map((row, index) => {
    const x = padX + index * step;
    const y = height - padY - (Number(row[field] || 0) / max) * (height - padY * 2);
    return { x, y, row };
  });
  const polyline = points.map((point) => `${point.x},${point.y}`).join(" ");
  const area = `${padX},${height - padY} ${polyline} ${padX + (usable.length - 1) * step},${height - padY}`;
  const yTicks = [0, 0.33, 0.66, 1].map((ratio) => {
    const y = height - padY - ratio * (height - padY * 2);
    const label = Math.round(max * ratio * 10) / 10;
    return `<line x1="${padX}" y1="${y}" x2="${width - padX}" y2="${y}" /><text x="6" y="${y + 4}">${label}${unit}</text>`;
  }).join("");
  const labelEvery = Math.max(1, Math.ceil(usable.length / 6));
  const labels = points.map((point, index) => index % labelEvery === 0 || index === points.length - 1 ? `<text x="${point.x}" y="${height - 5}" text-anchor="middle">${escapeHtml(point.row.label)}</text>` : "").join("");
  host.innerHTML = `
    <svg class="npt-line-chart" viewBox="0 0 ${width} ${height}" role="img">
      <g class="npt-line-grid">${yTicks}</g>
      <polygon points="${area}" class="npt-line-area"></polygon>
      <polyline points="${polyline}" class="npt-line-path"></polyline>
      ${points.map((point) => `<circle cx="${point.x}" cy="${point.y}" r="3.5" class="npt-line-dot"><title>${escapeHtml(point.row.label)} ${formatHours(point.row[field])}${unit}</title></circle>`).join("")}
      <g class="npt-line-labels">${labels}</g>
    </svg>
    <div class="npt-chart-caption"><i></i>${unit === "%" ? "日均NPT占比 (%)" : "NPT时长 (h)"}</div>
  `;
}

function renderNptPendingList(selector, details) {
  const host = document.querySelector(selector);
  if (!host) return;
  const grouped = new Map();
  (details || []).forEach((row) => {
    const key = `${row.rig || ""}__${row.wellbore || ""}`;
    if (!row.wellbore) return;
    const item = grouped.get(key) || { rig: row.rig || "", wellbore: row.wellbore || "", lastDate: "", hours: 0, eventCount: 0 };
    item.hours += Number(row.hours || 0);
    item.eventCount += 1;
    if (!item.lastDate || String(row.reportDate || "").localeCompare(item.lastDate) > 0) item.lastDate = row.reportDate || "";
    grouped.set(key, item);
  });
  const rows = [...grouped.values()].sort((left, right) => Number(right.hours || 0) - Number(left.hours || 0)).slice(0, 4);
  const badge = document.querySelector("[data-npt-pending-count]");
  if (badge) badge.textContent = String(rows.length);
  if (!rows.length) return host.innerHTML = emptyAnalytics();
  host.innerHTML = `
    <table class="npt-pending-table">
      <thead><tr><th>井号</th><th>最近NPT事件</th><th>NPT时长(h)</th><th>操作</th></tr></thead>
      <tbody>
        ${rows.map((row) => `
          <tr>
            <td>${escapeHtml(row.wellbore)}</td>
            <td>${escapeHtml(row.lastDate || "-")}</td>
            <td>${formatHours(row.hours)}</td>
            <td><button class="link-button npt-confirm-link" type="button" data-npt-confirm-shortcut="${escapeHtml(row.wellbore)}" data-rig="${escapeHtml(row.rig)}">确认 ›</button></td>
          </tr>
        `).join("")}
      </tbody>
    </table>
    <button class="link-button npt-view-all-pending" type="button" data-menu-target="rig-npt-ranking">查看全部 →</button>
  `;
}

function renderTrendBars(selector, rows) {
  const host = document.querySelector(selector);
  if (!host) return;
  if (!rows.length) return host.innerHTML = emptyAnalytics();
  const max = Math.max(...rows.map((row) => Number(row.hours || 0)), 1);
  host.innerHTML = `<div class="trend-bars">${rows.map((row) => `<div><i style="height:${Math.max(4, (Number(row.hours || 0) / max) * 130)}px"></i><strong>${formatHours(row.hours)}</strong><span>${escapeHtml(row.month)}</span></div>`).join("")}</div>`;
}

function renderLineChart(selector, rows, series) {
  const host = document.querySelector(selector);
  if (!host) return;
  if (!rows.length) return host.innerHTML = emptyAnalytics();
  const max = Math.max(...rows.flatMap((row) => series.map((item) => Number(row[item.key] || 0))), 1);
  const width = 760, height = 180, pad = 28;
  const step = rows.length > 1 ? (width - pad * 2) / (rows.length - 1) : 0;
  const lines = series.map((item, index) => {
    const points = rows.map((row, rowIndex) => {
      const x = pad + rowIndex * step;
      const y = height - pad - (Number(row[item.key] || 0) / max) * (height - pad * 2);
      return `${x},${y}`;
    }).join(" ");
    return `<polyline points="${points}" fill="none" stroke="${CHART_COLORS[index % CHART_COLORS.length]}" stroke-width="3" />`;
  }).join("");
  const labels = rows.map((row, index) => `<text x="${pad + index * step}" y="${height - 6}" text-anchor="middle">${escapeHtml(row.month)}</text>`).join("");
  host.innerHTML = `<svg class="line-chart" viewBox="0 0 ${width} ${height}" role="img">${lines}${labels}</svg>${legend(series.map((item) => item.label))}`;
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
    analyticsSortHeader("npt", "hours", ui("tableNptHours")),
    analyticsSortHeader("npt", "reason", "NPT描述关键词"),
    `<th>${escapeHtml("备注（NPT描述）")}</th>`
  ].filter(Boolean).join("");
  host.innerHTML = `<table class="record-table analytics-table npt-detail-table-lite npt-report-table ${showRig ? "npt-show-rig" : ""}"><thead><tr>${headers}</tr></thead><tbody>${pageRows.map((row) => {
    const rigCell = showRig ? `<td>${escapeHtml(row.rig || "-")}</td>` : "";
    const projectName = row.project_name || row.contract_project || "-";
    const keyword = row.op_sub || row.op_code || reasonLabel(row.reason) || "-";
    const description = row.operation_details || "-";
    return `<tr data-open-record="${escapeHtml(row.record_id)}" data-report-type="${escapeHtml(row.report_type)}"><td>${escapeHtml(row.wellbore || "-")}</td>${rigCell}<td>${escapeHtml(projectName)}</td><td>${escapeHtml(row.reportDate || "-")}</td><td>${formatHours(row.hours)}</td><td>${escapeHtml(keyword)}</td><td class="npt-report-description"><button type="button" class="npt-report-description-button" data-npt-description="${escapeHtml(description)}">${escapeHtml(description)}</button></td></tr>`;
  }).join("")}</tbody></table>${analyticsPaginationMarkup("npt", currentPage, totalPages, rows.length)}`;
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
    .filter(({ row }) => !onlyScNpt || ["SC", "NPT"].includes(String(row.confirmed_op_type || row.system_op_type || "").toUpperCase()));
  if (!visibleRows.length) {
    rowsHost.innerHTML = `<tr><td colspan="6">当前没有 SC 或 NPT 时效。</td></tr>`;
    return;
  }
  rowsHost.innerHTML = visibleRows.map(({ row, index }) => `
    <tr data-npt-row="${index}">
      <td>${escapeHtml((row.reportDate || "").slice(5) || "-")}</td>
      <td>${escapeHtml(row.from || "-")} ~ ${escapeHtml(row.to || "-")}</td>
      <td class="npt-description-cell"><button type="button" class="npt-description-preview" data-npt-description="${escapeHtml(row.operation_details || row.op_sub || row.op_code || "-")}">${escapeHtml(row.operation_details || row.op_sub || row.op_code || "-")}</button></td>
      <td>${opTypePill(row.system_op_type)}</td>
      <td>
        <select data-npt-confirm-type ${locked ? "disabled" : ""}>
          ${["P", "SC", "NPT"].map((type) => `<option value="${type}" ${type === String(row.confirmed_op_type || row.system_op_type).toUpperCase() ? "selected" : ""}>${type}</option>`).join("")}
        </select>
      </td>
      <td>${formatHours(row.hours)}</td>
    </tr>
  `).join("");
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
  popover.textContent = text;
  document.body.appendChild(popover);
  const width = Math.min(720, Math.max(420, window.innerWidth - 48));
  const left = Math.min(Math.max(24, rect.left), window.innerWidth - width - 24);
  const top = Math.min(rect.bottom + 8, window.innerHeight - 260);
  popover.style.width = `${width}px`;
  popover.style.left = `${left}px`;
  popover.style.top = `${Math.max(24, top)}px`;
}

function collectNptConfirmationRows() {
  const rows = nptConfirmState.detail?.operations || [];
  document.querySelectorAll("[data-npt-detail-rows] tr").forEach((tr) => {
    const index = Number(tr.dataset.nptRow);
    if (!rows[index]) return;
    rows[index].confirmed_op_type = tr.querySelector("[data-npt-confirm-type]")?.value || rows[index].confirmed_op_type;
  });
  return rows;
}

async function saveNptConfirmation(submit = false) {
  const detail = nptConfirmState.detail;
  if (!detail) return;
  const meta = detail.meta || {};
  const operations = collectNptConfirmationRows();
  const note = document.querySelector('[name="nptConfirmNote"]')?.value || "";
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

function productionReportExportColumns() {
  const showRig = analyticsState.productionReport.activeTab === "project";
  return [
    { key: "wellbore", label: ui("tableWell") },
    showRig ? { key: "rig", label: ui("tableRig") } : null,
    { key: "contract_project", label: ui("tableContractProject"), fallback: "project_name" },
    { key: "move_date", label: ui("tableMoveDate") },
    { key: "drilling_start_date", label: ui("tableDrillingStartDate") },
    { key: "drilling_finish_date", label: ui("tableDrillingFinishDate") },
    { key: "completion_date", label: ui("tableCompletionDate") },
    { key: "workover_date", label: ui("tableWorkoverDate") },
    { key: "move_hours", label: ui("tableMoveHours"), hours: true },
    { key: "drilling_hours", label: ui("tableDrillingHours"), hours: true },
    { key: "completion_hours", label: ui("tableCompletionHours"), hours: true },
    { key: "workover_hours", label: ui("tableWorkoverHours"), hours: true },
    { key: "npt_hours", label: ui("tableNptHours"), hours: true },
    { key: "remarks", label: ui("tableRemarks") },
  ].filter(Boolean);
}

function productionReportExportValue(row, column) {
  if (column.hours) return formatHours(row[column.key]);
  return row[column.key] ?? (column.fallback ? row[column.fallback] : "") ?? "";
}

function excelCellHtml(value) {
  const text = String(value ?? "");
  const safeText = /^[=+\-@]/.test(text) ? `'${text}` : text;
  return escapeHtml(safeText);
}

function downloadProductionReportExcel(rows) {
  const columns = productionReportExportColumns();
  const state = analyticsState.productionReport;
  const tabLabel = state.activeTab === "project" ? "按项目" : "按钻井队";
  const today = new Date().toISOString().slice(0, 10);
  const headerHtml = columns.map((column) => `<th>${excelCellHtml(column.label)}</th>`).join("");
  const bodyHtml = rows.map((row) => `<tr>${columns.map((column) => `<td>${excelCellHtml(productionReportExportValue(row, column))}</td>`).join("")}</tr>`).join("");
  const html = `<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <style>
    table { border-collapse: collapse; font-family: Arial, sans-serif; font-size: 12px; }
    th, td { border: 1px solid #9fb4c8; padding: 6px 8px; mso-number-format:"\\@"; }
    th { background: #0b4d7a; color: #ffffff; font-weight: 700; }
  </style>
</head>
<body>
  <table>
    <thead><tr>${headerHtml}</tr></thead>
    <tbody>${bodyHtml}</tbody>
  </table>
</body>
</html>`;
  const blob = new Blob(["\ufeff", html], { type: "application/vnd.ms-excel;charset=utf-8" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = `生产报表-${tabLabel}-${today}.xls`;
  link.style.display = "none";
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(link.href);
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
  const response = await fetch(path, {
    credentials: "same-origin",
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.error || "后台请求失败");
  return payload;
}

async function loadAdminSession() {
  try {
    const payload = await adminRequest("/api/admin/session");
    adminState.authenticated = payload.authenticated;
    adminState.user = payload.user || null;
    adminState.permissions = payload.permissions || {};
    renderAdminShell();
    if (adminState.authenticated && adminState.permissions.admin) await loadAdminData();
  } catch (error) {
    console.error(error);
    renderAdminShell();
  }
}

async function loadAdminData() {
  try {
    const [users, config, dataStatus, logs] = await Promise.all([
      adminRequest("/api/admin/users"),
      adminRequest("/api/admin/config"),
      adminRequest("/api/admin/data-status"),
      adminRequest("/api/admin/audit-logs"),
    ]);
    adminState.users = users.users || [];
    adminState.roles = users.roles || [];
    adminState.config = config.config || {};
    adminState.dataStatus = dataStatus;
    adminState.logs = logs.logs || [];
    renderAdminPanels();
  } catch (error) {
    showToast(error.message);
  }
}

function renderAdminShell() {
  const loginPanel = document.querySelector("[data-admin-login]");
  const consolePanel = document.querySelector("[data-admin-console]");
  const logoutButton = document.querySelector("[data-admin-logout]");
  if (!loginPanel || !consolePanel || !logoutButton) return;
  loginPanel.hidden = adminState.authenticated;
  consolePanel.hidden = !adminState.authenticated;
  logoutButton.hidden = !adminState.authenticated;
  if (adminState.authenticated && !adminState.permissions.admin) {
    consolePanel.querySelector(".admin-tabs")?.setAttribute("hidden", "");
    consolePanel.querySelector('[data-admin-panel="overview"]').hidden = false;
    consolePanel.querySelector('[data-admin-panel="overview"]').innerHTML = `<section class="panel"><div class="panel-heading"><h2>无后台权限</h2><span class="panel-note">当前账号可以登录，但没有系统后台管理权限。</span></div></section>`;
    consolePanel.querySelectorAll('[data-admin-panel]:not([data-admin-panel="overview"])').forEach((panel) => panel.hidden = true);
    return;
  }
  consolePanel.querySelector(".admin-tabs")?.removeAttribute("hidden");
  if (adminState.authenticated) renderAdminPanels();
}

function renderAdminPanels() {
  renderAdminOverview();
  renderAdminUsers();
  renderAdminRoles();
  renderAdminConfig();
  renderAdminData();
  renderAdminLogs();
  switchAdminTab(adminState.tab || "overview");
}

function renderAdminOverview() {
  const host = document.querySelector('[data-admin-panel="overview"]');
  if (!host) return;
  const status = adminState.dataStatus || {};
  const user = adminState.user || {};
  host.innerHTML = `
    <section class="admin-kpi-grid">
      ${adminKpi("当前账号", user.display_name || user.username || "-", user.role || "")}
      ${adminKpi("日报记录", status.records || 0, "Excel库记录数")}
      ${adminKpi("源PDF", status.source_pdf_count || 0, "本地保存数量")}
      ${adminKpi("库文件", fileSize(status.database_size || 0), status.database_updated_at || "未生成")}
    </section>
    <section class="panel">
      <div class="panel-heading"><h2>后台范围</h2><span class="panel-note">轻量 JSON 配置，适合单机或小团队部署</span></div>
      <div class="admin-note-grid">
        <span>账号与角色</span><span>配置项</span><span>Excel备份</span><span>操作日志</span>
      </div>
    </section>
  `;
}

function adminKpi(label, value, caption) {
  return `<div class="analytics-kpi"><span>${escapeHtml(label)}</span><strong>${escapeHtml(value)}</strong><small>${escapeHtml(caption || "")}</small></div>`;
}

function renderAdminUsers() {
  const host = document.querySelector('[data-admin-panel="users"]');
  if (!host) return;
  const roles = adminState.roles || [];
  host.innerHTML = `
    <section class="panel">
      <div class="panel-heading"><h2>账号管理</h2><span class="panel-note">新增账号、分配角色、启停账号</span></div>
      <div class="admin-user-form">
        <label>用户名<input name="adminUserUsername" placeholder="username" /></label>
        <label>姓名<input name="adminUserDisplay" placeholder="显示姓名" /></label>
        <label>邮箱<input name="adminUserEmail" placeholder="name@company.com" /></label>
        <label>角色<select name="adminUserRole">${roles.map((role) => `<option value="${escapeHtml(role.value)}">${escapeHtml(role.label)}</option>`).join("")}</select></label>
        <label>状态<select name="adminUserStatus"><option value="active">启用</option><option value="disabled">停用</option></select></label>
        <label>密码<input name="adminUserPassword" type="password" placeholder="新账号必填，留空不改" /></label>
        <button class="button" type="button" data-admin-save-user>保存账号</button>
      </div>
      <div class="table-wrap">
        <table class="record-table admin-table">
          <thead><tr><th>用户名</th><th>姓名</th><th>邮箱</th><th>角色</th><th>状态</th><th>最后登录</th><th>操作</th></tr></thead>
          <tbody>${(adminState.users || []).map((user) => `<tr><td>${escapeHtml(user.username)}</td><td>${escapeHtml(user.display_name)}</td><td>${escapeHtml(user.email)}</td><td>${escapeHtml(roleLabel(user.role))}</td><td>${escapeHtml(user.status)}</td><td>${escapeHtml(user.last_login)}</td><td><button class="link-button" type="button" data-admin-edit-user="${escapeHtml(user.username)}">填入</button></td></tr>`).join("")}</tbody>
        </table>
      </div>
    </section>
  `;
}

function renderAdminRoles() {
  const host = document.querySelector('[data-admin-panel="roles"]');
  if (!host) return;
  const actions = [["view", "查看"], ["import", "导入"], ["edit", "编辑"], ["save", "保存"], ["export", "导出"], ["admin", "后台"]];
  host.innerHTML = `
    <section class="panel">
      <div class="panel-heading"><h2>角色权限</h2><span class="panel-note">第一版固定四类角色，减少维护复杂度</span></div>
      <div class="table-wrap">
        <table class="record-table admin-table">
          <thead><tr><th>角色</th>${actions.map(([, label]) => `<th>${label}</th>`).join("")}</tr></thead>
          <tbody>${(adminState.roles || []).map((role) => `<tr><td>${escapeHtml(role.label)}</td>${actions.map(([key]) => `<td>${role.permissions?.[key] ? "✓" : "—"}</td>`).join("")}</tr>`).join("")}</tbody>
        </table>
      </div>
    </section>
  `;
}

function renderAdminConfig() {
  const host = document.querySelector('[data-admin-panel="config"]');
  if (!host) return;
  const config = adminState.config || {};
  host.innerHTML = `
    <section class="panel">
      <div class="panel-heading"><h2>系统配置</h2><span class="panel-note">保存基础配置和日报运行参数</span></div>
      <div class="admin-config-grid">
        <label>系统名称<input name="system_name" value="${escapeHtml(config.system_name)}" /></label>
        <label>默认语言<select name="default_language"><option value="zh">中文</option><option value="en">EN</option><option value="es">ES</option></select></label>
        <label>每页记录数<input name="records_per_page" type="number" min="5" max="100" value="${escapeHtml(config.records_per_page)}" /></label>
        <label>Excel路径<input name="excel_path" value="${escapeHtml(config.excel_path)}" /></label>
        <label>源PDF保存<select name="save_source_pdf"><option value="true">开启</option><option value="false">关闭</option></select></label>
        <label>PDF保留天数<input name="source_pdf_retention_days" type="number" min="1" value="${escapeHtml(config.source_pdf_retention_days)}" /></label>
      </div>
      <div class="admin-actions"><button class="button" type="button" data-admin-save-config>保存配置</button></div>
    </section>
  `;
  const form = host.querySelector(".admin-config-grid");
  form.querySelector('[name="default_language"]').value = config.default_language || "zh";
  form.querySelector('[name="save_source_pdf"]').value = String(config.save_source_pdf !== false);
}

function renderAdminData() {
  const host = document.querySelector('[data-admin-panel="data"]');
  if (!host) return;
  const status = adminState.dataStatus || {};
  const byType = status.by_type || {};
  host.innerHTML = `
    <section class="admin-kpi-grid">
      ${adminKpi("总记录", status.records || 0, "全部日报")}
      ${adminKpi("钻井", byType.drilling || 0, "drilling")}
      ${adminKpi("完井", byType.completion || 0, "completion")}
      ${adminKpi("修井/搬迁", `${byType.workover || 0} / ${byType.move || 0}`, "workover / move")}
    </section>
    <section class="panel">
      <div class="panel-heading"><h2>数据维护</h2><span class="panel-note">备份当前 Excel 库，查看最近备份</span></div>
      <div class="admin-actions">
        <a class="button secondary" href="/api/download-database">下载Excel库</a>
        <button class="button" type="button" data-admin-backup>立即备份</button>
      </div>
      <div class="table-wrap">
        <table class="record-table admin-table">
          <thead><tr><th>备份文件</th><th>大小</th><th>时间</th></tr></thead>
          <tbody>${(status.backups || []).map((item) => `<tr><td>${escapeHtml(item.name)}</td><td>${fileSize(item.size)}</td><td>${escapeHtml(item.created_at)}</td></tr>`).join("") || `<tr><td colspan="3">暂无备份</td></tr>`}</tbody>
        </table>
      </div>
    </section>
  `;
}

function renderAdminLogs() {
  const host = document.querySelector('[data-admin-panel="logs"]');
  if (!host) return;
  host.innerHTML = `
    <section class="panel">
      <div class="panel-heading"><h2>日志审计</h2><span class="panel-note">最近 120 条后台操作</span></div>
      <div class="table-wrap">
        <table class="record-table admin-table">
          <thead><tr><th>时间</th><th>用户</th><th>动作</th><th>模块</th><th>对象</th><th>结果</th><th>备注</th></tr></thead>
          <tbody>${(adminState.logs || []).map((log) => `<tr><td>${escapeHtml(log.time)}</td><td>${escapeHtml(log.user)}</td><td>${escapeHtml(log.action)}</td><td>${escapeHtml(log.module)}</td><td>${escapeHtml(log.target)}</td><td>${escapeHtml(log.result)}</td><td>${escapeHtml(log.note)}</td></tr>`).join("") || `<tr><td colspan="7">暂无日志</td></tr>`}</tbody>
        </table>
      </div>
    </section>
  `;
}

function switchAdminTab(tab) {
  adminState.tab = tab;
  document.querySelectorAll("[data-admin-tab]").forEach((button) => button.classList.toggle("active", button.dataset.adminTab === tab));
  document.querySelectorAll("[data-admin-panel]").forEach((panel) => panel.hidden = panel.dataset.adminPanel !== tab);
}

function roleLabel(value) {
  return (adminState.roles || []).find((role) => role.value === value)?.label || value || "-";
}

function fileSize(value) {
  const size = Number(value) || 0;
  if (size > 1024 * 1024) return `${(size / 1024 / 1024).toFixed(1)} MB`;
  if (size > 1024) return `${(size / 1024).toFixed(1)} KB`;
  return `${size} B`;
}

async function loginAdmin() {
  const username = document.querySelector('[name="adminUsername"]')?.value.trim() || "";
  const password = document.querySelector('[name="adminPassword"]')?.value || "";
  try {
    const payload = await adminRequest("/api/admin/login", { method: "POST", body: JSON.stringify({ username, password }) });
    adminState.authenticated = true;
    adminState.user = payload.user;
    adminState.permissions = payload.permissions || {};
    showToast("后台登录成功");
    renderAdminShell();
    if (adminState.permissions.admin) await loadAdminData();
  } catch (error) {
    showToast(error.message);
  }
}

async function logoutAdmin() {
  try {
    await adminRequest("/api/admin/logout", { method: "POST", body: "{}" });
  } catch (error) {
    console.error(error);
  }
  adminState.authenticated = false;
  adminState.user = null;
  adminState.users = [];
  showToast("已退出后台");
  renderAdminShell();
}

function fillAdminUserForm(username) {
  const user = (adminState.users || []).find((item) => item.username === username);
  if (!user) return;
  document.querySelector('[name="adminUserUsername"]').value = user.username || "";
  document.querySelector('[name="adminUserDisplay"]').value = user.display_name || "";
  document.querySelector('[name="adminUserEmail"]').value = user.email || "";
  document.querySelector('[name="adminUserRole"]').value = user.role || "viewer";
  document.querySelector('[name="adminUserStatus"]').value = user.status || "active";
  document.querySelector('[name="adminUserPassword"]').value = "";
}

async function saveAdminUser() {
  const payload = {
    username: document.querySelector('[name="adminUserUsername"]')?.value.trim(),
    display_name: document.querySelector('[name="adminUserDisplay"]')?.value.trim(),
    email: document.querySelector('[name="adminUserEmail"]')?.value.trim(),
    role: document.querySelector('[name="adminUserRole"]')?.value,
    status: document.querySelector('[name="adminUserStatus"]')?.value,
    password: document.querySelector('[name="adminUserPassword"]')?.value,
  };
  try {
    const response = await adminRequest("/api/admin/users", { method: "POST", body: JSON.stringify(payload) });
    adminState.users = response.users || [];
    showToast("账号已保存");
    renderAdminUsers();
  } catch (error) {
    showToast(error.message);
  }
}

async function saveAdminConfig() {
  const host = document.querySelector('[data-admin-panel="config"]');
  if (!host) return;
  const payload = {};
  host.querySelectorAll("[name]").forEach((control) => {
    let value = control.value;
    if (control.type === "number") value = Number(value);
    if (control.name === "save_source_pdf") value = value === "true";
    payload[control.name] = value;
  });
  try {
    const response = await adminRequest("/api/admin/config", { method: "POST", body: JSON.stringify(payload) });
    adminState.config = response.config || {};
    showToast("配置已保存");
    renderAdminConfig();
  } catch (error) {
    showToast(error.message);
  }
}

async function backupAdminDatabase() {
  try {
    await adminRequest("/api/admin/backup", { method: "POST", body: "{}" });
    showToast("Excel库已备份");
    const status = await adminRequest("/api/admin/data-status");
    adminState.dataStatus = status;
    renderAdminData();
    renderAdminOverview();
  } catch (error) {
    showToast(error.message);
  }
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
  normalized.lastCasing = joinAt(normalized.lastCasingSize, normalized.lastCasingDepth);
  normalized.nextCasing = joinAt(normalized.nextCasingSize, normalized.nextCasingDepth);
  normalized.mudTimeMd = joinSlash(normalized.mudTime, normalized.mudMd);
  normalized.pvYp = joinSlash(normalized.pv, normalized.yp);
  normalized.gels = joinSlash(normalized.gel10s, normalized.gel10m, normalized.gel30m);
  normalized.oilWater = joinSlash(normalized.oilPercent, normalized.waterPercent);
  return normalized;
}

function applyReportFields(fields = {}, targetForm = form) {
  const expanded = expandLegacyFields(fields);
  Object.entries(expanded).forEach(([name, value]) => {
    if (targetForm.elements[name]) targetForm.elements[name].value = value ?? "";
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

function markIssues(formEl, issues) {
  issues.forEach((issue) => {
    const className = issue.level === "warning" ? "warning-cell" : "invalid";
    if (issue.field && formEl?.elements?.[issue.field]) {
      const controls = formEl.elements[issue.field];
      if (controls.classList) {
        controls.classList.add(className);
      } else if (typeof controls.length === "number") {
        Array.from(controls).forEach((control) => control.classList?.add(className));
      }
    }
    if (issue.tableId && Number.isInteger(issue.rowIndex) && issue.field) {
      const row = document.querySelectorAll(`#${issue.tableId} tbody tr`)[issue.rowIndex];
      const control = row?.querySelector(`[name='${issue.field}']`);
      if (control) control.classList.add(className);
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

function validateOperationsTable(issues, tableId, rows, validTypes, typeMessageKey) {
  const stats = operationStats(rows);
  if (!rows.length) {
    pushIssue(issues, { level: "error", text: message("operationMissingTable") });
    return stats;
  }
  const clockHoursByRow = operationClockHoursByRow(rows);
  if (Math.abs(stats.total - 24) > 0.05) {
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

function validateNonNegativeRows(issues, tableId, rows, fields) {
  rows.forEach((row, index) => {
    fields.forEach((field) => {
      const value = toNumber(row[field]);
      if (Number.isFinite(value) && value < 0) {
        pushIssue(issues, { level: "error", text: message("negativeValue", { row: index + 1, field }), tableId, rowIndex: index, field });
      }
    });
  });
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
      daily_costs: readTable("costTable"),
      bulks: readTable("bulkTable")
    }),
    completion: () => ({
      metadata: { report_type: "completion", record_id: currentRecordIds.completion },
      report_fields: formData(completionForm),
      operations: readTable("completionOperationsTable"),
      bulks: readTable("completionBulkTable"),
      daily_costs: readTable("completionCostTable"),
      perforation_intervals: readTable("perforationIntervalsTable")
    }),
    workover: () => ({
      metadata: { report_type: "workover", record_id: currentRecordIds.workover },
      report_fields: formData(workoverForm),
      operations: readTable("workoverOperationsTable"),
      bulks: readTable("workoverBulkTable"),
      daily_costs: readTable("workoverCostTable"),
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
  if (reportContentState[reportType]?.mode === "translated") {
    button.disabled = true;
    return;
  }
  const currentSignature = reportSignature(reportType);
  button.disabled = isCurrentReportLocked(reportType) || !currentSignature || currentSignature === savedReportSignatures[reportType];
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
  if (reportContentState[reportType]?.mode === "translated") {
    showToast(ui("translationPreviewNotice"));
    return;
  }
  if (isCurrentReportLocked(reportType)) {
    showToast("该日报已被NPT确认锁定，不能再修改保存。");
    return;
  }
  updateSaveButton(reportType);
  const button = document.querySelector(`[data-save-report="${reportType}"]`);
  if (button?.disabled) return;
  const payload = reportPayload(reportType);
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
    job.warning = payload.metadata?.validation_status === "warning";
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

async function importPdfFile(file) {
  return importReportFiles("drilling", file ? [file] : []);
}

async function importCompletionPdfFile(file) {
  return importReportFiles("completion", file ? [file] : []);
}

async function importWorkoverPdfFile(file) {
  return importReportFiles("workover", file ? [file] : []);
}

async function importMovePdfFile(file) {
  return importReportFiles("move", file ? [file] : []);
}

function validate() {
  const data = normalizedReportFields(formData());
  const issues = [];
  const required = ["event", "reportDate", "reportNo", "wellbore", "rig", "todayMd", "progress", "currentOps", "summary24h", "forecast24h", "mudType", "mudDensity"];
  document.querySelectorAll("#drillingDailyPage .invalid, #drillingDailyPage .warning-cell").forEach((el) => el.classList.remove("invalid", "warning-cell"));

  required.forEach((name) => {
    if (!String(data[name] || "").trim()) pushIssue(issues, { level: "error", text: message("required", { field: labelFor(name) }), field: name });
  });

  validateReportDate(issues, data);
  validateMdProgress(issues, data);

  const operations = readTable("operationsTable");
  const opStats = validateOperationsTable(issues, "operationsTable", operations, ["P", "NPT"], "operationType");
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
  document.querySelectorAll("#completionDailyPage .invalid, #completionDailyPage .warning-cell").forEach((el) => el.classList.remove("invalid", "warning-cell"));

  required.forEach((name) => {
    if (!String(data[name] || "").trim()) pushIssue(issues, { level: "error", text: message("required", { field: labelFor(name) }), field: name });
  });

  validateReportDate(issues, data);
  validateOperationStartDate(issues, data);

  const operations = readTable("completionOperationsTable");
  const opStats = validateOperationsTable(issues, "completionOperationsTable", operations, ["P", "SC", "NPT"], "completionOperationType");
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
  document.querySelectorAll("#workoverDailyPage .invalid, #workoverDailyPage .warning-cell").forEach((el) => el.classList.remove("invalid", "warning-cell"));

  required.forEach((name) => {
    if (!String(data[name] || "").trim()) pushIssue(issues, { level: "error", text: message("required", { field: labelFor(name) }), field: name });
  });

  validateReportDate(issues, data);
  validateOperationStartDate(issues, data);

  const operations = readTable("workoverOperationsTable");
  const opStats = validateOperationsTable(issues, "workoverOperationsTable", operations, ["P", "SC", "NPT"], "workoverOperationType");
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
  document.querySelectorAll("#moveDailyPage .invalid, #moveDailyPage .warning-cell").forEach((el) => el.classList.remove("invalid", "warning-cell"));

  required.forEach((name) => {
    if (!String(data[name] || "").trim()) pushIssue(issues, { level: "error", text: message("required", { field: labelFor(name) }), field: name });
  });

  validateReportDate(issues, data);
  validateMdProgress(issues, data);

  const operations = readTable("moveOperationsTable");
  const opStats = validateOperationsTable(issues, "moveOperationsTable", operations, ["P", "SC", "NPT"], "moveOperationType");
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

document.querySelectorAll("[data-add-row]").forEach((button) => {
  button.addEventListener("click", () => {
    markReportOriginalEdited(tableReportType(button.dataset.addRow));
    addRow(button.dataset.addRow);
    validateForTable(button.dataset.addRow);
    updateSaveButton(tableReportType(button.dataset.addRow));
  });
});

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
  const adminLogin = event.target.closest("[data-admin-login-button]");
  if (adminLogin) {
    loginAdmin();
    return;
  }
  const adminLogout = event.target.closest("[data-admin-logout]");
  if (adminLogout) {
    logoutAdmin();
    return;
  }
  const adminTab = event.target.closest("[data-admin-tab]");
  if (adminTab) {
    switchAdminTab(adminTab.dataset.adminTab);
    return;
  }
  const adminEditUser = event.target.closest("[data-admin-edit-user]");
  if (adminEditUser) {
    fillAdminUserForm(adminEditUser.dataset.adminEditUser);
    return;
  }
  const adminSaveUser = event.target.closest("[data-admin-save-user]");
  if (adminSaveUser) {
    saveAdminUser();
    return;
  }
  const adminSaveConfig = event.target.closest("[data-admin-save-config]");
  if (adminSaveConfig) {
    saveAdminConfig();
    return;
  }
  const adminBackup = event.target.closest("[data-admin-backup]");
  if (adminBackup) {
    backupAdminDatabase();
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
      if (kind === "npt") renderNptTable(nptReportVisibleRows(analyticsState.npt.payload?.details || []));
      else if (kind === "productionReport") renderProductionReportTable(productionReportVisibleRows(analyticsState.productionReport.payload?.details || []));
      else renderProductionTable(analyticsState.production.payload?.details || []);
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

window.addEventListener("scroll", () => {
  document.querySelector(".npt-description-popover")?.remove();
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
  button.addEventListener("click", () => handleLanguageChoice(button.dataset.lang));
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
