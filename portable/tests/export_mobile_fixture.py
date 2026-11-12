"""Export portable YAML grid values for Chromium tests."""
import json
import pathlib
import yaml
root = pathlib.Path(__file__).resolve().parents[1]
result = {}
for name, field in (("heating-control","delete"),("manage-schedules","edit")):
    doc = yaml.safe_load((root/"dashboard"/(name+".yaml")).read_text())
    a = next(x for x in doc["cards"] if x["type"] == "custom:auto-entities")
    st = a["filter"]["include"][0]["options"]["styles"]
    def prop(group,key):
        return next(x[key] for x in st[group] if key in x)
    result[name] = {
        "field":field,"areas":prop("grid","grid-template-areas"),
        "columns":prop("grid","grid-template-columns"),
        "rows":prop("grid","grid-template-rows"),
        "gap":prop("grid","row-gap"),
        "min_height":prop("card","min-height"),
        "field_area":next(x["grid-area"] for x in st["custom_fields"][field] if "grid-area" in x),
        "button": a["filter"]["include"][0]["options"]["custom_fields"][field]["card"]["icon"],
        "mobile_columns": a["card"].get("layout",{}).get("mediaquery",{}).get("(max-width: 600px)",{}).get("grid-template-columns")
    }
(root/"tests"/"portable-layout.json").write_text(json.dumps(result))
