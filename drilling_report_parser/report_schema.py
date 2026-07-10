from __future__ import annotations


REPORT_TYPES = {"drilling", "completion", "workover", "move"}

REPORT_TYPE_ORDER = ("drilling", "completion", "workover", "move")

COMMON_FIELD_COLUMNS = [
    "record_id",
    "event",
    "reportDate",
    "reportNo",
    "wellbore",
    "rig",
    "primaryReason",
    "afeNumber",
    "refDatum",
    "currentOps",
    "summary24h",
    "forecast24h",
    "otherRemarks",
]

DRILLING_FIELD_COLUMNS = COMMON_FIELD_COLUMNS + [
    "todayMd", "prevMd", "progress", "rotHrsToday", "lastCasing", "lastCasingSize",
    "lastCasingDepth", "nextCasing", "nextCasingSize", "nextCasingDepth", "formTestEmw",
    "lastBopPressTest", "pumpRate", "pumpPress", "stringWeightUpDown", "torqueOnBottom",
    "mudEngineer", "sampleFrom", "mudType", "mudTime", "mudMd", "mudDensity",
    "mudTemperature", "rheologyTemp", "viscosity", "pv", "yp", "gel10s", "gel10m",
    "gel30m", "apiWl", "oilPercent", "waterPercent", "sand", "ecd", "mudComments",
    "bitNo", "bitSize", "bitManufacturer", "bitSerial", "bhaNo", "bhaMdIn",
    "bhaMdOut", "bhaTotalLength", "safetyIncident", "environmentIncident",
    "daysSinceRi", "daysSinceLta", "incidentComments",
]

COMPLETION_FIELD_COLUMNS = COMMON_FIELD_COLUMNS + [
    "description", "operationStartDate", "afeCost", "dailyCost", "cumulativeCost",
    "supervisor1", "supervisor2", "engineer", "pamEngineer", "geologist",
    "totalPersonnel", "safetyComments",
]

WORKOVER_FIELD_COLUMNS = COMMON_FIELD_COLUMNS + [
    "workoverNo", "description", "operationStartDate", "afeCost", "dailyCost",
    "cumulativeCost", "supervisor1", "supervisor2", "engineer", "pamEngineer",
    "geologist", "totalPersonnel", "safetyComments",
]

MOVE_FIELD_COLUMNS = COMMON_FIELD_COLUMNS + [
    "todayMd", "prevMd", "progress", "rotHrsToday", "groundElev", "afeMdDays",
    "wellborePrefix",
]

REPORT_TABLES = {
    "drilling": {
        "field_sheet": "drilling_fields",
        "field_columns": DRILLING_FIELD_COLUMNS,
        "multi": {
            "survey_data": "drilling_survey",
            "bha_components": "drilling_bha",
            "operations": "drilling_operations",
            "daily_costs": "drilling_costs",
            "bulks": "drilling_bulks",
        },
    },
    "completion": {
        "field_sheet": "completion_fields",
        "field_columns": COMPLETION_FIELD_COLUMNS,
        "multi": {
            "operations": "completion_operations",
            "bulks": "completion_bulks",
            "daily_costs": "completion_costs",
            "mud_products": "completion_mud_products",
            "perforation_intervals": "completion_intervals",
        },
    },
    "workover": {
        "field_sheet": "workover_fields",
        "field_columns": WORKOVER_FIELD_COLUMNS,
        "multi": {
            "operations": "workover_operations",
            "bulks": "workover_bulks",
            "daily_costs": "workover_costs",
            "mud_products": "workover_mud_products",
            "perforation_intervals": "workover_intervals",
        },
    },
    "move": {
        "field_sheet": "move_fields",
        "field_columns": MOVE_FIELD_COLUMNS,
        "multi": {
            "operations": "move_operations",
        },
    },
}


ROW_COLUMNS = {
    "operations": ["from", "to", "hours", "op_code", "op_sub", "op_type", "operation_details", "system_op_type", "confirmed_op_type"],
    "bulks": ["bulk", "qty_start", "qty_used", "qty_end"],
    "daily_costs": ["cost_description", "vendor", "amount"],
    "survey_data": ["md", "incl", "azi", "tvd", "vse", "ns", "dls", "build"],
    "bha_components": ["component", "od", "id", "joints", "length"],
    "perforation_intervals": [
        "formation", "top_md", "base_md", "length", "density", "charges", "phase",
        "penetration", "diameter", "date", "status", "comments",
    ],
    "mud_products": ["product", "unit", "received", "used", "returned", "ending"],
}


# Only fields that carry natural-language content are exposed to translation tuning.
TRANSLATION_SCOPE_FIELDS = {
    "drilling": {
        "report_fields": [
            "event", "primaryReason", "currentOps", "summary24h", "forecast24h",
            "lastCasing", "nextCasing", "mudEngineer", "mudType", "mudComments",
            "bitManufacturer", "incidentComments", "otherRemarks",
        ],
        "operations": ["op_sub", "operation_details"],
        "bha_components": ["component"],
        "daily_costs": ["cost_description", "vendor"],
        "bulks": ["bulk"],
    },
    "completion": {
        "report_fields": [
            "event", "primaryReason", "currentOps", "summary24h", "forecast24h",
            "description", "supervisor1", "supervisor2", "engineer", "pamEngineer",
            "geologist", "safetyComments", "otherRemarks",
        ],
        "operations": ["op_sub", "operation_details"],
        "daily_costs": ["cost_description", "vendor"],
        "bulks": ["bulk"],
        "mud_products": ["product"],
        "perforation_intervals": ["formation", "charges", "status", "comments"],
    },
    "workover": {
        "report_fields": [
            "event", "primaryReason", "currentOps", "summary24h", "forecast24h",
            "description", "supervisor1", "supervisor2", "engineer", "pamEngineer",
            "geologist", "safetyComments", "otherRemarks",
        ],
        "operations": ["op_sub", "operation_details"],
        "daily_costs": ["cost_description", "vendor"],
        "bulks": ["bulk"],
        "mud_products": ["product"],
        "perforation_intervals": ["formation", "charges", "status", "comments"],
    },
    "move": {
        "report_fields": ["event", "primaryReason", "currentOps", "summary24h", "forecast24h", "otherRemarks"],
        "operations": ["op_sub", "operation_details"],
    },
}
