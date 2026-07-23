import fs from "node:fs/promises";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const source = "/Users/jason/Documents/厄瓜钻井日报解析/厄瓜多尔资料/华为ai任务资料/安全生产运行重要事宜和异常事件汇总-6月10日.xlsx";
const outputDir = "/Users/jason/Documents/GitHub/drilling-report-parser/tmp/hsse_excel_review/previews";
await fs.mkdir(outputDir, { recursive: true });

const input = await FileBlob.load(source);
const workbook = await SpreadsheetFile.importXlsx(input);
const overview = await workbook.inspect({
  kind: "workbook,sheet,table",
  include: "id,name,values,formulas",
  maxChars: 18000,
  tableMaxRows: 40,
  tableMaxCols: 30,
  tableMaxCellChars: 160,
});
console.log("OVERVIEW", overview.ndjson.slice(0, 4000));

const extracted = [];
const normalizedRecords = [];

const categoryCodes = {
  1: "UNSAFE_BEHAVIOR",
  2: "SAFETY_HAZARD",
  3: "CONCERN_EMPLOYEE",
  4: "PRODUCTION_ANOMALY",
};

function excelSerialToDate(value) {
  if (typeof value !== "number" || !Number.isFinite(value)) return "";
  return new Date(Date.UTC(1899, 11, 30) + value * 86400000)
    .toISOString()
    .slice(0, 10);
}

function normalizeTeam(value) {
  const match = String(value ?? "").trim().match(/^SINOPEC\s*(\d+)$/i);
  return match ? `SINOPEC ${match[1]}` : "";
}

function columnName(index) {
  let value = index + 1;
  let name = "";
  while (value > 0) {
    const remainder = (value - 1) % 26;
    name = String.fromCharCode(65 + remainder) + name;
    value = Math.floor((value - 1) / 26);
  }
  return name;
}

function isIssueDescription(value) {
  const normalized = String(value ?? "")
    .replace(/[。；;，,：:、.\/\\—\-\s]/g, "")
    .toLowerCase();
  return !["", "无", "无异常", "未反馈", "未发生", "无记录", "正常", "na"].includes(normalized);
}

function parseItems(rawValue) {
  const text = String(rawValue ?? "").replace(/\r/g, "").trim();
  const markers = [];
  const regex = /(?:^|\n)\s*([1-4])\s*[.、．]\s*([^\n：:]{0,80})\s*[：:]?/gm;
  let match;
  while ((match = regex.exec(text)) !== null) {
    markers.push({ number: Number(match[1]), start: match.index, contentStart: regex.lastIndex });
  }

  const items = Object.keys(categoryCodes).map((number) => ({
    category_code: categoryCodes[number],
    has_issue: false,
    description: "",
  }));

  if (!markers.length) {
    const fallback = items.find((item) => item.category_code === "PRODUCTION_ANOMALY");
    fallback.description = text;
    fallback.has_issue = isIssueDescription(text);
    return items;
  }

  markers.forEach((marker, index) => {
    const end = index + 1 < markers.length ? markers[index + 1].start : text.length;
    const description = text
      .slice(marker.contentStart, end)
      .replace(/^\s*[：:]?\s*/, "")
      .trim();
    const item = items.find((candidate) => candidate.category_code === categoryCodes[marker.number]);
    item.description = description;
    item.has_issue = isIssueDescription(description);
  });
  return items;
}

for (const sheet of workbook.worksheets.items) {
  const used = sheet.getUsedRange();
  const values = used?.values ?? [];
  extracted.push({ name: sheet.name, address: used?.address, values });
  console.log(`SHEET ${sheet.name} ${used?.address}`);

  const headerIndex = values.findIndex((row) => String(row?.[0] ?? "").trim() === "序号");
  if (headerIndex >= 0) {
    const header = values[headerIndex];
    const startRow = Number(String(used?.address ?? "A1").match(/\d+/)?.[0] ?? 1);
    values.slice(headerIndex + 1).forEach((row, relativeIndex) => {
      const teamCode = normalizeTeam(row?.[2]);
      if (!teamCode) return;
      header.slice(7).forEach((dateValue, dateOffset) => {
        const recordDate = excelSerialToDate(dateValue);
        const rawValue = row?.[dateOffset + 7];
        if (!recordDate || rawValue === null || rawValue === undefined || String(rawValue).trim() === "") return;
        const sourceRow = startRow + headerIndex + 1 + relativeIndex;
        const sourceColumn = columnName(dateOffset + 7);
        normalizedRecords.push({
          record_date: recordDate,
          project_name: String(row?.[1] ?? "").trim(),
          team_code: teamCode,
          organization_name: String(row?.[3] ?? "").trim(),
          discipline: String(row?.[4] ?? "").trim(),
          well_descriptor: String(row?.[5] ?? "").trim(),
          drilled_remaining: String(row?.[6] ?? "").trim(),
          source_sheet: sheet.name,
          source_cell: `${sourceColumn}${sourceRow}`,
          source_row: sourceRow,
          raw_text: String(rawValue).trim(),
          items: parseItems(rawValue),
        });
      });
    });
  }

  const preview = await workbook.render({ sheetName: sheet.name, autoCrop: "all", scale: 1.4, format: "png" });
  const safeName = sheet.name.replace(/[^a-zA-Z0-9_-]+/g, "_");
  await fs.writeFile(`${outputDir}/${safeName}.png`, new Uint8Array(await preview.arrayBuffer()));
}
await fs.writeFile(`${outputDir}/workbook-values.json`, JSON.stringify(extracted, null, 2), "utf8");
await fs.writeFile(
  `${outputDir}/hsse-records.json`,
  JSON.stringify(
    {
      source_file: source,
      record_count: normalizedRecords.length,
      records: normalizedRecords,
    },
    null,
    2,
  ),
  "utf8",
);
console.log(`EXTRACTED ${extracted.length} sheet(s)`);
console.log(`NORMALIZED ${normalizedRecords.length} HSSE record(s)`);
