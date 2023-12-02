import os
import tarfile
from tqdm import tqdm
import json
import docker

import chardet

from utils import list_tex_files, filter_tex_file


RAW_PATH = "arxiv-subset-100"
PARSE_PATH = "parse"
OUTPUT_TEX_PATH = 'tex.jsonl'

client = docker.from_env()


def extract_interleaved_mm(main_tex_file):
    pass


def write_to_jsonl(tex_filelist):
    with open(OUTPUT_TEX_PATH, 'a', encoding='utf-8') as f_out:
        for tex_file in tex_filelist:
            with open(tex_file, 'rb') as f:
                encoding = chardet.detect(f.read())['encoding']
                
            with open(tex_file, 'r', encoding=encoding) as f_tex:
                content = f_tex.read()
                
                id_path = os.path.relpath(tex_file, PARSE_PATH)
                data = {
                    "id": id_path,
                    "text": content
                }
                
                json_line = json.dumps(data)
                f_out.write(json_line + '\n')

def extract_tex(arxiv_parse_path):
    # 找到所有.tex文件
    tex_filelist = list_tex_files(arxiv_parse_path)
    # 过滤有意义的.tex文件
    assert len(tex_filelist) > 0, "没有.tex文件"
    if len(tex_filelist) > 1:
        tex_filelist = list(filter(filter_tex_file, tex_filelist))
    write_to_jsonl(tex_filelist)
    return tex_filelist

def tex_to_html(main_tex_file, id):
    # 将.tex文件编译为html文件
    container_config = {
        'image': 'arxivvanity/engrafo',
        'command': [
            'engrafo',
            '{}'.format(main_tex_file),
            '{}/{}/html_output/'.format(PARSE_PATH, id)
        ],
        'volumes': {
            f"{os.getcwd()}": {
                'bind': '/workdir',
                'mode': 'rw'
            }
        },
        'working_dir': '/workdir',
        'detach': True,
    }
    container = client.containers.run(**container_config)
    print("Parse {id} from tex to html in Container ID:{cid}".format(id=id, cid=container.id))

def extract_one_arxiv(id):
    """
    提取一个arxiv_id的所有内容
    """
    is_success = None
    arxiv_path = os.path.join(RAW_PATH, id)
    arxiv_parse_path = os.path.join(PARSE_PATH, id)
    os.makedirs(arxiv_parse_path, exist_ok=True)
    pdf_path = os.path.join(arxiv_path, "pdf", id+".pdf")
    source_file_path = os.path.join(arxiv_path, "source", id)
    source_file_path_gz = source_file_path + ".tar.gz"

    # 重命名压缩包
    if os.path.exists(source_file_path):
        os.rename(source_file_path, source_file_path_gz)

    # 检查文件完整性
    if (not os.path.exists(pdf_path)) or (not os.path.exists(source_file_path_gz)):
        print(id + "文件不完整")
        is_success = False

    # 解压
    try:
        with tarfile.open(source_file_path_gz, 'r:gz') as tar_ref:
            # 这里会有一批古老的压缩包无法解压
            tar_ref.extractall(arxiv_parse_path)

        # 1.解析代码, 得到包含".tex"类型文件的list
        tex_filelist = extract_tex(arxiv_parse_path)
        # 2.将tex文件编译为html文件
        tex_to_html(tex_filelist[0], id)
        # 2.解析图文 (只有一个入口文件)
        extract_interleaved_mm(tex_filelist[0])
        is_success = True
    except tarfile.InvalidHeaderError as e:
        print(id, e)
        is_success = False
    finally:
        # 复原压缩包
        if os.path.exists(source_file_path_gz):
            os.rename(source_file_path_gz, source_file_path)
        return is_success


def main():
    os.makedirs(PARSE_PATH, exist_ok=True)
    arxiv_ids = [d for d in os.listdir(RAW_PATH) if os.path.isdir(os.path.join(RAW_PATH, d))]
    arxiv_ids = arxiv_ids
    success = 0
    for arxiv_id in tqdm(arxiv_ids):
        if extract_one_arxiv(arxiv_id):
            success += 1
    print("total: {}, success: {}, ratio: {}%,".format(len(arxiv_ids), success, success/len(arxiv_ids)*100.0))


if __name__ == "__main__":
    main()