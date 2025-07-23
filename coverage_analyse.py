
import math
import matplotlib.pyplot as plt
from collections import Counter, defaultdict
from itertools import combinations
from scipy.stats import chi2_contingency
import ast

# ---------------------------
# 1. 数据预处理
# ---------------------------
def load_patterns(file_path):
    """读取模式文件，返回关键字列表的列表（保留原始顺序）"""
    patterns = []
    with open(file_path, 'r') as f:
        for line in f:
            try:
                # 安全解析Python列表格式
                pattern = ast.literal_eval(line.strip())
                if isinstance(pattern, list):
                    patterns.append(pattern)
            except (SyntaxError, ValueError) as e:
                print(f"跳过无效行: {line.strip()}，错误: {e}")
                continue
        return patterns
    # with open(file_path, 'r') as f:
    #     return [line.strip().split(',') for line in f if line.strip()]


# covered = load_patterns('/Users/tianchenglin/Documents/大模型指导的测试用例生成/LlmDBTesting/new_cluster/coverage_analysis/oceanbase/oceanbase_cover_keywords.txt')
# uncovered = load_patterns('/Users/tianchenglin/Documents/大模型指导的测试用例生成/LlmDBTesting/new_cluster/coverage_analysis/oceanbase/oceanbase_not_cover_keywords.txt')


# ---------------------------
# 2. 模式长度分布分析
# ---------------------------
def plot_length_distribution(covered, uncovered):
    """绘制模式长度分布对比直方图"""
    plt.figure(figsize=(10, 5))
    plt.hist([len(p) for p in covered], alpha=0.5, label='covered', bins=20, color='black')
    plt.hist([len(p) for p in uncovered], alpha=0.5, label='uncovered', bins=20, color='red')
    plt.xlabel('pattern length')
    plt.ylabel('frequency')
    plt.title('covered vs uncovered')
    plt.legend()
    plt.show()


# plot_length_distribution(covered, uncovered)


# ---------------------------
# 3. 关键字频率差异分析
# ---------------------------
def keyword_ratio_diff(covered, uncovered):
    """计算未覆盖/已覆盖的关键字频率比率"""
    counter_covered = Counter(kw for p in covered for kw in p)
    counter_uncovered = Counter(kw for p in uncovered for kw in p)

    ratio_diff = {}
    for kw, uncov_count in counter_uncovered.items():
        cov_count = counter_covered.get(kw, 0)
        ratio = uncov_count / (cov_count + 1e-6)  # 防止除零
        ratio_diff[kw] = ratio

    return sorted(ratio_diff.items(), key=lambda x: -x[1])

# print("\n=== 关键字未覆盖/已覆盖频率比率 ===")
# with open("/Users/tianchenglin/Documents/大模型指导的测试用例生成/LlmDBTesting/new_cluster/coverage_analysis/oceanbase/oceanbase_keywords_comparison.txt", 'a', encoding='utf-8') as f:
#     for kw, ratio in keyword_ratio_diff(covered, uncovered):
#         print(f"{kw}: {ratio:.1f}")
#         f.write(f"{kw}: {ratio:.1f}\n")

def analyze_patterns(file_path):
    # 读取文件
    patterns = []
    with open(file_path, 'r') as f:
        for line in f:
            try:
                # 安全解析Python列表格式
                pattern = ast.literal_eval(line.strip())
                if isinstance(pattern, list):
                    patterns.append(pattern)
            except (SyntaxError, ValueError) as e:
                print(f"跳过无效行: {line.strip()}，错误: {e}")
                continue


    # # 功能一：关键字排名
    # keyword_counter = Counter()
    # for pattern in patterns:
    #     keyword_counter.update(pattern)
    # print("=== 未覆盖关键字排名 ===")
    # with open(output_file, 'a', encoding='utf-8') as f:

        # for keyword, count in keyword_counter.most_common():
        #     print(f"{keyword}: {count}")
        #
        #     f.write(f"{keyword}: {count}次\n")

    # 功能二：按长度分组的顺序组合统计
    # f.write("\n\n=== 按长度分组的顺序组合频率排名 ===\n")
    min_length = 4  # 最小统计组合长度
    max_length = 4  # 最大统计组合长度
    min_freq = 2  # 最低出现次数

    # 创建按长度分组的计数器
    length_groups = defaultdict(Counter)


    # 遍历所有pattern生成组合
    for pattern in patterns:
        n = len(pattern)
        # 生成从min_length到min(n, max_length)的各种长度组合
        for k in range(min_length, min(n, max_length) + 1):
            # 生成所有长度为k的顺序组合（保持元素顺序）
            for combo in combinations(pattern, k):
                length_groups[k][combo] += 1


    # 处理并过滤结果
    filtered_groups = {}
    for length in sorted(length_groups.keys()):
        group = length_groups[length]

        # 过滤并排序
        filtered = [
            (combo, count)
            for combo, count in group.items()
            if count >= min_freq
        ]
        filtered.sort(key=lambda x: (-x[1], -len(x[0]), x[0]))
        filtered_groups[length] = filtered
        # filtered_groups[length] = [combo for combo, _ in filtered]

    return filtered_groups
        # # 按组合长度排序输出
        # for length in sorted(length_groups.keys()):
        #     group = length_groups[length]
        #     # 过滤并排序
        #     filtered = [(combo, count) for combo, count in group.items() if count >= min_freq]
        #     filtered.sort(key=lambda x: (-x[1], -len(x[0]), x[0]))  # 按频率→长度→字典序排序
        #
        #     f.write(f"\n—— 长度 {length} 的组合 ——\n")
        #     for rank, (combo, count) in enumerate(filtered, 1):  # 取前10名
        #         f.write(f"第{rank}名: {' → '.join(combo)}\n")
        #         f.write(f"   出现次数: {count}\n")
        #         f.write("-" * 60 + "\n")

        # for i, (subseq, count, ratio, length) in enumerate(filtered[:100], 1):
        #     print(f"{i}. 子组合: {', '.join(subseq)}")
        #     print(f"   出现次数: {count}, 平均原长度比例: {ratio:.2f}, 长度: {length}\n")


# 调用过程示例
if __name__ == "__main__":
    covered = load_patterns(
        '/Users/tianchenglin/Documents/大模型指导的测试用例生成/LlmDBTesting/new_cluster/coverage_analysis/oceanbase/oceanbase_cover_keywords.txt')
    uncovered = load_patterns(
        '/Users/tianchenglin/Documents/大模型指导的测试用例生成/LlmDBTesting/new_cluster/coverage_analysis/oceanbase/oceanbase_not_cover_keywords.txt')
    print("\n=== 关键字未覆盖/已覆盖频率比率 ===")
    with open(
            "/Users/tianchenglin/Documents/大模型指导的测试用例生成/LlmDBTesting/new_cluster/coverage_analysis/oceanbase/oceanbase_keywords_comparison.txt",
            'a', encoding='utf-8') as f:
        for kw, ratio in keyword_ratio_diff(covered, uncovered):
            print(f"{kw}: {ratio:.1f}")
            f.write(f"{kw}: {ratio:.1f}\n")
    # 分析已覆盖和未覆盖的模式
    covered_stats = analyze_patterns('/Users/tianchenglin/Documents/大模型指导的测试用例生成/LlmDBTesting/new_cluster/coverage_analysis/oceanbase/oceanbase_cover_keywords.txt')
    uncovered_stats = analyze_patterns('/Users/tianchenglin/Documents/大模型指导的测试用例生成/LlmDBTesting/new_cluster/coverage_analysis/oceanbase/oceanbase_not_cover_keywords.txt')

    # 计算独有的组合
    unique_combinations = defaultdict(list)
    for length in uncovered_stats:
        # 转换为集合以便快速查找
        covered_combos = {combo for combo, _ in covered_stats.get(length, [])}
        # covered_set = set(covered_stats.get(length, []))
        # uncovered_set = set(uncovered_stats.get(length, []))
        # print(uncovered_set)
        # print(covered_set)
        # 保持原始顺序过滤
        unique = [
            (combo, count)
            for combo, count in uncovered_stats[length]
            if combo not in covered_combos
        ]
        if unique:
            unique_combinations[length] = unique

    # 打印结果示例
    with open("/Users/tianchenglin/Documents/大模型指导的测试用例生成/LlmDBTesting/new_cluster/coverage_analysis/oceanbase/oceanbase_pattern_analyse.txt", 'a', encoding='utf-8') as f:
        print("独有的顺序组合统计:")
        f.write("独有的顺序组合统计:\n")
        for length in sorted(unique_combinations.keys()):
            print(f"\n长度 {length} 的独有组合:")
            f.write(f"\n长度 {length} 的独有组合:\n")
            for combo, count in unique_combinations[length]:
                # 添加出现次数输出
                line = f"{' → '.join(combo)} (出现次数: {count})"
                print(line)
                f.write(line + '\n')
# 运行代码
# main("/Users/tianchenglin/Documents/大模型指导的测试用例生成/LlmDBTesting/new_cluster/coverage_analysis/oceanbase_not_cover_keywords.txt", "/Users/tianchenglin/Documents/大模型指导的测试用例生成/LlmDBTesting/new_cluster/coverage_analysis/oceanbase_pattern_analyse.txt")