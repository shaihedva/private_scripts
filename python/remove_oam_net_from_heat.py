#!/usr/bin/python2.7
import argparse
import os , glob
import ntpath
import sys
import traceback
import shutil
#from python_pkg.xradc.utils import yaml_utils
import yaml
from collections import OrderedDict
#from python.outputs_modules.heat_module import HeatModule
#from xradc import logger




def get_component_list_from_supreme(main_folder):
    #s_t = yaml_utils.parse_yaml_file(os.path.join(main_folder,  "SupremeTemplate", "SupremeTemplate.yaml"))
    with open(os.path.join(main_folder,  "SupremeTemplate", "SupremeTemplate.yaml"), 'r') as stream:
        try:
            s_t = yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)
        
        
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


def remove_string(yaml_resource , remove_array):
    for k in yaml_resource.keys():
        if k.lower() in remove_array:
            try:
                del(yaml_resource[k])
            except KeyError:
                #import pdb;pdb.set_trace()
                #print ("%s not exist in %s"%(s,yaml_resource.keys()))
                pass


def write_file(file_path, yaml_outout):
    path =  ntpath.dirname(file_path)
    if not os.path.exists(path):
        os.makedirs(path)
    #yaml_utils.write_to_yaml_file(file_path,yaml_outout)
    with open(file_path, 'w') as yaml_file:
        yaml.dump(yaml_outout, yaml_file, default_flow_style=False)



def main(script_args):
    """
    :param script_args:
    :return:
    """
    # Create logger
   
    # Validate the scripts arguments.

    shutil.copytree(os.path.join(script_args.heat_templates_path, "../RegisterStatus"), os.path.join(script_args.output_folder,'RegisterStatus'))
    shutil.copytree(os.path.join(script_args.heat_templates_path, "../site_info"), os.path.join(script_args.output_folder,'site_info'))
    shutil.copytree(os.path.join(script_args.heat_templates_path, "../CheckAvailability"), os.path.join(script_args.output_folder,'CheckAvailability'))
    shutil.copytree(script_args.heat_templates_path, os.path.join(script_args.output_folder,'OnboardingTemplates'))
    component_list =  get_component_list_from_supreme(script_args.heat_templates_path)


### Networks Stack
    #input_yaml = yaml_utils.parse_yaml_file(os.path.join(script_args.heat_templates_path,"NetworksTemplate.yaml"))
    with open(os.path.join(script_args.heat_templates_path,"NetworksTemplate.yaml"), 'r') as stream:
        try:
            input_yaml = yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    remove_string(input_yaml['parameters'],['router_name', 'external_net_name' , 'vprobes_mgmt_name' , 'vprobes_mgmt_subnet_name' , 'vprobes_mgmt_subnet_cidr' ,
                                            'vprobes_mgmt_subnet_alloc_start','vprobes_mgmt_subnet_alloc_end'])
    remove_string(input_yaml['resources'],['router' , 'router_interface' , 'vprobes_mgmt_net' , 'vprobes_mgmt_subnet'])
    remove_string(input_yaml['outputs'],['vprobes_mgmt_name', 'vprobes_mgmt_subnet_name', ])

    write_file(os.path.join(script_args.output_folder,'OnboardingTemplates',"NetworksTemplate.yaml"), input_yaml)


    #input_yaml = yaml_utils.parse_yaml_file(os.path.join(script_args.heat_templates_path, "NetworksEnvironment.env"))
    with open(os.path.join(script_args.heat_templates_path, "NetworksEnvironment.env"), 'r') as stream:
        try:
            input_yaml = yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    remove_string(input_yaml['parameters'],
                  ['external_net_name','vprobes_mgmt_name', 'vprobes_mgmt_subnet_name', 'vprobes_mgmt_name', 'vprobes_mgmt_subnet_cidr',
                   'vprobes_mgmt_subnet_alloc_start', 'vprobes_mgmt_subnet_alloc_end','router_name'])

    write_file(os.path.join(script_args.output_folder,'OnboardingTemplates', "NetworksEnvironment.env"), input_yaml)


### Supreme_stack
    #input_yaml = yaml_utils.parse_yaml_file(os.path.join(script_args.heat_templates_path,"SupremeTemplate",  "SupremeTemplate.yaml"))
    with open(os.path.join(script_args.heat_templates_path,"SupremeTemplate",  "SupremeTemplate.yaml"), 'r') as stream:
        try:
            input_yaml = yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    
    remove_string(input_yaml['parameters'], ['external_net_name'])

    for component in component_list.keys():
        remove_string(input_yaml['resources'][component]['properties'], ['external_net_name'])

    write_file(os.path.join(script_args.output_folder,'OnboardingTemplates',"SupremeTemplate",  "SupremeTemplate.yaml"), input_yaml)



    #input_yaml = yaml_utils.parse_yaml_file(os.path.join(script_args.heat_templates_path, "SupremeTemplate",  "SupremeEnvironment.env"))
    with open(os.path.join(script_args.heat_templates_path, "SupremeTemplate",  "SupremeEnvironment.env"), 'r') as stream:
        try:
            input_yaml = yaml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    
    remove_string(input_yaml['parameters'],['external_net_name'])


    write_file(os.path.join(script_args.output_folder,'OnboardingTemplates',"SupremeTemplate",  "SupremeEnvironment.env"), input_yaml)


    #import pdb;pdb.set_trace()



    for component in component_list.keys():
        #print ("Working on %s"%component)
        for type in ['Template','Launcher']:
            #input_yaml = yaml_utils.parse_yaml_file(component_list[component][type])
            with open(component_list[component][type], 'r') as stream:
                try:
                    input_yaml = yaml.load(stream)
                except yaml.YAMLError as exc:
                    print(exc)
            remove_string(input_yaml['resources'],
                          ['external_net_name',component.lower()+'_floating_ip', component.lower()+'_floating_ip_association', 'vprobes_mgmt_net', 'vprobes_mgmt_subnet'])
            remove_string(input_yaml['parameters'],
                          ['external_net_name',component.lower()+'_floating_vip_0'])
            if type == 'Launcher':
                try:
                    remove_string(input_yaml['resources'][component]['properties']['resource_def']['properties'], ['external_net_name'])
                except KeyError:
                    print ("%s doent have resource_def"%component)
            try:
                remove_string(input_yaml['resources'][component]['properties'],['external_net_name'])
            except KeyError:
                pass

            try:
                remove_string(input_yaml['resources'][component]['properties']['metadata'],['floating_ip','floating_vip_ip'])
            except KeyError:
                pass

            try:
                del (input_yaml['resources'][component.lower()+"_floating_vip_3_port"])
            except KeyError:
                #print ("%s has no vip"%component)
                pass

            try:
                del (input_yaml['resources'][component]['properties']['resource_def']['properties'][component.lower() + "_floating_vip_0"])
            except KeyError:
                #print ("%s has no _floating_vip_" % component)
                pass

            file_path = component_list[component][type].replace(script_args.heat_templates_path,os.path.join(script_args.output_folder,'OnboardingTemplates/'))
            write_file(file_path, input_yaml)

        cload_config_path = ntpath.dirname(component_list[component]['Template'])
        for file in glob.glob(os.path.join(cload_config_path,'*CloudConfig*')):
            #print(file)
            shutil.copy(file, ntpath.dirname(file_path))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="This script will generate VF-Module heat templates to be used by AT&T.")
    parser = argparse.ArgumentParser(description='Enter folders')
    parser.add_argument('-i', '--heat-templates-path', metavar='HEAT_TEMPLATES_PATH', action='store',
                        dest='heat_templates_path', type=str, help='The heat templates path', required=True)
    parser.add_argument('-o', '--output_folder', action='store', metavar='OUTPUT_FOLDER', dest='output_folder', type=str,
                        help='location of Output Folder', required=True)


    args = parser.parse_args()
    main(args)
