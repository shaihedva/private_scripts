#!/usr/bin/python2.7
import argparse
import os , glob
import ntpath
import sys
import subprocess
import traceback
import shutil
#from python_pkg.xradc.utils import yaml_utils
import yaml
from collections import OrderedDict
#from python.outputs_modules.heat_module import HeatModule
#from xradc import logger
from sys import platform

def change_path_linux_windows(path):
    if platform == "linux" or platform == "linux2":
        path = path
    elif platform == "darwin":
        path = path
    elif platform == "win32":
        path = path.replace('/', '\\')
    return path

def parse_yaml_file(file_path):
    """
    The functions returns file as parsed YAML
    :param file_path: The YAML file path
    :return: parsed YAML
    """
    with open(file_path, 'r') as yf:
        parsed_yaml = yaml.load(yf)
    return parsed_yaml


def get_component_list_from_supreme(main_folder):
    #s_t = yaml_utils.parse_yaml_file(os.path.join(main_folder,  "SupremeTemplate", "SupremeTemplate.yaml"))
    s_t  = parse_yaml_file(change_path_linux_windows(os.path.join(main_folder,  "SupremeTemplate", "SupremeTemplate.yaml")))

    arr = {}
    for e in s_t['resources']:
        component_path = s_t['resources'][e]["type"]
        component_path = os.path.join(main_folder, '/'.join(component_path.split("/")[1:-1]))
        arr[e] = {}
        arr[e]['output_files'] = {}
        arr[e]['Launcher'] = os.path.join(component_path, e+"Launcher.yaml")
        arr[e]['Template'] = os.path.join(component_path, e + "Template.yaml")
        arr[e]['output_files']['template'] = []
        arr[e]['output_files']['environment'] = []
        #arr[e]['CloudConfig'] = os.path.join(component_path, e + "CloudConfig.yaml")


    return arr

def ordered_dump(data, stream=None, Dumper=yaml.Dumper, **kwds):
    Dumper.ignore_aliases = lambda self, data: True

    class OrderedDumper(Dumper):
        pass

    def _dict_representer(dumper, data):
        return dumper.represent_mapping(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            data.items())

    OrderedDumper.add_representer(OrderedDict, _dict_representer)
    return yaml.dump(data, stream, OrderedDumper, width=float('inf'), **kwds)


def remove_string(yaml_resource , remove_array):
    for k in yaml_resource.keys():
        if k.lower() in remove_array:
            try:
                del(yaml_resource[k])
            except KeyError:
                #import pdb;pdb.set_trace()
                print ("%s not exist in %s"%(s,yaml_resource.keys()))
                pass

def write_to_yaml_file_NO(file_path, parsed_yaml):
    """
    This function creates new yaml file
    :param file_path: The path to the yaml file
    :param parsed_yaml: the parsed yaml
    """

    with open(file_path, 'w') as yamlFile:
        try:
            noalias_dumper = yaml.dumper.SafeDumper
            noalias_dumper.ignore_aliases = lambda self, data: True
            yamlFile.write(yaml.dump(parsed_yaml, default_flow_style=False, Dumper=noalias_dumper))
        except yaml.YAMLError as exc:
            print(exc)


def write_to_yaml_file(file_path, parsed_yaml, *args):
    """
    This function writes a new YAML file
    input - The path to the yaml file, the parsed yaml
    """
    flow_style = None
    if 'cloudconfig' in args:
        flow_style = False

        with open(file_path, 'w') as yamlFile:
            yamlFile.write('#cloud-config\n')
            yamlFile.write(ordered_dump(parsed_yaml, default_flow_style=flow_style, Dumper=yaml.SafeDumper))
    else:
        if 'env' in args:
            flow_style = check_yaml_keys(parsed_yaml['parameters'])

        with open(file_path, 'w') as yamlFile:
            """
            use default_flow_style=False in yaml.dump to change array: [a, b, c] to
            array:
            - a
            - b
            - c
            And not one liner
            True - one liner
            None - [a, b, c] and one liner
            """
            yamlFile.write(ordered_dump(parsed_yaml, default_flow_style=flow_style, Dumper=yaml.SafeDumper))


def write_file(file_path, yaml_outout):
    #print "saving %s"%file_path
    path =  ntpath.dirname(file_path)
    if not os.path.exists(path):
        os.makedirs(path)
    write_to_yaml_file(file_path,yaml_outout)
    #with open(file_path, 'w') as yaml_file:
    #    yaml.dump(yaml_outout, yaml_file, default_flow_style=False)

def execute_command(command):
    try:
        child = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        streamdata = child.communicate()
        child.poll()
        rc = child.returncode
        if rc == 0:
            return streamdata[0]
        else:
            return False

    except OSError:
        return False
FE_COMPONENTS = [ 'vProve', 'vLB' , 'vLBAgent']

def main(script_args):
    """
    :param script_args:
    :return:
    """

    # Validate the scripts arguments.

    shutil.copytree(script_args.heat_templates_path, os.path.join(script_args.output_folder))
    component_list =  get_component_list_from_supreme(script_args.heat_templates_path+"/Supreme/OnboardingTemplates")

    for component in component_list.keys():
        print ("Working on %s"%component)
        convert(component_list[component]['Template'].replace(script_args.heat_templates_path,os.path.join(script_args.output_folder)),component,component_list)
        #import pdb;pdb.set_trace()
        files = glob.glob(os.path.join(script_args.output_folder,"Flat","BE","*_%s*.yaml"%component.lower()))
        #files = glob.glob(os.path.join(script_args.output_folder,"Flat","BE","*_%s*.env"%component.lower()))

        files.extend(glob.glob(os.path.join(script_args.output_folder, "Flat", "BE", "BE_base_module.yaml")))
        files.extend(glob.glob(os.path.join(script_args.output_folder, "Flat", "FE", "FE_base_module.yaml")))

        files.extend(glob.glob(os.path.join(script_args.output_folder, "Flat", "FE", "*_%s*.yaml" % component.lower())))
        files.extend(glob.glob(os.path.join(script_args.output_folder, "Flat", "FE", "*_%s*.env" % component.lower())))
        print "list of files %s"%files
        for yaml_template_file in files:
            #if not yaml_template_file.endswith("_volume.yaml"):
			print yaml_template_file
			convert(yaml_template_file,component,component_list)
        files = glob.glob(os.path.join(script_args.output_folder, "Flat", "FE", "*_%s[_].yaml" % component.lower()))

        baremetal_path = os.path.join(script_args.output_folder , "Supreme" , "OnboardingTemplates" , "%s_baremetal"%component.lower() , "%s_baremetalTemplate.yaml"%component.lower())
        if os.path.exists(baremetal_path):
            print "%s has baremetal"%component
            convert(baremetal_path , component , component_list)


def convert(curr_input_yaml_file,component,component_list):
    try:
        print "working on %s"%curr_input_yaml_file
        input_yaml = parse_yaml_file(curr_input_yaml_file)
        server_element = get_cloadconfig_filename(input_yaml)
        if server_element:
            params = server_element['properties']['user_data']['str_replace']['params']
            arr = []
            output_folder_path = ntpath.dirname(curr_input_yaml_file)
            #import pdb;pdb.set_trace()

        write_file(curr_input_yaml_file, input_yaml)
            #return cload_config_path
    except KeyError:
        print "failed on file %s"%curr_input_yaml_file
        import pdb;
        pdb.set_trace()



def get_cloadconfig_filename(input_yaml):
    try:
        for r in input_yaml['resources']:

            if input_yaml['resources'][r]['type'] == "OS::Nova::Server":
                return input_yaml['resources'][r]
                return input_yaml['resources'][r]['properties']['user_data']['str_replace']['template']['get_file']
        return None
    except KeyError:
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="This script will generate VF-Module heat templates to be used by AT&T.")
    parser = argparse.ArgumentParser(description='Enter folders')
    parser.add_argument('-i', '--heat-templates-path', metavar='HEAT_TEMPLATES_PATH', action='store',
                        dest='heat_templates_path', type=str, help='The heat templates path', required=True)
    parser.add_argument('-o', '--output_folder', action='store', metavar='OUTPUT_FOLDER', dest='output_folder', type=str,
                        help='location of Output Folder', required=True)
    parser.add_argument('-t', '--temp_folder', action='store', metavar='TEMP_FOLDER', dest='temp_folder', type=str,
                        help='location of Temp Folder', required=False)



    args = parser.parse_args()
    main(args)
