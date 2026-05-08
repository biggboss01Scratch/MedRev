#!/usr/bin/env python3
"""Generate extra synthetic kidney test cases for page-1/page-2 coverage.

The script is idempotent: it creates or updates a small set of synthetic cases,
then rewrites the organ-level JSON files and leaves the task generator to rebuild
tasks from those JSON inputs.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from PIL import Image, ImageDraw, ImageFont


BASE = Path.cwd()
TEST_DATA = BASE / "test_data"
ORGAN_ROOT = TEST_DATA / "肾脏" / "普通" / "成人"
META_DIR = TEST_DATA / "整理后标注目录" / "肾脏"


def load_json(path: Path):
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def draw_placeholder_image(path: Path, title: str, subtitle: str, accent: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (640, 480), color=accent)
    draw = ImageDraw.Draw(img)
    try:
        font_title = ImageFont.truetype("arial.ttf", 36)
        font_body = ImageFont.truetype("arial.ttf", 22)
    except Exception:
        try:
            font_title = ImageFont.truetype("DejaVuSans.ttf", 36)
            font_body = ImageFont.truetype("DejaVuSans.ttf", 22)
        except Exception:
            font_title = ImageFont.load_default()
            font_body = ImageFont.load_default()

    draw.rounded_rectangle([24, 24, 616, 456], radius=24, outline="white", width=4)
    draw.text((48, 70), title, fill="white", font=font_title)
    draw.text((48, 135), subtitle, fill="white", font=font_body)
    draw.text((48, 390), path.name, fill="white", font=font_body)
    img.save(path, quality=92)


def rel(path: Path) -> str:
    return path.as_posix()


def case_dir(case_name: str) -> Path:
    return ORGAN_ROOT / case_name


def ensure_case_report(case_name: str, has_report: bool, label: str, accent: str) -> None:
    folder = case_dir(case_name)
    folder.mkdir(parents=True, exist_ok=True)
    if has_report:
        draw_placeholder_image(folder / "病例报告.jpg", f"{case_name} 病例报告", label, accent)


def main() -> None:
    META_DIR.mkdir(parents=True, exist_ok=True)

    gt_path = META_DIR / "GT.json"
    pred_path = META_DIR / "pred.json"
    organ_path = META_DIR / "organ.json"

    gt_list: List[Dict] = load_json(gt_path)
    pred_list: List[Dict] = load_json(pred_path)
    organ_list: List[Dict] = load_json(organ_path)

    gt_by_name = {row["image_name"]: row for row in gt_list}
    pred_by_name = {row["image_name"]: row for row in pred_list}
    organ_by_name = {row["image_name"]: row for row in organ_list}

    cases = [
        {
            "case_name": "case_005",
            "report": True,
            "accent": "#5271ff",
            "images": [
                {
                    "image_name": "005_1.jpg",
                    "has_gt": True,
                    "gt": [{"category": "cyst", "bbox": [110, 90, 255, 240], "confidence": 1.0}],
                    "pred": [{"category": "tumor", "bbox": [108, 88, 252, 236], "confidence": 0.93}],
                    "organ_present": None,
                },
                {
                    "image_name": "005_2.jpg",
                    "has_gt": True,
                    "gt": [{"category": "kidney", "bbox": [68, 64, 312, 268], "confidence": 1.0}],
                    "pred": [{"category": "kidney", "bbox": [70, 66, 310, 266], "confidence": 0.97}],
                    "organ_present": None,
                },
            ],
        },
        {
            "case_name": "case_006",
            "report": True,
            "accent": "#ff7a59",
            "images": [
                {
                    "image_name": "006_1.jpg",
                    "has_gt": True,
                    "gt": [{"category": "stone", "bbox": [140, 100, 280, 240], "confidence": 1.0}],
                    "pred": [{"category": "tumor", "bbox": [138, 98, 278, 238], "confidence": 0.91}],
                    "organ_present": None,
                },
                {
                    "image_name": "006_2.jpg",
                    "has_gt": True,
                    "gt": [{"category": "cyst", "bbox": [96, 84, 246, 230], "confidence": 1.0}],
                    "pred": [{"category": "cyst", "bbox": [98, 86, 244, 228], "confidence": 0.94}],
                    "organ_present": None,
                },
            ],
        },
        {
            "case_name": "case_007",
            "report": True,
            "accent": "#2aa876",
            "images": [
                {
                    "image_name": "007_1.jpg",
                    "has_gt": False,
                    "gt": [],
                    "pred": [{"category": "cyst", "bbox": [120, 82, 262, 226], "confidence": 0.89}],
                    "organ_present": True,
                },
                {
                    "image_name": "007_2.jpg",
                    "has_gt": False,
                    "gt": [],
                    "pred": [{"category": "kidney", "bbox": [100, 76, 284, 240], "confidence": 0.87}],
                    "organ_present": True,
                },
            ],
        },
        {
            "case_name": "case_008",
            "report": False,
            "accent": "#7d5cff",
            "images": [
                {
                    "image_name": "008_1.jpg",
                    "has_gt": False,
                    "gt": [],
                    "pred": [{"category": "tumor", "bbox": [142, 96, 286, 236], "confidence": 0.86}],
                    "organ_present": None,
                },
            ],
        },
        {
            "case_name": "case_009",
            "report": True,
            "accent": "#d84d8f",
            "images": [
                {
                    "image_name": "009_1.jpg",
                    "has_gt": False,
                    "gt": [],
                    "pred": [{"category": "kidney", "bbox": [132, 90, 286, 238], "confidence": 0.90}],
                    "organ_present": True,
                },
                {
                    "image_name": "009_2.jpg",
                    "has_gt": False,
                    "gt": [],
                    "pred": [{"category": "stone", "bbox": [150, 120, 262, 238], "confidence": 0.88}],
                    "organ_present": True,
                },
            ],
        },
    ]

    for case in cases:
        case_name = case["case_name"]
        ensure_case_report(case_name, case["report"], f"{case_name} synthetic kidney case", case["accent"])
        for item in case["images"]:
            image_path = case_dir(case_name) / item["image_name"]
            draw_placeholder_image(
                image_path,
                f"{case_name} / {item['image_name']}",
                "synthetic test image",
                case["accent"],
            )

            if item["has_gt"]:
                gt_by_name[item["image_name"]] = {
                    "image_name": item["image_name"],
                    "image_path": rel(image_path),
                    "annotations": item["gt"],
                }
            pred_by_name[item["image_name"]] = {
                "image_name": item["image_name"],
                "model_version": "v2",
                "predictions": item["pred"],
            }
            if item["organ_present"] is not None:
                organ_by_name[item["image_name"]] = {
                    "image_name": item["image_name"],
                    "organ_present": item["organ_present"],
                    "confidence": 0.91 if item["organ_present"] else 0.99,
                }

    gt_list = [gt_by_name[k] for k in sorted(gt_by_name.keys())]
    pred_list = [pred_by_name[k] for k in sorted(pred_by_name.keys())]
    organ_list = [organ_by_name[k] for k in sorted(organ_by_name.keys())]

    save_json(gt_path, gt_list)
    save_json(pred_path, pred_list)
    save_json(organ_path, organ_list)

    print(f"Updated {gt_path} with {len(gt_list)} GT records")
    print(f"Updated {pred_path} with {len(pred_list)} prediction records")
    print(f"Updated {organ_path} with {len(organ_list)} organ records")


if __name__ == "__main__":
    main()
