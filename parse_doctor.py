#!/usr/bin/env python3
"""解析教育博士考试HTML为JSON数据"""
import re, json

def strip_html(s):
    s = re.sub(r'<br\s*/?>', '\n', s)
    s = re.sub(r'<[^>]+>', '', s)
    s = re.sub(r'&nbsp;', ' ', s)
    s = re.sub(r'&amp;', '&', s)
    s = re.sub(r'&lt;', '<', s)
    s = re.sub(r'&gt;', '>', s)
    s = re.sub(r'&quot;', '"', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def extract_div_block(html, start_idx):
    depth = 0
    i = start_idx
    while i < len(html):
        if html[i:i+4] == '<div':
            depth += 1
            gt = html.find('>', i)
            if gt > 0: i = gt + 1
            else: i += 4
        elif html[i:i+6] == '</div>':
            depth -= 1
            if depth == 0:
                return html[start_idx:i+6]
            i += 6
        else:
            i += 1
    return html[start_idx:]

def parse_doctor(html_path, output_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    chapters = []
    
    # Find chapter cards
    ch_positions = [(m.start(), m.end()) for m in re.finditer(r'<div class="chapter-card">', html)]
    
    for ci, (ch_start, tag_end) in enumerate(ch_positions):
        ch_block = extract_div_block(html, ch_start)
        
        # Chapter title
        ch_title_match = re.search(r'<span class="chapter-title">(.*?)</span>', ch_block)
        if not ch_title_match:
            # Try alternative
            ch_title_match = re.search(r'<button class="chapter-toggle"[^>]*>(.*?)</button>', ch_block, re.DOTALL)
        
        if not ch_title_match:
            continue
        
        ch_title = strip_html(ch_title_match.group(1))
        ch_title = re.sub(r'\s*▼\s*$', '', ch_title)
        ch_title = re.sub(r'\s*★核心★\s*', '', ch_title)
        ch_title = re.sub(r'\s*★重点★\s*', '', ch_title)
        ch_title = re.sub(r'\s*基础\s*', '', ch_title)
        ch_title = ch_title.strip()
        
        ch_id = ci + 1
        
        # Find KP items
        sections = []
        kp_positions = [(m.start(), m.end()) for m in re.finditer(r'<div class="kp-item">', ch_block)]
        
        for ki, (kp_start, kp_tag_end) in enumerate(kp_positions):
            kp_block = extract_div_block(ch_block, kp_start)
            
            # KP title
            kp_title_match = re.search(r'<span class="kp-label">[^<]*</span>\s*(.*?)(?:</span>|<span)', kp_block)
            if not kp_title_match:
                kp_title_match = re.search(r'<button class="kp-toggle"[^>]*>.*?<span[^>]*>(.*?)</span>', kp_block, re.DOTALL)
            
            if not kp_title_match:
                continue
            
            kp_title = strip_html(kp_title_match.group(1))
            kp_title = re.sub(r'\s*▼\s*$', '', kp_title)
            kp_title = kp_title.strip()
            
            # KP body
            kp_body_idx = kp_block.find('<div class="kp-body"')
            if kp_body_idx < 0:
                continue
            
            kp_body = extract_div_block(kp_block, kp_body_idx)
            
            # Extract content-text paragraphs
            content_parts = []
            for ct in re.finditer(r'<p class="content-text">(.*?)</p>', kp_body, re.DOTALL):
                text = strip_html(ct.group(1))
                if text and len(text) > 20:
                    content_parts.append(text)
            
            # Extract tables as content
            for tbl in re.finditer(r'<table[^>]*>(.*?)</table>', kp_body, re.DOTALL):
                # Convert table to text
                rows = []
                for tr in re.finditer(r'<tr>(.*?)</tr>', tbl.group(1), re.DOTALL):
                    cells = []
                    for cell in re.finditer(r'<t[hd][^>]*>(.*?)</t[hd]>', tr.group(1), re.DOTALL):
                        cells.append(strip_html(cell.group(1)))
                    if cells:
                        rows.append(' | '.join(cells))
                if rows:
                    content_parts.append('表格: ' + '; '.join(rows[:5]))
            
            # Extract key points / tips
            tips = []
            
            # Find "易错辨析" sections
            for st in re.finditer(r'<div class="section-title[^"]*mistakes[^"]*"[^>]*>(.*?)</div>', kp_body, re.DOTALL):
                idx = st.end()
                # Get next 2000 chars and extract content
                section_area = kp_body[idx:idx+3000]
                
                # Extract table rows as tips
                for tr in re.finditer(r'<tr>(.*?)</tr>', section_area, re.DOTALL):
                    cells = []
                    for cell in re.finditer(r'<t[hd][^>]*>(.*?)</t[hd]>', tr.group(1), re.DOTALL):
                        cells.append(strip_html(cell.group(1)))
                    if len(cells) >= 2:
                        tips.append(f"❌ {cells[0]} → ✅ {cells[1]}")
                
                # Also extract paragraphs
                for ct in re.finditer(r'<p class="content-text">(.*?)</p>', section_area, re.DOTALL):
                    text = strip_html(ct.group(1))
                    if text and len(text) > 10:
                        tips.append(text)
            
            # Find "核心要点" / "重点" sections
            for st in re.finditer(r'<div class="section-title[^"]*"[^>]*>(.*?)</div>', kp_body, re.DOTALL):
                title = strip_html(st.group(1))
                if '要点' in title or '重点' in title or '关键' in title or '核心' in title or '记忆' in title:
                    idx = st.end()
                    body_match = re.search(r'<div class="section-body">(.*?)</div>', kp_body[idx:idx+2000], re.DOTALL)
                    if body_match:
                        for ct in re.finditer(r'<p class="content-text">(.*?)</p>', body_match.group(1), re.DOTALL):
                            text = strip_html(ct.group(1))
                            if text and len(text) > 10:
                                tips.append(text)
            
            # Extract formulas (if any)
            formulas = []
            for fb in re.finditer(r'<div class="formula[^"]*"[^>]*>(.*?)</div>', kp_body, re.DOTALL):
                text = strip_html(fb.group(1))
                if text:
                    formulas.append(text)
            
            # Extract examples
            examples = []
            for ex in re.finditer(r'<div class="[^"]*(?:example|case)[^"]*"[^>]*>(.*?)</div>', kp_body, re.DOTALL):
                text = strip_html(ex.group(1))
                if text and len(text) > 10:
                    examples.append({"q": text[:300], "a": ""})
            
            # Extract questions
            questions = []
            for eq in re.finditer(r'<div class="exam-q[^"]*"[^>]*>(.*?)</div>\s*(?:</div>|<div class="exam-q")', kp_body, re.DOTALL):
                q_block = eq.group(1)
                q_text = strip_html(q_block)
                if q_text and len(q_text) > 10:
                    # Try to extract options
                    opts = re.findall(r'([A-D])[.．]\s*([^A-D]{3,50})', q_text)
                    if opts:
                        opts = [strip_html(o[1]) for o in opts]
                        q_text_clean = q_text
                        for o in opts:
                            q_text_clean = q_text_clean.replace(f"{o[0]}. {o[1]}", '')
                        q_text = strip_html(q_text_clean)
                    
                    ans_match = re.search(r'答案[：:]\s*([A-Da-d])', q_block)
                    ans = 1
                    if ans_match:
                        a = ans_match.group(1).upper()
                        ans = ord(a) - ord('A') + 1
                    
                    questions.append({"q": q_text[:300], "opts": opts[:4] if opts else [], "ans": ans, "explanation": ""})
            
            content = '\n'.join(content_parts[:15])
            
            sec_id = f"ch{ch_id:02d}-sec{ki+1:02d}"
            sections.append({
                "id": sec_id,
                "title": kp_title,
                "content": content,
                "formulas": formulas,
                "examples": examples,
                "tips": tips,
                "questions": questions
            })
        
        chapters.append({
            "id": f"ch{ch_id:02d}",
            "title": ch_title,
            "level": f"ch{ch_id:02d}",
            "sections": sections
        })
    
    total_secs = sum(len(ch['sections']) for ch in chapters)
    total_qs = sum(len(s.get('questions', [])) for ch in chapters for s in ch['sections'])
    total_formulas = sum(len(s.get('formulas', [])) for ch in chapters for s in ch['sections'])
    total_tips = sum(len(s.get('tips', [])) for ch in chapters for s in ch['sections'])
    total_content = sum(len(s.get('content', '')) for ch in chapters for s in ch['sections'])
    
    data = {
        "site": {
            "title": "教育博士备考中心",
            "subtitle": "教育博士考试全面备考 · 核心考点 · 专题精讲",
            "modules": [
                {"id": "review", "icon": "📚", "title": "专题精讲", "desc": f"{len(chapters)}个专题完整覆盖教育学核心知识点", "stats": [f"{len(chapters)}专题", f"{total_secs}知识点", "完整覆盖"]},
                {"id": "practice", "icon": "📝", "title": "真题精练", "desc": "互动式答题训练", "stats": ["互动答题", "即时解析"]},
                {"id": "memorize", "icon": "🎯", "title": "考前背诵", "desc": "核心考点速记", "stats": ["核心考点", "快速回顾"]}
            ]
        },
        "chapters": chapters
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 博士数据解析完成:")
    print(f"  专题: {len(chapters)}")
    print(f"  知识点: {total_secs}")
    print(f"  题目: {total_qs}")
    print(f"  公式: {total_formulas}")
    print(f"  提示: {total_tips}")
    print(f"  内容总字数: {total_content}")
    print(f"  输出: {output_path}")
    
    if chapters and chapters[0]['sections']:
        print(f"\n示例 - {chapters[0]['title']}:")
        for s in chapters[0]['sections'][:3]:
            print(f"  {s['title']}:")
            print(f"    content={len(s['content'])}字, tips={len(s['tips'])}, questions={len(s['questions'])}")
            if s['content']:
                print(f"    内容预览: {s['content'][:80]}...")

if __name__ == '__main__':
    parse_doctor(
        '/Users/ayong/services/edu-doctor/教育博士考试_完整复习宝典.html',
        '/Users/ayong/services/edu-doctor/doctor_data.json'
    )
