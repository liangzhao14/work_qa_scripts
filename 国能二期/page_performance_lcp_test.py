from playwright.sync_api import sync_playwright
import statistics
import time

# URL = "https://cloud-skgs-ilink.chnenergy.com.cn/" # 主页
# URL = "https://cloud-skgs-ilink.chnenergy.com.cn/aicc-data-process/#/modelcompression?zone=default&activeRule=%2Faicc-bml" # 量化
URL = "https://cloud-skgs-ilink.chnenergy.com.cn/aicc-console/#/operate/analysis/index?activeRule=%2Faicc-console" # 监控
TEST_TIMES = 3
TIMEOUT = 60000
SLA_MS = 2000   # 2 秒


def collect_metrics(page):
    return page.evaluate("""
    () => {
        return new Promise(resolve => {
            let lcp = null;

            if ('PerformanceObserver' in window) {
                try {
                    new PerformanceObserver((entryList) => {
                        const entries = entryList.getEntries();
                        const last = entries[entries.length - 1];
                        lcp = Math.round(last.startTime);
                    }).observe({ type: 'largest-contentful-paint', buffered: true });
                } catch (e) {}
            }

            requestAnimationFrame(() => {
                requestAnimationFrame(() => {
                    const nav = performance.getEntriesByType('navigation')[0];
                    resolve({
                        dns_ms: Math.round(nav.domainLookupEnd - nav.domainLookupStart),
                        tcp_ms: Math.round(nav.connectEnd - nav.connectStart),
                        ttfb_ms: Math.round(nav.responseStart - nav.requestStart),
                        dom_content_loaded_ms:
                            Math.round(nav.domContentLoadedEventEnd),
                        load_ms: Math.round(nav.loadEventEnd),
                        lcp_ms: lcp
                    });
                });
            });
        });
    }
    """)


def test_once(context, url):
    page = context.new_page()
    page.goto(url, timeout=TIMEOUT, wait_until="networkidle")
    metrics = collect_metrics(page)
    page.close()
    return metrics


def summarize(results):
    summary = {}
    for key in results[0]:
        values = [v[key] for v in results if v[key] is not None]
        if not values:
            summary[key] = None
        else:
            summary[key] = {
                "avg": round(statistics.mean(values), 2),
                "min": min(values),
                "max": max(values)
            }
    return summary


def format_ms(ms):
    if ms is None:
        return "N/A"
    return f"{ms} ms ({round(ms / 1000, 2)} s)"


def sla_status(ms):
    if ms is None:
        return "N/A"
    return "✅ PASS" if ms <= SLA_MS else "❌ FAIL"


def run_for_browser(playwright, browser_type, name):
    print(f"\n▶ Testing {name}")
    browser = browser_type.launch(headless=True)
    context = browser.new_context()

    results = []
    for i in range(TEST_TIMES):
        print(f"  Run {i + 1}/{TEST_TIMES}")
        results.append(test_once(context, URL))
        time.sleep(1)

    context.close()
    browser.close()
    return summarize(results)


def main():
    with sync_playwright() as p:
        all_results = {
            "Chromium": run_for_browser(p, p.chromium, "Chromium"),
            "Firefox": run_for_browser(p, p.firefox, "Firefox"),
            "WebKit": run_for_browser(p, p.webkit, "WebKit"),
        }

    print("\n✅ Performance Test Result")
    print("SLA: 页面响应时间（Load） ≤ 2s\n")

    for browser, metrics in all_results.items():
        print(f"[{browser}]")
        for k, v in metrics.items():
            if v is None:
                print(f"{k:25s} N/A")
            else:
                line = (
                    f"{k:25s} "
                    f"avg={format_ms(v['avg'])} "
                    f"min={format_ms(v['min'])} "
                    f"max={format_ms(v['max'])}"
                )

                if k == "load_ms":
                    line += f"  => {sla_status(v['avg'])}"

                print(line)
        print()


if __name__ == "__main__":
    main()
