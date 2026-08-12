from pathlib import Path
import argparse, zipfile
from svdf import analyze_paper, ea_questions
from plots import frontier_plot, robustness_plot

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--output-dir',default='outputs')
    ap.add_argument('--draws',type=int,default=2000)
    args=ap.parse_args()
    out=Path(args.output_dir); out.mkdir(parents=True,exist_ok=True)
    r=analyze_paper(n_draws=args.draws)
    r.to_csv(out/'svdf_results.csv',index=False)
    frontier_plot(r,out/'figure_frontier.png')
    robustness_plot(r,out/'figure_robustness.png')
    ea_questions().to_csv(out/'ea_organisational_questions.csv',index=False)
    front=r[r.frontier].sort_values(['implementation_complexity','shared_value_gain'],ascending=[True,False])
    (out/'summary.txt').write_text(
        f'Projects/events: {len(r)}\nFrontier: {int(r.frontier.sum())}\nFrontier IDs: {", ".join(front.project_id.astype(str))}\n',encoding='utf-8')
    print((out/'summary.txt').read_text(),end='')

if __name__=='__main__': main()
