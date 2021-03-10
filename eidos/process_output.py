import os
import glob
import json
import tqdm
import pickle
from indra.sources import eidos
from read_pmids import OUTPUT_PATH
from indra.assemblers.html import HtmlAssembler


def fix_provenance(stmts, pmid):
    for stmt in stmts:
        for ev in stmt.evidence:
            ev.pmid = pmid
            ev.text_refs['PMID'] = pmid


def process_file(fname):
    pmid = os.path.splitext(os.path.basename(fname))[0]
    with open(fname, 'r') as fh:
        jd = json.load(fh)
    ep = eidos.process_json_bio(json_dict=jd)
    stmts = ep.statements
    fix_provenance(stmts, pmid)
    return stmts


if __name__ == '__main__':
    version = 'v1'
    output_fname = os.path.join(OUTPUT_PATH, f'eidos_{version}.pkl')
    fnames = glob.glob(os.path.join(OUTPUT_PATH, '*.jsonld'))
    all_stmts = []
    for fname in tqdm.tqdm(fnames):
        stmts = process_file(fname)
        all_stmts += stmts
    with open(output_fname, 'wb') as fh:
        pickle.dump(all_stmts, fh)

    ha = HtmlAssembler(all_stmts)
    ha.save_model(os.path.join(OUTPUT_PATH, f'eidos_{version}.html'))