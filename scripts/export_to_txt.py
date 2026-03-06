import os
import re

def export_chapters_to_txt():
    """
    将正文文件夹中的所有 Markdown 章节文件合并成一个 TXT 文件
    """
    # 获取当前工作目录下的正文文件夹路径
    main_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    source_dir = os.path.join(main_dir, '正文')
    output_file = os.path.join(main_dir, '全文导出.txt')
    
    # 检查正文文件夹是否存在
    if not os.path.exists(source_dir):
        print(f"错误: 找不到正文文件夹 {source_dir}")
        return
    
    # 获取所有以数字开头的章节文件（如 第001章.md）
    chapter_files = [f for f in os.listdir(source_dir) if f.endswith('.md') and f.startswith('第')]
    
    # 按照章节顺序排序（按数字顺序）
    chapter_files.sort(key=lambda x: int(re.search(r'\d+', x).group()) if re.search(r'\d+', x) else 0)
    
    if not chapter_files:
        print("未找到任何章节文件")
        return
    
    print(f"找到 {len(chapter_files)} 个章节文件")
    
    # 打开输出文件
    with open(output_file, 'w', encoding='utf-8') as outfile:
        # 写入标题信息
        outfile.write("="*50 + "\n")
        outfile.write("小说全文导出\n")
        outfile.write("="*50 + "\n\n")
        
        # 遍历每个章节文件
        for i, filename in enumerate(chapter_files):
            filepath = os.path.join(source_dir, filename)
            
            print(f"正在处理 {filename}...")
            
            # 读取每个 Markdown 文件的内容
            with open(filepath, 'r', encoding='utf-8') as infile:
                content = infile.read()
                
                # 在每个章节前添加分隔符和章节名
                outfile.write(f"\n{'='*60}\n")
                outfile.write(f"{filename}\n")
                outfile.write(f"{'='*60}\n")
                outfile.write(content)
                outfile.write("\n")  # 添加额外换行作为章节间的分隔
    
    print(f"\n所有章节已成功合并到 {output_file}")
    print(f"共处理了 {len(chapter_files)} 个章节")


if __name__ == "__main__":
    export_chapters_to_txt()