import os
import tqdm
import logging
from indra.sources.eidos import cli
from indra.literature.adeft_tools import universal_extract_text
from indra_db.util.content_scripts import TextContentSessionHandler


HERE = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(HERE, os.pardir, 'data')
TEXT_PATH = os.path.join(DATA_PATH, 'text')
OUTPUT_PATH = os.path.join(DATA_PATH, 'eidos_output')
PMIDS_FILE = os.path.join(DATA_PATH, 'brain_pmids_sample_200.csv')

logger = logging.getLogger('brain.eidos')


def get_text_for_pmid(pmid):
    content = tc.get_text_content_from_text_refs({'PMID': pmid})
    if not content:
        return None
    text = universal_extract_text(content)
    if not text:
        return None
    return text


def get_stash_text(pmid):
    fname = os.path.join(TEXT_PATH, f'{pmid}.txt')
    if os.path.exists(fname):
        with open(fname, 'r') as fh:
            return fh.read()
    text = get_text_for_pmid(pmid)
    if text:
        with open(fname, 'w') as fh:
            fh.write(text)
        return text
    return None


def get_pmids(fname):
    with open(fname, 'r') as fh:
        return [l.strip() for l in fh.readlines()]


if __name__ == '__main__':
    tc = TextContentSessionHandler()
    pmids = get_pmids(PMIDS_FILE)
    for pmid in tqdm.tqdm(pmids):
        get_stash_text(pmid)

    cli.extract_from_directory(TEXT_PATH, OUTPUT_PATH)