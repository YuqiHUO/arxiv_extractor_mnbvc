# arxiv_extractor_mnbvc
本项目从arxiv原始文件中收集两种语料:
1. .tex类型的代码语料
2. 多模态语料

## get started
### environment
```
pip install chardet docker
```
安装 https://github.com/arxiv-vanity/engrafo 中的[docker file](https://hub.docker.com/r/arxivvanity/engrafo/tags)


### usage
准备好arxiv原始文件
```
python extract.py
```

得到的`tex.jsonl`是代码语料。

