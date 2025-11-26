# XutheringWavesUID

<p align="center">
  <a href="https://github.com/tyql688/WutheringWavesUID"><img src="https://s2.loli.net/2024/10/08/ku3pLJBPoGjfQWq.png" width="256" height="256" alt="WutheringWavesUID"></a>
<h1 align = "center">XutheringWavesUID 2.0</h1>

## 说明

本插件为 [WutheringWavesUID](https://github.com/tyql688) 的封包版本，旨在避免代码偷窃，顺便避免加强了评分和伤害计算的保护，以免更改模板导致的计算不一致问题。本插件将继续更新，对于不计划自己编写权重计算和伤害计算的用户，与之前没有任何区别。

本插件并未更改原名，只需更换上游源并强制拉取即可：

```bash
cp -r gsuid_core/gsuid_core/plugins/WutheringWavesUID ./WutheringWavesUID_bak
cd gsuid_core/gsuid_core/plugins/WutheringWavesUID
git remote set-url origin https://github.com/Loping151/XutheringWavesUID.git
git fetch --all && git reset --hard origin/$(git rev-parse --abbrev-ref HEAD)
```
将继承原有数据和配置。

如果为首次安装：
```
git clone https://github.com/Loping151/XutheringWavesUID.git WutheringWavesUID
``` 

总排行数据库重建：群号 653696746

## 丨安装提醒

> **注意：该插件为[早柚核心(gsuid_core)](https://github.com/Genshin-bots/gsuid_core)
的扩展，具体安装方式可参考[GenshinUID](https://github.com/KimigaiiWuyi/GenshinUID)**
>
> **如果已经是最新版本的`gsuid_core`, 可以直接对bot发送`core安装插件WutheringWavesUID`，然后重启core以应用安装**

## 丨反馈渠道

- QQ群号：[653696746](http://qm.qq.com/cgi-bin/qm/qr?_wv=1027&k=hmB3ejtTx6cIDHegsLM91jd1Rn97eGAe&authKey=HqcnRdI0S98dUBcpHxwjWv72LYpUYE%2BSXVOEjiuBrAZbepCHPzP86szZFhxeiQkG&noverify=0&group_code=653696746)

## 丨其他

+ 本项目仅供学习使用，请勿用于商业用途
+ [GPL-3.0 License](https://github.com/tyql688/WutheringWavesUID/blob/master/LICENSE)

## 支持设备列表：
win_amd64: python3.10-3.13<br>
win_arm64: no<br>
linux_x86_64: python3.10-3.13<br>
linux_aarch64: python3.10-3.13<br>
macos_intel: no<br>
macos_apple: python3.10-3.13<br>

## 致谢
- ⭐[Echo](https://github.com/tyql688)，无需多言
- 特别鸣谢 [Wuyi无疑](https://github.com/KimigaiiWuyi) 为 WutheringWavesUID 作出的巨大贡献！本插件的设计图均出自 Wuyi无疑
  之手！！！
- [鸣潮声骸评分工具](http://asfaz.cn/mingchao/rule.html) 鸣潮声骸评分工具
- [waves-plugin](https://github.com/erzaozi/waves-plugin) Yunzai 鸣潮游戏数据查询插件
- [Yunzai-Kuro-Plugin](https://github.com/TomyJan/Yunzai-Kuro-Plugin) Yunzai 库洛插件
- [Kuro-API-Collection](https://github.com/TomyJan/Kuro-API-Collection) 库街区 API 文档
- 特别鸣谢以下攻略作者
  - [Moealkyne](https://www.taptap.cn/user/533395803)
  - [小沐XMu](https://www.kurobbs.com/person-center?id=10450567)
  - [金铃子攻略组](https://space.bilibili.com/487275027)
  - [結星](https://www.kurobbs.com/person-center?id=10015697)
  - [小羊早睡不遭罪](https://space.bilibili.com/37331716)
  - [吃我无痕](https://space.bilibili.com/347744)
