# JSON 字段说明（GT / organ / pred）

本文按 `GT.json`、`organ.json`、`pred.json` 分别说明 `images`、`annotations`、`categories` 的字段含义。

---

## 1. GT.json

### images
- `id`：图片唯一 ID（供 `annotations.image_id` 关联）。
- `file_name`：图片文件名（仅展示，不保证全局唯一）。
- `width` / `height`：图像宽高（像素）。
- `image_relpath`：相对数据根目录路径（推荐作为唯一主键）。
- `image_abspath`：图片绝对路径（可直接读取原图）。
- `case_relpath`：病例目录相对路径（用于病例分组）。
- `organ`：器官名（如 `肾脏`）。

### annotations
- `id`：标注唯一 ID。
- `image_id`：关联到 `images.id`。
- `category_id`：关联到 `categories.id`。
- `bbox`：框坐标，格式 `[x, y, w, h]`（像素坐标）。
- `area`：框面积。
- `iscrowd`：COCO 兼容字段，当前一般为 `0`。
- `segmentation`：分割多边形（若有）。
- `source_note`：来源标注备注（透传字段）。
- `source_category_raw`：原始标注类别名（透传字段，便于追溯）。

### categories
- `id`：类别 ID。
- `name`：类别名称（当前为拼音名）。
- `supercategory`：上位类（当前为器官名）。
- `is_negative`：是否阴性类别标记。

---

## 2. organ.json

用途：器官存在性结果（可用于页面二前置筛选）。

### images
- `id`：图片唯一 ID。
- `image_name` / `file_name`：图片文件名。
- `image_relpath`：相对路径（推荐主键）。
- `image_abspath`：绝对路径。
- `case_relpath`：病例相对路径。
- `width` / `height`：图像宽高。
- `organ`：器官名。
- `has_organ`：是否检测到器官（`kept_count > 0`）。
- `best_score`：该图器官检测最高分。
- `best_category`：最高分对应类别。
- `kept_count`：阈值+NMS 后保留框数量。

### annotations
- `id`：标注唯一 ID。
- `image_id`：关联 `images.id`。
- `category_id`：关联 `categories.id`。
- `bbox`：`[x, y, w, h]`。
- `bbox_xyxy`：`[x1, y1, x2, y2]`。
- `area`：框面积。
- `iscrowd`：固定为 `0`。
- `score`：置信度分数。
- `model_class_id`：模型原始类别 ID。

### categories
- `id`：类别 ID。
- `name`：类别名称。

---

## 3. pred.json

用途：伪标签结果（页面二主要使用）。

### images
- `id`：图片唯一 ID。
- `file_name`：图片文件名。
- `width` / `height`：图像宽高。
- `image_relpath`：相对路径（推荐主键）。
- `image_abspath`：绝对路径。
- `case_relpath`：病例相对路径。
- `organ`：器官名。

### annotations
- `id`：标注唯一 ID。
- `image_id`：关联 `images.id`。
- `category_id`：关联 `categories.id`。
- `bbox`：`[x, y, w, h]`。
- `bbox_xyxy`：`[x1, y1, x2, y2]`。
- `area`：框面积。
- `iscrowd`：固定为 `0`。
- `score`：置信度分数。
- `model_class_id`：模型原始类别 ID（用于追溯模型输出类别索引）。

### categories
- `id`：类别 ID。
- `name`：类别名称（当前为拼音名）。

---

## 4. 使用建议

- 业务关联主键优先使用 `image_relpath`，不要仅依赖 `file_name`。
- 跨 JSON 对齐图片时，优先按 `image_relpath` 匹配。
- 页面一主要依赖 `GT.json`；页面二主要依赖 `organ.json` + `pred.json`。
