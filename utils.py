import os
import glob


def list_tex_files(root_folder):
    # 使用os.path.join确保路径在所有操作系统上都有效
    pattern = os.path.join(root_folder, '**', '*.[tT][eE][xX]')
    
    # 使用glob.glob搜寻所有匹配的文件。注意recursive=True是必要的，以搜索所有子文件夹
    tex_files = glob.glob(pattern, recursive=True)

    return tex_files


def filter_tex_file(tex_file):
    # 筛选.tex文件是否保留
    filename = os.path.basename(tex_file)
    
    # 根据文件名判断
    name_check = ["main", "Main", "MAIN", "paper", "Paper"]
    if any(name in filename for name in name_check):
        return True
    
    # 根据文件内容判断
    tags = ["\\title", "\\section", "\\subsection"]
    with open(tex_file, 'r', encoding='utf-8') as file:
        for line in file:
            if any(line.strip().startswith(tag) for tag in tags):
                return True
    return False