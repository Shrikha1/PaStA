#!/usr/bin/env python3

import argparse
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from PaStA import *


def patch_stack_rating(evaluation_result, similar_patches, false_positives,
                       thresholds, resp_commit_date):
    evaluation_result.interactive_rating(similar_patches, false_positives,
                                         thresholds, resp_commit_date, upstream_rating=False)


def upstream_rating(evaluation_result, similar_patches, similar_upstream,
                    false_positives, thresholds, resp_commit_date):
    have_upstreams = set(map(lambda x: similar_patches.get_equivalence_id(x[0]), similar_upstream))

    # Prefilter Evaluation Result: Equivalence classes, that already have upstream candidates must be dropped.
    for key in list(evaluation_result.keys()):
        if similar_patches.get_equivalence_id(key) in have_upstreams:
            del evaluation_result[key]

    evaluation_result.interactive_rating(similar_upstream, false_positives,
                                         thresholds, resp_commit_date, upstream_rating=True)


def rate(prog, argv):
    parser = argparse.ArgumentParser(prog=prog, description='classify analysation results')

    parser.add_argument('-fp', dest='fp_filename', metavar='filename', default=config.false_positives,
                        help='False positive PKL filename')
    parser.add_argument('-sp', dest='sp_filename', metavar='filename', default=config.similar_patches,
                        help='Similar patches filename')
    parser.add_argument('-su', dest='su_filename', metavar='filename', default=config.similar_upstream,
                        help='Similar upstream filename')
    parser.add_argument('-er', dest='er_filename', metavar='filename', default=config.evaluation_result,
                        help='Evaluation result PKL filename')

    # Thresholds
    parser.add_argument('-ta', dest='thres_accept', metavar='threshold', type=float,
                        default=config.thresholds.autoaccept,
                        help='Autoaccept threshold (default: %(default)s)')
    parser.add_argument('-ti', dest='thres_interactive', metavar='threshold', type=float,
                        default=config.thresholds.interactive,
                        help='Interactive threshold (default: %(default)s)')
    parser.add_argument('-dlr', dest='thres_diff_lines', metavar='threshold',  type=float,
                        default=config.thresholds.diff_lines_ratio,
                        help='Diff lines ratio threshold (default: %(default)s)')
    parser.add_argument('-weight', dest='weight', metavar='weight', type=float,
                        default=config.thresholds.message_diff_weight,
                        help='Heuristic factor for message to diff rating. (default: %(default)s)')

    parser.add_argument('-rcd', dest='resp_commit_date', action='store_true', default=False,
                        help='Respect commit date')
    args = parser.parse_args(argv)

    config.thresholds = Thresholds(args.thres_accept,
                                   args.thres_interactive,
                                   args.thres_diff_lines,
                                   config.thresholds.heading,  # does not matter for interactive rating
                                   args.weight)

    # Load already known positives and false positives
    similar_patches = EquivalenceClass.from_file(args.sp_filename)
    similar_upstream = EquivalenceClass.from_file(args.su_filename)
    human_readable = not args.fp_filename.endswith('.pkl')
    false_positives = DictList.from_file(args.fp_filename, human_readable=human_readable)

    evaluation_result = EvaluationResult.from_file(args.er_filename)

    if evaluation_result.eval_type == EvaluationType.PatchStack:
        print('Running patch stack rating...')
        patch_stack_rating(evaluation_result, similar_patches, false_positives,
                           config.thresholds, args.resp_commit_date)
    elif evaluation_result.eval_type == EvaluationType.Upstream:
        print('Running upstream rating...')
        upstream_rating(evaluation_result, similar_patches, similar_upstream,
                        false_positives, config.thresholds, args.resp_commit_date)
    else:
        pass

    similar_upstream.to_file(args.su_filename)
    similar_patches.to_file(args.sp_filename)
    fp_filename = args.fp_filename
    if not human_readable:
        fp_filename = os.path.splitext(fp_filename)[0]
    false_positives.to_file(fp_filename)


if __name__ == '__main__':
    rate(sys.argv[0], sys.argv[1:])