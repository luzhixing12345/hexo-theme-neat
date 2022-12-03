# zood

Github仓库网页文档 + 注释生成文档

## [主题预览](https://luzhixing12345.github.io/zood/)

## 快速开始

### 1.安装

```bash
pip install zood
```

### 2.运行

进入当前项目根目录

- 生成文档

  ```bash
  zood -g
  ```

- 部署(需配合.git信息)

  ```bash
  zood -d
  ```

### 3.更多信息查阅[配置文档](https://luzhixing12345.github.io/zood/)

```bash
zood -h
```

## 开发

```bash
poetry build
```

```bash
poetry config pypi-token.pypi my-token
```

```bash
poetry publish
```
