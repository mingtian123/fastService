# 东莞科技局爬虫 (DgCrawler)

基于 ASP.NET Core + Playwright 的网页爬虫，用于抓取东莞市科学技术局网站数据。

## 功能特性

- 🚀 基于 Playwright 的自动化浏览器控制
- 📄 抓取政策文件、通知公告、工作动态
- 💾 支持 JSON 和 CSV 格式导出
- 📝 详细的日志记录
- 🔄 自动处理相对URL和日期解析

## 系统要求

- .NET 8.0 SDK
- Linux/Windows/macOS

## 安装依赖

```bash
# 安装 .NET 8.0 SDK (如果未安装)
# Ubuntu/Debian
wget https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/packages-microsoft-prod.deb -O packages-microsoft-prod.deb
sudo dpkg -i packages-microsoft-prod.deb
sudo apt-get update
sudo apt-get install -y dotnet-sdk-8.0

# 安装 Playwright 浏览器
cd dotnet-crawler
dotnet build
dotnet tool install --global Microsoft.Playwright.CLI
playwright install chromium
```

## 运行爬虫

```bash
cd dotnet-crawler
dotnet run
```

## 输出文件

运行后会在 `output/` 目录生成：

- `data.json` - 完整的抓取数据（JSON格式）
- `policies.csv` - 政策文件列表（CSV格式）
- `notices.csv` - 通知公告列表（CSV格式）
- `home.html` - 首页HTML
- `policy_list.html` - 政策列表页HTML
- `policy_*.html` - 政策详情页HTML

## 项目结构

```
dotnet-crawler/
├── DgCrawler.csproj    # 项目文件
├── Program.cs          # 主程序代码
├── README.md           # 说明文档
├── logs/               # 日志目录（运行时生成）
└── output/             # 输出目录（运行时生成）
```

## 抓取的数据字段

### 政策文件 (Policy)
- 标题
- 发布日期
- 来源机构
- 分类
- 正文内容
- URL
- 抓取时间

### 通知公告 (Notice)
- 标题
- 发布日期
- 分类（通知/公告）
- URL
- 抓取时间

### 工作动态 (News)
- 标题
- 发布日期
- 摘要
- 分类
- URL
- 抓取时间

## 注意事项

1. 请遵守目标网站的 robots.txt 和使用条款
2. 建议设置合理的抓取间隔，避免对服务器造成压力
3. 生产环境建议使用代理IP池

## License

MIT
