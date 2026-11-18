"""Use the packaged DOCX rasterizer with a native Word PDF conversion on Windows."""
from pathlib import Path
import importlib.util, shutil, os, json
ROOT=Path(__file__).resolve().parent
RUNTIME=Path(r'C:\Users\T14s Gen 3\.cache\codex-runtimes\codex-primary-runtime\dependencies')
os.environ['PATH']=str(RUNTIME/'native/poppler/Library/bin')+os.pathsep+os.environ.get('PATH','')
script=Path(r'C:\Users\T14s Gen 3\.codex\plugins\cache\openai-primary-runtime\documents\26.1117.11355\skills\documents\render_docx.py')
spec=importlib.util.spec_from_file_location('packaged_docx_renderer',script)
renderer=importlib.util.module_from_spec(spec); spec.loader.exec_module(renderer)
def native_pdf(doc_path,user_profile,convert_tmp_dir,stem,verbose=False):
    path=Path(convert_tmp_dir)/(stem+'.pdf')
    shutil.copy2(ROOT/'rendered/report.pdf',path)
    return str(path),'Converted by Microsoft Word native ExportAsFixedFormat on Windows; see word_render_info.json.'
renderer.convert_to_pdf=native_pdf
pages=renderer.rasterize(str(ROOT/'report.docx'),str(ROOT/'rendered'),150,False,False)
(ROOT/'evidence/rendered_pages.json').write_text(json.dumps(list(pages),indent=2),encoding='utf-8')
print('Rendered',len(pages),'pages')
