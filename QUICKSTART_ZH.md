# IntentWeave 中文快速开始

## 1. 准备数据

把官方 `catalog.jsonl` 放到：

```text
data/catalog.jsonl
```

不要把 catalog 提交到 GitHub。

## 2. 运行测试

```powershell
python -m unittest discover -v
```

应看到 7 个测试全部通过。

## 3. 复现官方公开集分数

```powershell
python -m evaluator.local_evaluator --output results.json
```

开发机记录结果：

- Hit Rate@10：0.950
- MRR：0.673812
- MTTC：2.780
- TechnicalScore：0.841544

不同机器的运行时间可能不同，但结果应保持确定性。

## 4. 演示一条多轮对话

```powershell
python -m scripts.trace_session public_0001
```

演示讲稿位于 `docs/DEMO_SCRIPT.md`。

## 5. 提交

完整仓库上传到公开 GitHub。Devpost 英文介绍可直接使用
`docs/DEVPOST_DESCRIPTION.md`。独立 Agent bundle 位于 `submission/`。

你仍需亲自完成的部分只有：填写团队信息、录制并上传公开视频、粘贴
GitHub 与 YouTube 链接。详见 `docs/SUBMISSION_CHECKLIST.md`。
