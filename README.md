# 项目说明

这是一个自动化生成 sing-box 规则集的项目，用于代理分流和广告屏蔽。生成以下规则集：

- `ads.json` / `ads.srs`（广告域名，包含 `httpdns-cn`）
- `geoip-cn.json` / `geoip-cn.srs`（中国大陆 IP 段）
- `geolocation-cn.json` / `geolocation-cn.srs`（地理定位中国常见域名）
- `geolocation-!cn.json` / `geolocation-!cn.srs`（地理定位非中国常见域名）
- `geosite-cn.json` / `geosite-cn.srs` （中国大陆常见域名，包含 `geolocation-cn`）
- `httpdns-cn.json` / `httpdns-cn.srs`（中国大陆常见 HTTPDNS）
- `porn.json` / `porn.srs` （色情域名）

## 🚀 使用说明

在 sing-box 配置文件中，参考如下示例即可使用本项目规则集。

```json
{
  "dns": {
    "servers": [
      {
        "type": "https",
        "tag": "cloudflare",
        "detour": "proxy",
        "domain_resolver": "hosts",
        "server": "dns.cloudflare.com"
      },
      {
        "type": "https",
        "tag": "alidns",
        "detour": "direct",
        "domain_resolver": "hosts",
        "server": "dns.alidns.com"
      },
      {
        "type": "hosts",
        "tag": "hosts",
        "predefined": {
          "dns.cloudflare.com": [
            "1.1.1.1",
            "1.0.0.1",
            "2606:4700:4700::1111",
            "2606:4700:4700::1001"
          ],
          "dns.alidns.com": [
            "223.5.5.5",
            "223.6.6.6",
            "2400:3200::1",
            "2400:3200:baba::1"
          ]
        }
      }
    ],
    "rules": [
      {
        "preferred_by": "hosts",
        "server": "hosts"
      },
      {
        "rule_set": "ads",
        "action": "predefined",
        "rcode": "NXDOMAIN"
      },
      {
        "rule_set": "geosite-cn",
        "server": "alidns"
      },
      {
        "action": "evaluate",
        "server": "cloudflare"
      },
      {
        "match_response": true,
        "rule_set": "geoip-cn",
        "server": "alidns"
      }
    ]
  },
  "outbounds": [
    {
      "type": "vless",
      "tag": "proxy"
    },
    {
      "type": "direct",
      "tag": "direct"
    }
  ],
  "route": {
    "rules": [
      {
        "rule_set": [
          "ads",
          "porn"
        ],
        "action": "reject",
        "method": "drop"
      },
      {
        "rule_set": "geolocation-!cn",
        "outbound": "proxy"
      },
      {
        "rule_set": [
          "geoip-cn",
          "geosite-cn"
        ],
        "outbound": "direct"
      }
    ],
    "rule_set": [
      {
        "type": "remote",
        "tag": [
          "ads",
          "geoip-cn",
          "geolocation-!cn",
          "geosite-cn",
          "porn"
        ],
        "url": "https://raw.githubusercontent.com/Moiudev/rule-set/main/{tag}.srs",
        "update_interval": "2h0m0s"
      }
    ]
  }
}
```

## 📚 规则源致谢

感谢以下开源项目和作者的辛勤劳动和持续更新，他们的规则源是本项目的基础，正是他们的努力让网络环境更加清洁。请访问原仓库支持作者！

| **名称**                       | **许可**                               | **链接**                                                                            |
| ------------------------------ | -------------------------------------- | ----------------------------------------------------------------------------------- |
| AdGuardFilters                 | GPL-3.0                                | [AdguardTeam/AdGuardFilters](https://github.com/AdguardTeam/AdGuardFilters)         |
| AdguardSDNSFilter              | GPL-3.0                                | [AdguardTeam/AdguardSDNSFilter](https://github.com/AdguardTeam/AdguardSDNSFilter)   |
| badmojr 1Hosts                 | MPL-2.0                                | [badmojr/1Hosts](https://github.com/badmojr/1Hosts)                                 |
| blackmatrix7 ios_rule_script   | GPL-2.0                                | [blackmatrix7/ios_rule_script](https://github.com/blackmatrix7/ios_rule_script)     |
| damengzhu banad                |                                        | [damengzhu/banad](https://github.com/damengzhu/banad)                               |
| Dan Pollock Hosts              |                                        | [someonewhocares.org/hosts](https://someonewhocares.org/hosts)                      |
| felixonmars dnsmasq-china-list | WTFPL                                  | [felixonmars/dnsmasq-china-list](https://github.com/felixonmars/dnsmasq-china-list) |
| gaoyifan China-Operator-IP     | MIT                                    | [gaoyifan/china-operator-ip](https://github.com/gaoyifan/china-operator-ip)         |
| hagezi dns-blocklists          | GPL-3.0                                | [hagezi/dns-blocklists](https://github.com/hagezi/dns-blocklists)                   |
| pgl.yoyo.org                   | [MCRAE](https://pgl.yoyo.org/license/) | [pgl.yoyo.org](https://pgl.yoyo.org/as/index.php)                                   |
| Phishing Army                  | CC-BY-NC-4.0                           | [phishing.army](https://phishing.army/)                                             |
| sjhgvr oisd                    | GPL-3.0                                | [sjhgvr/oisd](https://github.com/sjhgvr/oisd)                                       |
| StevenBlack Hosts              | MIT                                    | [StevenBlack/hosts](https://github.com/StevenBlack/hosts)                           |
| TG-Twilight AWAvenue-Ads-Rule  | GPL-3.0                                | [TG-Twilight/AWAvenue-Ads-Rule](https://github.com/TG-Twilight/AWAvenue-Ads-Rule)   |
| v2fly domain-list-community    | MIT                                    | [v2fly/domain-list-community](https://github.com/v2fly/domain-list-community)       |

***\* 对于未明示许可的源，请自行阅读其仓库说明以确认使用条款。***

## 📝 免责声明

- 本项目仅供个人学习和使用，不保证规则 100% 准确，可能导致误屏蔽或漏屏蔽。
- 用户需自行测试并承担风险，包括但不限于网络连接问题、数据隐私风险。
- 项目不提供任何担保，规则源可能随时变更，请定期更新。
- 违反源项目许可使用可能导致法律问题，请遵守原作者条款。

欢迎自由复制、分发、修改和使用本项目，但请保留源致谢，以尊重原作者劳动。祝网络畅通、远离广告！
