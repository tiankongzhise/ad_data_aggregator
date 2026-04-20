#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import re
import sys

DETAILS_DIR = "details"

def safe_filename(text):
    text = re.sub(r'[\\/*?:"<>|]', '_', text)
    return text.strip()

def write_details_file(filepath, content_list, title):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"{title}\n")
        f.write("=" * 60 + "\n")
        for item in content_list:
            f.write(str(item) + "\n")

def get_filter_options(dim):
    options = []
    if dim.get('filter_able') and 'filter_config' in dim:
        fc = dim['filter_config']
        if 'range_value' in fc and isinstance(fc['range_value'], list):
            for opt in fc['range_value']:
                label = opt.get('label', '')
                value = opt.get('value', '')
                options.append(f"{label} ({value})")
    return options

def main():
    json_file = "dimensions_and_metrics.json"
    html_file = "dimensions_metrics_report.html"

    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"错误: 找不到文件 '{json_file}'")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"错误: JSON 解析失败: {e}")
        sys.exit(1)

    if data.get('code') != 0:
        print(f"API 返回错误: {data.get('message')}")
        sys.exit(1)

    topics = data.get('data', {}).get('list', [])
    if not topics:
        print("没有找到任何数据主题。")
        return

    if not os.path.exists(DETAILS_DIR):
        os.makedirs(DETAILS_DIR)

    rows = []
    total_items = 0

    for topic in topics:
        topic_name = topic.get('data_topic', '未知主题')

        for dim in topic.get('dimensions', []):
            total_items += 1
            item_name = dim.get('name', '')
            field_name = dim.get('field', '')
            description = dim.get('description', '')
            filter_able = '是' if dim.get('filter_able') else '否'
            sort_able = '是' if dim.get('sort_able') else '否'

            filter_options = get_filter_options(dim)
            exclusion_dims = dim.get('exclusion_dims', [])
            exclusion_metrics = dim.get('exclusion_metrics', [])

            base_name = f"{topic_name}_维度_{item_name}"
            safe_base = safe_filename(base_name)

            filter_file = os.path.join(DETAILS_DIR, f"{safe_base}_过滤可选值.txt")
            dims_file = os.path.join(DETAILS_DIR, f"{safe_base}_排除维度.txt")
            metrics_file = os.path.join(DETAILS_DIR, f"{safe_base}_排除指标.txt")

            if filter_options:
                write_details_file(filter_file, filter_options, f"过滤可选值列表（{item_name}）")
            else:
                with open(filter_file, 'w', encoding='utf-8') as f:
                    f.write("无过滤可选值信息")

            if exclusion_dims:
                write_details_file(dims_file, exclusion_dims, f"排除维度列表（{item_name}）")
            else:
                with open(dims_file, 'w', encoding='utf-8') as f:
                    f.write("无排除维度")

            if exclusion_metrics:
                write_details_file(metrics_file, exclusion_metrics, f"排除指标列表（{item_name}）")
            else:
                with open(metrics_file, 'w', encoding='utf-8') as f:
                    f.write("无排除指标")

            rows.append({
                'topic': topic_name,
                'type': '维度',
                'name': item_name,
                'field': field_name,
                'description': description,
                'filter_able': filter_able,
                'sort_able': sort_able,
                'filter_count': len(filter_options),
                'filter_link': filter_file.replace('\\', '/'),
                'excl_dims_count': len(exclusion_dims),
                'excl_dims_link': dims_file.replace('\\', '/'),
                'excl_metrics_count': len(exclusion_metrics),
                'excl_metrics_link': metrics_file.replace('\\', '/'),
                'remark': ''
            })

        for metric in topic.get('metrics', []):
            total_items += 1
            item_name = metric.get('name', '')
            field_name = metric.get('field', '')
            description = metric.get('description', '')

            exclusion_dims = metric.get('exclusion_dims', [])
            exclusion_metrics = metric.get('exclusion_metrics', [])

            base_name = f"{topic_name}_指标_{item_name}"
            safe_base = safe_filename(base_name)

            filter_file = os.path.join(DETAILS_DIR, f"{safe_base}_过滤可选值.txt")
            dims_file = os.path.join(DETAILS_DIR, f"{safe_base}_排除维度.txt")
            metrics_file = os.path.join(DETAILS_DIR, f"{safe_base}_排除指标.txt")

            with open(filter_file, 'w', encoding='utf-8') as f:
                f.write("指标通常没有过滤可选值信息")

            if exclusion_dims:
                write_details_file(dims_file, exclusion_dims, f"排除维度列表（{item_name}）")
            else:
                with open(dims_file, 'w', encoding='utf-8') as f:
                    f.write("无排除维度")

            if exclusion_metrics:
                write_details_file(metrics_file, exclusion_metrics, f"排除指标列表（{item_name}）")
            else:
                with open(metrics_file, 'w', encoding='utf-8') as f:
                    f.write("无排除指标")

            rows.append({
                'topic': topic_name,
                'type': '指标',
                'name': item_name,
                'field': field_name,
                'description': description,
                'filter_able': '',
                'sort_able': '',
                'filter_count': 0,
                'filter_link': filter_file.replace('\\', '/'),
                'excl_dims_count': len(exclusion_dims),
                'excl_dims_link': dims_file.replace('\\', '/'),
                'excl_metrics_count': len(exclusion_metrics),
                'excl_metrics_link': metrics_file.replace('\\', '/'),
                'remark': ''
            })

    # 生成 HTML（所有花括号已转义，只保留一个 {} 给 total_items）
    html_template = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>广告投放数据字典 - 维度与指标</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
        }}
        table {{
            border-collapse: collapse;
            width: 100%;
            font-size: 14px;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
            vertical-align: top;
        }}
        th {{
            background-color: #f2f2f2;
            position: sticky;
            top: 0;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        a {{
            text-decoration: none;
            color: #0066cc;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        .count-link {{
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <h1>广告投放数据字典</h1>
    <p>共 {} 个维度/指标。点击数字链接可查看详细内容。</p>
    <div style="overflow-x: auto;">
    <table>
        <thead>
            <tr>
                <th>数据主题</th><th>类型</th><th>名称</th><th>字段名</th><th>描述</th>
                <th>可过滤</th><th>可排序</th>
                <th>过滤可选值数量</th><th>排除维度数量</th><th>排除指标数量</th><th>备注</th>
            </tr>
        </thead>
        <tbody>
"""

    for row in rows:
        filter_cell = f'<a href="{row["filter_link"]}" class="count-link" target="_blank">{row["filter_count"]}</a>' if row['filter_count'] > 0 else '0'
        dims_cell = f'<a href="{row["excl_dims_link"]}" class="count-link" target="_blank">{row["excl_dims_count"]}</a>' if row['excl_dims_count'] > 0 else '0'
        metrics_cell = f'<a href="{row["excl_metrics_link"]}" class="count-link" target="_blank">{row["excl_metrics_count"]}</a>' if row['excl_metrics_count'] > 0 else '0'

        html_template += f"""
            <tr>
                <td>{row['topic']}</td>
                <td>{row['type']}</td>
                <td>{row['name']}</td>
                <td>{row['field']}</td>
                <td>{row['description']}</td>
                <td>{row['filter_able']}</td>
                <td>{row['sort_able']}</td>
                <td>{filter_cell}</td>
                <td>{dims_cell}</td>
                <td>{metrics_cell}</td>
                <td>{row['remark']}</td>
            </tr>"""

    html_template += """
        </tbody>
    </table>
    </div>
    <p><em>生成时间: 使用 Python 脚本自动生成</em></p>
</body>
</html>"""

    # 使用 format 插入 total_items
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_template.format(total_items))

    print(f"解析完成！共处理 {total_items} 个维度/指标。")
    print(f"详细内容已保存在文件夹: {DETAILS_DIR}/")
    print(f"HTML 报告已保存为: {html_file}")

if __name__ == "__main__":
    main()