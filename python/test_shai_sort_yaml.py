#!/usr/bin/python2.7
import argparse 

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









