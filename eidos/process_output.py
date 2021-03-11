import os
import glob
import json
import tqdm
import pickle
import functools
from indra.sources import eidos
from read_pmids import OUTPUT_PATH
from indra.tools import assemble_corpus as ac
from indra.assemblers.html import HtmlAssembler


def fix_provenance(stmts, pmid):
    for stmt in stmts:
        for ev in stmt.evidence:
            ev.pmid = pmid
            ev.text_refs['PMID'] = pmid


def process_file(fname, grounder):
    pmid = os.path.splitext(os.path.basename(fname))[0]
    with open(fname, 'r') as fh:
        jd = json.load(fh)
    ep = eidos.process_json_bio(json_dict=jd, grounder=grounder)
    stmts = ep.statements
    fix_provenance(stmts, pmid)
    return stmts


def get_custom_grounder():
    from gilda.grounder import Grounder
    from gilda.grounder import load_terms_file
    from gilda.resources import get_grounding_terms
    from gilda.generate_terms import terms_from_obo_url
    conso_terms = terms_from_obo_url(
        'https://raw.githubusercontent.com/pharmacome/conso/master/export/'
        'conso.obo',
        prefix='conso')
    terms = load_terms_file(get_grounding_terms())
    for term in conso_terms:
        try:
            terms[term.norm_text].append(term)
        except KeyError:
            terms[term.norm_text] = [term]
    gr = Grounder(terms)
    return functools.partial(grounder_wrapper,
                             grounder=gr)


def grounder_wrapper(text, context, grounder):
    matches = grounder.ground(text, context)
    if not matches:
        return {}
    else:
        return {matches[0].term.db: matches[0].term.id}


if __name__ == '__main__':
    version = 'v1'
    output_fname = os.path.join(OUTPUT_PATH, f'eidos_{version}.pkl')
    fnames = glob.glob(os.path.join(OUTPUT_PATH, '*.jsonld'))
    all_stmts = []
    grounder = get_custom_grounder()
    for fname in tqdm.tqdm(fnames):
        stmts = process_file(fname, grounder=grounder)
        all_stmts += stmts

    stmts = ac.map_grounding(all_stmts)
    stmts = ac.run_preassembly(stmts)

    with open(output_fname, 'wb') as fh:
        pickle.dump(stmts, fh)

    ha = HtmlAssembler(stmts)
    ha.save_model(os.path.join(OUTPUT_PATH, f'eidos_{version}.html'))
