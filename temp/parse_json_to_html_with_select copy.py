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

    # 生成 HTML（数字列使用下拉框）
    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>广告投放数据字典 - 维度与指标</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .filter-container {{
            margin-bottom: 15px; display: flex; flex-wrap: wrap; gap: 15px;
            background: #f5f5f5; padding: 15px; border-radius: 5px;
            align-items: flex-start;
        }}
        .filter-group {{
            background: white; padding: 8px 12px; border-radius: 6px;
            border: 1px solid #ccc; min-width: 180px;
        }}
        .filter-group label {{
            font-weight: bold; font-size: 12px; display: block; margin-bottom: 5px;
        }}
        .filter-group select {{
            width: 100%; margin-top: 5px;
        }}
        .clear-btn {{
            background: #0066cc; color: white; border: none; padding: 6px 15px;
            border-radius: 4px; cursor: pointer; align-self: center;
        }}
        .clear-btn:hover {{ background: #004499; }}
        table {{ border-collapse: collapse; width: 100%; font-size: 14px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; vertical-align: top; }}
        th {{ background-color: #f2f2f2; position: sticky; top: 0; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        a {{ text-decoration: none; color: #0066cc; }}
        a:hover {{ text-decoration: underline; }}
        .count-link {{ font-weight: bold; }}
        .hidden-row {{ display: none; }}
        .filter-info {{ margin: 10px 0; font-weight: bold; }}
    </style>
</head>
<body>
    <h1>广告投放数据字典</h1>
    <p>共 {total_items} 个维度/指标。点击数字链接可查看详细内容。</p>

    <div class="filter-container">
        <div class="filter-group">
            <label>数据主题</label>
            <select id="filterTopic"><option value="">全部</option></select>
        </div>
        <div class="filter-group">
            <label>类型</label>
            <select id="filterType"><option value="">全部</option></select>
        </div>
        <div class="filter-group">
            <label>可过滤</label>
            <select id="filterFilterable"><option value="">全部</option></select>
        </div>
        <div class="filter-group">
            <label>过滤可选值数量</label>
            <select id="filterCountOp">
                <option value="=">=</option>
                <option value=">">></option>
                <option value=">=">>=</option>
            </select>
            <select id="filterCountVal" multiple size="1"></select>
        </div>
        <div class="filter-group">
            <label>排除维度数量</label>
            <select id="filterDimsOp">
                <option value="=">=</option>
                <option value=">">></option>
                <option value=">=">>=</option>
            </select>
            <select id="filterDimsVal" multiple size="1"></select>
        </div>
        <div class="filter-group">
            <label>排除指标数量</label>
            <select id="filterMetricsOp">
                <option value="=">=</option>
                <option value=">">></option>
                <option value=">=">>=</option>
            </select>
            <select id="filterMetricsVal" multiple size="1"></select>
        </div>
        <button class="clear-btn" id="clearFilters">清除所有筛选</button>
    </div>

    <div style="overflow-x: auto;">
    <table>
        <thead>
            <tr><th>数据主题</th><th>类型</th><th>名称</th><th>字段名</th><th>描述</th><th>可过滤</th><th>可排序</th><th>过滤可选值数量</th><th>排除维度数量</th><th>排除指标数量</th><th>备注</th></tr>
        </thead>
        <tbody id="tableBody">
"""

    for row in rows:
        filter_cell = f'<a href="{row["filter_link"]}" class="count-link" target="_blank">{row["filter_count"]}</a>' if row['filter_count'] > 0 else '0'
        dims_cell = f'<a href="{row["excl_dims_link"]}" class="count-link" target="_blank">{row["excl_dims_count"]}</a>' if row['excl_dims_count'] > 0 else '0'
        metrics_cell = f'<a href="{row["excl_metrics_link"]}" class="count-link" target="_blank">{row["excl_metrics_count"]}</a>' if row['excl_metrics_count'] > 0 else '0'

        html_content += f"""
            <tr>
                <td>{row['topic']}</td>
                <td>{row['type']}</td>
                <td>{row['name']}</td>
                <td>{row['field']}</td>
                <td>{row['description']}</td>
                <td>{row['filter_able']}</td>
                <td>{row['sort_able']}</td>
                <td data-count="{row['filter_count']}">{filter_cell}</td>
                <td data-dims="{row['excl_dims_count']}">{dims_cell}</td>
                <td data-metrics="{row['excl_metrics_count']}">{metrics_cell}</td>
                <td>{row['remark']}</td>
            </tr>"""

    html_content += """
        </tbody>
    </table>
    </div>
    <div id="filterInfo" class="filter-info"></div>

    <script>
        // 防抖
        function debounce(func, wait) {
            let timeout;
            return function() {
                clearTimeout(timeout);
                timeout = setTimeout(func, wait);
            };
        }

        // 获取某列的所有唯一数值
        function getUniqueNumbers(dataAttr) {
            let rows = document.querySelectorAll('#tableBody tr');
            let values = new Set();
            rows.forEach(row => {
                let cells = row.getElementsByTagName('td');
                if (cells.length < 11) return;
                let idx = dataAttr === 'count' ? 7 : (dataAttr === 'dims' ? 8 : 9);
                let val = cells[idx].getAttribute(`data-${dataAttr}`);
                if (val !== null && val !== '') {
                    values.add(parseInt(val, 10));
                }
            });
            return Array.from(values).sort((a,b) => a-b);
        }

        // 填充数字列下拉框（根据操作符决定多选/单选）
        function populateNumberSelect(selectId, values, op, currentSelected) {
            let select = document.getElementById(selectId);
            if (!select) return;
            select.innerHTML = '';
            // 添加“全部”选项
            let allOpt = document.createElement('option');
            allOpt.value = '';
            allOpt.text = '全部';
            select.appendChild(allOpt);
            if (values.length === 0) {
                let opt = document.createElement('option');
                opt.text = '(无数据)';
                select.appendChild(opt);
                return;
            }
            // 设置多选/单选属性
            if (op === '=') {
                select.multiple = true;
                select.size = 1;   // 显示为下拉框
            } else {
                select.multiple = false;
                select.size = 1;
            }
            values.forEach(v => {
                let opt = document.createElement('option');
                opt.value = v;
                opt.text = v;
                if (currentSelected && currentSelected.includes(String(v))) {
                    opt.selected = true;
                }
                select.appendChild(opt);
            });
        }

        // 获取当前选中的数值（根据操作符）
        function getSelectedNumbers(selectId, op) {
            let select = document.getElementById(selectId);
            if (!select) return [];
            let selected = Array.from(select.selectedOptions).map(opt => opt.value);
            // 如果包含空字符串（全部），则视为无筛选
            if (selected.includes('')) return [];
            if (op === '=') {
                return selected;
            } else {
                return selected.length > 0 ? [selected[0]] : [];
            }
        }

        // 初始化所有数字列
        function initNumberFilters() {
            let countValues = getUniqueNumbers('count');
            let dimsValues = getUniqueNumbers('dims');
            let metricsValues = getUniqueNumbers('metrics');

            let countOp = document.getElementById('filterCountOp').value;
            let dimsOp = document.getElementById('filterDimsOp').value;
            let metricsOp = document.getElementById('filterMetricsOp').value;

            populateNumberSelect('filterCountVal', countValues, countOp, []);
            populateNumberSelect('filterDimsVal', dimsValues, dimsOp, []);
            populateNumberSelect('filterMetricsVal', metricsValues, metricsOp, []);
        }

        // 刷新单个数字列（操作符变化时调用）
        function refreshNumberFilter(attr, selectId, opSelectId) {
            let values = getUniqueNumbers(attr);
            let op = document.getElementById(opSelectId).value;
            // 获取当前选中的值（用于保留，但通常重置）
            let currentSelected = getSelectedNumbers(selectId, op);
            populateNumberSelect(selectId, values, op, currentSelected);
            filterTable();
        }

        // 筛选主函数
        function filterTable() {
            let topic = document.getElementById('filterTopic').value;
            let type = document.getElementById('filterType').value;
            let filterable = document.getElementById('filterFilterable').value;

            let countOp = document.getElementById('filterCountOp').value;
            let countSelected = getSelectedNumbers('filterCountVal', countOp);
            let dimsOp = document.getElementById('filterDimsOp').value;
            let dimsSelected = getSelectedNumbers('filterDimsVal', dimsOp);
            let metricsOp = document.getElementById('filterMetricsOp').value;
            let metricsSelected = getSelectedNumbers('filterMetricsVal', metricsOp);

            let rows = document.querySelectorAll('#tableBody tr');
            let visible = 0;
            rows.forEach(row => {
                let cells = row.getElementsByTagName('td');
                if (cells.length < 11) return;

                let rowTopic = cells[0].innerText;
                let rowType = cells[1].innerText;
                let rowFilterable = cells[5].innerText;
                let countVal = parseInt(cells[7].getAttribute('data-count'), 10);
                let dimsVal = parseInt(cells[8].getAttribute('data-dims'), 10);
                let metricsVal = parseInt(cells[9].getAttribute('data-metrics'), 10);

                let match = true;
                if (topic && rowTopic !== topic) match = false;
                if (type && rowType !== type) match = false;
                if (filterable && rowFilterable !== filterable) match = false;

                // 过滤可选值数量
                if (match && countSelected.length > 0) {
                    if (countOp === '=') {
                        if (!countSelected.includes(String(countVal))) match = false;
                    } else if (countOp === '>') {
                        let threshold = parseFloat(countSelected[0]);
                        if (!(countVal > threshold)) match = false;
                    } else if (countOp === '>=') {
                        let threshold = parseFloat(countSelected[0]);
                        if (!(countVal >= threshold)) match = false;
                    }
                }

                // 排除维度数量
                if (match && dimsSelected.length > 0) {
                    if (dimsOp === '=') {
                        if (!dimsSelected.includes(String(dimsVal))) match = false;
                    } else if (dimsOp === '>') {
                        let threshold = parseFloat(dimsSelected[0]);
                        if (!(dimsVal > threshold)) match = false;
                    } else if (dimsOp === '>=') {
                        let threshold = parseFloat(dimsSelected[0]);
                        if (!(dimsVal >= threshold)) match = false;
                    }
                }

                // 排除指标数量
                if (match && metricsSelected.length > 0) {
                    if (metricsOp === '=') {
                        if (!metricsSelected.includes(String(metricsVal))) match = false;
                    } else if (metricsOp === '>') {
                        let threshold = parseFloat(metricsSelected[0]);
                        if (!(metricsVal > threshold)) match = false;
                    } else if (metricsOp === '>=') {
                        let threshold = parseFloat(metricsSelected[0]);
                        if (!(metricsVal >= threshold)) match = false;
                    }
                }

                if (match) {
                    row.classList.remove('hidden-row');
                    visible++;
                } else {
                    row.classList.add('hidden-row');
                }
            });
            document.getElementById('filterInfo').innerText = `当前显示 ${visible} / ${rows.length} 行`;
        }

        // 填充普通文本下拉框
        function populateTextSelect(selectId, columnIndex) {
            let select = document.getElementById(selectId);
            if (!select) return;
            let rows = document.querySelectorAll('#tableBody tr');
            let values = new Set();
            rows.forEach(row => {
                let cells = row.getElementsByTagName('td');
                if (cells.length < 11) return;
                let val = cells[columnIndex].innerText.trim();
                if (val) values.add(val);
            });
            let sorted = Array.from(values).sort();
            sorted.forEach(v => {
                let opt = document.createElement('option');
                opt.value = v;
                opt.text = v;
                select.appendChild(opt);
            });
        }

        // 清除所有筛选
        function clearFilters() {
            document.getElementById('filterTopic').value = '';
            document.getElementById('filterType').value = '';
            document.getElementById('filterFilterable').value = '';
            document.getElementById('filterCountOp').value = '=';
            document.getElementById('filterDimsOp').value = '=';
            document.getElementById('filterMetricsOp').value = '=';
            initNumberFilters();
            filterTable();
        }

        window.addEventListener('DOMContentLoaded', () => {
            populateTextSelect('filterTopic', 0);
            populateTextSelect('filterType', 1);
            populateTextSelect('filterFilterable', 5);
            initNumberFilters();

            let debouncedFilter = debounce(filterTable, 150);
            document.getElementById('filterTopic').addEventListener('change', debouncedFilter);
            document.getElementById('filterType').addEventListener('change', debouncedFilter);
            document.getElementById('filterFilterable').addEventListener('change', debouncedFilter);
            document.getElementById('filterCountOp').addEventListener('change', () => refreshNumberFilter('count', 'filterCountVal', 'filterCountOp'));
            document.getElementById('filterDimsOp').addEventListener('change', () => refreshNumberFilter('dims', 'filterDimsVal', 'filterDimsOp'));
            document.getElementById('filterMetricsOp').addEventListener('change', () => refreshNumberFilter('metrics', 'filterMetricsVal', 'filterMetricsOp'));
            document.getElementById('filterCountVal').addEventListener('change', debouncedFilter);
            document.getElementById('filterDimsVal').addEventListener('change', debouncedFilter);
            document.getElementById('filterMetricsVal').addEventListener('change', debouncedFilter);
            document.getElementById('clearFilters').addEventListener('click', clearFilters);
            filterTable();
        });
    </script>
    <p><em>生成时间: 使用 Python 脚本自动生成</em></p>
</body>
</html>"""

    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"解析完成！共处理 {total_items} 个维度/指标。")
    print(f"详细内容已保存在文件夹: {DETAILS_DIR}/")
    print(f"HTML 报告已保存为: {html_file}")

if __name__ == "__main__":
    main()