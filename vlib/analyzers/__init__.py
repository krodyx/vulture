import os, json, logging

from functools import partial

log = logging.getLogger()

from vlib.analyzers import exploitability, freshness, popularity
from vlib.analyzers.tools import call_for_each_bug

def store_analysis(summary, bug_cache_dir, analysis_dir, popularity_dict, bugdir):

    # mirror bug_cache_dir structure in analysis_dir
    dir_tail = bugdir[len(bug_cache_dir):]
    dir_tail = dir_tail.strip("/")
    out_dir = "%s/%s" % (analysis_dir, dir_tail)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    metadata = json.load(open("%s/vulture.json" % bugdir, "rt"))

    pop = popularity.get(metadata, popularity_dict)
    fresh = freshness.get(metadata)
    exp = exploitability.get(bugdir)
    # repro = ... TODO
    combined = {
            'popularity' : pop,
            'freshness' : fresh,
            'exploitability' : exp
            }

    # dump analysis for this bug 
    bug_id_str = bugdir.split("/")[-1]
    json.dump(combined, open("%s/analysis.json" % out_dir, "wt"), indent=4)

    # add this bug to summary
    metadata = json.load(open("%s/vulture.json" % bugdir, "rt"))

    bugrow = {}
    bugrow['id'] = bug_id_str
    bugrow['title'] = metadata['title']
    bugrow['web_link'] = metadata['web_link']
    bugrow['popcon_installs'] = pop['sum_inst']
    bugrow['date_modified'] = fresh['date_last_updated']
    bugrow['date_created'] = fresh['date_created']
    bugrow['status'] = fresh['best_status']
    bugrow['status_score'] = fresh['best_status_score']
    bugrow['exp_rank'] = exp.ranking[0] if exp else None
    summary.append(bugrow)

def analyze(bug_cache_dir, analysis_dir, popularity_cache_dir):
    '''
    This function should cache a JSON object corresponding to the
    data that will be used on index.html: bug_id, bug_title, <metric ranks>
    '''
    # gather/store analysis for each bug
    popularity_dict = json.load(open("%s/popularity.json" % popularity_cache_dir, "rt"))
    summary = []
    call_for_each_bug(bug_cache_dir, 
            partial(store_analysis, summary, bug_cache_dir, analysis_dir, popularity_dict))

    # store summary for all bugs 
    json.dump(summary, open("%s/summary.json" % analysis_dir, "wt"), indent=4)

    return summary

