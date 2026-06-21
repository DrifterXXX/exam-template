#!/usr/bin/env python3
"""解析期货投资分析考试HTML为JSON数据"""
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
    """从start_idx开始提取完整的div块（处理嵌套）"""
    depth = 0
    i = start_idx
    while i < len(html):
        if html[i:i+4] == '<div':
            depth += 1
            # Skip to end of opening tag
            gt = html.find('>', i)
            if gt > 0:
                i = gt + 1
            else:
                i += 4
        elif html[i:i+6] == '</div>':
            depth -= 1
            if depth == 0:
                return html[start_idx:i+6]
            i += 6
        else:
            i += 1
    return html[start_idx:]

def parse_futures(html_path, output_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    chapters = []
    
    # Find all chapter divs
    ch_positions = [(m.start(), m.end()) for m in re.finditer(r'<div class="chapter"[^>]*>', html)]
    
    for ci, (ch_start, tag_end) in enumerate(ch_positions):
        ch_block = extract_div_block(html, ch_start)
        
        # Chapter title
        ch_title_match = re.search(r'<div class="chapter-header".*?>(.*?)</div>', ch_block, re.DOTALL)
        if not ch_title_match:
            continue
        
        ch_title = strip_html(ch_title_match.group(1))
        ch_title = re.sub(r'\s*▶\s*$', '', ch_title)
        ch_title = re.sub(r'^(?:核心|次核心|基础|📐|🏆)\s+\d+%\s*', '', ch_title)
        ch_title = re.sub(r'^(?:核心|次核心|基础|📐|🏆)\s*', '', ch_title)
        ch_title = ch_title.strip()
        
        ch_id = ci + 1
        
        # Find all KP blocks within chapter
        sections = []
        kp_positions = [(m.start(), m.end()) for m in re.finditer(r'<div class="kp"[^>]*>', ch_block)]
        
        for ki, (kp_start, kp_tag_end) in enumerate(kp_positions):
            kp_block = extract_div_block(ch_block, kp_start)
            
            # KP title
            kp_title_match = re.search(r'<span class="kp-title">(.*?)</span>', kp_block)
            if not kp_title_match:
                continue
            
            kp_title = strip_html(kp_title_match.group(1))
            kp_title = re.sub(r'\s*★核心考点★\s*', '', kp_title)
            kp_title = re.sub(r'\s*★核心★\s*', '', kp_title)
            kp_title = kp_title.strip()
            
            # KP body
            kp_body_idx = kp_block.find('<div class="kp-body">')
            if kp_body_idx < 0:
                continue
            
            kp_body = extract_div_block(kp_block, kp_body_idx)
            
            # Extract content-text divs
            content_parts = []
            for ct in re.finditer(r'<div class="content-text">(.*?)</div>', kp_body, re.DOTALL):
                text = strip_html(ct.group(1))
                if text and len(text) > 10:
                    content_parts.append(text)
            
            # Extract formula-box divs
            formulas = []
            for fb in re.finditer(r'<div class="formula-box">(.*?)</div>', kp_body, re.DOTALL):
                text = strip_html(fb.group(1))
                if text:
                    # Remove label prefix
                    text = re.sub(r'^[^\n]+\n', '', text).strip()
                    formulas.append(text)
            
            # Extract warning-box (tips)
            tips = []
            for wb in re.finditer(r'<div class="warning-box">(.*?)</div>', kp_body, re.DOTALL):
                text = strip_html(wb.group(1))
                if text:
                    tips.append(text)
            
            # Extract calculation cases
            examples = []
            case_idx = kp_body.find('🧮 计算案例')
            if case_idx > 0:
                case_section = kp_body[case_idx:case_idx+1000]
                for ct in re.finditer(r'<div class="content-text">(.*?)</div>', case_section, re.DOTALL):
                    text = strip_html(ct.group(1))
                    if text and len(text) > 10:
                        examples.append({"q": text, "a": ""})
            
            # Extract exam questions
            questions = []
            for eq in re.finditer(r'<div class="exam-q">(.*?)</div>\s*(?:</div>|<div class="exam-q")', kp_body, re.DOTALL):
                q_block = eq.group(1)
                
                # Question type
                q_type = ''
                qt_match = re.search(r'<div class="q-type">(.*?)</div>', q_block)
                if qt_match:
                    q_type = strip_html(qt_match.group(1))
                
                # Get question text (before answer div)
                ans_div_idx = q_block.find('<div class="answer">')
                if ans_div_idx > 0:
                    q_text_area = q_block[:ans_div_idx]
                else:
                    q_text_area = q_block
                
                q_text = strip_html(q_text_area)
                q_text = re.sub(r'^\s*【[^】]*】\s*', '', q_text)
                q_text = q_text.strip()
                
                if not q_text or len(q_text) < 5:
                    continue
                
                # Extract inline options (A. xxx B. xxx C. xxx D. xxx)
                opts = []
                opt_matches = re.findall(r'([A-D])[.．]\s*([^A-D]{3,50}?)(?=\s+[A-D][.．]|\s*<br|<div|$)', q_text, re.DOTALL)
                if opt_matches:
                    opts = [strip_html(o[1]) for o in opt_matches]
                    # Remove options from question text
                    q_text_clean = q_text
                    for o in opt_matches:
                        q_text_clean = q_text_clean.replace(f"{o[0]}. {o[1]}", '')
                    q_text = strip_html(q_text_clean)
                
                if len(opts) < 2:
                    # Try to find options in separate lines
                    opt_lines = re.findall(r'^\s*([A-D])[.．]\s*(.+)$', q_text, re.MULTILINE)
                    if opt_lines:
                        opts = [strip_html(o[1]) for o in opt_lines]
                        q_text = re.sub(r'^\s*[A-D][.．].+$', '', q_text, flags=re.MULTILINE).strip()
                
                if len(opts) < 2:
                    # For true/false questions
                    if '正确' in q_text or '错误' in q_text or '判断' in q_type:
                        opts = ['正确', '错误']
                    else:
                        continue
                
                # Answer
                ans = 1
                ans_match = re.search(r'<div class="answer">(.*?)</div>', q_block, re.DOTALL)
                if ans_match:
                    ans_text = strip_html(ans_match.group(1))
                    ans_letter = re.search(r'答案[：:]\s*([A-Da-d])', ans_text)
                    if ans_letter:
                        a = ans_letter.group(1).upper()
                        ans = ord(a) - ord('A') + 1
                    elif '正确' in ans_text:
                        ans = 1
                    elif '错误' in ans_text:
                        ans = 2
                
                # Explanation
                explanation = ''
                exp_match = re.search(r'<div class="explain">(.*?)</div>', q_block, re.DOTALL)
                if exp_match:
                    explanation = strip_html(exp_match.group(1))
                
                questions.append({
                    "q": q_text,
                    "opts": opts[:4],
                    "ans": ans,
                    "explanation": explanation
                })
            
            content = '\n'.join(content_parts[:10])
            
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
            "title": "期货投资分析考试 · 备考中心",
            "subtitle": "全面覆盖考试大纲 · 精选真题 · 核心考点背诵",
            "modules": [
                {"id": "review", "icon": "📚", "title": "复习宝典", "desc": "12章完整精讲，涵盖概念详解、核心公式、计算案例、易错提醒和历年真题", "stats": ["12章", f"{total_secs}节", "完整覆盖"]},
                {"id": "practice", "icon": "📝", "title": "真题精练", "desc": "精选历年真题，互动式点击答题，即时反馈解析", "stats": ["互动答题", "即时解析", "真题实战"]},
                {"id": "memorize", "icon": "🎯", "title": "考前背诵", "desc": "核心考点速记，公式汇总，易错提醒", "stats": ["核心考点", "快速回顾"]}
            ]
        },
        "chapters": chapters
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 期货数据解析完成:")
    print(f"  章节: {len(chapters)}")
    print(f"  知识点: {total_secs}")
    print(f"  题目: {total_qs}")
    print(f"  公式: {total_formulas}")
    print(f"  提示: {total_tips}")
    print(f"  内容总字数: {total_content}")
    print(f"  输出: {output_path}")
    
    # Show samples
    if chapters and chapters[0]['sections']:
        print(f"\n示例 - {chapters[0]['title']}:")
        for s in chapters[0]['sections'][:3]:
            print(f"  {s['title']}:")
            print(f"    content={len(s['content'])}字, formulas={len(s['formulas'])}, tips={len(s['tips'])}, questions={len(s['questions'])}")
            if s['content']:
                print(f"    内容预览: {s['content'][:80]}...")

if __name__ == '__main__':
    parse_futures(
        '/Users/ayong/Downloads/package/期货投资分析考试_完整复习宝典.html',
        '/Users/ayong/Downloads/package/futures_data.json'
    )
