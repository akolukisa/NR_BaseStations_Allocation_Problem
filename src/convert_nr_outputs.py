import re
import csv
import sys

def parse_demo_txt(path):
    flows = []
    with open(path, 'r') as f:
        cur = None
        for line in f:
            m = re.match(r"Flow\s+(\d+) ", line)
            if m:
                cur = {"id": int(m.group(1))}
                flows.append(cur)
                continue
            if "Throughput:" in line and cur is not None:
                x = float(re.search(r"Throughput:\s+([0-9\.]+)\s+Mbps", line).group(1))
                cur["thr_mbps"] = x
            if "Mean delay:" in line and cur is not None:
                x = float(re.search(r"Mean delay:\s+([0-9\.]+)\s+ms", line).group(1))
                cur["delay_ms"] = x
            if "Mean jitter:" in line and cur is not None:
                x = float(re.search(r"Mean jitter:\s+([0-9\.]+)\s+ms", line).group(1))
                cur["jitter_ms"] = x
    return flows

def main():
    src = sys.argv[1]
    dst = sys.argv[2]
    flows = parse_demo_txt(src)
    with open(dst, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(["flow_id","throughput_mbps","delay_ms","jitter_ms"])
        for fl in flows:
            w.writerow([fl.get("id",0), fl.get("thr_mbps",0.0), fl.get("delay_ms",0.0), fl.get("jitter_ms",0.0)])

if __name__ == '__main__':
    main()
