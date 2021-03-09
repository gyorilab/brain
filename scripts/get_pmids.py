"""Get PMIDs for articles related to brain science."""

import random
from indra.literature import pubmed_client


if __name__ == '__main__':
    # MESH term for "Brain"
    mesh_id = 'D001921'
    sample_size = 200
    pmids = pubmed_client.get_ids_for_mesh(mesh_id, retmax=1300000)
    # Save all PMIDs to a file
    with open('brain_pmids.csv', 'wt') as f:
        for pmid in pmids:
            f.write(f'{pmid}\n')
    # Take a random sample of 200 articles 
    random.seed(1)
    samp_pmids = random.sample(pmids, sample_size)
    with open('brain_pmids_sample_200.csv', 'wt') as f:
        for pmid in samp_pmids:
            f.write(f'{pmid}\n')
    
