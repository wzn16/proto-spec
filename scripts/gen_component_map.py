#!/usr/bin/env python3
"""从 components.css 生成 references/component-map.md（页面主键 → 用途 → 变体/状态/子元素 → 对应框架组件）。

用法: python3 gen_component_map.py [--css starter/assets/components.css] [--out references/component-map.md]
"""
from __future__ import annotations
import argparse, re, sys
from collections import defaultdict
from pathlib import Path

MAP = {
 "c-btn": ("按钮", "ElButton / Button"), "c-input": ("单行输入", "ElInput / Input"),
 "c-textarea": ("多行文本", "ElInput textarea / Input.TextArea"), "c-select": ("下拉选择", "ElSelect / Select"),
 "c-checkbox": ("复选", "ElCheckbox / Checkbox"), "c-radio": ("单选", "ElRadio / Radio"),
 "c-switch": ("开关", "ElSwitch / Switch"), "c-tag": ("标签/徽标", "ElTag / Tag"),
 "c-alert": ("提示条", "ElAlert / Alert"), "c-field": ("表单字段容器", "ElFormItem / Form.Item"),
 "c-form-grid": ("表单栅格", "ElRow+ElCol / Row+Col"), "c-form-section": ("表单分组", "ElCard / Divider"),
 "c-form-footer": ("表单粘底操作条", "自定义"), "c-table": ("只读快照表", "ElTable / Table"),
 "c-data-table": ("数据表（冻结/密度/分组）", "ElTable / Table"), "c-table-scroll": ("表格横向滚动容器", "自定义"),
 "c-pagination": ("分页", "ElPagination / Pagination"), "c-pager": ("简化分页条", "自定义"),
 "c-modal": ("弹窗", "ElDialog / Modal"), "c-drawer": ("抽屉（默认浮动）", "ElDrawer / Drawer"),
 "c-dropdown": ("下拉菜单", "ElDropdown / Dropdown"), "c-toast": ("轻提示", "ElMessage / message"),
 "c-empty": ("空状态", "ElEmpty / Empty"), "c-skeleton": ("骨架屏", "ElSkeleton / Skeleton"),
 "c-card": ("卡片", "ElCard / Card"), "c-desc": ("描述列表", "ElDescriptions / Descriptions"),
 "c-kv": ("键值列表", "ElDescriptions 简化 / Descriptions"), "c-nav": ("侧栏导航", "ElMenu / Menu"),
 "c-breadcrumb": ("面包屑", "ElBreadcrumb / Breadcrumb"), "c-tabs": ("页签", "ElTabs / Tabs"),
 "c-tabbar": ("工作台页签条", "自定义"), "c-tree": ("层级树", "ElTree / Tree"),
 "c-timeline": ("时间线", "ElTimeline / Timeline"), "c-segmented": ("分段器", "ElSegmented / Segmented"),
 "c-detail": ("详情面板", "ElDescriptions 组合"), "c-board": ("看板（状态列）", "自定义 / Kanban"),
 "c-workbench": ("工作台外壳", "Layout"), "c-side-menu": ("工作台侧栏菜单", "Menu"),
 "c-kpi-row": ("指标卡行", "ElRow+ElStatistic / Row+Statistic"), "c-kpi": ("指标卡", "ElStatistic / Statistic"),
 "c-qbar": ("查询条（下划线式）", "ElForm inline / Form"), "c-chips": ("条件 chips", "ElTag closable / Tag"),
 "c-toolbar": ("工具栏", "自定义"), "c-bulkbar": ("批量操作条", "自定义"),
 "c-split": ("主从两栏布局", "Layout Sider / Layout"), "c-list-rows": ("列表行流", "自定义"),
 "c-filter-drawer": ("筛选抽屉", "Drawer + Form"), "c-col-code": ("列宽档位：编码", "column width"),
 "c-col-num": ("列宽档位：数字", "column width"), "c-col-ops": ("列宽档位：操作", "column width"),
}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--css", default="starter/assets/components.css")
    ap.add_argument("--out", default="references/component-map.md")
    args = ap.parse_args()
    css = Path(args.css).read_text(encoding="utf-8")
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    classes = defaultdict(lambda: {"variants": set(), "children": set(), "states": set()})
    for sel in re.findall(r"([^{}]+)\{", css):
        for cls in re.findall(r"\.(c-[a-z0-9-]+)", sel):
            base = cls.split("--")[0]
            rec = classes[base]
            if "--" in cls:
                rec["variants"].add(cls.split("--", 1)[1])
            if "__" in cls:
                rec["children"].add(cls.split("__", 1)[1])
            m = re.search(r"\.(is-[a-z-]+)", sel)
            if m:
                rec["states"].add(m.group(1))
    rows = []
    for base in sorted(classes):
        rec = classes[base]
        purpose, el = MAP.get(base, ("内部结构类", "—"))
        rows.append("| `{}` | {} | {} | {} | {} | {} |".format(
            base, purpose, "/".join(sorted(rec["variants"])) or "—",
            "/".join(sorted(rec["states"])) or "—",
            "/".join(sorted(rec["children"])) or "—", el))
    doc = ["# 组件映射（Component Map）", "",
           "> 由 `scripts/gen_component_map.py` 从 `{}` 解析生成；改动组件后请重跑本脚本。".format(args.css),
           "> 生成命令：`python3 scripts/gen_component_map.py`", "",
           "共 {} 个基础类。变体 `--x`、运行时状态 `is-*`、子元素 `__x`。".format(len(rows)), "",
           "| 基础类 | 用途 | 变体 | 运行时状态 | 关键子元素 | 对应 Element Plus / AntD |",
           "| --- | --- | --- | --- | --- | --- |"] + rows + ["",
           "## 使用纪律", "",
           "1. 变体只通过 `--x` 修饰，状态只通过 `is-*`；不要用行内 style 覆盖。",
           "2. 子元素结构由组件决定，页面不得自造同义子元素。",
           "3. 用途为「内部结构类」的不在页面直接使用。"]
    Path(args.out).write_text("\n".join(doc) + "\n", encoding="utf-8")
    print("[map] {} 个基础类 → {}".format(len(rows), args.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
