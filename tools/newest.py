import json,sys
d=json.loads(open(sys.argv[1]).read())
e=d["entries"] if isinstance(d,dict) else json.loads(d[0]["text"])["entries"]
for x in sorted([x for x in e if x.get("mtimeMs")],key=lambda x:-x["mtimeMs"])[:int(sys.argv[2]) if len(sys.argv)>2 else 6]: print(x["name"],x["size"],x["mtimeMs"])
