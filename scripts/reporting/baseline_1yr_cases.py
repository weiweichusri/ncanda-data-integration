#!/usr/bin/env python
##
##  Copyright 2015 SRI International
##  License: https://ncanda.sri.com/software-license.txt
##
"""
Report: Baseline and Year 1 Cases with Scans
============================================
Creates a csv files containing all cases that are included in the study, hanve
not missed their 1 year followup, and have a scanning session that was not
marked as missing

Usage:
python baseline_1yr_cases.py
"""
import os
import sys

import redcap

def get_project():
    # First REDCap connection for the Summary project (this is where we put data)
    summary_key_file = open(os.path.join(os.path.expanduser("~"),
                                         '.server_config/redcap-dataentry-token' ),
                                          'r')
    summary_api_key = summary_key_file.read().strip()
    rc_summary = redcap.Project('https://ncanda.sri.com/redcap/api/',
                                summary_api_key,
                                verify_ssl=False)

    # Get all the mri session reports for baseline and 1r
    mri  = rc_summary.export_records(fields=['study_id', 'exclude',
                                             'visit_ignore___yes', 'mri_missing'],
                                     forms=['mr_session_report', 'visit_date',
                                            'demographics'],
                                     events=['baseline_visit_arm_1',
                                             '1y_visit_arm_1'],
                                     format='df')
    return mri

def filter_dataframe(dataframe):
    # Create filters for cases that are included
    case_included = dataframe.exclude != 1 # baseline has 'exclude' in demographics
    visit_included = dataframe.visit_ignore___yes != 1 # Not consistent with 'exclude'
    mri_collected = dataframe.mri_missing != 1

    # Apply filters for results
    included = dataframe[case_included]
    results = included[visit_included & mri_collected]
    return results

def main(args=None):
    if args.verbose:
        print("Connecting to REDCap...")
    project = get_project()
    if args.verbose:
        print("Filtering dataframe...")
    results = filter_dataframe(project)
    if args.verbose:
        print("Writing results to {}...".format(args.outfile))
    # Write out results
    results.to_csv('baseline_1yr_cases.csv',
                   columns=['mri_xnat_sid', 'mri_xnat_eids'])

if __name__ == '__main__':
    import argparse

    formatter = argparse.RawDescriptionHelpFormatter
    default = 'default: %(default)s'
    parser = argparse.ArgumentParser(prog="baseline_1yr_cases.py",
                                     description=__doc__,
                                     formatter_class=formatter)
    parser.add_argument('-o', '--outfile', dest="outfile",
                        help="File to write out. {}".format(default),
                        default='baseline_1yr_cases.csv')
    parser.add_argument('-v', '--verbose', dest="verbose",
                        help="Turn on verbose", action='store_true')
    argv = parser.parse_args()
    sys.exit(main(args=argv))