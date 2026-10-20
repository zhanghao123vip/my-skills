"""Return local image + original text paths by exact group alias or image number."""
from pathlib import Path
import argparse,json,hashlib,sys
BASE=Path(__file__).resolve().parent
def package_dir(pid):
 # 仓库布局：archives/<id>；旧版平铺安装：与本Skill同级的 <id>
 for p in (BASE/'archives'/pid,BASE.parent/pid):
  if (p/'manifest.json').is_file():return p
 raise FileNotFoundError(f'找不到资料包 {pid}：请放在 {BASE/"archives"} 下。')
def retrieve(name=None,number=None):
 catalog=json.loads((BASE/'catalog.json').read_text(encoding='utf-8'))
 if number is not None:matches=[c for c in catalog if number in c['image_numbers']]
 else:
  q=(name or '').strip()
  if q.startswith('调用'):q=q[2:].strip()
  matches=[c for c in catalog if q in c['aliases'] or q==c['id']]
 if len(matches)!=1:raise ValueError('名称未收录或不唯一；请使用catalog.json的完整名称或已收录图片编号。')
 c=matches[0];p=package_dir(c['id']);m=json.loads((p/'manifest.json').read_text(encoding='utf-8'));items=[]
 for i in m['items']:
  if number is not None and i['image_number']!=number:continue
  im=p/i['image_file'];doc=p/i['source_document']
  if not im.is_file():raise FileNotFoundError(f'图片未随仓库发布，请把原图放到 {im}（文件名见manifest.json）。')
  if hashlib.sha256(im.read_bytes()).hexdigest()!=i['image_sha256']:raise ValueError('图片文件哈希不符')
  expected=next(d['sha256'] for d in m['documents'] if d['file']==i['source_document'])
  if hashlib.sha256(doc.read_bytes()).hexdigest()!=expected:raise ValueError('原文文件哈希不符')
  items.append({'编号':i['image_number'],'图片':str(im),'完整原文':str(doc),'对应范围':i['association_scope'],'关联级别':i['association_level']})
 return {'名称':c['name'],'取用成功':bool(items),'图文':items,'提示':'这是本地图文取用；全局Skill文件已安装；本次仅取用图文，没有执行出图。'}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--name');ap.add_argument('--image',type=int);args=ap.parse_args()
 try:print(json.dumps(retrieve(args.name,args.image),ensure_ascii=False,indent=2))
 except (ValueError,FileNotFoundError) as e:print(str(e),file=sys.stderr);sys.exit(1)
