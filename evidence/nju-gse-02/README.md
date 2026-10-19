# 第二讲：视频来源与核验记录

原课程：蒋炎岩，南京大学《生成式软件工程》2026 年第 2 讲。[原视频《提示词工程》](https://www.bilibili.com/video/BV1CQt365EzW/)；[官方讲义《提示词与上下文工程》](https://jyywiki.cn/GSE/2026/lect2.md)。

本讲实际采集媒体约 5905.536 秒，每 30 秒提取候选帧，共 197 张；从中选择 14 张课堂画面，逐张核对裁剪内容与图注。章节按每 5 分钟窗口核对主题覆盖。

- `acquisition.json` 保存完整音视频的时长和 SHA-256，不包含下载器的临时媒体地址。
- `audio_raw.srt`、`transcript_indexed.txt` 是本地 SenseVoice 的完整原始识别结果，保留英文术语误识别等问题。每段时间为真实的 20 秒输入窗口，不能视为逐字对齐。
- `figures.json`、`figure_manifest.tsv` 保存原始候选帧、时间范围、裁剪坐标与图像哈希。
- `timeline_coverage.tsv`、`teaching_atoms.tsv` 与 `numerical_claims.tsv` 记录章节覆盖、关键知识点和数字主张的范围。
- `content_review.json` 和 `source-verification.json` 区分 Agent 审阅范围与程序完整性检查，绑定当前讲义和字幕的哈希。

核验不包含逐字原声听写、逐帧全检或全部演示复现。模型训练细节、课堂中的模型比较与未来判断，不作为已经独立验证的事实；研究失败的候选解释保持为候选解释。原视频、音轨、模型与大体积中间文件在生成核验完成后清理，成品与证据记录保留。

讲义及所引用的课程图片属于对原课程的重组与解释，相关改编内容按原课程 [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) 的署名、非商业使用和许可条件提供，不代表讲师或学校认可。
