from __future__ import annotations


REPORT_TYPES = {"drilling", "completion", "workover"}

REPORT_TYPE_ORDER = ("drilling", "completion", "workover")

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
    "wellboreNo", "dfs", "todayMd", "prevMd", "progress", "rotHrsToday", "avgRopSlide", "avgRopRot",
    "dailyCost", "cumulativeCost", "afeCost", "supervisor1", "supervisor2", "engineer", "pamEngineer",
    "geologist", "totalPersonnel", "lastCasing", "lastCasingSize",
    "lastCasingDepth", "nextCasing", "nextCasingSize", "nextCasingDepth", "formTestType", "formTestEmw",
    "lastBopPressTest", "pumpRate", "pumpPress", "stringWeightUp", "stringWeightDown",
    "stringWeightUpDown", "torqueOffBottom", "torqueOnBottom",
    "mudEngineer", "sampleFrom", "mudType", "mudTime", "mudMd", "mudDensity",
    "mudTemperature", "rheologyTemp", "viscosity", "pv", "yp", "gel10s", "gel10m",
    "gel30m", "apiWl", "oilPercent", "waterPercent", "sand", "ecd", "mudComments",
    "bitNo", "bitSize", "bitManufacturer", "bitSerial", "bitWearIodl", "bitWearBgor", "bhaNo", "bhaMdIn",
    "bhaMdOut", "bhaTotalLength", "safetyIncident", "environmentIncident",
    "daysSinceRi", "daysSinceLta", "incidentComments", "groundElev", "afeMdDays",
]

COMPLETION_FIELD_COLUMNS = COMMON_FIELD_COLUMNS + [
    "completionNo", "wellboreNo", "groundElev", "dol", "dfs", "rigContractName",
    "description", "operationStartDate", "afeCost", "dailyCost", "cumulativeCost",
    "supervisor1", "supervisor2", "engineer", "pamEngineer", "geologist",
    "totalPersonnel", "safetyComments",
]

WORKOVER_FIELD_COLUMNS = COMMON_FIELD_COLUMNS + [
    "workoverNo", "wellboreNo", "groundElev", "dol", "dfs", "rigContractName",
    "description", "operationStartDate", "afeCost", "dailyCost",
    "cumulativeCost", "supervisor1", "supervisor2", "engineer", "pamEngineer",
    "geologist", "totalPersonnel", "safetyComments",
]

REPORT_TABLES = {
    "drilling": {
        "field_sheet": "drilling_fields",
        "field_columns": DRILLING_FIELD_COLUMNS,
        "multi": {
            "survey_data": "drilling_survey",
            "bha_components": "drilling_bha",
            "operations": "drilling_operations",
            "fluid_losses": "drilling_fluid_losses",
            "bulks": "drilling_bulks",
        },
    },
    "completion": {
        "field_sheet": "completion_fields",
        "field_columns": COMPLETION_FIELD_COLUMNS,
        "multi": {
            "operations": "completion_operations",
            "bulks": "completion_bulks",
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
            "mud_products": "workover_mud_products",
            "perforation_intervals": "workover_intervals",
        },
    },
}


ROW_COLUMNS = {
    "operations": ["from", "to", "hours", "op_code", "op_sub", "op_type", "operation_details", "system_op_type", "confirmed_op_type"],
    "bulks": ["bulk", "qty_start", "qty_used", "qty_end"],
    "fluid_losses": ["injected_volume_bbl", "returned_volume_bbl"],
    "survey_data": ["md", "incl", "azi", "tvd", "vse", "ns", "ew", "dls", "build"],
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
        "bulks": ["bulk"],
    },
    "completion": {
        "report_fields": [
            "event", "primaryReason", "currentOps", "summary24h", "forecast24h",
            "description", "supervisor1", "supervisor2", "engineer", "pamEngineer",
            "geologist", "safetyComments", "otherRemarks",
        ],
        "operations": ["op_sub", "operation_details"],
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
        "bulks": ["bulk"],
        "mud_products": ["product"],
        "perforation_intervals": ["formation", "charges", "status", "comments"],
    },
}
