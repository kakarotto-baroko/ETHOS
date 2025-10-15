# EtherionOS — 干净可部署包（v2）

- 前端：`index.html + assets/*`（本地 UMD，占位，可替换官方文件）
- 数据：从仓库根 `/output/*.json` 读取
- 缓存：根目录 `_headers` 禁止缓存 `/output/*`
- 工作流：`.github/workflows/` 提供 `daily / tplus3 / weekly` 三个仅数据的定时任务（**只提交 output/**）

## 部署 Cloudflare Pages（连接 Git）
1. 新建仓库并把本包所有文件上传到根目录。
2. Cloudflare → Pages → Connect to Git → 选此仓库。
   - Framework preset: None
   - Build command: *(空)*
   - Output directory: *(空)*（表示根目录）
3. 首次访问 `https://<your>.pages.dev` 即可看到导航骨架；JSON 来自 `/output/*.json`。

## 注意
- 先用占位 libs 跑通流程，之后可把 `assets/lib/*.js` 替换为官方 UMD。
- 真正的计算差异（daily / tplus3 / weekly）放在 `backend/main.py` 里按 cadence 分支实现。
