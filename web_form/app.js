const i18n = {
  zh: {
    ui: {
      appTitleShort: "厄瓜油田", appSubtitle: "Report Platform", pageTitle: "钻井日报填报工作台", completionPageTitle: "完井日报填报工作台", completionPageKicker: "COMPLETION DAILY REPORT", workoverPageTitle: "修井日报填报工作台", workoverPageKicker: "WORKOVER DAILY REPORT", movePageTitle: "搬迁日报填报工作台", movePageKicker: "RIG MOVE DAILY REPORT",
      menuDailyParsing: "日报解析", menuDrillingDaily: "钻井日报", menuCompletionDaily: "完井日报", menuWorkoverDaily: "修井日报", menuMoveDaily: "搬迁日报",
      menuProductionReport: "生产报表", menuRigProductionSummary: "生产汇总", menuWellNptConfirm: "NPT统计与确认", menuRigNptRanking: "NPT分析",
      menuHsse: "HSSE管理", menuHsseCollection: "信息填报", menuHsseDashboard: "安全驾驶舱", menuDailySafetySummary: "日报统计", menuPeriodSafetyReport: "安全周月报",
      descDrillingDaily: "支持按类别上传单井 PDF 日报，解析井基础信息及 Operation 内容，并进入钻井日报填报页面。",
      descCompletionDaily: "上传完井日报 PDF，解析基础信息、Operation、库存和射孔区间，预览后可二次编辑。", descWorkoverDaily: "上传修井日报 PDF，解析 WO 信息、Operation、库存、安全备注和射孔区间，预览后可二次编辑。", descMoveDaily: "上传搬迁日报 PDF，解析 Operation、重型设备和载荷清单，预览后可二次编辑。",
      descRigProductionSummary: "基于日报解析数据，按日汇总各井队生产作业情况，形成井队维度统计报表。", descWellNptConfirm: "统计每口井 P、SC、NPT 时长及具体情况，并支持后续按时效确认表修正。", descRigNptRanking: "统计各钻井队历史作业 NPT 时长、占比及排名，支持井队对比分析。",
      descHsseCollection: "按井、按队伍记录每日安全生产信息，包括人的不安全行为、物的不安全状态、不放心人员、生产异常和公共安全事件。", descHsseDashboard: "集中展示全油田各队伍 HSSE 关键指标、异常情况和跟踪总览。", descDailySafetySummary: "基于 HSSE 采集数据生成每日各队伍安全生产关键信息汇总。", descPeriodSafetyReport: "基于 HSSE 数据生成周度、月度安全生产统计报表，支持阶段性分析和汇报。",
      moduleStatusPlanned: "功能规划", moduleComingSoon: "功能待开发", moduleCurrent: "当前菜单", moduleComingSoonDesc: "该功能已按需求菜单预留入口，后续可在此接入数据采集、统计报表或数据分析页面。",
      navBasic: "基础信息", navSummary: "作业摘要", navWellControl: "井控与液压", navSurvey: "测斜数据", navMud: "泥浆数据", navBitBha: "钻头与 BHA", navOperations: "作业明细", navCosts: "成本与库存", navIncidents: "事故与备注",
      importPdf: "导入 PDF 日报", saveDatabase: "保存", downloadDatabase: "下载Excel库", backRecords: "返回记录", databaseSaved: "已保存到Excel数据库。", databaseSaveFailed: "保存Excel数据库失败。", databaseRecord: "数据库记录", sourceFileEmpty: "未上传文件",
      uploadDashboardTitle: "日报管理 Dashboard", wellSelection: "井选择", searchWell: "搜索井号", reportCalendar: "日报日历", uploadRecords: "上传文件记录", allTypes: "全部类型", allStatuses: "全部状态", exportList: "导出", preview: "预览", download: "下载", detail: "详情", uploaded: "已完成", queued: "排队中", parsing: "解析中", failed: "失败", warningStatus: "有告警", pending: "待补传", noRecords: "暂无上传记录", addWell: "添加新井", selectedWell: "当前井", monthlyUploaded: "本月已上传", monthlyPending: "待补传", reportKinds: "日报类型", monthlyUploaders: "本月上传人", calendarHint: "提示：点击已有完成记录的日期可直接预览", recordsCount: "条记录", uploader: "上传人", uploadTime: "上传时间", fileName: "文件名称", status: "状态", operation: "操作", date: "日期", well: "井号", reportType: "日报类型",
      metricCompletion: "完成度", metricIssues: "校验问题", metricHours: "作业合计", metricProgress: "进尺", metricIntervals: "射孔区间",
      sectionBasic: "基础信息", sectionSummary: "作业摘要", sectionWellControl: "井控与液压", sectionSurvey: "Survey Data (Last 6)", sectionMud: "泥浆数据", sectionBitBha: "钻头与 BHA", sectionOperations: "Operations", sectionCosts: "成本与库存", sectionIncidents: "事故与备注", sectionPersonnel: "人员信息", sectionPerforationIntervals: "射孔区间",
      noteBasic: "对应 PDF 顶部日报抬头和井基本信息", noteSummary: "当前作业、24 小时总结、下一步计划", noteWellControl: "套管、BOP、泵压、扭矩和钩载", noteIncidents: "HSE 状态、同步作业和其他说明",
      completionNoteBasic: "对应完井 PDF 顶部日报抬头、AFP 和井基本信息", completionNotePersonnel: "Supervisor、Engineer、Geologist 与现场总人数", completionNoteRemarks: "安全备注、固控说明和其他现场备注", workoverNoteBasic: "对应修井 PDF 顶部日报抬头、AFP 和井基本信息", workoverNotePersonnel: "Supervisor、Engineer、Geologist 与现场总人数", workoverNoteRemarks: "安全备注、固控说明和其他现场备注", moveNoteBasic: "对应搬迁 PDF 顶部日报抬头、AFE 和井队信息", moveNoteRemarks: "其他现场备注原文",
      addSurvey: "新增测斜", addBha: "新增 BHA", addOperation: "新增作业行", addCost: "新增成本", addBulk: "新增库存", addInterval: "新增区间", rulesTitle: "基础条件限制规则", liveValidation: "实时校验",
      noIssues: "当前没有校验问题。", pdfImporting: "正在解析 PDF 日报...", pdfImported: "PDF 日报已解析并填充到界面。", pdfImportFailed: "PDF 解析失败，请检查文件格式或模板。",
      thMd: "MD (ft)", thIncl: "Incl (deg)", thAzi: "Azi (deg)", thTvd: "TVD (ft)", thVse: "VSE (ft)", thNs: "N/-S (ft)", thDls: "DLS (deg/100ft)", thBuild: "Build (deg/100ft)", thComponent: "Component", thOd: "OD (in)", thId: "ID (in)", thJts: "Jts", thLength: "Length (ft)", thFrom: "From (HH:MM)", thTo: "To (HH:MM)", thHrs: "Hrs (h)", thOpCode: "Op Code", thOpSub: "Op Sub", thType: "Type", thOperationDetails: "Operation Details", thCostDescription: "Cost Description", thVendor: "Vendor", thAmount: "Amount (USD)", thBulk: "Bulk", thQtyStart: "Qty Start", thQtyUsed: "Qty Used", thQtyEnd: "Qty End", thFormation: "Formation", thTopMd: "Top MD (ft)", thBaseMd: "Base MD (ft)", thDensity: "Density (spf)", thCharges: "Charges", thPhase: "Phase (deg)", thPenetration: "Penetration (in)", thDiameter: "Diameter (in)", thDate: "Date", thStatus: "Status", thComments: "Comments", thLocation: "Location", thEquipment: "Equipment", thPlate: "Plate", thEntryDate: "Entry Date", thEntryTime: "Entry Time", thGuide: "Guide", thCargo: "Cargo", thTrip: "Trip"
    },
    fields: {
      event: "Event", reportDate: "Date", reportNo: "Report No", wellbore: "Wellbore", rig: "Rig", primaryReason: "Primary Reason", afeNumber: "AFE Number", refDatum: "Ref Datum", todayMd: "Today's MD (ft)", prevMd: "Prev MD (ft)", progress: "Progress (ft)", rotHrsToday: "Rot Hrs Today",
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
      "<strong>金额：</strong>成本金额不能为负，空成本表允许保存但会提示。"
    ],
    completionRules: [
      "<strong>必填：</strong>Date、Report No、Wellbore、Rig、Current Ops、24-Hr Summary、24-Hr Forecast。",
      "<strong>日期：</strong>日报日期不能晚于当前日期，Operation Start 不能晚于日报日期。",
      "<strong>工时：</strong>Operations 明细 Hrs 合计必须为 24.00 小时，允许 0.05 小时误差。",
      "<strong>作业行：</strong>From、To、Hrs、Op Code、Type、Operation Details 建议完整填写；Type 只能是 P、SC 或 NPT。",
      "<strong>射孔区间：</strong>Base MD 应大于等于 Top MD，Length 不能为负。",
      "<strong>库存和成本：</strong>库存数量、成本金额不能为负。"
    ],
    workoverRules: [
      "<strong>必填：</strong>Date、Report No、Wellbore、Rig、Current Ops、24-Hr Summary、24-Hr Forecast。",
      "<strong>日期：</strong>日报日期不能晚于当前日期，Operation Start 不能晚于日报日期。",
      "<strong>工时：</strong>Operations 明细 Hrs 合计必须为 24.00 小时，允许 0.05 小时误差。",
      "<strong>作业行：</strong>From、To、Hrs、Op Code、Type、Operation Details 建议完整填写；Type 只能是 P、SC 或 NPT。",
      "<strong>射孔区间：</strong>Base MD 应大于等于 Top MD，Length 不能为负。",
      "<strong>库存和成本：</strong>库存数量、成本金额不能为负。"
    ],
    moveRules: [
      "<strong>必填：</strong>Date、Report No、Wellbore、Rig、Current Ops、24-Hr Summary、24-Hr Forecast。",
      "<strong>工时：</strong>Operations 明细 Hrs 合计必须为 24.00 小时，允许 0.05 小时误差。",
      "<strong>作业行：</strong>From、To、Hrs、Op Code、Type、Operation Details 建议完整填写；Type 只能是 P、SC 或 NPT。",
      "<strong>备注：</strong>Other Remarks 可保留 PDF 末页原文，便于人工复核。"
    ],
    msg: {
      required: "{field} 为必填项。", futureDate: "日报日期不能晚于当前日期。", operationStartDate: "Operation Start 不能晚于日报日期。", mdOrder: "Today's MD 必须大于等于 Prev MD。", progressMismatch: "Progress 与井深差值不一致，当前差值为 {value} ft。", operationHours: "Operations 工时合计应为 24.00 h，当前为 {value} h。", operationMissing: "作业明细第 {row} 行缺少 {field}。", operationType: "作业明细第 {row} 行 Type 为空或不是 P/NPT，请复核。", completionOperationType: "完井作业第 {row} 行 Type 为空或不是 P/SC/NPT，请复核。", workoverOperationType: "修井作业第 {row} 行 Type 为空或不是 P/SC/NPT，请复核。", moveOperationType: "搬迁作业第 {row} 行 Type 为空或不是 P/SC/NPT，请复核。", operationHourRange: "作业明细第 {row} 行 Hrs 必须在 0 到 24 之间。", intervalDepth: "射孔区间第 {row} 行 Base MD 应大于等于 Top MD。", intervalLength: "射孔区间第 {row} 行 Length 不能为负。", surveyMd: "测斜第 {row} 行 MD 不能大于 Today's MD。", surveyIncl: "测斜第 {row} 行 Incl 应在 0 到 180 之间。", surveyDls: "测斜第 {row} 行 DLS 不能为负。", mudDensity: "泥浆 Density 推荐范围为 6 到 20 ppg。", sand: "泥浆 Sand 超过 10%，请复核。", bhaOdId: "BHA 第 {row} 行 OD 应大于等于 ID。", bhaNegative: "BHA 第 {row} 行存在负数。", costNegative: "成本第 {row} 行金额不能为负。", incidentRequired: "发生 Safety 或 Environmental Incident 时，Incident Comments 必填。"
    }
  },
  en: {
    ui: {
      appTitleShort: "Ecuador Field", appSubtitle: "Report Platform", pageTitle: "Drilling Daily Report Workspace", completionPageTitle: "Completion Daily Report Workspace", completionPageKicker: "COMPLETION DAILY REPORT", workoverPageTitle: "Workover Daily Report Workspace", workoverPageKicker: "WORKOVER DAILY REPORT",
      menuDailyParsing: "Daily Parsing", menuDrillingDaily: "Drilling Daily", menuCompletionDaily: "Completion Daily", menuWorkoverDaily: "Workover Daily", menuMoveDaily: "Move Daily",
      menuProductionReport: "Production Reports", menuRigProductionSummary: "Production Summary", menuWellNptConfirm: "NPT Stats & Confirmation", menuRigNptRanking: "NPT Analysis",
      menuHsse: "HSSE Management", menuHsseCollection: "Information Entry", menuHsseDashboard: "Safety Cockpit", menuDailySafetySummary: "Daily Report Stats", menuPeriodSafetyReport: "Weekly / Monthly Safety Report",
      descDrillingDaily: "Upload single-well PDF daily reports, parse well basics and Operation content, then edit the drilling daily report.",
      descCompletionDaily: "Upload completion daily PDFs, parse basics, operations, bulks, and perforated intervals, then preview and edit.", descWorkoverDaily: "Upload workover daily PDFs, parse WO information, operations, bulks, safety comments, and perforated intervals, then preview and edit.", descMoveDaily: "Reserved entry for rig move daily PDF parsing and structured entry.",
      descRigProductionSummary: "Summarize daily rig production activity from parsed daily report data by rig/team.", descWellNptConfirm: "Analyze P, SC, and NPT hours by well, with later updates from time-class confirmation sheets.", descRigNptRanking: "Rank drilling rigs by historical NPT duration and share for comparison analysis.",
      descHsseCollection: "Capture daily HSSE information by well and team, including unsafe acts, unsafe conditions, personnel concerns, production exceptions, and public security events.", descHsseDashboard: "Show field-wide HSSE KPIs, exceptions, tracking, and overview by team.", descDailySafetySummary: "Generate daily key safety production summaries from HSSE collection data.", descPeriodSafetyReport: "Generate weekly and monthly HSSE statistical reports for stage analysis and reporting.",
      moduleStatusPlanned: "Planned Feature", moduleComingSoon: "Feature Reserved", moduleCurrent: "Current Menu", moduleComingSoonDesc: "This menu entry is reserved from the requirement list. Data entry, reporting, or analytics pages can be connected here later.",
      navBasic: "Basic Info", navSummary: "Operations Summary", navWellControl: "Well Control & Hydraulics", navSurvey: "Survey Data", navMud: "Mud Data", navBitBha: "Bit & BHA", navOperations: "Operations Log", navCosts: "Costs & Bulks", navIncidents: "Incidents & Remarks",
      importPdf: "Import PDF Report", saveDatabase: "Save", downloadDatabase: "Download Excel DB", backRecords: "Back to Records", databaseSaved: "Saved to the Excel database.", databaseSaveFailed: "Failed to save the Excel database.", databaseRecord: "Database record", sourceFileEmpty: "No file uploaded",
      uploadDashboardTitle: "Daily Report Dashboard", wellSelection: "Well Selection", searchWell: "Search well", reportCalendar: "Report Calendar", uploadRecords: "Upload Records", allTypes: "All Types", allStatuses: "All Statuses", exportList: "Export", preview: "Preview", download: "Download", detail: "Details", uploaded: "Complete", queued: "Queued", parsing: "Parsing", failed: "Failed", warningStatus: "Warnings", pending: "Pending", noRecords: "No upload records", addWell: "Add Well", selectedWell: "Selected Well", monthlyUploaded: "Uploaded This Month", monthlyPending: "Pending Uploads", reportKinds: "Report Types", monthlyUploaders: "Uploaders This Month", calendarHint: "Tip: click a completed calendar date to preview it", recordsCount: "records", uploader: "Uploader", uploadTime: "Upload Time", fileName: "File Name", status: "Status", operation: "Actions", date: "Date", well: "Well", reportType: "Report Type",
      metricCompletion: "Completion", metricIssues: "Validation Issues", metricHours: "Operation Total", metricProgress: "Progress", metricIntervals: "Intervals",
      sectionBasic: "Basic Info", sectionSummary: "Operations Summary", sectionWellControl: "Well Control & Hydraulics", sectionSurvey: "Survey Data (Last 6)", sectionMud: "Mud Data", sectionBitBha: "Bit & BHA", sectionOperations: "Operations", sectionCosts: "Costs & Bulks", sectionIncidents: "Incidents & Remarks", sectionPersonnel: "Personnel", sectionPerforationIntervals: "Perforated Intervals",
      noteBasic: "Header and well information from the PDF template", noteSummary: "Current operation, 24-hour summary, and next plan", noteWellControl: "Casing, BOP, pump pressure, torque, and hookload", noteIncidents: "HSE status, simultaneous operations, and remarks",
      completionNoteBasic: "Completion PDF header, AFP, and well information", completionNotePersonnel: "Supervisors, engineers, geologist, and total personnel", completionNoteRemarks: "Safety comments, solids control, and field remarks", workoverNoteBasic: "Workover PDF header, AFP, and well information", workoverNotePersonnel: "Supervisors, engineers, geologist, and total personnel", workoverNoteRemarks: "Safety comments, solids control, and field remarks",
      addSurvey: "Add Survey", addBha: "Add BHA", addOperation: "Add Operation", addCost: "Add Cost", addBulk: "Add Bulk", addInterval: "Add Interval", rulesTitle: "Basic Validation Rules", liveValidation: "Live Validation",
      noIssues: "No validation issues.", pdfImporting: "Parsing PDF report...", pdfImported: "PDF report parsed and filled into the form.", pdfImportFailed: "PDF parsing failed. Check the file format or template.",
      thMd: "MD (ft)", thIncl: "Incl (deg)", thAzi: "Azi (deg)", thTvd: "TVD (ft)", thVse: "VSE (ft)", thNs: "N/-S (ft)", thDls: "DLS (deg/100ft)", thBuild: "Build (deg/100ft)", thComponent: "Component", thOd: "OD (in)", thId: "ID (in)", thJts: "Jts", thLength: "Length (ft)", thFrom: "From (HH:MM)", thTo: "To (HH:MM)", thHrs: "Hrs (h)", thOpCode: "Op Code", thOpSub: "Op Sub", thType: "Type", thOperationDetails: "Operation Details", thCostDescription: "Cost Description", thVendor: "Vendor", thAmount: "Amount (USD)", thBulk: "Bulk", thQtyStart: "Qty Start", thQtyUsed: "Qty Used", thQtyEnd: "Qty End", thFormation: "Formation", thTopMd: "Top MD (ft)", thBaseMd: "Base MD (ft)", thDensity: "Density (spf)", thCharges: "Charges", thPhase: "Phase (deg)", thPenetration: "Penetration (in)", thDiameter: "Diameter (in)", thDate: "Date", thStatus: "Status", thComments: "Comments"
    },
    fields: {
      event: "Event", reportDate: "Date", reportNo: "Report No", wellbore: "Wellbore", rig: "Rig", primaryReason: "Primary Reason", afeNumber: "AFE Number", refDatum: "Reference Datum", todayMd: "Today's MD (ft)", prevMd: "Previous MD (ft)", progress: "Progress (ft)", rotHrsToday: "Rotating Hours Today",
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
      "<strong>Cost:</strong> cost amount cannot be negative; empty cost tables are allowed with a warning."
    ],
    completionRules: [
      "<strong>Required:</strong> Date, Report No, Wellbore, Rig, Current Operations, 24-Hour Summary, and 24-Hour Forecast.",
      "<strong>Date:</strong> report date cannot be later than today, and Operation Start cannot be later than the report date.",
      "<strong>Hours:</strong> Operations Hrs must total 24.00 hours with 0.05 h tolerance.",
      "<strong>Operation rows:</strong> From, To, Hrs, Op Code, Type, and Operation Details should be complete; Type must be P, SC, or NPT.",
      "<strong>Perforated intervals:</strong> Base MD should be greater than or equal to Top MD; Length cannot be negative.",
      "<strong>Bulks and costs:</strong> bulk quantities and cost amounts cannot be negative."
    ],
    workoverRules: [
      "<strong>Required:</strong> Date, Report No, Wellbore, Rig, Current Operations, 24-Hour Summary, and 24-Hour Forecast.",
      "<strong>Date:</strong> report date cannot be later than today, and Operation Start cannot be later than the report date.",
      "<strong>Hours:</strong> Operations Hrs must total 24.00 hours with 0.05 h tolerance.",
      "<strong>Operation rows:</strong> From, To, Hrs, Op Code, Type, and Operation Details should be complete; Type must be P, SC, or NPT.",
      "<strong>Perforated intervals:</strong> Base MD should be greater than or equal to Top MD; Length cannot be negative.",
      "<strong>Bulks and costs:</strong> bulk quantities and cost amounts cannot be negative."
    ],
    moveRules: [
      "<strong>Required:</strong> Date, Report No, Wellbore, Rig, Current Operations, 24-Hour Summary, and 24-Hour Forecast.",
      "<strong>Hours:</strong> Operations Hrs must total 24.00 hours with 0.05 h tolerance.",
      "<strong>Operation rows:</strong> From, To, Hrs, Op Code, Type, and Operation Details should be complete; Type must be P, SC, or NPT.",
      "<strong>Remarks:</strong> Other Remarks can keep the original final-page text for manual review."
    ],
    msg: {
      required: "{field} is required.", futureDate: "Report date cannot be later than today.", operationStartDate: "Operation Start cannot be later than the report date.", mdOrder: "Today's MD must be greater than or equal to Previous MD.", progressMismatch: "Progress does not match the MD difference. Current difference is {value} ft.", operationHours: "Operations total must be 24.00 h. Current total is {value} h.", operationMissing: "Operations row {row} is missing {field}.", operationType: "Operations row {row} Type is empty or not P/NPT; please review.", completionOperationType: "Completion operation row {row} Type is empty or not P/SC/NPT; please review.", workoverOperationType: "Workover operation row {row} Type is empty or not P/SC/NPT; please review.", operationHourRange: "Operations row {row} Hrs must be between 0 and 24.", intervalDepth: "Perforated interval row {row} Base MD should be greater than or equal to Top MD.", intervalLength: "Perforated interval row {row} Length cannot be negative.", surveyMd: "Survey row {row} MD cannot exceed Today's MD.", surveyIncl: "Survey row {row} Incl must be between 0 and 180.", surveyDls: "Survey row {row} DLS cannot be negative.", mudDensity: "Mud density should be between 6 and 20 ppg.", sand: "Mud sand is above 10%; please review.", bhaOdId: "BHA row {row} OD should be greater than or equal to ID.", bhaNegative: "BHA row {row} contains a negative value.", costNegative: "Cost row {row} amount cannot be negative.", incidentRequired: "Incident Comments are required when Safety or Environmental Incident is Y."
    }
  },
  es: {
    ui: {
      appTitleShort: "Campo Ecuador", appSubtitle: "Plataforma de Reportes", pageTitle: "Mesa de Registro del Reporte Diario", completionPageTitle: "Mesa del Reporte Diario de Completación", completionPageKicker: "REPORTE DIARIO DE COMPLETACIÓN", workoverPageTitle: "Mesa del Reporte Diario de Workover", workoverPageKicker: "REPORTE DIARIO DE WORKOVER",
      menuDailyParsing: "Análisis de Reportes", menuDrillingDaily: "Reporte Diario de Perforación", menuCompletionDaily: "Reporte Diario de Completación", menuWorkoverDaily: "Reporte Diario de Workover", menuMoveDaily: "Reporte Diario de Movilización",
      menuProductionReport: "Reportes de Producción", menuRigProductionSummary: "Resumen de Producción", menuWellNptConfirm: "Estadísticas y Confirmación NPT", menuRigNptRanking: "Análisis NPT",
      menuHsse: "Gestión HSSE", menuHsseCollection: "Registro de Información", menuHsseDashboard: "Cabina de Seguridad", menuDailySafetySummary: "Estadísticas Diarias", menuPeriodSafetyReport: "Reporte Semanal / Mensual de Seguridad",
      descDrillingDaily: "Carga reportes diarios PDF de un pozo, extrae datos básicos y operaciones, y permite editar el reporte diario de perforación.",
      descCompletionDaily: "Carga PDFs diarios de completación, extrae datos básicos, operaciones, inventarios e intervalos cañoneados, y permite revisar y editar.", descWorkoverDaily: "Carga PDFs diarios de workover, extrae información WO, operaciones, inventarios, comentarios de seguridad e intervalos cañoneados, y permite revisar y editar.", descMoveDaily: "Entrada reservada para análisis PDF y captura estructurada de reportes diarios de movilización.",
      descRigProductionSummary: "Resume la actividad diaria de producción por equipo a partir de los reportes diarios procesados.", descWellNptConfirm: "Analiza horas P, SC y NPT por pozo, con actualización posterior desde tablas de confirmación de tiempos.", descRigNptRanking: "Clasifica equipos de perforación por duración y proporción histórica de NPT.",
      descHsseCollection: "Registra información HSSE diaria por pozo y equipo, incluyendo actos inseguros, condiciones inseguras, personal vulnerable, anomalías productivas y seguridad pública.", descHsseDashboard: "Muestra KPIs HSSE, excepciones y seguimiento general por equipo.", descDailySafetySummary: "Genera resúmenes diarios de información clave de seguridad a partir de datos HSSE.", descPeriodSafetyReport: "Genera reportes estadísticos HSSE semanales y mensuales para análisis y presentación.",
      moduleStatusPlanned: "Función Planificada", moduleComingSoon: "Función Reservada", moduleCurrent: "Menú Actual", moduleComingSoonDesc: "Esta entrada queda reservada según la lista de requisitos. Luego se podrá conectar captura de datos, reportes o análisis.",
      navBasic: "Información Básica", navSummary: "Resumen Operacional", navWellControl: "Control de Pozo e Hidráulica", navSurvey: "Datos Direccionales", navMud: "Datos de Lodo", navBitBha: "Broca y BHA", navOperations: "Registro de Operaciones", navCosts: "Costos e Inventario", navIncidents: "Incidentes y Observaciones",
      importPdf: "Importar Reporte PDF", saveDatabase: "Guardar", downloadDatabase: "Descargar Excel", backRecords: "Volver a registros", databaseSaved: "Guardado en la base Excel.", databaseSaveFailed: "No se pudo guardar la base Excel.", databaseRecord: "Registro de base", sourceFileEmpty: "No se ha cargado archivo",
      uploadDashboardTitle: "Panel de Reportes Diarios", wellSelection: "Selección de Pozo", searchWell: "Buscar pozo", reportCalendar: "Calendario", uploadRecords: "Registros de Carga", allTypes: "Todos los tipos", allStatuses: "Todos los estados", exportList: "Exportar", preview: "Vista previa", download: "Descargar", detail: "Detalle", uploaded: "Completo", queued: "En cola", parsing: "Analizando", failed: "Falló", warningStatus: "Alertas", pending: "Pendiente", noRecords: "Sin registros", addWell: "Agregar pozo", selectedWell: "Pozo actual", monthlyUploaded: "Cargados del mes", monthlyPending: "Pendientes", reportKinds: "Tipos de reporte", monthlyUploaders: "Cargadores del mes", calendarHint: "Tip: haga clic en una fecha completada para previsualizar", recordsCount: "registros", uploader: "Usuario", uploadTime: "Hora de carga", fileName: "Archivo", status: "Estado", operation: "Acciones", date: "Fecha", well: "Pozo", reportType: "Tipo",
      metricCompletion: "Avance", metricIssues: "Alertas", metricHours: "Total Operativo", metricProgress: "Progreso", metricIntervals: "Intervalos",
      sectionBasic: "Información Básica", sectionSummary: "Resumen Operacional", sectionWellControl: "Control de Pozo e Hidráulica", sectionSurvey: "Datos Direccionales (Últimos 6)", sectionMud: "Datos de Lodo", sectionBitBha: "Broca y BHA", sectionOperations: "Operaciones", sectionCosts: "Costos e Inventario", sectionIncidents: "Incidentes y Observaciones", sectionPersonnel: "Personal", sectionPerforationIntervals: "Intervalos Cañoneados",
      noteBasic: "Encabezado e información del pozo según la plantilla PDF", noteSummary: "Operación actual, resumen de 24 horas y plan siguiente", noteWellControl: "Casing, BOP, presión de bomba, torque y hookload", noteIncidents: "Estado HSE, operaciones simultáneas y observaciones",
      completionNoteBasic: "Encabezado PDF de completación, AFP e información del pozo", completionNotePersonnel: "Supervisores, ingenieros, geólogo y personal total", completionNoteRemarks: "Comentarios de seguridad, control de sólidos y observaciones de campo", workoverNoteBasic: "Encabezado PDF de workover, AFP e información del pozo", workoverNotePersonnel: "Supervisores, ingenieros, geólogo y personal total", workoverNoteRemarks: "Comentarios de seguridad, control de sólidos y observaciones de campo",
      addSurvey: "Agregar Survey", addBha: "Agregar BHA", addOperation: "Agregar Operación", addCost: "Agregar Costo", addBulk: "Agregar Inventario", addInterval: "Agregar Intervalo", rulesTitle: "Reglas Básicas de Validación", liveValidation: "Validación en Vivo",
      noIssues: "Sin alertas de validación.", pdfImporting: "Analizando reporte PDF...", pdfImported: "Reporte PDF analizado y cargado en el formulario.", pdfImportFailed: "No se pudo analizar el PDF. Revise el formato o la plantilla.",
      thMd: "MD (ft)", thIncl: "Incl (deg)", thAzi: "Azi (deg)", thTvd: "TVD (ft)", thVse: "VSE (ft)", thNs: "N/-S (ft)", thDls: "DLS (deg/100ft)", thBuild: "Build (deg/100ft)", thComponent: "Componente", thOd: "OD (in)", thId: "ID (in)", thJts: "Jts", thLength: "Longitud (ft)", thFrom: "Desde (HH:MM)", thTo: "Hasta (HH:MM)", thHrs: "Hrs (h)", thOpCode: "Código Op", thOpSub: "Sub Op", thType: "Tipo", thOperationDetails: "Detalle de Operación", thCostDescription: "Descripción de Costo", thVendor: "Proveedor", thAmount: "Monto (USD)", thBulk: "Inventario", thQtyStart: "Cant. Inicial", thQtyUsed: "Cant. Usada", thQtyEnd: "Cant. Final", thFormation: "Formación", thTopMd: "Tope MD (ft)", thBaseMd: "Base MD (ft)", thDensity: "Densidad (spf)", thCharges: "Cargas", thPhase: "Fase (deg)", thPenetration: "Penetración (in)", thDiameter: "Diámetro (in)", thDate: "Fecha", thStatus: "Estado", thComments: "Comentarios"
    },
    fields: {
      event: "Evento", reportDate: "Fecha", reportNo: "No. de Reporte", wellbore: "Pozo", rig: "Taladro", primaryReason: "Razón Principal", afeNumber: "Número AFE", refDatum: "Datum de Referencia", todayMd: "MD de Hoy (ft)", prevMd: "MD Anterior (ft)", progress: "Progreso (ft)", rotHrsToday: "Horas Rotando Hoy",
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
      required: "{field} es obligatorio.", futureDate: "La fecha del reporte no puede ser posterior a hoy.", operationStartDate: "Inicio OPR no puede ser posterior a la fecha del reporte.", mdOrder: "El MD de hoy debe ser mayor o igual al MD anterior.", progressMismatch: "El progreso no coincide con la diferencia de MD. La diferencia actual es {value} ft.", operationHours: "El total de operaciones debe ser 24.00 h. El total actual es {value} h.", operationMissing: "La fila de operaciones {row} no tiene {field}.", operationType: "El Tipo en la fila de operaciones {row} está vacío o no es P/NPT; revisar.", completionOperationType: "El Tipo en la fila de completación {row} está vacío o no es P/SC/NPT; revisar.", workoverOperationType: "El Tipo en la fila de workover {row} está vacío o no es P/SC/NPT; revisar.", operationHourRange: "Las Hrs de la fila {row} deben estar entre 0 y 24.", intervalDepth: "En intervalo cañoneado fila {row}, Base MD debe ser mayor o igual que Tope MD.", intervalLength: "La Longitud del intervalo cañoneado fila {row} no puede ser negativa.", surveyMd: "El MD de survey en la fila {row} no puede superar el MD de hoy.", surveyIncl: "La inclinación en la fila {row} debe estar entre 0 y 180.", surveyDls: "El DLS en la fila {row} no puede ser negativo.", mudDensity: "La densidad del lodo debe estar entre 6 y 20 ppg.", sand: "La arena del lodo supera 10%; revisar.", bhaOdId: "En BHA fila {row}, OD debe ser mayor o igual que ID.", bhaNegative: "La fila BHA {row} contiene un valor negativo.", costNegative: "El monto de costo en la fila {row} no puede ser negativo.", incidentRequired: "Los comentarios son obligatorios cuando Safety o Environmental Incident es Y."
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
let currentLanguage = localStorage.getItem("drillingReportLanguage") || "zh";
let activeMenuTarget = "drilling-daily";
let drillingSourceFileName = "";
const currentRecordIds = { drilling: "", completion: "", workover: "", move: "" };
const savedReportSignatures = { drilling: "", completion: "", workover: "", move: "" };
const recordState = {
  drilling: { records: [], selectedWell: "", selectedDate: "", search: "" },
  completion: { records: [], selectedWell: "", selectedDate: "", search: "" },
  workover: { records: [], selectedWell: "", selectedDate: "", search: "" },
  move: { records: [], selectedWell: "", selectedDate: "", search: "" }
};
const uploadJobs = [];
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

function activeMenuLink() {
  return document.querySelector(`.menu-link[data-menu-target="${activeMenuTarget}"]`);
}

function setDrillingSourceFile(filename = "") {
  drillingSourceFileName = filename;
  document.querySelector("#drillingSourceFile").textContent = filename || ui("sourceFileEmpty");
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
    el.hidden = mode !== "detail";
  });
}

function showReportRecords(reportType) {
  setReportMode(reportType, "records");
  refreshRecords(reportType);
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function showReportDetail(reportType) {
  setReportMode(reportType, "detail");
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function rememberRecord(reportType, payload = {}) {
  const recordId = payload.metadata?.record_id || "";
  currentRecordIds[reportType] = recordId;
  if (reportType === "drilling") {
    const source = payload.metadata?.source_file || drillingSourceFileName || "";
    const suffix = recordId ? ` · ${ui("databaseRecord")}: ${recordId}` : "";
    document.querySelector("#drillingSourceFile").textContent = source ? `${source}${suffix}` : ui("sourceFileEmpty");
  }
}

function renderModulePlaceholder(link = activeMenuLink()) {
  if (!link || activeMenuTarget === "drilling-daily" || activeMenuTarget === "completion-daily" || activeMenuTarget === "workover-daily" || activeMenuTarget === "move-daily") return;
  document.querySelector("#placeholderTitle").textContent = ui(link.dataset.titleI18n);
  document.querySelector("#placeholderDescription").textContent = ui(link.dataset.descI18n);
}

function setActiveMenu(target) {
  activeMenuTarget = target;
  document.querySelectorAll(".menu-link").forEach((link) => {
    link.classList.toggle("active", link.dataset.menuTarget === target);
  });
  const isDrillingDaily = target === "drilling-daily";
  const isCompletionDaily = target === "completion-daily";
  const isWorkoverDaily = target === "workover-daily";
  const isMoveDaily = target === "move-daily";
  document.querySelector("#drillingDailyPage").hidden = !isDrillingDaily;
  document.querySelector("#drillingDailyPage").classList.toggle("active", isDrillingDaily);
  document.querySelector("#completionDailyPage").hidden = !isCompletionDaily;
  document.querySelector("#completionDailyPage").classList.toggle("active", isCompletionDaily);
  document.querySelector("#workoverDailyPage").hidden = !isWorkoverDaily;
  document.querySelector("#workoverDailyPage").classList.toggle("active", isWorkoverDaily);
  document.querySelector("#moveDailyPage").hidden = !isMoveDaily;
  document.querySelector("#moveDailyPage").classList.toggle("active", isMoveDaily);
  const showPlaceholder = !isDrillingDaily && !isCompletionDaily && !isWorkoverDaily && !isMoveDaily;
  document.querySelector("#modulePlaceholder").hidden = !showPlaceholder;
  document.querySelector("#modulePlaceholder").classList.toggle("active", showPlaceholder);
  if (showPlaceholder) renderModulePlaceholder();
  if (isDrillingDaily) showReportRecords("drilling");
  if (isCompletionDaily) showReportRecords("completion");
  if (isWorkoverDaily) showReportRecords("workover");
  if (isMoveDaily) showReportRecords("move");
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
  currentLanguage = language;
  localStorage.setItem("drillingReportLanguage", language);
  document.documentElement.lang = language === "zh" ? "zh-CN" : language;
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    el.textContent = ui(el.dataset.i18n);
  });
  document.querySelectorAll(".language-switch [data-lang]").forEach((button) => {
    button.classList.toggle("active", button.dataset.lang === language);
  });
  document.querySelectorAll("label").forEach((label) => {
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
  renderModulePlaceholder();
  validate();
  validateCompletion();
  validateWorkover();
  validateMove();
  updateAllSaveButtons();
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
    tr.remove();
    validateForTable(tableId);
    updateSaveButton(tableReportType(tableId));
  });
  action.appendChild(button);
  tr.appendChild(action);
  tbody.appendChild(tr);
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

async function refreshRecords(reportType) {
  try {
    const response = await fetch(`/api/records?report_type=${encodeURIComponent(reportType)}`);
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || "Records failed");
    recordState[reportType].records = payload.records || [];
  } catch (error) {
    console.error(error);
    recordState[reportType].records = [];
  }
  renderRecordDashboard(reportType);
}

function renderRecordDashboard(reportType) {
  const host = document.querySelector(`[data-record-dashboard="${reportType}"]`);
  if (!host) return;
  const state = recordState[reportType];
  const records = state.records;
  const jobs = uploadJobs.filter((job) => job.reportType === reportType);
  const wells = [...new Set(records.map((record) => record.wellbore).filter(Boolean))];
  const sourceWells = wells.length ? wells : fallbackWells;
  const wellList = sourceWells.filter((well) => !state.search || well.toLowerCase().includes(state.search.toLowerCase()));
  if (!state.selectedWell || !wellList.includes(state.selectedWell)) state.selectedWell = wellList[0] || "";
  const selectedRecords = records.filter((record) => !state.selectedWell || record.wellbore === state.selectedWell);
  const selectedJobs = jobs.filter((job) => !state.selectedWell || !job.wellbore || job.wellbore === state.selectedWell);
  const monthBase = selectedRecords[0]?.reportDate || records[0]?.reportDate || new Date().toISOString().slice(0, 10);
  const monthRecords = recordsForMonth(selectedRecords, monthBase);
  const uploadedDays = new Set(monthRecords.map((record) => dayOfMonth(record.reportDate)));
  const pendingDays = pendingCalendarDays(uploadedDays, monthBase);
  const tableRecords = sortedRecords(state.selectedDate ? selectedRecords.filter((record) => record.reportDate === state.selectedDate) : selectedRecords);

  host.innerHTML = `
    <div class="record-layout">
      <aside class="well-panel panel">
        <div class="panel-heading">
          <h2>${ui("wellSelection")}</h2>
        </div>
        <input class="well-search" type="search" value="${escapeHtml(state.search)}" placeholder="${ui("searchWell")}" data-well-search="${reportType}" />
        <div class="well-list">
          ${wellList.map((well, index) => `
            <button class="well-card ${well === state.selectedWell ? "active" : ""}" type="button" data-well="${escapeHtml(well)}" data-report-type="${reportType}">
              <span class="well-icon">${String(index + 1).padStart(2, "0")}</span>
              <span><strong>${escapeHtml(well)}</strong><small>${well === state.selectedWell ? ui("selectedWell") : reportName(reportType)}</small></span>
              <i></i>
            </button>
          `).join("")}
        </div>
        <button class="button secondary add-well-button" type="button">${ui("addWell")}</button>
      </aside>
      <section class="record-main">
        <div class="record-top-grid">
          <section class="panel calendar-panel">
            <div class="panel-heading">
              <h2>${ui("reportCalendar")}</h2>
              <strong class="calendar-month">${calendarMonthLabel(monthBase)}</strong>
            </div>
            ${calendarMarkup(reportType, monthBase, uploadedDays, pendingDays)}
          </section>
          <section class="panel record-summary-panel">
            <div class="record-summary-grid">
              ${summaryCard("monthlyUploaded", `${monthRecords.length}`, ui("recordsCount"), "blue")}
              ${summaryCard("monthlyPending", `${pendingDays.size}`, "", "red")}
              ${summaryCard("reportKinds", "1", reportName(reportType), "green")}
              ${summaryCard("monthlyUploaders", `${new Set(monthRecords.map((record) => record.uploader || record.source_file || "local")).size}`, "", "violet")}
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
            ${recordTableMarkup(reportType, tableRecords, selectedJobs)}
          </div>
        </section>
      </section>
    </div>
  `;
}

function summaryCard(labelKey, value, caption, tone) {
  return `
    <div class="record-summary-card ${tone}">
      <span>${ui(labelKey)}</span>
      <strong>${escapeHtml(value)}</strong>
      <small>${escapeHtml(caption)}</small>
    </div>
  `;
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

function pendingCalendarDays(uploadedDays, monthBase) {
  const days = new Set();
  const date = new Date(`${(monthBase || new Date().toISOString().slice(0, 10)).slice(0, 7)}-01T00:00:00`);
  const totalDays = new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate();
  const today = new Date();
  const isCurrentMonth = today.getFullYear() === date.getFullYear() && today.getMonth() === date.getMonth();
  const upper = isCurrentMonth ? today.getDate() : totalDays;
  for (let day = 1; day <= upper; day++) {
    if (!uploadedDays.has(day)) days.add(day);
  }
  return days;
}

function calendarMonthLabel(dateValue) {
  const date = new Date(`${(dateValue || new Date().toISOString().slice(0, 10)).slice(0, 7)}-01T00:00:00`);
  if (currentLanguage === "zh") return `${date.getFullYear()}年${date.getMonth() + 1}月`;
  return date.toLocaleDateString(currentLanguage === "es" ? "es-ES" : "en-US", { year: "numeric", month: "long" });
}

function calendarMarkup(reportType, dateValue, uploadedDays, pendingDays) {
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
        const statusClass = cell.muted ? "muted" : uploadedDays.has(cell.day) ? "has-upload" : pendingDays.has(cell.day) ? "needs-upload" : "";
        return `<button type="button" class="${statusClass}" data-calendar-date="${cell.date || ""}" data-report-type="${reportType}" ${cell.muted ? "disabled" : ""}><span>${cell.day}</span></button>`;
      }).join("")}
    </div>
    <div class="calendar-legend"><span class="dot upload"></span>${ui("uploaded")}<span class="dot pending"></span>${ui("pending")}</div>
  `;
}

function recordTableMarkup(reportType, records, jobs = []) {
  if (!records.length && !jobs.length) return `<div class="empty-records">${ui("noRecords")}</div>`;
  return `
    <table class="record-table">
      <thead><tr><th>${ui("date")}</th><th>${ui("well")}</th><th>${ui("reportType")}</th><th>${ui("fileName")}</th><th>${ui("uploadTime")}</th><th>${ui("uploader")}</th><th>${ui("status")}</th><th>${ui("operation")}</th></tr></thead>
      <tbody>
        ${jobs.map((job) => `
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
        `).join("")}
        ${records.map((record) => `
          <tr>
            <td>${escapeHtml(record.reportDate)}</td>
            <td>${escapeHtml(record.wellbore)}</td>
            <td><span class="type-pill">${reportName(reportType)}</span></td>
            <td>${escapeHtml(record.source_file || `${record.wellbore || reportType}_${record.reportDate || "report"}.pdf`)}</td>
            <td>${escapeHtml(formatRecordTime(record.updated_at || record.created_at))}</td>
            <td>${escapeHtml(record.uploader || "本地导入")}</td>
            <td>${recordStatusMarkup(record)}</td>
            <td><button class="link-button" type="button" data-record-preview="${escapeHtml(record.record_id)}" data-report-type="${reportType}">${ui("preview")}</button></td>
          </tr>
        `).join("")}
      </tbody>
    </table>
  `;
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
  const currentSignature = reportSignature(reportType);
  button.disabled = !currentSignature || currentSignature === savedReportSignatures[reportType];
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
    showToast(ui("databaseSaveFailed"));
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
  } catch (error) {
    console.error(error);
    showToast(ui("databaseSaveFailed"));
  }
}

function applyImportedPayload(payload) {
  applyReportFields(payload.report_fields || {});
  setDrillingSourceFile(payload.metadata?.source_file || "");
  rememberRecord("drilling", payload);
  loadRows({
    surveyTable: rowsFromPayload(payload.survey_data, "surveyTable"),
    bhaTable: rowsFromPayload(payload.bha_components, "bhaTable"),
    operationsTable: rowsFromPayload(payload.operations, "operationsTable"),
    costTable: rowsFromPayload(payload.daily_costs, "costTable"),
    bulkTable: rowsFromPayload(payload.bulks, "bulkTable")
  });
  showReportDetail("drilling");
  markReportSaved("drilling");
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function applyImportedCompletionPayload(payload) {
  applyReportFields(payload.report_fields || {}, completionForm);
  rememberRecord("completion", payload);
  loadRows({
    completionOperationsTable: rowsFromPayload(payload.operations, "completionOperationsTable"),
    completionBulkTable: rowsFromPayload(payload.bulks, "completionBulkTable"),
    completionCostTable: rowsFromPayload(payload.daily_costs, "completionCostTable"),
    perforationIntervalsTable: rowsFromPayload(payload.perforation_intervals, "perforationIntervalsTable")
  }, completionTableIds);
  setActiveMenu("completion-daily");
  showReportDetail("completion");
  markReportSaved("completion");
}

function applyImportedWorkoverPayload(payload) {
  applyReportFields(payload.report_fields || {}, workoverForm);
  rememberRecord("workover", payload);
  loadRows({
    workoverOperationsTable: rowsFromPayload(payload.operations, "workoverOperationsTable"),
    workoverBulkTable: rowsFromPayload(payload.bulks, "workoverBulkTable"),
    workoverCostTable: rowsFromPayload(payload.daily_costs, "workoverCostTable"),
    workoverIntervalsTable: rowsFromPayload(payload.perforation_intervals, "workoverIntervalsTable")
  }, workoverTableIds);
  setActiveMenu("workover-daily");
  showReportDetail("workover");
  markReportSaved("workover");
}

function applyImportedMovePayload(payload) {
  applyReportFields(payload.report_fields || {}, moveForm);
  rememberRecord("move", payload);
  loadRows({
    moveOperationsTable: rowsFromPayload(payload.operations, "moveOperationsTable")
  }, moveTableIds);
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
    if (!String(data[name] || "").trim()) issues.push({ level: "error", text: message("required", { field: labelFor(name) }), field: name });
  });

  if (data.reportDate) {
    const reportDate = new Date(`${data.reportDate}T00:00:00`);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    if (reportDate > today) issues.push({ level: "error", text: message("futureDate"), field: "reportDate" });
  }

  const todayMd = toNumber(data.todayMd);
  const prevMd = toNumber(data.prevMd);
  const progress = toNumber(data.progress);
  const computedProgress = Number.isFinite(todayMd) && Number.isFinite(prevMd) ? todayMd - prevMd : 0;
  document.querySelector("#progressComputed").textContent = computedProgress.toFixed(2);
  if (Number.isFinite(todayMd) && Number.isFinite(prevMd) && todayMd < prevMd) issues.push({ level: "error", text: message("mdOrder"), field: "todayMd" });
  if (Number.isFinite(progress) && Math.abs(progress - computedProgress) > 0.5) issues.push({ level: "warning", text: message("progressMismatch", { value: computedProgress.toFixed(2) }), field: "progress" });

  const operations = readTable("operationsTable");
  const operationHours = operations.reduce((sum, row) => sum + (toNumber(row.hours) || 0), 0);
  document.querySelector("#operationHours").textContent = operationHours.toFixed(2);
  if (Math.abs(operationHours - 24) > 0.05) issues.push({ level: "error", text: message("operationHours", { value: operationHours.toFixed(2) }) });
  operations.forEach((row, index) => {
    ["from", "to", "hours", "op_code", "operation_details"].forEach((field) => {
      if (!row[field]) issues.push({ level: "warning", text: message("operationMissing", { row: index + 1, field }) });
    });
    if (!["P", "NPT"].includes(row.op_type)) {
      issues.push({ level: "warning", text: message("operationType", { row: index + 1 }) });
      const control = document.querySelectorAll("#operationsTable tbody tr")[index]?.querySelector("[name='op_type']");
      if (control) control.classList.add("warning-cell");
    }
    if (toNumber(row.hours) <= 0 || toNumber(row.hours) > 24) issues.push({ level: "error", text: message("operationHourRange", { row: index + 1 }) });
  });

  readTable("surveyTable").forEach((row, index) => {
    const md = toNumber(row.md);
    const incl = toNumber(row.incl);
    const dls = toNumber(row.dls);
    if (Number.isFinite(md) && Number.isFinite(todayMd) && md > todayMd) issues.push({ level: "error", text: message("surveyMd", { row: index + 1 }) });
    if (Number.isFinite(incl) && (incl < 0 || incl > 180)) issues.push({ level: "error", text: message("surveyIncl", { row: index + 1 }) });
    if (Number.isFinite(dls) && dls < 0) issues.push({ level: "error", text: message("surveyDls", { row: index + 1 }) });
  });

  const density = toNumber(data.mudDensity);
  if (Number.isFinite(density) && (density < 6 || density > 20)) issues.push({ level: "error", text: message("mudDensity"), field: "mudDensity" });
  const sand = toNumber(data.sand);
  if (Number.isFinite(sand) && sand > 10) issues.push({ level: "warning", text: message("sand"), field: "sand" });

  readTable("bhaTable").forEach((row, index) => {
    const values = [toNumber(row.od), toNumber(row.id), toNumber(row.joints), toNumber(row.length)];
    if (Number.isFinite(values[0]) && Number.isFinite(values[1]) && values[0] < values[1]) issues.push({ level: "error", text: message("bhaOdId", { row: index + 1 }) });
    if (values.some((value) => Number.isFinite(value) && value < 0)) issues.push({ level: "error", text: message("bhaNegative", { row: index + 1 }) });
  });

  readTable("costTable").forEach((row, index) => {
    const amount = toNumber(row.amount);
    if (Number.isFinite(amount) && amount < 0) issues.push({ level: "error", text: message("costNegative", { row: index + 1 }) });
  });

  if ((data.safetyIncident === "Y" || data.environmentIncident === "Y") && !String(data.incidentComments || "").trim()) {
    issues.push({ level: "error", text: message("incidentRequired"), field: "incidentComments" });
  }

  issues.forEach((issue) => {
    if (issue.field && form.elements[issue.field]) form.elements[issue.field].classList.add("invalid");
  });
  renderIssues(issues);
  updateCompletion(required, issues);
  return issues;
}

function validateCompletion() {
  const data = formData(completionForm);
  const issues = [];
  const required = ["event", "reportDate", "reportNo", "wellbore", "rig", "currentOps", "summary24h", "forecast24h"];
  document.querySelectorAll("#completionDailyPage .invalid, #completionDailyPage .warning-cell").forEach((el) => el.classList.remove("invalid", "warning-cell"));

  required.forEach((name) => {
    if (!String(data[name] || "").trim()) issues.push({ level: "error", text: message("required", { field: labelFor(name) }), field: name });
  });

  if (data.reportDate) {
    const reportDate = new Date(`${data.reportDate}T00:00:00`);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    if (reportDate > today) issues.push({ level: "error", text: message("futureDate"), field: "reportDate" });
    if (data.operationStartDate) {
      const startDate = new Date(`${data.operationStartDate}T00:00:00`);
      if (startDate > reportDate) issues.push({ level: "error", text: message("operationStartDate"), field: "operationStartDate" });
    }
  }

  const operations = readTable("completionOperationsTable");
  const operationHours = operations.reduce((sum, row) => sum + (toNumber(row.hours) || 0), 0);
  document.querySelector("#completionOperationHours").textContent = operationHours.toFixed(2);
  if (Math.abs(operationHours - 24) > 0.05) issues.push({ level: "error", text: message("operationHours", { value: operationHours.toFixed(2) }) });
  operations.forEach((row, index) => {
    ["from", "to", "hours", "op_code", "operation_details"].forEach((field) => {
      if (!row[field]) issues.push({ level: "warning", text: message("operationMissing", { row: index + 1, field }) });
    });
    if (!["P", "SC", "NPT"].includes(row.op_type)) {
      issues.push({ level: "warning", text: message("completionOperationType", { row: index + 1 }) });
      const control = document.querySelectorAll("#completionOperationsTable tbody tr")[index]?.querySelector("[name='op_type']");
      if (control) control.classList.add("warning-cell");
    }
    if (toNumber(row.hours) <= 0 || toNumber(row.hours) > 24) issues.push({ level: "error", text: message("operationHourRange", { row: index + 1 }) });
  });

  readTable("completionBulkTable").forEach((row, index) => {
    ["qty_start", "qty_used", "qty_end"].forEach((field) => {
      const value = toNumber(row[field]);
      if (Number.isFinite(value) && value < 0) issues.push({ level: "error", text: message("costNegative", { row: index + 1 }) });
    });
  });

  readTable("completionCostTable").forEach((row, index) => {
    const amount = toNumber(row.amount);
    if (Number.isFinite(amount) && amount < 0) issues.push({ level: "error", text: message("costNegative", { row: index + 1 }) });
  });

  const intervals = readTable("perforationIntervalsTable");
  document.querySelector("#completionIntervalCount").textContent = intervals.length;
  intervals.forEach((row, index) => {
    const topMd = toNumber(row.top_md);
    const baseMd = toNumber(row.base_md);
    const length = toNumber(row.length);
    if (Number.isFinite(topMd) && Number.isFinite(baseMd) && baseMd < topMd) issues.push({ level: "error", text: message("intervalDepth", { row: index + 1 }) });
    if (Number.isFinite(length) && length < 0) issues.push({ level: "error", text: message("intervalLength", { row: index + 1 }) });
  });

  issues.forEach((issue) => {
    if (issue.field && completionForm.elements[issue.field]) completionForm.elements[issue.field].classList.add("invalid");
  });
  renderCompletionIssues(issues);
  updateCompletionProgress(required, issues);
  return issues;
}

function validateWorkover() {
  const data = formData(workoverForm);
  const issues = [];
  const required = ["event", "reportDate", "reportNo", "wellbore", "rig", "currentOps", "summary24h", "forecast24h"];
  document.querySelectorAll("#workoverDailyPage .invalid, #workoverDailyPage .warning-cell").forEach((el) => el.classList.remove("invalid", "warning-cell"));

  required.forEach((name) => {
    if (!String(data[name] || "").trim()) issues.push({ level: "error", text: message("required", { field: labelFor(name) }), field: name });
  });

  if (data.reportDate) {
    const reportDate = new Date(`${data.reportDate}T00:00:00`);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    if (reportDate > today) issues.push({ level: "error", text: message("futureDate"), field: "reportDate" });
    if (data.operationStartDate) {
      const startDate = new Date(`${data.operationStartDate}T00:00:00`);
      if (startDate > reportDate) issues.push({ level: "error", text: message("operationStartDate"), field: "operationStartDate" });
    }
  }

  const operations = readTable("workoverOperationsTable");
  const operationHours = operations.reduce((sum, row) => sum + (toNumber(row.hours) || 0), 0);
  document.querySelector("#workoverOperationHours").textContent = operationHours.toFixed(2);
  if (Math.abs(operationHours - 24) > 0.05) issues.push({ level: "error", text: message("operationHours", { value: operationHours.toFixed(2) }) });
  operations.forEach((row, index) => {
    ["from", "to", "hours", "op_code", "operation_details"].forEach((field) => {
      if (!row[field]) issues.push({ level: "warning", text: message("operationMissing", { row: index + 1, field }) });
    });
    if (!["P", "SC", "NPT"].includes(row.op_type)) {
      issues.push({ level: "warning", text: message("workoverOperationType", { row: index + 1 }) });
      const control = document.querySelectorAll("#workoverOperationsTable tbody tr")[index]?.querySelector("[name='op_type']");
      if (control) control.classList.add("warning-cell");
    }
    if (toNumber(row.hours) <= 0 || toNumber(row.hours) > 24) issues.push({ level: "error", text: message("operationHourRange", { row: index + 1 }) });
  });

  readTable("workoverBulkTable").forEach((row, index) => {
    ["qty_start", "qty_used", "qty_end"].forEach((field) => {
      const value = toNumber(row[field]);
      if (Number.isFinite(value) && value < 0) issues.push({ level: "error", text: message("costNegative", { row: index + 1 }) });
    });
  });

  readTable("workoverCostTable").forEach((row, index) => {
    const amount = toNumber(row.amount);
    if (Number.isFinite(amount) && amount < 0) issues.push({ level: "error", text: message("costNegative", { row: index + 1 }) });
  });

  const intervals = readTable("workoverIntervalsTable");
  document.querySelector("#workoverIntervalCount").textContent = intervals.length;
  intervals.forEach((row, index) => {
    const topMd = toNumber(row.top_md);
    const baseMd = toNumber(row.base_md);
    const length = toNumber(row.length);
    if (Number.isFinite(topMd) && Number.isFinite(baseMd) && baseMd < topMd) issues.push({ level: "error", text: message("intervalDepth", { row: index + 1 }) });
    if (Number.isFinite(length) && length < 0) issues.push({ level: "error", text: message("intervalLength", { row: index + 1 }) });
  });

  issues.forEach((issue) => {
    if (issue.field && workoverForm.elements[issue.field]) workoverForm.elements[issue.field].classList.add("invalid");
  });
  renderWorkoverIssues(issues);
  updateWorkoverProgress(required, issues);
  return issues;
}

function validateMove() {
  const data = formData(moveForm);
  const issues = [];
  const required = ["event", "reportDate", "reportNo", "wellbore", "rig", "currentOps", "summary24h", "forecast24h"];
  document.querySelectorAll("#moveDailyPage .invalid, #moveDailyPage .warning-cell").forEach((el) => el.classList.remove("invalid", "warning-cell"));

  required.forEach((name) => {
    if (!String(data[name] || "").trim()) issues.push({ level: "error", text: message("required", { field: labelFor(name) }), field: name });
  });

  if (data.reportDate) {
    const reportDate = new Date(`${data.reportDate}T00:00:00`);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    if (reportDate > today) issues.push({ level: "error", text: message("futureDate"), field: "reportDate" });
  }

  const operations = readTable("moveOperationsTable");
  const operationHours = operations.reduce((sum, row) => sum + (toNumber(row.hours) || 0), 0);
  document.querySelector("#moveOperationHours").textContent = operationHours.toFixed(2);
  if (Math.abs(operationHours - 24) > 0.05) issues.push({ level: "error", text: message("operationHours", { value: operationHours.toFixed(2) }) });
  operations.forEach((row, index) => {
    ["from", "to", "hours", "op_code", "operation_details"].forEach((field) => {
      if (!row[field]) issues.push({ level: "warning", text: message("operationMissing", { row: index + 1, field }) });
    });
    if (!["P", "SC", "NPT"].includes(row.op_type)) {
      issues.push({ level: "warning", text: message("moveOperationType", { row: index + 1 }) });
      const control = document.querySelectorAll("#moveOperationsTable tbody tr")[index]?.querySelector("[name='op_type']");
      if (control) control.classList.add("warning-cell");
    }
    if (toNumber(row.hours) <= 0 || toNumber(row.hours) > 24) issues.push({ level: "error", text: message("operationHourRange", { row: index + 1 }) });
  });

  issues.forEach((issue) => {
    if (issue.field && moveForm.elements[issue.field]) moveForm.elements[issue.field].classList.add("invalid");
  });
  renderMoveIssues(issues);
  updateMoveProgress(required, issues);
  return issues;
}

function renderIssues(issues) {
  document.querySelector("#issueCount").textContent = issues.length;
  if (!issues.length) {
    issuesEl.innerHTML = `<div class="issue ok">${ui("noIssues")}</div>`;
    return;
  }
  issuesEl.innerHTML = issues.map((issue) => `<div class="issue ${issue.level}">${issue.text}</div>`).join("");
}

function renderCompletionIssues(issues) {
  document.querySelector("#completionIssueCount").textContent = issues.length;
  if (!issues.length) {
    completionIssuesEl.innerHTML = `<div class="issue ok">${ui("noIssues")}</div>`;
    return;
  }
  completionIssuesEl.innerHTML = issues.map((issue) => `<div class="issue ${issue.level}">${issue.text}</div>`).join("");
}

function renderWorkoverIssues(issues) {
  document.querySelector("#workoverIssueCount").textContent = issues.length;
  if (!issues.length) {
    workoverIssuesEl.innerHTML = `<div class="issue ok">${ui("noIssues")}</div>`;
    return;
  }
  workoverIssuesEl.innerHTML = issues.map((issue) => `<div class="issue ${issue.level}">${issue.text}</div>`).join("");
}

function renderMoveIssues(issues) {
  document.querySelector("#moveIssueCount").textContent = issues.length;
  if (!issues.length) {
    moveIssuesEl.innerHTML = `<div class="issue ok">${ui("noIssues")}</div>`;
    return;
  }
  moveIssuesEl.innerHTML = issues.map((issue) => `<div class="issue ${issue.level}">${issue.text}</div>`).join("");
}

function updateCompletion(required, issues) {
  const data = formData();
  const filledRequired = required.filter((name) => String(data[name] || "").trim()).length;
  const hasFatal = issues.some((issue) => issue.level === "error");
  const base = Math.round((filledRequired / required.length) * 100);
  document.querySelector("#completionRate").textContent = `${hasFatal ? Math.min(base, 85) : base}%`;
}

function updateCompletionProgress(required, issues) {
  const data = formData(completionForm);
  const filledRequired = required.filter((name) => String(data[name] || "").trim()).length;
  const hasFatal = issues.some((issue) => issue.level === "error");
  const base = Math.round((filledRequired / required.length) * 100);
  document.querySelector("#completionCompletionRate").textContent = `${hasFatal ? Math.min(base, 85) : base}%`;
}

function updateWorkoverProgress(required, issues) {
  const data = formData(workoverForm);
  const filledRequired = required.filter((name) => String(data[name] || "").trim()).length;
  const hasFatal = issues.some((issue) => issue.level === "error");
  const base = Math.round((filledRequired / required.length) * 100);
  document.querySelector("#workoverCompletionRate").textContent = `${hasFatal ? Math.min(base, 85) : base}%`;
}

function updateMoveProgress(required, issues) {
  const data = formData(moveForm);
  const filledRequired = required.filter((name) => String(data[name] || "").trim()).length;
  const hasFatal = issues.some((issue) => issue.level === "error");
  const base = Math.round((filledRequired / required.length) * 100);
  document.querySelector("#moveCompletionRate").textContent = `${hasFatal ? Math.min(base, 85) : base}%`;
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
    addRow(button.dataset.addRow);
    validateForTable(button.dataset.addRow);
    updateSaveButton(tableReportType(button.dataset.addRow));
  });
});

document.querySelectorAll("[data-save-report]").forEach((button) => {
  button.addEventListener("click", () => {
    saveCurrentReport(button.dataset.saveReport);
  });
});

document.querySelectorAll("[data-back-records]").forEach((button) => {
  button.addEventListener("click", () => {
    showReportRecords(button.dataset.backRecords);
  });
});

document.addEventListener("click", (event) => {
  const wellButton = event.target.closest("[data-well]");
  if (wellButton) {
    const reportType = wellButton.dataset.reportType;
    recordState[reportType].selectedWell = wellButton.dataset.well;
    recordState[reportType].selectedDate = "";
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
    renderRecordDashboard(reportType);
    return;
  }
  const uploadButton = event.target.closest("[data-record-upload]");
  if (uploadButton) {
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
  }
  const addWellButton = event.target.closest(".add-well-button");
  if (addWellButton) {
    const dashboard = addWellButton.closest("[data-record-dashboard]");
    const reportType = dashboard?.dataset.recordDashboard;
    if (reportType) {
      const wellName = prompt(ui("addWell") + " — " + ui("searchWell") + ":");
      if (wellName && wellName.trim()) {
        recordState[reportType].selectedWell = wellName.trim();
        renderRecordDashboard(reportType);
      }
    }
  }
});

document.addEventListener("input", (event) => {
  const search = event.target.closest("[data-well-search]");
  if (!search) return;
  const reportType = search.dataset.wellSearch;
  const term = search.value.trim().toLowerCase();
  recordState[reportType].search = search.value.trim();
  search.closest(".well-panel")?.querySelectorAll("[data-well]").forEach((button) => {
    button.hidden = term && !button.dataset.well.toLowerCase().includes(term);
  });
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
  button.addEventListener("click", () => applyLanguage(button.dataset.lang));
});

document.querySelectorAll(".menu-link").forEach((link) => {
  link.addEventListener("click", (event) => {
    event.preventDefault();
    link.closest(".menu-group")?.classList.add("open");
    link.closest(".menu-group")?.querySelector(".menu-group-toggle")?.setAttribute("aria-expanded", "true");
    setActiveMenu(link.dataset.menuTarget);
  });
});

document.querySelector("#importPdf").addEventListener("click", () => {
  const input = document.querySelector("#pdfInput");
  input.value = "";
  input.click();
});
document.querySelector("#pdfInput").addEventListener("change", (event) => {
  importReportFiles("drilling", event.target.files);
});
document.querySelector("#importCompletionPdf").addEventListener("click", () => {
  const input = document.querySelector("#completionPdfInput");
  input.value = "";
  input.click();
});
document.querySelector("#completionPdfInput").addEventListener("change", (event) => {
  importReportFiles("completion", event.target.files);
});
document.querySelector("#importWorkoverPdf").addEventListener("click", () => {
  const input = document.querySelector("#workoverPdfInput");
  input.value = "";
  input.click();
});
document.querySelector("#workoverPdfInput").addEventListener("change", (event) => {
  importReportFiles("workover", event.target.files);
});
document.querySelector("#importMovePdf").addEventListener("click", () => {
  const input = document.querySelector("#movePdfInput");
  input.value = "";
  input.click();
});
document.querySelector("#movePdfInput").addEventListener("change", (event) => {
  importReportFiles("move", event.target.files);
});
form.addEventListener("input", () => { validate(); updateSaveButton("drilling"); });
form.addEventListener("change", () => { validate(); updateSaveButton("drilling"); });
completionForm.addEventListener("input", () => { validateCompletion(); updateSaveButton("completion"); });
completionForm.addEventListener("change", () => { validateCompletion(); updateSaveButton("completion"); });
workoverForm.addEventListener("input", () => { validateWorkover(); updateSaveButton("workover"); });
workoverForm.addEventListener("change", () => { validateWorkover(); updateSaveButton("workover"); });
moveForm.addEventListener("input", () => { validateMove(); updateSaveButton("move"); });
moveForm.addEventListener("change", () => { validateMove(); updateSaveButton("move"); });

loadRows();
loadRows({}, completionTableIds);
loadRows({}, workoverTableIds);
loadRows({}, moveTableIds);
applyLanguage(currentLanguage);
setDrillingSourceFile();
setActiveMenu("drilling-daily");
Object.keys(savedReportSignatures).forEach((reportType) => {
  savedReportSignatures[reportType] = reportSignature(reportType);
});
updateAllSaveButtons();
