#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import os
import pathlib
import shutil
import signal
import subprocess  # nosec
import time
import urllib.request

SLS_PATH = shutil.which('sls')
PS_PATH = shutil.which('ps')
SERVICES = ('offline', 'dynamodb', 'elasticsearch')
ELASTIC_SEARCH_DIR = pathlib.Path.home().joinpath('sources/current')
ELASTIC_SEARCH_BIN = ELASTIC_SEARCH_DIR.joinpath('bin/elasticsearch')
ES_POST_SEED_FILE_PATH = 'seed/post.json'
ES_POST_INDEX_NAME = 'aws-serverless-skeleton-local-post_type'
ES_ENDPOINT = 'localhost:9200'


def _search_process_by_cmd_name(cmd_name):
    ps_proc = subprocess.Popen(  # nosec
        [PS_PATH, '-x'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proces_out = ps_proc.communicate()[0]
    proces_out_as_utf8 = proces_out.decode("utf8")
    proces_out_as_list = proces_out_as_utf8.split("\n")
    if ps_proc.returncode == 0:
        for line in proces_out_as_list:
            line_as_list = line.split()
            cmd = " ".join(line_as_list[3:])
            if cmd_name in cmd:
                return int(line_as_list[0])


def _start_process(process_args):
    proc = subprocess.Popen(  # nosec
        process_args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(1.5)
    return proc


def _start_dynamodb(extra_args):
    process_as_list = [SLS_PATH, 'dynamodb', 'start']
    process_as_list.extend(extra_args)
    ddb_process = _start_process(process_as_list)
    print("dynamodb started with command: {0} and pid: {1}".format(
        " ".join(process_as_list), ddb_process.pid))
    return ddb_process


def _read_proc_stdout(process_object):
    try:
        while process_object.poll() is None:
            line = process_object.stdout.readline()
            line_as_string = line.decode('utf-8')
            print(line_as_string.strip())
    except KeyboardInterrupt:
        # read the last bit in the buffer
        try:
            for line in process_object.stdout.read().decode('utf-8').split('\n'):
                print(line.strip())
        except KeyboardInterrupt:
            pass


def seed_elastic_search(seed_file_path, index_name):
    """I had to use std library so npm works everywhere"""
    current_file_location = pathlib.Path(__file__).resolve()
    root_directory = current_file_location.parents[1]
    abs_config_file_path = root_directory.joinpath(seed_file_path)
    content = json.loads(open(abs_config_file_path).read())[0]
    request_body = json.dumps(content)

    # check if index is already there, if not, create it:
    check_request = urllib.request.Request(
        url='http://localhost:9200/{0}'.format(index_name), method='HEAD')
    try:
        urllib.request.urlopen(check_request)  # nosec
    except urllib.error.HTTPError as requestException:
        if requestException.code == 404:
            urllib.request.Request(
                url='http://localhost:9200/{0}'.format(index_name), method='PUT')
    # insert data
    put_data_request = urllib.request.Request(
        url='http://localhost:9200/{0}/doc'.format(index_name), method='POST')
    response = urllib.request.urlopen(put_data_request, data=request_body.encode('utf-8'))  # nosec
    print("ElasticSearch data insertion ended with result {0}".format(response.code))


def start_dynamodb_with_seed():
    return _start_dynamodb(['--stage local', '--migrate', '--seed'])


def start_dynamodb_without_seed():
    return _start_dynamodb(['--stage local', '--migrate'])


def start_start_elasticsearch_with_seed():
    elasticsearch_proc = start_elasticsearch()
    if elasticsearch_proc is not None:
        # allow time for elasticsearch to get up and running
        time.sleep(15)
        seed_elastic_search(ES_POST_SEED_FILE_PATH, ES_POST_INDEX_NAME)
        return elasticsearch_proc


def start_sls_offline():
    process_as_list = [SLS_PATH, 'offline', '--noTimeout']
    sls_offline_process = _start_process(process_as_list)
    print("serverless offline started with command: {0} and pid: {1}".format(
        " ".join(process_as_list), sls_offline_process.pid))
    return sls_offline_process


def start_elasticsearch():
    process_as_list = [str(ELASTIC_SEARCH_BIN)]
    if pathlib.Path.is_symlink(ELASTIC_SEARCH_DIR):
        elasticsearch_proc = _start_process(process_as_list)
        print("elasticsearch started with command: {0} and pid: {1}".format(
            " ".join(process_as_list), elasticsearch_proc.pid))
        return elasticsearch_proc
    else:
        print("elasticsearch is not installed correctly")


def stop_dynamodb():
    pid_node_start = _search_process_by_cmd_name("dynamodb start")
    pid_ddb_java = _search_process_by_cmd_name("DynamoDBLocal_lib -jar DynamoDBLocal.jar")
    if not pid_ddb_java and not pid_node_start:
        print("dynamodb was not running")
    if pid_node_start:
        os.kill(pid_node_start, signal.SIGINT)
        print("node dynamodb with pid {0} has been stopped".format(pid_node_start))
    if pid_ddb_java:
        os.kill(pid_ddb_java, signal.SIGINT)
        print("java dynamodb with pid {0} has been stopped".format(pid_ddb_java))
    return pid_ddb_java or pid_ddb_java


def stop_sls_offline():
    pid_sls_offline = _search_process_by_cmd_name("{0} offline".format(SLS_PATH))
    if pid_sls_offline:
        os.kill(pid_sls_offline, signal.SIGINT)
        print("serverless offline with pid {0} has been stopped".format(pid_sls_offline))
    else:
        print("serverless offline was not running")
    return pid_sls_offline


def stop_elasticsearch():
    pid_elasticsearch = _search_process_by_cmd_name("org.elasticsearch.bootstrap.Elasticsearch")
    if pid_elasticsearch:
        os.kill(pid_elasticsearch, signal.SIGINT)
        print("elasticsearch with pid {0} has been stopped".format(pid_elasticsearch))
    else:
        print("elasticsearch was not running")
    return pid_elasticsearch


def setup_praser():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--verbose', action='store_true', default=False,
        help='enable verbose option for offline'
    )

    subparsers = parser.add_subparsers(help='commands', dest='cmd')

    start_parser = subparsers.add_parser('start', help='start service')
    start_parser.add_argument(
        'start_service', choices=SERVICES,
        help='start specific service'
    )
    start_parser.add_argument(
        '--seed', action='store_true', default=False,
        help='enable seed option for dynamodb'
    )

    stop_parser = subparsers.add_parser('stop', help='stop service')
    stop_parser.add_argument(
        'stop_service', choices=SERVICES,
        help='stop specific service'
    )

    group = parser.add_mutually_exclusive_group()

    group.add_argument(
        '--start-all', action='store_true', default=False, dest='start_all_services',
        help='start all services: {0}'.format(SERVICES)
    )

    group.add_argument(
        '--stop-all', action='store_true', default=False, dest='stop_all_services',
        help='stop all services: {0}'.format(SERVICES)
    )

    return parser


if __name__ == '__main__':

    parser = setup_praser()
    results = parser.parse_args()

    if results.cmd == 'start':
        if results.start_service == 'offline':
            if results.verbose:
                _read_proc_stdout(start_sls_offline())
            else:
                start_sls_offline()
        elif results.start_service == 'elasticsearch':
            if results.seed:
                start_start_elasticsearch_with_seed()
            else:
                start_elasticsearch()
        elif results.start_service == 'dynamodb':
            if results.seed:
                start_dynamodb_with_seed()
            else:
                start_dynamodb_without_seed()

    elif results.cmd == 'stop':
        if results.stop_service == 'offline':
            stop_sls_offline()
        elif results.stop_service == 'elasticsearch':
            stop_elasticsearch()
        elif results.stop_service == 'dynamodb':
            stop_dynamodb()

    elif results.start_all_services:
        start_dynamodb_with_seed()
        start_start_elasticsearch_with_seed()
        if results.verbose:
            _read_proc_stdout(start_sls_offline())
        else:
            start_sls_offline()

    elif results.stop_all_services:
        stop_sls_offline()
        stop_dynamodb()
        stop_elasticsearch()

    else:
        parser.print_help()
