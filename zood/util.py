import yaml
import os
import subprocess
from typing import Dict, List, NewType

DIR_TREE = NewType("DIR_TREE", Dict[str, List[Dict[str, str]]])

def load_yml(file_path: str) -> DIR_TREE:
    if not os.path.exists(file_path):
        print_info("找不到文件" + file_path)
        exit(0)

    with open(file_path, "r", encoding="utf-8") as f:
        file_data = f.read()

    data = yaml.load(file_data, Loader=yaml.FullLoader)
    return data


def save_yml(data, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)


def yml_sort(yml:DIR_TREE):
    for _, files in yml.items():
        files.sort(key=lambda item: list(item.values())[0])


def print_info(msg, color="red"):
    if color == "red":
        print(f"\033[1;31m{msg}\033[0m")
    elif color == "green":
        print(f"\033[1;32m{msg}\033[0m")


def get_zood_config():
    """
    获取基础配置信息, 优先查找当前目录下 md-docs/ 是否存在 _config.yml
    如果本地不存在则使用全局 _config.yml 作为配置信息
    """
    global_config_path = os.path.join(os.path.dirname(__file__), "config", "_config.yml")

    global_zood_config = load_yml(global_config_path)
    md_dir_name = global_zood_config["markdown_folder"]

    local_config_path = os.path.join(md_dir_name, "_config.yml")
    if os.path.exists(local_config_path):
        # 如果本地 config 比全局 config 的 key 少, 则说明更新了 zood 版本
        local_config = load_yml(local_config_path)
        global_config = load_yml(global_config_path)
        if set(local_config.keys()) < set(global_config.keys()):
            key_names = set(global_config.keys()) - set(local_config.keys())
            print_info(f'当前 zood 版本更新了配置项: {key_names}, 请使用 zood config 进行同步', color="red")
            exit()
        return local_config
    else:
        return load_yml(global_config_path)


def caculate_front_next_url(flat_paths: list, path: str, md_dir_name):
    dir_name = path.split(os.sep)[1]
    file_name = path.split(os.sep)[2].replace(".md", "")
    if dir_name == ".":
        dir_name = md_dir_name
    path = os.path.join(dir_name, file_name)
    pos = flat_paths.index(path)

    front_url = '"."'
    next_url = '"."'

    if pos != 0:
        front_url = htmlRelativeUrl(flat_paths[pos - 1])
    if pos != len(flat_paths) - 1:
        next_url = htmlRelativeUrl(flat_paths[pos + 1])

    return front_url, next_url


def htmlRelativeUrl(url: str):
    new_url = url.replace(os.sep, "/")
    new_url = f'"../../{new_url}"'
    return new_url


def get_dir_tree(directory_tree, md_dir_name):
    tree_html = ""
    for item in directory_tree:
        dir_name = list(item.keys())[0]
        files = item[dir_name]
        if dir_name == ".":
            dir_name = md_dir_name
            for file in files:
                dir_url_link = f"../../{dir_name}/{file}"
                # print(dir_url_link)
                tree_html += treeItem(file, dir_url_link)
        else:
            sub_tree_html = ""
            for file in files:
                dir_url_link = f"../../{dir_name}/{file}"
                # print(dir_url_link)
                sub_tree_html += treeItem(file, dir_url_link)

            first_dir_url_link = f"../../{dir_name}/{files[0]}"
            tree_html += treeItem(dir_name, first_dir_url_link, sub_tree=sub_tree_html)

    # print(tree_html)
    return f'<div class="dir-tree">{tree_html}</div>'


def treeItem(name, dir_url_link, sub_tree=False):
    if sub_tree:
        link = f'<a href="{dir_url_link}" >{name}</a>'
        return f"<ul><li>{link}{sub_tree}</li></ul>"
    else:
        link = f'<a href="{dir_url_link}" >{name}</a>'
        return f"<ul><li>{link}</li></ul>"


def url_replace(html_template: str, front_url, next_url, control):
    html_template = html_template.replace("<%front_url%>", front_url).replace("<%next_url%>", next_url)
    html_template = html_template.replace("<%control%>", f'"{control}"')
    return html_template


def get_github_icon(enable_github):
    if enable_github is False:
        return ""

    url = get_github_repo_url()
    if url == "":
        return ""
    else:
        return join_github_icon(url)


def get_github_repo_url() -> str:
    url = ""
    try:
        output = subprocess.check_output(["git", "config", "--get", "remote.origin.url"]).strip()
        url = output.decode("utf-8")
        if url.startswith("git@"):
            parts = url.split(":")
            if len(parts) == 2:
                username_and_repo = parts[1]
                username, repo = username_and_repo[:-4].split("/")
                url = f"https://github.com/{username}/{repo}"
    except subprocess.CalledProcessError:
        return url
    return url


def join_github_icon(url: str):
    # https://tholman.com/github-corners/
    github_icon = (
        '<a href="'
        + url
        + '" target="_blank" class="github-corner" aria-label="View source on GitHub"><svg width="80" height="80" viewBox="0 0 250 250" style="fill:#151513; color:#fff; position: absolute; top: 0; border: 0; right: 0;" aria-hidden="true"><path d="M0,0 L115,115 L130,115 L142,142 L250,250 L250,0 Z"></path><path d="M128.3,109.0 C113.8,99.7 119.0,89.6 119.0,89.6 C122.0,82.7 120.5,78.6 120.5,78.6 C119.2,72.0 123.4,76.3 123.4,76.3 C127.3,80.9 125.5,87.3 125.5,87.3 C122.9,97.6 130.6,101.9 134.4,103.2" fill="currentColor" style="transform-origin: 130px 106px;" class="octo-arm"></path><path d="M115.0,115.0 C114.9,115.1 118.7,116.5 119.8,115.4 L133.7,101.6 C136.9,99.2 139.9,98.4 142.2,98.6 C133.8,88.0 127.5,74.4 143.8,58.0 C148.5,53.4 154.0,51.2 159.7,51.0 C160.3,49.4 163.2,43.6 171.4,40.1 C171.4,40.1 176.1,42.5 178.8,56.2 C183.1,58.6 187.2,61.8 190.9,65.4 C194.5,69.0 197.7,73.2 200.1,77.6 C213.8,80.2 216.3,84.9 216.3,84.9 C212.7,93.1 206.9,96.0 205.4,96.6 C205.1,102.4 203.0,107.8 198.3,112.5 C181.9,128.9 168.3,122.5 157.7,114.1 C157.9,116.9 156.7,120.9 152.7,124.9 L141.0,136.5 C139.8,137.7 141.6,141.9 141.8,141.8 Z" fill="currentColor" class="octo-body"></path></svg></a><style>.github-corner:hover .octo-arm{animation:octocat-wave 560ms ease-in-out}@keyframes octocat-wave{0%,100%{transform:rotate(0)}20%,60%{transform:rotate(-25deg)}40%,80%{transform:rotate(10deg)}}@media (max-width:500px){.github-corner:hover .octo-arm{animation:none}.github-corner .octo-arm{animation:octocat-wave 560ms ease-in-out}}</style>'
    )
    return github_icon
