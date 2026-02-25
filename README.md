# 6657烂梗 - AstrBot 插件

[![AstrBot](https://img.shields.io/badge/AstrBot-Plugin-blue)](https://github.com/AstrBotDevs/AstrBot)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

从 [sb6657.cn](https://sb6657.cn) 获取随机烂梗或按关键词搜索烂梗的 [AstrBot](https://github.com/AstrBotDevs/AstrBot) 插件。

## 功能

- 🎲 **随机烂梗**：从 17000+ 条烂梗库中随机获取一条
- 🔍 **关键词搜索**：根据关键词搜索匹配的烂梗，从结果中随机返回一条

## 安装

### 方式一：通过 AstrBot 管理面板安装

1. 下载本仓库的 Release 中的 `.zip` 文件
2. 打开 AstrBot 管理面板 → 插件管理 → 上传 `.zip` 安装
3. 重启 AstrBot 生效

### 方式二：通过 Git 安装

在 AstrBot 管理面板的插件管理中，输入本仓库地址安装。

## 指令

| 指令 | 别名 | 说明 |
|------|------|------|
| `/烂梗` | `/随机烂梗`、`/langen` | 随机获取一条烂梗 |
| `/搜梗 <关键词>` | `/查梗`、`/找梗`、`/sougen` | 搜索包含关键词的烂梗 |

## 使用示例

```
/烂梗
🎲 随机烂梗 #8075
donk：载大哥我又坐牢了，看你狙几个每月挣一个冠军我就心生一股恨意

/搜梗 donk
🔍 搜索「donk」找到 5 条相关结果，随机一条：
#8075 donk：载大哥我又坐牢了...
```

## 适配平台

支持 AstrBot 所有消息平台（QQ / NapCat、Telegram 等）。

## 数据来源

本插件的烂梗数据来自 [sb6657.cn](https://sb6657.cn)（斗鱼主播玩机器的弹幕烂梗收集站）。

本插件与 sb6657.cn 网站及其开发者无关联，仅通过其公开 API 获取数据。烂梗内容版权归原作者及 sb6657.cn 所有。

## 依赖

- [aiohttp](https://pypi.org/project/aiohttp/)

## 开发说明

本插件大部分由 AI（GitHub Copilot / Claude）开发，包括代码编写、API 调试、文档撰写及打包发布。

## 许可证

本项目基于 [MIT License](LICENSE) 开源。
