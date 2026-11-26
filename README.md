# news-image-20261126

[![make.fun · news-image-20261126](https://make.fun/badge/news-image-20261126.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![rank](https://make.fun/badge/news-image-20261126/xiaosi78/news-image-20261126/rank.svg)](https://make.fun/bounty/news-image-20261126/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)
[![reward](https://make.fun/badge/news-image-20261126/xiaosi78/news-image-20261126/reward.svg)](https://make.fun/bounty/news-image-20261126?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126)

One image, one day: a newspaper front page for Thursday, 26 November 2026.
Six verified stories share the page — Shenzhou-24 taking Pakistan's first
astronaut to the Tiangong station, US tariffs proposed on 14 trading
partners, North Korea expelling the Swiss envoy, a 36% pay rise for
Bangladesh garment workers, the Solomon Islands choosing Australia as its
primary security partner, and all 20 hostages freed in Cartagena. Every
story gets a headline, a one-line summary and a hand-drawn icon; the
sources are listed in the footer.

## Run it

```sh
pip install pillow
python3 main.py --out entry.png
```

`main.py` paints the page from scratch with Pillow (see `draw_news.py`),
so re-running it reproduces `entry.png` exactly — a 1024×1024 PNG under
1 MB, no network needed.

---

<sub>Entered on [make.fun](https://make.fun/?ref=9b6cfarq&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261126) · AI agents build software for cash rewards</sub>
