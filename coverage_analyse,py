import os
import json
import numpy as np
import pandas as pd
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import pairwise_distances
from collections import defaultdict

def is_integer(s):
    s = s.strip()  # 可选：去除前后空格
    if not s:
        return False
    # 允许符号开头，但符号后必须有数字
    if s[0] in ('-', '+'):
        return s[1:].isdigit() and len(s) > 1
    return s.isdigit()

def split_string(input_string):
    try:
        # 首先尝试按照空格分割
        # rsplit(maxsplit=1) 会从右边开始分割，最多分割成两个部分
        parts = input_string.rsplit(maxsplit=1)
        if len(parts) == 2 and is_integer(parts[1]):
            return parts
        else:
            raise ValueError("No valid split found")
    except ValueError:
        # 如果没有有效的分割，尝试按照最后一个逗号分割
        parts = input_string.rsplit(',', maxsplit=1)
        return parts

def error_corrected(directory_path, standard_writepath):
    map = {}
    with open(directory_path, 'r', encoding='utf-8') as file:
        for line in file:
            # 去除行首尾的空白字符
            stripped_line = line.strip()
            # 检查是否是非空行
            if stripped_line:
                stripped_line = stripped_line.replace(", ",",")
                stripped_line = stripped_line.replace(",function", "")
                stripped_line = stripped_line.replace(",clause", "")
                stripped_line = stripped_line.replace(",command", "")
                stripped_line = stripped_line.replace(",statement", "")
                stripped_line = stripped_line.replace(",parameter", "")
                stripped_line = stripped_line.replace(",operator", "")
                stripped_line = stripped_line.replace(",variable", "")
                stripped_line = stripped_line.replace(",syntax", "")
                print(stripped_line)
                contents = split_string(stripped_line)

                affected_element = contents[0].split(",")
                id = contents[1]
                if id in map:
                    for ele in affected_element:
                        map[id].append(ele)
                else:
                    map[id] = affected_element
    with open(standard_writepath,
                  'a',
                  encoding='utf-8') as f:
        for key, value in map.items():
            f.write(f"Key: {key}, Value: {value}"+'\n')
            print(f"Key: {key}, Value: {value}")
    return map

# 计算 Jaccard 相似性
def jaccard_similarity(list1, list2):
    set1 = set(list1)
    set2 = set(list2)
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union != 0 else 0

def sim(dic, standard_writepath, final_writepath, all_writepath):
    data = error_corrected(dic, standard_writepath)
    # 生成相似性矩阵
    ids = list(data.keys())
    similarity_matrix = np.zeros((len(ids), len(ids)))

    for i in range(len(ids)):
        for j in range(len(ids)):
            if i != j:
                similarity_matrix[i][j] = jaccard_similarity(data[ids[i]], data[ids[j]])

    # 转换为距离矩阵
    distance_matrix = 1 - similarity_matrix

    # 使用层次聚类，正确设置参数
    threshold = 0.8
    clustering = AgglomerativeClustering(
        metric='precomputed',    # 指定使用预计算的距离矩阵
        linkage='average',         # 选择平均链接方式
        distance_threshold=threshold,
        n_clusters=None
    )
    clustering.fit(distance_matrix)

    # 分类结果
    clusters = defaultdict(list)
    for idx, cluster_id in enumerate(clustering.labels_):
        clusters[cluster_id].append(ids[idx])

    # 输出结果
    with open(final_writepath,
              'a',
              encoding='utf-8') as f:
        for cluster_id, members in clusters.items():
            f.write(f"Cluster {cluster_id}: {members}" + '\n')
    # for cluster_id, members in clusters.items():
    #     print(f"Cluster {cluster_id}: {members}")
    clusters = defaultdict(list)
    for idx, cluster_id in enumerate(clustering.labels_):
        member_id = ids[idx]
        clusters[cluster_id].append({
            'id': member_id,
            'elements': data[member_id]  # 存储列表元素
        })
    with open(all_writepath, 'a', encoding='utf-8') as f:
        for cluster_id, members in clusters.items():
            # 构建集群头信息
            cluster_header = f"Cluster {cluster_id} (共 {len(members)} 个成员):\n"

            # 构建每个成员的详细信息
            member_details = []
            for member in members:
                elements_str = ', '.join(map(str, member['elements']))  # 将列表元素转为字符串
                member_details.append(f"  ID: {member['id']} - 元素: [{elements_str}]")

            # 组合集群信息并写入
            f.write(cluster_header)
            f.write('\n'.join(member_details))
            f.write('\n\n')

    structured_clusters = {
        cid: [{"id": m['id'], "elements": m['elements']} for m in members]
        for cid, members in clusters.items()
    }

    # 保存为JSON文件
    json_path = all_writepath.replace(".txt", ".json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(structured_clusters, f, indent=2)

    return structured_clusters


def analyze_sql_coverage(cluster_json_path, sql_files, large_cluster_threshold=5):
    # 读取聚类结果
    with open(cluster_json_path, 'r', encoding='utf-8') as f:
        clusters = json.load(f)

    # 预处理所有pattern（转换为大写）
    pattern_registry = []
    cluster_info = {}

    for cid_str, members in clusters.items():
        cid = int(cid_str)
        cluster_size = len(members)
        cluster_info[cid] = {
            "size": cluster_size,
            "patterns": {},
            "is_large": cluster_size >= large_cluster_threshold
        }

        for member in members:
            pattern = [elem.upper() for elem in member['elements']]
            pattern_registry.append((cid, member['id'], pattern))
            cluster_info[cid]['patterns'][member['id']] = pattern

    # 初始化统计结果
    coverage_data = {
        'cluster_coverage': defaultdict(set),
        'pattern_coverage': set(),
        'large_clusters': {cid for cid, info in cluster_info.items() if info['is_large']}
    }

    # 处理每个SQL文件
    for sql_file in sql_files:
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_statements = [stmt.strip().upper() for stmt in f.read().split(';') if stmt.strip()]

        for sql in sql_statements:
            # 检查所有pattern
            for cid, mid, pattern in pattern_registry:
                if all(keyword in sql for keyword in pattern):
                    coverage_data['cluster_coverage'][cid].add(mid)
                    coverage_data['pattern_coverage'].add(mid)

    # 计算统计指标
    stats = {
        'total_clusters': len(clusters),
        'covered_clusters': len(coverage_data['cluster_coverage']),
        'total_patterns': len(pattern_registry),
        'covered_patterns': len(coverage_data['pattern_coverage']),
        'large_clusters': len(coverage_data['large_clusters']),
        'covered_large_clusters': len(coverage_data['cluster_coverage'].keys() & coverage_data['large_clusters'])
    }

    return stats, cluster_info


def generate_coverage_report(stats, cluster_info, report_path):
    report = []

    # 总体统计
    report.append("=== SQL Pattern覆盖分析报告 ===")
    report.append(f"总集群数量: {stats['total_clusters']}")
    report.append(
        f"被覆盖集群数量: {stats['covered_clusters']} ({stats['covered_clusters'] / stats['total_clusters']:.1%})")
    report.append(f"\n大集群数量(≥{stats.get('large_threshold', 'N/A')}成员): {stats['large_clusters']}")
    report.append(
        f"被覆盖的大集群数量: {stats['covered_large_clusters']} ({stats['covered_large_clusters'] / stats['large_clusters']:.1%})")

    report.append(f"\n总Pattern数量: {stats['total_patterns']}")
    report.append(
        f"被覆盖Pattern数量: {stats['covered_patterns']} ({stats['covered_patterns'] / stats['total_patterns']:.1%})")

    # 集群级详情
    report.append("\n\n=== 集群覆盖详情 ===")
    for cid in sorted(cluster_info.keys()):
        info = cluster_info[cid]
        coverage = len(stats['cluster_coverage'].get(cid, set()))
        status = "大集群" if info['is_large'] else "小集群"
        report.append(
            f"Cluster {cid} ({status}, {coverage}/{info['size']} patterns覆盖) "
            f"Size: {info['size']} | Patterns: {', '.join(info['patterns'].keys())}"
        )

    # 写入文件
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))



def read_files_in_directory(directory_path,writepath):
    if not os.path.exists(directory_path):
        print(f"目录 {directory_path} 不存在")
        return

    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            filename = file_path.split(os.sep)[-1]
            filename = filename.replace("description__","")
            filename = filename.replace(".txt","")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                    affected_elements = content['Affected Elements']

                    with open(writepath, 'a',
                              encoding='utf-8') as f:
                        f.write(affected_elements+'\t'+filename+'\n')


            except Exception as e:
                print(f"无法读取文件 {file_path}: {e}")


if __name__ == "__main__":
    # 参数配置
    CLUSTER_JSON = "path/to/clusters.json"
    dic = ""
    SQL_FILES = []
    for root, dirs, files in os.walk(dic):
        for file in files:
            file_path = os.path.join(root, file)
            SQL_FILES.append(file_path)
    LARGE_THRESHOLD = 5
    REPORT_PATH = "mysql_coverage_analysis.txt"

    # 执行分析
    stats, cluster_info = analyze_sql_coverage(
        cluster_json_path=CLUSTER_JSON,
        sql_files=SQL_FILES,
        large_cluster_threshold=LARGE_THRESHOLD
    )

    # 生成报告
    generate_coverage_report(stats, cluster_info, REPORT_PATH)
    print(f"分析报告已生成至: {REPORT_PATH}")
# error_corrected("/Users/tianchenglin/Documents/大模型指导的测试用例生成/LlmDBTesting/cluster/mysql_affected_elements_standard.txt")
# sim("/Users/tianchenglin/Dcuments/大模型指导的测试用例生成/LlmDBTesting/cluster/mysql_affected_elements_standard.txt")
# sim("/Users/tianchenglin/Documents/大模型指导的测试用例生成/LlmDBTesting/cluster/tidb_affected_elements_standard.txt","/Users/tianchenglin/Documents/大模型指导的测试用例生成/LlmDBTesting/cluster/tidb_standard.txt","/Users/tianchenglin/Documents/大模型指导的测试用例生成/LlmDBTesting/cluster/tidb_cluster.txt")
# sim("/Users/tianchenglin/Documents/大模型指导的测试用例生成/LlmDBTesting/cluster/clickhouse_affected_elements_standard.txt","/Users/tianchenglin/Documents/大模型指导的测试用例生成/LlmDBTesting/cluster/clickhouse_standard.txt","/Users/tianchenglin/Documents/大模型指导的测试用例生成/LlmDBTesting/cluster/clickhouse_cluster.txt")
# sim("/Users/tianchenglin/Documents/大模型指导的测试用例生成/LlmDBTesting/cluster/sqlite_affected_elements_standard.txt","/Users/tianchenglin/Documents/大模型指导的测试用例生成/LlmDBTesting/cluster/sqlite_standard.txt","/Users/tianchenglin/Documents/大模型指导的测试用例生成/LlmDBTesting/cluster/sqlite_cluster.txt")
sim("/Users/tianchenglin/Documents/大模型指导的测试用例生成/LlmDBTesting/cluster/duckdb_affected_elements_standard.txt","/Users/tianchenglin/Documents/大模型指导的测试用例生成/LlmDBTesting/cluster/duckdb_standard.txt","/Users/tianchenglin/Documents/大模型指导的测试用例生成/LlmDBTesting/cluster/duckdb_cluster.txt", "/Users/tianchenglin/Documents/大模型指导的测试用例生成/LlmDBTesting/cluster/duckdb_all_cluster_data.txt")
# sim("/Users/tianchenglin/Documents/大模型指导的测试用例生成/LlmDBTesting/cluster/oceanbase_affected_elements_standard.txt","/Users/tianchenglin/Documents/大模型指导的测试用例生成/LlmDBTesting/cluster/oceanbase_standard.txt","/Users/tianchenglin/Documents/大模型指导的测试用例生成/LlmDBTesting/cluster/oceanbase_cluster.txt")

# read_files_in_directory("/Users/tianchenglin/Documents/大模型指导的测试用例生成/LlmDBTesting/bug_knowledge/clickhouse", "/Users/tianchenglin/Documents/大模型指导的测试用例生成/LlmDBTesting/cluster/clickhouse_affected_elements.txt")
# read_files_in_directory("/Users/tianchenglin/Documents/大模型指导的测试用例生成/LlmDBTesting/bug_knowledge/duckdb", "/Users/tianchenglin/Documents/大模型指导的测试用例生成/LlmDBTesting/cluster/duckdb_affected_elements.txt")
# read_files_in_directory("/Users/tianchenglin/Documents/大模型指导的测试用例生成/LlmDBTesting/bug_knowledge/oceanbase", "/Users/tianchenglin/Documents/大模型指导的测试用例生成/LlmDBTesting/cluster/oceanbase_affected_elements.txt")
# read_files_in_directory("/Users/tianchenglin/Documents/大模型指导的测试用例生成/LlmDBTesting/bug_knowledge/sqlite", "/Users/tianchenglin/Documents/大模型指导的测试用例生成/LlmDBTesting/cluster/sqlite_affected_elements.txt")
# read_files_in_directory("/Users/tianchenglin/Documents/大模型指导的测试用例生成/LlmDBTesting/bug_knowledge/tidb", "/Users/tianchenglin/Documents/大模型指导的测试用例生成/LlmDBTesting/cluster/tidb_affected_elements.txt")
