#!/usr/bin/env python3
"""
Exam Template Builder — 通用备考网站构建脚本
从JSON数据生成完整的备考站点（index/review/practice/memorize）
用法: python3 build.py <data.json> <output_dir>
"""
import json, os, sys, re
from datetime import datetime

def load_data(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_template(name):
    tpl_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(tpl_dir, name), 'r', encoding='utf-8') as f:
        return f.read()

def esc(s):
    if not s: return ''
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

def build_index(data, out_dir):
    site = data['site']
    css = load_template('template.css')
    
    modules_html = ''
    for m in site.get('modules', []):
        stats_html = ' '.join(f'<span>{s}</span>' for s in m.get('stats', []))
        modules_html += f'''
<a class="entry" href="{m['id']}.html">
<span class="icon">{m['icon']}</span>
<h2>{m['title']}</h2>
<p class="desc">{m['desc']}</p>
<div class="stats">{stats_html}</div>
</a>'''
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{site['title']}</title>
<style>{css}</style>
</head>
<body>
<div class="header">
<button class="theme-btn">🌙 主题</button>
<h1>{site['title']}</h1>
<p>{site.get('subtitle', '')}</p>
</div>
<div class="container">
<div class="entries">{modules_html}</div>
</div>
<div class="footer">© {datetime.now().year} {site['title']}</div>
<script src="template.js"></script>
</body></html>'''
    
    with open(os.path.join(out_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html)
    print('✅ index.html')

def build_review(data, out_dir):
    site = data['site']
    chapters = data.get('chapters', [])
    css = load_template('template.css')
    
    # Build chapter cards
    chapters_html = ''
    levels = set()
    for ch in chapters:
        level = ch.get('level', ch['id'])
        levels.add(level)
        sections_html = ''
        for sec in ch.get('sections', []):
            content_html = f'<div class="content-block"><p>{esc(sec.get("content", ""))}</p></div>'
            
            # Formulas
            formulas = sec.get('formulas', [])
            if formulas:
                f_html = ''.join(f'<div class="formula-box">{esc(f)}</div>' for f in formulas)
                content_html += f'<div class="content-block"><h4>📐 核心公式</h4>{f_html}</div>'
            
            # Examples
            examples = sec.get('examples', [])
            if examples:
                e_html = ''.join(f'<div class="content-block"><p><strong>题目：</strong>{esc(e["q"])}</p><p><strong>解答：</strong>{esc(e["a"])}</p></div>' for e in examples)
                content_html += f'<div class="content-block"><h4>📝 计算案例</h4>{e_html}</div>'
            
            # Tips
            tips = sec.get('tips', [])
            if tips:
                t_html = ''.join(f'<div class="tip-box">⚠️ {esc(t)}</div>' for t in tips)
                content_html += f'<div class="content-block"><h4>💡 易错提醒</h4>{t_html}</div>'
            
            sections_html += f'''
<div class="section-card" data-id="{sec['id']}">
<div class="section-header" onclick="toggleSection(this)">
<span class="sec-title">{esc(sec['title'])}</span>
<span class="sec-arrow">▶</span>
</div>
<div class="section-body">{content_html}</div>
</div>'''
        
        chapters_html += f'''
<div class="chapter-card" data-level="{level}">
<div class="chapter-header" onclick="toggleChapter(this)">
<span class="ch-title">{esc(ch['title'])}</span>
<span class="ch-arrow">▶</span>
</div>
<div class="chapter-body">{sections_html}</div>
</div>'''
    
    # Filter buttons
    filter_html = '<button class="filter-btn active" onclick="setFilter(\'all\',this)">全部</button>'
    for lvl in sorted(levels):
        filter_html += f'<button class="filter-btn" onclick="setFilter(\'{lvl}\',this)">{lvl}</button>'
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{site['title']} · 复习宝典</title>
<style>{css}</style>
</head>
<body>
<div class="header">
<a class="back-link" href="index.html">← 返回</a>
<button class="theme-btn">🌙 主题</button>
<h1>📚 复习宝典</h1>
<p>{site.get('subtitle', '')}</p>
</div>
<div class="controls">
<input type="text" class="search-box" placeholder="搜索章节标题、概念、公式..." oninput="initSearch()">
<div class="filter-btns">{filter_html}</div>
<div style="text-align:center;margin-top:8px;font-size:0.85em;color:var(--text-light)">
共 <span id="search-count">{len(chapters)}</span> 章
<button onclick="expandAll()" style="margin-left:12px;padding:4px 12px;border-radius:6px;border:1px solid var(--border);background:var(--card-bg);color:var(--text);cursor:pointer">▼ 全部展开</button>
<button onclick="collapseAll()" style="margin-left:8px;padding:4px 12px;border-radius:6px;border:1px solid var(--border);background:var(--card-bg);color:var(--text);cursor:pointer">▲ 全部收起</button>
</div>
</div>
<div class="container">{chapters_html}</div>
<div class="footer">© {datetime.now().year} {site['title']}</div>
<script src="template.js"></script>
</body></html>'''
    
    with open(os.path.join(out_dir, 'review.html'), 'w', encoding='utf-8') as f:
        f.write(html)
    print('✅ review.html')

def build_practice(data, out_dir):
    site = data['site']
    chapters = data.get('chapters', [])
    css = load_template('template.css')
    
    # Collect all questions
    all_questions = []
    for ch in chapters:
        for sec in ch.get('sections', []):
            for i, q in enumerate(sec.get('questions', [])):
                uid = f"{sec['id']}-q{i}"
                all_questions.append({
                    'uid': uid,
                    'chapter': ch['title'],
                    'section': sec['title'],
                    'q': q['q'],
                    'opts': q.get('opts', []),
                    'ans': q['ans'],
                    'explanation': q.get('explanation', '')
                })
    
    if not all_questions:
        print('⚠️  无题目数据，跳过 practice.html')
        return
    
    questions_html = ''
    for q in all_questions:
        opts_html = ''
        for j, opt in enumerate(q['opts']):
            opts_html += f'<button class="opt-btn" onclick="selectOption(this,{j+1},\'{q["uid"]}\')">{chr(65+j)}. {esc(opt)}</button>'
        
        exp_html = f'<span style="color:var(--success)">✅ 正确答案：{chr(64+q["ans"])}</span>'
        if q['explanation']:
            exp_html += f'<span style="color:var(--text-light)"> — {esc(q["explanation"])}</span>'
        
        questions_html += f'''
<div class="q-block" id="qblock-{q['uid']}">
<div style="font-size:0.8em;color:var(--text-light);margin-bottom:6px">{esc(q['chapter'])} · {esc(q['section'])}</div>
<div class="q-text">{esc(q['q'])}</div>
<div class="opts">{opts_html}</div>
<button class="show-ans-btn" id="sbtn-{q['uid']}" onclick="revealAnswer('{q['uid']}',{q['ans']})">显示答案</button>
<div class="explanation" id="exp-{q['uid']}">{exp_html}</div>
</div>'''
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{site['title']} · 真题精练</title>
<style>{css}</style>
</head>
<body>
<div class="header">
<a class="back-link" href="index.html">← 返回</a>
<button class="theme-btn">🌙 主题</button>
<h1>📝 真题精练</h1>
<p>互动答题 · 显示答案按钮 · 即时解析</p>
</div>
<div class="container">
<div class="stats-bar">
<div class="stat-item"><div class="stat-label">已做</div><div class="stat-val" id="stat-done">0</div></div>
<div class="stat-item"><div class="stat-label">正确</div><div class="stat-val" id="stat-correct">0</div></div>
<div class="stat-item"><div class="stat-label">正确率</div><div class="stat-val" id="stat-rate">0%</div></div>
</div>
{questions_html}
</div>
<div class="footer">© {datetime.now().year} {site['title']}</div>
<script src="template.js"></script>
</body></html>'''
    
    with open(os.path.join(out_dir, 'practice.html'), 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'✅ practice.html ({len(all_questions)} 题)')

def build_memorize(data, out_dir):
    site = data['site']
    chapters = data.get('chapters', [])
    css = load_template('template.css')
    
    # Extract key points (tips + formulas) for memorization
    cards_html = ''
    count = 0
    for ch in chapters:
        for sec in ch.get('sections', []):
            items = []
            for f in sec.get('formulas', []):
                items.append(('📐', f))
            for t in sec.get('tips', []):
                items.append(('💡', t))
            if items:
                items_html = ''.join(f'<div style="padding:8px 0;border-bottom:1px solid var(--border)"><span style="margin-right:8px">{icon}</span>{esc(text)}</div>' for icon, text in items)
                cards_html += f'''
<div class="section-card">
<div class="section-header" onclick="toggleSection(this)">
<span class="sec-title">{esc(sec['title'])}</span>
<span class="sec-arrow">▶</span>
</div>
<div class="section-body">{items_html}</div>
</div>'''
                count += 1
    
    if not cards_html:
        print('⚠️  无背诵内容，跳过 memorize.html')
        return
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{site['title']} · 考前背诵</title>
<style>{css}</style>
</head>
<body>
<div class="header">
<a class="back-link" href="index.html">← 返回</a>
<button class="theme-btn">🌙 主题</button>
<h1>🎯 考前背诵</h1>
<p>核心公式 · 易错提醒 · 快速回顾</p>
</div>
<div class="container">
<div style="text-align:center;margin-bottom:16px;font-size:0.9em;color:var(--text-light)">
共 {count} 个考点
<button onclick="expandAll()" style="margin-left:12px;padding:4px 12px;border-radius:6px;border:1px solid var(--border);background:var(--card-bg);color:var(--text);cursor:pointer">▼ 全部展开</button>
<button onclick="collapseAll()" style="margin-left:8px;padding:4px 12px;border-radius:6px;border:1px solid var(--border);background:var(--card-bg);color:var(--text);cursor:pointer">▲ 全部收起</button>
</div>
{cards_html}
</div>
<div class="footer">© {datetime.now().year} {site['title']}</div>
<script src="template.js"></script>
</body></html>'''
    
    with open(os.path.join(out_dir, 'memorize.html'), 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'✅ memorize.html ({count} 个考点)')

def main():
    if len(sys.argv) < 3:
        print('用法: python3 build.py <data.json> <output_dir>')
        sys.exit(1)
    
    data_path = sys.argv[1]
    out_dir = sys.argv[2]
    
    os.makedirs(out_dir, exist_ok=True)
    
    # Copy template files
    tpl_dir = os.path.dirname(os.path.abspath(__file__))
    for f in ['template.css', 'template.js']:
        src = os.path.join(tpl_dir, f)
        dst = os.path.join(out_dir, f)
        with open(src, 'r', encoding='utf-8') as sf:
            with open(dst, 'w', encoding='utf-8') as df:
                df.write(sf.read())
    
    data = load_data(data_path)
    
    print(f'📦 构建站点: {data["site"]["title"]}')
    print(f'📁 输出目录: {out_dir}')
    print()
    
    build_index(data, out_dir)
    build_review(data, out_dir)
    build_practice(data, out_dir)
    build_memorize(data, out_dir)
    
    print(f'\n✅ 构建完成！共生成 4 个页面 + 模板文件')

if __name__ == '__main__':
    main()
