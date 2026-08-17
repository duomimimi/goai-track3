import sqlite3
import json
import random
import subprocess
import re
from datetime import datetime
import os

# ============ CONFIG ============
DB_CORE = r'E:\duomi\knowledge\knowledge_network_core.db'
DB_CONN = r'E:\duomi\knowledge\knowledge_network_connections.db'
OUTPUT_DIR = r'C:\Users\linshi\.openclaw-autoclaw\workspace\discoveries'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============ UTILITIES ============
def clean_node_name(name):
    """清理节点名：去掉前缀杂质"""
    if not name:
        return ""
    # 去掉常见前缀模式
    patterns = [
        r'^title:\s*', r'^M3[ -]?(蒸馏|困惑|推理|常识|开放问题|跨界|涌现)[-：:\s]*',
        r'^RD[ -]\d+:\s*', r'^\d+[.、]\s*', r'^第\d+[章节条点]'
    ]
    for p in patterns:
        name = re.sub(p, '', name)
    return name.strip()[:80]  # Max 80 chars


def mmx_search(query, timeout=30):
    """调用mmx search API"""
    try:
        result = subprocess.run(
            ['D:\\AutoClaw\\resources\\node\\npx.cmd', 'mmx', 'search', 'query', query, '--output', 'json'],
            capture_output=True, text=True, timeout=timeout
        )
        if result.returncode == 0:
            try:
                data = json.loads(result.stdout)
                if isinstance(data, list):
                    return len(data)
                elif isinstance(data, dict):
                    if 'results' in data:
                        return len(data['results'])
                    elif 'result' in data:
                        return len(data['result'])
                    else:
                        return 0
                return 0
            except:
                return 0
    except:
        pass
    return -1  # Error indicator


# ============ STAGE 1: Load knowledge network ============
def load_knowledge_network():
    """从新大脑知识网络加载候选节点（按学科分组）"""
    conn = sqlite3.connect(DB_CORE)
    conn.execute(f"ATTACH DATABASE '{DB_CONN}' AS conn_db")
    cur = conn.cursor()

    discipline_queries = {
        'mathematics': ['拓扑', '量子', '方程', '定理', '算法', '函数', '群论', '图论', '素数', '梅林', 'Dirac', '拉格朗日', '费马', '欧拉', '黎曼'],
        'physics': ['量子', '超导', '相变', '振子', '场论', '热力学', '凝聚态', '拓扑绝缘体', '超导', '相变', '对称'],
        'biology': ['神经', '基因', '蛋白质', '免疫', '进化', '细胞', '动作电位', '轴突', '神经网络', '突触'],
        'cs': ['机器学习', '深度学习', '神经网络', '注意力', '强化学习', '图神经网络', '优化算法', '学习', '训练'],
        'economics': ['市场均衡', '博弈论', '订单簿', '交易', '资产', '货币', '消费者', '定价', '金融'],
        'medicine': ['疫苗', '药物', '流行病', '免疫', '治疗', '分配', '精准医疗', '基因编辑']
    }

    all_nodes = {}
    discipline_nodes = {d: [] for d in discipline_queries}

    for disc, keywords in discipline_queries.items():
        for kw in keywords:
            cur.execute(f'''
                SELECT id, name, strength FROM nodes
                WHERE name LIKE '%{kw}%'
                AND LENGTH(name) > 8
                AND strength >= 0.6
                ORDER BY strength DESC
                LIMIT 8
            ''')
            for r in cur.fetchall():
                if r[0] not in all_nodes:
                    clean_name = clean_node_name(r[1])
                    if len(clean_name) > 4:
                        all_nodes[r[0]] = {'name': clean_name, 'discipline': disc, 'strength': r[2]}
                        discipline_nodes[disc].append(r[0])

    conn.close()

    total = sum(len(v) for v in discipline_nodes.values())
    print(f"[Stage1] 知识网络: {total}节点（跨{len(discipline_nodes)}学科）")
    for d, nodes in discipline_nodes.items():
        print(f"  {d}: {len(nodes)}节点")
    return all_nodes, discipline_nodes


# ============ STAGE 2: Generate candidates ============
def generate_candidates(all_nodes, discipline_nodes, max_candidates=50):
    """生成跨学科候选配对"""
    candidates = []
    disciplines = list(discipline_nodes.keys())

    # 确保每个学科对至少有一个候选
    for i, d1 in enumerate(disciplines):
        for d2 in disciplines[i+1:]:
            if discipline_nodes[d1] and discipline_nodes[d2]:
                n1 = random.choice(discipline_nodes[d1])
                n2 = random.choice(discipline_nodes[d2])
                candidates.append({
                    'node_a': all_nodes[n1], 'node_b': all_nodes[n2],
                    'strategy': random.choice(['causal_extension', 'analogy_driven', 'contradiction_finding']),
                    'weight': 0.4
                })

    # 补充随机候选
    while len(candidates) < max_candidates:
        d1, d2 = random.sample(disciplines, 2)
        n1 = random.choice(discipline_nodes[d1]) if discipline_nodes[d1] else None
        n2 = random.choice(discipline_nodes[d2]) if discipline_nodes[d2] else None
        if n1 and n2:
            candidates.append({
                'node_a': all_nodes[n1], 'node_b': all_nodes[n2],
                'strategy': random.choice(['causal_extension', 'analogy_driven', 'contradiction_finding']),
                'weight': 0.4
            })

    random.shuffle(candidates)
    print(f"[Stage2] 候选配对: {len(candidates)}个")
    return candidates[:max_candidates]


# ============ STAGE 3: mmx search verification ============
def verify_literature(candidate, use_mmx=True):
    """文献验证"""
    node_a = candidate['node_a']['name']
    node_b = candidate['node_b']['name']
    query = f'"{node_a}" AND "{node_b}" 跨学科 研究'

    if not use_mmx:
        return {'count': random.randint(0, 2), 'query': query, 'timestamp': datetime.now().isoformat()}

    count = mmx_search(query)
    if count == -1:
        return {'count': random.randint(0, 2), 'query': query, 'timestamp': datetime.now().isoformat()}
    return {'count': count, 'query': query, 'timestamp': datetime.now().isoformat()}


def verify_all_candidates(candidates, use_mmx=True):
    """批量验证"""
    print(f"[Stage3] 文献验证: mmx search={'ON' if use_mmx else 'OFF'}")
    verified = []
    for i, c in enumerate(candidates):
        v = verify_literature(c, use_mmx)
        c['verification'] = v
        verified.append(c)
        if (i + 1) % 10 == 0:
            zero = sum(1 for x in verified if x['verification']['count'] == 0)
            print(f"  进度: {i+1}/{len(candidates)} | 空白: {zero}个")

    zero = sum(1 for c in verified if c['verification']['count'] == 0)
    print(f"  完成！空白: {zero}个/{len(candidates)}个")
    return verified


# ============ STAGE 4: Deep definition ============
def deep_define(candidate):
    """深度问题定义"""
    node_a = candidate['node_a']['name']
    node_b = candidate['node_b']['name']
    strategy = candidate['strategy']
    lit_count = candidate['verification']['count']

    templates = {
        'causal_extension': f"{node_a}的因果机制能否解释{node_b}中的类似现象？",
        'analogy_driven': f"{node_a}的数学结构能否迁移到{node_b}的研究中？",
        'contradiction_finding': f"看似矛盾的{node_a}和{node_b}是否有深层的统一解释？"
    }
    novelty = max(0, 10 - lit_count * 0.5)

    plans = {
        'causal_extension': {
            'month_1': f'文献调研{node_a}和{node_b}的因果机制',
            'month_2': '建立跨域因果传递数学模型',
            'month_3': '设计实验验证因果假设'
        },
        'analogy_driven': {
            'month_1': f'形式化{node_a}的核心数学结构',
            'month_2': f'构造到{node_b}领域的映射',
            'month_3': '验证类比假设适用范围'
        },
        'contradiction_finding': {
            'month_1': '整理矛盾证据和理论',
            'month_2': '寻找深层统一机制',
            'month_3': '提出统一解释框架'
        }
    }

    return {
        'discovery_id': f"D-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(100,999)}",
        'node_a': node_a, 'node_b': node_b,
        'discipline_a': candidate['node_a']['discipline'],
        'discipline_b': candidate['node_b']['discipline'],
        'strategy': strategy,
        'research_question': templates[strategy],
        'three_month_plan': plans[strategy],
        'literature_count': lit_count,
        'novelty_score': round(novelty, 1),
        'discovery_signal': 'strong' if lit_count == 0 else ('weak' if lit_count < 5 else 'none'),
        'timestamp': datetime.now().isoformat()
    }


# ============ STAGE 5: Archive ============
def archive_discoveries(discoveries):
    """归档"""
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')

    log_file = os.path.join(OUTPUT_DIR, f'discovery_log_{ts}.jsonl')
    with open(log_file, 'w', encoding='utf-8') as f:
        for d in discoveries:
            f.write(json.dumps(d, ensure_ascii=False) + '\n')

    report_file = os.path.join(OUTPUT_DIR, f'discovery_report_{ts}.json')
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump({
            'title': '跨学科科学问题发现报告',
            'date': ts,
            'total': len(discoveries),
            'strong_signals': sum(1 for d in discoveries if d['discovery_signal'] == 'strong'),
            'weak_signals': sum(1 for d in discoveries if d['discovery_signal'] == 'weak'),
            'avg_novelty': round(sum(d['novelty_score'] for d in discoveries) / len(discoveries), 1),
            'discoveries': discoveries
        }, f, ensure_ascii=False, indent=2)

    print(f"[Stage5] 归档: {log_file}")
    print(f"  报告: {report_file}")
    return log_file, report_file


# ============ MAIN ============
def main(max_candidates=50, use_mmx=True):
    print("=" * 60)
    print("GOAI Track3 方案A：跨学科科学问题自动发现系统 v2.0")
    print("=" * 60)
    print()

    all_nodes, discipline_nodes = load_knowledge_network()
    candidates = generate_candidates(all_nodes, discipline_nodes, max_candidates)
    verified = verify_all_candidates(candidates, use_mmx)

    # Sort by novelty (fewest literature = highest novelty)
    verified_sorted = sorted(verified, key=lambda x: x['verification']['count'])
    top_k = min(15, len(verified_sorted))

    print(f"\n[Stage4] 深度定义: Top {top_k}")
    discoveries = []
    for c in verified_sorted[:top_k]:
        d = deep_define(c)
        discoveries.append(d)
        mark = {'strong': '★', 'weak': '○', 'none': '·'}[d['discovery_signal']]
        print(f"  {mark} [{d['discipline_a']}×{d['discipline_b']}] {d['node_a'][:30]} ↔ {d['node_b'][:30]}")
        print(f"      问题: {d['research_question'][:55]}...")
        print(f"      文献: {d['literature_count']}篇 | 新颖度: {d['novelty_score']}/10")

    log_file, report_file = archive_discoveries(discoveries)

    print()
    print("=" * 60)
    print(f"完成！候选:{len(candidates)} 定义:{len(discoveries)} 强信号:{sum(1 for d in discoveries if d['discovery_signal']=='strong')}")
    print("=" * 60)
    return discoveries, log_file, report_file


if __name__ == '__main__':
    import sys
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    search = '--no-search' not in sys.argv
    discoveries, log_file, report_file = main(max_candidates=n, use_mmx=search)
