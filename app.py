"""Local Gradio application for SVDF."""
from pathlib import Path
import tempfile, zipfile
import pandas as pd
import gradio as gr
from svdf import analyze_paper, specification_robustness, ea_questions, load_remote_api
from plots import frontier_plot, robustness_plot

def _bundle(results,work):
    work=Path(work); csv=work/'svdf_results.csv'; results.to_csv(csv,index=False)
    f1=frontier_plot(results,work/'figure_frontier.png'); f2=robustness_plot(results,work/'figure_robustness.png')
    ea=work/'ea_organisational_questions.csv'; ea_questions().to_csv(ea,index=False)
    out=work/'svdf_results_bundle.zip'
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
        for f in [csv,f1,f2,ea]: z.write(f,arcname=f.name)
    return str(out),str(f1),str(f2)

def _format(r,label):
    work=Path(tempfile.mkdtemp(prefix='svdf_')); bundle,f1,f2=_bundle(r,work)
    front=r[r.frontier].sort_values(['implementation_complexity','shared_value_gain'],ascending=[True,False])
    summary=(f"### {label}\n**Projects:** {len(r)}  \n**Non-dominated frontier:** {int(r.frontier.sum())}  \n"
             f"**Frontier IDs:** {', '.join(front.project_id.astype(str))}")
    cols=[c for c in ['project_id','event_type','adjusted_change_pct','annualized_kwh_saved','shared_value_gain','implementation_complexity','frontier_frequency','frontier'] if c in r]
    return summary,r[cols].sort_values(['frontier','shared_value_gain'],ascending=[False,False]),f1,f2,bundle

def reproduce_paper(): return _format(analyze_paper(n_draws=2000),'Paper reproduction complete')
def analyze_upload(file):
    if file is None: raise gr.Error('Upload a CSV using the schema in README.md.')
    return _format(specification_robustness(pd.read_csv(file),1000),'Portfolio analysis complete')
def analyze_api(url):
    if not url: raise gr.Error('Enter a CSV/JSON API URL.')
    return _format(specification_robustness(load_remote_api(url),1000),'API portfolio analysis complete')

with gr.Blocks(title='Shared Value Decision Frontier') as demo:
    gr.Markdown('# Shared Value Decision Frontier (SVDF)\nA reproducible strategy-screening tool. Lower IC and higher SVG are preferred.')
    with gr.Tab('Reproduce paper'):
        gr.Markdown('Bundled processed UNICON data. No upload is required.')
        run=gr.Button('Reproduce Paper Analysis',variant='primary')
        s=gr.Markdown(); t=gr.Dataframe(interactive=False); p1=gr.Image(type='filepath',label='SVDF frontier'); p2=gr.Image(type='filepath',label='Robustness'); d=gr.File(label='Download results bundle')
        run.click(reproduce_paper,outputs=[s,t,p1,p2,d])
    with gr.Tab('Own CSV'):
        up=gr.File(file_types=['.csv'],type='filepath',label='Upload portfolio CSV'); go=gr.Button('Run SVDF',variant='primary')
        s2=gr.Markdown(); t2=gr.Dataframe(interactive=False); q1=gr.Image(type='filepath'); q2=gr.Image(type='filepath'); d2=gr.File()
        go.click(analyze_upload,inputs=[up],outputs=[s2,t2,q1,q2,d2])
    with gr.Tab('API source'):
        gr.Markdown('For private APIs set `SVDF_API_KEY` in the environment. The key is sent as a Bearer token and is never stored by the app.')
        url=gr.Textbox(label='CSV/JSON API URL'); api_go=gr.Button('Fetch API and Run SVDF',variant='primary')
        s3=gr.Markdown(); t3=gr.Dataframe(interactive=False); a1=gr.Image(type='filepath'); a2=gr.Image(type='filepath'); d3=gr.File()
        api_go.click(analyze_api,inputs=[url],outputs=[s3,t3,a1,a2,d3])

if __name__=='__main__': demo.launch(server_name='0.0.0.0')
