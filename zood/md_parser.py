
import os
import shutil
from .util import *
from .zood import parseConfig,parseMarkdownFiles,caculateFrontNext,directoryTreeList,urlReplace

def parseDocs(md_dir_name):
    
    directory_tree, markdown_htmls = parseMarkdownFiles(md_dir_name)
    generateDocs(directory_tree,markdown_htmls,md_dir_name)
 
    
def generateDocs(directory_tree,markdown_htmls,md_dir_name):

    config = getZoodConfig()
    html_dir_name = config['options']['html_folder']
    
    index_README_path = os.path.join(md_dir_name,'.','README.md')
    if not os.path.exists(index_README_path):
        printInfo(f'您需要保留 {md_dir_name}/README.md 作为首页')
        exit()

    if os.path.exists(html_dir_name):
        printInfo(f"删除原 {html_dir_name}",color='green')
        shutil.rmtree(html_dir_name)
    os.makedirs(os.path.join(html_dir_name,'articles'))
    os.makedirs(os.path.join(html_dir_name,'js'))
    os.makedirs(os.path.join(html_dir_name,'css'))
    os.makedirs(os.path.join(html_dir_name,'img'))
    
    # 复制图片
    imgs_path = os.path.join(os.path.dirname(__file__),'config','img')
    for root,_,files in os.walk(imgs_path):
        for img in files:
            shutil.copy(os.path.join(root,img),os.path.join(html_dir_name,'img'))
    
    html_template = parseConfig(config)
    index_html_path = os.path.join(html_dir_name,'index.html')
    html_template = html_template.replace('directory-tree-scope',directoryTreeList(directory_tree))


    flat_paths = [] # 扁平化之后的所有文件的路径
    for item in directory_tree:
        dir_name = list(item.keys())[0]
        files = item[dir_name]
        if dir_name == '.':
            dir_name = md_dir_name
        for file in files:
            flat_paths.append(os.path.join(dir_name,file))
    
    front_url, next_url = caculateFrontNext(flat_paths,index_README_path,md_dir_name)
    
    with open(index_html_path,'w',encoding='utf-8') as f:
        index_html_template = html_template.replace('../../.','')
        next_url = next_url.replace('../..','./articles')
        index_html_template = urlReplace(index_html_template,front_url,next_url,'b')
        f.write(index_html_template.replace('html-scope',markdown_htmls[index_README_path]))
    
    for file_path, markdown_html in markdown_htmls.items():
        dir_name = file_path.split(os.sep)[1]
        file_name = file_path.split(os.sep)[2].replace('.md','')
        if dir_name == '.':
            dir_name = md_dir_name
        doc_path = os.path.join(html_dir_name,"articles",dir_name,file_name)
        os.makedirs(doc_path)
        html_path = os.path.join(doc_path,'index.html')
        with open(html_path,'w',encoding='utf-8') as f:
            front_url, next_url = caculateFrontNext(flat_paths,file_path,md_dir_name)
            print(html_path,front_url,next_url)
            final_html = urlReplace(html_template,front_url,next_url,'ab')
            f.write(final_html.replace('html-scope',markdown_html))
            
    printInfo("已生成 docs/",color='green')            
    