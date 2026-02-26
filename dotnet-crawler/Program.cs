using Microsoft.Playwright;
using HtmlAgilityPack;
using Newtonsoft.Json;
using Serilog;
using System.Text.RegularExpressions;

namespace DgCrawler;

public class Program
{
    private static ILogger _logger = null!;
    private static readonly string BaseUrl = "https://dgstb.dg.gov.cn/";
    
    public static async Task Main(string[] args)
    {
        // 配置日志
        _logger = new LoggerConfiguration()
            .MinimumLevel.Debug()
            .WriteTo.Console()
            .WriteTo.File("logs/crawler-.log", rollingInterval: RollingInterval.Day)
            .CreateLogger();

        _logger.Information("东莞科技局爬虫启动...");
        _logger.Information("目标网站: {Url}", BaseUrl);

        try
        {
            // 安装Playwright浏览器
            _logger.Information("正在安装Playwright浏览器...");
            Microsoft.Playwright.Program.Main(new[] { "install", "chromium" });
            
            var crawler = new DgCrawler(_logger);
            await crawler.RunAsync();
            
            _logger.Information("爬虫执行完成");
        }
        catch (Exception ex)
        {
            _logger.Error(ex, "爬虫执行失败");
            Environment.Exit(1);
        }
    }
}

public class DgCrawler
{
    private readonly ILogger _logger;
    private readonly string _baseUrl;
    private readonly string _outputDir;
    private readonly List<PolicyInfo> _policies = new();
    private readonly List<NewsInfo> _news = new();
    private readonly List<NoticeInfo> _notices = new();

    public DgCrawler(ILogger logger)
    {
        _logger = logger;
        _baseUrl = "https://dgstb.dg.gov.cn/";
        _outputDir = Path.Combine(Directory.GetCurrentDirectory(), "output");
        Directory.CreateDirectory(_outputDir);
    }

    public async Task RunAsync()
    {
        using var playwright = await Playwright.CreateAsync();
        await using var browser = await playwright.Chromium.LaunchAsync(new BrowserTypeLaunchOptions
        {
            Headless = true,
            SlowMo = 100
        });

        var context = await browser.NewContextAsync(new BrowserNewContextOptions
        {
            UserAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        });

        var page = await context.NewPageAsync();

        try
        {
            // 1. 抓取首页
            _logger.Information("正在抓取首页...");
            await page.GotoAsync(_baseUrl, new PageGotoOptions { WaitUntil = WaitUntilState.NetworkIdle });
            await Task.Delay(2000);
            
            var homeHtml = await page.ContentAsync();
            await SaveHtmlAsync("home.html", homeHtml);
            ParseHomePage(homeHtml);

            // 2. 抓取政策文件
            _logger.Information("正在抓取政策文件...");
            await CrawlPolicyPagesAsync(page);

            // 3. 抓取通知公告
            _logger.Information("正在抓取通知公告...");
            await CrawlNoticePagesAsync(page);

            // 4. 抓取工作动态
            _logger.Information("正在抓取工作动态...");
            await CrawlNewsPagesAsync(page);

            // 5. 保存汇总数据
            await SaveDataAsync();

            _logger.Information("数据抓取完成，共抓取:");
            _logger.Information("- 政策文件: {Count} 条", _policies.Count);
            _logger.Information("- 通知公告: {Count} 条", _notices.Count);
            _logger.Information("- 工作动态: {Count} 条", _news.Count);
        }
        catch (Exception ex)
        {
            _logger.Error(ex, "抓取过程中发生错误");
            throw;
        }
    }

    private void ParseHomePage(string html)
    {
        var doc = new HtmlDocument();
        doc.LoadHtml(html);

        // 解析首页轮播图和重点内容
        var bannerNodes = doc.DocumentNode.SelectNodes("//div[contains(@class,'banner')]//a");
        if (bannerNodes != null)
        {
            _logger.Information("首页发现 {Count} 个轮播项", bannerNodes.Count);
        }
    }

    private async Task CrawlPolicyPagesAsync(IPage page)
    {
        // 政策文件栏目
        var policyUrl = _baseUrl + "zwgk/zcwj/zcjd/";
        
        try
        {
            await page.GotoAsync(policyUrl, new PageGotoOptions { WaitUntil = WaitUntilState.NetworkIdle });
            await Task.Delay(2000);

            var html = await page.ContentAsync();
            await SaveHtmlAsync("policy_list.html", html);

            var doc = new HtmlDocument();
            doc.LoadHtml(html);

            // 解析政策列表
            var policyNodes = doc.DocumentNode.SelectNodes("//div[contains(@class,'list')]//li|//div[contains(@class,'list')]//tr");
            if (policyNodes != null)
            {
                foreach (var node in policyNodes.Take(20)) // 限制抓取数量
                {
                    try
                    {
                        var titleNode = node.SelectSingleNode(".//a");
                        var dateNode = node.SelectSingleNode(".//span[contains(@class,'date')]|.//td[last()]");
                        
                        if (titleNode != null)
                        {
                            var policy = new PolicyInfo
                            {
                                Title = CleanText(titleNode.InnerText),
                                Url = ResolveUrl(titleNode.GetAttributeValue("href", "")),
                                PublishDate = ParseDate(dateNode?.InnerText),
                                Category = "政策解读",
                                CrawlTime = DateTime.Now
                            };

                            // 抓取详情页
                            if (!string.IsNullOrEmpty(policy.Url))
                            {
                                await CrawlPolicyDetailAsync(page, policy);
                            }

                            _policies.Add(policy);
                            _logger.Debug("抓取政策: {Title}", policy.Title);
                        }
                    }
                    catch (Exception ex)
                    {
                        _logger.Warning(ex, "解析政策项失败");
                    }
                }
            }

            _logger.Information("政策文件抓取完成，共 {Count} 条", _policies.Count);
        }
        catch (Exception ex)
        {
            _logger.Error(ex, "抓取政策文件失败");
        }
    }

    private async Task CrawlPolicyDetailAsync(IPage page, PolicyInfo policy)
    {
        try
        {
            await page.GotoAsync(policy.Url, new PageGotoOptions { WaitUntil = WaitUntilState.NetworkIdle, Timeout = 30000 });
            await Task.Delay(1500);

            var html = await page.ContentAsync();
            var doc = new HtmlDocument();
            doc.LoadHtml(html);

            // 解析正文内容
            var contentNode = doc.DocumentNode.SelectSingleNode("//div[contains(@class,'content')]|//div[contains(@class,'detail')]|//div[contains(@class,'main')]");
            if (contentNode != null)
            {
                policy.Content = CleanText(contentNode.InnerText);
                policy.HtmlContent = contentNode.InnerHtml;
            }

            // 解析发布机构
            var sourceNode = doc.DocumentNode.SelectSingleNode("//span[contains(text(),'发布机构')]|//div[contains(@class,'source')]");
            if (sourceNode != null)
            {
                policy.Source = CleanText(sourceNode.InnerText).Replace("发布机构：", "").Trim();
            }

            // 保存详情页HTML
            var fileName = $"policy_{policy.GetHashCode()}.html";
            await SaveHtmlAsync(fileName, html);
        }
        catch (Exception ex)
        {
            _logger.Warning(ex, "抓取政策详情失败: {Url}", policy.Url);
        }
    }

    private async Task CrawlNoticePagesAsync(IPage page)
    {
        // 通知公告栏目
        var noticeUrls = new[]
        {
            _baseUrl + "zwgk/tzgg/",
            _baseUrl + "zwgk/tzgg/tz/"
        };

        foreach (var url in noticeUrls)
        {
            try
            {
                await page.GotoAsync(url, new PageGotoOptions { WaitUntil = WaitUntilState.NetworkIdle });
                await Task.Delay(2000);

                var html = await page.ContentAsync();
                var doc = new HtmlDocument();
                doc.LoadHtml(html);

                var noticeNodes = doc.DocumentNode.SelectNodes("//div[contains(@class,'list')]//li|//table//tr[position()>1]");
                if (noticeNodes != null)
                {
                    foreach (var node in noticeNodes.Take(15))
                    {
                        try
                        {
                            var titleNode = node.SelectSingleNode(".//a");
                            var dateNode = node.SelectSingleNode(".//span[contains(@class,'date')]|.//td[last()]");

                            if (titleNode != null)
                            {
                                var notice = new NoticeInfo
                                {
                                    Title = CleanText(titleNode.InnerText),
                                    Url = ResolveUrl(titleNode.GetAttributeValue("href", "")),
                                    PublishDate = ParseDate(dateNode?.InnerText),
                                    Category = url.Contains("/tz/") ? "通知" : "公告",
                                    CrawlTime = DateTime.Now
                                };

                                _notices.Add(notice);
                            }
                        }
                        catch (Exception ex)
                        {
                            _logger.Warning(ex, "解析公告项失败");
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                _logger.Error(ex, "抓取公告失败: {Url}", url);
            }
        }

        _logger.Information("通知公告抓取完成，共 {Count} 条", _notices.Count);
    }

    private async Task CrawlNewsPagesAsync(IPage page)
    {
        // 工作动态/新闻栏目
        var newsUrls = new[]
        {
            _baseUrl + "gzdt/",
            _baseUrl + "gzdt/bmdt/"
        };

        foreach (var url in newsUrls)
        {
            try
            {
                await page.GotoAsync(url, new PageGotoOptions { WaitUntil = WaitUntilState.NetworkIdle });
                await Task.Delay(2000);

                var html = await page.ContentAsync();
                var doc = new HtmlDocument();
                doc.LoadHtml(html);

                var newsNodes = doc.DocumentNode.SelectNodes("//div[contains(@class,'list')]//li|//div[contains(@class,'news')]//div[contains(@class,'item')]");
                if (newsNodes != null)
                {
                    foreach (var node in newsNodes.Take(15))
                    {
                        try
                        {
                            var titleNode = node.SelectSingleNode(".//a|.//h3|.//h4");
                            var dateNode = node.SelectSingleNode(".//span[contains(@class,'date')]|.//time");
                            var summaryNode = node.SelectSingleNode(".//p|.//div[contains(@class,'summary')]");

                            if (titleNode != null)
                            {
                                var news = new NewsInfo
                                {
                                    Title = CleanText(titleNode.InnerText),
                                    Url = ResolveUrl(titleNode.GetAttributeValue("href", "")),
                                    PublishDate = ParseDate(dateNode?.InnerText),
                                    Summary = summaryNode != null ? CleanText(summaryNode.InnerText) : null,
                                    Category = "工作动态",
                                    CrawlTime = DateTime.Now
                                };

                                _news.Add(news);
                            }
                        }
                        catch (Exception ex)
                        {
                            _logger.Warning(ex, "解析新闻项失败");
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                _logger.Error(ex, "抓取新闻失败: {Url}", url);
            }
        }

        _logger.Information("工作动态抓取完成，共 {Count} 条", _news.Count);
    }

    private async Task SaveHtmlAsync(string fileName, string html)
    {
        var filePath = Path.Combine(_outputDir, fileName);
        await File.WriteAllTextAsync(filePath, html);
        _logger.Debug("保存HTML: {FilePath}", filePath);
    }

    private async Task SaveDataAsync()
    {
        // 保存JSON数据
        var data = new CrawlResult
        {
            CrawlTime = DateTime.Now,
            Source = _baseUrl,
            Policies = _policies,
            Notices = _notices,
            News = _news
        };

        var json = JsonConvert.SerializeObject(data, Formatting.Indented);
        var jsonPath = Path.Combine(_outputDir, "data.json");
        await File.WriteAllTextAsync(jsonPath, json);
        _logger.Information("数据已保存: {Path}", jsonPath);

        // 保存CSV格式
        await SaveCsvAsync();
    }

    private async Task SaveCsvAsync()
    {
        // 政策CSV
        var policyCsv = "标题,发布日期,来源,分类,URL\n";
        foreach (var p in _policies)
        {
            policyCsv += $"\"{p.Title}\",{p.PublishDate:yyyy-MM-dd},\"{p.Source}\",\"{p.Category}\",\"{p.Url}\"\n";
        }
        await File.WriteAllTextAsync(Path.Combine(_outputDir, "policies.csv"), policyCsv);

        // 公告CSV
        var noticeCsv = "标题,发布日期,分类,URL\n";
        foreach (var n in _notices)
        {
            noticeCsv += $"\"{n.Title}\",{n.PublishDate:yyyy-MM-dd},\"{n.Category}\",\"{n.Url}\"\n";
        }
        await File.WriteAllTextAsync(Path.Combine(_outputDir, "notices.csv"), noticeCsv);

        _logger.Information("CSV文件已保存");
    }

    private string ResolveUrl(string href)
    {
        if (string.IsNullOrEmpty(href)) return "";
        if (href.StartsWith("http")) return href;
        if (href.StartsWith("/")) return _baseUrl.TrimEnd('/') + href;
        return _baseUrl + href;
    }

    private string CleanText(string? text)
    {
        if (string.IsNullOrEmpty(text)) return "";
        return Regex.Replace(text.Trim(), @"\s+", " ");
    }

    private DateTime ParseDate(string? dateText)
    {
        if (string.IsNullOrEmpty(dateText)) return DateTime.MinValue;
        
        dateText = CleanText(dateText);
        
        // 尝试多种日期格式
        var formats = new[] { "yyyy-MM-dd", "yyyy/MM/dd", "MM-dd", "yyyy年MM月dd日" };
        foreach (var format in formats)
        {
            if (DateTime.TryParseExact(dateText, format, null, System.Globalization.DateTimeStyles.None, out var date))
                return date;
        }
        
        if (DateTime.TryParse(dateText, out var parsedDate))
            return parsedDate;
        
        return DateTime.MinValue;
    }
}

// 数据模型
public class PolicyInfo
{
    public string Title { get; set; } = "";
    public string Url { get; set; } = "";
    public DateTime PublishDate { get; set; }
    public string Source { get; set; } = "";
    public string Category { get; set; } = "";
    public string? Content { get; set; }
    public string? HtmlContent { get; set; }
    public DateTime CrawlTime { get; set; }
}

public class NoticeInfo
{
    public string Title { get; set; } = "";
    public string Url { get; set; } = "";
    public DateTime PublishDate { get; set; }
    public string Category { get; set; } = "";
    public DateTime CrawlTime { get; set; }
}

public class NewsInfo
{
    public string Title { get; set; } = "";
    public string Url { get; set; } = "";
    public DateTime PublishDate { get; set; }
    public string? Summary { get; set; }
    public string Category { get; set; } = "";
    public DateTime CrawlTime { get; set; }
}

public class CrawlResult
{
    public DateTime CrawlTime { get; set; }
    public string Source { get; set; } = "";
    public List<PolicyInfo> Policies { get; set; } = new();
    public List<NoticeInfo> Notices { get; set; } = new();
    public List<NewsInfo> News { get; set; } = new();
}
