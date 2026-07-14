# -*- coding: utf-8 -*-
"""
不合格处理报告渲染器（文字版 .txt + Markdown .md）

只输出纯文本文档，不生成网页(HTML)、Word、Excel 等格式——重实效、不花哨。
不合格处置逻辑以「处置单 + MRB 评审记录」两部分呈现，内容直给、可直接打印或复制流转。

用法：
  python build_report.py                                  # 内置小样本，产出 txt+md
  python build_report.py --data-file nc.json              # 自定义数据
  python build_report.py --out-dir D:/临时                 # 指定输出目录

数据文件（--data-file, JSON）结构：
{
  "nc": {
    "product":"六角头螺栓 M10×40","batch":"B-2606-01","qty":200,
    "stage":"来料检验(IQC)","defect":"螺纹通规无法旋入（中径偏小）",
    "type":"严重","scope":"本批次","urgency":"限时",
    "disposition":"返工","approve_qe":"张__","approve_qm":"李__",
    "rework_record":"车削至中径上限，100%全检","reinspect":"合格196/不合格4","final":"放行(返工后)"
  },
  "mrb": {"date":"2026-07-13","members":"质量/技术/生产/采购",
          "resolution":"返工后全检放行，4件降级评估","owner":"质量工程师","due":"2026-07-15","verify":"重检合格报告"}
}
"""
import argparse
import json
import os
from datetime import date

SAMPLE = {
    "nc": {
        "product": "六角头螺栓 M10×40", "batch": "B-2606-01", "qty": 200,
        "stage": "来料检验(IQC)", "defect": "螺纹通规无法旋入（中径偏小）",
        "type": "严重", "scope": "本批次", "urgency": "限时",
        "disposition": "返工", "approve_qe": "张__", "approve_qm": "李__",
        "rework_record": "车削至中径上限，100%全检", "reinspect": "合格196/不合格4",
        "final": "放行(返工后)",
    },
    "mrb": {
        "date": str(date.today()), "members": "质量/技术/生产/采购",
        "resolution": "返工后全检放行，4件降级评估", "owner": "质量工程师",
        "due": "2026-07-15", "verify": "重检合格报告",
    },
}


def build_md(data):
    """Markdown 版：保留表格与勾选框，便于在支持 MD 的系统中查看。"""
    nc = data["nc"]
    mrb = data.get("mrb", {})
    lines = []
    lines.append("# 不合格品处置与 MRB 评审报告")
    lines.append("")
    lines.append("## 一、不合格处置单")
    lines.append("")
    rows = [
        ("产品名称/型号", nc.get("product", "待填写")),
        ("批次号", nc.get("batch", "待填写")),
        ("数量", nc.get("qty", "待填写")),
        ("发现环节", nc.get("stage", "待填写")),
        ("缺陷描述", nc.get("defect", "待填写")),
        ("不合格类型", nc.get("type", "待填写")),
        ("影响范围", nc.get("scope", "待填写")),
        ("紧急程度", nc.get("urgency", "待填写")),
    ]
    lines.append("| 项目 | 内容 |")
    lines.append("|------|------|")
    for k, v in rows:
        lines.append(f"| {k} | {v} |")
    lines.append("")
    lines.append(f"**处置方式**：■{nc.get('disposition','待填写')}　"
                 "□返修　□让步接收　□降级使用　□报废")
    lines.append("")
    lines.append("**审批签字**")
    lines.append("")
    lines.append(f"- 质量工程师：{nc.get('approve_qe','____')}")
    lines.append(f"- 质量主管：{nc.get('approve_qm','____')}（返修需技术主管加签）")
    lines.append(f"- 客户确认：____（让步涉及客户时必签）")
    lines.append("")
    lines.append(f"**返工/返修记录**：{nc.get('rework_record','-')}")
    lines.append(f"**重新检验**：{nc.get('reinspect','-')}（返工/返修须100%重检）")
    lines.append(f"**最终处置**：■{nc.get('final','待填写')}")
    lines.append("")
    lines.append("> 铁律：返工≠返修；返工后100%重检，返修须100%重检+专项检验；"
                 "返工返修>2次强制报废；让步须限量/限期/限批。")
    lines.append("")
    if mrb:
        lines.append("## 二、MRB 评审记录")
        lines.append("")
        mrows = [
            ("评审日期", mrb.get("date", "待填写")),
            ("参会方", mrb.get("members", "待填写")),
            ("评审决议", mrb.get("resolution", "待填写")),
            ("责任人", mrb.get("owner", "待填写")),
            ("完成时限", mrb.get("due", "待填写")),
            ("验证方式", mrb.get("verify", "待填写")),
        ]
        lines.append("| 项目 | 内容 |")
        lines.append("|------|------|")
        for k, v in mrows:
            lines.append(f"| {k} | {v} |")
        lines.append("")
    lines.append("---")
    lines.append("*本报告由 nonconformance-handling 生成（仅文字/MD，无网页与办公格式）*")
    return "\n".join(lines)


def build_txt(data):
    """纯文字版：去掉 MD 语法，用等号/横线与缩进排版，便于打印或粘贴流转。"""
    nc = data["nc"]
    mrb = data.get("mrb", {})
    L = []
    L.append("不合格品处置与 MRB 评审报告")
    L.append("=" * 40)
    L.append("")
    L.append("【一、不合格处置单】")
    L.append("-" * 40)
    rows = [
        ("产品名称/型号", nc.get("product", "待填写")),
        ("批次号", nc.get("batch", "待填写")),
        ("数量", nc.get("qty", "待填写")),
        ("发现环节", nc.get("stage", "待填写")),
        ("缺陷描述", nc.get("defect", "待填写")),
        ("不合格类型", nc.get("type", "待填写")),
        ("影响范围", nc.get("scope", "待填写")),
        ("紧急程度", nc.get("urgency", "待填写")),
    ]
    for k, v in rows:
        L.append(f"{k}：{v}")
    L.append("")
    L.append(f"处置方式：■{nc.get('disposition','待填写')}　□返修　□让步接收　□降级使用　□报废")
    L.append("")
    L.append("审批签字：")
    L.append(f"  质量工程师：{nc.get('approve_qe','____')}")
    L.append(f"  质量主管：{nc.get('approve_qm','____')}（返修需技术主管加签）")
    L.append(f"  客户确认：____（让步涉及客户时必签）")
    L.append("")
    L.append(f"返工/返修记录：{nc.get('rework_record','-')}")
    L.append(f"重新检验：{nc.get('reinspect','-')}（返工/返修须100%重检）")
    L.append(f"最终处置：■{nc.get('final','待填写')}")
    L.append("")
    L.append("【铁律】返工≠返修；返工后100%重检，返修须100%重检+专项检验；"
             "返工返修>2次强制报废；让步须限量/限期/限批。")
    L.append("")
    if mrb:
        L.append("【二、MRB 评审记录】")
        L.append("-" * 40)
        mrows = [
            ("评审日期", mrb.get("date", "待填写")),
            ("参会方", mrb.get("members", "待填写")),
            ("评审决议", mrb.get("resolution", "待填写")),
            ("责任人", mrb.get("owner", "待填写")),
            ("完成时限", mrb.get("due", "待填写")),
            ("验证方式", mrb.get("verify", "待填写")),
        ]
        for k, v in mrows:
            L.append(f"{k}：{v}")
        L.append("")
    L.append("=" * 40)
    L.append("本报告由 nonconformance-handling 生成（仅文字/MD，无网页与办公格式）")
    return "\n".join(L)


def main():
    parser = argparse.ArgumentParser(description="不合格处理报告（文字版 .txt + Markdown .md）")
    parser.add_argument("--data-file", default="", help="JSON 数据文件路径")
    parser.add_argument("--out-dir", default="", help="输出目录，默认当前工作目录")
    args = parser.parse_args()

    data = SAMPLE
    if args.data_file:
        with open(args.data_file, "r", encoding="utf-8") as f:
            data = json.load(f)

    out_dir = args.out_dir or os.getcwd()
    os.makedirs(out_dir, exist_ok=True)

    md_path = os.path.join(out_dir, "nonconformance_report.md")
    txt_path = os.path.join(out_dir, "nonconformance_report.txt")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(build_md(data))
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(build_txt(data))
    print(f"[OK] MD  -> {os.path.abspath(md_path)}")
    print(f"[OK] TXT -> {os.path.abspath(txt_path)}")


if __name__ == "__main__":
    main()
