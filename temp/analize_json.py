#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import csv
import sys

def safe_get(obj, key, default=''):
    """安全获取字典值，处理 None 和缺失"""
    val = obj.get(key, default)
    return val if val is not None else default

def format_bool(value):
    return '是' if value else '否'

def get_filter_options_count(dim):
    """获取过滤可选值的数量"""
    if dim.get('filter_able') and 'filter_config' in dim:
        fc = dim['filter_config']
        if 'range_value' in fc and isinstance(fc['range_value'], list):
            return len(fc['range_value'])
    return ''

def main():
    json_file = "dimensions_and_metrics.json"
    csv_file = "parsed_dimensions_metrics.csv"

    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"错误: 找不到文件 '{json_file}'，请确保文件在当前目录下。")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"错误: JSON 解析失败: {e}")
        sys.exit(1)

    if data.get('code') != 0:
        print(f"API 返回错误: code={data.get('code')}, message={data.get('message')}")
        sys.exit(1)

    topics = data.get('data', {}).get('list', [])
    if not topics:
        print("没有找到任何数据主题。")
        return

    # 准备 CSV 列头
    headers = [
        '数据主题', '类型', '名称', '字段名', '描述',
        '可过滤', '可排序', '过滤可选值数量',
        '排除维度数量', '排除指标数量', '备注'
    ]

    rows = []

    for topic in topics:
        topic_name = safe_get(topic, 'data_topic')

        # 处理维度
        for dim in topic.get('dimensions', []):
            row = {
                '数据主题': topic_name,
                '类型': '维度',
                '名称': safe_get(dim, 'name'),
                '字段名': safe_get(dim, 'field'),
                '描述': safe_get(dim, 'description'),
                '可过滤': format_bool(dim.get('filter_able', False)),
                '可排序': format_bool(dim.get('sort_able', False)),
                '过滤可选值数量': get_filter_options_count(dim),
                '排除维度数量': len(dim.get('exclusion_dims', [])),
                '排除指标数量': len(dim.get('exclusion_metrics', [])),
                '备注': ''
            }
            rows.append(row)

        # 处理指标
        for metric in topic.get('metrics', []):
            row = {
                '数据主题': topic_name,
                '类型': '指标',
                '名称': safe_get(metric, 'name'),
                '字段名': safe_get(metric, 'field'),
                '描述': safe_get(metric, 'description'),
                '可过滤': '',  # 指标通常没有 filter_able
                '可排序': '',
                '过滤可选值数量': '',
                '排除维度数量': len(metric.get('exclusion_dims', [])),
                '排除指标数量': len(metric.get('exclusion_metrics', [])),
                '备注': ''
            }
            rows.append(row)

    # 写入 CSV
    with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

    print(f"解析完成！共写入 {len(rows)} 条记录。")
    print(f"CSV 文件已保存为: {csv_file}")

if __name__ == "__main__":
    main()