#!/usr/bin/env python3
"""为备考站点生成TTS音频
用法: python3 generate_audio.py <data.json> <output_dir> [--limit N]
"""
import json, os, sys, subprocess, asyncio

async def generate_audio(text, output_path, voice="zh-CN-YunxiNeural"):
    """使用edge-tts生成音频"""
    # Truncate text to avoid timeout (max ~3000 chars per audio)
    if len(text) > 3000:
        text = text[:3000] + "..."
    
    cmd = [
        "edge-tts",
        "--voice", voice,
        "--text", text,
        "--write-media", output_path
    ]
    
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode == 0 and os.path.exists(output_path):
            return True
        else:
            print(f"  ⚠️ 失败: {stderr.decode()[:100]}")
            return False
    except Exception as e:
        print(f"  ⚠️ 异常: {e}")
        return False

async def main():
    if len(sys.argv) < 3:
        print("用法: python3 generate_audio.py <data.json> <output_dir> [--limit N]")
        sys.exit(1)
    
    data_path = sys.argv[1]
    output_dir = sys.argv[2]
    limit = None
    
    if '--limit' in sys.argv:
        idx = sys.argv.index('--limit')
        if idx + 1 < len(sys.argv):
            limit = int(sys.argv[idx + 1])
    
    os.makedirs(output_dir, exist_ok=True)
    
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    chapters = data.get('chapters', [])
    total = sum(len(ch.get('sections', [])) for ch in chapters)
    
    print(f"📦 准备生成 {total} 个音频文件")
    if limit:
        print(f"⏱️  限制: 前 {limit} 个")
    
    count = 0
    success = 0
    
    for ch in chapters:
        for sec in ch.get('sections', []):
            if limit and count >= limit:
                break
            
            count += 1
            sec_id = sec['id']
            title = sec['title']
            content = sec.get('content', '')
            
            if not content or len(content) < 20:
                print(f"  ⏭️  [{count}/{total}] {title} (内容太短)")
                continue
            
            output_path = os.path.join(output_dir, f"{sec_id}.mp3")
            
            if os.path.exists(output_path):
                print(f"  ⏭️  [{count}/{total}] {title} (已存在)")
                success += 1
                continue
            
            # Prepare text: title + content
            text = f"{title}。{content[:2500]}"
            
            print(f"  🎙️  [{count}/{total}] {title[:30]}...")
            
            if await generate_audio(text, output_path):
                success += 1
                print(f"  ✅ 完成")
            else:
                print(f"  ❌ 失败")
        
        if limit and count >= limit:
            break
    
    print(f"\n✅ 音频生成完成: {success}/{count} 成功")
    print(f"📁 输出目录: {output_dir}")

if __name__ == '__main__':
    asyncio.run(main())
