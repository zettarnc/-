"""Course-specific source crop selection; inspect images before approving reviews."""
import csv
import hashlib
import json
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parent
SELECTIONS=[
 ('context',6,'上下文组成与条件生成','### “安全命令”为什么不能只靠一句话判断','课堂列出系统、项目、技能、工具与历史材料，并区分内容与指令。'),
 ('safety',26,'模型、外围系统与操作系统的分工','## 2. AI 降低的是开始行动的门槛','用于说明课堂如何拆分执行机制，不作为当前所有产品版本行为的独立验证。'),
 ('learning',21,'用复述与追问暴露理解缺口','## 3. 怎样让模型知道什么才算完成','课堂把学习组织为选择概念、自己解释、暴露缺口与查证重讲的循环。'),
 ('completion',51,'明确要求与显式失败','### 让旁观者也能判断是否完成','画面强调默认选择与失败状态；正文将其整理为可检查的完成标准。'),
 ('depth',71,'利用上下文和 token 延展推理','### 约束写作题把验收拆给我们看','草稿纸与复杂性问题仅用于建立直觉，不是计算能力的形式证明。'),
 ('verifier',91,'形式验证与质量评价的边界','## 5. 为什么规则越写越多，反而可能更难执行','课堂区分检查器看得到的形式条件与没有覆盖的品味和表达质量。'),
 ('attention',106,'规则副作用与按需加载','## 6. “你是一位审稿人”，为什么仍然不够','否定要求可能进入产物；长期约定、任务细节和程序检查需要分层。'),
 ('review',141,'三条独立的审稿路线','### Skill 应保存什么','课堂分别从判据、证据和反方视角安排审查，强调独立判断后再汇总。'),
 ('skills',151,'把成功方法沉淀为 Skill','## 7. 代码库为什么本身也是上下文','保存可复用的搜索策略和判断标准；技能本身同样有指令复杂度。'),
 ('codebase',156,'代码库的上下文与自由度','## 8. 长程编程与长程研究缺少的是同一种反馈吗','文件多不等于当前任务选择多；课堂把大系统与空项目作对比，结论带有适用条件。'),
 ('research',176,'研究失败与反馈分辨率','## 9. 人应该在哪些地方投入注意力','课件列出反馈与目标方面的候选解释；视频中讲师另回顾了任务表述导致的偏向，以及回到真实工具和搜索路径的纠正。'),
 ('human',181,'少干预与整体吞吐量','## 10. 怎样把更多算力变成更多有效探索','课堂区分单任务耗时与全天任务总量，并讨论应该审查哪些边界。'),
 ('exploration',191,'用多样化候选扩大探索','## 小结与练习','取名字是探索案例；先组织方向差异，再用实际偏好、出处和谐音筛选。'),
 ('future',196,'算力集中与未来可能性','## 小结与练习','结尾的墙内外图像表达未来担忧，本讲义不把它当作已经验证的预测。'),
]

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def clock(t):return f'{int(t)//60:02}:{int(t)%60:02}'

def prepare():
 work=ROOT/'work/nju-gse-02'; evidence=ROOT/'evidence/nju-gse-02'; evidence.mkdir(parents=True,exist_ok=True)
 notes=ROOT/'notes/prompt-context-engineering.md';text=notes.read_text(encoding='utf8'); rows=[]
 for name,n,topic,anchor,description in SELECTIONS:
  frame=work/f'frames/frame_{n:05}.jpg'; target=notes.parent/f'pce_{name}.jpg'; crop=[550,0,1280,410]
  if name=='research':crop[3]=378
  if name=='future':crop[3]=280
  Image.open(frame).crop(tuple(crop)).save(target,quality=95)
  start=(n-1)*30;end=min(start+30,5905.536)
  row=dict(figure=target.name,frame=frame.name,start=start,end=end,topic=topic,crop=crop,
           sha256=sha(target),source_frame_sha256=sha(frame),visual_review='pending')
  rows.append(row)
  if target.name not in text:
   image=f'![{topic}]({target.name})\n\n画面证据：原视频 {clock(start)}–{clock(end)}，[回看课堂片段](https://www.bilibili.com/video/BV1CQt365EzW/?t={start})。{description}\n\n'
   assert anchor in text,anchor
   text=text.replace(anchor,image+anchor,1)
 notes.write_text(text,encoding='utf8')
 (evidence/'figures.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
 with (evidence/'figure_manifest.tsv').open('w',encoding='utf8',newline='') as f:
  w=csv.writer(f,delimiter='\t');w.writerow(['figure','frame','start','end','topic','crop'])
  for r in rows:w.writerow([r[k] for k in ['figure','frame','start','end','topic','crop']])
 print(f'Prepared {len(rows)} crops; reviews remain pending until inspected.')

if __name__=='__main__':prepare()
