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



network_name = {
	'int_backend_ic': "backend_ic_net",
       'oam_protected': "oam_protected_net",
       'vprobes_mgmt': "vprobes_mgmt_int_net",
       'int_cdr_direct': "cdr_direct_net",
       'int_pktmirror': "int_pktmirror",
       'int_pktinternal': "pktinternal_int_net",
       'int_vertica_ic': 'int_vertica_ic'
}


def ordered_load(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    class OrderedLoader(Loader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))

    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)

def parse_yaml_file(file_path):
    """
    The functions returns as parsed YAML string
    :input file_path: The YAML file path
    An example of creating new dict and keep its order:
     yaml.load(str('{heat_template_version: 2014-10-16, description: {}, parameters: {}, resources: {}}'),
                                         Loader=yamlordereddictloader.Loader)
    """
    yaml_file_content = open(file_path)
    parsed_yaml = ordered_load(yaml_file_content, yaml.SafeLoader)
    return parsed_yaml


def parse_yaml_file_old(file_path):
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
    s_t  = parse_yaml_file(os.path.join(main_folder,  "SupremeTemplate", "SupremeTemplate.yaml"))

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
                print ("%s not exist in %s"%(s,yaml_resource.keys()))
                pass



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

def write_file(file_path, parsed_yaml, *args):
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



def write_file_old(file_path, yaml_outout):
    #print "saving %s"%file_path
    path =  ntpath.dirname(file_path)
    if not os.path.exists(path):
        os.makedirs(path)
    #yaml_utils.write_to_yaml_file(file_path,yaml_outout)
    with open(file_path, 'w') as yaml_file:
        yaml.dump(yaml_outout, yaml_file, default_flow_style=False)

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
    if os.path.exists(script_args.output_folder):
        shutil.rmtree(script_args.output_folder)
    shutil.copytree(script_args.heat_templates_path, os.path.join(script_args.output_folder))
    component_list =  get_component_list_from_supreme(script_args.output_folder)
    spr_input_file = parse_yaml_file(os.path.join(script_args.output_folder, "SupremeTemplate", "SupremeTemplate.yaml"))
    spre_input_file = parse_yaml_file(os.path.join(script_args.output_folder, "SupremeTemplate", "SupremeEnvironment.env"))
    for component in component_list.keys():
        print ("Working on %s"%component)
        #convert(component_list[component]['Template'].replace(script_args.heat_templates_path,os.path.join(script_args.output_folder)),component,component_list)
        if component != "QTrace" and component != "QInsight":
          convert(component_list[component]['Template'],component_list[component]['Launcher'],component,component_list,spr_input_file,spre_input_file)
        #import pdb;pdb.set_trace()

    write_file(os.path.join(script_args.output_folder, "SupremeTemplate", "SupremeTemplate.yaml"), spr_input_file)
    write_file(os.path.join(script_args.output_folder, "SupremeTemplate", "SupremeEnvironment.env"), spre_input_file)
def convert(template_yaml_file,luancer_yaml_file,component,component_list,spr_input_file , spre_input_file):
    try:

        template_input_yaml = parse_yaml_file(template_yaml_file)
        luancer_input_yaml = parse_yaml_file(luancer_yaml_file)

        server_element = get_cloadconfig_filename(template_input_yaml,"OS::Nova::Server")
        if server_element:
            cload_config = os.path.join(os.path.dirname(template_yaml_file), server_element['properties']['user_data']['str_replace']['template']['get_file'])

            cload_config_yaml = parse_yaml_file(cload_config)
            remove_arr = []
            index = 0
            for line in cload_config_yaml['runcmd']:
                if "edit_interface_file_ip_version.sh" in line:
                    #cload_config_yaml['runcmd'].remove(line)
                    remove_arr.append(line)
                elif "create_router.py" in line:
                    #import pdb;pdb.set_trace()
		    #cload_config_yaml['runcmd'].remove(line)
		    remove_arr.append(line)
                elif line == "sed -i 's|_slash_|/|g' /meta.js":
                    cload_config_yaml['runcmd'].insert(index+1,"python /root/network_config.py")
		    cload_config_yaml['runcmd'].insert(index+2,"systemctl restart network")
                index = index + 1

            for line in remove_arr:
                cload_config_yaml['runcmd'].remove(line)

            #import pdb;pdb.set_trace()
            #
            try:
                del (server_element['properties']['personality']['/root/edit_interface_file_ip_version.sh'])
                server_element['properties']['personality']['/root/network_config.py'] = {'get_file': '../network_config.py'}
            except KeyError:
                print ("%s has no edit_interface_file_ip_version.sh" % component)
            for template_port_ref in server_element['properties']['networks']:
                #print template_port_ref
                #import pdb;
                #pdb.set_trace()
                #parameter_main_name = template_port['properties']['network']['get_param'].split("_name")[0]
		parameter_main_name = template_input_yaml['resources'][template_port_ref['port']['get_resource']]['properties']['network']['get_param'].split("_name")[0]     
		parameter_main_name_parsed = network_name[parameter_main_name]
		print ("parameter_main_name is:"+parameter_main_name)
	        print ("parameter_main_name_parsed is:"+parameter_main_name_parsed)
		#server_element['properties']['user_data']['str_replace']['params']["%%%s_interface_mac%%"%parameter_main_name] = {'get_attr': [template_port_ref['port']['get_resource'], 'mac_address']}
                #server_element['properties']['user_data']['str_replace']['params']["%%%s_interface_network_method%%"%parameter_main_name] = {'get_param': parameter_main_name+ "_interface_network_method" }
		server_element['properties']['metadata']["%s_mac"%parameter_main_name_parsed] = {'get_attr': [template_port_ref['port']['get_resource'], 'mac_address']}
                server_element['properties']['metadata']["%s_method"%parameter_main_name_parsed] = {'get_param': parameter_main_name_parsed+ "_method" }
                                
		template_input_yaml['parameters'][parameter_main_name_parsed+ "_method"] = {"type": "string"}
                luancer_input_yaml['parameters'][parameter_main_name_parsed + "_method"] = {"type": "string"  , 'description': parameter_main_name+" network method"}
                
		if component == "RpmRepository":
                    luancer_input_yaml['resources'][component]['properties'][parameter_main_name_parsed + "_method"] = {'get_param': parameter_main_name_parsed + "_method"}
		else:
		    luancer_input_yaml['resources'][component]['properties']['resource_def']['properties'][parameter_main_name_parsed + "_method"] = {'get_param': parameter_main_name_parsed + "_method"}
                #import pdb;pdb.set_trace()
                spr_input_file['resources'][component]['properties'][parameter_main_name_parsed + "_method"] =  {'get_param': parameter_main_name_parsed + "_method"}
                spr_input_file['parameters'][parameter_main_name_parsed+ "_method"] = {"type": "string"}
                spre_input_file['parameters'][parameter_main_name_parsed  + "_method"] = "dhcp"
            write_file(template_yaml_file, template_input_yaml)
            write_file(luancer_yaml_file, luancer_input_yaml)
            write_file(cload_config, cload_config_yaml ,'cloudconfig')



            print ("Finish Template")


            #output_folder_path = ntpath.dirname(template_yaml_file)
            # cloadconfig_file_name = server_element['properties']['user_data']['str_replace']['template']['get_file']
            # #import pdb;pdb.set_trace()
            # cload_config_file = os.path.join(output_folder_path,cloadconfig_file_name)
            # for i in arr:
            #     del server_element['properties']['user_data']['str_replace']['params'][i['old_name']]
            #     server_element['properties']['user_data']['str_replace']['params'][
            #         i['new_name']] = i['value']
            #     command = "sed -i 's/%s/%s/g' %s" % (i['old_name'], i['new_name'], cload_config_file)
            #     #print command
            #     execute_command(command)



            #return cload_config_path
    except KeyError:
        print "failed on file %s"%template_yaml_file
        traceback.print_exc(file=sys.stdout)
        print sys.exc_info()
        import pdb;
        pdb.set_trace()



def get_cloadconfig_filename(input_yaml , resource_type, resource_name = None):
    try:
        for r in input_yaml['resources']:

            if input_yaml['resources'][r]['type'] == resource_type:
                if not resource_name:
                    return input_yaml['resources'][r]
                else:
                    if r == resource_name:
                        return input_yaml['resources'][r]
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

